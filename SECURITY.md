# Security Policy

Contributor Scout tells other people how to report vulnerabilities responsibly,
so it holds itself to the same standard. If you find a security problem in
**this project**, please report it privately first.

> Found a vulnerability **in a repository you analysed with Contributor
> Scout**? That is not ours to receive. Follow that project's own security
> policy — the skill's
> [responsible-disclosure reference](skills/contributor-scout/references/responsible-disclosure.md)
> describes how to locate the right private channel. Never open a public issue
> for it, here or there.

## Supported versions

| Version | Supported |
|---|---|
| Latest release / `main` | ✅ |
| Anything older | ❌ — please reproduce on `main` |

## What counts as a vulnerability here

Contributor Scout is a set of prompts, Markdown playbooks, standard-library
Python scripts, and an optional enforcement hook. Its interesting attack
surface is unusual but real:

- **Discovery-guard bypass.** Any input that gets a source-modifying, Git-state
  mutating, GitHub-writing, or destructive command past
  [`hooks/discovery_guard.py`](hooks/discovery_guard.py) when the hook is
  enabled — in any of the four host payload dialects — is a vulnerability.
  Includes path-normalisation tricks around the `contribution-discovery/`
  write boundary and shell-redirection evasion.
- **Prompt injection via the analysed repository.** The skill reads untrusted
  repositories by design. Content in an analysed repository (README, code
  comments, issue text fetched via `gh`) that reliably induces the assistant to
  violate the hard constraints in `SKILL.md` §2 — editing source, pushing,
  posting to GitHub, exfiltrating vulnerability details — is in scope. We know
  instruction-layer defences are probabilistic; reports that demonstrate a
  *reliable* bypass, especially one the hook then fails to catch, are valuable.
- **Script vulnerabilities.** Command or argument injection through repository
  metadata (branch names, remote URLs, file paths, issue titles) into the five
  helper scripts; unsafe file writes outside the output directory; anything
  that makes `collect_repo_metadata.py` or `search_github_candidates.py`
  execute untrusted content.
- **Permission-template holes.** An allow-rule in
  [`hooks/settings.example.json`](hooks/settings.example.json) (or the other
  host example configs) that permits a write or destructive operation it
  claims to deny.

Out of scope: vulnerabilities in the host assistants themselves (report to
Anthropic, GitHub, Cursor, or Google), the model producing a wrong-but-safe
analysis (that is a [run-failure report](CONTRIBUTING.md#what-to-contribute)),
and social-engineering scenarios that require the user to disable the
documented safety layers.

## How to report

**Preferred:** GitHub private vulnerability reporting —
[Report a vulnerability](https://github.com/Phantom-IN/contributor-scout/security/advisories/new).

**Alternative:** email **vaibhav.vanage@gmail.com** with the subject line
`[contributor-scout security]`.

Please include: the host and payload dialect (for hook bypasses), the exact
input or repository content that triggers the issue, what the system did, and
what it should have done. A minimal reproduction repository is the gold
standard.

## What to expect

- **Acknowledgement within 72 hours**, an initial assessment within 7 days.
- Fixes for confirmed hook bypasses and script injection are prioritised ahead
  of all feature work.
- Coordinated disclosure: we will agree a timeline with you before anything is
  published, and credit you in the advisory and changelog unless you prefer
  otherwise.
- There is currently no bug bounty; this is an independent open-source project.
