<!--
One coherent change per PR — the project scores other people's candidates down
for bundled refactors, and holds itself to the same bar.
-->

## What and why

<!-- What changes, and what observed problem motivates it. Link the issue. -->

Closes #

## Type of change

- [ ] Playbook / reference / prompt change — **link the run-failure report or observed failure that motivates it** (required, see [the ground rule](https://github.com/Phantom-IN/contributor-scout/blob/main/CONTRIBUTING.md#ground-rule-playbooks-grow-from-failures-not-ideas)):
- [ ] Report-contract change — validator, affected templates, and `docs/output-format.md` all updated together
- [ ] Scoring change — weights/gates/anchors, citing outcome data where any exists
- [ ] Script fix or robustness improvement (standard library only)
- [ ] Hook change — all four payload dialects handled; deny tests extended
- [ ] New host support
- [ ] Documentation / examples
- [ ] Repo infrastructure (CI, templates, packaging)

## Evidence (for prompt-behaviour changes)

<!--
Prompts cannot be unit-tested. Before/after dossier excerpts from a real run,
trimmed, with the target repo named or anonymised. Delete this section for
pure script/docs/infra changes.
-->

## Verification

- [ ] Edited the **canonical** tree (`skills/contributor-scout/`, `agents/`), then ran `python3 tools/sync_hosts.py --write`
- [ ] `python3 tools/sync_hosts.py` reports no drift
- [ ] `python3 -m py_compile skills/contributor-scout/scripts/*.py hooks/*.py tools/*.py` passes
- [ ] Example validation and scoring round-trip pass (commands in [CONTRIBUTING.md](https://github.com/Phantom-IN/contributor-scout/blob/main/CONTRIBUTING.md#verifying-a-change))
- [ ] Hook deny tests pass in all host dialects (if the hook or safety model changed)
- [ ] Documentation updated where behaviour changed (README, docs/, CHANGELOG "Unreleased")
