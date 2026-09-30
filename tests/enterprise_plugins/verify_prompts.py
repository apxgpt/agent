# ==============================================================================
# AI-Generated Enterprise Verification Plugin
# Module: jinx.prompts
# Generated At: 2026-09-30T13:53:32Z
#
# This file is dynamically managed by the JINX AI Synthesis Engine.
# Public classes and methods are verified automatically.
# Add custom verification logic in the marked block below to prevent deletion.
# ==============================================================================
import sys
import importlib
from jinx_test import VerificationPhase, EnterpriseVerificationSuite

class VerifyPromptsPhase(VerificationPhase):
    @property
    def name(self) -> str:
        return "verify_prompts"

    @property
    def title(self) -> str:
        return "Phase AI: Dynamic Verification of jinx.prompts"

    def run(self, suite: EnterpriseVerificationSuite) -> bool:
        success = True
        suite.print_badge("Initiating AI-Synthesized Verification for jinx.prompts", True)
        
        # Dynamic import of the target module
        try:
            target_module = importlib.import_module("jinx.prompts")
            suite.print_badge("Import of jinx.prompts: SUCCESS", True)
        except Exception as e:
            suite.print_badge("Import of jinx.prompts: FAILED (" + str(e) + ")", False)
            return False

        # --- CLASS VERIFICATIONS ---
        # --- FUNCTION VERIFICATIONS ---
        # Verify Function note_name_list
        if hasattr(target_module, "note_name_list"):
            suite.print_badge("Function note_name_list: PRESENT", True)
        else:
            suite.print_badge("Function note_name_list: MISSING", False)
            success = False

        # Verify Function note_name_list_plain
        if hasattr(target_module, "note_name_list_plain"):
            suite.print_badge("Function note_name_list_plain: PRESENT", True)
        else:
            suite.print_badge("Function note_name_list_plain: MISSING", False)
            success = False

        # Verify Function note_calibration
        if hasattr(target_module, "note_calibration"):
            suite.print_badge("Function note_calibration: PRESENT", True)
        else:
            suite.print_badge("Function note_calibration: MISSING", False)
            success = False

        # Verify Function note_deadlock_risk
        if hasattr(target_module, "note_deadlock_risk"):
            suite.print_badge("Function note_deadlock_risk: PRESENT", True)
        else:
            suite.print_badge("Function note_deadlock_risk: MISSING", False)
            success = False

        # Verify Function note_repeated_cause
        if hasattr(target_module, "note_repeated_cause"):
            suite.print_badge("Function note_repeated_cause: PRESENT", True)
        else:
            suite.print_badge("Function note_repeated_cause: MISSING", False)
            success = False

        # Verify Function note_regression
        if hasattr(target_module, "note_regression"):
            suite.print_badge("Function note_regression: PRESENT", True)
        else:
            suite.print_badge("Function note_regression: MISSING", False)
            success = False

        # Verify Function regression_part_broken
        if hasattr(target_module, "regression_part_broken"):
            suite.print_badge("Function regression_part_broken: PRESENT", True)
        else:
            suite.print_badge("Function regression_part_broken: MISSING", False)
            success = False

        # Verify Function regression_part_count
        if hasattr(target_module, "regression_part_count"):
            suite.print_badge("Function regression_part_count: PRESENT", True)
        else:
            suite.print_badge("Function regression_part_count: MISSING", False)
            success = False

        # Verify Function note_attribution
        if hasattr(target_module, "note_attribution"):
            suite.print_badge("Function note_attribution: PRESENT", True)
        else:
            suite.print_badge("Function note_attribution: MISSING", False)
            success = False

        # Verify Function note_requirement_keys
        if hasattr(target_module, "note_requirement_keys"):
            suite.print_badge("Function note_requirement_keys: PRESENT", True)
        else:
            suite.print_badge("Function note_requirement_keys: MISSING", False)
            success = False

        # Verify Function exit_blocker_min_rounds
        if hasattr(target_module, "exit_blocker_min_rounds"):
            suite.print_badge("Function exit_blocker_min_rounds: PRESENT", True)
        else:
            suite.print_badge("Function exit_blocker_min_rounds: MISSING", False)
            success = False

        # Verify Function exit_blocker_evidence
        if hasattr(target_module, "exit_blocker_evidence"):
            suite.print_badge("Function exit_blocker_evidence: PRESENT", True)
        else:
            suite.print_badge("Function exit_blocker_evidence: MISSING", False)
            success = False

        # Verify Function exit_blocker_not_all_pass
        if hasattr(target_module, "exit_blocker_not_all_pass"):
            suite.print_badge("Function exit_blocker_not_all_pass: PRESENT", True)
        else:
            suite.print_badge("Function exit_blocker_not_all_pass: MISSING", False)
            success = False

        # Verify Function exit_blocker_plateau
        if hasattr(target_module, "exit_blocker_plateau"):
            suite.print_badge("Function exit_blocker_plateau: PRESENT", True)
        else:
            suite.print_badge("Function exit_blocker_plateau: MISSING", False)
            success = False

        # Verify Function note_exit
        if hasattr(target_module, "note_exit"):
            suite.print_badge("Function note_exit: PRESENT", True)
        else:
            suite.print_badge("Function note_exit: MISSING", False)
            success = False

        # Verify Function citation_unreadable
        if hasattr(target_module, "citation_unreadable"):
            suite.print_badge("Function citation_unreadable: PRESENT", True)
        else:
            suite.print_badge("Function citation_unreadable: MISSING", False)
            success = False

        # Verify Function citation_past_end
        if hasattr(target_module, "citation_past_end"):
            suite.print_badge("Function citation_past_end: PRESENT", True)
        else:
            suite.print_badge("Function citation_past_end: MISSING", False)
            success = False

        # Verify Function citation_symbol_moved
        if hasattr(target_module, "citation_symbol_moved"):
            suite.print_badge("Function citation_symbol_moved: PRESENT", True)
        else:
            suite.print_badge("Function citation_symbol_moved: MISSING", False)
            success = False

        # Verify Function note_citation
        if hasattr(target_module, "note_citation"):
            suite.print_badge("Function note_citation: PRESENT", True)
        else:
            suite.print_badge("Function note_citation: MISSING", False)
            success = False

        # Verify Function note_plan
        if hasattr(target_module, "note_plan"):
            suite.print_badge("Function note_plan: PRESENT", True)
        else:
            suite.print_badge("Function note_plan: MISSING", False)
            success = False

        # Verify Function contradiction_non_bool
        if hasattr(target_module, "contradiction_non_bool"):
            suite.print_badge("Function contradiction_non_bool: PRESENT", True)
        else:
            suite.print_badge("Function contradiction_non_bool: MISSING", False)
            success = False

        # Verify Function contradiction_pass_count
        if hasattr(target_module, "contradiction_pass_count"):
            suite.print_badge("Function contradiction_pass_count: PRESENT", True)
        else:
            suite.print_badge("Function contradiction_pass_count: MISSING", False)
            success = False

        # Verify Function contradiction_all_pass_true
        if hasattr(target_module, "contradiction_all_pass_true"):
            suite.print_badge("Function contradiction_all_pass_true: PRESENT", True)
        else:
            suite.print_badge("Function contradiction_all_pass_true: MISSING", False)
            success = False

        # Verify Function contradiction_all_pass_false
        if hasattr(target_module, "contradiction_all_pass_false"):
            suite.print_badge("Function contradiction_all_pass_false: PRESENT", True)
        else:
            suite.print_badge("Function contradiction_all_pass_false: MISSING", False)
            success = False

        # Verify Function note_score_contradiction
        if hasattr(target_module, "note_score_contradiction"):
            suite.print_badge("Function note_score_contradiction: PRESENT", True)
        else:
            suite.print_badge("Function note_score_contradiction: MISSING", False)
            success = False

        # Verify Function round_problem
        if hasattr(target_module, "round_problem"):
            suite.print_badge("Function round_problem: PRESENT", True)
        else:
            suite.print_badge("Function round_problem: MISSING", False)
            success = False

        # Verify Function note_mirror_drift
        if hasattr(target_module, "note_mirror_drift"):
            suite.print_badge("Function note_mirror_drift: PRESENT", True)
        else:
            suite.print_badge("Function note_mirror_drift: MISSING", False)
            success = False

        # Verify Function assemble_notes
        if hasattr(target_module, "assemble_notes"):
            suite.print_badge("Function assemble_notes: PRESENT", True)
        else:
            suite.print_badge("Function assemble_notes: MISSING", False)
            success = False

        # Verify Function construct_round_prompt
        if hasattr(target_module, "construct_round_prompt"):
            suite.print_badge("Function construct_round_prompt: PRESENT", True)
        else:
            suite.print_badge("Function construct_round_prompt: MISSING", False)
            success = False

        # ==============================================================================
        # <CUSTOM_CODE_START>
        # Add custom assertions and execution tests below. They will be preserved.
        try:
            # Verify existence of required prompt constants
            assert hasattr(target_module, "MISSING_STATE_WARNING"), "MISSING_STATE_WARNING is missing from prompts.py"
            assert hasattr(target_module, "TOOL_DEPTH_CRITICAL_MSG"), "TOOL_DEPTH_CRITICAL_MSG is missing from prompts.py"
            # Reported when a self-patch passed verification but the model's own
            # test files were restored first, so the coverage it just wrote is gone.
            assert hasattr(target_module, "TEST_FILES_RESTORED"), "TEST_FILES_RESTORED is missing from prompts.py"
            suite.print_badge("Prompt Constants: PRESENT", True)

            # Verify content of prompt constants
            assert "REQUIRED markdown YAML state block" in target_module.MISSING_STATE_WARNING
            assert "inner tool-calling depth limit" in target_module.TOOL_DEPTH_CRITICAL_MSG
            # The notice must name the files it reverted, or the model cannot tell
            # which of its tests disappeared.
            assert "%s" in target_module.TEST_FILES_RESTORED, "TEST_FILES_RESTORED must report the affected paths"
            assert "restored" in target_module.TEST_FILES_RESTORED.lower()
            suite.print_badge("Prompt Constants: CORRECT", True)

            # Verify existence of construct_round_prompt function
            assert hasattr(target_module, "construct_round_prompt"), "construct_round_prompt is missing from prompts.py"
            assert callable(target_module.construct_round_prompt), "construct_round_prompt is not callable"
            suite.print_badge("Function construct_round_prompt: PRESENT", True)

            # Test round prompt constructor without missing state
            test_state = "task: Verify Refactoring\nfacts: []"
            res_normal = target_module.construct_round_prompt(rnd=2, min_rounds=5, state_dump=test_state, missing_state=False)
            expected_normal = f"ROUND 2 (at least 5 rounds required before exit is considered)\nCURRENT STATE:\n{test_state}"
            assert res_normal == expected_normal, f"Round prompt mismatch without missing state warning.\nExpected:\n{expected_normal}\nGot:\n{res_normal}"

            # Test round prompt constructor with missing state
            res_warning = target_module.construct_round_prompt(rnd=2, min_rounds=5, state_dump=test_state, missing_state=True)
            expected_warning = f"{target_module.MISSING_STATE_WARNING}ROUND 2 (at least 5 rounds required before exit is considered)\nCURRENT STATE:\n{test_state}"
            assert res_warning == expected_warning, f"Round prompt mismatch with missing state warning.\nExpected:\n{expected_warning}\nGot:\n{res_warning}"

            # Verify task is NOT duplicated: no separate TASK: line in prompt
            assert "TASK:" not in res_normal, "Redundant TASK: line found in prompt — task should only appear inside state_dump"
            assert "TASK:" not in res_warning, "Redundant TASK: line found in prompt — task should only appear inside state_dump"
            
            suite.print_badge("Function construct_round_prompt: BEHAVIOR VERIFIED", True)

        except Exception as e:
            suite.print_badge(f"Dynamic Prompt Verification Failed: {e}", False)
            success = False
        # <CUSTOM_CODE_END>
        # ==============================================================================

        return success
