<!--
TEMPLATE: 00-repository-profile.md  (Phase 0)
See references/repository-assessment.md. Tag every claim.
-->

# Repository Profile: <owner/name>

| Field | Value |
|---|---|
| Repository | `<owner/name>` |
| Local path | `<path>` |
| Remote | `<url>` |
| Default branch | `<branch>` |
| Analysed at commit | `<short SHA>` (`<date>`) |
| Analysed on | `<YYYY-MM-DD>` |
| Skill version | `contributor-scout 1.0.0` |

## Eligibility decision

> **`PROCEED` / `PROCEED_WITH_LIMITATIONS` / `DO_NOT_INVEST`**

**Reasoning:** <two to four sentences>

**Limitations carried into later phases** (mandatory for `PROCEED_WITH_LIMITATIONS`):

| # | Limitation | Effect on the analysis |
|---|---|---|
| 1 | <e.g. `gh` unauthenticated> | Duplicate-detection confidence capped at LOW |
| 2 | <e.g. tests require a database> | No `[TEST]` evidence available |

## Project identity

- **Purpose:** <one paragraph, in the maintainers' words where possible> `[DOCS]`
- **Primary users:** <personas>
- **Stated scope:** "<quote>" `[DOCS]`
- **Stated non-goals:** "<quote>" `[DOCS]`
- **Licence:** `<SPDX id>` `[DOCS]`
- **Primary languages:** <list with approximate proportions>
- **Repository size:** <files, lines, largest directories>

## Activity signals

| Signal | Value | Evidence |
|---|---|---|
| Last commit | `<date>` (`<sha>`) | `[HISTORY]` |
| Commits in last 6 months | `<n>` | `[HISTORY]` |
| Active contributors (12 months) | `<n>` | `[HISTORY]` |
| Latest release | `<tag>` (`<date>`) | `[HISTORY]` |
| Releases in last 12 months | `<n>` | `[HISTORY]` |
| Open issues / open PRs | `<n>` / `<n>` | `[MAINTAINER]` |
| Oldest untouched open PR | `<age>` | `[MAINTAINER]` |
| Merged external PRs (last 30) | `<n>` | `[MAINTAINER]` |
| Archived / mirror / fork | no / no / no | `[DOCS]` |
| CI status on default branch | <passing/failing/unknown> | `[DOCS]` |

## Contribution environment

| Item | Present | Location | Notes |
|---|---|---|---|
| `CONTRIBUTING` | yes/no | `<path>` | <process summary> |
| `CODE_OF_CONDUCT` | yes/no | `<path>` | |
| `SECURITY` policy | yes/no | `<path>` | **Private disclosure channel: `<channel or NONE FOUND>`** |
| Issue templates | yes/no | `<path>` | |
| PR template | yes/no | `<path>` | |
| CLA / DCO | yes/no | `<source>` | <can the contributor satisfy it?> |
| Roadmap | yes/no | `<path>` | |
| `good first issue` / `help wanted` | `<n>` / `<n>` | - | |

## Development commands

| Purpose | Command | Source | Verified |
|---|---|---|---|
| Install | `<cmd>` | `<file>` | not run (needs approval) |
| Build | `<cmd>` | `<file>` | |
| Test | `<cmd>` | `<file>` | |
| Lint | `<cmd>` | `<file>` | |
| Type check | `<cmd>` | `<file>` | |
| Benchmark | `<cmd>` | `<file>` | |
| Static analysis | `<cmd>` | `<file>` | |

- **Toolchain requirements:** <language and tool versions>
- **Commands actually run in this session:** see `evidence/commands-run.md`

## Maintainer culture

- **Review speed:** <observed from recent merged PRs> `[MAINTAINER]`
- **Typical merged PR size:** <lines / files> `[HISTORY]`
- **Discussion-first expectation:** yes/no - "<quote>" `[DOCS]`
- **Recent rejection reasons:** <patterns observed across closed PRs> `[MAINTAINER]`
- **Area owners:** <from CODEOWNERS / MAINTAINERS / commit history>

## Blocking-condition checks

| Condition | Present | Evidence |
|---|---|---|
| Archived or read-only | no | |
| Read-only mirror of another forge | no | |
| No open-source licence | no | |
| In-flight rewrite that obsoletes current-tree changes | no | |
| Maintainers decline external contributions | no | |
| Unsatisfiable CLA or legal constraint | no | |
| Cannot be built or tested without privileged infrastructure | no | |

## Tooling availability

| Tool | Available | Notes |
|---|---|---|
| `git` | yes/no | |
| `gh` (GitHub CLI) | yes/no | Authenticated: yes/no - **bounds duplicate-detection confidence** |
| Language toolchain | yes/no | <versions> |
| Test runner | yes/no | |
| Benchmark harness | yes/no | |

## Recommended next step

<e.g. "Run `/contributor-scout full`. Expect duplicate-detection confidence
HIGH; tests are runnable locally in ~40 s." or "Do not invest: repository was
archived on <date>.">
