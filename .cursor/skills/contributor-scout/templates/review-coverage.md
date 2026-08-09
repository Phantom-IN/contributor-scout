<!--
TEMPLATE: 03-review-coverage.md  (Phase 3)
Honest coverage reporting. What was NOT reviewed matters as much as what was.
-->

# Review Coverage: <owner/name>

| Field | Value |
|---|---|
| Mode | `full` / `security` / `performance` / `features` |
| Analysed at commit | `<short SHA>` on `<branch>` |
| Generated | `<YYYY-MM-DD>` |
| Reviewers run | security / performance / features |

## Scope

- **Repository size:** <n> source files, <n> lines
- **Files opened in this run:** <n>
- **Directories reviewed in depth:** <list>
- **Directories sampled only:** <list>
- **Directories not examined:** <list, with reason>

<If the repository was too large to review exhaustively, say so here and state
the sampling strategy used.>

## Security coverage

| Attack surface | Reviewed | Locations examined | Findings | Notes |
|---|---|---|---|---|
| Network entry points | yes/no/n-a | `<paths>` | <n> | |
| CLI / IPC input | | | | |
| File and archive parsing | | | | |
| Deserialisation | | | | |
| Template rendering | | | | |
| Database queries | | | | |
| Subprocess execution | | | | |
| Outbound requests (SSRF) | | | | |
| Authentication | | | | |
| Authorisation | | | | |
| Cryptography | | | | |
| Secrets handling | | | | |
| Plugin / extension loading | | | | |
| CI and supply chain | | | | |
| Update mechanisms | | | | |

**Not reviewed and why:** <e.g. "vendored `third_party/` excluded - not project
code"; "Windows-specific paths not analysed - no environment available">

## Performance coverage

| Path | Importance evidence | Reviewed | Measured | Findings |
|---|---|---|---|---|
| <path name> | <signal> | yes/no | yes/no | <n> |

- **Existing benchmark harness used:** yes/no - <name>
- **Measurements taken:** <n> - see `evidence/commands-run.md`
- **Profiling performed:** yes/no - <tool>
- **Not reviewed and why:** <e.g. "no representative workload available for the
  streaming path">

## Feature coverage

| Source | Examined | Items reviewed | Candidates raised |
|---|---|---|---|
| Roadmap | yes/no | <n> | <n> |
| Open issues (`enhancement`) | | | |
| `help wanted` / `good first issue` | | | |
| Closed / not-planned issues | | | |
| Discussions | | | |
| Documentation limitations | | | |
| TODO / FIXME comments | | | |
| Release notes | | | |

## Degraded capabilities

| Capability | Status | Effect on findings |
|---|---|---|
| GitHub CLI | available and authenticated / unauthenticated / not installed | <duplicate-detection confidence> |
| Test suite | runnable / not runnable - <reason> | <no `[TEST]` evidence> |
| Benchmarks | available / none | <performance claims are estimates> |
| Git history | complete / shallow / squashed import | <historical justification limited> |
| Discussions | accessible / disabled / not accessible | <duplicate detection gap> |
| Static analysis | <tools run, or none available> | |

## Candidates raised

| ID | Category | Title | Disposition |
|---|---|---|---|
| `SEC-001` | security | <title> | |
| `PERF-001` | performance | <title> | |
| `FEAT-001` | feature | <title> | |
| `REJECTED-001` | <category> | <title> | REJECT |

## Confidence in coverage

> **Overall coverage confidence: `HIGH` / `MEDIUM` / `LOW`**

<Reasoning. State plainly what a second reviewer should check that this run did
not. Absence of findings in an area that was not reviewed is not evidence of
absence.>

## Commands run

Full log: `evidence/commands-run.md` (<n> commands).
