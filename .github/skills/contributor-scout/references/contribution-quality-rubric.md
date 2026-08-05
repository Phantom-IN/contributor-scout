# Contribution Quality Rubric (Phases 6 and 7)

This document defines adversarial validation, dispositions, and the scoring
model. `scripts/calculate_candidate_score.py` is the authoritative implementation
of the arithmetic - this document defines the *judgement* that feeds it.

---

## Part 1 - Adversarial validation

Every candidate arrives as a hypothesis from a reviewer that wanted to find
something. This phase exists to try to **disprove** it. Approach each candidate
as though you were the maintainer looking for a reason to close it.

| Dimension | Questions to answer |
|---|---|
| **Reality** | Is the path actually reachable? Can the behaviour be reproduced? Is there validation elsewhere that I missed? Did I read the code correctly, or did I pattern-match? Is this dead code, test-only code, or vendored? |
| **Impact** | Who is affected? Under what configuration? How often? What is the concrete consequence? Would a user ever notice? |
| **Duplication** | Is there an issue, draft PR, merged fix, assigned contributor, or a semantically equivalent proposal? Was the search competent? |
| **Alignment** | Does this fit project goals, architecture, non-goals, dependency policy, and compatibility expectations? |
| **Feasibility** | Can this be delivered as a focused PR with clear tests and reviewable scope? Can *this contributor* do it? |
| **Communication** | Is the historical explanation accurate and respectful? Would the pitch convince a sceptical maintainer? |

### Falsification checklist

Run through this for each candidate and record the answers:

- [ ] I re-read every cited `file:line` and they say what the candidate claims.
- [ ] I searched for validation, guards, or mitigations upstream of the sink and
      found none (or found some and adjusted the finding).
- [ ] I checked whether the behaviour is documented as intentional.
- [ ] I checked whether it is already fixed on `main` but unreleased.
- [ ] I checked whether an open or draft PR overlaps.
- [ ] I checked whether maintainers previously declined this direction.
- [ ] I can state the impact in one sentence a user would care about.
- [ ] I can state the minimum PR scope in one sentence.
- [ ] I can name what would make me wrong.

If any answer is "no" or "did not check", the candidate cannot be `SHORTLIST`.

---

## Part 2 - Dispositions

| Disposition | Meaning | Requirement |
|---|---|---|
| `SHORTLIST` | Evidence, impact, alignment, and feasibility are sufficient for human review. | All falsification checks passed; duplicate status is `CLEAR`, `RELATED`, or `PARTIALLY_COVERED`; core claim is `[CODE]` or `[TEST]`. |
| `NEEDS_MAINTAINER_INPUT` | Credible, but scope or design direction requires discussion before implementation. | The specific question for maintainers is written down. |
| `HOLD` | Potentially valuable, blocked by missing evidence, active project change, or timing. | The unblocking condition is written down. |
| `REJECT` | Duplicate, low-value, misaligned, unproven, superseded, or impractical. | The reason and the reconsideration condition are written down. |
| `PRIVATE_DISCLOSURE` | Security-sensitive; unsuitable for a public issue or PR. | Disclosure channel identified; public artefacts contain no exploit detail. |

Every non-shortlisted candidate still gets a file. Recording rejections stops
the same weak idea from being rediscovered on the next run.

---

## Part 3 - Scoring model

100 points across ten weighted categories. Rate each **0-5** against the anchors
below; the script scales by weight (`points = weight × rating ÷ 5`).

| Category | Weight |
|---|---|
| Evidence that the problem or opportunity is real | 15 |
| User or project impact | 15 |
| Maintainer and roadmap alignment | 15 |
| Non-duplication confidence | 15 |
| Technical solution confidence | 10 |
| Scope clarity | 10 |
| Testability | 5 |
| Backward compatibility | 5 |
| Historical justification | 5 |
| Contributor ability to implement and explain | 5 |

### Rating anchors

**evidence_problem_real** (15)
- 5 - Reproduced locally with a recorded command; `[TEST]`.
- 4 - Verified in source end to end; `[CODE]` at every hop.
- 3 - Verified in source with one modest unverified assumption.
- 2 - Mostly `[INFERENCE]`; key hop unverified.
- 1 - Pattern-based suspicion.
- 0 - Not established.

**user_project_impact** (15)
- 5 - Affects most users on a common path, with a concrete consequence.
- 4 - Affects a significant subset, or a smaller group severely.
- 3 - Affects a narrow but real configuration.
- 2 - Marginal; users are unlikely to notice.
- 1 - Theoretical.
- 0 - None.

**maintainer_alignment** (15) - see
`references/maintainer-alignment-playbook.md` for full anchors.
- 5 - Explicitly requested (roadmap, `help wanted`, maintainer comment).
- 4 - Clearly in scope; similar changes recently merged.
- 3 - Plausibly in scope; no signal either way.
- 2 - Adjacent; needs discussion.
- 1 - Weak fit; similar proposals declined.
- 0 - Conflicts with a stated non-goal.

**non_duplication_confidence** (15)
- 5 - `CLEAR`, confidence HIGH, ≥8 query variants across issues/PRs/discussions.
- 4 - `CLEAR` or `RELATED`, confidence HIGH.
- 3 - `RELATED` or `PARTIALLY_COVERED` with distinct scope documented.
- 2 - `PARTIALLY_COVERED` with unclear boundary, or confidence MEDIUM.
- 1 - `UNKNOWN` with only local evidence.
- 0 - `DUPLICATE`, `CLAIMED`, `REJECTED`, or `SUPERSEDED`.

> Gate: `UNKNOWN` caps this rating at 2. Statuses `DUPLICATE`, `CLAIMED`,
> `REJECTED`, and `SUPERSEDED` force rating 0 and a blocking error.

**technical_solution_confidence** (10)
- 5 - The fix is obvious, local, and follows an existing pattern in the repo.
- 4 - Clear approach; minor design choices remain.
- 3 - Approach known; a real design decision remains open.
- 2 - Several plausible approaches; trade-offs unresolved.
- 1 - No credible approach identified.
- 0 - Would require redesign of a subsystem.

**scope_clarity** (10)
- 5 - One coherent problem, one small diff, exclusions written down.
- 4 - Focused, with a clear boundary.
- 3 - Focused but touches several files or needs a small refactor.
- 2 - Boundary is fuzzy; scope creep is likely.
- 1 - Would need multiple PRs to be useful.
- 0 - Effectively a rewrite.

**testability** (5)
- 5 - A deterministic regression test or benchmark exists or is trivial to add
      in the project's existing harness.
- 4 - Testable with modest fixture work.
- 3 - Testable, but needs new infrastructure.
- 2 - Hard to test deterministically (timing, network, platform-specific).
- 1 - Only manually verifiable.
- 0 - Not verifiable.

**backward_compatibility** (5)
- 5 - No behaviour change for existing users; default preserved.
- 4 - Additive only; opt-in.
- 3 - Behaviour changes only in the buggy case.
- 2 - Observable change requiring release notes.
- 1 - Deprecation needed.
- 0 - Breaking public API change.

**historical_justification** (5)
- 5 - Introducing commit **and** PR identified; original constraints understood;
      changed assumptions documented.
- 4 - Introducing commit identified; PR inferred but unverified, and labelled so.
- 3 - Relevant history found; introducing commit ambiguous.
- 2 - History exists but was not conclusive.
- 1 - History unavailable (shallow clone, squashed import) - stated.
- 0 - Not investigated.

**contributor_fit** (5)
- 5 - Language, domain, and test tooling are all familiar to the contributor.
- 4 - Familiar language; some domain learning needed.
- 3 - Learnable within the scope of the change.
- 2 - Significant unfamiliar domain.
- 1 - Would need substantial ramp-up.
- 0 - Beyond current capability.

Where contributor capability is unknown, default `contributor_fit` to 3 and say
so; do not silently inflate it.

### Risk deductions

Applied after the weighted total, floored at 0:

| Risk flag | Deduction | Set when |
|---|---|---|
| `overlapping_open_pr` | -30 | An open or draft PR materially overlaps |
| `previously_rejected` | -30 | Maintainers previously declined this approach |
| `no_reproducible_evidence` | -20 | No reproduction, benchmark, or `[TEST]` evidence |
| `repository_inactive` | -20 | Phase 0 flagged inactivity |
| `breaking_api_change` | -15 | A public API break is required |
| `major_new_dependency` | -10 | A significant new dependency is required |
| `unclear_ownership_or_scope` | -10 | Scope boundary or code ownership is unclear |

Declare risk flags honestly. Omitting a true flag to protect a score is the
single most damaging thing this system can do.

### Bands

| Score | Recommendation |
|---|---|
| 85-100 | Excellent contribution candidate |
| 70-84 | Strong candidate |
| 55-69 | Discuss with maintainers before implementation |
| 40-54 | Weak candidate; pursue only with new evidence |
| Below 40 | Do not pursue |

Security severity is **not** part of this score. A critical vulnerability may
score low here because a public PR is the wrong route - that is the model
working correctly, not a bug.

---

## Part 4 - Shortlist rules

- At most **three** shortlisted candidates. At most **one** primary
  recommendation.
- The primary candidate must score in the "Strong" band (≥70) or higher, unless
  the user explicitly asked for the best available regardless of quality - in
  which case say plainly that it is below threshold.
- Do not fill the shortlist. Two strong candidates beat three where the third is
  padding.
- If nothing reaches 55, the correct output is:

  ```text
  No contribution currently meets the required evidence and alignment threshold.
  ```

  with the rejected candidates and their reasons as supporting evidence, and a
  short note on what would change the answer (e.g. "re-run after the v3 branch
  merges", "ask maintainers whether X is in scope").
