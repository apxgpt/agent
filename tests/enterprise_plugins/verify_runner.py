# ==============================================================================
# AI-Generated Enterprise Verification Plugin
# Module: jinx.runner
# Generated At: 2026-09-27T17:29:47Z
#
# This file is dynamically managed by the JINX AI Synthesis Engine.
# Public classes and methods are verified automatically.
# Add custom verification logic in the marked block below to prevent deletion.
# ==============================================================================
import sys
import importlib
from jinx_test import VerificationPhase, EnterpriseVerificationSuite

class VerifyRunnerPhase(VerificationPhase):
    @property
    def name(self) -> str:
        return "verify_runner"

    @property
    def title(self) -> str:
        return "Phase AI: Dynamic Verification of jinx.runner"

    def run(self, suite: EnterpriseVerificationSuite) -> bool:
        success = True
        suite.print_badge("Initiating AI-Synthesized Verification for jinx.runner", True)
        
        # Dynamic import of the target module
        try:
            target_module = importlib.import_module("jinx.runner")
            suite.print_badge("Import of jinx.runner: SUCCESS", True)
        except Exception as e:
            suite.print_badge("Import of jinx.runner: FAILED (" + str(e) + ")", False)
            return False

        # --- CLASS VERIFICATIONS ---
        # Verify Class Dumper
        if hasattr(target_module, "Dumper"):
            suite.print_badge("Class Dumper: PRESENT", True)
            cls_obj = getattr(target_module, "Dumper")
        else:
            suite.print_badge("Class Dumper: MISSING", False)
            success = False

        # Verify Class JinxError
        if hasattr(target_module, "JinxError"):
            suite.print_badge("Class JinxError: PRESENT", True)
            cls_obj = getattr(target_module, "JinxError")
        else:
            suite.print_badge("Class JinxError: MISSING", False)
            success = False

        # Verify Class SerializationError
        if hasattr(target_module, "SerializationError"):
            suite.print_badge("Class SerializationError: PRESENT", True)
            cls_obj = getattr(target_module, "SerializationError")
        else:
            suite.print_badge("Class SerializationError: MISSING", False)
            success = False

        # Verify Class IPCError
        if hasattr(target_module, "IPCError"):
            suite.print_badge("Class IPCError: PRESENT", True)
            cls_obj = getattr(target_module, "IPCError")
        else:
            suite.print_badge("Class IPCError: MISSING", False)
            success = False

        # Verify Class Yaml
        if hasattr(target_module, "Yaml"):
            suite.print_badge("Class Yaml: PRESENT", True)
            cls_obj = getattr(target_module, "Yaml")
            if hasattr(cls_obj, "dump_to_string"):
                suite.print_badge("  - Method Yaml.dump_to_string: PRESENT", True)
            else:
                suite.print_badge("  - Method Yaml.dump_to_string: MISSING", False)
                success = False
            if hasattr(cls_obj, "safe_atomic_write"):
                suite.print_badge("  - Method Yaml.safe_atomic_write: PRESENT", True)
            else:
                suite.print_badge("  - Method Yaml.safe_atomic_write: MISSING", False)
                success = False
            if hasattr(cls_obj, "load_from_file"):
                suite.print_badge("  - Method Yaml.load_from_file: PRESENT", True)
            else:
                suite.print_badge("  - Method Yaml.load_from_file: MISSING", False)
                success = False
        else:
            suite.print_badge("Class Yaml: MISSING", False)
            success = False

        # --- FUNCTION VERIFICATIONS ---
        # Verify Function str_presenter
        if hasattr(target_module, "str_presenter"):
            suite.print_badge("Function str_presenter: PRESENT", True)
        else:
            suite.print_badge("Function str_presenter: MISSING", False)
            success = False

        # Verify Function parse_state_block
        if hasattr(target_module, "parse_state_block"):
            suite.print_badge("Function parse_state_block: PRESENT", True)
        else:
            suite.print_badge("Function parse_state_block: MISSING", False)
            success = False

        # Verify Function check_exit
        if hasattr(target_module, "check_exit"):
            suite.print_badge("Function check_exit: PRESENT", True)
        else:
            suite.print_badge("Function check_exit: MISSING", False)
            success = False

        # Verify Function check_deadlock
        if hasattr(target_module, "check_deadlock"):
            suite.print_badge("Function check_deadlock: PRESENT", True)
        else:
            suite.print_badge("Function check_deadlock: MISSING", False)
            success = False

        # Verify Function get_tool_result_from_editor
        if hasattr(target_module, "get_tool_result_from_editor"):
            suite.print_badge("Function get_tool_result_from_editor: PRESENT", True)
        else:
            suite.print_badge("Function get_tool_result_from_editor: MISSING", False)
            success = False

        # Verify Function request_llm_from_editor
        if hasattr(target_module, "request_llm_from_editor"):
            suite.print_badge("Function request_llm_from_editor: PRESENT", True)
        else:
            suite.print_badge("Function request_llm_from_editor: MISSING", False)
            success = False

        # Verify Function clean_up_ipc_files
        if hasattr(target_module, "clean_up_ipc_files"):
            suite.print_badge("Function clean_up_ipc_files: PRESENT", True)
        else:
            suite.print_badge("Function clean_up_ipc_files: MISSING", False)
            success = False

        # Verify Function compact_history_for_request
        if hasattr(target_module, "compact_history_for_request"):
            suite.print_badge("Function compact_history_for_request: PRESENT", True)
        else:
            suite.print_badge("Function compact_history_for_request: MISSING", False)
            success = False

        # Verify Function summarize_dropped_history
        if hasattr(target_module, "summarize_dropped_history"):
            suite.print_badge("Function summarize_dropped_history: PRESENT", True)
        else:
            suite.print_badge("Function summarize_dropped_history: MISSING", False)
            success = False

        # Verify Function write_llm_request
        if hasattr(target_module, "write_llm_request"):
            suite.print_badge("Function write_llm_request: PRESENT", True)
        else:
            suite.print_badge("Function write_llm_request: MISSING", False)
            success = False

        # Verify Function run_file_ipc
        if hasattr(target_module, "run_file_ipc"):
            suite.print_badge("Function run_file_ipc: PRESENT", True)
        else:
            suite.print_badge("Function run_file_ipc: MISSING", False)
            success = False

        # Verify Function run
        if hasattr(target_module, "run"):
            suite.print_badge("Function run: PRESENT", True)
        else:
            suite.print_badge("Function run: MISSING", False)
            success = False

        # ==============================================================================
        # <CUSTOM_CODE_START>
        # Behavioural verification. Everything outside this block is generated by
        # AST introspection and can only prove that a name exists; these checks
        # are the ones that go red when the behaviour breaks.
        import contextlib
        import io
        import json as _json
        import pathlib as _pathlib
        import shutil as _shutil
        import signal as _signal
        import tempfile as _tempfile
        from unittest import mock

        def _assert(label, ok):
            suite.print_badge(label, bool(ok))
            return bool(ok)

        # --- 1. The min_rounds brake -------------------------------------
        # Every generated check above is hasattr-only, and the pure-function
        # tests in tests/test_check_exit.py all pass min_rounds=1 or carry fewer
        # than two scores, so a second condition masks the brake either way.
        # These two pin it from both sides.
        _passing = [
            {"round": 1, "all_pass": True, "pass_count": 5},
            {"round": 2, "all_pass": True, "pass_count": 5},
        ]
        if not _assert(
            "check_exit: a passing history does not exit below min_rounds",
            target_module.check_exit(_passing, min_rounds=10, rnd=2) is False,
        ):
            success = False
        if not _assert(
            "check_exit: exits as soon as min_rounds is reached",
            target_module.check_exit(_passing, min_rounds=2, rnd=2) is True,
        ):
            success = False

        # --- 2. SIGBREAK registration ------------------------------------
        # SIGBREAK is the interrupt Windows actually adds and SIGHUP the one it
        # lacks. Listing only the POSIX set left Ctrl+Break unhandled, so a run
        # died without deleting its IPC files.
        _installed = []
        try:
            target_module._install_signal_handlers()
            for _name in ("SIGINT", "SIGTERM", "SIGBREAK", "SIGHUP"):
                _sig = getattr(_signal, _name, None)
                if _sig is not None and _signal.getsignal(_sig) is target_module._signal_cleanup:
                    _installed.append(_name)
        except Exception as exc:
            suite.print_badge("signal registration raised: %s" % exc, False)
        if not _assert(
            "signals: SIGINT and SIGTERM registered",
            {"SIGINT", "SIGTERM"}.issubset(set(_installed)),
        ):
            success = False
        if hasattr(_signal, "SIGBREAK") and not _assert(
            "signals: SIGBREAK registered (Windows Ctrl+Break)",
            "SIGBREAK" in _installed,
        ):
            success = False

        # --- 3. IPC ownership --------------------------------------------
        # AGENT_DIR is derived from this module's location, not the CWD, so the
        # IPC paths belong to the live session from any working directory. A
        # bystander process (editor, linter, test runner) that imports jinx and
        # is interrupted must leave them alone; only the owner may delete them.
        _scratch = _pathlib.Path(_tempfile.mkdtemp())
        try:
            _files = []
            for _name in ("jinx_request.yaml", "jinx_response.yaml", "jinx_run_state.yaml"):
                _f = _scratch / _name
                _f.write_text("sentinel\n", encoding="utf-8")
                _files.append(_f)

            with mock.patch.object(target_module, "AGENT_DIR", _scratch), \
                 mock.patch.object(target_module, "REQUEST_PATH", _files[0]), \
                 mock.patch.object(target_module, "RESPONSE_PATH", _files[1]), \
                 mock.patch.object(target_module, "RUN_STATE_PATH", _files[2]), \
                 mock.patch.object(target_module, "_IPC_OWNER", False), \
                 mock.patch.object(target_module.os, "_exit", lambda *a, **k: None):
                target_module._signal_cleanup(getattr(_signal, "SIGINT", None), None)
                _bystander_kept = all(_f.exists() for _f in _files)
            if not _assert(
                "ipc: a non-owner process leaves the session files intact", _bystander_kept
            ):
                success = False

            with mock.patch.object(target_module, "AGENT_DIR", _scratch), \
                 mock.patch.object(target_module, "REQUEST_PATH", _files[0]), \
                 mock.patch.object(target_module, "RESPONSE_PATH", _files[1]), \
                 mock.patch.object(target_module, "RUN_STATE_PATH", _files[2]), \
                 mock.patch.object(target_module, "_IPC_OWNER", True), \
                 mock.patch.object(target_module.os, "_exit", lambda *a, **k: None):
                target_module._signal_cleanup(getattr(_signal, "SIGINT", None), None)
                _owner_cleared = not any(_f.exists() for _f in _files)
            if not _assert(
                "ipc: the owning process still cleans up its own files", _owner_cleared
            ):
                success = False
        finally:
            _shutil.rmtree(_scratch, ignore_errors=True)

        # Ownership must be claimed by the session entry point, not by whichever
        # helper happens to write first. Claiming it inside write_llm_request
        # looked correct and was wrong: three other helpers also write these
        # files (_write_tool_request, _write_llm_request_no_tools,
        # _handle_tool_response), so a run that went through the tool-call or
        # no-tools path created the files without owning them and Ctrl+C left
        # them behind. Pinned here because the behaviour test above passes even
        # when the claim sits on the wrong function.
        try:
            import ast
            _tree = ast.parse(
                _pathlib.Path(target_module.__file__).read_text(encoding="utf-8")
            )
            _claimers = [
                _fn.name for _fn in ast.walk(_tree)
                if isinstance(_fn, ast.FunctionDef)
                and any(
                    isinstance(_c, ast.Call) and isinstance(_c.func, ast.Name)
                    and _c.func.id == "_claim_ipc_files"
                    for _c in ast.walk(_fn)
                )
            ]
        except Exception as exc:
            _claimers = ["<parse failed: %s>" % exc]
        if not _assert(
            "ipc: ownership is claimed by run_file_ipc, not by a write helper",
            _claimers == ["run_file_ipc"],
        ):
            success = False

        # prompts.py documents itself as "the single home for every piece of
        # text JINX sends to the model", but model-facing prose had drifted into
        # evidence.py, state.py, selfpatch.py and learning.py. Nothing caught it
        # because nothing checked it. These two assertions pin the contract:
        # every fragment lives in prompts.py, and no other module in the package
        # carries a string literal of its own that a model could read.
        _prompt_modules = sorted(
            p for p in _pathlib.Path(target_module.__file__).parent.glob("*.py")
            if p.name != "prompts.py" and p.name != "__init__.py"
        )
        _expected_prompt_names = (
            "EVIDENCE_HEADER", "EVIDENCE_GROUP_LINE", "EVIDENCE_UNDERCOUNTED",
            "EVIDENCE_UNPARSED", "LEARNED_RULES_HEADER",
            "PROTECTED_EDIT_REFUSAL", "STATE_BLOCK_REJECTED",
        )
        try:
            import jinx.prompts as _prompts_mod
        except Exception:
            _prompts_mod = None
        if not _assert(
            "prompt: the model-facing fragments live in prompts.py",
            _prompts_mod is not None
            and all(hasattr(_prompts_mod, _n) for _n in _expected_prompt_names),
        ):
            success = False

        # The failure mode this exists to stop is a prompt *constant* reappearing
        # outside prompts.py, which is how LEARNED_RULES_HEADER came to sit in
        # learning.py. Only top-level assignments are tested: a log line or an
        # argparse help string lives inside a function and is not model prose, so
        # flagging those would make this check cry wolf on its first run.
        _src_dir = _pathlib.Path(target_module.__file__).parent
        _stray_constants = []
        for _p in _prompt_modules:
            _tree = ast.parse(_p.read_text(encoding="utf-8"))
            for _n in _tree.body:
                _val = None
                _names = []
                if isinstance(_n, ast.Assign):
                    _val = _n.value
                    _names = [t.id for t in _n.targets if isinstance(t, ast.Name)]
                elif isinstance(_n, ast.AnnAssign):
                    _val = _n.value
                    _names = [_n.target.id] if isinstance(_n.target, ast.Name) else []
                if (_val is not None and isinstance(_val, ast.Constant)
                        and isinstance(_val.value, str) and len(_val.value) > 40):
                    _stray_constants.append("%s: %s = %r" % (
                        _p.name, _names[0] if _names else "?", _val.value[:50]))
        if not _assert(
            "prompt: no module outside prompts.py declares prompt prose",
            not _stray_constants,
        ):
            for _s in _stray_constants[:6]:
                print("   prompt text declared outside prompts.py: %s" % _s)
            success = False

        # Each moved fragment must be read from prompts at its use site, so the
        # next person changing the wording has exactly one file to edit.
        _consumer_sites = {
            "evidence.py": ("prompts.EVIDENCE_HEADER", "prompts.EVIDENCE_UNDERCOUNTED"),
            "state.py": ("prompts.STATE_BLOCK_REJECTED", "prompts.STATE_SCORES_MERGED"),
            "selfpatch.py": ("prompts.PROTECTED_EDIT_REFUSAL",),
            "learning.py": ("from .prompts import LEARNED_RULES_HEADER",),
            "runner.py": ("prompts.HISTORY_ELISION_MARKER",),
        }
        _not_rewired = []
        for _mod, _needles in _consumer_sites.items():
            _f = _src_dir / _mod
            _text = _f.read_text(encoding="utf-8") if _f.exists() else ""
            for _needle in _needles:
                if _needle not in _text:
                    _not_rewired.append("%s -> %s" % (_mod, _needle))
        if not _assert(
            "prompt: every consumer reads its fragment from prompts",
            not _not_rewired,
        ):
            for _s in _not_rewired:
                print("   not rewired: %s" % _s)
            success = False


        # --- 4. RPC wire format -------------------------------------------
        # The stdio transport had no coverage at all. A host reads one JSON
        # object per line, so a pretty-printed or multi-line request silently
        # breaks every editor integration.
        _stdout = io.StringIO()
        with mock.patch.object(
            target_module, "_read_stdin_with_retries",
            lambda *a: _json.dumps({"content": [{"type": "text", "text": "ok"}]}),
        ), contextlib.redirect_stdout(_stdout):
            _got = target_module.request_llm_from_editor(
                "SYS", [{"role": "user", "content": "hi"}]
            )
        _emitted = [ln for ln in _stdout.getvalue().splitlines() if ln.strip()]
        if not _assert("rpc: request is exactly one line", len(_emitted) == 1):
            success = False
        else:
            _payload = _json.loads(_emitted[0])
            if not _assert(
                "rpc: request carries jinx_command=llm_generate and the system prompt",
                _payload.get("jinx_command") == "llm_generate"
                and _payload.get("params", {}).get("system") == "SYS",
            ):
                success = False
        if not _assert(
            "rpc: host content blocks are returned verbatim",
            _got == [{"type": "text", "text": "ok"}],
        ):
            success = False

        # A malformed host reply must raise rather than be treated as content.
        for _label, _reply in (
            ("non-list content", _json.dumps({"content": "text"})),
            ("unparseable line", "not json at all"),
            ("no reply (timeout)", None),
        ):
            with mock.patch.object(
                target_module, "_read_stdin_with_retries", lambda *a, _r=_reply: _r
            ):
                try:
                    target_module.request_llm_from_editor("SYS", [])
                    _raised = False
                except target_module.IPCError:
                    _raised = True
                except Exception:
                    _raised = False
            if not _assert("rpc: %s is rejected" % _label, _raised):
                success = False

        # --- 5. RPC protected-write guard --------------------------------
        # run() has its own copy of the dispatch guard; nothing else exercised it.
        _dispatched = []
        with mock.patch.object(
            target_module, "get_tool_result_from_editor",
            lambda *a: _dispatched.append(a[1]) or ("ok", False, False),
        ):
            _refused = target_module._execute_rpc_tool({
                "type": "tool_use", "id": "t1", "name": "file_write",
                "input": {
                    "path": str(target_module.selfpatch.SRC_DIR / "jinx" / "runner.py"),
                    "content": "def check_exit(a, b, c):\n    return True\n",
                },
            })
        if not _assert(
            "rpc: a protected write is refused before reaching the host",
            not _dispatched and "refused" in str(_refused.get("content", "")).lower(),
        ):
            success = False

        _dispatched.clear()
        with mock.patch.object(
            target_module, "get_tool_result_from_editor",
            lambda *a: _dispatched.append(a[1]) or ("ok", False, False),
        ):
            target_module._execute_rpc_tool({
                "type": "tool_use", "id": "t2", "name": "file_write",
                "input": {"path": "evidence.py", "content": "# note\n"},
            })
        if not _assert("rpc: a benign write is dispatched", _dispatched == ["file_write"]):
            success = False

        # --- 6. RPC loop exit arithmetic ----------------------------------
        # The RPC loop re-implements the exit rule instead of reusing
        # run_file_ipc's, so dropping the check_exit() call there would let a
        # single round end the session with nothing else noticing.
        _store = {
            "protocol": {"loop": {"min": 2}},
            "state": {
                "task": "rpc exit arithmetic", "facts": [], "scores": [],
                "debt": [], "open": [], "exit_ready": False, "deadlock": False,
            },
        }
        _rounds = {"n": 0}

        def _fake_request(*a, **k):
            _rounds["n"] += 1
            return [{"type": "text", "text": (
                "```yaml\nid: JINX\nprotocol:\n  loop:\n    min: 2\nstate:\n"
                "  task: rpc exit arithmetic\n  facts: []\n  scores:\n"
                f"    - round: {_rounds['n']}\n      all_pass: true\n      pass_count: 1\n"
                "  debt: []\n  open: []\n  exit_ready: true\n  deadlock: false\n```"
            )}]

        with mock.patch.object(target_module, "read_jinx", lambda *a, **k: _store), \
             mock.patch.object(target_module, "write_jinx", lambda *a, **k: None), \
             mock.patch.object(target_module, "_init_new_session", lambda *a, **k: None), \
             mock.patch.object(target_module, "_install_signal_handlers", lambda: None), \
             mock.patch.object(target_module, "clean_up_ipc_files", lambda: None), \
             mock.patch.object(target_module, "request_llm_from_editor", _fake_request), \
             mock.patch.object(target_module, "HARD_CAP", 8):
            target_module.run("rpc exit arithmetic", min_override=5, ipc_mode="rpc")
        if not _assert(
            "rpc: loop honours min_rounds (%d of 5 rounds)" % _rounds["n"],
            _rounds["n"] == 5,
        ):
            success = False

        # A round whose text has no parsable state block must keep looping and
        # end at HARD_CAP, never exit 0: a rejected block is not a finished run.
        _store2 = {
            "protocol": {"loop": {"min": 2}},
            "state": {
                "task": "rpc rejected block", "facts": [], "scores": [],
                "debt": [], "open": [], "exit_ready": False, "deadlock": False,
            },
        }
        _bad_rounds = {"n": 0}

        def _bad_request(*a, **k):
            _bad_rounds["n"] += 1
            return [{"type": "text", "text": "no state block in this reply"}]

        _hcap_code = None
        try:
            with mock.patch.object(target_module, "read_jinx", lambda *a, **k: _store2), \
                 mock.patch.object(target_module, "write_jinx", lambda *a, **k: None), \
                 mock.patch.object(target_module, "_init_new_session", lambda *a, **k: None), \
                 mock.patch.object(target_module, "_install_signal_handlers", lambda: None), \
                 mock.patch.object(target_module, "clean_up_ipc_files", lambda: None), \
                 mock.patch.object(target_module, "request_llm_from_editor", _bad_request), \
                 mock.patch.object(target_module, "HARD_CAP", 3):
                target_module.run("rpc rejected block", min_override=2, ipc_mode="rpc")
        except SystemExit as exc:
            _hcap_code = exc.code
        if not _assert(
            "rpc: a rejected state block runs to HARD_CAP instead of exiting 0",
            _hcap_code == 2,
        ):
            success = False

        # A malformed tool block has to come back as an error result the host can
        # read, not an exception that kills the run mid-round.
        try:
            _malformed = target_module._execute_rpc_tool({"type": "tool_use"})
            _malformed_ok = (
                isinstance(_malformed, dict) and _malformed.get("type") == "tool_result"
            )
        except Exception:
            _malformed_ok = False
        if not _assert("rpc: a malformed tool block yields a tool_result", _malformed_ok):
            success = False
        # <CUSTOM_CODE_END>
        # ==============================================================================

        return success
