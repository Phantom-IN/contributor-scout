<!--
TEMPLATE: 01-architecture-and-context.md  (Phase 1)
See references/repository-comprehension.md. Facts only - no recommendations.
-->

# Architecture and Context: <owner/name>

| Field | Value |
|---|---|
| Analysed at commit | `<short SHA>` on `<branch>` |
| Generated | `<YYYY-MM-DD>` |
| Depth | <full / focused on: modules X, Y, Z> |

## Purpose and users

- **What it does:** <one paragraph> `[DOCS]`
- **Who depends on it:** <end users, library consumers, operators, CI, other projects>
- **Load-bearing behaviours:** <what users would notice immediately if broken>
- **Explicit non-goals:** "<quote>" `[DOCS]`

## Module map

| Module | Responsibility | Entry from | Depends on | Notes |
|---|---|---|---|---|
| `<dir>` | <what it owns> | <caller> | <internal/external deps> | |

## Entry points

| Entry point | Type | Location | Notes |
|---|---|---|---|
| `<name>` | CLI / HTTP / library export / worker / plugin loader | `path:line` | `[CODE]` |

## Data flows

Traced end to end, with verified locations.

### Flow 1: <name>

```text
<input source>  ->  path:line
    ->  path:line   <transformation>
    ->  path:line   <decision or validation>
    ->  path:line   <sink or output>
```

<One paragraph on what this flow means and where it can go wrong.> `[CODE]`

### Flow 2: <name>

<As above.>

## Trust boundaries

| Boundary | Input source | Trust assumed | Validation present | Privilege after crossing | Location |
|---|---|---|---|---|---|
| <name> | <network / file / env / config / plugin> | trusted / untrusted | <what runs> | <privileges> | `path:line` |

## External systems and dependencies

| System / dependency | Purpose | Where used | Risk notes |
|---|---|---|---|

## Public interfaces and stability

| Surface | Stability signal | Location | Notes |
|---|---|---|---|
| <exported API / route / CLI flag / config key> | public / internal / experimental | `path:line` | <how stability is signalled> |

- **Versioning policy:** <SemVer? deprecation window?> `[DOCS]`
- **How internal code is marked:** <`_private`, `internal/`, `@unstable`>

## Authentication, authorisation, and storage

- **Authentication:** <where identity is established> `path:line`
- **Authorisation:** <where permission is checked> `path:line`
- **Storage:** <schemas, migrations, serialisation formats, on-disk layout>
- **Secrets handling:** <where credentials enter and how they are stored>

## Extension points

| Extension point | Mechanism | Location | Notes |
|---|---|---|---|
| <plugins / hooks / middleware / adapters> | <mechanism> | `path:line` | <a good place to add features without touching core> |

## Critical paths

| Path | Why it matters | Location | Evidence |
|---|---|---|---|
| <name> | runs per request / handles untrusted input / scales with user data | `path:line` | `[CODE]` / `[HISTORY]` |

Churn analysis (last 12 months):

| File | Commits | Interpretation |
|---|---|---|

## Test architecture

- **Framework:** <name> `[CODE]`
- **Layout:** <unit / integration / e2e directories>
- **How to run:** `<command>` - runtime `<duration>` - <requires network? services?>
- **Coverage of critical paths:** <observed, with examples>
- **Fixture and mocking conventions:** <pattern>
- **Benchmark harness:** <name and location, or "none">

## Build and release process

- **Build:** `<command>` -> `<artefacts>`
- **CI:** <workflows, which gate merges, matrix breadth>
- **Release:** <how versions are cut, changelog discipline, deprecation policy>

## Coding conventions

| Aspect | Convention | Evidence |
|---|---|---|
| Naming and layout | | `[CODE]` |
| Error handling | | `[CODE]` |
| Logging | | `[CODE]` |
| Tests | | `[CODE]` |
| Docstrings / comments | | `[CODE]` |
| Commit messages | | `[HISTORY]` |
| PR titles | | `[HISTORY]` |

## Known limitations

| Limitation | Source | Location |
|---|---|---|
| <limitation> | `TODO` / docs / issue / maintainer comment | `path:line` or #<n> |

## Historical design decisions

| Decision | When | Rationale | Source |
|---|---|---|---|
| <decision> | `<sha>` / `<release>` | <why> | `[HISTORY]` / `[DOCS]` |

## Coverage and gaps

**Read in depth:** <files and directories>
**Sampled:** <directories skimmed>
**Not examined:** <directories not opened, and why>

<Later reviewers must know the boundaries of this map. Under-claiming here is
better than implying completeness.>
