# Contributing to Contributor Scout

Thank you for considering it. This project applies its own standard to itself:
**a contribution should exist because there is evidence it is needed**, not
because it was easy to write. The single most valuable thing you can send us is
not code — it is a record of a real run that went wrong.

This document covers how the repository is organised, how to make and verify a
change, and what we look for in a pull request. The short version:

1. Open an issue before any non-trivial change.
2. Edit the canonical tree, then propagate with the sync tool.
3. Run the four verification suites before pushing.
4. Keep the pull request small enough to review in one sitting.

By participating you agree to our [Code of Conduct](CODE_OF_CONDUCT.md).
Security problems in Contributor Scout itself go through
[SECURITY.md](SECURITY.md), not the public issue tracker.

---

## What to contribute

In descending order of value to the project right now:

| Contribution | Why it matters | Where to start |
|---|---|---|
| **Failure report from a real run** | A false positive that survived adversarial validation, or a duplicate the two-pass search missed, is the raw material every playbook improvement is built from | [Run-failure issue form](https://github.com/Phantom-IN/contributor-scout/issues/new?template=20-run-failure-report.yml) |
| **Maintainer outcome report** | Whether scouted candidates actually get accepted is the only honest measure of the system — see [SHOWCASE.md](SHOWCASE.md) | [Outcome issue form](https://github.com/Phantom-IN/contributor-scout/issues/new?template=30-outcome-report.yml) |
| **Language-specific playbooks** | The current security and performance playbooks are ecosystem-neutral and miss language-specific classes | [`references/`](skills/contributor-scout/references/) + an issue describing the observed gap |
| **Rating-anchor calibration** | Scoring anchors should reflect observed maintainer outcomes, not a priori judgement | Outcome reports feed this directly |
| **Script robustness** | New manifest formats, build systems, and CI platforms in `collect_repo_metadata.py`; new forge support in the search scripts | [`scripts/`](skills/contributor-scout/scripts/) |
| **New host support** | The four-tree layout is designed to extend to further coding agents | [docs/architecture.md](docs/architecture.md) |
| **Documentation fixes** | Anything that made you stop and re-read | Direct PR is fine |

Small fixes (typos, broken links, obvious script bugs) can go straight to a
pull request. For anything that changes behaviour — playbooks, scoring,
templates, the hook, the workflow — **open an issue first** so the change can be
discussed against evidence before you invest time in it.

---

## Ground rule: playbooks grow from failures, not ideas

The fastest way to ruin this system is to grow the playbooks faster than the
evidence justifies. Every addition to a playbook, checklist, or template makes
every future run longer and more expensive, so each one has to earn its place.

A playbook change should cite at least one of:

- a **run-failure report** (yours or an existing issue) showing the current
  playbook produced a wrong result;
- a **maintainer outcome** showing a scouted candidate failed for a reason the
  playbook should have caught;
- a **documented ecosystem fact** (for language-specific playbooks) with a
  reference.

"This check seems like it would help" is not sufficient. Pull requests that
grow a playbook speculatively will be declined kindly, with a request for the
evidence.

---

## Development setup

There is deliberately almost nothing to set up.

```bash
git clone https://github.com/Phantom-IN/contributor-scout.git
cd contributor-scout
python3 --version   # 3.8 or later; the scripts are standard-library-only
```

There is no `pip install`, no build step, and no test framework dependency.
[`requirements.txt`](skills/contributor-scout/scripts/requirements.txt) exists
to document that this is intentional. Keeping the scripts standard-library-only
is a hard constraint: a dependency is a permanent tax on every user, on every
host, forever.

To try your changes in a real assistant, install your working copy for your
host as described in the [README](README.md#installation), pointing the copy
commands at your checkout.

---

## Repository layout — canonical and mirrors

```text
skills/contributor-scout/        ← CANONICAL. Edit here.
agents/                          ← CANONICAL agent definitions (Claude Code)

.github/skills/ + .github/agents/   GitHub Copilot mirror
.cursor/skills/ + .cursor/agents/   Cursor mirror
.agents/skills/ + .agents/agents/   Antigravity mirror (+ workflows/)
```

The same skill ships four times because each host discovers extensions from a
different path. Inside every copy, `references/`, `templates/`, and `scripts/`
must be **byte-identical**; `SKILL.md` frontmatter, a few host-specific
sentences, and agent frontmatter legitimately differ.

The workflow is always:

```bash
# 1. edit the canonical tree
# 2. propagate the shared payload
python3 tools/sync_hosts.py --write
# 3. verify nothing is left drifting (exit 1 means drift remains)
python3 tools/sync_hosts.py
```

`--write` fixes `references/`, `templates/`, and `scripts/` automatically. It
does **not** merge `SKILL.md` prose or agent frontmatter — those are
host-specific by design, so the tool reports differences and leaves the merge
to you. If you changed the body of an agent or a `SKILL.md` section, apply the
equivalent edit in all four trees and let the tool confirm the bodies match.

Never edit a mirror directly. The sync check in CI will fail the pull request.

---

## Making specific kinds of change

### Playbooks and references (`references/`)

- Cite the motivating failure (see the ground rule above).
- Keep the progressive-disclosure structure: `SKILL.md` stays short and points
  to references that are loaded only in the phase that needs them. If your
  addition makes `SKILL.md` itself longer, it is probably in the wrong file.
- Prefer sharpening an existing check over adding a new one.

### Report contract changes (templates, mandatory sections)

The report contract is enforced mechanically, so it must change atomically.
Any change to the mandatory section list updates **all three together**:

1. `skills/contributor-scout/scripts/validate_report_schema.py`
2. `skills/contributor-scout/templates/candidate-finding.md` (and any other
   affected template)
3. [docs/output-format.md](docs/output-format.md)

…and then the worked examples in [`examples/`](examples/) must still validate.
A contract change that breaks previously valid reports needs a very good
reason, called out explicitly in the PR description.

### Scoring changes (`calculate_candidate_score.py`)

The split is deliberate: **the model supplies judgement; the script owns the
arithmetic.** Weights, gates, deduction values, and bands live in the script so
they are deterministic and reviewable. Changes to weights or anchors should
cite outcome reports ([SHOWCASE.md](SHOWCASE.md) data) wherever any exist.
Never add a way for the model to override a blocking error.

### The discovery-guard hook (`hooks/`)

`discovery_guard.py` serves four hosts with one script. A change must:

- handle **all four payload dialects** (Claude Code, Copilot, Cursor,
  Antigravity) — see the parser at the top of the script;
- keep the deny response carrying every host's spelling at once;
- extend the deny tests in CI (and the examples in
  [hooks/README.md](hooks/README.md)) for any new blocked category;
- never weaken a default deny without an issue discussing the trade-off.

### Agents (`agents/` and mirrors)

Agent **bodies** are identical across hosts; only frontmatter differs. Edit the
canonical body, replicate it to the three mirrors, and adjust frontmatter only
in host-specific terms (the sync tool verifies bodies, reports frontmatter).
Antigravity's `commandExecutionPolicy` is a documented trade-off — do not
change it casually in either direction.

### Prompt-behaviour changes in general

Prompts are code here, but they cannot be unit-tested. The evidence standard
for a prompt change is empirical:

- run the affected mode against at least one real repository **before and
  after** the change;
- include in the PR the relevant dossier excerpts (trimmed, with the target
  repository named or anonymised — your choice);
- state what got better, and what you checked for regression (e.g. "rejections
  still record a revival condition").

---

## Verifying a change

The full battery — CI runs exactly this:

```bash
# 1. everything compiles
python3 -m py_compile skills/contributor-scout/scripts/*.py hooks/*.py tools/*.py

# 2. the four host trees agree
python3 tools/sync_hosts.py

# 3. the worked examples still validate and score
python3 skills/contributor-scout/scripts/validate_report_schema.py \
  --candidate examples/sample-candidate.md --strict
python3 skills/contributor-scout/scripts/calculate_candidate_score.py --example \
  | python3 skills/contributor-scout/scripts/calculate_candidate_score.py --input -

# 4. the hook still denies what it should, in every host dialect
echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m x"},"cwd":"'"$PWD"'"}' \
  | python3 hooks/discovery_guard.py            # must print a deny
echo '{"hook_event_name":"beforeShellExecution","command":"git push","cwd":"'"$PWD"'"}' \
  | python3 hooks/discovery_guard.py            # must print a deny
echo '{"toolCall":{"name":"run_command","args":{"CommandLine":"git push","Cwd":"'"$PWD"'"}}}' \
  | python3 hooks/discovery_guard.py            # must print a deny
```

---

## Pull requests

- **One coherent change per PR.** No drive-by refactors — the project scores
  other people's candidates down for that, and holds itself to the same bar.
- Use the [pull request template](.github/PULL_REQUEST_TEMPLATE.md); the
  checklist mirrors the battery above.
- Write commit messages in the imperative mood, describing the change and the
  reason ("Tighten reachability gate for handler-registered routes").
- CI must pass. If the sync check fails, run `tools/sync_hosts.py --write` and
  commit the result.
- Expect review questions about evidence. That is the culture working, not
  gatekeeping.
- If a PR sits unreviewed for a week, a polite ping on the PR is welcome.

### Licensing of contributions

The project is [MIT-licensed](LICENSE). By submitting a contribution you agree
that it is your own work (or that you have the right to submit it) and that it
is provided under the same MIT licence. There is no CLA.

---

## How decisions get made

Contributor Scout is run by a three-person maintainer team — the canonical
list, the decision rules, and the path to joining it live in
[MAINTAINERS.md](MAINTAINERS.md). The short version: any maintainer can merge
routine changes; contract, scoring, safety-model, and hook changes take two
maintainer reviews; unresolved disagreements are settled by majority vote among
the three; and the
*principles* section of [ROADMAP.md](ROADMAP.md) is effectively constitutional
— it changes only with every maintainer's agreement, never through a routine
PR. Disagreements are resolved by evidence where possible: a reproducible run
beats an opinion, including a maintainer's.
[`.github/CODEOWNERS`](.github/CODEOWNERS) auto-requests the team's review on
every pull request, so you do not need to pick a reviewer.

---

## Questions

Open a [discussion](https://github.com/Phantom-IN/contributor-scout/discussions)
if enabled, or an issue with the plain bug/feature form. If you are unsure
whether a run went wrong "enough" to report — report it. Calibration data is
the point.
