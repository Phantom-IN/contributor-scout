# Repository Assessment (Phase 0)

Decide whether this repository deserves further review effort **before**
spending it. The output of this phase is one decision and a written profile.

Run `scripts/collect_repo_metadata.py --repo . --output <out>/machine-readable/repository-profile.json`
first, then reason over the result plus the manual checks below.

---

## 1. What to check

### Activity and lifecycle

| Check | Command / source | Healthy signal |
|---|---|---|
| Recent commits | `git log -15 --date=short --pretty='%ad %an %s'` | Commits within the last 1-3 months |
| Commit cadence | `git log --since='6 months ago' --oneline \| wc -l` | Sustained, not a single burst |
| Active maintainers | `git shortlog -sne --since='12 months ago' \| head -20` | More than one active name |
| Releases | `git tag --sort=-creatordate \| head -10`, `gh release list -L 10` | A release in the last 6-12 months |
| Archival status | `gh repo view --json isArchived,isFork,isMirror,visibility` | Not archived, not a mirror |
| Default branch health | CI badge, `gh run list -L 10` | Recent runs mostly green |

### Contribution environment

| Check | Where | Healthy signal |
|---|---|---|
| Licence | `LICENSE`, `COPYING`, manifest metadata | An OSI-approved licence |
| Contribution guide | `CONTRIBUTING.md`, `.github/CONTRIBUTING.md`, `docs/contributing*` | Exists and describes a real process |
| Code of conduct | `CODE_OF_CONDUCT.md` | Present |
| Security policy | `SECURITY.md`, `.github/SECURITY.md` | Private disclosure channel documented |
| Templates | `.github/ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md` | Present - tells you what maintainers expect |
| CLA / DCO | `CONTRIBUTING.md`, bot config, `Signed-off-by` in history | Requirement understood and satisfiable |
| Tests | test dirs, `pytest.ini`, `jest.config`, `go test`, `cargo test` | Runnable locally without exotic setup |
| CI | `.github/workflows/`, `.gitlab-ci.yml`, `azure-pipelines.yml` | Runs tests on pull requests |

### External-contribution receptiveness

- `gh pr list --state merged --limit 30 --json author,mergedAt,title` - are merged
  PRs from people outside the core team?
- `gh pr list --state open --limit 30 --json createdAt,author,title` - how old is
  the oldest untouched open PR?
- `gh issue list --label 'good first issue' --limit 20` and
  `--label 'help wanted'` - is external help actively solicited?
- Read 3-5 recent closed PRs from outside contributors. How did maintainers
  respond? Fast and constructive, slow and terse, or silent?
- Search `CONTRIBUTING.md` and recent issues for explicit statements such as
  "we do not accept feature PRs", "scope is frozen", "please open an issue first".

### Blocking conditions

Check for each of these explicitly; any one of them is a strong signal:

- repository archived, read-only, or a downstream mirror of another forge;
- no licence, or a licence that forbids derivative contribution;
- an in-flight rewrite (`v2` branch, "rewrite in progress" notice, a pinned issue
  announcing a rewrite) that would obsolete most changes to the current tree;
- maintainers publicly declining external contributions;
- a CLA the contributor cannot sign;
- the project cannot be built or tested locally without privileged or paid
  infrastructure.

---

## 2. Signal table

| Positive | Negative |
|---|---|
| Recent commits, releases, and maintainer responses | Archived, mirror, or dormant |
| External PRs are reviewed and merged | Open PRs untouched for months |
| Clear `CONTRIBUTING` and `SECURITY` policies | No setup instructions, unclear route in |
| Tests and CI runnable locally | Default branch is persistently broken |
| Roadmap, `help wanted`, `good first issue` labels | Maintainers reject external feature proposals |
| Scope matches the contributor's expertise | CLA or legal constraints cannot be satisfied |
| Issue and PR templates exist | Issue tracker is disabled or unused |

---

## 3. Decision

Emit exactly one:

| Decision | Meaning | Next step |
|---|---|---|
| `PROCEED` | Active, contribution-friendly, locally workable. | Continue to Phase 1. |
| `PROCEED_WITH_LIMITATIONS` | Worth reviewing, but with named constraints (e.g. tests cannot run locally, `gh` unavailable, slow maintainer response, discussion-first culture). | Continue, but carry each limitation into every candidate's confidence and into the final recommendation. |
| `DO_NOT_INVEST` | One or more blocking conditions hold. | Write the profile, explain, and stop. |

State the decision with its reasons and the evidence tags that support them.
`PROCEED_WITH_LIMITATIONS` must list its limitations explicitly - it is not a
softer way of saying `PROCEED`.

---

## 4. Also record for later phases

These feed Phases 1-8, so capture them now:

- build, test, lint, type-check, benchmark, and static-analysis commands (with
  the file they came from);
- minimum toolchain versions;
- the private security disclosure channel (or its absence);
- the project's stated scope and non-goals;
- release cadence and versioning policy (SemVer? deprecation windows?);
- whether `gh` is installed and authenticated - this bounds duplicate-detection
  confidence for the entire run.

Output: `00-repository-profile.md` (template: `templates/repository-profile.md`)
and `machine-readable/repository-profile.json`.
