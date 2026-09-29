"""Turns a raw test-run tail into evidence grouped by cause.

Verification hands the model the last 25 lines of output. That tail is a symptom
list, not a diagnosis: it is capped, it keeps the tail rather than the start, and
one broken helper shows up as dozens of near-identical lines with the common
cause nowhere in view. This module groups failures so the model spends its budget
on distinct causes instead of on repeats of one.

Pure functions only. Nothing here runs a suite, writes a file, or decides whether
a patch is acceptable: it reformats output that has already been produced, and the
verdict stays where it belongs.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

SCHEMA: str = "jinx.evidence/1"

# "FAILED tests/test_x.py::test_y - AssertionError: expected >= 0.7"
# The reason is optional: pytest omits it for some outcomes and truncates it.
_FAILURE_RE = re.compile(
    r"^(?:FAILED|ERROR)\s+(?P<nodeid>\S+)(?:\s+-\s+(?P<reason>.*))?$"
)

# "4 failed, 205 passed, 2 skipped in 8.67s"
_COUNTS_RE = re.compile(
    r"(?P<failed>\d+)\s+failed"
    r"(?:,\s*(?P<passed>\d+)\s+passed)?"
    r"(?:,\s*(?P<skipped>\d+)\s+skipped)?"
    r"(?:,\s*(?P<errors>\d+)\s+error)?"
)

# Values that differ between two runs of the same failure and would otherwise
# split one cause into several. Long digit runs, hex ids, durations and paths are
# what pytest embeds in a message and what changes per run. Short numbers are
# deliberately NOT masked: "expected 0.41 >= 0.70" is the diagnostic, and
# replacing it with "~.~" throws away the threshold the model needs to act.
_VOLATILE_RE = re.compile(
    r"(?:[A-Za-z]:\\[^\s'\"]+|/(?:tmp|var|home|Users)/[^\s'\"]+)"
    r"|\b0x[0-9a-fA-F]+\b"
    r"|\b\d{4,}\b"
    r"|\b\d+\.\d+s\b"
    r"|\b[0-9a-f]{8,}\b"
)

# pytest's own separators and colour codes, so a tail captured from a coloured
# terminal still parses.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_RULE_RE = re.compile(r"^[=_\-]{3,}\s*$")

DEFAULT_MAX_GROUPS: int = 8
DEFAULT_MAX_EXAMPLES: int = 3


def strip_noise(line: str) -> str:
    """Removes ANSI codes and collapses a progress-bar line to empty."""
    cleaned = _ANSI_RE.sub("", line).rstrip()
    return "" if _RULE_RE.match(cleaned.strip()) else cleaned


def canonical_reason(reason: str) -> str:
    """Reduces a failure message to the coarse key that identifies its cause.

    Two failures differing only by temp path, hash or timestamp are one cause.
    Short numbers and quoted payloads are kept: they carry the threshold or the
    expected value, and masking them would merge genuinely different faults
    while destroying the information needed to fix them.
    """
    text = strip_noise(reason).strip()
    if not text:
        return "no reason reported"
    head, sep, tail = text.partition(":")
    if sep and len(head) <= 60 and " " not in head.strip():
        return "%s: %s" % (head.strip(), _VOLATILE_RE.sub("~", tail).strip()[:120])
    return _VOLATILE_RE.sub("~", text)[:160]


def group_key(nodeid: str, reason: str) -> Tuple[str, str]:
    """Groups by file and by canonical reason, never by test name.

    The file is the coarse bucket because a patch usually breaks one module, and
    the reason separates genuinely different faults inside the same module.
    """
    nodeid = nodeid.strip()
    path = nodeid.split("::", 1)[0]
    return path, canonical_reason(reason)


def parse_failures(
    text: str, max_examples: int = DEFAULT_MAX_EXAMPLES,
) -> Dict[str, object]:
    """Extracts failures and counts from raw output.

    Returns a dict with ``groups`` (ordered by size, largest first), ``counts``
    and ``unparsed``. ``unparsed`` is reported rather than hidden: a tail the
    parser cannot read is a different failure mode from "nothing failed", and
    conflating the two would let a broken reporter look like a green run.
    """
    failures: List[Tuple[str, str]] = []
    counts: Dict[str, int] = {}
    saw_summary = False
    unparsed: List[str] = []

    for raw in (text or "").splitlines():
        line = strip_noise(raw)
        if not line:
            continue
        match = _FAILURE_RE.match(line)
        if match:
            failures.append((match.group("nodeid"), match.group("reason") or ""))
            continue
        counts_match = _COUNTS_RE.search(line)
        if counts_match and "failed" in line:
            saw_summary = True
            for key in ("failed", "passed", "skipped", "errors"):
                value = counts_match.group(key)
                if value is not None:
                    counts[key] = int(value)
            continue
        if line.startswith(("E ", "E\t")) or "Error" in line or "assert" in line.lower():
            unparsed.append(line)

    grouped: Dict[Tuple[str, str], List[str]] = {}
    samples: Dict[Tuple[str, str], str] = {}
    for nodeid, reason in failures:
        key = group_key(nodeid, reason)
        grouped.setdefault(key, []).append(nodeid)
        if key not in samples:
            samples[key] = strip_noise(reason).strip()[:200] or "no reason reported"

    groups = [
        {
            "file": key[0],
            "reason": key[1],
            "sample": samples[key],
            "count": len(nodeids),
            "examples": nodeids[:max_examples],
        }
        for key, nodeids in grouped.items()
    ]
    groups.sort(key=lambda g: (-int(g["count"]), str(g["file"]), str(g["reason"])))

    reported = counts.get("failed", 0) + counts.get("errors", 0)
    return {
        "schema": SCHEMA,
        "groups": groups,
        "counts": counts,
        "parsed_failures": len(failures),
        "summary_seen": saw_summary,
        # A tail that reports failures the parser never saw is evidence of a
        # different problem than a clean run, and the difference decides whether
        # the model can trust this report.
        "undercounted": bool(counts.get("failed")) and len(failures) < counts["failed"],
        "unparsed": unparsed[:max_examples],
    }


def render_digest(
    report: Dict[str, object], max_groups: int = DEFAULT_MAX_GROUPS,
) -> str:
    """Renders the report as text bounded by ``max_groups``.

    Grouping is the whole point: 45 failures caused by one helper become a
    single line naming the file, the cause and how many tests share it, instead
    of 45 lines that bury the cause.
    """
    groups = list(report.get("groups") or [])  # type: ignore[arg-type]
    counts = dict(report.get("counts") or {})  # type: ignore[arg-type]
    if not groups:
        return ""

    lines: List[str] = ["TEST EVIDENCE (grouped by cause, not by test):"]
    failed = counts.get("failed", 0)
    passed = counts.get("passed")
    if failed or passed is not None:
        summary = "%d failed" % failed
        if passed is not None:
            summary += ", %d passed" % passed
        if counts.get("skipped"):
            summary += ", %d skipped" % counts["skipped"]
        lines.append(summary)
    lines.append("%d distinct cause(s):" % len(groups))

    for group in groups[:max_groups]:
        nodeids = ", ".join(str(e) for e in group["examples"])  # type: ignore[index]
        # The group key is masked and lossy on purpose, so the row shows the
        # first original reason verbatim: the model gets a coarse grouping and a
        # concrete message to act on, rather than a fingerprint it must guess at.
        line = "- %s | %s | %d test(s): %s" % (
            group["file"], group.get("sample") or group["reason"],
            group["count"], nodeids,
        )
        if int(group["count"]) > len(group["examples"]):  # type: ignore[arg-type]
            line += ", ..."
        lines.append(line)
    if len(groups) > max_groups:
        lines.append("- ...and %d more cause(s), each above the budget" % (len(groups) - max_groups))

    if report.get("undercounted"):
        lines.append(
            "WARNING: the run reported %s failure(s) but only %s could be parsed "
            "from the captured output; the tail was truncated, so causes listed "
            "here are partial." % (
                counts.get("failed"), report.get("parsed_failures"),
            )
        )
    return "\n".join(lines)


def evidence_from_check(
    check: Dict[str, object], max_groups: int = DEFAULT_MAX_GROUPS,
) -> Optional[str]:
    """Builds a digest for one verification check, or None if there is nothing.

    ``None`` means "no evidence to add", not "everything passed": a check that
    failed without a parseable summary still warrants a line, so a caller can
    tell silence from absence.
    """
    if check.get("ok") and not str(check.get("tail") or "").strip():
        return None
    tail = str(check.get("tail") or "")
    report = parse_failures(tail)
    digest = render_digest(report, max_groups=max_groups)
    if digest:
        return digest
    if not check.get("ok"):
        return "TEST EVIDENCE: %s failed but produced no parseable failure line." % check.get("name")
    return None
