# Showcase — verified maintainer outcomes

This is the registry of real contributions that started as Contributor Scout
candidates, and what the maintainers of the target projects actually did with
them. It is the project's scoreboard, and it follows the project's own rules:

- **Outcomes, not claims.** Every entry links to a public pull request, issue,
  or discussion that anyone can read.
- **Rejections are listed too.** A registry with only wins is marketing; the
  declined and redirected entries are what make the accepted ones credible —
  and they are exactly what recalibrates the scoring rubric.
- **A human shipped it.** Contributor Scout produced the dossier; the
  contributor verified the evidence, wrote the code, and owns the PR. Entries
  credit the person, not the tool.

Once the registry holds ten or more entries, the acceptance rate — including
the unflattering breakdown — will be published in the README, per
[Roadmap Theme 1](ROADMAP.md#theme-1--proof-and-reputation).

---

## Merged and accepted

| Date | Target repository | Contribution | Category | Mode | Outcome | Contributor |
|---|---|---|---|---|---|---|
| 2026-11-23 | BaaRai/ARTEX | [PR #517](https://github.com/BaaRai/ARTEX/pull/517) — check for Docker buildx before building the image (FEAT-001) | FEAT | full | Merged, no changes requested | [@Phantom-IN](https://github.com/Phantom-IN) |
| 2026-11-23 | BaaRai/ARTEX | [PR #481](https://github.com/BaaRai/ARTEX/pull/481) — seed a goal URL that is followed by punctuation (BUG-001) | BUG | full | Merged after one review round | [@Phantom-IN](https://github.com/Phantom-IN) |

**What the review of #481 taught us.** The maintainer's review was a table of
probe inputs, base vs head. One of them, `http://[::1]`, regressed: trimming
trailing punctuation also stripped the closing bracket of an IPv6 host. The fix
went in the same day, but the dossier should have listed that input. That is
why candidate files now carry a mandatory "Regression probes" section. BUG-001
was also a plain bug the scorer had no category for; `correctness` exists now
for the same reason.

### In review

Not counted in any acceptance rate until the maintainers decide. These came
from the `performance-reviewer` and `feature-scout` subagents run on their own,
outside a full skill run.

| Opened | Target repository | Contribution | Category | Source |
|---|---|---|---|---|
| 2026-11-25 | BaaRai/ARTEX | [PR #540](https://github.com/BaaRai/ARTEX/pull/540) — index exchanges on (host, ts) | PERF | `performance-reviewer` |
| 2026-11-25 | BaaRai/ARTEX | [PR #541](https://github.com/BaaRai/ARTEX/pull/541) — set LLM profile prices in the settings dialog | FEAT | `feature-scout` (an unshipped maintainer follow-up from issue #70) |
| 2026-11-25 | BaaRai/ARTEX | [Issue #542](https://github.com/BaaRai/ARTEX/issues/542) + [PR #543](https://github.com/BaaRai/ARTEX/pull/543) — write the full-text index off the request path | PERF | `performance-reviewer` (issue first, with the trade-off laid out) |

<!-- Entry format (keep the table sortable by date, newest first):
| Date | Target repository | Contribution | Category | Mode | Outcome | Contributor |
|---|---|---|---|---|---|---|
| 2026-08-15 | owner/repo | [PR #123](https://github.com/owner/repo/pull/123) — cache compiled schema | PERF | full | Merged | [@you](https://github.com/you) |
-->

## Discussed, redirected, or declined

*Nothing recorded yet. These entries are as welcome as the merged ones —
"maintainer redirected the approach before code was written" is the system
working exactly as designed.*

## Disclosed responsibly

Security findings routed through private disclosure are listed here only
after the target project has published a fix or advisory, and only with the
maintainers' outcome — never with vulnerability detail that the upstream
advisory does not itself disclose.

*Nothing recorded yet.*

---

## Add your outcome

1. Ship the contribution yourself, per
   [the human workflow](README.md#the-human-workflow) — verify the evidence,
   write the code, submit the PR under your name.
2. When the maintainers respond (merge, redirect, decline, or a substantive
   discussion), record it:
   - **Easiest:** file an
     [outcome report](https://github.com/Phantom-IN/contributor-scout/issues/new?template=30-outcome-report.yml)
     and we will add the entry, or
   - open a PR editing this file directly, following the comment template
     above.
3. Honest labelling only: the candidate must genuinely have come from a
   Contributor Scout run (any mode). "The tool said nothing was worth doing and
   it was right" stories are valuable too — file them as outcome reports; they
   are counted, even though they have no PR to link.

What the entries feed: the public acceptance-rate metric, the rating-anchor
calibration described in the [roadmap](ROADMAP.md#theme-1--proof-and-reputation),
and the case studies. One honest entry moves this project further than any
amount of prose.
