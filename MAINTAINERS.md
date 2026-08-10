# Maintainers

The people who review, merge, release, and answer for Contributor Scout.
GitHub's collaborator list is not publicly visible, so this file is the
canonical record; if it disagrees with anything else, this file wins.

## Current maintainers

| Name | GitHub | Role | Since |
|---|---|---|---|
| Vaibhav Vanage | [@Phantom-IN](https://github.com/Phantom-IN) | Maintainer | 2026-08 |
| Arav Saxena | [@arav7781](https://github.com/arav7781) | Maintainer | 2026-08 |
| Faheem | [@Faheem219](https://github.com/Faheem219) | Maintainer | 2026-08 |

All three maintainers triage issues, review and merge pull requests, and share
responsibility for the [roadmap](ROADMAP.md), releases and version tags,
[security reports](SECURITY.md), and enforcement of the
[Code of Conduct](CODE_OF_CONDUCT.md). Ownership of specific areas (playbooks,
scripts, hosts) will be recorded here as it settles;
[`.github/CODEOWNERS`](.github/CODEOWNERS) mirrors whatever this table says.

## How maintainers decide

1. **Evidence first.** A reproducible run beats any opinion, including a
   maintainer's. Playbook and scoring changes follow the
   [evidence rules](CONTRIBUTING.md#ground-rule-playbooks-grow-from-failures-not-ideas)
   like everyone else's.
2. **Lazy consensus.** Any maintainer may approve and merge routine changes;
   anything touching the report contract, scoring gates, the safety model, or
   the hook waits for a second maintainer's review.
3. **Tie-break.** When maintainers disagree and evidence does not settle it,
   the three resolve it by majority vote — and record the reasoning in the PR
   or issue.
4. **Constitutional changes.** The [principles in ROADMAP.md](ROADMAP.md#principles-that-will-not-change)
   change only with the explicit agreement of **all** maintainers.
5. **Own work gets reviewed too.** Maintainers open pull requests like anyone
   else; nobody pushes to `main` directly.

## Becoming a maintainer

Maintainership is offered, not applied for. The path in is sustained, quality
participation: verified run-failure reports, evidence-backed playbook
improvements, solid reviews of other people's PRs, outcome reports that close
the loop. When the existing maintainers agree someone has been operating at
that level for a while, they will be invited, added as a repository
collaborator, and recorded here.

## Stepping back

Maintainers who become inactive for six months or more will be moved to the
emeritus list below (with thanks, and with the door open to return).

**Emeritus:** none yet.
