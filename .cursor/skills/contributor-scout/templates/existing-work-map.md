<!--
TEMPLATE: 02-existing-work-map.md  (Phase 2)
See references/duplicate-detection-playbook.md.
This is the broad sweep. Phase 5 repeats detection per candidate.
-->

# Existing Work Map: <owner/name>

| Field | Value |
|---|---|
| Collected | `<YYYY-MM-DD>` |
| Remote access | `gh` available: yes/no - authenticated: yes/no |
| **Duplicate-detection confidence** | `HIGH` / `MEDIUM` / `LOW` |
| Sources reachable | issues / PRs / discussions / advisories / releases |

> If remote access failed, no candidate in this run may be classified `CLEAR`.
> Use `UNKNOWN` and state that a human must verify before implementation.

## Summary

| Source | Count examined | Notes |
|---|---|---|
| Open issues | | |
| Closed issues (last 12 months) | | |
| Open PRs | | including `<n>` drafts |
| Merged PRs (last 3 months) | | |
| Closed unmerged PRs (last 12 months) | | rejection patterns noted below |
| Discussions | | enabled: yes/no |
| Security advisories | | |
| Releases (last 12 months) | | |

## Active work in flight

Anything here is occupied ground - avoid proposing into it.

| Ref | Title | Author | State | Age | Area touched |
|---|---|---|---|---|---|
| PR #<n> | <title> | @<user> | open / draft | <days> | `<path>` |

## Themes in open issues

| Theme | Issue count | Representative issues | Maintainer engagement |
|---|---|---|---|
| <e.g. startup performance> | <n> | #<n>, #<n> | <responded / silent> |

## Maintainer-solicited work

| Ref | Title | Label | Notes |
|---|---|---|---|
| #<n> | <title> | `help wanted` / `good first issue` | <maintainer comment> `[MAINTAINER]` |

## Recently merged work

Recent merges tell you what is already fixed and what direction the project is
moving.

| PR | Title | Merged | Area | Implication |
|---|---|---|---|---|

## Rejected directions

The most valuable table in this document. Read the maintainer comment on each.

| Ref | Proposal | Outcome | Maintainer reasoning |
|---|---|---|---|
| #<n> | <proposal> | closed as not planned | "<quote>" `[MAINTAINER]` |

## Roadmap and planned work

| Item | Source | Status |
|---|---|---|

## In-repository signals

### TODO / FIXME / HACK comments

| Location | Comment | Age | Interpretation |
|---|---|---|---|
| `path:line` | "<text>" | `<sha>` `<date>` | <maintainer-flagged gap> |

Command used: `grep -rn -E '(TODO|FIXME|XXX|HACK)' --include='*.<ext>' <src>`

### Documented limitations

| Limitation | Source |
|---|---|

### Recent commit activity by area

| Area | Commits (12 months) | Interpretation |
|---|---|---|

## Security advisories

| ID | Severity | Affected | Fixed in | Notes |
|---|---|---|---|---|

## Queries executed

Every query, including those returning nothing. This is what makes the
duplicate-detection claim auditable.

| # | Query | Scope | Results | Tool |
|---|---|---|---|---|
| 1 | `<query>` | issues, all states | <n> | `gh` / `WebFetch` / `git log` |

Full machine-readable record: `evidence/github-searches.json`

## Occupied ground

Areas where a new contribution would likely duplicate or collide:

- <area> - <reason, with reference>

## Open ground

Areas with demand signals and no visible work in flight:

- <area> - <signal, with reference>
