<!--
TEMPLATE: 05-final-recommendation.md  (Phase 8)
At most 3 shortlisted candidates, exactly 1 primary.
"No contribution currently meets the required evidence and alignment threshold."
is a valid and successful outcome.

For PRIVATE_DISCLOSURE candidates: name the candidate and severity band here,
but do NOT restate the vulnerable path. Point to the candidate file.
-->

# Final Recommendation: <owner/name>

| Field | Value |
|---|---|
| Repository | `<owner/name>` |
| Analysed at commit | `<short SHA>` on `<branch>` (`<date>`) |
| Generated | `<YYYY-MM-DD>` |
| Mode | `full` / `security` / `performance` / `features` |
| Duplicate-detection confidence | `HIGH` / `MEDIUM` / `LOW` |
| Eligibility decision | `PROCEED` / `PROCEED_WITH_LIMITATIONS` |

---

## Recommendation

> **Primary candidate: `<ID>` - <title>**
> Score `<nn>`/100 (`<band>`) · Disposition `<disposition>`
> Recommended action: **<implement / discuss first / disclose privately / hold>**

<Or, when nothing meets the threshold:>

> **No contribution currently meets the required evidence and alignment
> threshold.**
> <Two to four sentences on why, and what would change the answer.>

---

## Why this candidate is strongest

| Dimension | Assessment |
|---|---|
| Evidence | <how the problem was proven, with tag> |
| Impact | <who is affected and how> |
| Maintainer alignment | <the signal, with citation> |
| Non-duplication | <status, confidence, what was searched> |
| Scope | <why it is a focused PR> |
| Risk | <the main risk and its mitigation> |

**Compared with the alternatives:** <one paragraph on why this beat the other
shortlisted candidates - it should be a real comparison, not a restatement>

---

## Evidence summary

| Claim | Tag | Source |
|---|---|---|
| <core problem claim> | `[CODE]` | `path:line` |
| <impact claim> | `[TEST]` | <command, result> |
| <historical claim> | `[HISTORY]` | `<sha>` / PR #<n> |
| <alignment claim> | `[MAINTAINER]` | issue #<n> |

**Reproduction / benchmark:** <one line, pointing at the candidate file and
`evidence/benchmark-plan.md`>

**Unresolved:** <anything still `[INFERENCE]` or `[UNVERIFIED]` that a human
must confirm> - full list in `evidence/unresolved-questions.md`

---

## Maintainer pitch

> **Problem.** <user-visible symptom with evidence>
> **Where.** `file:line`, running <frequency>
> **Why it is like this.** <historical constraint, respectfully framed>
> **What changed.** <assumption that no longer holds>
> **Proposal.** <minimum scope, one sentence>
> **Not included.** <explicit exclusions>
> **Compatibility.** <impact, or "none">
> **Question.** <the one decision needed from maintainers, if any>

Adapt this before posting. It is a draft for a human, not a message to send
verbatim.

---

## Implementation prerequisites

Complete every item before writing any code.

- [ ] Independently reproduce the evidence in the candidate file.
- [ ] Re-run duplicate detection - issues, PRs (including drafts), and commits
      since `<date>`.
- [ ] Pull the latest default branch and confirm the finding still applies.
- [ ] Confirm the local build, test, and (if relevant) benchmark commands run.
- [ ] Read `CONTRIBUTING.md` in full and follow its process.
- [ ] Confirm the CLA/DCO requirement is satisfied.
- [ ] <candidate-specific prerequisite, e.g. "post the benchmark numbers on
      issue #<n> and wait for a maintainer reply">
- [ ] Confirm you can explain the problem, root cause, fix, alternatives, and
      risks without referring to this document.

---

## Scope boundaries

**In scope**

- <the coherent change>
- <the test proving it>

**Explicitly out of scope**

- <adjacent bug in the same file>
- <refactor of the surrounding module>
- <dependency upgrades>
- <style, typing, or formatting changes>

**Expected diff size:** <n> files, roughly <n> lines.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| <e.g. maintainers consider this out of scope> | | | <discuss on the issue first> |
| <e.g. the benchmark gain is smaller in real workloads> | | | <measure before proposing> |
| <e.g. an overlapping PR appears> | | | <re-check immediately before starting> |

---

## Next action

<One concrete first step. Examples:>

- "Comment on issue #<n> with the benchmark baseline and the proposed minimum
  scope; wait for a maintainer response before implementing."
- "Report `SEC-001` privately via `<channel>` using the structure in
  `references/responsible-disclosure.md` §7. Do not open an issue or PR."
- "Implement the minimum scope in a focused branch, referencing issue #<n> in
  the PR description."

---

## Alternatives considered (shortlist)

### 2. `<ID>` - <title>

- **Score:** `<nn>`/100 (`<band>`) · **Disposition:** `<disposition>`
- **Why not primary:** <specific reason>
- **When it would become primary:** <condition>
- **Details:** `candidates/<ID>.md`

### 3. `<ID>` - <title>

- **Score:** `<nn>`/100 (`<band>`) · **Disposition:** `<disposition>`
- **Why not primary:** <specific reason>
- **When it would become primary:** <condition>
- **Details:** `candidates/<ID>.md`

---

## Security handling

<Include only if the run produced security findings.>

| ID | Severity band | Route | Channel |
|---|---|---|---|
| `SEC-001` | <band> | `PRIVATE_DISCLOSURE` | `<channel>` |

> `contribution-discovery/` contains sensitive security material. Do not commit
> it to a public repository, and do not paste candidate contents into a public
> issue. Details deliberately omitted from this summary - see
> `candidates/SEC-001.md`.

---

## Rejected candidates

| ID | Title | Reason | Reconsider if |
|---|---|---|---|

Full records: `candidates/REJECTED-*.md`

---

## Run limitations

State every degradation honestly. A reader must be able to judge how much to
trust this recommendation.

| Limitation | Effect |
|---|---|
| <e.g. `gh` unauthenticated> | Duplicate status is `UNKNOWN`; verify manually |
| <e.g. tests not runnable locally> | No `[TEST]` evidence; claims rest on `[CODE]` |
| <e.g. only 3 of 11 modules reviewed> | Absence of findings elsewhere is not evidence of absence |

---

## Human approval gate

This document is **not** authorisation to implement. Before any code is written:

1. A human reproduces the evidence independently.
2. A human re-checks current issues, PRs, and default-branch commits.
3. A human decides the route: implement, discuss, disclose privately, hold, or drop.
4. Only then does a separate implementation workflow begin.
5. Every generated line of code is reviewed by a human before submission.
