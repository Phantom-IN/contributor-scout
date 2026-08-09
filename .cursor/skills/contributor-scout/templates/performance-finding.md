<!--
PERFORMANCE CANDIDATE TEMPLATE - Contributor Scout

Extends templates/candidate-finding.md. Every heading from the canonical
template must be present, plus the performance-specific sections below.

HARD RULE: no performance candidate is shortlisted without a credible
measurement or benchmark strategy.
-->

# PERF-<nnn>: <Specific bottleneck> in <component>

| Field | Value |
|---|---|
| Candidate ID | `PERF-<nnn>` |
| Category | `performance` |
| Bottleneck type | algorithmic / repeated work / I/O / concurrency / memory / cold start |
| Repository | `<owner/name>` |
| Analysed at commit | `<short SHA>` on `<branch>` |
| Generated | `<YYYY-MM-DD>` |

## Classification and disposition

- **Disposition:** `SHORTLIST` / `NEEDS_MAINTAINER_INPUT` / `HOLD` / `REJECT`
- **Category:** performance
- **Bottleneck type:** <category>
- **Expected magnitude:** <measured or estimated, with the basis stated>
- **Contribution score:** `<nn>`/100 - band `<band>`
- **Affected component:** `<module>`

## Executive summary

<Two to four sentences: which path, what the cost is, how it scales, and what
the proposed change does.>

## Project and user impact

- **Who is affected:** <users / operators / CI>
- **Under what conditions:** <data size, concurrency, configuration>
- **How often the path runs:** <per request / per startup / per item>
- **Concrete consequence:** <latency, throughput, memory, cost, timeout>
- **Evidence:** `[TEST]` / `[CODE]` <citation>

## Path importance

Establish that the path matters **before** arguing it is slow.

| Signal | Evidence |
|---|---|
| Invocation frequency | `[CODE]` called from `path:line`, once per <unit> |
| Already benchmarked by the project | `[CODE]` `<benchmark file>` |
| Reported by users | `[MAINTAINER]` issue #<n> |
| Scales with user-controlled data | `[CODE]` loop over `<collection>` at `path:line` |
| High churn | `[HISTORY]` <n> commits in 12 months |

<If no signal can be produced, reject the candidate: "path importance not
established".>

## Affected components and exact source locations

| Location | Role | Evidence |
|---|---|---|
| `path:line-line` | the cost centre | `[CODE]` |
| `path:line` | call site establishing frequency | `[CODE]` |

## Current behaviour

<What the code does now, and what it costs. Be specific about the operation:
re-parses, re-allocates, re-queries, re-compiles.>

## Expected behaviour

<What an efficient implementation would do, and why that is safe here.>

## Root cause or capability gap

<Why the cost exists: wrong data structure, missing memoisation, per-call
initialisation, N+1 access pattern, serial I/O, etc.>

## Cost model and scaling

```text
Complexity:  O(<expression>) where n = <what the user controls, typical range>
Frequency:   <invocations per request / per run>
Unit cost:   <measured or estimated per-invocation cost, with basis>
Aggregate:   <arithmetic showing the total effect>
```

State clearly which numbers are measured `[TEST]` and which are estimated
`[INFERENCE]`.

## Evidence

| # | Claim | Tag | Source |
|---|---|---|---|

## Reproduction, benchmark, or demand evidence

### Benchmark design

| Element | Content |
|---|---|
| **Scenario** | <data size, invocation pattern, concurrency, platform, configuration - and why it is representative> |
| **Baseline** | <exact command on the current default branch> |
| **Measurements** | median, p95 / throughput; plus CPU, memory, allocations, I/O, or query count as relevant |
| **Comparison** | current `main` vs proposed; correctness edge cases; invalidation or fallback path |
| **Success criterion** | <threshold justified by the project's own context> |
| **Correctness guard** | <tests proving identical output, stable API, no leak or race regression> |

### Baseline measurement

```text
Command:   <exact command>
Platform:  <OS, CPU, runtime version>
Runs:      <n>
Result:    median <x>, p95 <y>
```

<If no measurement was taken, say so plainly and set the
`no_reproducible_evidence` risk flag. Do not present an estimate as a
measurement.>

### Harness availability

- **Existing harness:** <name and location, or "none">
- **If none:** <proposed harness in the project's idiom, and a note that adding
  one may itself require maintainer agreement>

## Existing mitigations and false-positive analysis

**What already limits the cost**

| Mitigation | Location | Effect |
|---|---|---|

**Why this might not be worth changing**

1. <the path may be less hot than it looks>
2. <the runtime/compiler may already optimise this>
3. <the project may have chosen clarity deliberately - check comments and history>

**Why it survives**

<Reasoning with evidence.>

## Related issues, PRs, discussions, and recent commits

| Type | Ref | Title | State | Relationship |
|---|---|---|---|---|

## Introducing commit and original PR

- **Introducing commit:** `<sha>` - <subject> (<date>) `[HISTORY]`
- **Introducing PR:** #<n>, or `not identified`
- **Original objective:** <what it was solving>

## Historical design constraints

<Why the current implementation was reasonable when written - e.g. the data was
small, no cache layer existed, the path ran once per process.>

## Changed assumptions

| Assumption at introduction | Evidence | Still true? | What changed |
|---|---|---|---|

## Proposed solution direction

<The minimal change. If it involves caching, specify: what is cached, the key,
the invalidation trigger, the bound on size, and the behaviour on a stale hit.
An unbounded or unclear cache is a rejection.>

## Alternative solutions considered

| Alternative | Expected gain | Complexity | Risk | Why not chosen |
|---|---|---|---|---|

## Trade-off analysis

| Dimension | Effect |
|---|---|
| Readability / maintenance | |
| Memory | |
| Correctness risk | |
| Behaviour change (error timing, laziness, ordering, logs) | |
| Platform / version dependence | |
| New dependency | |

## Minimum PR scope

<Files expected to change, and the one coherent change being made.>

## Optional follow-ups

<Further optimisations for later PRs.>

## Explicit exclusions

<Unrelated optimisations, refactors, style changes, adjacent hot paths.
Performance PRs attract scope creep more than any other kind.>

## Backward compatibility and maintenance cost

- **Public API impact:** <none / additive / behavioural>
- **Observable behaviour change:** <timing, ordering, laziness, error messages>
- **Ongoing cost:** <cache invalidation logic, new configuration, new tests>

## Required tests and documentation

| Test | Type | What it proves |
|---|---|---|
| <name> | regression | Output is identical to the current implementation |
| <name> | benchmark | The improvement is measurable and reproducible |
| <name> | edge case | Invalidation / fallback path behaves correctly |

- **Documentation impact:** <performance notes, configuration docs>

## Maintainer-facing pitch

> **Problem.** <cost on a path that matters, with the measurement>
> **Where.** `file:line`, called <frequency>
> **Why it is like this.** <historical constraint>
> **What changed.** <assumption that no longer holds>
> **Proposal.** <minimum scope>
> **Measurement.** <how they can verify it themselves>
> **Not included.** <exclusions>
> **Compatibility.** <impact, or "none">

## Duplicate status and confidence

- **Status:** `<status>`
- **Duplicate-detection confidence:** `HIGH` / `MEDIUM` / `LOW`
- **Query variants run:** <list>
- **Reasoning:** <why>

## Overall score

<Table from templates/candidate-finding.md, produced by
`scripts/calculate_candidate_score.py`.>

## Confidence

- **Overall confidence:** `Confirmed` / `High` / `Medium` / `Low`
- **What would raise it:** <run the benchmark; profile the real workload>
- **What would falsify it:** <the benchmark shows less than the threshold>

## Recommended next action

<e.g. "Run the baseline benchmark, then comment on issue #<n> with the numbers
before implementing.">

## Open questions

| # | Question | Who can answer | What it blocks |
|---|---|---|---|

## Rejection conditions

- <the benchmark shows improvement below the success criterion>
- <the path proves to be cold in realistic workloads>
- <maintainers state the current implementation is a deliberate clarity choice>
