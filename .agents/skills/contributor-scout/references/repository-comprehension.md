# Repository Comprehension (Phase 1)

You cannot judge whether a change is a good contribution without knowing what
the project is for, how it is built, and which paths matter. This phase produces
**facts for other reviewers**, not recommendations.

Budget this phase. Depth beats breadth: understanding three subsystems properly
is more useful than skimming thirty.

---

## 1. Purpose and users

- What does the project do, in one paragraph, in the maintainers' own words?
- Who depends on it - end users, library consumers, operators, CI pipelines,
  other projects in the ecosystem?
- Which behaviours are load-bearing? What would a user notice immediately if it
  broke?
- What does the project explicitly say it is **not** for? Read the README's
  non-goals, scope, and "alternatives" sections.

Sources: `README`, docs site, package description, `ROADMAP`, release notes,
the project's own tests (they encode the contract better than prose).

---

## 2. Architecture map

Work from entry points inward.

1. **Entry points.** CLI `main`, HTTP route registration, server bootstrap,
   library public exports, plugin loaders, background workers, scheduled jobs.
   Find them via manifests (`bin`, `scripts`, `entry_points`, `main`) rather
   than guessing.
2. **Module inventory.** For each top-level source directory: responsibility,
   approximate size, key types, and who calls it.
3. **Data flow.** Trace at least two representative requests or invocations end
   to end. Record the actual call chain with `file:line` references.
4. **External systems.** Databases, caches, queues, HTTP clients, filesystem,
   subprocess execution, cloud SDKs, telemetry.
5. **Dependencies.** Direct dependencies that carry real risk or cost
   (parsers, crypto, serialisation, template engines, archive handling,
   network clients).

Record findings in a table:

| Module | Responsibility | Entry from | Depends on | Notes |
|---|---|---|---|---|

---

## 3. Trust boundaries

For the security reviewer, mark where data crosses a trust boundary:

| Boundary | Input source | Trust level | Validation present | Privilege after crossing |
|---|---|---|---|---|

Typical boundaries: network request handlers, CLI argument parsing, file and
archive reading, environment variables, configuration files, plugin and hook
loading, deserialisation, template rendering, subprocess invocation, database
query construction, inter-process and IPC channels, CI workflow inputs.

---

## 4. Interfaces and contracts

- Public API surface (exported symbols, HTTP routes, CLI flags, config keys,
  plugin interfaces) and how stability is signalled (`_private`, `@internal`,
  `unstable`, `experimental`, SemVer policy).
- Authentication and authorisation: where identity is established, where
  permission is checked, and whether those are the same place.
- Storage: schemas, migrations, serialisation formats, on-disk layout.
- Extension points: plugins, hooks, middleware, adapters, custom backends -
  these are where features can often be added without touching core.

Marking the API-stability boundary matters: a change inside a private module is
a far easier contribution than one that alters a public contract.

---

## 5. Critical paths

Identify the paths where security, latency, throughput, memory, reliability, or
compatibility matter most. These are where contributions have the most value and
the most risk.

Evidence for "this path matters":

- it runs on every request, every startup, or every file processed;
- it is covered by benchmarks the project already maintains;
- it appears repeatedly in issue reports;
- it handles untrusted input;
- it is called in a loop over user-scale data;
- `git log` shows it changing often (churn signals importance and risk).

Useful churn probe:

```bash
git log --since='12 months ago' --name-only --pretty=format: \
  | grep -v '^$' | sort | uniq -c | sort -rn | head -30
```

---

## 6. Engineering environment

| Aspect | What to capture |
|---|---|
| Build | Exact command, toolchain versions, generated artefacts |
| Test | Unit, integration, e2e commands; how long they take; what needs network |
| Lint / format | Commands and configuration; auto-fix availability |
| Types / static analysis | mypy, tsc, clippy, go vet, Semgrep, CodeQL if configured |
| Benchmarks | Existing harness, how results are reported, historical baselines |
| CI | Which jobs gate merges; matrix breadth; required checks |
| Release | Versioning scheme, changelog discipline, deprecation policy |

Read what each command does before running it. Record every command you run in
`evidence/commands-run.md`.

---

## 7. Conventions

Contributions that look foreign get rejected on style before they are judged on
merit. Capture:

- naming, file layout, and module boundaries;
- error handling idiom (exceptions vs results, wrapping, logging discipline);
- logging and telemetry conventions;
- test structure, fixtures, naming, and mocking policy;
- documentation and docstring style;
- commit message format and PR title conventions (read the last 30 commits);
- whether comments are sparse or dense - match the surrounding code.

---

## 8. Known limitations and history

- `TODO`, `FIXME`, `XXX`, `HACK`, `NOTE:` comments - grep for them; they are
  maintainer-authored statements of known gaps.
- Documented limitations, caveats sections, and "not supported" notes.
- `CHANGELOG` and release notes: what has the project been prioritising?
- Long-lived design decisions: ADRs, `docs/design/`, RFC directories, wiki.
- Major refactors visible in history (`git log --merges --oneline | head -40`).

---

## Output

`01-architecture-and-context.md` using `templates/architecture-context.md`.

Every architectural claim carries an evidence tag and, where it is about code,
a `file:line` reference verified in this run. Where you are inferring structure
rather than reading it, tag `[INFERENCE]`.

End the document with **Coverage and gaps**: which parts of the repository you
read, which you sampled, and which you did not open at all. Later reviewers must
know the boundaries of this map.
