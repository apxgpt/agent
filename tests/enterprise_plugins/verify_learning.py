# ==============================================================================
# AI-Generated Enterprise Verification Plugin
# Module: jinx.learning
# Generated At: 2026-09-27T17:29:47Z
#
# This file is dynamically managed by the JINX AI Synthesis Engine.
# Public classes and methods are verified automatically.
# Add custom verification logic in the marked block below to prevent deletion.
# ==============================================================================
import sys
import importlib
from jinx_test import VerificationPhase, EnterpriseVerificationSuite

class VerifyLearningPhase(VerificationPhase):
    @property
    def name(self) -> str:
        return "verify_learning"

    @property
    def title(self) -> str:
        return "Phase AI: Dynamic Verification of jinx.learning"

    def run(self, suite: EnterpriseVerificationSuite) -> bool:
        success = True
        suite.print_badge("Initiating AI-Synthesized Verification for jinx.learning", True)
        
        # Dynamic import of the target module
        try:
            target_module = importlib.import_module("jinx.learning")
            suite.print_badge("Import of jinx.learning: SUCCESS", True)
        except Exception as e:
            suite.print_badge("Import of jinx.learning: FAILED (" + str(e) + ")", False)
            return False

        # --- CLASS VERIFICATIONS ---
        # --- FUNCTION VERIFICATIONS ---
        # Verify Function normalize_lesson_text
        if hasattr(target_module, "normalize_lesson_text"):
            suite.print_badge("Function normalize_lesson_text: PRESENT", True)
        else:
            suite.print_badge("Function normalize_lesson_text: MISSING", False)
            success = False

        # Verify Function add_lessons
        if hasattr(target_module, "add_lessons"):
            suite.print_badge("Function add_lessons: PRESENT", True)
        else:
            suite.print_badge("Function add_lessons: MISSING", False)
            success = False

        # Verify Function record_outcome
        if hasattr(target_module, "record_outcome"):
            suite.print_badge("Function record_outcome: PRESENT", True)
        else:
            suite.print_badge("Function record_outcome: MISSING", False)
            success = False

        # Verify Function render_lessons
        if hasattr(target_module, "render_lessons"):
            suite.print_badge("Function render_lessons: PRESENT", True)
        else:
            suite.print_badge("Function render_lessons: MISSING", False)
            success = False

        # Verify Function load_ledger
        if hasattr(target_module, "load_ledger"):
            suite.print_badge("Function load_ledger: PRESENT", True)
        else:
            suite.print_badge("Function load_ledger: MISSING", False)
            success = False

        # Verify Function save_ledger
        if hasattr(target_module, "save_ledger"):
            suite.print_badge("Function save_ledger: PRESENT", True)
        else:
            suite.print_badge("Function save_ledger: MISSING", False)
            success = False

        # ==============================================================================
        # <CUSTOM_CODE_START>
        # Behavioural verification for the lesson ledger. The generated checks
        # above only prove the module's names exist.
        def _assert(label, ok):
            suite.print_badge(label, bool(ok))
            return bool(ok)

        # The 300-character cap is a storage bound applied in
        # normalize_lesson_text. Nothing asserted it: render_lessons enforces
        # the aggregate prompt budget by dropping whole entries, so deleting
        # the per-rule cap leaves every other check green while letting an
        # unbounded rule into the ledger.
        _stored = target_module.normalize_lesson_text("word " * 5000)
        if not _assert(
            "normalize_lesson_text: an overlong rule is capped at 300 chars",
            isinstance(_stored, str) and len(_stored) == 300,
        ):
            success = False
        if not _assert(
            "normalize_lesson_text: the cap truncates rather than rejecting",
            isinstance(_stored, str) and _stored.startswith("word word"),
        ):
            success = False
        if not _assert(
            "normalize_lesson_text: a short rule is left untouched",
            target_module.normalize_lesson_text("  a   b  ") == "a b",
        ):
            success = False
        if not _assert(
            "normalize_lesson_text: unusable input is dropped, not stored",
            target_module.normalize_lesson_text(None) is None
            and target_module.normalize_lesson_text("   ") is None,
        ):
            success = False
        # <CUSTOM_CODE_END>
        # ==============================================================================

        return success
