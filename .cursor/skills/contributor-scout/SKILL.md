---
name: contributor-scout
description: >-
  Discover evidence-backed open-source contribution opportunities in a cloned
  repository. Analyses security, performance, and feature opportunities; checks
  issues, pull requests, discussions, and Git history for duplicates and
  maintainer intent; scores candidates; and writes discovery documents under
  contribution-discovery/. Discovery only - never modifies source code, never
  commits, never opens issues or pull requests. Use when the user asks what to
  contribute to a repository, wants to find a good first contribution, wants a
  security/performance/feature review aimed at contributing upstream, or asks
  whether a repository is worth contributing to.
---

# Contributor Scout

Evidence-first contribution discovery for third-party open-source repositories.

Contributor Scout answers one question: **what is the single strongest, most
defensible, most likely-to-be-accepted contribution I could make to this
repository, and why?** It produces discovery documents. It never produces code.

Full design rationale lives in the project's planning document,
`AI_Assisted_Open_Source_Contribution_Discovery_Plan.md`.

---

## 1. Activation context

Use this skill when the user is standing in (or points at) a **cloned
third-party open-source repository** and wants to know:

- whether the repository is worth contributing to;
- what security, performance, or feature contribution to pursue;
- whether an idea they already have is duplicate, aligned, or historically naive;
- why the current code is written the way it is, before proposing a change.

Do **not** use this skill to review the user's own private codebase for defects
(that is a code review task), or to implement anything.

---

## 2. Hard constraints (non-negotiable)

During discovery you **MUST NOT**:

- modify application source code, configuration, tests, or documentation of the
  analysed repository;
- implement fixes, patches, or features, even "as an illustration" inside a file;
- create branches, stage files, create commits, amend, rebase, or push;
- open issues, create pull requests, post comments, add reactions, or edit
  anything on GitHub or any other forge;
- publish, paste, or upload vulnerability details anywhere outside the local
  discovery output, and never into a public-facing artefact;
- run destructive commands (`git reset --hard`, `git clean -fd`, `git checkout`
  over dirty files, `rm -rf`, `make clean` on a dirty tree, database drops,
  deployment or release commands);
- execute untrusted scripts, installers, or `curl | sh` style commands;
- install dependencies, create virtualenvs, run Docker builds, or start network
  services without explicit user approval;
- write anywhere outside `contribution-discovery/` in the analysed repository
  (or an output directory the user names).

You **MAY**:

- read code, search files, and follow references across the repository;
- inspect Git history (`git log`, `git show`, `git blame`, `git diff`,
  `git branch`, `git tag`, `git shortlog`);
- inspect issues, pull requests, and discussions read-only (`gh issue list/view`,
  `gh pr list/view`, `gh search`, read-only `gh api` GET requests);
- run the repository's **existing** test suite and **existing** static-analysis,
  lint, and benchmark commands, after checking what they actually do;
- create discovery documents and machine-readable metadata under the output
  directory;
- run the bundled scripts in `scripts/`.

> If the user explicitly asks you to implement an approved candidate, that is a
> **different** task. Stop this skill, state that discovery is complete, and
> begin implementation as a separate, explicitly authorised piece of work.

### Sandbox check before running anything

Before running any repository command, read what it does
(`package.json` scripts, `Makefile`, `noxfile.py`, `tox.ini`, `justfile`, CI
workflow). If a command downloads code, installs packages, starts a service,
touches credentials, or is not already documented by the repository, **ask
first**. Log every command you run to `evidence/commands-run.md`.

---

## 3. Modes

Invoke by typing `/` in Agent chat and picking `contributor-scout`, then
naming the mode - or in natural language ("use the contributor-scout skill in
profile mode"). Both are equivalent - the mode is just an argument that selects
which phases run.

| Mode | Phases | Purpose |
|---|---|---|
| `profile` | 0-1 | Repository viability and architecture only. Cheap. Run this first. |
| `full` | 0-8 | Complete discovery across all three categories. |
| `security` | 0-2, 3a, 4-8 | Security-only review with disclosure handling. |
| `performance` | 0-2, 3b, 4-8 | Performance-only review with benchmark design. |
| `features` | 0-2, 3c, 4-8 | Roadmap and demand-backed feature discovery. |
| `validate <candidate-id>` | 4-7 | Adversarial revalidation of one existing dossier. |
| `refresh` | 2, 5, 7-8 | Re-check remote activity, duplicate status, and ranking of existing candidates. |

Default when no mode is given: **`profile`**. Never silently escalate to `full` -
profile mode is cheap and its viability decision may end the run.

If the repository has more than roughly 5,000 source files, ask the user to name
the subsystems to focus on before running `full`.

---

## 4. Workflow

Track phases with a todo list. Do not skip phases. Do not reorder them.

### Phase 0 - Repository eligibility

Read `references/repository-assessment.md`.

Run `scripts/collect_repo_metadata.py` and inspect: recent commit and release
activity, licence, `CONTRIBUTING`, `CODE_OF_CONDUCT`, `SECURITY`, test setup,
CI, whether external PRs are merged, maintainer response behaviour, roadmap,
archival status, mirror status, in-flight rewrites, CLA requirements.

Emit exactly one decision:

```text
PROCEED | PROCEED_WITH_LIMITATIONS | DO_NOT_INVEST
```

Write `00-repository-profile.md` and `machine-readable/repository-profile.json`.

**Stop condition:** on `DO_NOT_INVEST`, write the profile, explain the negative
signals, and stop. Do not proceed without explicit user override.

### Phase 1 - Repository comprehension

Read `references/repository-comprehension.md`.

Map purpose, user personas, architecture, modules, data flows, trust boundaries,
external systems, public interfaces, authn/authz, storage, extension points,
critical paths, test architecture, build and release process, coding
conventions, known limitations, roadmap, and historical design decisions.

Write `01-architecture-and-context.md`.

**Stop condition (`profile` mode):** stop here. Report the viability decision and
the architecture summary, and tell the user which mode to run next.

### Phase 2 - Existing-work map

Read `references/duplicate-detection-playbook.md`.

Run `scripts/search_github_candidates.py` for the broad sweep. Collect open and
closed issues, open/draft/merged/closed PRs, discussions, roadmap, changelog,
release notes, TODO/FIXME comments, security advisories, maintainer comments,
and repeated user requests.

Write `02-existing-work-map.md` and `evidence/github-searches.json`.

If `gh` is missing or unauthenticated, record
`Duplicate-detection confidence: LOW` in the map and carry that limitation into
every candidate. Do not silently proceed as if the remote were checked.

### Phase 3 - Specialised discovery

Run the enabled reviewers **independently**. Each produces *raw candidates* -
hypotheses, not recommendations. Do not let one reviewer read another's
conclusions before Phase 6.

- 3a Security - `references/security-review-playbook.md`
- 3b Performance - `references/performance-review-playbook.md`
- 3c Features - `references/feature-discovery-playbook.md`

For non-trivial repositories, delegate each reviewer to its subagent
(`/security-reviewer`, `/performance-reviewer`, `/feature-scout`) with the Phase 1
context as input. Record what was and was not reviewed in `03-review-coverage.md` -
honest coverage gaps are more useful than implied completeness.

### Phase 4 - Historical investigation

Read `references/git-history-playbook.md`. Run `scripts/collect_git_history.py`
on each promising candidate's source locations.

Identify the introducing commit, the introducing PR where verifiable, the
original objective and constraints, relevant maintainer comments, which
assumptions have since changed, and why a change is now justified.

**History is explanation, not blame.** Frame the original design as reasonable
under its original constraints. Never name a contributor as the cause of a
defect. If you cannot verify the introducing PR, say so - do not guess a number.

### Phase 5 - Duplicate validation (second pass)

Re-run duplicate detection now that candidate-specific terminology exists:
symptom, component, file path, function name, error string, root cause,
synonyms, and the *proposed solution* wording.

Assign one status per candidate:

```text
CLEAR | RELATED | PARTIALLY_COVERED | CLAIMED | DUPLICATE | REJECTED | SUPERSEDED | UNKNOWN
```

**Rule:** never assign `CLEAR` unless current remote issues *and* pull requests
were checked successfully in this run. Where remote access failed, use
`UNKNOWN` with `Duplicate-detection confidence: LOW`.

### Phase 6 - Adversarial validation

Try to **disprove** every candidate. Read
`references/contribution-quality-rubric.md`.

Test: reachability, reproducibility, impact, expected behaviour, hidden
mitigations, project relevance, architecture fit, compatibility, testability,
scope, duplicate status, maintainer alignment.

Assign one disposition:

```text
SHORTLIST | NEEDS_MAINTAINER_INPUT | HOLD | REJECT | PRIVATE_DISCLOSURE
```

Every rejected candidate gets a `REJECTED-nnn.md` file recording why it was
rejected and the condition under which it would become worth reconsidering.

### Phase 7 - Scoring

Score every surviving candidate with
`scripts/calculate_candidate_score.py`. Do not hand-compute totals; the script
is the authority on arithmetic, gates, and bands. Rate each category 0-5 against
the anchors in `references/contribution-quality-rubric.md` and declare each risk
flag honestly.

Write `04-candidate-scorecard.md` and `machine-readable/candidates.json`.

### Phase 8 - Final recommendation

Shortlist **at most three** candidates and recommend **one** primary. Include
selection reasoning, evidence summary, maintainer pitch, implementation
prerequisites, scope boundaries, risks, and the next action.

Write `05-final-recommendation.md` and `machine-readable/final-ranking.json`.

Then run `scripts/validate_report_schema.py` over the output directory and fix
every reported error before declaring completion.

**A valid, successful outcome is:**

```text
No contribution currently meets the required evidence and alignment threshold.
```

Prefer that over shortlisting something weak.

---

## 5. Output contract

Write everything under `contribution-discovery/` at the repository root (or the
directory the user names). Never write outside it.

```text
contribution-discovery/
├── 00-repository-profile.md
├── 01-architecture-and-context.md
├── 02-existing-work-map.md
├── 03-review-coverage.md
├── 04-candidate-scorecard.md
├── 05-final-recommendation.md
├── candidates/            SEC-001.md, PERF-001.md, FEAT-001.md, REJECTED-001.md
├── evidence/              commands-run.md, source-locations.json,
│                          github-searches.json, benchmark-plan.md,
│                          unresolved-questions.md
└── machine-readable/      repository-profile.json, candidates.json,
                           final-ranking.json
```

Candidate IDs: `SEC-nnn`, `PERF-nnn`, `FEAT-nnn`, `REJECTED-nnn` (zero-padded to
three digits). IDs are stable across `refresh` runs - never renumber.

Use `templates/` for every document. Every shortlisted candidate must contain
all mandatory sections listed in `templates/candidate-finding.md`;
`scripts/validate_report_schema.py` enforces this.

Add `contribution-discovery/` to the user's global gitignore or tell them to
exclude it - do **not** edit the target repository's `.gitignore`.

---

## 6. Evidence requirements

Read `references/evidence-classification.md`.

Every material claim carries a tag:

```text
[CODE] [TEST] [HISTORY] [MAINTAINER] [DOCS] [INFERENCE] [UNVERIFIED]
```

Rules:

- Source locations are `path/to/file.ext:LINE` or `:START-END`, verified by
  reading the file in this run. Never cite a line number you did not read.
- `[TEST]` requires a command you actually ran, with its output recorded.
- `[MAINTAINER]` requires a quotable statement with a link or reference.
- Any claim you cannot support is `[INFERENCE]` or `[UNVERIFIED]` - never
  upgrade a guess to a fact to make a candidate look stronger.
- A candidate whose core impact claim is `[INFERENCE]` or `[UNVERIFIED]` cannot
  be `SHORTLIST`. It is `HOLD` or `NEEDS_MAINTAINER_INPUT` at best.

---

## 7. Security disclosure handling

Read `references/responsible-disclosure.md` before writing any security
candidate.

1. Read `SECURITY.md`, `.github/SECURITY.md`, advisory settings, and any
   bug-bounty policy. Record the private disclosure channel in the profile.
2. If a finding is materially exploitable, set disposition
   `PRIVATE_DISCLOSURE`. Do not recommend a public issue or public PR for it.
3. Keep exploit detail, working payloads, and precise reproduction steps out of
   any document intended for public sharing. The candidate file records
   *enough* for the maintainer conversation and no more.
4. Severity and contribution suitability are separate judgements. A critical
   vulnerability may be an excellent disclosure and a poor public PR.
5. Where no security policy exists, say so and recommend a private channel
   (maintainer email, GitHub private vulnerability reporting) rather than
   defaulting to a public issue.

---

## 8. Human approval gates

The skill stops at every gate and asks. It never proceeds through one on its own.

| Gate | Question | Where |
|---|---|---|
| Repository | Active, contribution-friendly, feasible? | End of Phase 0 |
| Cost | Full discovery is expensive - proceed? | Before Phase 3 |
| Disclosure | Does this need private disclosure? | Phase 6, security only |
| Human | Can the engineer explain and defend this? | After Phase 8 |
| Implementation | Approved to implement? | **Outside this skill** |

---

## 9. Completion criteria

A run is complete only when all of these hold:

- [ ] Every phase for the selected mode ran, or was explicitly skipped with a
      recorded reason in `03-review-coverage.md`.
- [ ] `00`-`05` documents exist and are populated (subject to mode).
- [ ] Every shortlisted candidate passes `scripts/validate_report_schema.py`.
- [ ] Every shortlisted candidate has a duplicate status assigned in this run,
      with confidence, and `CLEAR` was only used after a successful remote check.
- [ ] Every shortlisted candidate has introducing-commit analysis, or an explicit
      statement of why history tracing was not possible.
- [ ] Every score came from `calculate_candidate_score.py`.
- [ ] Security candidates have a disclosure recommendation.
- [ ] Rejected candidates are recorded with rejection reasons and reconsideration
      conditions.
- [ ] `evidence/commands-run.md` lists every command run.
- [ ] No file outside the output directory was created or modified.
- [ ] No write operation was performed against GitHub.

Report honestly. If a phase was degraded (no `gh`, no runnable tests, partial
coverage), say so in the final summary rather than implying completeness.

---

## 10. Stop conditions

Stop immediately and report when:

- repository eligibility is `DO_NOT_INVEST`;
- the repository is archived, a read-only mirror, or has no open-source licence;
- the user asks for implementation (hand off, do not implement here);
- a required command needs approval and the user declines;
- no candidate survives Phase 6 - report "no contribution currently meets the
  threshold" with the rejected list as supporting evidence;
- you find yourself about to write outside `contribution-discovery/`.

---

## 11. Bundled resources

Load these on demand - do not read them all up front.

**References** (`references/`)

| File | When to read |
|---|---|
| `repository-assessment.md` | Phase 0 |
| `repository-comprehension.md` | Phase 1 |
| `duplicate-detection-playbook.md` | Phases 2 and 5 |
| `security-review-playbook.md` | Phase 3a |
| `performance-review-playbook.md` | Phase 3b |
| `feature-discovery-playbook.md` | Phase 3c |
| `git-history-playbook.md` | Phase 4 |
| `maintainer-alignment-playbook.md` | Phases 3c and 6 |
| `contribution-quality-rubric.md` | Phases 6 and 7 |
| `evidence-classification.md` | All phases that write documents |
| `responsible-disclosure.md` | Any security finding |
| `threat-model-template.md` | Any security finding |

**Templates** (`templates/`) - one per output document; use verbatim structure.

**Scripts** (`scripts/`) - run with `python3`; all support `--help`.

| Script | Purpose |
|---|---|
| `collect_repo_metadata.py` | Phase 0 repository facts as JSON |
| `collect_git_history.py` | Phase 4 blame, log, introducing-commit candidates |
| `search_github_candidates.py` | Phases 2 and 5 read-only `gh` searches |
| `calculate_candidate_score.py` | Phase 7 deterministic scoring |
| `validate_report_schema.py` | Phase 8 report completeness check |

**Subagents** (`.cursor/agents/` directory): `repository-intelligence`,
`security-reviewer`, `performance-reviewer`, `feature-scout`,
`duplicate-history-validator`, `contribution-ranker`.
