# Final Recommendation: example-org/fluxconf

> **FICTIONAL EXAMPLE.** `example-org/fluxconf` is an invented repository. Every
> figure, path, commit SHA, and issue number below is fabricated to demonstrate
> the expected report style. Nothing here is a claim about any real project.

| Field | Value |
|---|---|
| Repository | `example-org/fluxconf` |
| Analysed at commit | `9f3a1c2` on `main` (2026-07-24) |
| Generated | 2026-07-29 |
| Mode | `full` |
| Duplicate-detection confidence | HIGH |
| Eligibility decision | PROCEED |

---

## Recommendation

> **Primary candidate: `PERF-001` - Schema is recompiled on every `validate()` call**
> Score 90/100 (Excellent contribution candidate) · Disposition SHORTLIST
> Recommended action: **discuss first, then implement**

Comment on issue #412 with the benchmark baseline and the proposed scope, ask
the one open design question, and implement once a maintainer replies. The
question changes the diff, so implementing first risks rework.

---

## Why this candidate is strongest

| Dimension | Assessment |
|---|---|
| Evidence | Reproduced with the project's own benchmark harness: 4.13 ms median, 3.9 ms of it compilation `[TEST]` |
| Impact | Every request in the server integration pays the cost; ~1.95 CPU-seconds per wall-clock second at the documented throughput target |
| Maintainer alignment | A maintainer already suggested compilation caching on #412 `[MAINTAINER]`; `ROADMAP.md` names "reload performance" as the current theme `[DOCS]` |
| Non-duplication | CLEAR at HIGH confidence - 12 query variants across issues, PRs (including drafts), discussions, and recent commits |
| Scope | 3 files, ~60 lines including tests; reuses an existing cache boundary rather than adding a mechanism |
| Risk | One unresolved question about in-place schema mutation; asked directly in the pitch, and it only narrows the scope rather than invalidating the finding |

**Compared with the alternatives:** `FEAT-001` has genuine Tier 1 demand but
needs a design decision from maintainers before any code can be written, so it
cannot start today. `SEC-001` is real but routes to private disclosure, which is
a different workflow with a different timeline. `PERF-001` is the only candidate
that is measurable now, aligned now, and reviewable as a small diff.

---

## Evidence summary

| Claim | Tag | Source |
|---|---|---|
| Compilation happens inside `validate()` | `[CODE]` | `fluxconf/validation/validator.py:52` |
| `validate()` runs once per request | `[CODE]` | `fluxconf/server/handler.py:88` |
| 3.9 ms of a 4.13 ms median call is compilation | `[TEST]` | `python -m pytest benchmarks/bench_validation.py --benchmark-only` |
| Introduced when the validator ran once per process | `[HISTORY]` | `a1b2c3d`, PR #87 |
| A maintainer suggested compilation caching | `[MAINTAINER]` | issue #412 |

**Reproduction / benchmark:** `candidates/PERF-001.md`, "Benchmark design";
scenarios in `evidence/benchmark-plan.md`.

**Unresolved:** whether the `fluxconf edit` workflow relies on in-place schema
mutation - `[UNVERIFIED]`, question 1 in `evidence/unresolved-questions.md`.

---

## Maintainer pitch

> **Problem.** `validate()` recompiles the schema on every call; on your own
> benchmark fixture that is 3.9 ms of a 4.1 ms call.
> **Where.** `fluxconf/validation/validator.py:52`, reached once per request from
> `fluxconf/server/handler.py:88`.
> **Why it is like this.** When validation was added in #87 the validator was
> built once per process and used once, so compiling inside `validate()` was
> free - the PR explicitly deferred caching until there was a long-running
> consumer.
> **What changed.** The server integration made `validate()` a per-request call,
> and v2.1 introduced the `cache/lifecycle.py` boundary that deferral was
> waiting for.
> **Proposal.** Route compilation through the existing cache boundary, keyed by
> schema content hash. No public API change.
> **Not included.** No compiler internals, no new cache backend, no unrelated
> cleanup.
> **Compatibility.** None, unless in-place schema mutation with an unchanged
> content hash is supported.
> **Question.** Does `fluxconf edit` rely on a mutated schema object taking
> effect without a content change? If so, I will scope the cache to the server
> path only.

Adapt this before posting. It is a draft for a human, not a message to send
verbatim.

---

## Implementation prerequisites

- [ ] Independently reproduce the benchmark on `main` at `9f3a1c2`.
- [ ] Re-run duplicate detection - issues, PRs (including drafts), and commits since 2026-07-29.
- [ ] Pull the latest `main` and confirm `validator.py:52` still compiles per call.
- [ ] Confirm `python -m pytest` and the benchmark suite run locally.
- [ ] Read `CONTRIBUTING.md` in full; note the DCO sign-off requirement (`git commit -s`).
- [ ] Post the benchmark numbers and the design question on issue #412; wait for a maintainer reply.
- [ ] Confirm you can explain the root cause, the fix, the alternatives, and the invalidation risk without referring to this document.

---

## Scope boundaries

**In scope**

- Route `compile_schema()` through `cache/lifecycle.py` at `validator.py:52`.
- Add the cache key derivation.
- Add three regression tests and one benchmark case.
- Add a changelog entry under `## Unreleased / Performance`.

**Explicitly out of scope**

- Compiler internals and the tree-walk algorithm.
- The `$ref` ordering issue noticed at `compiler.py:110`.
- New cache backends, configuration keys, or eviction policies.
- Typing, formatting, or lint cleanup in the touched files.
- Any change to the server integration.

**Expected diff size:** 3 files, roughly 60 lines.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Per-call compilation turns out to be deliberate for `fluxconf edit` | Medium | Rework - the cache must be scoped to the server path | Ask on #412 before implementing |
| Benchmark gain is smaller on the maintainer's platform | Low | The 1 ms criterion is missed | Reproduce on Linux and report both numbers |
| An overlapping PR appears | Low | Duplicate work | Re-check immediately before starting |
| Reviewer asks for the `$ref` fix in the same PR | Low | Scope creep | The exclusions list is in the pitch; offer a follow-up PR |

---

## Next action

Comment on issue #412 with the benchmark baseline, the root cause at
`validator.py:52`, the proposed minimum scope, the explicit exclusions, and the
`fluxconf edit` question. Do not open a PR until a maintainer answers.

---

## Alternatives considered (shortlist)

### 2. `FEAT-001` - Structured reload events for observability

- **Score:** 68/100 (Discuss with maintainers before implementation) · **Disposition:** NEEDS_MAINTAINER_INPUT
- **Why not primary:** Tier 1 demand (`ROADMAP.md` names observability; issue #388 is labelled `help wanted` with 14 reactions), but the event schema is a public API commitment and the roadmap entry does not specify a shape. Implementing before that decision risks a rejected design.
- **When it would become primary:** once a maintainer confirms the event shape on #388.
- **Details:** `candidates/FEAT-001.md`

### 3. `SEC-001` - Reload endpoint accepts unauthenticated requests when `bind_host` is overridden

- **Score:** 34/100 (Do not pursue *as a public contribution*) · **Disposition:** PRIVATE_DISCLOSURE
- **Why not primary:** the low score reflects public-contribution suitability, not severity. A public PR would disclose the issue before users can patch.
- **When it would become primary:** never, as a public PR. It becomes the top *action* if maintainers ask for a coordinated patch after private disclosure.
- **Details:** `candidates/SEC-001.md` - handle privately

---

## Security handling

| ID | Severity band | Route | Channel |
|---|---|---|---|
| `SEC-001` | High | `PRIVATE_DISCLOSURE` | `security@fluxconf.example.org` (5-day acknowledgement target); GitHub private vulnerability reporting also enabled |

> `contribution-discovery/` contains sensitive security material. Do not commit
> it to a public repository, and do not paste candidate contents into a public
> issue. Details are deliberately omitted from this summary - see
> `candidates/SEC-001.md`.

---

## Rejected candidates

| ID | Title | Reason | Reconsider if |
|---|---|---|---|
| `REJECTED-001` | Cache environment variable lookups | Path importance not established - the lookup runs once at startup | The lookup moves onto a per-request path |
| `REJECTED-002` | Suspected path traversal in the template loader | Not reachable - names are allowlisted at `registry.py:29-44` | `load()` gains a caller that bypasses `resolve()` |
| `REJECTED-003` | Add a plugin marketplace command | Conflicts with a documented non-goal | Maintainers revise the stated scope |

Full records: `candidates/REJECTED-*.md`

---

## Run limitations

| Limitation | Effect |
|---|---|
| Windows code paths could not be exercised | Findings in `fluxconf/platform/win32.py` remain `[INFERENCE]`; none were shortlisted |
| Benchmarks were run on macOS arm64 only | The magnitude claim needs confirmation on Linux CI before being quoted to maintainers |
| The Rust extension in `fluxconf/_native/` was read but not built | No performance review of the parser fast path |

---

## Human approval gate

This document is **not** authorisation to implement. Before any code is written:

1. A human reproduces the evidence independently.
2. A human re-checks current issues, PRs, and default-branch commits.
3. A human decides the route: implement, discuss, disclose privately, hold, or drop.
4. Only then does a separate implementation workflow begin.
5. Every generated line of code is reviewed by a human before submission.
