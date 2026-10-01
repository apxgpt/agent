# Copyright 2026 JINX Enterprise Team. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Prompt definitions and constructor constants for the JINX Sovereign Agent Framework.

This module is the single home for every piece of text JINX sends to the model:
the system prompt, the per-round user prompt, the tool declarations offered in
each request, and every notice, warning, diagnostic and refusal injected
mid-run. No other module hard-codes model-facing prose; they import it from
here instead, so a wording change is a one-file change and the whole prompt
contract can be reviewed in one place.

Two exceptions are deliberate, and the second is enforced by the self-patch gate
rather than by convention:

* ``state.py`` — the state-block rejection and score-merge diagnostics are
  built inside ``merge_state``, which is protected brake logic, so they stay
  where they are. Moving them out would mean editing a function JINX refuses to
  edit.
* ``selfpatch.py`` (``guard_tool_call``'s refusal text) and ``learning.py``
  (``LEARNED_RULES_HEADER``) are protected files that JINX refuses to rewrite
  at all. See ``selfpatch.PROTECTED_FILES``.
"""

from typing import Any, Dict, List, Tuple

from . import reasoning


SYSTEM_PROMPT: str = """You are JINX, a single-agent cognitive loop. You execute tasks through disciplined iterative refinement.

LOOP PROTOCOL (enforced externally — each call is one real round):

GATE BEFORE TRY: Write exactly what the previous round failed on. No silent retries.
TRY: Choose an approach genuinely different from all prior approaches. Systematically inspect the `approach_graph` of all previous failing rounds in `scores` to perform structural deduction. Identify which nodes, relations, and paths failed, and construct a new strategy that targets completely different components, files, or relationships (aiming for minimal structural intersection/overlap with prior failing graphs).
TEST: You have access to bash_exec, file_read, and file_write tools.
  CRITICAL: Never describe changes in conversational text; doing so does NOT modify disk. You MUST explicitly call `file_write` to create/edit files and `bash_exec` to run commands. Text descriptions are non-operational.
SCORE: Per-requirement pass/fail. Not holistic.
GATE BEFORE COMMIT: Functional end-to-end verification required.
You cannot finish on round 1 even if everything passes — at least 2 rounds of evidence are always required before exit is possible, regardless of the configured minimum.

STATE PERSISTENCE — READ CAREFULLY, THIS IS WHERE MOST FAILURES HAPPEN:
Your state lives in JINX.yaml on disk. You MUST return an updated state block at the end of every response.

- `scores` is merged by round number, so you only need to send THIS round's entry. Any entry whose `round`
  already exists replaces it; rounds you omit are preserved on disk. Deadlock detection and exit criteria
  still see the complete history — they read it from disk, not from what you re-send. Re-sending older
  rounds is still accepted and simply overwrites them, so never rely on it to keep history alive.
- `facts`, `debt`, and `open` are different: each is REPLACED by whatever you send, so send the full list
  from CURRENT STATE each round, not just new items. Near-duplicates are collapsed automatically and
  `facts` is capped (oldest dropped first), so there is no benefit to padding it with restatements.
- `requirements` keys (e.g. `req_name` below) must be the exact same strings every round for the same
  requirement. Renaming a requirement between rounds breaks deadlock clustering, which matches failures by
  literal key name.
- `exit_ready` and `deadlock` must always be included explicitly as real booleans (`true`/`false`, not
  strings) — never omit them.
- Your ENTIRE state block is validated as one unit. One malformed field anywhere inside it — including deep
  inside `approach_graph` — causes the WHOLE block to be rejected and discarded, not just that field. When
  in doubt, leave `approach_graph` out entirely rather than send an incomplete one.
- Output EXACTLY ONE ```yaml fenced code block, and it must be the LAST fenced block in your response. If
  you show any other ```yaml/```json/```yml block earlier (e.g. while reading a config file during TEST),
  that is fine, but never let one appear after your actual state block.

APPROACH KNOWLEDGE GRAPH (optional — include only when it helps):
When a requirement has failed more than once, you may model your technical approach as a semantic knowledge
graph under `approach_graph` so deadlock detection can tell genuinely different strategies apart from
superficial rewordings. If you include it, every node needs both `id` and `type`, and every edge needs
`source`, `target`, and `relation` — incomplete graphs reject the entire state block (see above), so omit
it on rounds where you can't fill it out correctly.
- `nodes`: key entities (files, tools, actions, or concepts), each with a unique `id` and a `type` (one of
  'file', 'tool', 'action', 'concept').
- `edges`: directed links between those nodes — `source` node ID, `target` node ID, and a `relation` label
  (e.g. 'reads', 'modifies', 'tests', 'depends_on').

SELF-IMPROVEMENT — TWO SEPARATE THINGS, DON'T CONFUSE THEM:
1. `lessons` (YOUR CALL, ALWAYS SAFE): send a `lessons` list in your state block to record a
   durable rule distilled from what you actually observed this round. Unlike `facts`/`debt`/`open`,
   lessons are ADDITIVE and survive into future tasks in a separate ledger, so a rule worth keeping
   must be stated as a general, reusable imperative, not a note about this task. Examples:
   "state blocks are validated as one unit, so never leave approach_graph half-filled",
   "measure a notice against the same window you actually send, not the one you persist".
   Send only NEW lessons; duplicates are collapsed automatically. Each round, the lessons you were
   shown are credited or blamed by whether that round passed, so a rule that keeps failing stops
   being shown. Do not pad this list — unproven rules start at zero credit and are dropped at the cap.
2. Editing your own code under `.agent` (POWERFUL, GATED): you MAY edit `.agent/src/jinx/*.py` to
   improve your own results, and that is a legitimate strategy. It is verified automatically: after
   any round that touches framework source, the runner executes the full test suite. If anything
   fails, your edit is REVERTED and you are told exactly what broke — you will not be left with a
   silently broken framework. Rules:
   - Always run the tests yourself before you consider such an edit finished.
   - You may NOT redefine the brake logic: `merge_state`, `StateBlock`, `atomic_write_yaml`,
     `_resolve_jinx_path` in state.py, or `check_exit`, `check_deadlock`, `_resolve_min_rounds`,
     `_handle_llm_response` in runner.py. Writes that do are refused outright, and selfpatch.py and
     learning.py are wholly off limits. These detect a broken framework; an agent that can rewrite
     them cannot be verified by them.
   - Prefer additive, backward-compatible changes. A change that makes the suite green by weakening
     an assertion is worse than no change.

REQUIRED — end every response with exactly one markdown YAML code block containing the updated state. The
schema below shows the SHAPE of each field, not data to copy — replace every value with this task's real
current state. Send only this round's `scores` entry; send `facts`/`debt`/`open` as the full list, and
`lessons` as NEW entries only:

FULL FORMAT (preferred for complex tasks with multiple requirements):
```yaml
id: JINX
protocol:
  loop:
    min: 2
state:
  task: <string — restate the task as you understand it>
  facts: [<every known scope fact/constraint so far, not just new ones>]
  scores:
  - round: 1
    approach: <short name for round 1's strategy>
    prior_failure: <what failed before round 1; "none" if this is round 1>
    requirements: {<requirement_name>: <true|false>}
    pass_count: <int — how many requirements passed>
    all_pass: <true|false>
  - round: 2
    approach: <short name for round 2's strategy — must differ from round 1's>
    prior_failure: <exactly what round 1 failed on>
    requirements: {<requirement_name>: <true|false>}
    pass_count: <int>
    all_pass: <true|false>
  debt: [<every shortcut taken so far, not just new ones>]
  open: [<every unresolved issue so far, not just new ones>]
  lessons: [<only NEW durable rules learned this round, each a general imperative, not a task note>]
  exit_ready: <true|false — true only once all_pass is true on the latest round AND you are not still improving>
  deadlock: <true|false — true only if 3+ genuinely different approaches failed the same requirement>
```
"""

# ==============================================================================
# JINX Prompt Templates & Construction Utilities
# ==============================================================================

MISSING_STATE_WARNING: str = (
    "WARNING: You did not output the REQUIRED markdown YAML state block (```yaml ... ```) at the end of your last response!\n"
    "You MUST output the updated state block with your final evaluation (including 'exit_ready: true' if the task is finished) "
    "so that JINX can parse it, update the state, and terminate cleanly. Do not skip this block!\n"
    "Use CURRENT STATE below as your starting point — send this round's 'scores' entry (the runner merges it "
    "with the history already on disk by round number, so omitted rounds are kept).\n\n"
)

TOOL_DEPTH_CRITICAL_MSG: str = (
    "CRITICAL: The inner tool-calling depth limit has been reached. "
    "Do not call any more tools. You must immediately output your final thought "
    "and the exact, complete markdown YAML code block (```yaml ... ```) to persist your progress and avoid state loss.\n"
    "Being cut off here does not mean the task is done — only set 'exit_ready: true' if the requirements "
    "genuinely all passed. Otherwise set it false and describe what's left in 'open', so the next round can "
    "continue from an honest state. Send this round's 'scores' entry only — it is merged with the history "
    "on disk by round number, so the earlier rounds are preserved without you re-sending them."
)

# History-window notice. Prepended to a request whose bounded window dropped
# earlier messages, so the model does not mistake the window for the session.
HISTORY_ELISION_NOTICE: str = (
    "[context note] %d earlier message(s) from this session were elided from "
    "the history window to bound prompt size; %d of them involved tool "
    "traffic. CURRENT STATE (see 'scores') preserves only each round's "
    "summary -- approach, requirements and pass counts -- not the contents of "
    "tool results, so an elided tool result is NOT recoverable from the state "
    "block. If you need a result that is no longer in this window, call that "
    "tool again rather than assuming you already have its output. Do not "
    "assume this window is the whole session."
)

# One failing check inside a self-patch verification report.
CHECK_FAILURE_LINE: str = "[%s] %s"

# Protection feedback prompts
PROTECTED_FILE_REFUSAL: str = (
    "your edit to JINX's own source modified a protected file (%s). "
    "These files are off-limits to self-patching to prevent the agent from "
    "disabling its own guardrails."
)

PROTECTED_SYMBOL_REFUSAL: str = (
    "your edit to JINX's own source changed protected brake logic "
    "in %s (%s). It was rolled back automatically and NOT verified: "
    "these functions are what stop a self-patch from removing its own "
    "safety checks, so no test result can justify changing them."
)

PROTECTION_CHECK_FAILURE: str = (
    "the protected-logic check could not be completed (%s: %s), so this "
    "edit was neither verified nor accepted"
)

# Self-patch gate feedback. The gate reports the rollback separately from the
# reason, because the two can disagree: a partially failed restore leaves files
# on disk that the model believes were undone, and saying so is the only way it
# can find out.
SELF_PATCH_ROLLBACK_FAILED: str = (
    "SELF-PATCH REFUSED and ROLLBACK FAILED: %s\nThe rollback itself "
    "raised %s: %s. Treat JINX's source as untrustworthy and ask a human "
    "before continuing — the next run's preflight will retry the repair "
    "from the baseline."
)

SELF_PATCH_REFUSED: str = (
    "SELF-PATCH REFUSED: %s\nFiles rolled back: %s"
)

TEST_SUITE_RESTORE_FAILURE: str = (
    "the test files that decide whether this patch is acceptable could "
    "not be restored (%s: %s), so it was not verified against a trusted "
    "suite"
)

# Reported on a patch that PASSED verification. The suite is the yardstick, so
# the model's own test edits are reverted before it runs; without this the model
# would go on believing coverage it just wrote still exists.
TEST_FILES_RESTORED: str = (
    "SELF-PATCH VERIFIED: your edit to the framework was accepted.\n"
    "NOTE: the test files are the yardstick, so they were restored to the "
    "baseline before verification ran. These are back at their baseline state "
    "and no longer contain your changes: %s\n"
    "Your source change is kept, but any test you added or edited for it is "
    "gone. Do not assume that coverage still exists."
)

SELF_PATCH_REVERTED: str = (
    "SELF-PATCH REVERTED: your edit to the files JINX verifies (%s) failed "
    "verification (%s). The change was rolled back automatically, so the "
    "framework is intact — the round was not wasted, it produced evidence. "
    "Read the failure below, decide whether the idea is still right, and if "
    "so apply it in a smaller or more targeted form.\n%s"
)

# Tool-result notices. Not instructions, but handed straight back to the model
# as `tool_result` content, so they belong to the same contract. Exception
# messages raised at the runner itself (IPCError, SerializationError, ...) are
# not model-facing and stay with their raisers.
MALFORMED_TOOL_BLOCK_MSG: str = "Error: Malformed tool_use block (missing id or name)."

INVALID_TOOL_BLOCK_INPUT_MSG: str = "Error: Malformed tool_use block (input must be an object)."

FILE_SLICE_FAILURE_MSG: str = "Error: Failed to slice file content: %s"

# The test-evidence block. `jinx.evidence` decides which failures exist and how
# they group by cause; every phrase the model reads in the digest is assembled
# here, so the wording can be reviewed in one place.
EVIDENCE_HEADER: str = "TEST EVIDENCE (grouped by cause, not by test):"
EVIDENCE_FAILED_COUNT: str = "%d failed"
EVIDENCE_PASSED_COUNT: str = ", %d passed"
EVIDENCE_SKIPPED_COUNT: str = ", %d skipped"
EVIDENCE_CAUSE_COUNT: str = "%d distinct cause(s):"
EVIDENCE_GROUP_LINE: str = "- %s | %s | %d test(s): %s"
EVIDENCE_MORE_EXAMPLES: str = ", ..."
EVIDENCE_MORE_CAUSES: str = "- ...and %d more cause(s), each above the budget"
EVIDENCE_UNDERCOUNTED: str = (
    "WARNING: the run reported %s failure(s) but only %s could be parsed "
    "from the captured output; the tail was truncated, so causes listed "
    "here are partial."
)
EVIDENCE_UNPARSED_WITH_TAIL: str = (
    "TEST EVIDENCE: %s failed but produced no parseable failure line.\n%s"
)
EVIDENCE_UNPARSED: str = (
    "TEST EVIDENCE: %s failed but produced no parseable failure line."
)

# Marker spliced into an elided history so the model sees a gap it cannot read,
# rather than two halves of a transcript that look consecutive.
HISTORY_ELISION_MARKER: str = "... %d line(s) elided by JINX to fit the budget ..."

# Sent back when the state block was valid but carried fewer score entries than
# the loop already stored, which the merge resolves in favour of what is on disk.
STATE_SCORES_MERGED: str = (
    "State accepted. Score history merged by round: %d entr%s on "
    "disk, %d sent this round — %d preserved from earlier rounds. "
    "You may send only the current round's entry from now on."
)

# Refusal returned when a tool call tries to rewrite brake logic. Kept apart from
# PROTECTED_SYMBOL_REFUSAL, which is the message for a change that was already
# written and then rolled back: one is a refusal, the other an explanation.
PROTECTED_EDIT_REFUSAL: str = (
    "Self-patch refused: '%s' defines protected JINX logic (%s). These are "
    "the mechanisms that detect a broken framework, so the agent may not "
    "rewrite them. Change non-brake code in the same file instead, or have "
    "a human set JINX_ALLOW_PROTECTED_EDITS=1 to override deliberately."
)

# Sent back when a submitted state block fails validation. Distinct from
# MISSING_STATE_WARNING, which covers a block that was never sent at all.
STATE_BLOCK_REJECTED: str = (
    "Your previous state block was REJECTED and discarded; the state on "
    "disk is unchanged. Reason: %s: %s. Re-send a corrected block. Common "
    "causes: an unquoted ':' or '#' inside a scalar value, a tab used for "
    "indentation, or a key nested one level too deep. Because the block "
    "was rejected, your exit_ready/deadlock flags were NOT honoured."
)

REASONING_NOTES_HEADER: str = (
    "REASONING NOTES (computed from the score history above, not from this round):"
)


# Learned rules header used when injecting durable lessons into the prompt. Moved
# here so every model-facing phrase lives in prompts.py.
LEARNED_RULES_HEADER: str = (
    "LEARNED RULES (durable, carried over from earlier sessions; "
    "verified rules float up, rules that kept failing are no longer shown):"
)

# Why the four optional fields below exist. The loop protocol already demands
# structural deduction between rounds, but the state it persists keeps only a
# pass/fail flag per requirement, so a wrong belief about the code and a clumsy
# implementation of a correct idea are indistinguishable once the round is over.
# These two blocks are the editable half of that contract: the protocol says what
# to reason with, the notes say what the run's own history says about how well
# that reasoning has been working.
REASONING_PROTOCOL: str = """REASONING PROTOCOL - the loop scores predictions, not prose.

PLAN (before your first tool call this round): one line naming the file or function you will change and the exact command, test or assertion that will prove it. A round with no falsifiable plan can only be narrated, not scored. Put it in this round's scores entry as `plan`.
HYPOTHESIS (same entry, `hypothesis`): a falsifiable prediction - "if I <change>, <requirement> passes because <mechanism>". Name the mechanism. A prediction without one cannot be refuted, and a refutation is the only thing here that teaches you anything.
PREDICTION CHECK (same entry, `prediction_check`): after TEST, set it to `hit`, `miss` or `partial` and name the belief the outcome confirmed or refuted. A miss is the most valuable line in the state: it marks the part of your model of this code that is wrong, and that is exactly what the next round has to change.
CAUSE (same entry, `cause`): classify the PREVIOUS round's failure with exactly one label:
  wrong_target - right idea, wrong file/function/entry point
  wrong_mechanism - right place, but the code does not work the way you assumed
  wrong_hypothesis - the prediction above was refuted: your model is wrong, not your code
  incomplete_test - possibly right, but never exercised by a real command or test
  env_issue - the tool, dependency or environment failed, not the logic
  scope_misread - you solved a different problem than the requirement asked
  unknown - none of the above; append the reason to the same field
The cause decides what may NOT stay the same next round: wrong_target => move the target; wrong_mechanism => change the mechanism; wrong_hypothesis => re-read the code before editing; incomplete_test => run the test before touching code; env_issue => fix the environment first.
The four fields are optional, but the loop measurably reasons better with them: `hypothesis` and `prediction_check` are what produce the PREDICTION RECORD, and `cause` is what turns "pick a different approach" into a decision instead of a guess.
"""

# ==============================================================================
# Tool Declarations (the `tools` field of every llm_generate request)
# ==============================================================================
# The schema is prose aimed at the model, so it lives here with the rest of the
# prompt contract. `jinx.tools.tool_schema` hands out a deep copy of it, so a
# caller mutating the result cannot corrupt the shared template.

TOOL_SCHEMA: List[Dict[str, Any]] = [
    {
        "name": "bash_exec",
        "description": "Execute a bash or shell script in the environment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "The script to execute"
                }
            },
            "required": ["script"]
        }
    },
    {
        "name": "file_read",
        "description": "Read the contents of a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Optional 1-indexed starting line to read (inclusive)"
                },
                "end_line": {
                    "type": "integer",
                    "description": "Optional 1-indexed ending line to read (inclusive)"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "file_write",
        "description": "Write or overwrite a file with new content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file"
                },
                "content": {
                    "type": "string",
                    "description": "The full content to write"
                }
            },
            "required": ["path", "content"]
        }
    }
]


# ==============================================================================
# Reasoning-note text
# ==============================================================================
# Every string the model reads inside the REASONING NOTES block lives here, for the
# same reason the rest of this file exists: the prompt is one artefact, and prose
# split across a computation module and its caller is prose nobody can review in
# one place. `jinx.reasoning` decides *whether* a note fires and with which
# numbers; the wording of the note is assembled here and nowhere else.
#
# Each function takes already-computed data and returns the finished sentence, so
# no model-facing string is ever built by string arithmetic in the caller. An
# empty list or empty string means the note does not apply, which is how the
# reasoning side decides whether to call at all.

# The clause a truncated name list ends with. A list that reads as complete when
# it was cut is a small lie told to a model deciding where to look.
NOTE_MORE_ITEMS = " and %d more"


def note_name_list(names: List[str], limit: int) -> str:
    """Up to ``limit`` quoted names, saying so when the list was cut.

    Used where the note is the only place the model learns the list is partial.
    """
    shown = ", ".join("'%s'" % name for name in names[:limit])
    if len(names) > limit:
        shown += NOTE_MORE_ITEMS % (len(names) - limit)
    return shown


def note_name_list_plain(names: List[str], limit: int) -> str:
    """Up to ``limit`` quoted names, with no mention of what was left out.

    Kept separate from ``note_name_list`` because the notes that use this one
    already name a count or a bound in the same sentence, so announcing the cut
    would double-count; the behaviour is preserved rather than unified.
    """
    return ", ".join("'%s'" % name for name in names[:limit])


def note_calibration(hit: int, miss: int, partial: int, checked: int, rate: int) -> str:
    """How well the model's own predictions about this code have held."""
    note = (
        "PREDICTION RECORD: %d hit, %d miss, %d partial across %d scored round(s) "
        "(%d%% of the predictions you made about this code held)."
        % (hit, miss, partial, checked, rate)
    )
    if miss > hit:
        return note + (
            " More were refuted than confirmed, so the model you are carrying into"
            " this round is the thing under test: re-read the real implementation"
            " of the path you are about to change instead of reasoning about it"
            " from memory, and make this round's hypothesis about something you"
            " have just observed rather than something you expect."
        )
    return note + (
        " The mechanism named in your latest hypothesis is worth extending,"
        " so keep that reasoning and widen its scope rather than restarting"
        " from a new idea."
    )


def note_deadlock_risk(items: List[Tuple[str, int]]) -> str:
    """The one cluster about to abort the run, named by requirement."""
    body = "; ".join(
        "requirement '%s' has now failed under %d structurally different"
        " approaches, and one more distinct approach on it aborts the run"
        " as a deadlock, so change the CATEGORY of approach for that"
        " requirement now instead of reworking the details of the last one"
        % (req, clusters)
        for req, clusters in items
    )
    return "DEADLOCK RISK: " + body + "."


def note_repeated_cause(rounds_text: str, label: str, repeats: int) -> str:
    """Two consecutive rounds that failed the same way under different names."""
    note = "REPEATED CAUSE: rounds %s both failed with cause '%s'" % (rounds_text, label)
    if repeats >= 3:
        note += ", which is %d rounds running" % repeats
    return note + (
        ". The class of mistake did not change, so rewording the approach is not"
        " a new strategy: act on the constraint that label implies, or correct"
        " the label if it was misclassified."
    )


def note_regression(parts: List[str]) -> str:
    """Work an earlier round had already achieved and this one lost."""
    return (
        "REGRESSION: %s. Nothing else in the loop will notice, because check_exit"
        " reads only all_pass of the latest round: restore what was lost before"
        " starting new work." % "; ".join(parts)
    )


def regression_part_broken(named: str) -> str:
    """A requirement that was true earlier and is false now."""
    return "%s passed in an earlier round and is failing in your latest entry" % named


def regression_part_count(latest: int, best: int) -> str:
    """A lower pass count on the same requirement set."""
    return (
        "your latest round scored %d requirements against a best of %d"
        " on the same requirement set" % (latest, best)
    )


def note_attribution(items: List[Tuple[str, int, str]]) -> str:
    """Where the approach graph and the approach sentence disagree.

    ``kind`` is "one_cluster" when the graph is coarser than the prose and
    "many_clusters" when it is finer.
    """
    parts = []
    for req, count, kind in items:
        if kind == "one_cluster":
            parts.append(
                "requirement '%s' has %d differently worded attempts but your"
                " approach graphs put all of them in one cluster, so check_deadlock"
                " cannot see the later attempts as new approaches and its abort will"
                " not fire" % (req, count)
            )
        else:
            parts.append(
                "requirement '%s' has %d structurally distinct approach graphs while"
                " your approach sentences describe a single attempt, so the graphs"
                " claim a variety of approaches that the text does not support and"
                " the cluster count is counting rewrites of one idea" % (req, count)
            )
    return "APPROACH ATTRIBUTION: " + "; ".join(parts) + "."


def note_requirement_keys(dropped: str, flickering: str) -> str:
    """Requirement keys that were being measured and then were not."""
    parts = [
        "%s was scored in earlier rounds and is missing from your latest entry, so"
        " its earlier passes no longer count toward exit and its earlier failures"
        " no longer feed the deadlock check" % dropped
    ]
    if flickering:
        parts.append(
            "%s also flipped between pass and fail while it was being measured, so"
            " one requirement's history is split across two incompatible records"
            % flickering
        )
    return (
        "REQUIREMENT KEYS DROPPED: %s. Either keep measuring them under one"
        " spelling, or retire them explicitly in the state block rather than"
        " letting them fall out." % "; ".join(parts)
    )


# The four conditions check_exit applies, phrased as what is missing rather than
# as a rule, because the plateau rule appears in no prompt and a run refused for
# improving would otherwise be refused with no explanation.
def exit_blocker_min_rounds(min_rounds: int, rnd: int) -> str:
    return (
        "the loop runs at least %d rounds before exit is considered and this is round %d"
        % (min_rounds, rnd)
    )


def exit_blocker_evidence(count: int) -> str:
    return (
        "exit needs at least two scored rounds of evidence and the history holds %d"
        % count
    )


def exit_blocker_not_all_pass() -> str:
    return "your latest round is not all_pass"


def exit_blocker_plateau(last3: int, prior_best: int) -> str:
    return (
        "the last three rounds still beat every earlier round (%d"
        " > %d requirements passed), and the loop only stops at a"
        " plateau" % (last3, prior_best)
    )


def note_exit(blockers: List[str]) -> str:
    """Why a run that looks finished will not be allowed to stop."""
    return (
        "EXIT NOT AVAILABLE: this round reads as finished, but check_exit will not"
        " stop the run - %s. Work the first blocker rather than re-sending the"
        " same state and expecting a different verdict." % "; ".join(blockers)
    )


# One stale citation. Three shapes, kept apart because they need different
# corrections: a file that cannot be found, a line past the end of it, and a
# symbol that has moved since the fact was written.
def citation_unreadable(path_text: str) -> str:
    return (
        "a fact cites %s, which is not a file this loop can read under"
        " the working directory, the package, or the system temp"
        " directory" % path_text
    )


def citation_past_end(path_text: str, cited: int, length: int) -> str:
    return "a fact cites %s:%d in a file of %d lines" % (path_text, cited, length)


def citation_symbol_moved(path_text: str, cited: int, symbol: str, start: int) -> str:
    return (
        "a fact cites %s:%d for %s, which now starts at line %d"
        % (path_text, cited, symbol, start)
    )


def note_citation(problems: List[str]) -> str:
    return (
        "STALE CITATION: %s. A file the loop cannot find is a claim it cannot check"
        " rather than one it has disproved - name the path the way the file sits in"
        " the tree, so the next round can settle it. The substance of a fact is"
        " often still right, but a pointer the model has not checked is how a wrong"
        " line number becomes load-bearing evidence; re-read the file and correct"
        " the fact rather than reasoning from the citation."
        % "; ".join(problems)
    )


# Where the plan probe looks. Named once, because a plan note that describes the
# probe inaccurately sends the model looking for its file in a directory that
# holds it.
PLAN_PROBE_ROOTS = "the working directory, the package, or the system temp directory"


def note_plan(named: str, all_pass: bool) -> str:
    """A path the previous round's plan named that the loop cannot see."""
    if all_pass:
        return (
            "PLAN NOT IN TREE: your last plan named %s, which is not under %s, and"
            " that round scored every requirement as passing. If the pass depended"
            " on that change, the change is not where this loop can see it - find out"
            " what was actually written before treating the requirement as done."
            % (named, PLAN_PROBE_ROOTS)
        )
    return (
        "PLAN NOT IN TREE: your last plan named %s, which is not under %s, so what"
        " that round changed to fix the failing requirements was somewhere this loop"
        " cannot see, or was never written. Name a path this loop can check in the"
        " plan." % (named, PLAN_PROBE_ROOTS)
    )


# The three claims a score entry makes about itself, and the ways they can
# disagree. `plural` is passed in rather than derived from a count here, so the
# grammar of the sentence is decided once, next to the sentence.
def contradiction_non_bool(named: str, plural: bool) -> str:
    return (
        "the verdict%s for %s %s not true/false, and check_deadlock reads every"
        " verdict by truthiness" % ("s" if plural else "", named,
                                    "are" if plural else "is")
    )


def contradiction_pass_count(claimed: int, actual: int) -> str:
    return "pass_count is %d but the requirements map holds %d true verdict(s)" % (
        claimed, actual
    )


def contradiction_all_pass_true(named: str, plural: bool) -> str:
    return "all_pass is true while %s %s false in the same entry" % (
        named, "are" if plural else "is"
    )


def contradiction_all_pass_false(total: int) -> str:
    return "all_pass is false while all %d requirement(s) in the same entry are true" % total


def note_score_contradiction(problems: List[str]) -> str:
    return (
        "SCORE CONTRADICTION: a score entry disagrees with itself, and the brakes"
        " read the halves separately - check_exit decides whether the run may stop"
        " from all_pass alone and builds its plateau rule from pass_count alone,"
        " while check_deadlock reads the requirements map. All three cannot be"
        " true at once: %s. Correct the entry before trusting either verdict."
        % "; ".join(problems)
    )


def round_problem(round_number: Any, problem: str) -> str:
    """One problem, attributed to the round whose entry holds it."""
    return "round %s: %s" % (round_number, problem)


# What a drifted mirror is no longer able to tell the model. Named per key so the
# drift note says which advice is missing rather than that something is.
MIRROR_LOST_LABELS: Dict[str, str] = {
    "exit": "why the run cannot exit yet",
    "similarity": (
        "whether a requirement is close to a deadlock and whether the"
        " approach graphs match the attempts they describe"
    ),
}


def note_mirror_drift(keys: List[str]) -> str:
    lost = [MIRROR_LOST_LABELS[key] for key in keys if key in MIRROR_LOST_LABELS]
    return (
        "MIRROR DRIFT: %s could not be reported, because the advisory computation"
        " no longer matches the protected logic it describes and would be claiming"
        " from a rule that has changed underneath it. Treat the rest of this block"
        " as incomplete for this round." % ", ".join(lost)
    )


def assemble_notes(header: str, parts: List[str], max_chars: int) -> str:
    """Joins the notes that fit the budget, in the order they were produced.

    An over-budget note is dropped rather than truncated, so a late note can never
    cost an urgent one its space, and an empty part never reaches the block: a
    header with no body reads as a truncated message and spends tokens saying
    nothing. The caller owns the order, because priority is a decision about what
    the model should read first.
    """
    kept: List[str] = []
    for part in parts:
        if not part:
            continue
        projected = len(header) + 1 + sum(len(p) + 1 for p in kept) + len(part)
        if projected > max_chars:
            continue
        kept.append(part)
    if not kept:
        return ""
    return "%s\n%s" % (header, "\n".join(kept))


def construct_round_prompt(
    rnd: int, min_rounds: int, state_dump: str, missing_state: bool = False,
    lessons_text: str = "",
) -> str:
    """Constructs the structured user prompt for a specific execution round in the cognitive loop.

    Args:
        rnd (int): The current execution round index.
        min_rounds (int): The minimum configured round threshold.
        state_dump (str): The serialized YAML or JSON string representing the current state block.
        missing_state (bool): If True, prepends the missing state block warning message.
        lessons_text (str): Pre-rendered, already-bounded LEARNED RULES block from the
            durable cross-run ledger. Passed in pre-rendered so the cost bound lives
            in one place (``learning.render_lessons``) instead of being re-derived here.

    Returns:
        str: The fully-formed, formatted user prompt string for the cognitive loop.
    """
    warning_prefix = MISSING_STATE_WARNING if missing_state else ""
    round_label = f"ROUND {rnd} (at least {min_rounds} rounds required before exit is considered)"
    sections = [f"{warning_prefix}{round_label}\nCURRENT STATE:\n{state_dump}"]
    notes = reasoning.render_notes(
        state_dump, REASONING_NOTES_HEADER, min_rounds=min_rounds, rnd=rnd,
    )
    if notes:
        sections.append(notes)
    if reasoning.scores_from_dump(state_dump):
        sections.append(REASONING_PROTOCOL)
    if lessons_text:
        sections.append(lessons_text)
    return "\n\n".join(sections)
