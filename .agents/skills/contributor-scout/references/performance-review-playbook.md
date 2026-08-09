# Performance Review Playbook (Phase 3b)

The objective is a **measurable improvement on a path that matters**. Code that
looks inefficient is not a finding. You must explain why the path is important,
how the cost scales, how it will be measured, and what the change costs in
complexity.

> **Hard rule:** no performance candidate is shortlisted without a credible
> measurement or benchmark strategy. If you cannot describe how a maintainer
> would verify the improvement, the candidate is rejected.

---

## Required proof chain

```text
Important execution path
        ↓  (why does this path matter? how often does it run?)
Identified cost centre
        ↓  (file:line - what specifically costs)
Scaling or frequency explanation
        ↓  (O(n²) in what? per request? per file? per element?)
Benchmark or profiling plan
        ↓  (exact command, data shape, baseline)
Proposed improvement
        ↓  (minimal change, not a redesign)
Expected measurable effect
        ↓  (justified magnitude, not "faster")
Correctness, memory, latency, and complexity trade-offs
```

---

## Step 1 - Establish that the path matters

Do this **before** looking for inefficiency, or you will find inefficiency in
code that runs twice a year.

Evidence that a path is important:

| Signal | How to check |
|---|---|
| Runs per request / per item / per startup | Trace call sites from Phase 1's entry points |
| Already benchmarked by the project | Existing benchmark suite - the maintainers told you what matters |
| Appears in issue reports | Search issues for "slow", "hang", "timeout", "memory", "CPU", "OOM" |
| High churn | `git log --since='12 months ago' --name-only --pretty=format: \| sort \| uniq -c \| sort -rn` |
| Scales with user data | Loops over collections whose size the user controls |
| Documented as a hot path | Comments, docs, or profiling notes in the repo |

If you cannot produce one of these signals, stop. Record it as rejected with the
reason "path importance not established".

---

## Step 2 - Find the cost centre

Target categories, roughly in descending order of typical value:

1. **Algorithmic complexity** - quadratic scans over user-scale data, nested
   loops with membership tests against lists, repeated sorting, unnecessary
   full-collection copies, wrong data structure (list where set/dict is needed).
2. **Repeated work** - re-parsing configuration, recompiling regexes or schemas,
   re-reading files, re-establishing connections, recomputing pure functions
   with the same inputs, per-call initialisation that belongs at module or
   process scope.
3. **I/O patterns** - N+1 queries, missing batching, sequential network calls
   that could be concurrent, chatty filesystem access, missing pagination,
   fetching more columns/fields than used.
4. **Concurrency** - serial work that is safely parallelisable, unbounded
   concurrency causing thrash, lock contention, holding locks across I/O,
   blocking calls on an async event loop.
5. **Memory and allocation** - large object copies, unnecessary
   materialisation of iterators/generators into lists, string concatenation in
   loops, buffers reallocated per iteration, leaks and unbounded caches.
6. **Caching opportunities** - but only with an explicit lifecycle: what is
   cached, keyed on what, invalidated when, bounded how, and what happens on a
   stale hit.
7. **Cold start and initialisation** - heavy imports, eager loading, expensive
   module-level work, schema compilation at import time.
8. **Miscellaneous** - catastrophic regex backtracking, logging (especially
   string formatting) on hot paths, retries without backoff, redundant
   serialisation round-trips, debug instrumentation left enabled.

---

## Step 3 - Quantify the scaling

State the cost in terms the maintainer can check:

- **Complexity:** "O(n·m) where n = number of rules (user-configurable, commonly
  10-200) and m = number of events per batch".
- **Frequency:** "called once per HTTP request from `handler.py:88`".
- **Magnitude:** measured, or explicitly labelled as an estimate with the
  arithmetic shown.

Never write "significant improvement" without a number or a stated range and the
assumptions behind it.

---

## Step 4 - Design the benchmark

| Element | Required content |
|---|---|
| **Scenario** | Representative data size, invocation pattern, concurrency level, platform, and configuration. Justify why it is representative. |
| **Baseline** | Current default-branch behaviour and the exact command to reproduce it. |
| **Measurements** | Median plus p95 (or throughput) as appropriate; add CPU, memory, allocations, I/O, or query count where the finding is about those. |
| **Comparison** | Current `main` vs proposed approach, plus correctness edge cases and the invalidation or fallback path. |
| **Success criterion** | A threshold justified by the project's own context - not an arbitrary universal percentage. |
| **Correctness guard** | Tests proving identical output, unchanged public API behaviour, and no leak or race regression. |

Prefer the project's **existing** benchmark harness. If none exists, propose one
in the project's idiom (`pytest-benchmark`, `go test -bench`, `criterion`,
`benchmark.js`, `hyperfine` for CLI) and note that adding a harness may itself
need maintainer buy-in.

Record the plan in `evidence/benchmark-plan.md`. If you ran a measurement,
record the command and output in `evidence/commands-run.md` and tag `[TEST]`.
Measurements taken on a laptop are noisy - say so, report medians over repeated
runs, and do not over-claim.

---

## Step 5 - Trade-off analysis

Every optimisation costs something. Name it:

- readability and maintenance burden;
- memory for speed (caches, precomputed tables, memoisation);
- correctness risk (staleness, invalidation bugs, ordering changes, concurrency
  hazards);
- behavioural changes (error timing, lazy vs eager failures, log output);
- API or compatibility impact;
- platform or version dependence (a new stdlib API, a new dependency).

If the trade-off analysis is short, you have not thought about it hard enough.

---

## Rejection criteria

Reject when:

- no realistic benchmark or profile can be created;
- the code is not on a meaningful path;
- the likely gain is negligible relative to the added complexity;
- the change introduces caching without a safe invalidation story;
- the workload assumptions are artificial or unrepresentative;
- the project has explicitly chosen clarity or compatibility over this
  optimisation (check comments, docs, and prior rejected PRs);
- an active PR or newer branch already addresses the bottleneck;
- the "optimisation" is a micro-benchmark artefact that the compiler, JIT, or
  interpreter already handles.

**Micro-optimisation test:** if the change would not be noticeable in the
project's own benchmarks or in a user-visible metric, it is not a contribution
worth a maintainer's review time.

---

## Output

One candidate file per finding, `PERF-nnn.md`, using
`templates/performance-finding.md`, plus a benchmark plan section in
`evidence/benchmark-plan.md`.

Include the full proof chain, the scaling explanation, the benchmark design, the
trade-offs, the minimum PR scope, and the explicit exclusions - performance PRs
attract scope creep more than any other kind, so the exclusion list matters.
