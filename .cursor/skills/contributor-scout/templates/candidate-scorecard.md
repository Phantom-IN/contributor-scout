<!--
TEMPLATE: 04-candidate-scorecard.md  (Phase 7)
All scores must come from scripts/calculate_candidate_score.py. Do not
hand-compute totals.
-->

# Candidate Scorecard: <owner/name>

| Field | Value |
|---|---|
| Generated | `<YYYY-MM-DD>` |
| Analysed at commit | `<short SHA>` |
| Candidates evaluated | `<n>` |
| Shortlisted | `<n>` (maximum 3) |
| Scoring | `scripts/calculate_candidate_score.py` v1.0.0 |

## Ranking

| Rank | ID | Category | Title | Score | Band | Disposition | Duplicate status |
|---|---|---|---|---|---|---|---|
| 1 | `PERF-001` | performance | <title> | <nn> | Strong | SHORTLIST | CLEAR (HIGH) |
| 2 | `FEAT-001` | feature | <title> | <nn> | Discuss | NEEDS_MAINTAINER_INPUT | RELATED (HIGH) |
| 3 | `SEC-001` | security | <title> | <nn> | Do not pursue | PRIVATE_DISCLOSURE | CLEAR (HIGH) |
| - | `REJECTED-001` | <category> | <title> | <nn> | Do not pursue | REJECT | DUPLICATE (HIGH) |

## Category breakdown

| Category (weight) | `PERF-001` | `FEAT-001` | `SEC-001` |
|---|---|---|---|
| Evidence problem is real (15) | | | |
| User or project impact (15) | | | |
| Maintainer alignment (15) | | | |
| Non-duplication confidence (15) | | | |
| Technical solution confidence (10) | | | |
| Scope clarity (10) | | | |
| Testability (5) | | | |
| Backward compatibility (5) | | | |
| Historical justification (5) | | | |
| Contributor fit (5) | | | |
| **Weighted subtotal** | | | |

## Risk deductions

| Risk | Deduction | `PERF-001` | `FEAT-001` | `SEC-001` |
|---|---|---|---|---|
| Overlapping open or draft PR | -30 | - | - | - |
| Previously rejected by maintainers | -30 | - | - | - |
| No reproducible evidence | -20 | - | - | - |
| Repository appears inactive | -20 | - | - | - |
| Breaking public API change | -15 | - | - | - |
| Major new dependency | -10 | - | - | - |
| Unclear ownership or scope | -10 | - | - | - |
| **Total deductions** | | | | |
| **Final score** | | | | |

## Blocking errors and warnings

Emitted by `calculate_candidate_score.py`. Blocking errors force
`Do not pursue` regardless of the weighted subtotal.

| ID | Type | Message |
|---|---|---|
| `<id>` | blocking / warning | <message> |

## Band reference

| Score | Recommendation |
|---|---|
| 85-100 | Excellent contribution candidate |
| 70-84 | Strong candidate |
| 55-69 | Discuss with maintainers before implementation |
| 40-54 | Weak candidate; pursue only with new evidence |
| Below 40 | Do not pursue |

Security severity is scored separately from contribution suitability. A
`PRIVATE_DISCLOSURE` candidate scoring low here means "do not open a public PR",
not "unimportant".

## Scoring notes

Where a rating required judgement, record the reasoning so a human can challenge
it.

| Candidate | Category | Rating | Reasoning |
|---|---|---|---|
| `PERF-001` | maintainer_alignment | 4 | <reasoning, with citation> |

## Rejected candidates

| ID | Title | Score | Primary rejection reason | Reconsider if |
|---|---|---|---|---|
| `REJECTED-001` | <title> | <nn> | <reason> | <condition> |

Full records: `candidates/REJECTED-*.md`
