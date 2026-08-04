# Implementation Roadmap

Delivery plan for Contributor Scout, aligned with
[`AI_Assisted_Open_Source_Contribution_Discovery_Plan.md`](../AI_Assisted_Open_Source_Contribution_Discovery_Plan.md),
sections 18-22.

---

## V1 - Structured discovery foundation (this release)

| Capability | Status |
|---|---|
| Orchestrator skill with explicit phases and stop conditions | Delivered - [`SKILL.md`](../skills/contributor-scout/SKILL.md) |
| Security, performance, and feature reference playbooks | Delivered - 12 references |
| GitHub CLI read-only searches for issues and pull requests | Delivered - [`search_github_candidates.py`](../skills/contributor-scout/scripts/search_github_candidates.py) |
| Git blame, log, commit, and introducing-PR analysis | Delivered - [`collect_git_history.py`](../skills/contributor-scout/scripts/collect_git_history.py) |
| Markdown dossiers, evidence JSON, scorecard, final recommendation | Delivered - 11 templates |
| Deterministic scoring and report completeness checks | Delivered - [`calculate_candidate_score.py`](../skills/contributor-scout/scripts/calculate_candidate_score.py), [`validate_report_schema.py`](../skills/contributor-scout/scripts/validate_report_schema.py) |
| Read-only permissions, writes restricted to the discovery directory | Delivered - [`safety-model.md`](safety-model.md), optional [hook](../hooks/README.md) |
| Specialised subagents | Delivered ahead of plan - six agents in [`agents/`](../agents/) |

### V1 exit criteria

Run V1 against three repositories with different languages or architectures,
then answer:

- Are the findings real? Have they been independently verified by a second
  engineer?
- Is duplicate detection demonstrably better than exact-title search?
- Does the dossier materially reduce implementation and PR-writing effort?
- Did any unsafe action occur - source edit, public post, push, destructive
  command? (Target: zero.)
- Which components should be automated in V2, and which should stay human?

Pilot exit is met when at least two repositories produce either a useful,
independently verified candidate **or** a well-justified "no candidate" result.

---

## V2 - Specialised agents and automation

- Formalise the adversarial validator as a distinct agent rather than a phase of
  the ranker, so falsification is genuinely independent of scoring.
- Candidate-specific semantic query generation - derive the query variant set
  from the candidate's own terminology instead of relying on the model to
  brainstorm it each time.
- `refresh` mode hardening: stale-candidate detection that diffs the current
  remote state against the state recorded at generation time and flags what
  changed.
- A persistent rejected-findings store, so a later run recognises an idea it has
  already rejected rather than rediscovering it.
- Schema-versioned reports with automated migration, so pilot results stay
  comparable as the rubric evolves.
- Calibration of the rating anchors against real maintainer outcomes.

---

## V3 - Language and ecosystem depth

- Language-specific security and performance playbooks (Python, TypeScript, Go,
  Rust, Java) - generic playbooks miss ecosystem-specific classes.
- Optional integrations, all opt-in and approval-gated: Semgrep, CodeQL,
  language profilers, benchmark harnesses, dependency analysis.
- Framework and build-system heuristics: Django, FastAPI, Express, Next.js,
  Spring, Bazel, Cargo workspaces.
- Historical calibration - feed accepted, rejected, and revised proposals back
  into the scoring anchors so the weights reflect observed outcomes rather than
  a priori judgement.

---

## V4 - Open-source productisation

- Package as a distributable Claude Code plugin with a marketplace entry.
- Publish the report schemas as versioned JSON Schema documents.
- Build an evaluation dataset linking discovery proposals to maintainer
  outcomes - the only honest way to measure whether the system works.
- Support other repository hosts (GitLab, Codeberg, Gitea) and other coding
  agents.
- Position the project explicitly as an evidence-first contribution *discovery*
  framework, not an automated pull-request generator.

---

## Success metrics

Track these from the first pilot. The V1 targets come from the planning
document, section 19.

| Metric | Definition | V1 target |
|---|---|---|
| True-positive rate | Shortlisted findings independently confirmed as real and correctly understood | ≥ 70% |
| Duplicate avoidance | Candidates shortlisted despite existing equivalent work | < 10% |
| Evidence completeness | Dossiers containing all mandatory sections and references | 100% |
| Human approval rate | Shortlisted candidates approved for discussion or implementation | ≥ 50% |
| Scope quality | Approved candidates expressible as a focused PR with no unrelated refactors | ≥ 80% |
| Maintainer outcome | Proposals accepted, positively discussed, or constructively redirected | Track; no hard target initially |
| Unsafe action count | Unauthorised source edits, public posts, pushes, destructive commands | **Zero** |
| Reviewer usefulness | Engineer rating of whether the dossier reduced research effort | ≥ 4/5 average |

Evidence completeness is the one metric the system enforces mechanically -
`validate_report_schema.py` should make 100% achievable on every run. The others
require human review.

---

## Quality review questions

Ask these of every pilot dossier, as a team:

- Could an engineer reproduce the finding using only the dossier?
- Does the report distinguish facts, tests, history, maintainer statements,
  inference, and uncertainty?
- Would the maintainer pitch remain respectful if the original author read it?
- Does the proposed PR solve one coherent problem?
- Are alternatives and compatibility risks represented fairly?
- **Would the team still recommend this contribution if no AI had been
  involved?**

The last question is the real test.

---

## Operating model

| Role | Responsibility |
|---|---|
| Skill owner | `SKILL.md`, phase definitions, permissions, release versions |
| Security reviewer | Security playbooks, disclosure rules, validation thresholds |
| Performance reviewer | Benchmark standards, profiler integrations, evidence quality |
| Feature and product reviewer | Roadmap analysis, demand evidence, maintenance-cost evaluation |
| Tooling engineer | GitHub, history, scoring, validation, and report-generation scripts |
| Pilot contributors | Run the system, verify candidates, record maintainer outcomes |
| Approver | Authorises implementation; confirms the engineer can defend the proposal |

**Cadence:** review every completed pilot report as a team. Track false
positives, missed duplicates, unclear evidence, and maintainer feedback. Update
playbooks **only from observed failure patterns**, never from speculative
complexity - the fastest way to ruin this system is to grow the playbooks
faster than the evidence justifies. Version the skill and the report schema so
historical pilot results stay comparable.

---

## Pilot selection

Choose three repositories that are active, accept external contributions, have
working tests, and match team expertise. Prefer diversity in language or
architecture so the workflow does not overfit one ecosystem. Avoid very large
repositories for the first pilot.

Sequence per repository:

1. `profile` mode; validate the viability decision manually.
2. One category-specific mode, to calibrate depth and token use.
3. `full` mode; no more than three final candidates.
4. A second engineer independently verifies the primary candidate.
5. Classify: implement, discuss, disclose, hold, or reject.
6. For approved candidates, use a separate implementation workflow and submit a
   focused contribution.
7. Record the maintainer outcome and update the rubric from what actually
   happened.
