# Maintainer Alignment Playbook

A technically correct change that conflicts with project direction is a rejected
pull request. Alignment is worth as many points as impact in the scoring model
(15), and it is the dimension AI reviewers most often get wrong, because it is
the one that cannot be derived from the code.

---

## Where maintainer intent is written down

In descending order of authority:

| Source | What it tells you |
|---|---|
| `CONTRIBUTING.md` | The process, and often explicit statements about what is and is not accepted |
| README scope / non-goals / "alternatives" | The project's own boundary |
| `ROADMAP.md`, milestones, project boards, pinned issues | Where they are going next |
| Issue and PR templates | What they need in order to say yes |
| Governance / `MAINTAINERS` / `CODEOWNERS` | Who decides, and who reviews which area |
| ADRs, `docs/design/`, RFC directories | Decisions already made and why |
| Maintainer comments on closed PRs | The most honest source: why they said no |
| Release notes | What they choose to highlight - their priorities |
| Commit messages by maintainers | Their idiom and standards |

Read at least five recent closed-without-merge PRs. The rejection reasons form a
pattern, and that pattern is the alignment model.

---

## Alignment checklist

Answer each explicitly for every shortlisted candidate:

- [ ] Is the change inside the project's **stated scope**? Quote the scope
      statement.
- [ ] Does it avoid every documented **non-goal**? Quote them.
- [ ] Has this direction been proposed before? What happened?
- [ ] Does the design follow existing idioms (error handling, config, extension
      points), or does it import a foreign pattern?
- [ ] Does it respect the stability policy for the surface it touches?
- [ ] Does it add a dependency? Does the project have a stated policy on that?
      (Many minimal-dependency projects say so loudly.)
- [ ] Does it fit the current release cycle, or does it collide with an in-flight
      refactor?
- [ ] Which maintainer owns this area, and what do their comments suggest they
      care about?
- [ ] Is the size reviewable? Check the size distribution of recently merged PRs.
- [ ] Does the project prefer "issue first" for this kind of change?

---

## Reading the project's culture

| Observation | What it implies for your contribution |
|---|---|
| PRs merged within days, light review | Direct implementation is welcome |
| Long review threads, many revision requests | Discuss first; expect iteration; keep the diff small |
| "Please open an issue before submitting a PR" | Always discuss first, even for small changes |
| Many PRs closed as "out of scope" | Alignment risk is high; weight Tier 1 evidence heavily |
| Detailed CONTRIBUTING with checklists | Follow it exactly; deviation reads as carelessness |
| Consistent commit-message format | Match it; it is a signal you read their history |
| Tests required for every change | Include the test plan in the proposal, not as an afterthought |
| Sparse comments, dense code | Do not add a comment paragraph to a one-line fix |

---

## Alignment rating anchors

Used by `calculate_candidate_score.py` for `maintainer_alignment` (weight 15):

| Rating | Meaning |
|---|---|
| **5** | An explicit maintainer request, roadmap item, or `help wanted` issue asks for exactly this. `[MAINTAINER]` evidence exists. |
| **4** | Clearly within stated scope, matches project idiom, and similar changes have recently been merged. |
| **3** | Plausibly in scope; no direct signal either way; would benefit from confirmation. |
| **2** | Adjacent to scope; touches an area with a stated preference that this change bends; needs discussion first. |
| **1** | Weak fit; similar proposals have been declined for reasons that still apply. |
| **0** | Conflicts with a documented non-goal or an explicit maintainer rejection. |

A rating of 0 or 1 should normally produce disposition `REJECT`, not a low
shortlist entry.

---

## Writing the maintainer-facing pitch

The pitch is the paragraph a human will adapt into an issue comment or PR
description. It must:

1. Lead with the **user-visible problem**, not the code smell.
2. Cite evidence the maintainer can check in under a minute.
3. Acknowledge the original design's reasoning (see
   `references/git-history-playbook.md`).
4. State the **minimum scope** and the explicit exclusions.
5. Name the compatibility impact honestly, including "none".
6. Ask a specific question when the answer changes the design.
7. Be short. Maintainers read many of these.

Template:

> **Problem.** <user-visible symptom, with evidence>
> **Where.** <file:line, and how often the path runs>
> **Why it is like this.** <historical constraint, framed respectfully>
> **What changed.** <assumption that no longer holds>
> **Proposal.** <minimum scope, one sentence>
> **Not included.** <explicit exclusions>
> **Compatibility.** <impact, or "none">
> **Question.** <the one decision you need from them, if any>

Anti-patterns to avoid:

- "This code is inefficient / insecure / badly written."
- Claiming severity without evidence ("critical vulnerability" for a hardening
  suggestion).
- Bundling unrelated cleanups into the proposal.
- Presenting AI analysis as authority. Present evidence; let it stand on its own.
- Implying urgency the maintainer has not agreed to.

---

## Choosing the route

| Signal | Route |
|---|---|
| `help wanted` issue, scope clear | Implement, reference the issue in the PR |
| Existing issue, no assignee, design obvious | Comment stating intent, then implement |
| Existing issue with assignee or draft PR | Offer help; do not duplicate |
| No issue, small and clearly in scope | Small PR is usually fine; check CONTRIBUTING |
| No issue, material scope | Open an issue or discussion first |
| Security-sensitive | Private disclosure channel - see `references/responsible-disclosure.md` |
| Contradicts stated non-goals | Do not pursue |
