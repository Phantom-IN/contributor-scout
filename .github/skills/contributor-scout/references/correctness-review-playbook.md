# Correctness Review Playbook (Phase 3d)

The objective is a **bug a user actually hits**: wrong output, a crash, a step
that fails, an install that breaks. Correctness fixes are often the most
mergeable contributions a newcomer can make - small, testable, and wanted by
every maintainer - but only when the bug is reproduced, not imagined.

> **Hard rule:** no correctness candidate is shortlisted without a `[TEST]`
> reproduction: a command, input, or step that produced the wrong result in this
> run, recorded in `evidence/commands-run.md`. "This looks like it could fail"
> is `[INFERENCE]` and stays `HOLD`.

---

## Required proof chain

```text
Observed failure
        ↓  (exact input or step, observed vs expected output)
Reproduction on the current default branch
        ↓  (recorded command; still fails today)
Root cause
        ↓  (file:line - the one decision that produces the wrong result)
Scope of the failure
        ↓  (which inputs, platforms, or configurations; how common)
Minimal fix direction
        ↓  (smallest change that corrects it)
Regression probes
           (what must keep working - see the candidate template)
```

---

## Source 1 - Dogfood the project (approval-gated)

The most convincing bugs come from using the software the way its README says
to. Static reading finds what code *could* do; running it finds what users
*hit*.

**Ask the user first.** Dogfooding builds images, installs dependencies, or
starts services - exactly what the hard constraints forbid without explicit
approval. Show the commands you intend to run and wait for a yes. If the user
declines, mark the source "approval declined" in `03-review-coverage.md`.

Then follow the documented path, and nothing more exotic:

1. **Install** exactly as the README or install script says. Note every step
   that fails, needs an undocumented prerequisite, or prints a misleading error.
2. **First run** - setup wizard, first login, default configuration.
3. **One core workflow** end to end, with the smallest realistic input (a local
   test target, a sample file, the project's own example config).
4. **Read the logs** while it runs. A warning or "could not parse" line on the
   happy path is often the finding.

Record each friction point as it happens - command, output, what was expected -
before moving on. Keep everything the run creates out of the analysed
repository's tracked files (use the discovery directory or a scratch path), and
stop anything you started when the run ends.

Typical findings: an install script that does not check a prerequisite the
build needs; free-text input that a parser rejects for ordinary punctuation; a
"test connection" button that reports success on a wrong reply; an error
message that names the wrong cause.

## Source 2 - Fresh bug reports nobody has answered

```bash
gh issue list --state open --label bug --limit 40 --json number,title,createdAt,comments
gh issue list --state open --limit 40 --search "sort:created-desc" --json number,title,createdAt,comments
```

A recent, well-written report with no maintainer reply and no linked PR is open
ground. Reproduce it locally before anything else: a report you can reproduce
and root-cause in the same day is a strong candidate; one you cannot reproduce
is a comment on the issue at most, never a PR.

## Source 3 - Error paths and boundary inputs

Read the parsers, validators, and normalisers on the critical paths found in
Phase 1. For each, list the inputs real users produce that tests do not cover:

- trailing or leading punctuation, whitespace, mixed case;
- empty, very long, Unicode, and full-width characters;
- IPv6 and bracketed hosts, ports, user-info in URLs;
- platform differences (paths, line endings, file modes, missing loopback
  aliases on macOS, case-insensitive filesystems).

A boundary that is mishandled is only a candidate once a `[TEST]` shows the
wrong result.

## Source 4 - Install, upgrade, and migration scripts

Shell installers and upgrade scripts are rarely covered by tests and run on
every new deployment. Check prerequisites they assume, error handling under
`set -e`, and what happens on a second run or when the user answers "no".

---

## Rejection criteria

Reject (with a `REJECTED-nnn.md`) when:

- the failure only reproduces in a non-standard setup the project explicitly
  does not support;
- the reproduction depends on the user's own environment (a blocked network, a
  misconfigured host) rather than the project - say so on the issue instead;
- the "wrong" behaviour is documented as intended, or a maintainer has said so;
- an open PR already fixes it (`CLAIMED`), or the fix is in an unreleased
  commit on the default branch;
- the fix sits in a contended file and the conflicting PRs make it moot.

---

## Output

Write each candidate as `candidates/BUG-nnn.md` from
`templates/candidate-finding.md`, category `correctness`. Fill "Reproduction,
benchmark, or demand evidence" with the exact reproduction and "Regression
probes" with the inputs that must keep working. Record every source you
examined - including a declined dogfood run - in the correctness coverage table
of `03-review-coverage.md`.
