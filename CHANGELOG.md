# Changelog

All notable changes to Contributor Scout are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
— for a skill, "breaking" means a change to the report contract, the scoring
gates, or the safety model, not just to code.

## [Unreleased]

Lessons from the first real run (BaaRai/ARTEX, see SHOWCASE.md). Two changes
touch the report contract: candidate files need a "Regression probes" section,
and a shortlisted performance candidate can no longer rest on a stand-in
measurement alone. Existing dossiers need the new section to validate.

### Added

- **`correctness` category and `BUG-nnn` candidates.** The scorer only knew
  security, performance, and feature, so a plain bug - the most mergeable kind
  of contribution - could not be scored. New `correctness` mode (phases 0-2,
  3d, 4-8), `references/correctness-review-playbook.md`, and a
  `correctness-reviewer` subagent for all four hosts.
- **Dogfooding (Phase 3d, approval-gated).** Install the project, do the first
  run, and push one core workflow through it, after the user approves the
  exact commands. A new approval gate in SKILL.md section 8 covers it.
- **Deferred follow-up mining.** `search_github_candidates.py --followups`
  searches for work maintainers pushed to "a follow-up PR" and lists it under
  `followup_matches`, maintainer-authored first. Search results now carry the
  author and their association with the repository.
- **Contributor-queue facts.** `collect_repo_metadata.py --remote` records open
  PRs per author, files touched by two or more open PRs (contended files), the
  closed-unmerged share, and closed PRs that mention "superseded". The open-PR
  cap is read from CONTRIBUTING.
- **House conventions.** `collect_repo_metadata.py` now reports changelog
  format, commit style (conventional-commit share, types, scopes, sign-offs),
  rule-like CONTRIBUTING lines, the exact `run:` commands CI executes, locale
  directories, and the PR template. They feed a new "Contribution checklist" in
  `05-final-recommendation.md`.
- **Regression probes.** A mandatory candidate section listing inputs the fix
  must not break, with today's behaviour. The ranker's falsification checklist
  checks it, and contended files.
- **`[PROXY-TEST]` evidence tag** for measurements taken outside the project's
  runtime. A shortlisted `PERF-*` candidate tagged only `[PROXY-TEST]` fails
  validation until it has a `[TEST]` from the project's own toolchain.
- **Rate-limit backoff** in `search_github_candidates.py`: a query that hits
  GitHub's search limit is retried (10 s, 20 s, 40 s, capped by
  `--max-rate-limit-wait`) instead of being recorded as failed.
- SHOWCASE.md: the first entries - two merged ARTEX PRs (#481, #517) and three
  in review.

### Fixed

- `collect_repo_metadata.py` skipped every directory starting with `.git`,
  including `.github`, so GitHub Actions workflows never appeared in
  `ci_files`.

- `tools/sync_hosts.py` no longer counts build artifacts and OS junk
  (`__pycache__/`, `*.pyc`, `.DS_Store`) as host-tree drift, and `--write`
  never copies them into the mirrors. Previously a fresh clone failed the
  drift check when the compile step ran before it — which is exactly the
  order CI and CONTRIBUTING use.

## [1.2.0] - 2026-08-10

Open-source launch release. No skill-behaviour changes; everything here is
community infrastructure, packaging, and distribution.

### Added

- Claude Code plugin-marketplace packaging
  (`.claude-plugin/marketplace.json`), enabling
  `/plugin marketplace add Phantom-IN/contributor-scout`.
- Community guidelines: `CONTRIBUTING.md` (canonical-tree workflow,
  evidence rules for playbook changes, verification battery),
  `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), and `SECURITY.md`
  (private reporting for hook bypasses, prompt-injection vectors, and script
  vulnerabilities).
- `ROADMAP.md`: north star, constitutional principles, and the five roadmap
  themes — proof and reputation, token and cost efficiency, validation depth,
  ecosystem depth, distribution.
- `SHOWCASE.md`: public registry of verified maintainer outcomes, listing
  accepted *and* declined scouted contributions.
- `MAINTAINERS.md` and `.github/CODEOWNERS`: the three-person maintainer team
  (Vaibhav Vanage, Arav Saxena, Faheem), its decision rules, the path to
  maintainership, and automatic review routing for every pull request.
- GitHub issue forms: bug report, run-failure report (false positives, missed
  duplicates, wrong rejections), maintainer outcome report, and feature
  request; plus a pull-request template mirroring the verification battery.
- Continuous integration (`.github/workflows/ci.yml`): script compilation on
  Python 3.8 and 3.12, host-tree drift check, example validation and scoring
  round-trip, discovery-guard deny tests in all host dialects, and manifest
  JSON validation.

### Changed

- Plugin version aligned with the release line (`.claude-plugin/plugin.json`
  → 1.2.0).
- README: marketplace install path, and links to the new community documents.

## [1.1.0] - 2026-08-09

Multi-host release: one skill, four assistants.

### Added

- **GitHub Copilot (VS Code) support**: `.github/skills/contributor-scout/`
  and `.github/agents/*.agent.md`.
- **Cursor support**: `.cursor/skills/contributor-scout/` and
  `.cursor/agents/*.md`.
- **Antigravity support**: `.agents/skills/contributor-scout/`,
  `.agents/agents/*.md`, and the `/contributor-scout` workflow
  (`.agents/workflows/contributor-scout.md`).
- Unified discovery-guard hook (`hooks/discovery_guard.py`): one script that
  reads all four hosts' payload shapes and emits a deny every host
  understands, with per-host example configurations and installation guide.
- `tools/sync_hosts.py`: enforces byte-identical `references/`, `templates/`,
  and `scripts/` across the four host trees; verifies agent bodies and
  SKILL.md section contracts.
- README banner (light and dark SVG).

### Changed

- README rewritten around the four-host layout, with per-host installation,
  troubleshooting, and safety-model comparison.
- Safety-model documentation extended to cover each host's permission layer.

### Removed

- Deprecated single-host discovery-guard configuration (replaced by the
  unified hook and per-host examples).

## [1.0.0] - 2026-08-04

Initial release.

### Added

- Orchestrator skill (`skills/contributor-scout/SKILL.md`) with seven modes
  (`profile`, `full`, `security`, `performance`, `features`,
  `validate <id>`, `refresh`), explicit phases, and stop conditions.
- Six reviewer subagents: repository intelligence, security reviewer,
  performance reviewer, feature scout, duplicate-and-history validator,
  contribution ranker.
- Twelve reference playbooks covering repository assessment and
  comprehension, security review, performance review, feature discovery,
  duplicate detection, git-history tracing, maintainer alignment, evidence
  classification, responsible disclosure, threat modelling, and the
  contribution-quality rubric.
- Eleven report templates and the fixed 28-section candidate contract.
- Five standard-library-only helper scripts: repository metadata collection,
  git-history collection, GitHub candidate search, deterministic candidate
  scoring, and report-schema validation.
- Read-only safety model with restricted write scope
  (`contribution-discovery/` only) and responsible-disclosure handling for
  security findings.
- Worked fictional examples (candidate, rejection, repository profile, final
  recommendation) and full documentation set (architecture, workflow, output
  format, safety model, implementation roadmap).

[Unreleased]: https://github.com/Phantom-IN/contributor-scout/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/Phantom-IN/contributor-scout/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Phantom-IN/contributor-scout/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Phantom-IN/contributor-scout/releases/tag/v1.0.0
