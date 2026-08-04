# Evidence Classification

Every material claim in every discovery document carries an evidence tag. The
tag states *how you know*, so a human reviewer can audit the claim without
re-deriving it.

---

## Tags

| Tag | Meaning | Minimum requirement to use it |
|---|---|---|
| `[CODE]` | Directly verified in source. | You read the file in this run and cite `path:line` or `path:start-end`. |
| `[TEST]` | Reproduced through a test, benchmark, or command. | You ran the command in this run; its invocation and relevant output are recorded in `evidence/commands-run.md`. |
| `[HISTORY]` | Supported by commit or pull-request history. | You cite a commit SHA (short form acceptable) or a PR number you verified exists. |
| `[MAINTAINER]` | Supported by a maintainer statement. | You quote the statement and cite where it appears (issue/PR/discussion number, file, or release note). |
| `[DOCS]` | Supported by project documentation. | You cite the document and section. |
| `[INFERENCE]` | Reasoned conclusion that is not directly stated anywhere. | The reasoning is written out, not merely asserted. |
| `[UNVERIFIED]` | Believed but not yet checked; needs validation. | The document says what would verify it. |

---

## Rules

1. **One tag per claim, at the strongest level you can actually support.**
   Not the strongest level that would be convenient.
2. **Never upgrade.** If you inferred that a code path is reachable from network
   input but did not trace it, it is `[INFERENCE]`, not `[CODE]`.
3. **Line numbers are facts.** Cite only lines you read in this run. If the file
   changed since you read it, re-read it. Never approximate a line number.
4. **`[TEST]` is earned, not assumed.** "The test suite would show this" is
   `[INFERENCE]`. "I ran `pytest tests/test_parser.py -k cache` and it failed
   with X" is `[TEST]`.
5. **`[MAINTAINER]` needs attribution.** Confirm the person is actually a
   maintainer (commit history, `CODEOWNERS`, org membership, `MAINTAINERS` file)
   before using this tag; otherwise it is a user statement - tag it `[DOCS]`
   with a note, or `[INFERENCE]`.
6. **Absence of evidence is a finding.** "No issue found matching X across N
   query variants" is a legitimate, useful `[UNVERIFIED]`-adjacent statement -
   record the queries, not just the conclusion.

---

## Consequences for candidate disposition

Evidence quality gates what a candidate is allowed to become:

| Core claim strength | Maximum disposition |
|---|---|
| Impact and reachability are `[CODE]` + `[TEST]` | `SHORTLIST` |
| `[CODE]` only, with stated environmental assumptions | `SHORTLIST` if assumptions are modest and named; otherwise `NEEDS_MAINTAINER_INPUT` |
| Core claim rests on `[INFERENCE]` | `HOLD` or `NEEDS_MAINTAINER_INPUT` |
| Core claim rests on `[UNVERIFIED]` | `HOLD` at best; usually `REJECT` |

The "core claim" is whichever statement, if false, makes the candidate
worthless - typically reachability for security, path importance for
performance, and demand for features.

---

## Worked examples

Weak, and why:

```text
The config parser is called on every request, so caching it will speed things up.
```
No tag, no location, two unproven assertions, no measurement.

Strong:

```text
[CODE] `Config.load()` is invoked per request from `server/handler.py:88`,
       inside `handle()` rather than at startup.
[CODE] `Config.load()` re-reads and re-parses `config.yaml` on every call -
       `config/loader.py:41-67`; there is no memoisation on the path.
[TEST] `python -m pytest tests/bench/test_config.py -k load --durations=5`
       reports a median 4.1 ms per `load()` call on the sample config
       (command and output in evidence/commands-run.md).
[HISTORY] Introduced in `a1b2c3d` (2019-04-11) when config was loaded once per
       process; the per-request call site arrived later in `d4e5f6a`.
[INFERENCE] At the project's documented 500 req/s target this is roughly 2 s of
       CPU per wall-clock second across workers - assumes uniform config size,
       unverified against production data.
[UNVERIFIED] Whether hot-reload semantics are relied upon by any consumer;
       resolve by asking maintainers or grepping downstream usage.
```

The second version can be audited, argued with, and defended in a PR
description. The first cannot.

---

## Where evidence lives

| Artefact | Contents |
|---|---|
| `evidence/commands-run.md` | Every command executed, in order, with purpose, exit status, and relevant output excerpt. |
| `evidence/source-locations.json` | Machine-readable list of every cited `file:line` with the claim it supports. |
| `evidence/github-searches.json` | Every remote query run, with result counts and the tool used. |
| `evidence/benchmark-plan.md` | Benchmark scenarios, baselines, thresholds, and correctness guards. |
| `evidence/unresolved-questions.md` | Open questions, who could answer them, and what each blocks. |

A claim in a candidate document that is not traceable to one of these is not
finished.
