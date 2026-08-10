# Changelog

All notable changes to Contributor Scout are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
— for a skill, "breaking" means a change to the report contract, the scoring
gates, or the safety model, not just to code.

## [Unreleased]

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
