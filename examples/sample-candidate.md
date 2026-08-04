# PERF-001: Schema is recompiled on every `validate()` call

> **FICTIONAL EXAMPLE.** `example-org/fluxconf` is an invented repository. Every
> file path, line number, commit SHA, issue number, and measurement below is
> fabricated to demonstrate the expected report style. Nothing here is a claim
> about any real project.

| Field | Value |
|---|---|
| Candidate ID | `PERF-001` |
| Category | `performance` |
| Bottleneck type | repeated work (schema compilation) |
| Repository | `example-org/fluxconf` |
| Analysed at commit | `9f3a1c2` on `main` |
| Generated | 2026-07-29 |
| Skill version | `contributor-scout 1.0.0` |

## Classification and disposition

- **Disposition:** SHORTLIST
- **Category:** performance
- **Bottleneck type:** repeated work - JSON Schema is compiled per call rather than per schema
- **Expected magnitude:** 3.9 ms saved per `validate()` call on the sample schema, measured locally
- **Contribution score:** 90/100 - band Excellent contribution candidate
- **Affected component:** `fluxconf.validation`

## Executive summary

`Validator.validate()` compiles the JSON Schema on every invocation instead of
caching the compiled form. The validator is called once per configuration reload
and once per incoming request in the server integration, so the compilation cost
is paid continuously rather than once per schema. A local benchmark shows 4.1 ms
per call, of which 3.9 ms is compilation. Reusing the schema-lifecycle cache that
the project already added in v2.1 removes the repeated work without changing the
public API or the error behaviour.

## Project and user impact

- **Who is affected:** every user of `fluxconf.server`, and any library consumer calling `validate()` in a loop
- **Under what conditions:** all configurations; cost grows with schema size
- **How often:** once per request in the server integration, plus once per configuration reload
- **Concrete consequence:** at the 500 req/s throughput target documented in the README, schema compilation accounts for roughly 2 CPU-seconds per wall-clock second across workers
- **Evidence:** `[TEST]` benchmark below; `[CODE]` call site at `fluxconf/server/handler.py:88`

## Path importance

| Signal | Evidence |
|---|---|
| Invocation frequency | `[CODE]` called from `fluxconf/server/handler.py:88`, inside `handle()` rather than at startup |
| Already benchmarked by the project | `[CODE]` `benchmarks/bench_validation.py:12` benchmarks `validate()` directly |
| Reported by users | `[MAINTAINER]` issue #412 "validation is slower than expected under load", maintainer @fictional-maintainer replied "we should look at compilation caching" |
| Scales with user data | `[CODE]` compilation walks the whole schema tree at `fluxconf/validation/compiler.py:64-97` |
| High churn | `[HISTORY]` 14 commits touched `fluxconf/validation/` in the last 12 months |

## Affected components and exact source locations

| Location | Role | Evidence |
|---|---|---|
| `fluxconf/validation/validator.py:41-67` | the cost centre - `compile_schema()` invoked inside `validate()` | `[CODE]` |
| `fluxconf/validation/compiler.py:64-97` | schema tree walk performed on each compilation | `[CODE]` |
| `fluxconf/server/handler.py:88` | per-request call site establishing frequency | `[CODE]` |
| `fluxconf/cache/lifecycle.py:22-58` | existing cache boundary added in v2.1, keyed by schema identity | `[CODE]` |

## Current behaviour

`Validator.validate(document)` calls `compile_schema(self.schema)` at
`fluxconf/validation/validator.py:52` before every validation pass. The compiler
walks the full schema tree, resolves `$ref` pointers, and builds a closure tree,
returning a fresh compiled object each time. No memoisation exists on this path;
the compiled object is discarded when `validate()` returns. `[CODE]`

## Expected behaviour

A compiled schema should be built once per distinct schema and reused for
subsequent validations of that schema, invalidated when the schema itself
changes. The project already applies exactly this pattern to resolver results
via `cache/lifecycle.py`, which is documented in `docs/architecture.md` as "the
single place where derived artefacts are cached and invalidated". `[DOCS]`

## Root cause or capability gap

Compilation is coupled to validation rather than to schema lifetime. When
`validate()` was written the validator was constructed per process and used once
per configuration load, so per-call compilation and per-schema compilation were
the same thing. The per-request server integration, added later, broke that
equivalence without revisiting the compilation site. `[HISTORY]`

## Cost model and scaling

```text
Complexity:  O(n) per call, where n = schema nodes (typical 200-2,000 in the
             project's own fixtures)
Frequency:   1 per HTTP request (server integration) + 1 per config reload
Unit cost:   3.9 ms of the 4.1 ms median call, measured on the sample schema
Aggregate:   at the documented 500 req/s target, ~1.95 CPU-seconds per
             wall-clock second across workers
```

Measured: unit cost and median call time `[TEST]`. Estimated: the aggregate
figure, which assumes uniform schema size and the README's throughput target
`[INFERENCE]`.

## Evidence

| # | Claim | Tag | Source |
|---|---|---|---|
| 1 | `compile_schema()` is called inside `validate()`, not at construction | `[CODE]` | `fluxconf/validation/validator.py:52` |
| 2 | No memoisation exists on the compilation path | `[CODE]` | `fluxconf/validation/compiler.py:64-97` |
| 3 | `validate()` is called once per request | `[CODE]` | `fluxconf/server/handler.py:88` |
| 4 | Median `validate()` call is 4.1 ms; 3.9 ms is compilation | `[TEST]` | `python -m pytest benchmarks/bench_validation.py --benchmark-only`, output in `evidence/commands-run.md` |
| 5 | Compilation predates the v2.1 cache lifecycle | `[HISTORY]` | commit `a1b2c3d` (2019-04-11) |
| 6 | A maintainer has already suggested compilation caching | `[MAINTAINER]` | issue #412, comment by @fictional-maintainer |
| 7 | Aggregate CPU cost at the documented throughput target | `[INFERENCE]` | arithmetic above; assumes uniform schema size |
| 8 | Whether any consumer relies on per-call recompilation for hot schema edits | `[UNVERIFIED]` | resolve by asking maintainers on #412 |

## Reproduction, benchmark, or demand evidence

### Benchmark design

| Element | Content |
|---|---|
| **Scenario** | The project's own `benchmarks/fixtures/large_schema.json` (1,204 nodes), single-threaded, 1,000 iterations, Python 3.12, macOS arm64. Representative because it is the fixture the maintainers already benchmark against. |
| **Baseline** | `python -m pytest benchmarks/bench_validation.py --benchmark-only` on `main` at `9f3a1c2` |
| **Measurements** | Median and p95 wall time per `validate()` call; allocation count via `tracemalloc`; no I/O involved |
| **Comparison** | Current `main` vs cached compilation; plus a schema-mutation case proving invalidation works, and a distinct-schema case proving the cache is keyed correctly |
| **Success criterion** | Median `validate()` time on the existing fixture falls below 1 ms, and the project's existing benchmark suite shows no regression elsewhere. Chosen because 1 ms keeps validation under 10% of the project's documented 12 ms per-request budget. |
| **Correctness guard** | Existing validation test suite passes unchanged; new tests assert identical error messages and error ordering for invalid documents, and assert that mutating a schema object produces newly compiled behaviour |

### Baseline measurement

```text
Command:   python -m pytest benchmarks/bench_validation.py --benchmark-only
Platform:  macOS 15 arm64, CPython 3.12.3
Runs:      1,000 iterations, 5 rounds
Result:    median 4.13 ms, p95 4.61 ms
           with compilation stubbed out: median 0.21 ms
```

Laptop measurements are noisy; these are medians over five rounds and should be
reproduced on the maintainer's platform before the numbers are quoted publicly.

### Harness availability

- **Existing harness:** `benchmarks/bench_validation.py`, `pytest-benchmark`
- **If none:** not applicable - the project already benchmarks this exact function

## Existing mitigations and false-positive analysis

**What already limits the cost**

| Mitigation | Location | Effect |
|---|---|---|
| `$ref` resolution results are cached | `fluxconf/cache/lifecycle.py:22-58` | Removes network and file I/O, but not the tree walk |
| Server integration is optional | `fluxconf/server/__init__.py:9` | Library-only users pay the cost less often |

**Why this might not be worth changing**

1. The maintainers may have deliberately kept compilation per-call so that
   in-place schema mutation takes effect immediately - a documented behaviour for
   the interactive `fluxconf edit` workflow.
2. CPython may already be cheaper here than the benchmark suggests under a real
   workload with warm caches.
3. Adding a cache introduces an invalidation surface the project would own
   forever.

**Why it survives**

Point 1 is the real risk and is unresolved - it is recorded as `[UNVERIFIED]`
evidence #8 and as the primary open question. Point 2 is addressed by using the
project's own fixture and harness rather than a synthetic benchmark. Point 3 is
mitigated by reusing the existing `cache/lifecycle.py` boundary instead of
introducing a new mechanism, which keeps the invalidation surface unchanged.

## Related issues, PRs, discussions, and recent commits

| Type | Ref | Title | State | Relationship |
|---|---|---|---|---|
| Issue | #412 | "validation is slower than expected under load" | open | Same symptom; no root cause identified in the thread; maintainer suggested compilation caching |
| Issue | #298 | "cache `$ref` resolution" | closed (completed) | Partially related - solved the I/O half in v2.1, not the tree walk |
| PR | #451 | "docs: clarify validation performance" | merged | Documentation only; no code overlap |
| Commit | `7e2b9d0` | "perf: avoid re-reading schema files" | - | Adjacent optimisation on the same subsystem; does not touch compilation |

## Introducing commit and original PR

- **Introducing commit:** `a1b2c3d` - "validation: compile schema before each pass" (2019-04-11) `[HISTORY]`
- **Introducing PR:** #87 - "Add JSON Schema validation" (verified via squash-merge subject `(#87)`)
- **First release containing it:** `v0.4.0` (`git tag --contains a1b2c3d`)
- **Original objective:** add schema validation at all; the compile step was placed inside `validate()` because the validator was constructed per process and used once per configuration load `[HISTORY]`

## Historical design constraints

At `a1b2c3d` the library had no caching layer at all - `fluxconf/cache/` did not
exist, and the only consumer was the CLI, which loaded one configuration and
exited. Compiling inside `validate()` was the simplest correct choice and cost
nothing, because `validate()` was called at most once per process. The PR
discussion on #87 explicitly deferred caching: "no need to cache until we have a
long-running consumer." That consumer arrived four years later. `[HISTORY]`

## Changed assumptions

| Assumption at introduction | Evidence | Still true? | What changed |
|---|---|---|---|
| `validate()` is called at most once per process | `[HISTORY]` PR #87 discussion | No | The server integration calls it per request - `fluxconf/server/handler.py:88`, added in `d4e5f6a` (2023) |
| No caching layer exists | `[HISTORY]` tree at `a1b2c3d` | No | `fluxconf/cache/lifecycle.py` landed in v2.1 with a documented invalidation contract |
| Schemas are small | `[HISTORY]` fixtures at `a1b2c3d` were under 50 nodes | No | The project's own benchmark fixture is now 1,204 nodes |

## Proposed solution direction

Move compilation from per-call to per-schema by storing the compiled form
through the existing `cache/lifecycle.py` boundary.

- **What is cached:** the compiled schema closure tree
- **Key:** the schema's identity and content hash, as `cache/lifecycle.py` already does for `$ref` results
- **Invalidation:** the existing lifecycle invalidation trigger - no new mechanism
- **Bound:** the existing cache's LRU bound (`fluxconf/cache/lifecycle.py:31`), unchanged
- **Stale hit behaviour:** identical to `$ref` caching today - the content hash changes, so a mutated schema misses the cache and recompiles

No public API change. `Validator.validate()` keeps its signature, its return
type, and its error behaviour.

## Alternative solutions considered

| Alternative | Expected gain | Complexity | Risk | Why not chosen |
|---|---|---|---|---|
| Compile eagerly in `Validator.__init__` | Same | Lower | Breaks the `fluxconf edit` workflow where schemas are mutated after construction | Changes observable behaviour |
| Add a `compiled_schema` parameter to `validate()` | Same, opt-in | Low | Public API change; pushes the problem to every caller | Breaks the "no API change" property |
| Memoise with `functools.lru_cache` on `compile_schema` | Same | Lowest | Unbounded by schema identity; a second cache mechanism to maintain; ignores the project's documented cache boundary | Conflicts with the architecture document |
| Rewrite the compiler to be incremental | Larger | Very high | Wide blast radius | Far beyond a first contribution's scope |

## Trade-off analysis

| Dimension | Effect |
|---|---|
| Readability / maintenance | Slight - one extra indirection through an existing, documented cache |
| Memory | One compiled tree retained per distinct schema, bounded by the existing LRU |
| Correctness risk | Concentrated in invalidation; mitigated by reusing the existing tested boundary |
| Behaviour change | A mutated schema object with an unchanged content hash would now reuse the compiled form - this is the open question for maintainers |
| Platform / version dependence | None |
| New dependency | None |

## Minimum PR scope

Route `compile_schema()` through `cache/lifecycle.py` at
`fluxconf/validation/validator.py:52`, add the cache key, and add two tests.
Expected diff: 3 files, roughly 60 lines including tests.

## Optional follow-ups

- Extend the benchmark suite to cover the multi-schema case.
- Document the compilation cache in `docs/architecture.md` alongside `$ref` caching.

## Explicit exclusions

- No changes to `compiler.py` internals or the tree-walk algorithm.
- No new cache backend, configuration key, or eviction policy.
- No typing, formatting, or lint cleanup in the touched files.
- No fix for the adjacent `$ref` resolution ordering issue noticed at `compiler.py:110`.
- No changes to the server integration.

## Backward compatibility and maintenance cost

- **Public API impact:** none - signature, return type, and exceptions unchanged
- **Configuration impact:** none
- **Observable behaviour change:** only for in-place schema mutation that leaves the content hash unchanged; this is the open question below
- **Migration or deprecation needed:** no
- **Ongoing maintenance burden:** none beyond the existing cache boundary, which the project already maintains

## Required tests and documentation

| Test | Type | What it proves |
|---|---|---|
| `test_validate_reuses_compiled_schema` | regression | The compiler runs once for repeated validations of one schema |
| `test_validate_recompiles_after_schema_change` | regression | Invalidation works when the schema content changes |
| `test_validate_errors_unchanged` | regression | Error messages and ordering are byte-identical to `main` |
| `bench_validation.py::test_validate_large_schema` | benchmark | The improvement is measurable using the project's own harness |

- **Documentation impact:** one paragraph in `docs/architecture.md` under the caching section
- **Changelog entry:** required - the project uses Keep a Changelog format under `## Unreleased / Performance`

## Maintainer-facing pitch

> **Problem.** `validate()` recompiles the schema on every call; on the project's
> own benchmark fixture that is 3.9 ms of a 4.1 ms call.
> **Where.** `fluxconf/validation/validator.py:52`, reached once per request from
> `fluxconf/server/handler.py:88`.
> **Why it is like this.** When validation was added in #87 the validator was
> built once per process and used once, so compiling inside `validate()` was free
> - the PR explicitly deferred caching until there was a long-running consumer.
> **What changed.** The server integration made `validate()` a per-request call,
> and v2.1 introduced the `cache/lifecycle.py` boundary the deferral was waiting
> for.
> **Proposal.** Route compilation through the existing cache boundary, keyed by
> schema content hash, with no public API change.
> **Measurement.** `python -m pytest benchmarks/bench_validation.py
> --benchmark-only` on `main` vs the branch; target is median under 1 ms.
> **Not included.** No compiler internals, no new cache backend, no unrelated
> cleanup.
> **Compatibility.** None, unless in-place schema mutation with an unchanged
> content hash is a supported pattern.
> **Question.** Does the `fluxconf edit` workflow rely on a mutated schema object
> taking effect without a content change? If so, I will scope the cache to the
> server path only.

## Duplicate status and confidence

- **Status:** CLEAR
- **Duplicate-detection confidence:** HIGH
- **Sources checked:** open and closed issues, open/draft/merged/closed PRs, discussions (enabled), recent commits on `main`, published advisories
- **Query variants run:** "schema compilation", "compile schema cache", "validation performance", "slow validation", "compile_schema", "fluxconf/validation/validator.py", "recompile", "memoize schema", "validator cache", "validation slow under load", "per-request validation", "schema cache invalidation" (12 variants; 3 returned results, all recorded above)
- **Reasoning:** issue #412 reports the same symptom but identifies no root cause and has no assignee or linked PR; issue #298 solved the `$ref` half only; no open or draft PR touches `validation/`. The symptom overlap with #412 makes this a candidate to reference in the PR, not a duplicate.

## Overall score

| Category | Weight | Rating (0-5) | Points |
|---|---|---|---|
| Evidence that the problem is real | 15 | 5 | 15.0 |
| User or project impact | 15 | 4 | 12.0 |
| Maintainer and roadmap alignment | 15 | 4 | 12.0 |
| Non-duplication confidence | 15 | 5 | 15.0 |
| Technical solution confidence | 10 | 4 | 8.0 |
| Scope clarity | 10 | 5 | 10.0 |
| Testability | 5 | 4 | 4.0 |
| Backward compatibility | 5 | 5 | 5.0 |
| Historical justification | 5 | 5 | 5.0 |
| Contributor ability to implement | 5 | 4 | 4.0 |
| **Weighted subtotal** | **100** | | **90** |

| Risk deduction | Applied | Points |
|---|---|---|
| Overlapping open or draft PR | no | 0 |
| Previously rejected by maintainers | no | 0 |
| No reproducible evidence | no | 0 |
| Repository appears inactive | no | 0 |
| Breaking public API change | no | 0 |
| Major new dependency | no | 0 |
| Unclear ownership or scope | no | 0 |

**Final score: 90/100 - band Excellent contribution candidate**
(Produced by `scripts/calculate_candidate_score.py`; do not hand-compute.)

## Confidence

- **Overall confidence in this candidate:** Confirmed
- **What would raise it:** a maintainer answering the `fluxconf edit` question on #412; reproducing the benchmark on Linux
- **What would falsify it:** a maintainer confirming that per-call compilation is deliberate for in-place schema mutation

## Recommended next action

Comment on issue #412 with the benchmark baseline, the root cause, and the
proposed minimum scope, and ask the `fluxconf edit` question. Wait for a
maintainer response before implementing - the answer changes whether the cache
should be global or scoped to the server path.

## Open questions

| # | Question | Who can answer | What it blocks |
|---|---|---|---|
| 1 | Does `fluxconf edit` rely on in-place schema mutation taking effect without a content change? | Maintainers, on #412 | The cache scope, and therefore the diff |
| 2 | Is 1 ms the right success criterion, or does the project have a stricter budget? | Maintainers | The benchmark threshold |
| 3 | Does the benchmark hold on Linux CI, or is this arm64-specific? | Any contributor with a Linux machine | The magnitude claim |

## Rejection conditions

- A maintainer states that per-call compilation is intentional for in-place schema mutation.
- An open or draft PR appears touching `fluxconf/validation/`.
- The benchmark on the maintainer's platform shows median improvement below the 1 ms criterion.
- Issue #412 is closed as not planned.
