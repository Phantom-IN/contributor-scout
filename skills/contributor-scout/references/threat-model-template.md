# Threat Model Template

Use this structure for the threat-model section of every security candidate. It
forces the analysis that separates a finding from a pattern match.

Copy the blocks below into `SEC-nnn.md` and fill them in. Delete nothing - an
empty section is a signal that the analysis is incomplete.

---

## Asset

What is being protected, and why it matters to this project's users.

```text
Asset:            <e.g. user session tokens stored in the local keyring>
Value to attacker:<e.g. account takeover across all connected services>
Owner:            <who is harmed - end user, operator, downstream consumer>
```

---

## Attacker model

Be specific. "An attacker" is not an attacker model.

| Question | Answer |
|---|---|
| Who is the attacker? | Unauthenticated remote / authenticated user / co-tenant / local user / malicious dependency / malicious repository contributor / CI actor |
| What access do they start with? | |
| What can they control? | Exact inputs, fields, headers, filenames, config keys |
| What can they observe? | Timing, error messages, logs, side channels |
| What is out of scope? | Per the project's documented trust assumptions |

**Privilege test:** does the attack require privilege that already implies the
resulting impact? If an attacker must be an admin to gain admin capability, this
is not a vulnerability. State the answer explicitly.

---

## Trust boundary crossed

```text
From:       <untrusted zone - e.g. public HTTP request>
To:         <trusted zone - e.g. filesystem write with service privileges>
Crossing:   <file:line where the boundary is crossed>
Assumed:    <what the code assumes about the data at this point>
Actual:     <what an attacker can actually supply>
```

---

## Attack path

Every hop with a verified `file:line`. No gaps, no "presumably".

| Step | Location | What happens | Evidence |
|---|---|---|---|
| 1. Entry | `path:line` | Attacker supplies `<input>` | `[CODE]` |
| 2. Propagation | `path:line` | Value passed unvalidated to `<callee>` | `[CODE]` |
| 3. Missing control | `path:line` | Expected `<validation>` is absent | `[CODE]` |
| 4. Sink | `path:line` | `<sensitive operation>` executes with attacker data | `[CODE]` |
| 5. Impact | - | `<concrete consequence>` | `[CODE]` / `[TEST]` |

---

## Preconditions

Everything that must be true for the attack to work. Then estimate how common
that combination is in real deployments.

```text
- [ ] Configuration:   <flag / setting / non-default option>
- [ ] Deployment:      <mode, platform, container, privilege level>
- [ ] Version:         <affected range>
- [ ] Authentication:  <state required>
- [ ] Timing / race:   <window, if applicable>

Prevalence in real deployments: <high / moderate / rare> - <reasoning>
```

---

## Impact

Map to concrete consequences, not adjectives.

| Dimension | Effect |
|---|---|
| Confidentiality | |
| Integrity | |
| Availability | |
| Scope / blast radius | Single user / all users of an instance / all instances |
| Persistence | One-off / persistent / self-propagating |

---

## Existing mitigations

What already reduces the risk, and by how much. Look hard - this is where most
findings are correctly killed.

| Mitigation | Location | Effect | Bypassable? |
|---|---|---|---|

---

## False-positive analysis

Argue against your own finding. Then say why the finding survives - or reject it.

```text
Reasons this may not be a real vulnerability:
1. <e.g. framework-level escaping may already neutralise this>
2. <e.g. the documented threat model treats config files as trusted>
3. <e.g. the path may be unreachable in supported configurations>

Why it survives (or does not):
<reasoning, with evidence>
```

---

## Severity reasoning

State the severity band and the reasoning. If using CVSS, give the vector and
say it is an estimate; do not present a computed score as authoritative.

```text
Severity band:   Critical / High / Medium / Low
Reasoning:       <attacker model + preconditions + impact + prevalence>
CVSS (estimate): <vector, optional> - estimate only, not an assigned score
```

---

## Disclosure recommendation

```text
Route:           PRIVATE_DISCLOSURE / public contribution / not a finding
Channel:         <from SECURITY.md, or the fallback identified in Phase 0>
Rationale:       <why this route>
Public artefact: <what may appear in a public issue or PR, if anything>
```

See `references/responsible-disclosure.md` for the routing rules.
