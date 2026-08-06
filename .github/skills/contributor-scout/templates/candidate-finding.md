<!--
CANONICAL CANDIDATE TEMPLATE - Contributor Scout

Every candidate file (SEC-nnn.md, PERF-nnn.md, FEAT-nnn.md) MUST contain every
level-2 heading below, spelled exactly as written. `scripts/validate_report_schema.py`
enforces this list. Category-specific templates (security-finding.md,
performance-finding.md, feature-proposal.md) add sections; they never remove any.

Tag every material claim: [CODE] [TEST] [HISTORY] [MAINTAINER] [DOCS] [INFERENCE] [UNVERIFIED]
Delete these HTML comments when generating a real document.
-->

# <TYPE-ID>: <Concise, specific candidate title>

| Field | Value |
|---|---|
| Candidate ID | `<SEC-001 / PERF-001 / FEAT-001>` |
| Category | `security` / `performance` / `feature` |
| Repository | `<owner/name>` |
| Analysed at commit | `<short SHA>` on `<branch>` |
| Generated | `<YYYY-MM-DD>` |
| Skill version | `contributor-scout 1.0.0` |

## Classification and disposition

- **Disposition:** `SHORTLIST` / `NEEDS_MAINTAINER_INPUT` / `HOLD` / `REJECT` / `PRIVATE_DISCLOSURE`
- **Category:** <security / performance / feature>
- **Severity or magnitude:** <band, with one line of reasoning>
- **Contribution score:** `<nn>/100` - band `<Excellent / Strong / Discuss / Weak / Do not pursue>`
- **Affected component:** `<module or subsystem>`

## Executive summary

<Two to four sentences. What the problem or opportunity is, who it affects, and
what the proposed change is. A maintainer should be able to decide from this
paragraph alone whether to keep reading.>

## Project and user impact

- **Who is affected:** <users / operators / downstream consumers / CI>
- **Under what conditions:** <configuration, platform, version, scale>
- **How often:** <per request / per startup / per file / rarely>
- **Concrete consequence:** <what actually goes wrong, in user-visible terms>
- **Evidence:** `[CODE]` / `[TEST]` / `[MAINTAINER]` <citation>

## Affected components and exact source locations

| Location | Role in the finding | Evidence |
|---|---|---|
| `path/to/file.ext:120-141` | <what this code does and why it matters here> | `[CODE]` |
| `path/to/other.ext:88` | <call site / boundary / sink> | `[CODE]` |

<Every line number must have been read in this run.>

## Current behaviour

<What the code does today, described factually, with citations. No judgement
language here - just behaviour.>

## Expected behaviour

<What it should do instead, and the basis for that expectation: documentation,
tests, maintainer statement, established convention, or reasoned argument.
Cite the basis.>

## Root cause or capability gap

<The single underlying reason, not the symptom. For features, the capability
that is missing and why the architecture does not currently provide it.>

## Evidence

| # | Claim | Tag | Source |
|---|---|---|---|
| 1 | <claim> | `[CODE]` | `path:line` |
| 2 | <claim> | `[TEST]` | command + result, recorded in `evidence/commands-run.md` |
| 3 | <claim> | `[HISTORY]` | commit `<sha>` |
| 4 | <claim> | `[MAINTAINER]` | issue #<n>, comment by @<maintainer> |
| 5 | <claim> | `[INFERENCE]` | <reasoning> |

## Reproduction, benchmark, or demand evidence

<Security: minimal local reproduction conditions - mechanism, not a weaponised
exploit.>
<Performance: benchmark scenario, baseline command, measurements, success
criterion. Cross-reference `evidence/benchmark-plan.md`.>
<Feature: demand signals with citations - issue numbers, reaction counts,
maintainer statements, recurring support questions.>

## Existing mitigations and false-positive analysis

**Existing mitigations**

| Mitigation | Location | Effect |
|---|---|---|

**Why this might not be a real finding**

1. <the strongest argument against this candidate>
2. <the second strongest>

**Why it survives**

<Reasoning with evidence. If it does not survive, the disposition is `REJECT`.>

## Related issues, PRs, discussions, and recent commits

| Type | Ref | Title | State | Relationship |
|---|---|---|---|---|
| Issue | #<n> | <title> | open/closed | related / partially covers / unrelated |
| PR | #<n> | <title> | open/draft/merged/closed | <relationship> |
| Discussion | #<n> | <title> | - | <relationship> |
| Commit | `<sha>` | <subject> | - | <relationship> |

<If nothing was found, say so and list the query variants that were run.>

## Introducing commit and original PR

- **Introducing commit:** `<sha>` - <subject> (<author date>) `[HISTORY]`
- **Introducing PR:** #<n> - <title>, or `not identified` with what was tried
- **First release containing it:** `<tag>` (`git tag --contains`)
- **Original objective:** <what that change was solving> `[HISTORY]`

## Historical design constraints

<What constraints made the original implementation reasonable at the time.
Framed as context, never as criticism. Cite the commit message, linked issue, or
the state of the tree at that commit.>

## Changed assumptions

| Assumption at introduction | Evidence | Still true? | What changed |
|---|---|---|---|
| <assumption> | `[HISTORY]` `<sha>` | No | <the change, with evidence> |

<If every assumption still holds, the current design is probably still correct.
Say so and reconsider the disposition.>

## Proposed solution direction

<Direction, not an implementation. Enough for a maintainer to agree or redirect.
Reference an existing pattern in the repository where one applies.>

## Alternative solutions considered

| Alternative | Pros | Cons | Why not chosen |
|---|---|---|---|

## Minimum PR scope

<The smallest change that delivers the value. One coherent problem. List the
files expected to change.>

## Optional follow-ups

<What could reasonably come later, in separate PRs.>

## Explicit exclusions

<What this contribution deliberately does NOT include. Unrelated refactors,
dependency upgrades, style changes, adjacent bugs. This section prevents scope
creep and earns maintainer trust.>

## Backward compatibility and maintenance cost

- **Public API impact:** <none / additive / behavioural / breaking>
- **Configuration impact:** <none / new optional key / changed default>
- **Behaviour change for existing users:** <describe, or "none">
- **Migration or deprecation needed:** <yes/no - describe>
- **Ongoing maintenance burden:** <new surface, docs, tests, support>

## Required tests and documentation

| Test | Type | What it proves |
|---|---|---|
| `<test name/path>` | regression / unit / integration / benchmark | <assertion> |

- **Documentation impact:** <files to update, or "none">
- **Changelog entry:** <required? in what format?>

## Maintainer-facing pitch

> **Problem.** <user-visible symptom with evidence>
> **Where.** <file:line and how often the path runs>
> **Why it is like this.** <historical constraint, framed respectfully>
> **What changed.** <assumption that no longer holds>
> **Proposal.** <minimum scope in one sentence>
> **Not included.** <explicit exclusions>
> **Compatibility.** <impact, or "none">
> **Question.** <the one decision needed from maintainers, if any>

## Duplicate status and confidence

- **Status:** `CLEAR` / `RELATED` / `PARTIALLY_COVERED` / `CLAIMED` / `DUPLICATE` / `REJECTED` / `SUPERSEDED` / `UNKNOWN`
- **Duplicate-detection confidence:** `HIGH` / `MEDIUM` / `LOW`
- **Sources checked:** issues (open/closed), PRs (open/draft/merged/closed), discussions, recent commits, advisories
- **Query variants run:** <list every one, including those with zero results>
- **Reasoning:** <why this status>

## Overall score

| Category | Weight | Rating (0-5) | Points |
|---|---|---|---|
| Evidence that the problem is real | 15 | | |
| User or project impact | 15 | | |
| Maintainer and roadmap alignment | 15 | | |
| Non-duplication confidence | 15 | | |
| Technical solution confidence | 10 | | |
| Scope clarity | 10 | | |
| Testability | 5 | | |
| Backward compatibility | 5 | | |
| Historical justification | 5 | | |
| Contributor ability to implement | 5 | | |
| **Weighted subtotal** | **100** | | |

| Risk deduction | Applied | Points |
|---|---|---|
| Overlapping open or draft PR | no | 0 |
| Previously rejected by maintainers | no | 0 |
| No reproducible evidence | no | 0 |
| Repository appears inactive | no | 0 |
| Breaking public API change | no | 0 |
| Major new dependency | no | 0 |
| Unclear ownership or scope | no | 0 |

**Final score: `<nn>`/100 - band `<band>`**
(Produced by `scripts/calculate_candidate_score.py`; do not hand-compute.)

## Confidence

- **Overall confidence in this candidate:** `Confirmed` / `High` / `Medium` / `Low`
- **What would raise it:** <specific action>
- **What would falsify it:** <specific observation>

## Recommended next action

<One of: implement and open a focused PR / comment on issue #n first / open a
design discussion / disclose privately via <channel> / hold until <condition> /
do not pursue. Include the immediate first step.>

## Open questions

| # | Question | Who can answer | What it blocks |
|---|---|---|---|

## Rejection conditions

<The specific observations that would invalidate this candidate. If any becomes
true, drop it.>

- <e.g. an open PR appears that covers the same path>
- <e.g. a maintainer states the current behaviour is intentional>
- <e.g. the benchmark shows less than the threshold improvement>
