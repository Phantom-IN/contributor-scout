<!--
FEATURE CANDIDATE TEMPLATE - Contributor Scout

Extends templates/candidate-finding.md. Every heading from the canonical
template must be present, plus the feature-specific sections below.

HARD RULE: every feature candidate starts from a citable demand signal. A Tier 3
(AI-inferred) candidate should rarely be the primary recommendation and defaults
to NEEDS_MAINTAINER_INPUT.
-->

# FEAT-<nnn>: <Capability> for <component or user need>

| Field | Value |
|---|---|
| Candidate ID | `FEAT-<nnn>` |
| Category | `feature` |
| Demand tier | `Tier 1` / `Tier 2` / `Tier 3` |
| Repository | `<owner/name>` |
| Analysed at commit | `<short SHA>` on `<branch>` |
| Generated | `<YYYY-MM-DD>` |

## Classification and disposition

- **Disposition:** `SHORTLIST` / `NEEDS_MAINTAINER_INPUT` / `HOLD` / `REJECT`
- **Category:** feature
- **Demand tier:** `Tier 1` (roadmap / help-wanted / maintainer request) /
  `Tier 2` (repeated user need, ecosystem requirement) /
  `Tier 3` (inferred - discussion first)
- **Contribution score:** `<nn>`/100 - band `<band>`
- **Affected component:** `<module or new surface>`

## Executive summary

<Two to four sentences: the user problem, the evidence it is real, and the
smallest capability that addresses it.>

## Project and user impact

- **Who benefits:** <persona>
- **What they can do afterwards that they cannot do now:** <concrete>
- **How many are affected:** <evidence: reaction counts, duplicate issues,
  support questions>
- **Consequence of not having it:** <current cost to users>

## Demand evidence

| Signal | Strength | Source | Date |
|---|---|---|---|
| <issue / roadmap item / maintainer comment / discussion> | strong / moderate / weak | #<n>, `[MAINTAINER]` | <date> |

**Demand summary:** <how many independent requests, over what period, with what
maintainer engagement>

<If the only signal is your own reasoning, this is Tier 3. Say so plainly.>

## Current workaround

- **What users do today:** <workaround>
- **Why it is insufficient:** <cost, fragility, incompleteness>
- **Evidence:** `[DOCS]` / `[MAINTAINER]` / issue #<n>

## Project and roadmap alignment

- **Stated scope:** "<quote from README/CONTRIBUTING>" `[DOCS]`
- **Stated non-goals:** "<quote>" `[DOCS]`
- **Does this fit?** <argument, referencing the quotes>
- **Roadmap item:** <reference, or "none">
- **Maintainer statements:** "<quote>" `[MAINTAINER]` - #<n>
- **Is another project the correct home?** <plugin, integration, external
  package - answer this explicitly; maintainers will ask>

## Affected components and exact source locations

| Location | Role | Evidence |
|---|---|---|
| `path:line` | extension point the feature would use | `[CODE]` |
| `path:line` | existing analogous feature to model it on | `[CODE]` |

## Current behaviour

<What the software does today in this area, factually, with citations.>

## Expected behaviour

<What the feature would let a user do, described as observable behaviour.>

## Root cause or capability gap

<Why the capability is missing: no extension point, an architectural
assumption, a deliberate earlier decision, or simply that nobody built it.>

## Evidence

| # | Claim | Tag | Source |
|---|---|---|---|

## Reproduction, benchmark, or demand evidence

<For features this is the demand case: issue numbers, reaction counts, quotes,
recurring support questions, and ecosystem requirements. Reference the demand
evidence table above and add anything not captured there.>

## Prior art and rejected alternatives

| Reference | What was proposed | Outcome | Maintainer reasoning |
|---|---|---|---|
| #<n> | <proposal> | closed as not planned / merged / stale | "<quote>" `[MAINTAINER]` |

<If a similar proposal was declined, state specifically what has changed since.
"Time has passed" is not a change in assumptions.>

## Existing mitigations and false-positive analysis

**Why this feature might not be wanted**

1. <it may belong in a plugin or a separate package>
2. <the maintenance burden may exceed the benefit>
3. <it may conflict with a stated non-goal>

**Why it survives**

<Reasoning with evidence.>

## Related issues, PRs, discussions, and recent commits

| Type | Ref | Title | State | Relationship |
|---|---|---|---|---|

## Introducing commit and original PR

<For features, trace the history of the *related subsystem*: when the extension
point was added, when the limitation was introduced, or when a similar feature
was deliberately left out.>

- **Relevant commit:** `<sha>` - <subject> (<date>) `[HISTORY]`
- **Relevant PR:** #<n>, or `not identified`
- **Original objective:** <what that change was solving>

## Historical design constraints

<Why the capability was not built at the time - scope, dependencies,
architecture, or an explicit decision.>

## Changed assumptions

| Assumption then | Evidence | Still true? | What changed |
|---|---|---|---|

## Proposed solution direction

### Minimum viable scope

<The smallest change that delivers real value and is reviewable in one sitting.>

### Proposed surface

```text
<API signature / CLI flag / config key, in the project's existing style>
```

- **Default behaviour:** <must preserve current behaviour>
- **Opt-in mechanism:** <flag, config key, parameter>
- **Follows existing pattern:** `path:line` <the analogous feature>

### Non-goals

<What this proposal deliberately does NOT do. Mandatory - this is the section
that earns maintainer trust.>

## Alternative solutions considered

| Alternative | Pros | Cons | Why not chosen |
|---|---|---|---|

## Architectural fit

- **Extension point used:** `path:line`
- **New abstractions introduced:** <none / list them>
- **New dependency required:** <none / name it and justify>
- **Does it constrain future refactoring?** <assessment>

## Minimum PR scope

<Files expected to change; the coherent unit of work.>

## Optional follow-ups

<Later PRs that build on this, if it lands well.>

## Explicit exclusions

<Adjacent capabilities, generalisations, and refactors deliberately excluded.>

## Backward compatibility and maintenance cost

- **Public API impact:** <additive only, ideally>
- **Configuration impact:** <new optional key with a safe default>
- **Behaviour change for existing users:** <should be "none">
- **Test matrix growth:** <platforms, versions, optional dependencies>
- **Documentation obligation:** <what must be written>
- **Long-term support burden:** <who answers issues about this in three years>
- **Would you maintain it?** <state your willingness - maintainers will ask>

## Required tests and documentation

| Test | Type | What it proves |
|---|---|---|
| <name> | unit | New behaviour works |
| <name> | regression | Existing behaviour is unchanged by default |

- **Documentation impact:** <README, docs page, docstrings, examples>
- **Changelog entry:** <required format>

## Maintainer-facing pitch

> **Problem.** <user need with demand evidence>
> **Evidence.** <issue numbers, counts, quotes>
> **Current workaround.** <and why it is insufficient>
> **Proposal.** <minimum scope in one sentence>
> **Surface.** <the API/flag/config key>
> **Not included.** <non-goals>
> **Compatibility.** <"no change to existing behaviour", ideally>
> **Maintenance.** <who supports it>
> **Question.** <the design decision needed from maintainers>

## Duplicate status and confidence

- **Status:** `<status>`
- **Duplicate-detection confidence:** `HIGH` / `MEDIUM` / `LOW`
- **Closed / not-planned issues checked:** yes/no
- **Query variants run:** <list>
- **Reasoning:** <why>

## Overall score

<Table from templates/candidate-finding.md, produced by
`scripts/calculate_candidate_score.py`.>

## Confidence

- **Overall confidence:** `Confirmed` / `High` / `Medium` / `Low`
- **What would raise it:** <a maintainer replying positively on the issue>
- **What would falsify it:** <a maintainer stating it is out of scope>

## Recommended next action

<Usually: "Comment on issue #<n> proposing the minimum scope and non-goals, and
wait for a maintainer response before implementing." Tier 3 candidates should
always start with a discussion.>

## Open questions

| # | Question | Who can answer | What it blocks |
|---|---|---|---|

## Rejection conditions

- <a maintainer states this belongs in a plugin>
- <the referenced issue is closed as not planned>
- <an open PR implements the same capability>
