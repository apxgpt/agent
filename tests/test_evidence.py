from __future__ import annotations

from jinx import evidence


def test_summary_counts_are_parsed_regardless_of_order() -> None:
    report = evidence.parse_failures("1 warning, 1 error, 1 failed in 0.42s")

    assert report["counts"]["failed"] == 1
    assert report["counts"]["errors"] == 1
    assert report["counts"]["warnings"] == 1


def test_summary_with_error_only_tail_is_undercounted_when_failures_are_reported() -> None:
    tail = (
        "ERROR tests/test_api.py::test_traces\n"
        "=========================== short test summary info ============================\n"
        "1 failed, 1 error in 0.42s"
    )

    report = evidence.parse_failures(tail)

    assert report["counts"]["failed"] == 1
    assert report["counts"]["errors"] == 1
    assert report["undercounted"] is True


def test_summary_without_failed_still_counts_errors() -> None:
    report = evidence.parse_failures("1 warning, 1 error in 0.42s")

    assert report["counts"]["errors"] == 1
    assert report["counts"]["warnings"] == 1
    assert report["undercounted"] is True
