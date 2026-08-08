# Duplicate Detection Playbook (Phases 2 and 5)

Duplicate work is the single most common way an AI-assisted contribution wastes
a maintainer's time. Exact-title search is not sufficient - the same problem
gets described a dozen different ways.

Duplicate detection runs **twice**:

- **Phase 2 (broad)** - before review, to learn what the project is already
  working on and to bias reviewers away from occupied ground.
- **Phase 5 (candidate-specific)** - after a candidate exists, using its exact
  symptom, component, function name, error string, root cause, and *proposed
  solution wording*. This pass is far more precise and is mandatory.

---

## Sources to inspect

| Source | Why | How |
|---|---|---|
| Open issues | Active known problems | `gh issue list --state open` |
| Closed issues | Prior rejections and prior fixes | `gh issue list --state closed`, check `stateReason` |
| Open PRs | Work in flight | `gh pr list --state open` |
| Draft PRs | Work in flight but easy to miss | `gh pr list --state open --json isDraft` |
| Merged PRs | Recently fixed - your finding may be stale | `gh pr list --state merged --limit 50` |
| Closed unmerged PRs | Rejected approaches - read the maintainer comment | `gh pr list --state closed` |
| Discussions | Design conversations that never became issues | `gh api repos/{o}/{r}/discussions`, or `WebFetch` the discussions page |
| Roadmap / projects | Planned work | `ROADMAP.md`, `gh project list`, pinned issues |
| Release notes / changelog | Recently shipped fixes | `CHANGELOG.md`, `gh release list` |
| Security advisories | Known vulnerabilities | `gh api repos/{o}/{r}/security-advisories` |
| Recent commits | Fixed but unreleased | `git log --since='3 months ago' --oneline -- <path>` |
| Active branches | Work not yet in a PR | `git branch -r --sort=-committerdate \| head -30` |
| Source comments | Maintainer-flagged known gaps | grep `TODO`, `FIXME`, `XXX`, `HACK` |

---

## Query variant generation

For each candidate, generate queries across **all** of these axes. Ten to twenty
variants is normal; three is not enough.

| Axis | Example variants |
|---|---|
| Component | module name, class name, subsystem nickname |
| Function / symbol | exact function name, method name |
| File path | `src/config/loader.py`, `config/loader` |
| Symptom | "slow startup", "high memory", "hangs on large files" |
| Error string | the literal message a user would paste |
| Root cause | "re-parses config", "no caching", "quadratic" |
| Solution terminology | "cache", "memoise", "lazy load", "batch", "pool" |
| Synonyms | config/configuration/settings; slow/performance/latency/speed |
| User framing | how a non-expert would describe it |

Worked example, for a repeated-configuration-parsing finding:

```text
"configuration parsing performance"
"cache parsed config"
"repeated file parsing"
ConfigLoader.load            (exact symbol)
src/config/loader.py         (exact path)
"slow startup"
"startup performance"
"config reload"
"config invalidation"
"parse yaml every request"
memoize config
```

Use `scripts/search_github_candidates.py` to run the sweep and normalise the
results:

```bash
python3 scripts/search_github_candidates.py \
  --repo owner/name \
  --query "cache parsed config" --query "slow startup" --query "ConfigLoader" \
  --state all --include-prs --include-issues \
  --output contribution-discovery/evidence/github-searches.json
```

Record **every** query you ran and its result count, including the empty ones.
"No results across 14 variants" is itself evidence, and a reviewer needs to see
the variants to judge whether the search was competent.

---

## Reading results

For each plausible hit, determine:

1. **Same problem?** Or a superficially similar symptom with a different cause?
2. **Same solution?** A different fix for the same problem is often still a
   duplicate in practice - the maintainer only wants one.
3. **Is it active?** Check last comment date, assignee, linked PR, draft status.
4. **What did maintainers say?** Their comment is the most important text on the
   page. Quote it.
5. **Why was it closed?** `not planned` is a rejection; `completed` means it may
   already be fixed on `main` but not released.

---

## Status taxonomy

| Status | Meaning | Default action |
|---|---|---|
| `CLEAR` | No materially related issue, PR, discussion, or recent change found. | Candidate may proceed. |
| `RELATED` | Similar topic exists, but the candidate has a distinct root cause or scope. | Document the relationship; proceed carefully; reference it in the PR. |
| `PARTIALLY_COVERED` | Existing work solves only part of the problem. | Clarify the non-overlapping scope explicitly. |
| `CLAIMED` | Another contributor appears to be actively implementing the same change. | Do not duplicate. Coordinate or drop. |
| `DUPLICATE` | Same problem and materially the same solution already exists. | Reject. |
| `REJECTED` | Maintainers previously rejected this direction. | Reject unless assumptions demonstrably changed. |
| `SUPERSEDED` | A newer architecture, branch, or release makes the finding obsolete. | Reject. |
| `UNKNOWN` | Current remote activity could not be checked adequately. | Do **not** classify as clear. Lower confidence. |

---

## Confidence rules

| Confidence | When |
|---|---|
| **HIGH** | `gh` authenticated; issues, PRs (all states, including drafts), and recent commits searched with ≥8 query variants; discussions checked or confirmed disabled. |
| **MEDIUM** | Remote searched but a source was unavailable (e.g. discussions not accessible), or fewer variants were run. |
| **LOW** | `gh` unavailable or unauthenticated; only local evidence (git log, TODOs) was used. |

**Two absolute rules:**

1. `CLEAR` requires a successful remote check of both issues *and* pull requests
   in this run. No exceptions.
2. If remote access failed, the status is `UNKNOWN` and the document states
   `Duplicate-detection confidence: LOW`, with a note that a human must recheck
   before implementation.

---

## Degraded mode (no `gh`)

When `gh` is missing or unauthenticated, you can still do useful work:

```bash
git log --since='12 months ago' --oneline -- <path>       # recent fixes
git log --grep='<term>' --oneline -i --all                # historical mentions
git branch -r --sort=-committerdate | head -30            # in-flight branches
```

Plus `WebFetch` against public issue/PR search URLs where the user permits
network access. Record clearly which sources were and were not reachable, keep
the status at `UNKNOWN`, and tell the user in the final summary that duplicate
status must be verified manually.

---

## Output

- Phase 2: `02-existing-work-map.md` (template:
  `templates/existing-work-map.md`) plus `evidence/github-searches.json`.
- Phase 5: a per-candidate duplicate section - status, confidence, every query
  run, every related item with number/title/state/author/date, and the reasoning
  that led to the status.
