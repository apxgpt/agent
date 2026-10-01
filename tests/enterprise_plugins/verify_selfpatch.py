# ==============================================================================
# AI-Generated Enterprise Verification Plugin
# Module: jinx.selfpatch
# Generated At: 2026-09-27T17:29:47Z
#
# This file is dynamically managed by the JINX AI Synthesis Engine.
# Public classes and methods are verified automatically.
# Add custom verification logic in the marked block below to prevent deletion.
# ==============================================================================
import sys
import importlib
from jinx_test import VerificationPhase, EnterpriseVerificationSuite

class VerifySelfpatchPhase(VerificationPhase):
    @property
    def name(self) -> str:
        return "verify_selfpatch"

    @property
    def title(self) -> str:
        return "Phase AI: Dynamic Verification of jinx.selfpatch"

    def run(self, suite: EnterpriseVerificationSuite) -> bool:
        success = True
        suite.print_badge("Initiating AI-Synthesized Verification for jinx.selfpatch", True)
        
        # Dynamic import of the target module
        try:
            target_module = importlib.import_module("jinx.selfpatch")
            suite.print_badge("Import of jinx.selfpatch: SUCCESS", True)
        except Exception as e:
            suite.print_badge("Import of jinx.selfpatch: FAILED (" + str(e) + ")", False)
            return False

        # --- CLASS VERIFICATIONS ---
        # Verify Class ProtectionError
        if hasattr(target_module, "ProtectionError"):
            suite.print_badge("Class ProtectionError: PRESENT", True)
            cls_obj = getattr(target_module, "ProtectionError")
        else:
            suite.print_badge("Class ProtectionError: MISSING", False)
            success = False

        # --- FUNCTION VERIFICATIONS ---
        # Verify Function protection_violations
        if hasattr(target_module, "protection_violations"):
            suite.print_badge("Function protection_violations: PRESENT", True)
        else:
            suite.print_badge("Function protection_violations: MISSING", False)
            success = False

        # Verify Function is_protected_change
        if hasattr(target_module, "is_protected_change"):
            suite.print_badge("Function is_protected_change: PRESENT", True)
        else:
            suite.print_badge("Function is_protected_change: MISSING", False)
            success = False

        # Verify Function within_src_tree
        if hasattr(target_module, "within_src_tree"):
            suite.print_badge("Function within_src_tree: PRESENT", True)
        else:
            suite.print_badge("Function within_src_tree: MISSING", False)
            success = False

        # Verify Function snapshot
        if hasattr(target_module, "snapshot"):
            suite.print_badge("Function snapshot: PRESENT", True)
        else:
            suite.print_badge("Function snapshot: MISSING", False)
            success = False

        # Verify Function changed_files
        if hasattr(target_module, "changed_files"):
            suite.print_badge("Function changed_files: PRESENT", True)
        else:
            suite.print_badge("Function changed_files: MISSING", False)
            success = False

        # Verify Function restore
        if hasattr(target_module, "restore"):
            suite.print_badge("Function restore: PRESENT", True)
        else:
            suite.print_badge("Function restore: MISSING", False)
            success = False

        # Verify Function capture_baseline
        if hasattr(target_module, "capture_baseline"):
            suite.print_badge("Function capture_baseline: PRESENT", True)
        else:
            suite.print_badge("Function capture_baseline: MISSING", False)
            success = False

        # Verify Function baseline_changed
        if hasattr(target_module, "baseline_changed"):
            suite.print_badge("Function baseline_changed: PRESENT", True)
        else:
            suite.print_badge("Function baseline_changed: MISSING", False)
            success = False

        # Verify Function restore_baseline
        if hasattr(target_module, "restore_baseline"):
            suite.print_badge("Function restore_baseline: PRESENT", True)
        else:
            suite.print_badge("Function restore_baseline: MISSING", False)
            success = False

        # Verify Function clear_baseline
        if hasattr(target_module, "clear_baseline"):
            suite.print_badge("Function clear_baseline: PRESENT", True)
        else:
            suite.print_badge("Function clear_baseline: MISSING", False)
            success = False

        # Verify Function verify
        if hasattr(target_module, "verify"):
            suite.print_badge("Function verify: PRESENT", True)
        else:
            suite.print_badge("Function verify: MISSING", False)
            success = False

        # Verify Function guard_tool_call
        if hasattr(target_module, "guard_tool_call"):
            suite.print_badge("Function guard_tool_call: PRESENT", True)
        else:
            suite.print_badge("Function guard_tool_call: MISSING", False)
            success = False

        # ==============================================================================
        # <CUSTOM_CODE_START>
        # Behavioural verification for the self-patch guard. The generated
        # checks above are hasattr-only.
        def _assert(label, ok):
            suite.print_badge(label, bool(ok))
            return bool(ok)

        # guard_tool_call resolves the path against the CWD and only then asks
        # whether it is inside SRC_DIR. That ordering is load-bearing and easy to
        # misread as a filename check, so both halves are pinned: the real brake
        # file is refused, and a same-named file elsewhere is not.
        _real_runner = str(target_module.SRC_DIR / "jinx" / "runner.py")
        _brake_content = "def check_exit(a, b, c):\n    return True\n"

        _reason = target_module.guard_tool_call(_real_runner, _brake_content)
        if not _assert(
            "guard: rewriting check_exit in the real runner.py is refused",
            bool(_reason) and "refused" in _reason.lower(),
        ):
            success = False

        for _label, _content in (
            ("check_deadlock", "def check_deadlock(a, b, c):\n    return True\n"),
            ("min_rounds brake", "def check_exit(scores, min_rounds, rnd):\n    return True\n"),
        ):
            _r = target_module.guard_tool_call(_real_runner, _content)
            if not _assert("guard: %s removal is refused" % _label, bool(_r)):
                success = False

        # A file named runner.py that is not the framework's own must stay
        # writable, otherwise the guard blocks unrelated work.
        if not _assert(
            "guard: a same-named file outside SRC_DIR is not refused",
            target_module.guard_tool_call("runner.py", _brake_content) is None,
        ):
            success = False

        # An edit to non-brake code in the same file is allowed.
        if not _assert(
            "guard: non-brake code in runner.py stays writable",
            target_module.guard_tool_call(_real_runner, "# harmless comment\n") is None,
        ):
            success = False
        # <CUSTOM_CODE_END>
        # ==============================================================================

        return success
