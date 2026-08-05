# Security Review Playbook (Phase 3a)

The objective is **reachable, materially risky behaviour** - not suspicious
syntax. A dangerous-looking function call is a hypothesis. It becomes a finding
only when you can trace attacker-controlled input to a security impact.

Read `references/responsible-disclosure.md` before writing anything down, and
`references/threat-model-template.md` for the threat-model section format.

---

## Required proof chain

Every finding must complete this chain. If any link is missing, the finding is
not shortlistable.

```text
Attacker-controlled input
        ↓  (where does it enter? who controls it?)
Missing or insufficient validation
        ↓  (what should have stopped it, and why doesn't it?)
Reachable sensitive operation
        ↓  (prove the call path with file:line at each hop)
Security impact
        ↓  (confidentiality, integrity, availability - concretely)
Reproducible conditions and affected configurations
```

Write the chain out explicitly in the candidate. If you cannot name the entry
point, the finding is pattern-matching.

---

## Layer 1 - Attack-surface mapping

Enumerate before analysing. Use Phase 1's trust-boundary table as the starting
point and extend it.

| Surface | Look for |
|---|---|
| Network | HTTP handlers, gRPC services, websockets, listeners, webhook receivers |
| CLI / IPC | Argument parsing, stdin handling, signal handlers, unix sockets |
| File input | Parsers (YAML/XML/JSON/CSV/images), archive extraction, path joining, symlink handling, temp files |
| Serialisation | `pickle`, `yaml.load`, `Marshal`, Java serialisation, `eval`, `Function()`, custom binary decoders |
| Templates | Server-side templates, autoescape configuration, `\|safe` filters, raw HTML sinks |
| Database | Query construction, string interpolation into SQL, ORM `raw`/`extra` escapes |
| Subprocess | `shell=True`, `exec`, `system`, argument arrays built from input, `PATH` handling |
| Outbound requests | URL construction from input (SSRF), redirect following, proxy handling, DNS rebinding surface |
| Auth | Session issuance, token validation, signature verification, comparison functions, expiry handling |
| Authorisation | Object-level checks, tenant isolation, admin gates, IDOR surfaces |
| Crypto | Algorithm choice, key generation, IV/nonce reuse, random source, custom crypto |
| Secrets | Hardcoded credentials, secrets in logs or error messages, `.env` handling, debug endpoints |
| Plugins / extensions | Dynamic import, code loading from config or network, sandbox claims |
| CI / supply chain | `pull_request_target`, untrusted input in workflow expressions, unpinned actions, self-hosted runner exposure, publish steps |
| Update mechanisms | Signature verification, TLS verification, download-and-execute paths |

Record what you examined **and what you did not** - it goes into
`03-review-coverage.md`.

---

## Layer 2 - Trust-boundary analysis

For each boundary crossing:

| Question | Why it matters |
|---|---|
| Where does the data originate? | Determines who the attacker must be |
| What trust does the code assume? | Mismatch between assumption and reality is the bug |
| What validation runs, and is it complete? | Partial validation is the common case |
| Does privilege change at the crossing? | Privilege transitions are where impact escalates |
| Can an attacker realistically control it? | "Admin-only config file" is usually not an attack |

---

## Layer 3 - Vulnerability-class review

Scope this by what the repository actually does. A CLI tool with no network
surface does not need an SSRF pass.

- **Injection** - SQL, NoSQL, command, LDAP, header, log, template.
- **Path traversal** - `../` handling, `os.path.join` with absolute inputs,
  archive extraction (zip-slip, tar-slip), symlink following.
- **Unsafe deserialisation** - `pickle`, unsafe YAML loaders, gadget chains.
- **SSRF** - user-controlled URLs, internal metadata endpoints, redirect chains.
- **Authentication bypass** - missing verification, algorithm confusion,
  non-constant-time comparison, replayable tokens.
- **Authorisation failures** - missing object-level checks, tenant leakage,
  privilege escalation through defaults.
- **Race conditions** - TOCTOU on files, non-atomic check-then-act, unsafe
  concurrent state mutation.
- **Resource exhaustion** - unbounded allocation from input, decompression
  bombs, missing pagination, unbounded recursion, missing timeouts.
- **ReDoS** - catastrophic backtracking on attacker-controlled input.
- **Secret exposure** - logs, errors, stack traces, debug modes, cache files.
- **Insecure temporary files** - predictable names, world-readable modes,
  `mktemp` misuse.
- **Workflow injection** - CI expressions interpolating untrusted PR content.
- **Unsafe defaults** - verification disabled by default, permissive CORS,
  debug-on-by-default, weak default credentials.

---

## Layer 4 - Reachability validation

This is where most candidate security findings die. Do the work.

1. Find every caller of the sink (`grep`, then follow, do not assume).
2. Walk **backwards** to a boundary from Layer 1. Record `file:line` for every
   hop.
3. Enumerate preconditions at each hop: configuration flags, feature gates,
   authentication state, deployment mode, platform, version.
4. Ask what proportion of real deployments satisfy all preconditions.
5. If the path only exists in tests, examples, fixtures, or vendored code, it is
   usually not a finding - say so and reject it.

---

## Layer 5 - Expected-behaviour and mitigation review

Actively look for reasons you are wrong. Check for:

- validation earlier in the chain that you missed (middleware, decorators,
  framework-level escaping, a schema layer);
- sandboxing, container isolation, or dropped privileges that bound the impact;
- a documented threat model that explicitly excludes this attacker
  ("config files are trusted", "the plugin API is arbitrary code by design");
- platform protections (ASLR, read-only filesystems, seccomp);
- whether the "vulnerability" is the documented, intentional feature.

**A documented non-goal is a rejection, not a finding.** Many projects state
plainly that plugins, config files, or local users are trusted. Reporting
arbitrary code execution via a plugin API in such a project wastes maintainer
time and damages credibility.

---

## Confidence levels

| Confidence | Minimum requirement | Shortlist policy |
|---|---|---|
| **Confirmed** | Reproducible with a clear input-to-impact path, demonstrated locally. | Eligible |
| **High** | Strong source evidence; only minor environmental assumptions remain, and they are stated. | Eligible with assumptions stated |
| **Medium** | Plausible, but runtime or deployment assumptions are unresolved. | Research further; normally do not shortlist |
| **Low** | Pattern-based suspicion without validated reachability. | Reject, or retain as a research note only |

---

## Rejection criteria

Reject the candidate when:

- no attacker-controlled input reaches the sink;
- the "attacker" must already have the privilege the attack would grant;
- the behaviour is documented as intentional;
- an existing mitigation already blocks the chain;
- the path exists only in tests, examples, or vendored third-party code;
- an advisory, fix, or open PR already covers it;
- impact is theoretical with no realistic consequence;
- the finding is a dependency CVE with no project-specific reachability analysis
  (report those through the project's dependency-update process instead).

---

## Severity vs contribution suitability

These are two different judgements and must be scored separately.

| | Low severity | High severity |
|---|---|---|
| **Good public PR** | Hardening, defaults, defence in depth | Rare - usually needs coordination first |
| **Private disclosure** | Rarely necessary | The default for anything materially exploitable |

A critical vulnerability can be an excellent disclosure and a terrible public
pull request. Set `PRIVATE_DISCLOSURE` and follow
`references/responsible-disclosure.md`.

---

## Output

One candidate file per finding, `SEC-nnn.md`, using
`templates/security-finding.md`. Include:

- classification, severity reasoning, and confidence;
- affected component, exact source locations, and preconditions;
- the full proof chain with `file:line` at each hop;
- threat model (`references/threat-model-template.md`);
- existing mitigations and honest false-positive analysis;
- related advisories, issues, PRs, introducing commit, and original PR;
- proposed remediation direction, alternatives, compatibility, and required tests;
- disclosure recommendation and unresolved questions.

Do not include working exploit code or a copy-pasteable payload. Describe the
mechanism precisely enough for a maintainer to reproduce, and no further.
