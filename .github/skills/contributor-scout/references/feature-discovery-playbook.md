# Feature Discovery Playbook (Phase 3c)

Feature discovery is where speculative AI output is most likely and most costly.
The discipline is inverted from security and performance review: **start from
evidence of demand, then find the capability gap** - never the other way round.

> **Hard rule:** do not invent features from generic assumptions about what a
> project "should" have. Every feature candidate starts from a citable signal
> from the project or its users.

---

## Evidence hierarchy

| Tier | Source of opportunity | Default approach |
|---|---|---|
| **Tier 1** | Roadmap item, `help wanted` / `good first issue`, accepted proposal, explicit maintainer request, documented limitation, or repeatedly requested capability. | Strong candidate for implementation after duplicate check. |
| **Tier 2** | Repeated user workaround, missing compatibility with a common ecosystem tool, natural extension of an existing subsystem, or an ecosystem requirement strongly supported by usage. | Validate with maintainers if scope is material. |
| **Tier 3** | AI-inferred capability gap or developer-experience improvement with no explicit project demand. | Discussion first. High evidence threshold. Usually `NEEDS_MAINTAINER_INPUT`, not `SHORTLIST`. |

A Tier 3 candidate should almost never be the primary recommendation. If your
strongest finding is Tier 3, seriously consider reporting "no contribution
currently meets the threshold" instead.

---

## Step 1 - Harvest demand signals

Search widely before forming any opinion.

```bash
gh issue list --state open  --label enhancement --limit 60 --json number,title,labels,comments,reactionGroups
gh issue list --state open  --label 'help wanted' --limit 40
gh issue list --state open  --label 'good first issue' --limit 40
gh issue list --state closed --limit 60 --search 'is:closed reason:not-planned'
gh pr list --state closed --limit 40 --json number,title,author,closedAt
```

Also read, in the repository:

- `ROADMAP.md`, project boards, milestone descriptions, pinned issues;
- `CHANGELOG` / release notes - direction of travel and recent themes;
- documentation "limitations", "not supported", "known issues" sections;
- `TODO` / `FIXME` / `XXX` / "future work" comments in source;
- discussions (`gh api repos/{owner}/{repo}/discussions` where enabled, or the
  web UI via `WebFetch`);
- issue templates - they reveal what maintainers consider in-scope reporting.

Rank demand honestly:

| Strength | Signal |
|---|---|
| Strong | Maintainer says they want it; roadmap item; issue labelled `help wanted` with maintainer comment |
| Moderate | Multiple independent users request it over time; high reaction counts; recurring support questions |
| Weak | One user asked once; a stale issue with no maintainer engagement |
| None | You thought of it |

Reaction counts and duplicate issues are the most reliable proxy for real
demand. A single enthusiastic requester is not.

---

## Step 2 - Check the graveyard first

Before developing any proposal, check whether it has been proposed and declined:

```bash
gh issue list --state closed --search '<feature terms>' --limit 40 \
  --json number,title,stateReason,closedAt
gh pr list --state closed --search '<feature terms>' --limit 40 \
  --json number,title,closedAt
```

Read maintainer comments on anything closed as `not planned`. A previously
rejected direction is `REJECTED` unless you can articulate specifically what has
changed since - a new dependency became available, the architecture moved, the
maintainer's stated reason no longer applies. "It's been a while" is not a
change in assumptions.

---

## Step 3 - Alignment checks

Answer each explicitly in the candidate:

- Does it fit the project's **stated scope**, and does it avoid the stated
  non-goals? Quote them.
- Have maintainers or users expressed demand? Cite it.
- Is a plugin, integration, or separate project the correct home? Many good
  ideas belong outside core, and maintainers will say so.
- Can an MVP land **without** introducing a broad new subsystem?
- Does it create a new dependency, a new public API commitment, a migration, or
  a long-term support burden? Who maintains it in three years?
- Can it be delivered incrementally and tested deterministically?
- Does it preserve backward compatibility and follow established configuration
  patterns?
- Does it match the project's design idiom, or does it import conventions from
  elsewhere?

---

## Step 4 - Define the smallest viable feature

Write three lists. All three are mandatory.

1. **Minimum viable scope** - the smallest change that delivers real value and
   is reviewable in one sitting.
2. **Optional follow-ups** - what could come later, in separate PRs, if the
   first lands well.
3. **Explicit non-goals** - what this proposal deliberately does *not* do.
   This is the section that earns maintainer trust; it shows you understand the
   cost of what you are asking them to own.

Then specify the surface: proposed API, CLI flag, configuration key, or
extension point, in the project's existing style, with defaults that preserve
current behaviour.

---

## Step 5 - Assess maintenance burden

Maintainers reject features because of the cost after merge, not the cost of
review. Assess:

- ongoing support surface (new configuration, new failure modes, new docs);
- test matrix growth (platforms, versions, optional dependencies);
- documentation obligations;
- backwards-compatibility commitment - can it be removed later?
- who answers issues about it;
- whether it constrains future refactoring.

State whether you would be willing to maintain it, and say so in the pitch.

---

## Step 6 - Choose the first action

| Situation | Recommended first action |
|---|---|
| Tier 1, small, clearly aligned, no open work | Implement, referencing the issue |
| Tier 1, but scope or design is ambiguous | Comment on the issue proposing an approach; wait for a maintainer reply |
| Tier 2, material scope | Open a design discussion or comment before implementing |
| Tier 3 | Discussion first. Do not write code. |
| Existing issue with an assignee or a linked draft PR | Do not duplicate - offer to review or help instead |
| Contradicts a stated non-goal | Do not pursue |

The recommended first action is often "comment, then wait". That is a successful
discovery outcome, not a failure.

---

## Rejection criteria

- No demand signal beyond your own reasoning.
- Conflicts with a documented non-goal or a prior maintainer rejection.
- Requires a new subsystem, a heavy dependency, or a breaking API change to be
  useful.
- Better served by a plugin or an external package.
- Cannot be tested deterministically.
- Scope cannot be reduced to a reviewable first PR.
- The project is in a feature freeze or a rewrite.

---

## Output

One candidate file per proposal, `FEAT-nnn.md`, using
`templates/feature-proposal.md`. Include the demand evidence with citations, the
current workaround and why it is insufficient, roadmap alignment, related and
rejected prior work, minimum scope, non-goals, proposed surface, architectural
fit, compatibility, maintenance cost, tests, documentation impact, the
maintainer-facing pitch, and the recommended first action.
