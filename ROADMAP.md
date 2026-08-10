# Roadmap

Where Contributor Scout is going, what will never change on the way, and how to
influence it. Delivery-level detail (exit criteria, success metrics, pilot
operations) lives in [docs/implementation-roadmap.md](docs/implementation-roadmap.md);
this document is the direction.

---

## North star

**Make "scouted by Contributor Scout" mean something to a maintainer.**

AI assistants have made it trivially cheap to open a pull request, and
maintainers are drowning in the result: duplicate work, unmeasured
optimisations, false vulnerability reports, speculative features. The scarce
resource in open source is no longer code — it is *justified confidence that a
change is worth reviewing*.

Contributor Scout exists to produce that confidence before a single line is
written. The end state we are building toward:

- A contributor runs discovery, gets one defensible candidate (or a
  well-argued "nothing meets the threshold"), and ships a focused PR that cites
  its evidence.
- A maintainer who sees that dossier-backed PR knows the duplicate check, the
  history trace, and the measurement actually happened — and reviews it
  faster, not slower, because of the AI involvement.
- The project can prove this works, with a public registry of real maintainer
  outcomes — acceptances *and* rejections — rather than with adjectives.

The measure of success is not findings produced, stars, or installs. It is the
**maintainer acceptance rate of scouted contributions**, published openly,
including when the numbers are unflattering.

---

## Principles that will not change

These are constitutional. Pull requests that violate them will be declined
regardless of how useful the feature is; changes here require the explicit,
deliberate agreement of the maintainers.

1. **Discovery only.** The skill writes reports, never code, and never writes
   to GitHub. Implementation is a separate, human-authorised workflow.
2. **Rewarded for rejecting.** A run that concludes "no contribution currently
   meets the threshold" is a successful run. Every rejection records the
   condition that would revive it.
3. **Evidence over fluency.** Every material claim carries an evidence tag; a
   candidate whose core impact claim is `[INFERENCE]` or `[UNVERIFIED]` cannot
   be shortlisted.
4. **The script owns the arithmetic.** Scoring weights, gates, and bands stay
   deterministic and reviewable. The model supplies judgement, never the maths.
5. **Never a spam engine.** No feature will be added whose purpose is opening
   more pull requests with less human understanding — bulk repository
   scanning for mass contribution, auto-submitted PRs and issues, or
   "contribution farming" of any kind. Tools that make low-effort
   contributions cheaper make open source worse; we would rather stay small.
6. **Standard-library-only scripts, opt-in everything.** No runtime
   dependencies, no telemetry without explicit opt-in, no integration that
   runs without the user seeing it.

---

## Theme 1 — Proof and reputation

*The project's credibility should rest on verified outcomes, not claims.*

| Milestone | Status |
|---|---|
| Public outcome registry ([SHOWCASE.md](SHOWCASE.md)) — merged, discussed, redirected, and declined outcomes, with links | **This release** |
| Outcome-report issue form feeding the registry | **This release** |
| Published acceptance-rate metric in the README once ≥ 10 outcomes are recorded — including the unflattering breakdown | Next |
| Evaluation dataset linking anonymised dossiers to maintainer outcomes — the only honest way to measure whether discovery works | Planned (V4) |
| Rating-anchor calibration from recorded outcomes: when maintainers consistently reject a class of candidate the rubric scored highly, the anchors change | Planned (V2/V3) |
| Case studies: full dossier → PR → review-thread walkthroughs for a handful of representative outcomes | Planned |

**Why this is first.** Every other roadmap item can be faked with good writing;
this one cannot. A registry with three honest entries beats a landing page —
and the rejected entries are what make the accepted ones believable.

---

## Theme 2 — Token and cost efficiency

*A full run is expensive. It should cost what the evidence requires and not a
token more.*

| Milestone | Status |
|---|---|
| Published cost baseline: measured token/turn cost per mode (`profile`, category modes, `full`) on reference repositories, in the docs | Next |
| Phase-budget audit: what each phase actually loads, and which references are loaded but unused — progressive disclosure already exists (references load per phase); make it measurably tight | Next |
| Reusable repository profile: `profile` output cached and reused by later category runs instead of re-deriving Phases 0–1 | Next |
| Cheap-model routing for mechanical stages: metadata collection, query fan-out, and schema validation do not need the strongest model; adversarial validation does | Planned |
| Shared evidence store between reviewer agents, so three reviewers stop independently re-reading the same files | Planned |
| `refresh` as true increment: diff remote state since the recorded analysis date rather than re-searching from scratch | Planned (V2) |
| Cost guard: a per-run budget the orchestrator respects, degrading scope explicitly (and recording it in review-coverage) instead of overrunning silently | Planned |

**Design constraint.** Efficiency never silently narrows coverage: any scope a
budget removes must appear in `03-review-coverage.md` as unreviewed ground.
Cheaper and *quieter about what was skipped* is not an acceptable trade.

---

## Theme 3 — Validation depth

*The adversarial layer is the product. Deepen it.*

- Independent adversarial validator agent — falsification fully separated from
  scoring, with its own instruction set (currently a phase of the ranker).
- Candidate-specific duplicate-query generation derived from the candidate's
  own terminology, replacing per-run brainstorming.
- Persistent rejected-findings store, so a later run recognises an idea it has
  already rejected instead of rediscovering and re-litigating it.
- Stale-candidate detection: diff current remote state against the state
  recorded at generation time; flag what moved.
- Schema-versioned reports with automated migration, keeping historical runs
  comparable as the contract evolves.

---

## Theme 4 — Ecosystem depth

*Generic playbooks miss language-specific classes. Grow them — from observed
failures only.*

- Language-specific security and performance playbooks (Python, TypeScript,
  Go, Rust, Java), each anchored to documented ecosystem failure classes.
- Optional, approval-gated integrations: Semgrep, CodeQL, language profilers,
  benchmark harnesses — always suggestions into the evidence chain, never
  unreviewed verdicts.
- Framework and build-system heuristics: Django, FastAPI, Express, Next.js,
  Spring, Bazel, Cargo workspaces.

---

## Theme 5 — Distribution and hosts

*Meet contributors where they already work.*

| Milestone | Status |
|---|---|
| Claude Code plugin-marketplace install (`/plugin marketplace add Phantom-IN/contributor-scout`) | **This release** |
| Four supported hosts (Claude Code, GitHub Copilot, Cursor, Antigravity) with a drift-checked shared payload | Shipped (V1.1) |
| Published, versioned JSON Schemas for the machine-readable reports | Planned (V4) |
| Non-GitHub forges: GitLab, Codeberg, Gitea duplicate detection and metadata (`glab`, forge REST APIs) | Planned (V4) |
| Further hosts as their extension formats stabilise — the four-tree layout is designed to take a fifth | Open to contributions |

---

## Version map

How the themes land as releases (detail per version:
[docs/implementation-roadmap.md](docs/implementation-roadmap.md)):

| Version | Contents | Status |
|---|---|---|
| V1 | Core orchestrator, playbooks, scoring, validation, safety model | Shipped |
| V1.1 | Copilot, Cursor, Antigravity hosts; unified hook; drift check | Shipped |
| **V1.2** | **Open-source launch: marketplace packaging, CI, community guidelines, outcome registry** | **This release** |
| V2 | Validation depth (Theme 3) + first calibration + refresh hardening | Planned |
| V3 | Ecosystem depth (Theme 4) + cost-efficiency work (Theme 2) landing across both | Planned |
| V4 | Evaluation dataset, published schemas, non-GitHub forges | Planned |

Themes 1 and 2 are not single releases — outcome collection starts now and
compounds, and every version is expected to lower or hold per-run cost, never
raise it silently.

---

## How to influence this roadmap

Priority follows evidence, in this order:

1. **Recorded failures** — a [run-failure report](CONTRIBUTING.md#what-to-contribute)
   showing the system got something wrong outranks everything else.
2. **Recorded outcomes** — [SHOWCASE.md](SHOWCASE.md) entries showing what
   maintainers actually accepted or declined.
3. **Repeated requests** from real runs (several people hitting the same wall).
4. Everything else, including the maintainer's own preferences.

Propose roadmap changes as an issue using the feature-request form — which
will ask you for the evidence. This document is updated when direction
actually changes, not on a schedule; the Git history of this file is the
project's decision log.
