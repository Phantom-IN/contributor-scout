# Workflow

The nine phases of a Contributor Scout run, what each produces, and where each
can stop.

Design source: [`AI_Assisted_Open_Source_Contribution_Discovery_Plan.md`](../AI_Assisted_Open_Source_Contribution_Discovery_Plan.md),
sections 6-13.

---

## Modes and phase coverage

| Mode | Phases | Typical use |
|---|---|---|
| `profile` | 0-1 | First contact with a repository. Cheap. Run this before anything else. |
| `full` | 0-8 | Complete discovery across all three categories. |
| `security` | 0-2, 3a, 4-8 | Security-only review with disclosure handling. |
| `performance` | 0-2, 3b, 4-8 | Performance-only review with benchmark design. |
| `features` | 0-2, 3c, 4-8 | Roadmap and demand-backed feature discovery. |
| `validate <id>` | 4-7 | Adversarial revalidation of one existing dossier. |
| `refresh` | 2, 5, 7-8 | Re-check remote activity and re-rank before implementing. |

Default when no mode is given: `profile`. The skill never escalates to `full` on
its own - the viability decision may end the run.

---

## Phase 0 - Repository eligibility

**Reference:** [`repository-assessment.md`](../skills/contributor-scout/references/repository-assessment.md)

Checks activity, licence, contribution and security policies, tests, CI,
external-PR receptiveness, maintainer response behaviour, releases, roadmap,
archival and mirror status, in-flight rewrites, CLA constraints, and whether
contribution is realistically feasible.

**Produces:** `00-repository-profile.md`, `machine-readable/repository-profile.json`

**Decision:** `PROCEED` · `PROCEED_WITH_LIMITATIONS` · `DO_NOT_INVEST`

**Stops here when:** `DO_NOT_INVEST`. The profile is still written - the negative
result is the deliverable.

`PROCEED_WITH_LIMITATIONS` must name its limitations. Each one propagates into
every candidate's confidence and into the final recommendation. It is not a
gentler way of saying `PROCEED`.

---

## Phase 1 - Repository comprehension

**Reference:** [`repository-comprehension.md`](../skills/contributor-scout/references/repository-comprehension.md)

Maps purpose, personas, architecture, modules, data flows, trust boundaries,
external systems, public interfaces, authn/authz, storage, extension points,
critical paths, test architecture, build and release process, conventions, known
limitations, roadmap, and historical design decisions.

**Produces:** `01-architecture-and-context.md`

**Stops here when:** mode is `profile`.

The document ends with a **Coverage and gaps** section. Downstream reviewers need
the boundaries of the map, and a later reader needs to know that "no findings in
`platform/`" might mean "nobody opened `platform/`".

---

## Phase 2 - Existing-work map

**Reference:** [`duplicate-detection-playbook.md`](../skills/contributor-scout/references/duplicate-detection-playbook.md)

The broad sweep, before any review. Collects open and closed issues,
open/draft/merged/closed PRs, discussions, roadmap, changelog, release notes,
TODO and FIXME comments, advisories, maintainer comments, and repeated user
requests.

**Produces:** `02-existing-work-map.md`, `evidence/github-searches.json`

The most valuable table here is **Rejected directions** - what maintainers have
already declined, and why. It is the cheapest way to avoid proposing something
that has already been argued about.

**Degraded mode:** without `gh`, the map records
`Duplicate-detection confidence: LOW` and the limitation propagates to every
candidate.

---

## Phase 3 - Specialised discovery

Reviewers run **independently**. No reviewer sees another's conclusions before
Phase 6 - shared conclusions produce correlated errors.

| Sub-phase | Agent | Reference |
|---|---|---|
| 3a | [security-reviewer](../agents/security-reviewer.md) | [`security-review-playbook.md`](../skills/contributor-scout/references/security-review-playbook.md) |
| 3b | [performance-reviewer](../agents/performance-reviewer.md) | [`performance-review-playbook.md`](../skills/contributor-scout/references/performance-review-playbook.md) |
| 3c | [feature-scout](../agents/feature-scout.md) | [`feature-discovery-playbook.md`](../skills/contributor-scout/references/feature-discovery-playbook.md) |

**Produces:** raw candidates in `candidates/`, plus `03-review-coverage.md`

Each reviewer's output is a **hypothesis**. Reviewers record what they did *not*
review as carefully as what they did.

---

## Phase 4 - Historical investigation

**Reference:** [`git-history-playbook.md`](../skills/contributor-scout/references/git-history-playbook.md)

For each promising candidate: the introducing commit, the introducing PR where
verifiable, the original objective and constraints, relevant maintainer
comments, which assumptions have changed, and why a change is now justified.

**Produces:** `evidence/history-<id>.json`, plus populated history sections

**The rule:** history is explanation, never blame. The original design was
reasonable under its original constraints; the argument is that the constraints
changed. If every assumption still holds, the current design is probably still
correct and the candidate should be rejected.

**Never guess a PR number.** `collect_git_history.py` reports a PR reference as
`verified`, `unverified`, or `none`, and only `verified` may be cited.

---

## Phase 5 - Duplicate validation (second pass)

The second pass is far more precise than Phase 2 because it can use the
candidate's exact symptom, component, function name, file path, error string,
root cause, and *proposed solution wording*.

**Produces:** a duplicate status and confidence per candidate

```text
CLEAR · RELATED · PARTIALLY_COVERED · CLAIMED · DUPLICATE · REJECTED · SUPERSEDED · UNKNOWN
```

**Two absolute rules:**

1. `CLEAR` requires a successful remote check of issues *and* pull requests in
   this run.
2. Where remote access failed: status `UNKNOWN`, confidence `LOW`, and an
   explicit note that a human must verify before implementation.

---

## Phase 6 - Adversarial validation

**Reference:** [`contribution-quality-rubric.md`](../skills/contributor-scout/references/contribution-quality-rubric.md), Part 1

Tries to **disprove** every candidate: reachability, reproducibility, impact,
expected behaviour, hidden mitigations, project relevance, architecture fit,
compatibility, testability, scope, duplicate status, maintainer alignment.

**Produces:** one disposition per candidate

```text
SHORTLIST · NEEDS_MAINTAINER_INPUT · HOLD · REJECT · PRIVATE_DISCLOSURE
```

Every rejection gets a `REJECTED-nnn.md` file with the reason and the
reconsideration condition. Rejections are retained so a later run does not
rediscover the same weak idea - and, often, so the *facts learned while rejecting
it* survive.

---

## Phase 7 - Scoring

**Reference:** [`contribution-quality-rubric.md`](../skills/contributor-scout/references/contribution-quality-rubric.md), Part 3

Ten weighted categories rated 0-5, scaled to 100 points, minus risk deductions:

| Category | Weight | | Risk | Deduction |
|---|---|---|---|---|
| Evidence problem is real | 15 | | Overlapping open PR | -30 |
| User or project impact | 15 | | Previously rejected | -30 |
| Maintainer alignment | 15 | | No reproducible evidence | -20 |
| Non-duplication confidence | 15 | | Repository inactive | -20 |
| Technical solution confidence | 10 | | Breaking API change | -15 |
| Scope clarity | 10 | | Major new dependency | -10 |
| Testability | 5 | | Unclear ownership or scope | -10 |
| Backward compatibility | 5 | | | |
| Historical justification | 5 | | | |
| Contributor fit | 5 | | | |

All arithmetic comes from `calculate_candidate_score.py`. The script enforces the
duplicate-status gates: `DUPLICATE`/`CLAIMED`/`REJECTED`/`SUPERSEDED` force a
blocking error and the `Do not pursue` band; `UNKNOWN` caps the non-duplication
rating at 2.

**Produces:** `04-candidate-scorecard.md`, `machine-readable/candidates.json`

---

## Phase 8 - Final recommendation

At most three shortlisted candidates, exactly one primary. Includes selection
reasoning, evidence summary, maintainer pitch, implementation prerequisites,
scope boundaries, risks, and the next action.

**Produces:** `05-final-recommendation.md`, `machine-readable/final-ranking.json`

Then `validate_report_schema.py` runs over the whole output directory, and every
error must be fixed before the run is declared complete.

**A valid outcome:**

```text
No contribution currently meets the required evidence and alignment threshold.
```

The system is rewarded for rejecting weak ideas. A run that concludes there is
nothing worth contributing, and shows its working, has succeeded.

---

## Stage gates

| Gate | Question | Outcomes |
|---|---|---|
| Repository | Active, contribution-friendly, feasible? | Proceed / proceed with limitations / do not invest |
| Finding | Does the problem actually exist? | Retain as hypothesis / reject |
| Impact | Does it matter to users, maintainers, cost, reliability, security? | Continue / reject as low value |
| Duplicate | Is someone already doing this? | One of the eight statuses |
| Alignment | Does it fit project scope and direction? | Implement / discuss first / hold / reject |
| Safety | Does this need private disclosure? | Private workflow / normal workflow |
| Human | Can the engineer explain and defend it? | Approve / return for research |

---

## The human workflow around the run

1. Clone the repository and build it manually once.
2. `profile` mode. Stop if viability is poor.
3. One category mode to calibrate depth and cost.
4. `full` mode.
5. Read the primary dossier and **independently reproduce its evidence**.
6. `refresh` mode immediately before implementing - issues and PRs move.
7. Contact maintainers where scope or direction is uncertain.
8. Pass only an approved dossier to a separate implementation workflow.
9. Review every changed line yourself.
10. Submit a focused contribution.
11. Record the maintainer outcome and feed it back into the rubric.
