# REJECTED-002: Suspected path traversal in the template loader

> **FICTIONAL EXAMPLE.** `example-org/fluxconf` is an invented repository. Every
> path, line number, commit SHA, and issue number below is fabricated to
> demonstrate how a candidate should be rejected and recorded. Nothing here is a
> claim about any real project.

| Field | Value |
|---|---|
| Original ID | `SEC-002` |
| Category | `security` |
| Disposition | REJECT |
| Rejected on | 2026-07-29 |
| Analysed at commit | `9f3a1c2` |
| Score | 22/100 - band Do not pursue |

## What was proposed

`TemplateLoader.load()` joins a user-supplied template name onto the template
root with `os.path.join()` without an explicit containment check, which looked
like a path-traversal sink allowing arbitrary file reads via
`../../etc/passwd`-style input.

## Where

| Location | Role |
|---|---|
| `fluxconf/templates/loader.py:73` | the suspected sink - `os.path.join(self.root, name)` |
| `fluxconf/templates/loader.py:61-70` | the caller that supplies `name` |
| `fluxconf/templates/registry.py:29-44` | the guard that was initially missed |

## Primary rejection reason

> **Not reachable - input is validated upstream**

The template name never reaches `loader.py:73` unvalidated. `TemplateRegistry.resolve()`
at `fluxconf/templates/registry.py:29-44` rejects any name that is not an exact
match against the registered template set before `load()` is called, and
`load()` is not part of the public API - it is imported only by `registry.py`
(`grep -rn "from .loader import"` returns a single call site). The traversal
string cannot survive the allowlist, so no attacker-controlled input reaches the
join.

A second, independent reason: the project's documented threat model states that
"template roots are operator-controlled and trusted", so even a bypass would
target a boundary the project explicitly does not defend.

## Falsifying evidence

| Evidence | Tag | Source |
|---|---|---|
| `resolve()` allowlists template names against the registered set before calling `load()` | `[CODE]` | `fluxconf/templates/registry.py:29-44` |
| `load()` has exactly one caller, inside `registry.py` | `[CODE]` | `grep -rn "loader import\|loader\.load" fluxconf/` - output in `evidence/commands-run.md` |
| Template roots are documented as trusted | `[DOCS]` | `docs/security-model.md`, "Trust assumptions" section |
| A traversal attempt raises `UnknownTemplateError` before reaching the join | `[TEST]` | `python -m pytest tests/test_registry.py -k traversal` - existing test at `tests/test_registry.py:118` already covers this |
| The guard was added deliberately in response to an earlier report | `[HISTORY]` | commit `c4d5e6f`, "registry: allowlist template names (#233)" |

## Duplicate status

- **Status:** REJECTED
- **Duplicate-detection confidence:** HIGH
- **Related work:** #233 - "harden template name handling" (closed, merged) added the very guard that makes this unreachable. Reporting it again would tell maintainers that their existing fix was not read.

## What was learned

Three things worth carrying into the rest of this run:

1. `fluxconf/templates/registry.py` is the enforcement boundary for the template
   subsystem - anything downstream of it can assume validated names. Future
   findings in `templates/` must start from `registry.py`, not from the sink.
2. `docs/security-model.md` contains an explicit trust-assumption list. It was
   not discovered until Phase 6, which is too late; it should be read in Phase 1
   on every future run.
3. The project responds to security reports by adding allowlists at the boundary
   rather than sanitising at the sink. A hardening proposal that sanitises at the
   sink would read as not understanding their design.

## Reconsider if

- `load()` is exported publicly or gains a second caller that bypasses `registry.resolve()`.
- The allowlist in `registry.py:29-44` is replaced with pattern matching rather than exact matching.
- `docs/security-model.md` is revised to treat template roots as untrusted.

## Effort spent

Roughly 40 minutes: attack-surface mapping of `templates/`, reachability tracing
from the sink backwards, and one test run. The reachability walk is what killed
it - the pattern match alone would have produced a false report.
