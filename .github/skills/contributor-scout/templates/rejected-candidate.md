<!--
TEMPLATE: candidates/REJECTED-nnn.md

Rejected findings are retained so the system does not rediscover the same weak
idea on a later run. Keep these short - a rejected candidate does not need the
full 28-section dossier. Record what it was, why it failed, and what would
change the answer.
-->

# REJECTED-<nnn>: <Candidate title>

| Field | Value |
|---|---|
| Original ID | `<SEC-00x / PERF-00x / FEAT-00x>` (if one was assigned) |
| Category | `security` / `performance` / `feature` |
| Disposition | REJECT |
| Rejected on | `<YYYY-MM-DD>` |
| Analysed at commit | `<short SHA>` |
| Score | `<nn>`/100 - band `<band>` (if scored) |

## What was proposed

<Two to three sentences describing the hypothesis, so a future run recognises it
immediately and does not repeat the work.>

## Where

| Location | Role |
|---|---|
| `path:line` | <what was examined> |

## Primary rejection reason

> **`<one of:>`** duplicate / already fixed / claimed by another contributor /
> previously rejected by maintainers / superseded / not reachable / no impact /
> path not important / no benchmark possible / out of stated scope / no demand
> evidence / scope too large / not testable / documented as intentional

<One paragraph explaining it, with the evidence that settled it.>

## Falsifying evidence

| Evidence | Tag | Source |
|---|---|---|
| <e.g. input is validated at `path:line` before reaching the sink> | `[CODE]` | `path:line` |
| <e.g. fixed in `<sha>`, unreleased> | `[HISTORY]` | `<sha>` |
| <e.g. maintainer: "this is intentional - config files are trusted"> | `[MAINTAINER]` | #<n> |
| <e.g. open PR #<n> covers the same path> | `[MAINTAINER]` | PR #<n> |

## Duplicate status

- **Status:** `DUPLICATE` / `CLAIMED` / `REJECTED` / `SUPERSEDED` / `RELATED` / `CLEAR` / `UNKNOWN`
- **Confidence:** `HIGH` / `MEDIUM` / `LOW`
- **Related work:** #<n> - <title> (<state>)

## What was learned

<Anything worth carrying forward: an architectural fact, a maintainer
preference, a trust assumption, a hot path that turned out to be cold. This is
often more valuable than the rejected candidate itself.>

## Reconsider if

The specific, observable conditions under which this becomes worth revisiting:

- <e.g. PR #<n> is closed without merging>
- <e.g. the project drops support for <platform>, removing the constraint>
- <e.g. a maintainer requests this capability>
- <e.g. the config-reload path is removed, making caching safe>

<If there is no realistic condition, write "Not reconsiderable - <reason>".>

## Effort spent

<Rough indication - helps calibrate future runs on where review time goes.>
