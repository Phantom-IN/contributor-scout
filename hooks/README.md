# Optional discovery-guard hook

This directory contains an **optional, opt-in** enforcement layer that turns
Contributor Scout's "discovery only" principle into a technical control rather
than relying on prompt compliance alone.

> **Nothing here is installed or activated automatically.** No file in this
> project registers the hook. You must add it to a settings file yourself.

## What it enforces

[`discovery_guard.py`](discovery_guard.py) is a `PreToolUse` hook, usable with
both Claude Code and GitHub Copilot. It reads the tool-call payload on stdin
(either host's shape) and denies:

| Category | Examples |
|---|---|
| Writes outside the output directory | `Write`/`Edit`/`NotebookEdit` (or Copilot's file-edit tools) to any path not under `contribution-discovery/` |
| Git state mutation | `git commit`, `git push`, `git reset --hard`, `git clean -fd`, `git checkout`, `git rebase`, `git merge`, `git stash`, `git add`, branch/tag creation |
| GitHub writes | `gh issue create/comment/close`, `gh pr create/comment/merge/review`, `gh release create`, `gh repo fork/edit`, `gh api` with `POST`/`PUT`/`PATCH`/`DELETE` or a request body |
| Destructive shell | `rm -rf`, `mkfs`, `dd of=`, writes to block devices, `chmod 777`, `curl … \| sh` |
| Shell redirection | `>` or `>>` to a path outside `contribution-discovery/` |

Everything else falls through to the host tool's normal permission handling.

## Trade-off before you enable it

The hook applies to **every** tool call in the session, not just Contributor
Scout's. If you enable it in your user settings, ordinary development in any
project will be blocked from committing, pushing, and editing files. That is
usually not what you want.

**Recommended:** enable it in the *analysed repository's* settings for the
duration of the discovery run, then remove it. Or start a session dedicated to
discovery.

## Installing it - Claude Code

1. Note the absolute path to your Contributor Scout checkout.
2. Open (or create) `.claude/settings.json` in the repository you are analysing.
3. Copy the `hooks` block from [`settings.example.json`](settings.example.json),
   replacing `/ABSOLUTE/PATH/TO/contributor-scout` with the real path.
4. Optionally copy the `permissions` block too - it allowlists the read-only
   commands the skill needs, marks installation and network commands as `ask`,
   and denies the write commands outright. The permission rules and the hook are
   independent; either works alone, and together they overlap deliberately.
5. Restart Claude Code, or run `/hooks` to confirm registration.

## Installing it - GitHub Copilot

1. Note the absolute path to your Contributor Scout checkout.
2. Create `.github/hooks/discovery-guard.json` in the repository you are
   analysing.
3. Copy the contents of
   [`copilot-hooks.example.json`](copilot-hooks.example.json), replacing
   `/ABSOLUTE/PATH/TO/contributor-scout` with the real path.
4. Reload the window, or check the Copilot hooks output for confirmation of
   registration.

> Do not place a real (non-placeholder) copy of this file at `.github/hooks/`
> inside the **contributor-scout checkout itself** - Copilot auto-loads any
> `*.json` file it finds there for that workspace.

Verify it is working:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git commit -m x"},"cwd":"'"$PWD"'"}' \
  | python3 hooks/discovery_guard.py
```

Expected output:

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Contributor Scout is discovery-only: git commit is not permitted during discovery. Blocked command: git commit -m x"}}
```

An allowed call produces no output at all:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git log --oneline -5"},"cwd":"'"$PWD"'"}' \
  | python3 hooks/discovery_guard.py
```

## Removing it

Delete the `hooks` block (or the `.github/hooks/discovery-guard.json` file) you
added and restart/reload. The hook keeps no state and writes nothing.

## Limitations - read these

- **It is defence in depth, not a sandbox.** The Bash rules inspect command text.
  A sufficiently creative command string (unusual quoting, indirection through a
  variable, a wrapper script) can evade it. It complements the skill's
  instructions and the host tool's permission rules; it does not replace either.
- **It fails open.** A malformed payload is allowed through rather than wedging
  the session. A safety net that breaks your session gets disabled, and a
  disabled safety net protects nothing.
- **It does not stop reads.** Reading source, history, and issues is exactly what
  discovery needs.
- **It cannot tell discovery work from ordinary work.** See the trade-off above.
- **Path checks resolve symlinks.** A symlink from inside
  `contribution-discovery/` pointing elsewhere will be denied, which is intended.

## Related

- [`docs/safety-model.md`](../docs/safety-model.md) - the full permission model
- [`skills/contributor-scout/SKILL.md`](../skills/contributor-scout/SKILL.md) §2
  and [`.github/skills/contributor-scout/SKILL.md`](../.github/skills/contributor-scout/SKILL.md) §2
  - the hard constraints this hook mirrors
