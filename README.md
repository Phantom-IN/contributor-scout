<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="Contributor Scout — evidence-first open-source contribution discovery for Claude Code, GitHub Copilot, Cursor and Antigravity" src="assets/banner-light.svg" width="100%">
</picture>

<br>

[![License](https://img.shields.io/badge/license-MIT-0969da?style=flat-square)](LICENSE)
[![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Copilot%20%C2%B7%20Cursor%20%C2%B7%20Antigravity-1a7f37?style=flat-square)](#supported-hosts)
[![Python](https://img.shields.io/badge/python-3.8%2B-3572a5?style=flat-square)](#requirements)
[![Dependencies](https://img.shields.io/badge/dependencies-0-1a7f37?style=flat-square)](skills/contributor-scout/scripts/requirements.txt)
[![Mode](https://img.shields.io/badge/mode-discovery--only-bf8700?style=flat-square)](#safety-model)

**[Quick start](#quick-start)** · **[Hosts](#supported-hosts)** · **[Usage](#usage)** · **[What you get](#what-you-get)** · **[How it works](#how-it-works)** · **[Safety](#safety-model)** · **[Limitations](#limitations)**

</div>

---

Point Contributor Scout at a cloned open-source repository and it tells you what
is worth contributing — with source evidence, historical context, proof that
nobody else is already doing it, and a maintainer-facing argument for why the
change should happen.

**It writes reports. It never writes code.**

```text
   ┌─ raw hypotheses ─┐   ┌──── adversarial validation ────┐   ┌ result ─┐
   │  security  ● ● ● │   │ reachable?      already taken? │   │         │
   │  perf      ● ●   │──▶│ measurable?     in scope?      │──▶│ 1 pick  │
   │  features  ● ● ● │   │ wanted?         why this code? │   │ + 2 alts│
   └──────────────────┘   └────────────────────────────────┘   └─────────┘
          8 ideas             most die here — on purpose            ▲
                                                                    │
   every rejection is written down with the condition that would ───┘
   revive it. "nothing currently meets the threshold" is a valid run.
```

<details>
<summary><b>Contents</b></summary>

- [Why it exists](#why-it-exists)
- [What it does not do](#what-it-does-not-do)
- [Core capabilities](#core-capabilities)
- [Supported hosts](#supported-hosts)
- [Quick start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [What you get](#what-you-get)
- [How it works](#how-it-works)
- [The human workflow](#the-human-workflow)
- [Safety model](#safety-model)
- [Limitations](#limitations)
- [Troubleshooting](#troubleshooting)
- [Project structure](#project-structure)
- [Contributing](#contributing)
- [Roadmap](#roadmap)

</details>

---

## Why it exists

Writing the code is the easy part of an open-source contribution. The hard part
is deciding *what* to contribute: something technically valid, valuable to
users, aligned with where the project is going, small enough to review, and not
already being worked on by someone else.

AI assistants generate patches quickly. Without disciplined discovery they also
generate duplicate work, false security reports, unmeasured optimisations, and
speculative features — all of which land on a maintainer's desk as unpaid work.

| Common failure | Why it happens | What it costs maintainers |
|---|---|---|
| Duplicate contribution | Only issue titles searched; drafts, discussions, synonyms, recent commits missed | Time reviewing work that already exists |
| False security finding | Dangerous-looking pattern reported without reachability or mitigation analysis | Noise, or an accidental public disclosure |
| Unmeasured optimisation | Code looks slow, but the path is cold or no benchmark exists | Complexity with no user benefit |
| Random feature proposal | Capability gap inferred without demand, roadmap alignment, or maintenance cost | Scope creep and permanent support burden |
| Historically naive fix | The change ignores why the original implementation was chosen | Reintroduces solved problems |
| Oversized first PR | Unrelated refactors bundled in | Slow review, likely rejection |

Contributor Scout is designed around one principle:

> **It should be rewarded for rejecting weak ideas, not for producing findings.**
> A successful run may conclude that no contribution currently meets the
> threshold.

**Who should use it:** engineers who want to contribute to a third-party
open-source project and would rather spend an hour proving one idea is right
than a day implementing three that are wrong.

---

## What it does not do

During discovery it will not:

- modify application source code, tests, or configuration;
- implement fixes or features;
- create branches, commits, or pushes;
- open issues, create pull requests, or post comments;
- publish vulnerability details;
- run destructive commands or untrusted scripts;
- install dependencies without your approval;
- write anywhere except `contribution-discovery/`.

It also will not guarantee maintainer acceptance, replace your responsibility to
understand and defend a contribution, or formally verify a repository.

---

## Core capabilities

**Security contribution discovery** — maps the attack surface, traces
attacker-controlled input to sensitive operations, builds a threat model,
verifies reachability, checks existing mitigations, and separates severity from
contribution suitability. Findings without a complete input-to-impact chain are
rejected, not reported.

**Performance contribution discovery** — establishes that a path matters
*before* looking for inefficiency, quantifies how the cost scales, designs a
benchmark against the project's own harness, and analyses the trade-offs. No
candidate is shortlisted without a credible measurement strategy.

**Feature discovery** — starts from citable demand: roadmap items, `help wanted`
issues, maintainer statements, documented limitations, repeated user requests.
Defines the smallest viable scope and an explicit non-goals list. AI-inferred
features default to "discuss first".

**Duplicate detection** — runs twice. A broad sweep before review, and a
candidate-specific sweep afterwards using the exact symptom, file path, function
name, error string, root cause, synonyms, and proposed solution wording. Every
query is recorded, including the ones that found nothing.

**Git-history tracing** — finds the introducing commit and, where verifiable,
the introducing pull request; recovers the original design constraints; and
identifies which assumptions have since changed. History is used as explanation,
never blame.

**Maintainer-alignment analysis** — reads contribution policies, stated
non-goals, rejected proposals, and review culture, then frames the proposal in
terms the project will recognise.

**Evidence-backed scoring** — ten weighted categories and seven risk deductions,
computed by a deterministic script that also enforces the duplicate-status
gates. The model supplies judgement; the script owns the arithmetic.

**Structured reports** — a fixed 28-section candidate contract, machine-readable
JSON alongside every Markdown document, and a validator that fails a report
missing impact, evidence, duplicate status, history, tests, confidence, or a
next action.

---

## Supported hosts

The same skill, the same six reviewers, the same reports — packaged four times,
because each host discovers extensions from a different path.

| Host | Skill | Reviewer agents | Slash command | Optional hook |
|---|---|---|---|---|
| **Claude Code** | `skills/contributor-scout/` | `agents/*.md` | `/contributor-scout` | `.claude/settings.json` |
| **GitHub Copilot** (VS Code) | `.github/skills/contributor-scout/` | `.github/agents/*.agent.md` | `/contributor-scout` | `.github/hooks/*.json` |
| **Cursor** | `.cursor/skills/contributor-scout/` | `.cursor/agents/*.md` | `/contributor-scout` | `.cursor/hooks.json` |
| **Antigravity** | `.agents/skills/contributor-scout/` | `.agents/agents/*.md` | `/contributor-scout` <sup>via workflow</sup> | `.agents/hooks.json` |

`skills/contributor-scout/` is the canonical tree. Inside every copy the
`references/`, `templates/` and `scripts/` directories are byte-identical —
[`tools/sync_hosts.py`](tools/sync_hosts.py) enforces that. Only the `SKILL.md`
frontmatter, three "where do the subagents live" sentences, and the agent
frontmatter differ per host.

Two host quirks worth knowing:

- **Cursor** also reads project skills from `.agents/skills/`, so on a machine
  that has both editors a single workspace copy can serve both. `.cursor/` wins
  on a name conflict.
- **Antigravity** additionally ships
  [`.agents/workflows/contributor-scout.md`](.agents/workflows/contributor-scout.md),
  which is what turns `/contributor-scout <mode>` into a real slash command
  there. Its bundled agents use `commandExecutionPolicy: auto` so read-only
  `git` and `gh` queries do not prompt on every call — see
  [Safety model](#safety-model) for what that trades away.

---

## Quick start

### Requirements

| Requirement | Needed for | Notes |
|---|---|---|
| One of the four hosts above | Everything | Any recent version |
| Python 3.8+ | The five helper scripts | Standard library only — nothing to `pip install` |
| `git` | History tracing, repository metadata | Already required to clone the target |
| `gh` (GitHub CLI) | Duplicate detection against the remote | **Optional but strongly recommended** — without it, duplicate status can never be better than `UNKNOWN` |

```bash
python3 --version   # 3.8 or later
git --version
gh --version        # optional
```

### 60 seconds to a first run

```bash
git clone https://github.com/Phantom-IN/contributor-scout.git
cd contributor-scout
```

Install for your host — the personal/user-scope install, so it works in every
project (full per-host detail is in [Installation](#installation)):

```bash
# Claude Code
mkdir -p ~/.claude/skills ~/.claude/agents
cp -R skills/contributor-scout ~/.claude/skills/ && cp agents/*.md ~/.claude/agents/

# Cursor
mkdir -p ~/.cursor/skills ~/.cursor/agents
cp -R .cursor/skills/contributor-scout ~/.cursor/skills/ && cp .cursor/agents/*.md ~/.cursor/agents/
```

Then open your assistant from the root of a **cloned third-party repository**
and say:

```text
Use the contributor-scout skill in profile mode.
Assess whether this repository is worth contributing to.
Do not modify source code.
```

That is the cheap run, and its answer may end the investigation — which is the
point.

---

## Installation

Pick your host. Every install ships the same behaviour; only the paths differ.

> [!WARNING]
> Do **not** run a project-local install inside a third-party repository you
> intend to contribute to — it adds untracked files to their tree. Use the
> personal install, or copy into a private fork.

<details>
<summary><b>Claude Code</b></summary>

<br>

**Option A — personal skill (recommended).** Available in every project on your
machine.

```bash
mkdir -p ~/.claude/skills ~/.claude/agents
cp -R skills/contributor-scout ~/.claude/skills/
cp agents/*.md ~/.claude/agents/
```

Verify:

```bash
ls ~/.claude/skills/contributor-scout/SKILL.md
ls ~/.claude/agents/ | grep -E 'security-reviewer|contribution-ranker'
```

Restart Claude Code, then run `/skills` (or ask "what skills are available?") to
confirm `contributor-scout` is listed.

**Option B — project-local.** Scoped to one repository; useful when you want the
skill checked in alongside a team's analysis conventions.

```bash
mkdir -p /path/to/target-repo/.claude/skills /path/to/target-repo/.claude/agents
cp -R skills/contributor-scout /path/to/target-repo/.claude/skills/
cp agents/*.md /path/to/target-repo/.claude/agents/
```

**Option C — plugin layout.** This repository is already shaped as a Claude Code
plugin: `.claude-plugin/plugin.json` plus top-level `skills/`, `agents/`, and
`hooks/`. If your Claude Code version supports local plugin installation, point
it at this directory. Otherwise use Option A — it is equivalent in effect.

</details>

<details>
<summary><b>GitHub Copilot (VS Code)</b></summary>

<br>

**Option A — personal skill.** Available in every workspace, via your VS Code
user profile.

```bash
mkdir -p ~/.copilot/skills
cp -R .github/skills/contributor-scout ~/.copilot/skills/
```

Custom agents are not currently supported at user-profile scope with the same
subagent-delegation behaviour as project scope, so for full functionality (the
six specialised reviewers), prefer Option B in the target repository.

Restart VS Code, then type `/` in the Copilot Chat view to confirm
`contributor-scout` is listed.

**Option B — project-local (recommended for full functionality).** Scoped to one
repository, including the six custom agents the skill delegates to.

```bash
mkdir -p /path/to/target-repo/.github/skills /path/to/target-repo/.github/agents
cp -R .github/skills/contributor-scout /path/to/target-repo/.github/skills/
cp .github/agents/*.agent.md /path/to/target-repo/.github/agents/
```

Verify:

```bash
ls /path/to/target-repo/.github/skills/contributor-scout/SKILL.md
ls /path/to/target-repo/.github/agents/ | grep -E 'security-reviewer|contribution-ranker'
```

Reload the window, then type `/` in Copilot Chat to confirm `contributor-scout`
is listed.

</details>

<details>
<summary><b>Cursor</b></summary>

<br>

**Option A — personal skill and subagents (recommended).** Available in every
workspace.

```bash
mkdir -p ~/.cursor/skills ~/.cursor/agents
cp -R .cursor/skills/contributor-scout ~/.cursor/skills/
cp .cursor/agents/*.md ~/.cursor/agents/
```

Verify:

```bash
ls ~/.cursor/skills/contributor-scout/SKILL.md
ls ~/.cursor/agents/ | grep -E 'security-reviewer|contribution-ranker'
```

Restart Cursor, then type `/` in Agent chat — `contributor-scout` appears in the
list, and so do the six reviewers (`/security-reviewer`, `/contribution-ranker`,
and the rest) for when you want to drive one directly.

**Option B — project-local.**

```bash
mkdir -p /path/to/target-repo/.cursor/skills /path/to/target-repo/.cursor/agents
cp -R .cursor/skills/contributor-scout /path/to/target-repo/.cursor/skills/
cp .cursor/agents/*.md /path/to/target-repo/.cursor/agents/
```

Cursor walks the skills root recursively, so a monorepo can scope the skill to
one package by installing under `apps/web/.cursor/skills/` instead.

> Cursor also reads project skills from `.agents/skills/`. If you already
> installed the Antigravity copy into a workspace, Cursor will find it — the
> `.cursor/` copy takes precedence when both exist.

</details>

<details>
<summary><b>Antigravity</b></summary>

<br>

**Option A — global skill and agents (recommended).** Available in every
workspace.

```bash
mkdir -p ~/.gemini/config/skills
cp -R .agents/skills/contributor-scout ~/.gemini/config/skills/

# Global agents live one directory deep, as <name>/agent.md
for f in .agents/agents/*.md; do
  name=$(basename "$f" .md)
  mkdir -p ~/.gemini/config/agents/"$name"
  cp "$f" ~/.gemini/config/agents/"$name"/agent.md
done
```

Verify:

```bash
ls ~/.gemini/config/skills/contributor-scout/SKILL.md
ls ~/.gemini/config/agents/
```

Reload the window. The skill activates by name or by context; run `/agents` to
see the six reviewers listed.

**Option B — workspace install (adds the slash command).** The
`/contributor-scout` workflow is workspace-scoped, so this is the option to use
if you want the slash command rather than natural-language activation.

```bash
mkdir -p /path/to/target-repo/.agents/{skills,agents,workflows}
cp -R .agents/skills/contributor-scout /path/to/target-repo/.agents/skills/
cp .agents/agents/*.md                 /path/to/target-repo/.agents/agents/
cp .agents/workflows/contributor-scout.md /path/to/target-repo/.agents/workflows/
```

Reload the window, then type `/contributor-scout profile` in the agent panel.

> The bundled agents set `commandExecutionPolicy: auto` so that read-only `git`
> and `gh` queries run without a confirmation on every call — which is what
> makes duplicate detection usable, and also what removes the per-command prompt
> the other three hosts give you. Installing the
> [discovery-guard hook](hooks/README.md) matters most on this host. To trade
> the other way, set `commandExecutionPolicy: sandbox` in the agent files and
> accept weaker duplicate detection.

</details>

<details>
<summary><b>GitHub CLI setup (optional, all hosts)</b></summary>

<br>

```bash
gh auth login          # follow the prompts
gh auth status         # confirm authentication
```

Without authentication the skill runs in **degraded mode**: duplicate status is
capped at `UNKNOWN`, duplicate-detection confidence is `LOW`, and the scoring
script caps the non-duplication rating at 2 out of 5.

</details>

<details>
<summary><b>Python setup and keeping output out of the target repo</b></summary>

<br>

No Python setup is required. Verify the scripts run:

```bash
python3 skills/contributor-scout/scripts/calculate_candidate_score.py --example
python3 skills/contributor-scout/scripts/validate_report_schema.py --list-required-sections
```

[`requirements.txt`](skills/contributor-scout/scripts/requirements.txt) exists to
document that there are deliberately no dependencies.

Keep discovery output out of the repository you are analysing:

```bash
git config --global core.excludesFile ~/.gitignore_global
echo 'contribution-discovery/' >> ~/.gitignore_global
```

The skill will not edit the target repository's `.gitignore` — that would be a
source modification.

</details>

---

## Usage

Open your assistant from the root of a cloned open-source repository. Invoke the
skill by slash command or in plain language — both work, because the mode is
just an argument.

| Mode | Phases | What it costs you | What you get |
|---|---|---|---|
| `profile` | 0–1 | Minutes | Viability decision, architecture map, dev commands |
| `full` | 0–8 | The expensive one | Everything, across all three categories |
| `security` | 0–2, 3a, 4–8 | Moderate | Attack surface, reachable findings, disclosure routing |
| `performance` | 0–2, 3b, 4–8 | Moderate | Hot paths, scaling analysis, benchmark plans |
| `features` | 0–2, 3c, 4–8 | Moderate | Demand-backed proposals with explicit non-goals |
| `validate <id>` | 4–7 | Small | One candidate, re-attacked and re-scored |
| `refresh` | 2, 5, 7–8 | Small | Updated duplicate status and ranking |

Default when no mode is given is `profile`. The skill never silently escalates
to `full`.

### 1. Always start with profile mode

```text
Use the contributor-scout skill in profile mode.
Assess whether this repository is worth contributing to.
Do not modify source code.
```

You get `PROCEED`, `PROCEED_WITH_LIMITATIONS`, or `DO_NOT_INVEST`, plus an
architecture map and the development commands.

### 2. Full discovery

```text
Use the contributor-scout skill in full mode.
Analyse security, performance, and feature contribution opportunities.
Generate all reports under contribution-discovery/.
Do not implement anything.
```

<details>
<summary><b>More prompt recipes</b></summary>

<br>

**Security-only review**

```text
Use the contributor-scout skill in security mode.
Map the attack surface and look for reachable vulnerabilities.
Follow the repository's SECURITY.md disclosure policy.
Do not open any issue or pull request, and do not include exploit code.
```

**Performance-only review**

```text
Use the contributor-scout skill in performance mode.
Focus on the request-handling path.
Every finding needs a benchmark plan and a scaling explanation.
Reject micro-optimisations.
```

**Feature-only review**

```text
Use the contributor-scout skill in features mode.
Only propose features with citable demand — roadmap items, help-wanted issues,
maintainer statements, or repeated user requests.
Define the minimum viable scope and explicit non-goals for each.
```

**Validate a single candidate**

```text
Use the contributor-scout skill to validate candidate PERF-001.
Try to disprove it: re-check reachability, re-run duplicate detection,
and re-score it.
```

**Refresh an older analysis** — run this immediately before you start
implementing. Issues and pull requests move.

```text
Use the contributor-scout skill in refresh mode.
Re-check issues, pull requests, and commits since the analysis date,
update duplicate status, and re-rank the candidates.
```

**Focus a large repository**

```text
Use the contributor-scout skill in performance mode,
scoped to src/parser/ and src/runtime/ only.
```

**Raise the bar**

```text
Only shortlist candidates with [TEST] evidence and a duplicate status of CLEAR.
```

</details>

---

## What you get

```text
contribution-discovery/
├── 00-repository-profile.md        eligibility decision, activity, policies, commands
├── 01-architecture-and-context.md  modules, data flows, trust boundaries, critical paths
├── 02-existing-work-map.md         issues, PRs, discussions, occupied vs open ground
├── 03-review-coverage.md           what was reviewed — and what was not
├── 04-candidate-scorecard.md       scores, deductions, blocking errors
├── 05-final-recommendation.md      one primary candidate, up to two alternatives
├── candidates/
│   ├── SEC-001.md
│   ├── PERF-001.md
│   ├── FEAT-001.md
│   └── REJECTED-001.md
├── evidence/
│   ├── commands-run.md
│   ├── source-locations.json
│   ├── github-searches.json
│   ├── benchmark-plan.md
│   └── unresolved-questions.md
└── machine-readable/
    ├── repository-profile.json
    ├── candidates.json
    └── final-ranking.json
```

Every material claim carries an evidence tag:

```text
[CODE]  [TEST]  [HISTORY]  [MAINTAINER]  [DOCS]  [INFERENCE]  [UNVERIFIED]
```

A claim you cannot support is `[INFERENCE]` or `[UNVERIFIED]` — and a candidate
whose *core impact claim* is either of those cannot be shortlisted at all.

### What a recommendation actually reads like

Trimmed from [`examples/sample-final-recommendation.md`](examples/sample-final-recommendation.md)
(a fictional repository):

> **Primary candidate: `PERF-001` — Schema is recompiled on every `validate()` call**
> Score 90/100 · Disposition SHORTLIST
> Recommended action: **discuss first, then implement**

| Claim | Tag | Source |
|---|---|---|
| Compilation happens inside `validate()` | `[CODE]` | `fluxconf/validation/validator.py:52` |
| `validate()` runs once per request | `[CODE]` | `fluxconf/server/handler.py:88` |
| 3.9 ms of a 4.13 ms median call is compilation | `[TEST]` | `pytest benchmarks/bench_validation.py --benchmark-only` |
| Introduced when the validator ran once per process | `[HISTORY]` | `a1b2c3d`, PR #87 |
| A maintainer suggested compilation caching | `[MAINTAINER]` | issue #412 |

> **Compared with the alternatives:** `FEAT-001` has genuine demand but needs a
> design decision from maintainers before any code can be written. `SEC-001` is
> real but routes to private disclosure. `PERF-001` is the only candidate that is
> measurable now, aligned now, and reviewable as a small diff.

Full worked output — including
[a rejection](examples/sample-rejected-candidate.md) — lives in
[examples/](examples/). Format contract and JSON schemas:
[docs/output-format.md](docs/output-format.md).

---

## How it works

```mermaid
flowchart TD
    U[Engineer in a cloned repository] --> ORC[Contributor Scout orchestrator]

    ORC --> RI[Repository Intelligence<br/>viability · architecture · critical paths]
    RI --> G0{Repository gate}
    G0 -->|DO_NOT_INVEST| STOP[Stop and report]
    G0 -->|PROCEED| EWM[Existing-work map<br/>issues · PRs · discussions · roadmap]

    EWM --> SEC[Security Reviewer]
    EWM --> PERF[Performance Reviewer]
    EWM --> FEAT[Feature Scout]

    SEC --> DHV[Duplicate and History Validator<br/>non-duplication · introducing commit]
    PERF --> DHV
    FEAT --> DHV

    DHV --> ADV[Adversarial validation<br/>try to disprove every candidate]
    ADV --> RANK[Contribution Ranker<br/>deterministic scoring · shortlist of 3]
    RANK --> REP[Discovery documents<br/>contribution-discovery/]
    REP --> HG{Human approval gate}

    HG -->|approved| IMPL[Separate implementation workflow]
    HG -->|not approved| BACK[Research more · discuss · disclose · hold · drop]

    subgraph SCRIPTS[Deterministic scripts]
        S1[collect_repo_metadata.py]
        S2[collect_git_history.py]
        S3[search_github_candidates.py]
        S4[calculate_candidate_score.py]
        S5[validate_report_schema.py]
    end

    RI -.-> S1
    EWM -.-> S3
    DHV -.-> S2
    DHV -.-> S3
    RANK -.-> S4
    REP -.-> S5
```

Three structural decisions do most of the work:

1. **Reviewers produce hypotheses, not recommendations.** A separate validation
   layer, with a different instruction — *find the reason a maintainer would
   close this* — tries to destroy them first. A reviewer that has spent an hour
   building a case is the worst possible judge of that case.
2. **Deterministic work lives in scripts.** The model supplies 0–5 ratings and
   risk flags; the script owns the weights, the gates, and the bands. Degraded
   modes become visible rather than being quietly routed around.
3. **Discovery and implementation never share a context.** The skill has no
   code-writing phase. It stops at a dossier.

Details in [docs/architecture.md](docs/architecture.md) and
[docs/workflow.md](docs/workflow.md).

---

## The human workflow

Contributor Scout is one step in a longer loop. It does not close the loop.

1. **Run profile mode.** Stop here if viability is poor — that is a result, not
   a failure.
2. **Run full discovery** (or one category mode to calibrate cost first).
3. **Review the shortlisted candidates.** Read the rejections too; they often
   contain the most useful facts about the codebase.
4. **Manually verify the top candidate.** Reproduce the evidence yourself. If
   you cannot reproduce it, do not propose it.
5. **Re-check current issues and pull requests.** Use `refresh` mode. Remote
   state moves faster than your analysis.
6. **Contact maintainers** where scope or design direction is uncertain.
   "Comment and wait" is frequently the correct next action.
7. **Use a separate implementation workflow.** The approved dossier is its input.
8. **Review every changed line yourself.** You are submitting it under your name.
9. **Submit a focused pull request** — minimum scope, explicit exclusions, and a
   description a maintainer can act on.

> [!IMPORTANT]
> The gate that matters most is step 4. If you cannot explain the problem, root
> cause, fix, alternatives, and risks *without referring to the dossier*, you
> are not ready to submit.

---

## Safety model

**Contributor Scout is discovery-only.** It reads, reasons, and writes reports
under `contribution-discovery/`. It does not modify the software it analyses and
does not write to GitHub.

Three independent layers enforce this:

1. **Instruction** — hard constraints in `SKILL.md` §2, repeated in every agent.
2. **Permission** — the host's own gate. This is the layer that differs:

   | Host | Layer 2 mechanism |
   |---|---|
   | Claude Code | Declarative allow/ask/deny rules in `settings.json` — the strongest of the four |
   | GitHub Copilot | Per-tool confirmation prompts |
   | Cursor | Per-command confirmation prompts and command allow/deny lists |
   | Antigravity | The agent's `commandExecutionPolicy`; the bundled agents ship `auto` |

3. **Hook** — the optional [`discovery_guard.py`](hooks/discovery_guard.py)
   pre-tool-use hook denies writes outside the output directory, Git state
   mutation, GitHub write commands, and destructive shell. One script serves all
   four hosts: it accepts each host's payload shape and emits a deny carrying
   every host's spelling at once.

The hook is **not installed automatically**. Read [hooks/README.md](hooks/README.md)
first — it applies to every tool call in the session, which will block ordinary
development if you enable it globally.

Security findings get separate handling: the disclosure channel is identified in
Phase 0, materially exploitable findings are marked `PRIVATE_DISCLOSURE`, no
document contains a working exploit, and the final recommendation names the
finding without restating the vulnerable path.

Full model, including what it does **not** protect against:
[docs/safety-model.md](docs/safety-model.md).

---

## Limitations

Read these before trusting a report.

**AI false positives.** The system can produce a confident, wrong finding. The
adversarial validation phase and the evidence gates reduce this; they do not
eliminate it. Independently verify the primary candidate before acting.

**Incomplete semantic duplicate detection.** Two people can describe the same
problem with no shared vocabulary. Searching 12 query variants across issues,
PRs, and discussions is far better than title matching, and still not complete.
Always re-check manually before implementing.

**Imperfect maintainer intent.** Alignment is inferred from written artefacts.
Unwritten preferences, private discussions, and recent changes of direction are
invisible. When alignment matters, ask — that is why "comment first" is so often
the recommended action.

**Dependence on repository quality.** A project with no tests, no CONTRIBUTING,
squashed history, and an empty issue tracker gives the system very little to work
with. Reports will be correspondingly weak, and should say so.

**GitHub authentication.** Without `gh`, duplicate status cannot exceed
`UNKNOWN` and confidence stays `LOW`. Rate limits can also truncate searches on
large repositories.

**Benchmark uncertainty.** Measurements taken on a laptop are noisy and may not
reflect the maintainer's platform or a production workload. Treat magnitudes as
estimates until reproduced on CI.

**Security disclosure constraints.** The system identifies a disclosure channel
and drafts a report; it cannot judge every project's coordination norms, and it
will not send anything. Private disclosure is a human action.

**Scale.** Very large repositories cannot be reviewed exhaustively. The skill
asks you to name subsystems above roughly 5,000 files, and
`03-review-coverage.md` records what was not examined. Absence of findings in an
unreviewed area is not evidence of absence.

---

## Troubleshooting

<details>
<summary><b>The skill does not appear in my assistant</b></summary>

<br>

Confirm the file is where your host looks for it, then restart or reload:

```bash
ls ~/.claude/skills/contributor-scout/SKILL.md            # Claude Code
ls ~/.copilot/skills/contributor-scout/SKILL.md           # Copilot
ls ~/.cursor/skills/contributor-scout/SKILL.md            # Cursor
ls ~/.gemini/config/skills/contributor-scout/SKILL.md     # Antigravity
```

The directory name must stay `contributor-scout` — on Cursor the `name:` in the
frontmatter is required to match the parent folder, and on the other hosts a
mismatch makes the skill hard for the model to select. If you copied a host tree
into the wrong host's path, the frontmatter will be wrong for that host; copy
from the matching directory in the [Supported hosts](#supported-hosts) table.
</details>

<details>
<summary><b>GitHub CLI is not authenticated</b></summary>

<br>

```bash
gh auth status      # diagnose
gh auth login       # fix
```

The skill continues without it, in degraded mode: duplicate status `UNKNOWN`,
confidence `LOW`, non-duplication rating capped at 2. Verify duplicate status by
hand before implementing anything. Check what degraded mode recorded:

```bash
python3 -c "import json;d=json.load(open('contribution-discovery/evidence/github-searches.json'));print(d['remote_access'],d['duplicate_detection_confidence'])"
```
</details>

<details>
<summary><b>Tests cannot run</b></summary>

<br>

Expected for projects needing databases, services, or paid infrastructure. Tell
the skill:

```text
Tests cannot run locally — the suite needs a Postgres instance.
Proceed with [CODE]-only evidence and set the no_reproducible_evidence risk flag.
```

Consequence: no `[TEST]` evidence, a −20 risk deduction on affected candidates,
and a lower ceiling on `evidence_problem_real`. That is the correct outcome, not
a bug — an unreproduced finding is genuinely weaker.
</details>

<details>
<summary><b>Repository setup is incomplete</b></summary>

<br>

Do not let the skill install anything to fix it. Either build the project
manually once yourself (recommended before any run), or accept
`PROCEED_WITH_LIMITATIONS` and carry the limitation into every candidate. If the
project cannot be built at all without privileged infrastructure, that is a
legitimate `DO_NOT_INVEST`.
</details>

<details>
<summary><b>Repository is too large</b></summary>

<br>

Above roughly 5,000 source files, scope the run explicitly:

```text
Use the contributor-scout skill in performance mode, scoped to src/parser/ only.
```

Pick the scope from Phase 1's churn analysis and critical-path table — the
highest-churn directories are usually where contributions have most value.
</details>

<details>
<summary><b>Findings are too broad or vague</b></summary>

<br>

Usually means Phase 1 was too shallow — path importance and trust boundaries
were never established, so reviewers had nothing to anchor to. Re-run `profile`
mode with a narrower scope, then re-run the category mode. You can also raise the
bar directly:

```text
Only shortlist candidates with [TEST] evidence and a duplicate status of CLEAR.
```
</details>

<details>
<summary><b>Duplicate status stays UNKNOWN</b></summary>

<br>

Either `gh` is unavailable (see above), or the repository is not on GitHub.
Check the remote:

```bash
git remote -v
```

For GitLab, Codeberg, or Gitea, duplicate detection currently has no automated
path — it stays `UNKNOWN` and you must check the issue tracker manually. Host
support is on the [V4 roadmap](docs/implementation-roadmap.md).
</details>

<details>
<summary><b>Security policy is missing</b></summary>

<br>

The skill recommends a private channel anyway — GitHub private vulnerability
reporting if enabled, otherwise a maintainer email from commit history. It will
never default to a public issue for a sensitive finding. The absence of a policy
is itself worth raising with maintainers, separately and non-urgently. See
[responsible-disclosure.md](skills/contributor-scout/references/responsible-disclosure.md).
</details>

<details>
<summary><b>Reports fail schema validation</b></summary>

<br>

```bash
python3 skills/contributor-scout/scripts/validate_report_schema.py \
  --dir contribution-discovery --format json
```

Common causes: a missing mandatory section, no duplicate status, no evidence
tags, `CLEAR` combined with `LOW` confidence, no introducing-commit SHA and no
statement that history was unavailable, an empty next action, or more than three
shortlisted candidates. Fix the content — do not relax the validator. Print the
required list with `--list-required-sections`.
</details>

<details>
<summary><b>Scoring reports blocking errors</b></summary>

<br>

```bash
python3 skills/contributor-scout/scripts/calculate_candidate_score.py \
  --input contribution-discovery/machine-readable/candidates.json
```

Exit code 2 means at least one candidate is disqualified — usually a duplicate
status of `DUPLICATE`, `CLAIMED`, `REJECTED`, or `SUPERSEDED`, a missing rating,
or `CLEAR` with `LOW` confidence. Blocking errors are resolved by fixing the
candidate or rejecting it, never by overriding the script.
</details>

<details>
<summary><b>The discovery-guard hook blocks ordinary work</b></summary>

<br>

That is the documented trade-off: the hook applies to every tool call in the
session, not just Contributor Scout's. Remove the block or file you added —
`.claude/settings.json` `hooks`, `.github/hooks/discovery-guard.json`,
`.cursor/hooks.json`, or `.agents/hooks.json` — and reload. Prefer enabling it
in the *analysed* repository for the duration of a run. See
[hooks/README.md](hooks/README.md).
</details>

---

## Project structure

```text
contributor-scout/
├── README.md
├── LICENSE                          MIT
├── assets/                          README banner (light + dark SVG)
├── .claude-plugin/plugin.json       Claude Code plugin manifest
├── AI_Assisted_Open_Source_Contribution_Discovery_Plan.md   design source of truth
│
├── skills/contributor-scout/        ← CANONICAL skill payload (Claude Code)
│   ├── SKILL.md                     workflow, hard constraints, modes, gates
│   ├── references/                  12 review playbooks (loaded per phase)
│   ├── templates/                   11 report templates
│   └── scripts/                     5 stdlib-only Python helpers
├── agents/                          6 Claude Code subagent definitions
│
├── .github/                         GitHub Copilot equivalents
│   ├── skills/contributor-scout/
│   └── agents/*.agent.md
├── .cursor/                         Cursor equivalents
│   ├── skills/contributor-scout/
│   └── agents/*.md
├── .agents/                         Antigravity equivalents
│   ├── skills/contributor-scout/
│   ├── agents/*.md
│   └── workflows/contributor-scout.md   the /contributor-scout slash command
│
├── hooks/                           optional discovery-guard hook, all four hosts
├── tools/sync_hosts.py              drift check across the four host trees
├── examples/                        worked fictional output
└── docs/
    ├── architecture.md
    ├── workflow.md
    ├── output-format.md
    ├── safety-model.md
    └── implementation-roadmap.md
```

The [planning document](AI_Assisted_Open_Source_Contribution_Discovery_Plan.md)
is the detailed design source and is kept unchanged.

---

## Contributing

Improvements to Contributor Scout itself are welcome. The most valuable ones
come from running it and recording what went wrong.

**High-value contributions**

- **Failure reports from real runs.** A false positive that survived adversarial
  validation, or a duplicate the two-pass search missed, is worth more than a new
  feature. Include the repository, the candidate, and what the system should have
  noticed.
- **Language-specific playbooks.** The current security and performance
  playbooks are ecosystem-neutral and therefore miss language-specific classes.
- **Rating-anchor calibration** based on observed maintainer outcomes.
- **Script robustness** — new manifest formats, build systems, and CI platforms
  in `collect_repo_metadata.py`.
- **New hosts.** The four-tree layout is designed to extend; see
  [docs/architecture.md](docs/architecture.md#host-packaging).

**Ground rules**

- Edit `skills/contributor-scout/` — it is canonical — then propagate:

  ```bash
  python3 tools/sync_hosts.py --write   # references/, templates/, scripts/
  python3 tools/sync_hosts.py           # verify; exit 1 means drift remains
  ```

  `SKILL.md` and agent frontmatter are host-specific by design, so the tool
  reports those and leaves the merge to you.
- Update playbooks **only from observed failure patterns**, never from
  speculative complexity. The fastest way to ruin this system is to grow the
  playbooks faster than the evidence justifies.
- Keep `SKILL.md` short. Detail belongs in `references/`, loaded on demand.
- Scripts stay standard-library-only. A dependency is a permanent tax on every
  user.
- Any change to the mandatory section list must update
  `validate_report_schema.py`, `templates/candidate-finding.md`, and
  `docs/output-format.md` together.

**Before submitting**

```bash
# 1. everything compiles
for f in skills/contributor-scout/scripts/*.py hooks/*.py tools/*.py; do
  python3 -m py_compile "$f" || echo "FAILED: $f"
done

# 2. the four host trees agree
python3 tools/sync_hosts.py

# 3. the worked examples still validate and score
python3 skills/contributor-scout/scripts/validate_report_schema.py \
  --candidate examples/sample-candidate.md --strict
python3 skills/contributor-scout/scripts/calculate_candidate_score.py --example \
  | python3 skills/contributor-scout/scripts/calculate_candidate_score.py --input -

# 4. the hook still denies what it should, in every host dialect
echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m x"},"cwd":"'"$PWD"'"}' \
  | python3 hooks/discovery_guard.py
echo '{"hook_event_name":"beforeShellExecution","command":"git push","cwd":"'"$PWD"'"}' \
  | python3 hooks/discovery_guard.py
echo '{"toolCall":{"name":"run_command","args":{"CommandLine":"git push","Cwd":"'"$PWD"'"}}}' \
  | python3 hooks/discovery_guard.py
```

---

## Roadmap

| Version | Theme | Status |
|---|---|---|
| **V1** | Core orchestrator, review playbooks, GitHub and Git integration, templates, deterministic scoring and validation, read-only safety model | **Shipped** |
| **V1.1** | Cursor and Antigravity support, one hook for four hosts, host-tree drift check | **This release** |
| **V2** | Independent adversarial validator, candidate-specific query generation, stale-candidate detection, persistent rejected-findings store, schema-versioned reports | Planned |
| **V3** | Language-specific playbooks, optional Semgrep/CodeQL/profiler integrations, framework heuristics, historical calibration | Planned |
| **V4** | Distributable plugin, published JSON Schemas, evaluation dataset linking proposals to maintainer outcomes, non-GitHub repository hosts | Planned |

Detail, success metrics, and the pilot plan:
[docs/implementation-roadmap.md](docs/implementation-roadmap.md).

---

## Licence

[MIT](LICENSE) © 2026 Vaibhav Vanage

---

<div align="center">

**Contributor Scout does not optimise for the number of pull requests you open.**
**It optimises for the quality of the decision that precedes one.**

</div>
