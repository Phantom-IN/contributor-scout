# Output Format

The document contract Contributor Scout produces, and the rules that make it
auditable.

Design source: [`AI_Assisted_Open_Source_Contribution_Discovery_Plan.md`](../AI_Assisted_Open_Source_Contribution_Discovery_Plan.md),
section 14.

---

## Directory layout

Everything is written under `contribution-discovery/` at the root of the
analysed repository (or a directory the user names). Nothing is written outside
it.

```text
contribution-discovery/
├── 00-repository-profile.md        Phase 0 - eligibility decision and facts
├── 01-architecture-and-context.md  Phase 1 - architecture, boundaries, paths
├── 02-existing-work-map.md         Phase 2 - issues, PRs, occupied ground
├── 03-review-coverage.md           Phase 3 - what was and was not reviewed
├── 04-candidate-scorecard.md       Phase 7 - scores and deductions
├── 05-final-recommendation.md      Phase 8 - one primary, up to two alternatives
├── candidates/
│   ├── SEC-001.md
│   ├── PERF-001.md
│   ├── FEAT-001.md
│   └── REJECTED-001.md
├── evidence/
│   ├── commands-run.md             every command executed, in order
│   ├── source-locations.json       every cited file:line and its claim
│   ├── github-searches.json        every query, including zero-result ones
│   ├── benchmark-plan.md           scenarios, baselines, thresholds, guards
│   ├── history-<id>.json           per-candidate Git history evidence
│   └── unresolved-questions.md     open questions, who can answer, what it blocks
└── machine-readable/
    ├── repository-profile.json
    ├── candidates.json
    └── final-ranking.json
```

**Candidate IDs** are `SEC-nnn`, `PERF-nnn`, `FEAT-nnn`, `REJECTED-nnn`,
zero-padded to three digits, and **stable across `refresh` runs**. Never
renumber - a human may have referenced an ID in an issue comment.

Add `contribution-discovery/` to your global gitignore. Do not edit the analysed
repository's `.gitignore`; that is a source modification.

---

## Mandatory candidate sections

Every `SEC-*`, `PERF-*`, and `FEAT-*` report contains all 28 level-2 headings
below. `validate_report_schema.py` enforces the list; category templates add
sections but never remove any.

```text
Classification and disposition          Proposed solution direction
Executive summary                       Alternative solutions considered
Project and user impact                 Minimum PR scope
Affected components and exact           Optional follow-ups
  source locations                      Explicit exclusions
Current behaviour                       Backward compatibility and
Expected behaviour                        maintenance cost
Root cause or capability gap            Required tests and documentation
Evidence                                Maintainer-facing pitch
Reproduction, benchmark, or             Duplicate status and confidence
  demand evidence                       Overall score
Existing mitigations and                Confidence
  false-positive analysis               Recommended next action
Related issues, PRs, discussions,       Open questions
  and recent commits                    Rejection conditions
Introducing commit and original PR
Historical design constraints
Changed assumptions
```

Print the authoritative list at any time:

```bash
python3 skills/contributor-scout/scripts/validate_report_schema.py \
  --list-required-sections
```

`REJECTED-*.md` files use a shorter contract - *What was proposed*, *Primary
rejection reason*, *Falsifying evidence*, *Duplicate status*, *Reconsider if* -
plus a `Disposition | REJECT` field. A rejection does not need a full dossier;
it needs enough for a later run to recognise the idea and not repeat the work.

---

## Evidence tags

| Tag | Meaning | Minimum requirement |
|---|---|---|
| `[CODE]` | Verified in source | `path:line` read in this run |
| `[TEST]` | Reproduced by running something | Command and output in `evidence/commands-run.md` |
| `[HISTORY]` | Supported by commit or PR history | A real SHA or a verified PR number |
| `[MAINTAINER]` | A maintainer said so | Quotable statement with a reference |
| `[DOCS]` | Project documentation says so | Document and section |
| `[INFERENCE]` | Reasoned, not stated | The reasoning is written out |
| `[UNVERIFIED]` | Believed, not checked | What would verify it is stated |

Rules that matter:

- Use the strongest tag you can **actually support**, not the strongest that
  would be convenient.
- Line numbers are facts. Cite only lines read in this run.
- A candidate whose core claim is `[INFERENCE]` or `[UNVERIFIED]` cannot be
  `SHORTLIST`.
- The validator requires at least one `[CODE]` or `[TEST]` claim in any
  shortlisted candidate.

Full rules: [`evidence-classification.md`](../skills/contributor-scout/references/evidence-classification.md).

---

## Machine-readable schemas

All JSON carries a `schema` and `schema_version` field so outputs stay
comparable as the rubric evolves.

### `repository-profile.json` - `contributor-scout/repository-profile`

Produced by `collect_repo_metadata.py`. Keys: `repository_root`, `git`
(head, branch, remotes, commit counts, authors, tags, churn), `licence`,
`security_policy`, `inventory` (languages, known files, CI files, test
directories), `likely_commands`, `tooling_available`.

### `candidates.json` - input to scoring

One object per candidate:

```json
{
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
        "contributor_fit": 4
      },
      "risks": {
        "overlapping_open_pr": false,
        "previously_rejected": false,
        "no_reproducible_evidence": false,
        "repository_inactive": false,
        "breaking_api_change": false,
        "major_new_dependency": false,
        "unclear_ownership_or_scope": false
      },
      "rating_notes": {
        "maintainer_alignment": "Issue #412 labelled 'help wanted' - [MAINTAINER]"
      }
    }
  ]
}
```

Generate a valid starting point with
`calculate_candidate_score.py --example`.

### `final-ranking.json` - `contributor-scout/scores`

Produced by `calculate_candidate_score.py`. Per candidate: `category_scores`
(with per-category rating, weight, points, and note), `weighted_subtotal`,
`deductions_applied`, `total_deduction`, `final_score`, `band`, `band_label`,
`gate_applied`, `blocking_errors`, `warnings`, `scoreable`,
`shortlist_eligible`.

### `github-searches.json` - `contributor-scout/github-searches`

Produced by `search_github_candidates.py`. Records every query with its command,
timestamp, result count, and normalised results - including zero-result queries,
which are what make "no duplicate found" auditable. Also carries
`duplicate_detection_confidence` and `confidence_notes`.

### `history-<id>.json` - `contributor-scout/git-history`

Produced by `collect_git_history.py`. Blame lines, line-range log, file log,
ranked `introducing_commit_candidates` (each with a
`pull_request_reference` marked `verified`, `unverified`, or `none`), branch and
tag containment, and warnings such as shallow-clone detection.

---

## Score bands

| Score | Recommendation |
|---|---|
| 85-100 | Excellent contribution candidate |
| 70-84 | Strong candidate |
| 55-69 | Discuss with maintainers before implementation |
| 40-54 | Weak candidate; pursue only with new evidence |
| Below 40 | Do not pursue |

Two additional band values come from the script rather than the arithmetic:

- `DO_NOT_PURSUE` is forced when the duplicate status is `DUPLICATE`, `CLAIMED`,
  `REJECTED`, or `SUPERSEDED`.
- `INVALID` is returned when the candidate has blocking errors, so a malformed
  candidate never displays as "Excellent".

Security severity is **not** part of this score. A critical vulnerability may
score low because a public PR is the wrong route.

---

## Validation

```bash
# Whole run
python3 skills/contributor-scout/scripts/validate_report_schema.py \
  --dir contribution-discovery

# One candidate, with unfilled placeholders treated as errors
python3 skills/contributor-scout/scripts/validate_report_schema.py \
  --candidate contribution-discovery/candidates/PERF-001.md --strict

# Machine-readable result
python3 skills/contributor-scout/scripts/validate_report_schema.py \
  --dir contribution-discovery --format json
```

Exit codes: `0` valid (warnings possible), `2` errors found, `1` bad arguments.

The validator checks section completeness, disposition presence, duplicate
status and confidence, the `CLEAR`+`LOW` contradiction, evidence tags, source
locations, introducing-commit evidence (or an explicit statement that history
was unavailable), a non-empty next action, security disclosure recommendations,
JSON parseability, the three-candidate shortlist limit, and that every
shortlisted candidate is referenced in the final recommendation.

---

## Sensitive output

If any candidate is `PRIVATE_DISCLOSURE`, `contribution-discovery/` contains
sensitive material:

- do not commit it to a public repository;
- do not paste candidate contents into a public issue;
- `05-final-recommendation.md` names the candidate and severity band but must
  not restate the vulnerable path;
- `machine-readable/candidates.json` carries the ID, disposition, and score, but
  not the technical detail.

See [`responsible-disclosure.md`](../skills/contributor-scout/references/responsible-disclosure.md).
