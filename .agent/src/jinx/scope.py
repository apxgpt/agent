# Copyright 2026 JINX Enterprise Team. All Rights Reserved.
#
# Use of this software is governed by the JINX End User License Agreement (EULA): the LICENSE.md file
# at the root of the JINX repository (https://github.com/machinegpt/agent), and in the `.agent` folder of
# a project where JINX is installed. It is free for personal, educational and non-commercial use,
# including non-commercial research; commercial use needs a commercial license (section 2 of the EULA).
# ==============================================================================
"""The lifecycle of a session as a *scope*, and what follows from it for runs that are started inside other runs.

A JINX run is a state machine whose every transition is a process of its own: ``jinx.py`` is called, does one step and
exits, and between two calls the editor works. A model that is asked to use JINX for a part of its job can therefore
start another JINX run from a shell command of its own (``bash_exec``), and that run can do the same again. Nothing
in the runtime used to say whether such a run was *inside* another one, whether it was still open, or whether the run
around it could end first. This module gives every session an explicit scope with an exact beginning and end, decided
by code and not by anything the model is told:

``open`` -> ``closed``
    A session is *open* from the moment it is created until ``sessions.end`` closes it, and it is closed exactly once.
    How it ended is on its card (``ended``: ``complete``, ``deadlock``, ``hard_cap``, ``aborted``, ``cancelled``,
    ``orphaned`` or ``lost``) with who closed it (``closed_by``: ``self``, ``parent:<id>``, ``user`` or ``sweep``).
    A session that is not closed and has not been heard from for its lease is *lost*: nobody drives it any more.

lineage
    A session that is started from a tool call of another one is its *child*: its card names ``parent``, ``root`` and
    ``depth``. The link is made only from evidence, never guessed (see :func:`resolve_parent`): the caller said so
    (``--parent``, ``JINX_PARENT``), or exactly one live session is waiting for a tool batch that contains this very launch.
    A launch that cannot be linked is an ordinary, unrelated session, as it always was.

rules (all enforced here, in code)
    * a child that would be too deep, would repeat the task of one of its ancestors, or would be one too many for its
      parent is refused, and so is any launch once too many sessions are open at all (:func:`admit`);
    * two calls never advance one session at the same moment (:func:`step_lock`);
    * a run that is ready to end waits (a bounded number of rounds) for the children that are still open, and when it
      ends, the children that are left are closed with it (:func:`close_tree`): no scope outlives the one it was
      started in;
    * a child that nobody has driven for a long time, whose parent is gone too, is closed as ``lost`` instead of
      staying "unfinished" for a week (:func:`reap`).

Nothing here adds a word to a prompt. The model reads a sentence from this module only when a rule actually acts on
it: as the output of the command that was refused, or as one line of the round in which an exit is held back.

The module needs nothing but ``mail.py``, so ``jinx.py --close`` runs without the runner, as ``--peek`` does.
"""
from __future__ import annotations

import argparse
import contextlib
import errno
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, NamedTuple, Optional, Sequence, Tuple

import yaml

from . import mail

logger = logging.getLogger("jinx.scope")

DEFAULT_MAX_DEPTH = 3          # runs inside runs: the first run is level 0, so three more can be nested in it
DEFAULT_MAX_CHILDREN = 4       # open runs that one run has started
DEFAULT_MAX_SESSIONS = 12      # open sessions in one project: the backstop for a recursion nobody could link
EXIT_HOLDS = 1                 # rounds in which a run that is ready to end waits for its open children
REAP_AFTER_S = 3600.0          # a child nobody has driven this long (and at least four leases) may be closed as lost
TASK_KEY_MIN = 12              # letters and digits a task needs before it can be recognised inside a script
TASK_KEY_LEN = 60              # ... and how many of them are compared
REQUEST_READ_CAP = 2_000_000   # bytes of a request that are read to look for a launch in it
LOCK_NAME = ".step.lock"       # the lock file of one session, inside its directory

OPEN, LOST, CLOSED, GONE = "open", "lost", "closed", "gone"

COMPLETE, DEADLOCK, HARD_CAP, ABORTED, CANCELLED, ORPHANED = (
    "complete", "deadlock", "hard_cap", "aborted", "cancelled", "orphaned")

_BATCH_FILES = ("jinx_request.yaml", "jinx_response.yaml", "jinx_run_state.yaml")


class Refused(Exception):
    """A launch that the scope rules do not allow. The message is read by the model that ran the command."""


class Closed(Exception):
    """The session that was asked for is closed. The message says how it ended."""


class Busy(Exception):
    """Another call is advancing the session that was asked for right now (see :func:`step_lock`)."""

    def __init__(self, sid: str):
        super().__init__(sid)
        self.sid = sid


def _env_int(name: str, default: int, floor: int) -> int:
    try:
        return max(floor, int(float(os.environ.get(name, default))))
    except (TypeError, ValueError, OverflowError):
        return default


def max_depth() -> int:
    """``JINX_MAX_DEPTH``: how many levels of runs may be nested (0 allows none)."""
    return _env_int("JINX_MAX_DEPTH", DEFAULT_MAX_DEPTH, 0)


def max_children() -> int:
    """``JINX_MAX_CHILDREN``: how many open runs one run may have started."""
    return _env_int("JINX_MAX_CHILDREN", DEFAULT_MAX_CHILDREN, 1)


def max_sessions() -> int:
    """``JINX_MAX_SESSIONS``: how many sessions may be open in one project."""
    return _env_int("JINX_MAX_SESSIONS", DEFAULT_MAX_SESSIONS, 1)


def exit_holds() -> int:
    """``JINX_EXIT_HOLDS``: in how many rounds a run that is ready to end waits for its open children (0: never)."""
    return _env_int("JINX_EXIT_HOLDS", EXIT_HOLDS, 0)


# --------------------------------------------------------------------------- reading the state
def cards_of(office: mail.Office) -> Dict[str, Dict[str, Any]]:
    """Every readable card, by session id."""
    out: Dict[str, Dict[str, Any]] = {}
    for sid in office.session_ids():
        card = office.card(sid)
        if card:
            out[sid] = card
    return out


def _num(value: Any, default: float = 0.0) -> float:
    """``value`` as a number; ``default`` for what a card should never hold (a hand-edited or damaged card)."""
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return default


def _alive(office: mail.Office, sid: str, card: Dict[str, Any], now: Optional[float] = None) -> bool:
    """Whether the session was heard from within its lease; a card that cannot tell it says no."""
    try:
        return office.alive(sid, card, now)
    except (TypeError, ValueError, OverflowError):
        return False


def state_of(office: mail.Office, sid: str, card: Optional[Dict[str, Any]] = None, now: Optional[float] = None) -> str:
    """``open``, ``lost`` (not closed, but silent for longer than its lease), ``closed`` or ``gone`` (no such session)."""
    c = office.card(sid) if card is None else card
    if not c:
        return GONE
    if c.get("state") == "done":
        return CLOSED
    return OPEN if _alive(office, sid, c, now) else LOST


def depth_of(card: Dict[str, Any]) -> int:
    try:
        return max(0, int(card.get("depth") or 0))
    except (TypeError, ValueError, OverflowError):
        return 0


def how_ended(card: Dict[str, Any]) -> str:
    """``cancelled by user``, ``orphaned by parent s1``, ``complete``: how a closed session ended, in words."""
    ended = str(card.get("ended") or "finished").replace("_", " ")
    by = str(card.get("closed_by") or "")
    if by in ("", "self"):
        return ended
    return f"{ended} by {by.replace(':', ' ')}"


def chain(cards: Dict[str, Dict[str, Any]], sid: str, limit: int = 32) -> List[str]:
    """``sid`` and the sessions it was started in, nearest first (the last one is the root)."""
    out: List[str] = []
    while sid and sid in cards and sid not in out and len(out) < limit:
        out.append(sid)
        sid = str(cards[sid].get("parent") or "")
    return out


def children(office: mail.Office, cards: Dict[str, Dict[str, Any]], sid: str, now: Optional[float] = None,
             states: Sequence[str] = (OPEN,)) -> List[str]:
    """The sessions started in ``sid`` that are in one of ``states`` (by default: open)."""
    return sorted(s for s, c in cards.items()
                  if c.get("parent") == sid and state_of(office, s, c, now) in states)


def unfinished_descendants(cards: Dict[str, Dict[str, Any]], sid: str) -> List[str]:
    """Every session below ``sid`` that is not closed, the deepest first: the order in which a scope is closed."""
    out: List[str] = []
    seen = {sid}

    def walk(parent: str) -> None:
        for kid in sorted(k for k, c in cards.items() if c.get("parent") == parent and k not in seen):
            seen.add(kid)
            walk(kid)
            if cards[kid].get("state") != "done":
                out.append(kid)

    walk(sid)
    return out


# --------------------------------------------------------------------------- is this launch inside another run?
class Link(NamedTuple):
    parent: str
    via: str            # flag | env | batch: how the link was established


_NOT_ALNUM = re.compile(r"[\W_]+")
# What starts JINX from a shell: the entry point, the console script, the module.
_LAUNCH = re.compile(r"jinx\.py\b|\bjinx-cli\b|\bjinx\.cli\b", re.I)
_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def task_key(text: Any) -> str:
    """A task as letters and digits only, case-folded: what two spellings of one task (quoted, escaped, wrapped) share."""
    return _NOT_ALNUM.sub("", str(text or "").casefold())


def _card_task(task: Any) -> str:
    """The task as a card keeps it (see ``mail.Office.new_session``)."""
    return " ".join(str(task or "").split())[:200]


def _load_capped(path: Path) -> Any:
    """A YAML file as data; None when it is missing, unreadable, malformed or larger than ``REQUEST_READ_CAP``."""
    try:
        if path.stat().st_size > REQUEST_READ_CAP:
            return None
        return yaml.load(path.read_text("utf-8", errors="replace"), Loader=_LOADER)
    except (OSError, ValueError, RecursionError, yaml.YAMLError):
        return None


def _launch_scripts(calls: Iterable[Tuple[Any, Any]]) -> List[str]:
    """The shell scripts among ``(tool name, parameters)`` pairs that start JINX."""
    out: List[str] = []
    for name, params in calls:
        script = params.get("script") if isinstance(params, dict) else None
        if name == "bash_exec" and isinstance(script, str) and _LAUNCH.search(script):
            out.append(script)
    return out


def _unanswered_calls(history: Any) -> List[Tuple[Any, Any]]:
    """``(tool name, input)`` of the newest assistant message that asks for tools none of whose results is there yet.

    The run state keeps the batch in the history of the run, with the full inputs, until its results come back
    (``runner._extract_last_tool_calls`` reads it the same way).
    """
    answered = set()
    for msg in reversed(history if isinstance(history, list) else []):
        content = msg.get("content") if isinstance(msg, dict) else None
        if not isinstance(content, list):
            continue
        calls: List[Tuple[Any, Any]] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result":
                answered.add(block.get("tool_use_id"))
            elif block.get("type") == "tool_use" and block.get("id") not in answered:
                calls.append((block.get("name"), block.get("input")))
        if calls:
            return calls
    return []


def pending_launches(office: mail.Office, sid: str) -> List[str]:
    """The shell scripts of the tool batch that ``sid`` is waiting for which start JINX; none when it waits for nothing.

    The batch is the request the runner wrote for the editor: the one place where it is certain what the editor was
    asked to run on behalf of that session. A host that deletes the request before it runs the batch (the loop in the
    README does) leaves the same batch in the run state, and that is read instead.
    """
    base = office.sessions_dir / sid
    data = _load_capped(base / "jinx_request.yaml")
    if isinstance(data, dict) and data.get("type") == "tool_calls":
        calls = data.get("calls")
        return _launch_scripts((c.get("name"), c.get("params")) for c in (calls if isinstance(calls, list) else [])
                               if isinstance(c, dict))
    state = _load_capped(base / "jinx_run_state.yaml")
    if isinstance(state, dict) and state.get("waiting_for") == "tool_calls":
        return _launch_scripts(_unanswered_calls(state.get("history")))
    return []


def find_parent_by_batch(office: mail.Office, cards: Dict[str, Dict[str, Any]], task: str,
                         now: Optional[float] = None) -> Optional[str]:
    """The one session whose pending tool batch starts JINX with this task, or None.

    Only a session that is alive and waits for a tool batch (``waiting: tool_calls`` on its card) can have started a
    run (one that has not been heard from for its lease has lost its editor: a launch is not made its child), and
    only one whose shell script contains a JINX launch *and the words of this task* is taken for the parent. A task
    too short to be told from other text, or two sessions that both qualify, give no answer: an unrelated launch is
    never made a child by a coincidence.
    """
    key = task_key(_card_task(task))[:TASK_KEY_LEN]
    if len(key) < TASK_KEY_MIN:
        return None
    found = [sid for sid, c in cards.items()
             if c.get("state") != "done" and c.get("waiting") == "tool_calls" and _alive(office, sid, c, now)
             and any(key in task_key(script) for script in pending_launches(office, sid))]
    return found[0] if len(found) == 1 else None


def resolve_parent(office: mail.Office, cards: Dict[str, Dict[str, Any]], *, flag: Optional[str],
                   env: Optional[str], task: str, now: Optional[float] = None) -> Optional[Link]:
    """The session this launch runs inside, or None for an independent one.

    ``flag`` (``--parent``) is a statement of the caller: it must name a session that is not closed, or the launch is
    refused. ``env`` (``JINX_PARENT``) can be left over in a shell, so it counts only while that session is alive and
    waits for a tool batch, and is ignored otherwise. Without either, the pending batches are looked at
    (find_parent_by_batch).
    """
    if flag:
        card = cards.get(flag)
        if not card:
            raise Refused(f"--parent {flag}: there is no such session")
        if card.get("state") == "done":
            raise Refused(f"--parent {flag}: that session is closed ({how_ended(card)}); "
                          "a run inside another needs the other one to be open")
        return Link(flag, "flag")
    if env:
        card = cards.get(env)
        if card and card.get("state") != "done" and card.get("waiting") == "tool_calls" and _alive(office, env, card, now):
            return Link(env, "env")
    parent = find_parent_by_batch(office, cards, task, now)
    return Link(parent, "batch") if parent else None


def admit(office: mail.Office, cards: Dict[str, Dict[str, Any]], task: str, link: Optional[Link],
          now: Optional[float] = None) -> Dict[str, Any]:
    """Lets a new session in, or raises :class:`Refused`. Returns the lineage fields for its card ({} when it has none)."""
    now = time.time() if now is None else now
    cmd = office.cmd
    fields: Dict[str, Any] = {}
    if link is not None:
        parent = cards[link.parent]
        ancestors = chain(cards, link.parent)
        depth = depth_of(parent) + 1
        if depth > max_depth():
            raise Refused(
                f"nested too deep: this run would be level {depth} inside {' > '.join(reversed(ancestors))} "
                f"(limit {max_depth()}, JINX_MAX_DEPTH). Do this part in the session you are in instead of "
                "starting another run.")
        key = task_key(_card_task(task))
        if key:
            for anc in ancestors:
                if task_key(cards[anc].get("task")) == key:
                    raise Refused(
                        f"{anc} runs this same task and its tool call started this one: a nested run of it would "
                        "start itself again without end. Do the work in this session, or give the nested run a "
                        "smaller task than its parent's.")
        kids = children(office, cards, link.parent, now)
        if len(kids) >= max_children():
            raise Refused(
                f"{link.parent} already has {len(kids)} open child runs ({', '.join(kids)}; limit {max_children()}, "
                "JINX_MAX_CHILDREN). Let one of them finish before starting another.")
        fields = {"parent": link.parent, "root": ancestors[-1], "depth": depth, "via": link.via}
    live = sorted(s for s, c in cards.items() if state_of(office, s, c, now) == OPEN)
    if len(live) >= max_sessions():
        raise Refused(
            f"{len(live)} sessions are open in this project (limit {max_sessions()}, JINX_MAX_SESSIONS): "
            f"{', '.join(live[:8])}{' ...' if len(live) > 8 else ''}. Finish some of them, or close abandoned ones "
            f"with `{cmd} --close <id> --force`.")
    return fields


# --------------------------------------------------------------------------- one step of a session at a time
@contextlib.contextmanager
def step_lock(path: Path, timeout: float = 0.0) -> Iterator[bool]:
    """An exclusive lock on the right to advance one session, held for the whole call and freed by the system.

    ``jinx.py`` does one transition per call, and nothing used to stop two calls from doing it at the same moment
    on one session: a double resume, or a command that runs inside a tool batch of the very session it resumes.
    Both would read the same run state and each write its own successor. The lock is an operating-system file lock
    (``flock``, ``msvcrt.locking`` on Windows), so a call that is killed frees it and there is no stale lock to break.

    Yields True when the caller holds the lock, and False when another call kept it for the whole ``timeout``. A lock
    that cannot exist here at all (the file cannot be opened, the platform has no file locks) is not held by anybody
    else: that is warned about and the caller goes ahead, as a single process would. It never raises.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(path, "a+b")
    except OSError as e:
        logger.warning("%s: cannot open the step lock (%s); going on without it", path, e)
        yield True
        return
    held = False
    usable = True
    try:
        deadline = time.monotonic() + max(0.0, timeout)
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                held = True
                break
            except OSError as e:
                if e.errno not in (errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK, errno.EDEADLK):
                    usable = False
                    logger.warning("%s: file locks are not usable here (%s); going on without the step lock", path, e)
                    break
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.02)
            except ImportError:
                usable = False
                logger.warning("%s: this platform has no file locks; going on without the step lock", path)
                break
        yield held or not usable
    finally:
        if held:
            try:
                if os.name == "nt":
                    import msvcrt
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            except (OSError, ImportError):
                pass
        handle.close()


# --------------------------------------------------------------------------- closing a scope
def _remove(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError as e:
        logger.warning("Could not remove %s: %s", path, e)


def _close_one(office: mail.Office, sid: str, ended: str, by: str, wait: float) -> Optional[bool]:
    """Closes one session from outside: True when it was closed, False when its step is running, None when it is closed already.

    Its request, response and run state go, so that the editor that still drives it is told (by
    ``sessions.open_session``) that it is closed instead of finding half a run; its leases are released and its card
    says how it ended. What it changed in the working tree stays, and so do its round files.
    """
    base = office.sessions_dir / sid
    with step_lock(base / LOCK_NAME, wait) as held:
        if not held:
            return False
        card = office.card(sid)
        if not card or card.get("state") == "done":
            return None
        for name in _BATCH_FILES:
            _remove(base / name)
        try:
            office.session(sid).close(ended=ended, closed_by=by, closed_at=mail.utc_iso())
        except (OSError, mail.MailError) as e:
            logger.warning("Could not close session %s: %s", sid, e)
            return False
    return True


def close_tree(office: mail.Office, sid: str, *, ended: str, by: str, kids_ended: Optional[str] = None,
               include_self: bool = True, wait: float = 1.0) -> Tuple[List[str], List[str]]:
    """Closes the sessions that are open below ``sid`` (deepest first) and, unless ``include_self`` is False, ``sid``.

    Returns ``(closed, busy)``: the ids that were closed now, and those that could not be because a call was
    advancing them for the whole ``wait`` (they stay open, and their own next call will find their parent gone).
    A session that is closed already is not named in either list.
    """
    cards = cards_of(office)
    closed: List[str] = []
    busy: List[str] = []
    targets = [(kid, kids_ended or ended, f"parent:{sid}") for kid in unfinished_descendants(cards, sid)]
    if include_self:
        targets.append((sid, ended, by))
    for target, how, who in targets:
        result = _close_one(office, target, how, who, wait)
        if result:
            closed.append(target)
        elif result is False:
            busy.append(target)
    return closed, busy


def reap(office: mail.Office, now: Optional[float] = None) -> List[str]:
    """Closes, as ``lost``, the children that nobody drives any more. Safe to run from any process at any time.

    A child whose editor gave up used to stay "unfinished" for up to a week (until archived), and kept a bare call
    from being matched to its session. It is closed only when it has been silent for a long time (at least
    ``REAP_AFTER_S`` and four leases) *and* the run it was started in is not alive either (closed, silent or
    gone): while the parent is alive somebody still may come back for the child.
    """
    now = time.time() if now is None else now
    cards = cards_of(office)
    out: List[str] = []
    for sid, card in cards.items():
        if not card.get("parent") or card.get("state") == "done":
            continue
        silent = now - _num(card.get("hb"))
        if silent < max(REAP_AFTER_S, 4 * (_num(card.get("lease_s")) or mail.DEFAULT_LEASE_S)):
            continue
        parent = str(card["parent"])
        if state_of(office, parent, cards.get(parent), now) == OPEN:
            continue
        if _close_one(office, sid, "lost", "sweep", 0.0):
            out.append(sid)
    return out


# --------------------------------------------------------------------------- a run that wants to end with open children
def hold_note(office: mail.Office, kids: Sequence[str]) -> str:
    """The one line the model reads in the round whose exit is held back (model-facing text)."""
    shown = "; ".join(f'{k} ("{mail._short(office.card(k).get("task"), 30)}")' for k in kids[:3])
    if len(kids) > 3:
        shown += f"; +{len(kids) - 3} more"
    return (f"[scope] Runs you started are still open: {shown}. Take each to its end "
            f"({office.cmd} --session <id>) before you finish: what is open when this run ends is closed with it.")


# --------------------------------------------------------------------------- JINX_SESSIONS=0: one shared set of files
def _read_yaml(path: Path) -> Dict[str, Any]:
    try:
        data = yaml.load(path.read_text("utf-8", errors="replace"), Loader=_LOADER)
    except (OSError, ValueError, RecursionError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def shared_refusal(run_state: Path, task: str, lease_s: float, force: bool, cmd: str) -> Optional[str]:
    """Why a new task must not start in the shared files right now, or None.

    With ``JINX_SESSIONS=0`` there is one request, one response and one run state. A new task replaces the run that
    is there, and so a run started from a tool batch of the run that waits for that very batch would wipe it. A run
    that is waiting for a tool batch it issued less than ``lease_s`` ago is not abandoned, so the new task is
    refused unless the caller insists (``--force``); an older one is replaced as before.
    """
    if not task or force or not run_state.exists():
        return None
    state = _read_yaml(run_state)
    if state.get("waiting_for") != "tool_calls":
        return None
    try:
        age = time.time() - float(state.get("updated_at") or 0)
    except (TypeError, ValueError):
        return None
    if age >= lease_s:
        return None
    return (f"a run in the shared files is waiting for its tool batch (issued {int(age)} s ago), and a new task would "
            "replace it. A run inside a run needs sessions: leave JINX_SESSIONS=0 out. To end the open run and "
            f"start this task in its place: `{cmd} --close --force`, then the same command again.")


# --------------------------------------------------------------------------- jinx.py --close
def _sessions_off() -> bool:
    """The same rule as ``sessions.enabled()`` (this module cannot import it: it runs before the runner does)."""
    return os.environ.get("JINX_SESSIONS", "1").strip().lower() in ("0", "false", "no", "off")


def close_main(argv: Sequence[str], agent_dir: Path) -> int:
    """``jinx.py --close [id ...] [--force]``: close sessions, with the runs inside them. Prints and returns an exit code.

    A session that is alive (heard from within its lease), or has an open run inside it that is, is closed only
    with ``--force``: closing takes the run away from the editor that drives it. A session that is lost or already
    closed needs no force. With ``JINX_SESSIONS=0`` and no id, the one shared run is closed.
    """
    ap = argparse.ArgumentParser(prog="jinx.py", add_help=False)
    ap.add_argument("--close", nargs="*", default=None)
    ap.add_argument("--force", action="store_true")
    args, _ = ap.parse_known_args(list(argv))
    ids = [s.strip() for s in (args.close or []) if s.strip()]
    agent_dir = Path(agent_dir)
    root = Path(os.environ.get("JINX_PROJECT_ROOT") or agent_dir.parent).resolve()
    ipc = Path(os.environ.get("JINX_IPC_DIR") or (agent_dir / "ipc"))
    try:
        rel_agent = Path(os.path.relpath(agent_dir, root)).as_posix()
    except ValueError:
        rel_agent = str(agent_dir)
    cmd = mail.jinx_command(rel_agent)

    if _sessions_off():
        return _close_shared(agent_dir, ids, args.force, cmd)
    if not ids:
        print(f"[JINX_REFUSED] name the session to close: `{cmd} --close <id> [<id> ...] [--force]`; "
              f"`{cmd} --peek` lists the sessions")
        return 1
    if not (ipc / "sessions").is_dir():
        print("no JINX sessions yet")
        return 1
    try:
        office = mail.Office(ipc, label=Path(os.path.relpath(ipc, root)).as_posix(), cmd=cmd)
    except (OSError, ValueError, mail.MailError) as e:
        print(f"cannot read {ipc}: {e}")
        return 1
    code = 0
    for sid in ids:
        cards = cards_of(office)
        card = cards.get(sid)
        if not card:
            print(f"{sid}: no such session")
            code = 1
            continue
        if card.get("state") == "done":
            print(f"[JINX_CLOSED] id={sid} already closed ({how_ended(card)})")
            continue
        now = time.time()
        alive = [s for s in [sid] + unfinished_descendants(cards, sid) if state_of(office, s, cards[s], now) == OPEN]
        if alive and not args.force:
            print(f"[JINX_REFUSED] {', '.join(alive)} still run{'s' if len(alive) == 1 else ''} (heard from within "
                  f"the last {int(_num(card.get('lease_s')) or mail.DEFAULT_LEASE_S)} s); closing takes the run away "
                  f"from its editor. To do it anyway: `{cmd} --close {sid} --force`")
            code = 1
            continue
        closed, busy = close_tree(office, sid, ended=CANCELLED, by="user")
        inside = [s for s in closed if s != sid]
        line = f"[JINX_CLOSED] id={sid} ended={CANCELLED}" + (f" with={','.join(inside)}" if inside else "")
        if busy:
            line += f" busy={','.join(busy)} (a call was advancing them; close them again in a moment)"
            code = 1
        print(line)
    return code


def _close_shared(agent_dir: Path, ids: Sequence[str], force: bool, cmd: str) -> int:
    """``--close`` with ``JINX_SESSIONS=0``: end the one shared run."""
    if ids:
        print("[JINX_REFUSED] JINX_SESSIONS=0: there is one shared run and no session ids; use `--close` alone")
        return 1
    files = [agent_dir / name for name in _BATCH_FILES]
    if not any(f.exists() for f in files):
        print("no run is open in the shared files")
        return 0
    state = _read_yaml(agent_dir / "jinx_run_state.yaml")
    try:
        age = time.time() - float(state.get("updated_at") or 0)
    except (TypeError, ValueError):
        age = float("inf")
    lease = _env_int("JINX_LEASE_S", mail.DEFAULT_LEASE_S, 30)
    if state.get("waiting_for") == "tool_calls" and age < lease and not force:
        print(f"[JINX_REFUSED] the shared run is waiting for a tool batch issued {int(age)} s ago; closing it takes "
              f"the run away from its editor. To do it anyway: `{cmd} --close --force`")
        return 1
    for f in files:
        _remove(f)
    print(f"[JINX_CLOSED] id=- ended={CANCELLED}")
    return 0
