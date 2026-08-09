# Git History and Maintainer-Intent Analysis (Phase 4)

Tracing the change that introduced a behaviour gives context static review
cannot. The goal is to understand the requirement and constraints that made the
current design reasonable **at the time**, then determine whether those
assumptions still hold.

> **History is explanation, not blame.**
> Never name a contributor as the cause of a defect. Never write "the author
> failed to". Frame every historical finding as a constraint that has since
> changed.

---

## Investigation sequence

Run `scripts/collect_git_history.py` first; it automates most of this and writes
structured JSON.

```bash
python3 scripts/collect_git_history.py \
  --repo . --path src/config/loader.py --start-line 41 --end-line 67 \
  --output contribution-discovery/evidence/history-PERF-001.json
```

Manual equivalents, in order:

```bash
git blame -L 41,67 -- src/config/loader.py     # who/when for each line
git log -L 41,67:src/config/loader.py          # evolution of that range
git log --follow --oneline -- src/config/loader.py   # survives renames
git show <commit>                              # the full introducing change
git show --stat <commit>                       # blast radius of that commit
git log -1 --format='%H%n%an%n%ad%n%s%n%n%b' <commit>   # full message
git branch --contains <commit>                 # where it landed
git tag --contains <commit> | head -5          # first release containing it
git log --merges --ancestry-path <commit>..HEAD | tail -5   # merge that carried it
```

`git blame` shows the *last* change to a line, not necessarily the one that
introduced the behaviour. Follow blame backwards through reformattings, moves,
and renames (`git blame -w -C -C`) until you reach a commit that actually
changed semantics.

---

## Mapping a commit to a pull request

In priority order:

1. **Merge commit subject** - `Merge pull request #1234 from ...` is definitive.
2. **Squash-merge subject** - `Some change (#1234)` is the GitHub squash
   convention and is reliable.
3. **Commit trailers** - `Closes #123`, `Fixes #456`, `PR-URL:`, `Reviewed-by:`.
4. **`gh` lookup** - `gh api repos/{owner}/{repo}/commits/{sha}/pulls` returns
   the PRs containing a commit (read-only).
5. **Search** - `gh pr list --search '<sha>'` or `gh search prs '<sha>'`.

> **Do not guess a PR number.** If none of the above resolves it, write
> "introducing PR not identified" and explain what you tried. A wrong PR
> reference in a contribution proposal destroys credibility instantly.

---

## Questions to answer

For each candidate whose history you trace:

1. What problem was the original change solving? (Read the message and the
   linked issue, not just the diff.)
2. What compatibility, lifecycle, API, platform, or deployment constraints
   existed then? Check what else the codebase looked like at that commit
   (`git show <commit>:<other-file>`).
3. Was the current behaviour **deliberate** or an incidental side effect? A
   deliberate choice needs a much stronger argument to change.
4. Did reviewers note follow-up work, limitations, or a planned migration?
   Read the PR discussion where accessible - reviewer comments frequently say
   "let's do the simple thing now and revisit".
5. Have later releases removed the original constraint? (Dropped Python/Node
   versions, a new dependency now available, a subsystem that now exists.)
6. Does the proposed change preserve the original intent while adapting to the
   current architecture?

---

## Reading the surrounding history

Beyond the single introducing commit:

```bash
git log --oneline --since='24 months ago' -- <path>   # how the file evolved
git log --grep='<subsystem>' --oneline -i -20         # related work elsewhere
git shortlog -sne -- <path>                           # who owns this area
git log --format='%an' -- <path> | sort | uniq -c | sort -rn | head -5
```

Knowing who has touched the file most tells you who will review the PR, and
their commit messages tell you what they care about.

---

## Changed-assumptions table

This table is the core of the historical argument. Include it in every candidate
whose history was traced.

| Assumption at introduction | Evidence | Still true? | What changed |
|---|---|---|---|
| Config was loaded once per process | `[HISTORY]` `a1b2c3d` message | No | Per-request call site added in `d4e5f6a` (2021) |
| No caching layer existed | `[CODE]` tree at `a1b2c3d` | No | `cache/` subsystem added in v2.1 |

If every assumption still holds, the current design is probably still correct
and the candidate should likely be rejected. That is a useful outcome.

---

## Maintainer framing

Write the pitch in this shape:

> The original implementation was appropriate under constraint **X**. Since the
> project changed **Y**, the same approach now causes **Z**. This proposal
> preserves the original intent while adapting the implementation to the current
> architecture.

Concrete example:

> `Config.load()` was written when configuration was read once at process start
> (`a1b2c3d`, 2019), so re-reading the file was free. Since the per-request
> reload path was added in `d4e5f6a` and the `cache/` lifecycle landed in v2.1,
> the same code now re-parses the file on every request. This proposal reuses
> the existing cache boundary and keeps the reload semantics the original change
> was protecting.

Test it: **would this framing read as respectful to the original author?** If
not, rewrite it before it goes anywhere near a maintainer.

---

## When history is unavailable

Shallow clones, squashed imports, vendored code, and generated files all break
history tracing. Handle it explicitly:

- try `git fetch --unshallow` **only** if the user approves the network call;
- note "history unavailable: shallow clone" or "file imported in initial commit"
  in the candidate;
- do not fabricate historical context;
- reduce the `historical_justification` rating accordingly - the scoring script
  treats missing history as a low rating, not a zero-cost omission.

---

## Output

- `evidence/history-<candidate-id>.json` from the script.
- A populated "Introducing commit and original PR", "Historical design
  constraints", and "Changed assumptions" section in each candidate, every claim
  tagged `[HISTORY]` with a real SHA.
