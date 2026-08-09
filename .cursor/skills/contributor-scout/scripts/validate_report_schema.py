#!/usr/bin/env python3
"""Validate the completeness of Contributor Scout discovery reports.

Part of the Contributor Scout skill (Phase 8: completion check).

Checks that a `contribution-discovery/` directory contains the documents the
output contract requires, that every candidate report contains every mandatory
section, and that shortlisted candidates carry the evidence the rubric demands:
source locations, evidence tags, a duplicate status assigned in this run, and a
recommended next action.

The validator is intentionally strict about the things that are easy to skip and
expensive to get wrong - duplicate status, evidence tags, and next actions.

Usage
-----
    python3 validate_report_schema.py --dir contribution-discovery
    python3 validate_report_schema.py --dir contribution-discovery --strict
    python3 validate_report_schema.py --candidate contribution-discovery/candidates/PERF-001.md
    python3 validate_report_schema.py --list-required-sections

Exit codes
----------
    0  valid (warnings may still be present)
    1  bad arguments or missing directory
    2  validation errors found
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_VERSION = "1.0.0"

# Level-2 headings every candidate report must contain, in canonical spelling.
# Mirrors templates/candidate-finding.md. Matching is case-insensitive and
# ignores trailing punctuation.
REQUIRED_SECTIONS: List[str] = [
    "Classification and disposition",
    "Executive summary",
    "Project and user impact",
    "Affected components and exact source locations",
    "Current behaviour",
    "Expected behaviour",
    "Root cause or capability gap",
    "Evidence",
    "Reproduction, benchmark, or demand evidence",
    "Existing mitigations and false-positive analysis",
    "Related issues, PRs, discussions, and recent commits",
    "Introducing commit and original PR",
    "Historical design constraints",
    "Changed assumptions",
    "Proposed solution direction",
    "Alternative solutions considered",
    "Minimum PR scope",
    "Optional follow-ups",
    "Explicit exclusions",
    "Backward compatibility and maintenance cost",
    "Required tests and documentation",
    "Maintainer-facing pitch",
    "Duplicate status and confidence",
    "Overall score",
    "Confidence",
    "Recommended next action",
    "Open questions",
    "Rejection conditions",
]

# Shorter contract for REJECTED-*.md files.
REQUIRED_REJECTED_SECTIONS: List[str] = [
    "What was proposed",
    "Primary rejection reason",
    "Falsifying evidence",
    "Duplicate status",
    "Reconsider if",
]

EXPECTED_TOP_LEVEL_DOCS = [
    "00-repository-profile.md",
    "01-architecture-and-context.md",
    "02-existing-work-map.md",
    "03-review-coverage.md",
    "04-candidate-scorecard.md",
    "05-final-recommendation.md",
]

EXPECTED_EVIDENCE_FILES = [
    "commands-run.md",
    "source-locations.json",
    "github-searches.json",
    "unresolved-questions.md",
]

EXPECTED_MACHINE_READABLE = [
    "repository-profile.json",
    "candidates.json",
    "final-ranking.json",
]

EVIDENCE_TAGS = ["[CODE]", "[TEST]", "[HISTORY]", "[MAINTAINER]",
                 "[DOCS]", "[INFERENCE]", "[UNVERIFIED]"]

DUPLICATE_STATUSES = ["CLEAR", "RELATED", "PARTIALLY_COVERED", "CLAIMED",
                      "DUPLICATE", "REJECTED", "SUPERSEDED", "UNKNOWN"]

DISPOSITIONS = ["SHORTLIST", "NEEDS_MAINTAINER_INPUT", "HOLD", "REJECT",
                "PRIVATE_DISCLOSURE"]

# path/to/file.ext:12  or  path/to/file.ext:12-34
SOURCE_LOCATION_RE = re.compile(r"[\w./+-]+\.[A-Za-z0-9_]+:\d+(?:-\d+)?")
TEMPLATE_PLACEHOLDER_RE = re.compile(r"<[a-z][^>\n]{2,60}>")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def normalise_heading(text: str) -> str:
    """Lower-case, strip markdown emphasis and trailing punctuation."""
    cleaned = re.sub(r"[*_`]", "", text).strip().rstrip(":.").strip()
    return re.sub(r"\s+", " ", cleaned).lower()


class Report:
    """Accumulates errors and warnings for a whole validation run."""

    def __init__(self) -> None:
        self.errors: List[Dict[str, str]] = []
        self.warnings: List[Dict[str, str]] = []

    def error(self, where: str, message: str) -> None:
        self.errors.append({"file": where, "message": message})

    def warn(self, where: str, message: str) -> None:
        self.warnings.append({"file": where, "message": message})


def read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def find_field(text: str, label: str) -> Optional[str]:
    """Find a `- **Label:** value` or `| Label | value |` style field."""
    bullet = re.search(
        r"^[-*]\s*\**{0}\**\s*:?\**\s*(.+)$".format(re.escape(label)),
        text, re.IGNORECASE | re.MULTILINE)
    if bullet:
        return bullet.group(1).strip()
    row = re.search(
        r"^\|\s*\**{0}\**\s*\|\s*(.+?)\s*\|".format(re.escape(label)),
        text, re.IGNORECASE | re.MULTILINE)
    if row:
        return row.group(1).strip()
    return None


def validate_candidate(path: Path, report: Report, strict: bool) -> Dict[str, Any]:
    """Validate one candidate markdown report."""
    where = str(path)
    result: Dict[str, Any] = {
        "file": where, "id": path.stem, "kind": "candidate",
        "sections_missing": [], "disposition": None,
        "duplicate_status": None, "evidence_tags": [], "valid": True,
    }

    text = read_text(path)
    if text is None:
        report.error(where, "file could not be read")
        result["valid"] = False
        return result

    # Canonical names are REJECTED-nnn.md; also match example/derived filenames.
    is_rejected = "REJECTED" in path.stem.upper()
    required = REQUIRED_REJECTED_SECTIONS if is_rejected else REQUIRED_SECTIONS
    result["kind"] = "rejected" if is_rejected else "candidate"

    present = {normalise_heading(h) for h in HEADING_RE.findall(text)}
    for section in required:
        if normalise_heading(section) not in present:
            result["sections_missing"].append(section)
            report.error(where, "missing required section: '## {0}'".format(section))

    # Disposition
    disposition_field = find_field(text, "Disposition")
    found_dispositions = [d for d in DISPOSITIONS
                          if re.search(r"\b{0}\b".format(d), text)]
    result["disposition"] = disposition_field
    if not found_dispositions:
        report.error(where, "no disposition found - expected one of {0}".format(
            ", ".join(DISPOSITIONS)))

    is_shortlisted = bool(disposition_field and "SHORTLIST" in disposition_field.upper())
    is_private = bool(
        (disposition_field and "PRIVATE_DISCLOSURE" in disposition_field.upper())
        or re.search(r"\bPRIVATE_DISCLOSURE\b", text))

    # Duplicate status
    status_found = [s for s in DUPLICATE_STATUSES
                    if re.search(r"\b{0}\b".format(s), text)]
    result["duplicate_status"] = status_found
    if not status_found:
        report.error(where, "no duplicate status found - duplicate detection is "
                            "mandatory (expected one of {0})".format(
                                ", ".join(DUPLICATE_STATUSES)))

    confidence_field = find_field(text, "Duplicate-detection confidence")
    if not confidence_field:
        report.error(where, "missing 'Duplicate-detection confidence' "
                            "(HIGH / MEDIUM / LOW)")
    elif "CLEAR" in status_found and "LOW" in confidence_field.upper():
        report.error(where, "duplicate status CLEAR is not permitted with "
                            "confidence LOW - use UNKNOWN instead")

    # Evidence tags
    tags = [tag for tag in EVIDENCE_TAGS if tag in text]
    result["evidence_tags"] = tags
    if not tags:
        report.error(where, "no evidence tags found - every material claim must "
                            "carry one of {0}".format(" ".join(EVIDENCE_TAGS)))
    elif is_shortlisted and not ({"[CODE]", "[TEST]"} & set(tags)):
        report.error(where, "a shortlisted candidate needs at least one [CODE] or "
                            "[TEST] claim; only weaker tags were found")

    # Source locations
    locations = SOURCE_LOCATION_RE.findall(text)
    result["source_location_count"] = len(locations)
    if not locations and not is_rejected:
        report.error(where, "no source locations in 'path/to/file.ext:LINE' form")

    # History
    if not is_rejected:
        history_ok = (
            re.search(r"\b[0-9a-f]{7,40}\b", text)
            or re.search(r"not identified|history unavailable|shallow clone",
                         text, re.IGNORECASE)
        )
        if not history_ok:
            report.error(where, "no introducing-commit SHA and no explicit "
                                "statement that history was unavailable")

    # Next action
    if not is_rejected and not re.search(r"##\s*Recommended next action\s*\n+\s*\S",
                                         text, re.IGNORECASE):
        report.error(where, "'Recommended next action' section is empty")

    # Security-specific handling
    if path.stem.upper().startswith("SEC") or "SEC-" in path.stem.upper() or is_private:
        if not re.search(r"disclosure", text, re.IGNORECASE):
            report.error(where, "security candidate has no disclosure "
                                "recommendation")
        if is_private and not re.search(r"do not publish|private disclosure|"
                                        r"handle privately|HANDLING", text,
                                        re.IGNORECASE):
            report.warn(where, "PRIVATE_DISCLOSURE candidate has no handling "
                               "banner - add one so the file is not shared by "
                               "accident")

    # Unfilled template placeholders
    placeholders = TEMPLATE_PLACEHOLDER_RE.findall(text)
    if placeholders:
        message = "{0} unfilled template placeholder(s), e.g. {1}".format(
            len(placeholders), ", ".join(sorted(set(placeholders))[:4]))
        if strict:
            report.error(where, message)
        else:
            report.warn(where, message)

    if "<!--" in text and strict:
        report.warn(where, "template HTML comments remain - remove them from "
                           "generated documents")

    result["valid"] = not any(e["file"] == where for e in report.errors)
    return result


def validate_directory(root: Path, report: Report, strict: bool) -> Dict[str, Any]:
    """Validate the whole contribution-discovery/ tree."""
    where = str(root)
    summary: Dict[str, Any] = {"directory": where, "candidates": []}

    for name in EXPECTED_TOP_LEVEL_DOCS:
        path = root / name
        if not path.is_file():
            # Category-limited modes legitimately omit some documents.
            report.warn(where, "expected document not found: {0} (acceptable if "
                               "the mode did not produce it)".format(name))
        elif path.stat().st_size < 200:
            report.warn(str(path), "document is suspiciously small "
                                   "({0} bytes)".format(path.stat().st_size))

    candidates_dir = root / "candidates"
    if not candidates_dir.is_dir():
        report.error(where, "missing 'candidates/' directory")
        candidate_files: List[Path] = []
    else:
        candidate_files = sorted(candidates_dir.glob("*.md"))
        if not candidate_files:
            report.warn(str(candidates_dir),
                        "no candidate files - acceptable only if the run "
                        "concluded that no contribution meets the threshold")

    for candidate_file in candidate_files:
        summary["candidates"].append(validate_candidate(candidate_file, report, strict))

    evidence_dir = root / "evidence"
    if not evidence_dir.is_dir():
        report.error(where, "missing 'evidence/' directory")
    else:
        for name in EXPECTED_EVIDENCE_FILES:
            if not (evidence_dir / name).is_file():
                report.warn(str(evidence_dir), "expected evidence file not "
                                               "found: {0}".format(name))
        commands = evidence_dir / "commands-run.md"
        if commands.is_file() and commands.stat().st_size < 50:
            report.warn(str(commands), "command log is empty - every command run "
                                       "must be recorded")

    machine_dir = root / "machine-readable"
    if not machine_dir.is_dir():
        report.error(where, "missing 'machine-readable/' directory")
    else:
        for name in EXPECTED_MACHINE_READABLE:
            path = machine_dir / name
            if not path.is_file():
                report.warn(str(machine_dir), "expected file not found: {0}".format(name))
                continue
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                report.error(str(path), "not valid JSON: {0}".format(exc))

    # Cross-check: shortlisted candidates should appear in the final recommendation.
    final = root / "05-final-recommendation.md"
    final_text = read_text(final) if final.is_file() else None
    if final_text:
        no_candidate = re.search(
            r"no contribution currently meets", final_text, re.IGNORECASE)
        shortlisted = [
            c for c in summary["candidates"]
            if c.get("disposition") and "SHORTLIST" in str(c["disposition"]).upper()
        ]
        for candidate in shortlisted:
            if candidate["id"] not in final_text:
                report.error(str(final), "shortlisted candidate '{0}' is not "
                                         "referenced in the final recommendation"
                                         .format(candidate["id"]))
        if len(shortlisted) > 3:
            report.error(str(final), "{0} candidates are shortlisted - the "
                                     "maximum is 3".format(len(shortlisted)))
        if not shortlisted and not no_candidate:
            report.warn(str(final), "no shortlisted candidates and no explicit "
                                    "'No contribution currently meets the "
                                    "required evidence and alignment threshold.' "
                                    "statement")
    return summary


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Contributor Scout discovery report completeness "
                    "(Phase 8).",
        epilog="Errors must be fixed before a run is considered complete. "
               "Warnings should be reviewed and explained.",
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--dir", help="Path to a contribution-discovery/ directory")
    target.add_argument("--candidate", help="Validate a single candidate markdown file")
    parser.add_argument("--strict", action="store_true",
                        help="Treat unfilled template placeholders as errors")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--list-required-sections", action="store_true",
                        help="Print the mandatory candidate sections and exit")
    return parser.parse_args(argv)


def emit_text(report: Report, summary: Dict[str, Any]) -> None:
    if report.errors:
        print("ERRORS ({0}):".format(len(report.errors)))
        for item in report.errors:
            print("  [ERROR] {0}\n          {1}".format(item["file"], item["message"]))
    if report.warnings:
        print("\nWARNINGS ({0}):".format(len(report.warnings)))
        for item in report.warnings:
            print("  [warn]  {0}\n          {1}".format(item["file"], item["message"]))
    candidates = summary.get("candidates", [])
    if candidates:
        print("\nCandidates checked: {0}".format(len(candidates)))
        for candidate in candidates:
            status = "OK" if not candidate["sections_missing"] else "INCOMPLETE"
            print("  {0:<16} {1:<12} sections missing: {2}".format(
                candidate["id"], status, len(candidate["sections_missing"])))
    if not report.errors:
        print("\nVALID - no blocking errors." if not report.warnings
              else "\nVALID with warnings - review them before completing the run.")
    else:
        print("\nINVALID - fix the errors above before completing the run.")


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    if args.list_required_sections:
        print("Mandatory sections for SEC-*/PERF-*/FEAT-* candidate reports:")
        for section in REQUIRED_SECTIONS:
            print("  ## {0}".format(section))
        print("\nMandatory sections for REJECTED-* reports:")
        for section in REQUIRED_REJECTED_SECTIONS:
            print("  ## {0}".format(section))
        return 0

    if not args.dir and not args.candidate:
        print("error: pass --dir or --candidate (or --list-required-sections)",
              file=sys.stderr)
        return 1

    report = Report()
    summary: Dict[str, Any]

    if args.candidate:
        path = Path(args.candidate).expanduser()
        if not path.is_file():
            print("error: candidate file not found: {0}".format(path), file=sys.stderr)
            return 1
        summary = {"candidates": [validate_candidate(path, report, args.strict)]}
    else:
        root = Path(args.dir).expanduser()
        if not root.is_dir():
            print("error: directory not found: {0}".format(root), file=sys.stderr)
            return 1
        summary = validate_directory(root, report, args.strict)

    if args.format == "json":
        print(json.dumps({
            "schema": "contributor-scout/validation",
            "schema_version": "1.0.0",
            "script_version": SCRIPT_VERSION,
            "error_count": len(report.errors),
            "warning_count": len(report.warnings),
            "errors": report.errors,
            "warnings": report.warnings,
            "summary": summary,
            "valid": not report.errors,
        }, indent=2))
    else:
        emit_text(report, summary)

    return 2 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
