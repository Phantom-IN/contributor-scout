#!/usr/bin/env python3
"""Apply the Contributor Scout contribution-success scoring rubric.

Part of the Contributor Scout skill (Phase 7: scoring).

Scoring must be deterministic, so the model never hand-computes a total. Each of
the ten rubric categories is rated 0-5; the script scales each rating by its
weight, applies risk deductions, enforces the duplicate-status gates, and
returns a final score with its recommendation band.

Rubric (100 points before deductions)
-------------------------------------
    evidence_problem_real          15
    user_project_impact            15
    maintainer_alignment           15
    non_duplication_confidence     15
    technical_solution_confidence  10
    scope_clarity                  10
    testability                     5
    backward_compatibility          5
    historical_justification        5
    contributor_fit                 5

Rating anchors are defined in references/contribution-quality-rubric.md.

Usage
-----
    python3 calculate_candidate_score.py --example > candidates.json
    python3 calculate_candidate_score.py --input candidates.json
    python3 calculate_candidate_score.py --input candidates.json --format markdown
    cat candidates.json | python3 calculate_candidate_score.py --input -

Input is either a single candidate object or {"candidates": [ ... ]}.

Exit codes
----------
    0  all candidates scored with no blocking errors
    1  bad arguments or unreadable input
    2  at least one candidate has a blocking error
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_VERSION = "1.0.0"
RUBRIC_VERSION = "1.0.0"
MAX_RATING = 5

WEIGHTS: List[Tuple[str, int, str]] = [
    ("evidence_problem_real", 15, "Evidence that the problem or opportunity is real"),
    ("user_project_impact", 15, "User or project impact"),
    ("maintainer_alignment", 15, "Maintainer and roadmap alignment"),
    ("non_duplication_confidence", 15, "Non-duplication confidence"),
    ("technical_solution_confidence", 10, "Technical solution confidence"),
    ("scope_clarity", 10, "Scope clarity"),
    ("testability", 5, "Testability"),
    ("backward_compatibility", 5, "Backward compatibility"),
    ("historical_justification", 5, "Historical justification"),
    ("contributor_fit", 5, "Contributor ability to implement and explain"),
]
WEIGHT_BY_KEY = {key: weight for key, weight, _ in WEIGHTS}
LABEL_BY_KEY = {key: label for key, _, label in WEIGHTS}

DEDUCTIONS: List[Tuple[str, int, str]] = [
    ("overlapping_open_pr", -30, "Open or draft PR materially overlaps"),
    ("previously_rejected", -30, "Maintainers previously rejected the same approach"),
    ("no_reproducible_evidence", -20, "No reproducible evidence"),
    ("repository_inactive", -20, "Repository appears inactive"),
    ("breaking_api_change", -15, "Breaking public API change required"),
    ("major_new_dependency", -10, "Major new dependency required"),
    ("unclear_ownership_or_scope", -10, "Unclear ownership or scope"),
]
DEDUCTION_BY_KEY = {key: (points, label) for key, points, label in DEDUCTIONS}

BANDS: List[Tuple[int, int, str, str]] = [
    (85, 100, "EXCELLENT", "Excellent contribution candidate"),
    (70, 84, "STRONG", "Strong candidate"),
    (55, 69, "DISCUSS", "Discuss with maintainers before implementation"),
    (40, 54, "WEAK", "Weak candidate; pursue only with new evidence"),
    (0, 39, "DO_NOT_PURSUE", "Do not pursue"),
]

VALID_DUPLICATE_STATUS = {
    "CLEAR", "RELATED", "PARTIALLY_COVERED", "CLAIMED",
    "DUPLICATE", "REJECTED", "SUPERSEDED", "UNKNOWN",
}
# Statuses that disqualify a candidate outright.
BLOCKING_DUPLICATE_STATUS = {"DUPLICATE", "CLAIMED", "REJECTED", "SUPERSEDED"}
VALID_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
VALID_CATEGORY = {"security", "performance", "feature"}

EXAMPLE = {
    "candidates": [
        {
            "id": "PERF-001",
            "category": "performance",
            "title": "Configuration is re-parsed on every request",
            "duplicate_status": "CLEAR",
            "duplicate_confidence": "HIGH",
            "ratings": {
                "evidence_problem_real": 5,
                "user_project_impact": 4,
                "maintainer_alignment": 4,
                "non_duplication_confidence": 5,
                "technical_solution_confidence": 4,
                "scope_clarity": 5,
                "testability": 4,
                "backward_compatibility": 5,
                "historical_justification": 5,
                "contributor_fit": 4,
            },
            "risks": {
                "overlapping_open_pr": False,
                "previously_rejected": False,
                "no_reproducible_evidence": False,
                "repository_inactive": False,
                "breaking_api_change": False,
                "major_new_dependency": False,
                "unclear_ownership_or_scope": False,
            },
            "rating_notes": {
                "maintainer_alignment": "Issue #412 labelled 'help wanted' "
                                        "mentions startup cost - [MAINTAINER]",
            },
        }
    ]
}


def band_for(score: int) -> Tuple[str, str]:
    for low, high, key, label in BANDS:
        if low <= score <= high:
            return key, label
    return "DO_NOT_PURSUE", "Do not pursue"


def score_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Score one candidate. Never raises - problems are returned as errors."""
    errors: List[str] = []      # blocking
    warnings: List[str] = []    # advisory

    candidate_id = candidate.get("id") or "<missing id>"
    if not candidate.get("id"):
        errors.append("missing required field 'id'")

    category = candidate.get("category")
    if category not in VALID_CATEGORY:
        errors.append(
            "'category' must be one of {0} (got {1!r})".format(
                sorted(VALID_CATEGORY), category))

    if not candidate.get("title"):
        warnings.append("missing 'title' - the scorecard will be hard to read")

    # ---- duplicate status gates -------------------------------------------
    status = candidate.get("duplicate_status")
    if status not in VALID_DUPLICATE_STATUS:
        errors.append(
            "'duplicate_status' must be one of {0} (got {1!r}). Duplicate "
            "detection is mandatory.".format(sorted(VALID_DUPLICATE_STATUS), status))
        status = None

    confidence = candidate.get("duplicate_confidence")
    if confidence not in VALID_CONFIDENCE:
        errors.append(
            "'duplicate_confidence' must be one of {0} (got {1!r})".format(
                sorted(VALID_CONFIDENCE), confidence))

    # ---- ratings -----------------------------------------------------------
    raw_ratings = candidate.get("ratings")
    if not isinstance(raw_ratings, dict):
        errors.append("'ratings' must be an object with all ten rubric categories")
        raw_ratings = {}

    ratings: Dict[str, int] = {}
    for key, _weight, label in WEIGHTS:
        if key not in raw_ratings:
            errors.append("missing rating '{0}' ({1})".format(key, label))
            continue
        value = raw_ratings[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append("rating '{0}' must be a number 0-{1}".format(key, MAX_RATING))
            continue
        if not 0 <= value <= MAX_RATING:
            errors.append("rating '{0}' must be between 0 and {1} (got {2})".format(
                key, MAX_RATING, value))
            continue
        ratings[key] = int(round(value))

    for unknown in set(raw_ratings) - set(WEIGHT_BY_KEY):
        warnings.append("unknown rating key ignored: '{0}'".format(unknown))

    # Duplicate-status gates act on the non-duplication rating.
    gate_applied: Optional[str] = None
    if status in BLOCKING_DUPLICATE_STATUS:
        ratings["non_duplication_confidence"] = 0
        gate_applied = (
            "duplicate_status '{0}' forces non_duplication_confidence to 0 and "
            "band DO_NOT_PURSUE".format(status))
        errors.append(
            "duplicate_status '{0}' disqualifies this candidate - it must not be "
            "shortlisted".format(status))
    elif status == "UNKNOWN" and ratings.get("non_duplication_confidence", 0) > 2:
        ratings["non_duplication_confidence"] = 2
        gate_applied = ("duplicate_status UNKNOWN caps "
                        "non_duplication_confidence at 2")
        warnings.append(gate_applied + " - a human must verify before implementation")

    if status == "CLEAR" and confidence == "LOW":
        errors.append(
            "duplicate_status CLEAR is not permitted with confidence LOW - use "
            "UNKNOWN when the remote could not be checked")

    # ---- risk flags --------------------------------------------------------
    raw_risks = candidate.get("risks") or {}
    if not isinstance(raw_risks, dict):
        errors.append("'risks' must be an object of boolean flags")
        raw_risks = {}
    for unknown in set(raw_risks) - set(DEDUCTION_BY_KEY):
        warnings.append("unknown risk flag ignored: '{0}'".format(unknown))

    applied_deductions: List[Dict[str, Any]] = []
    total_deduction = 0
    for key, points, label in DEDUCTIONS:
        flag = raw_risks.get(key, False)
        if not isinstance(flag, bool):
            warnings.append("risk flag '{0}' should be a boolean".format(key))
            flag = bool(flag)
        if flag:
            applied_deductions.append({"key": key, "label": label, "points": points})
            total_deduction += points

    # Consistency checks between ratings and declared risks.
    if (ratings.get("evidence_problem_real", 5) <= 2
            and not raw_risks.get("no_reproducible_evidence")):
        warnings.append(
            "evidence_problem_real <= 2 but 'no_reproducible_evidence' is not "
            "flagged - declare risk flags honestly")
    if (ratings.get("backward_compatibility", 5) == 0
            and not raw_risks.get("breaking_api_change")):
        warnings.append(
            "backward_compatibility is 0 but 'breaking_api_change' is not flagged")

    # ---- arithmetic --------------------------------------------------------
    category_scores: List[Dict[str, Any]] = []
    subtotal = 0.0
    for key, weight, label in WEIGHTS:
        rating = ratings.get(key)
        points = 0.0 if rating is None else round(weight * rating / MAX_RATING, 2)
        subtotal += points
        category_scores.append({
            "key": key, "label": label, "weight": weight,
            "rating": rating, "points": points,
            "note": (candidate.get("rating_notes") or {}).get(key),
        })

    subtotal_rounded = int(round(subtotal))
    final = max(0, min(100, subtotal_rounded + total_deduction))

    if status in BLOCKING_DUPLICATE_STATUS:
        band_key, band_label = "DO_NOT_PURSUE", "Do not pursue"
        final = min(final, 39)
    elif errors:
        # A candidate with blocking errors must never display as a good one.
        band_key = "INVALID"
        band_label = "Invalid - fix the blocking errors before using this score"
    else:
        band_key, band_label = band_for(final)

    return {
        "id": candidate_id,
        "category": category,
        "title": candidate.get("title"),
        "duplicate_status": candidate.get("duplicate_status"),
        "duplicate_confidence": candidate.get("duplicate_confidence"),
        "category_scores": category_scores,
        "weighted_subtotal": subtotal_rounded,
        "deductions_applied": applied_deductions,
        "total_deduction": total_deduction,
        "final_score": final,
        "band": band_key,
        "band_label": band_label,
        "gate_applied": gate_applied,
        "blocking_errors": errors,
        "warnings": warnings,
        "scoreable": not errors,
        "shortlist_eligible": (
            not errors
            and status not in BLOCKING_DUPLICATE_STATUS
            and band_key in {"EXCELLENT", "STRONG"}
        ),
    }


def render_markdown(results: List[Dict[str, Any]]) -> str:
    """Emit tables that drop straight into 04-candidate-scorecard.md."""
    out: List[str] = []
    out.append("### Ranking\n")
    out.append("| Rank | ID | Category | Title | Score | Band |")
    out.append("|---|---|---|---|---|---|")
    ranked = sorted(results, key=lambda r: -r["final_score"])
    for index, result in enumerate(ranked, start=1):
        out.append("| {0} | `{1}` | {2} | {3} | {4} | {5} |".format(
            index, result["id"], result.get("category") or "-",
            result.get("title") or "-", result["final_score"], result["band_label"]))

    for result in ranked:
        out.append("\n### `{0}` - {1}\n".format(result["id"], result.get("title") or ""))
        out.append("| Category | Weight | Rating | Points |")
        out.append("|---|---|---|---|")
        for score in result["category_scores"]:
            out.append("| {0} | {1} | {2} | {3} |".format(
                score["label"], score["weight"],
                "-" if score["rating"] is None else score["rating"], score["points"]))
        out.append("| **Weighted subtotal** | **100** | | **{0}** |".format(
            result["weighted_subtotal"]))

        if result["deductions_applied"]:
            out.append("\n| Risk deduction | Points |")
            out.append("|---|---|")
            for deduction in result["deductions_applied"]:
                out.append("| {0} | {1} |".format(deduction["label"], deduction["points"]))
            out.append("| **Total deductions** | **{0}** |".format(result["total_deduction"]))
        else:
            out.append("\nNo risk deductions applied.")

        out.append("\n**Final score: {0}/100 - {1}**".format(
            result["final_score"], result["band_label"]))
        if result["gate_applied"]:
            out.append("\n> Gate: {0}".format(result["gate_applied"]))
        for error in result["blocking_errors"]:
            out.append("\n> **BLOCKING:** {0}".format(error))
        for warning in result["warnings"]:
            out.append("\n> Warning: {0}".format(warning))
    return "\n".join(out) + "\n"


def load_input(source: str) -> Any:
    if source == "-":
        return json.load(sys.stdin)
    path = Path(source).expanduser()
    if not path.is_file():
        raise FileNotFoundError("input file not found: {0}".format(path))
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply the Contributor Scout scoring rubric deterministically "
                    "(Phase 7).",
        epilog="Rating anchors: references/contribution-quality-rubric.md. "
               "Use --example to print a valid input document.",
    )
    parser.add_argument("--input", help="JSON file, or '-' for stdin")
    parser.add_argument("--output", help="Write results here (default: stdout)")
    parser.add_argument("--format", choices=["json", "markdown"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--example", action="store_true",
                        help="Print an example input document and exit")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return 0
    if not args.input:
        print("error: --input is required (or use --example)", file=sys.stderr)
        return 1

    try:
        data = load_input(args.input)
    except (OSError, FileNotFoundError) as exc:
        print("error: {0}".format(exc), file=sys.stderr)
        return 1
    except ValueError as exc:
        print("error: input is not valid JSON: {0}".format(exc), file=sys.stderr)
        return 1

    if isinstance(data, dict) and "candidates" in data:
        candidates = data["candidates"]
    elif isinstance(data, list):
        candidates = data
    elif isinstance(data, dict):
        candidates = [data]
    else:
        print("error: expected an object or a list of candidate objects",
              file=sys.stderr)
        return 1

    if not isinstance(candidates, list) or not candidates:
        print("error: no candidates found in input", file=sys.stderr)
        return 1

    results = []
    for entry in candidates:
        if not isinstance(entry, dict):
            print("error: each candidate must be an object", file=sys.stderr)
            return 1
        results.append(score_candidate(entry))

    blocking = sum(len(r["blocking_errors"]) for r in results)

    if args.format == "markdown":
        payload = render_markdown(results)
    else:
        payload = json.dumps({
            "schema": "contributor-scout/scores",
            "schema_version": "1.0.0",
            "script_version": SCRIPT_VERSION,
            "rubric_version": RUBRIC_VERSION,
            "scored_at": datetime.now(timezone.utc).isoformat(),
            "candidate_count": len(results),
            "blocking_error_count": blocking,
            "results": sorted(results, key=lambda r: -r["final_score"]),
            "bands": [{"min": low, "max": high, "key": key, "label": label}
                      for low, high, key, label in BANDS],
        }, indent=args.indent)

    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload if payload.endswith("\n") else payload + "\n",
                               encoding="utf-8")
        print("wrote {0}".format(output_path))
    else:
        print(payload)

    if blocking:
        print("\n{0} blocking error(s) across {1} candidate(s) - these candidates "
              "must not be shortlisted.".format(blocking, len(results)),
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
