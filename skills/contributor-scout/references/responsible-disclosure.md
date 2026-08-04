# Responsible Disclosure

Security findings are not ordinary contributions. Publishing a working
vulnerability before maintainers can fix it harms users, and a public PR that
"quietly" fixes a security bug is itself a disclosure - the diff tells an
attacker exactly what to exploit in every unpatched deployment.

This document is mandatory reading before writing any security candidate.

---

## 1. Find the disclosure channel first

Before writing a single finding, establish where a report should go:

| Source | What to look for |
|---|---|
| `SECURITY.md`, `.github/SECURITY.md`, `docs/security.md` | The canonical policy: contact, expected response time, supported versions |
| GitHub private vulnerability reporting | `gh api repos/{owner}/{repo} --jq '.security_and_analysis'`, or the Security tab |
| `README` security section | Often the only channel for smaller projects |
| Bug bounty programme | HackerOne, Bugcrowd, or a company security page - has its own rules |
| Foundation policy | CNCF, Apache, Eclipse, PSF projects route through the foundation |
| `MAINTAINERS`, `CODEOWNERS` | Fallback contact where no policy exists |

Record the channel (or its absence) in `00-repository-profile.md`. It is a
Phase 0 output, not something to discover after finding a vulnerability.

**If no policy exists:** recommend a private route anyway - GitHub private
vulnerability reporting if enabled, otherwise a direct maintainer email from
commit history. Do **not** default to opening a public issue. Note in the
candidate that the absence of a policy is itself worth raising with maintainers,
separately and non-urgently.

---

## 2. Decide the route

| Finding characteristic | Route |
|---|---|
| Remotely exploitable with meaningful impact | `PRIVATE_DISCLOSURE` |
| Authentication or authorisation bypass | `PRIVATE_DISCLOSURE` |
| Data exposure, secret leakage, privilege escalation | `PRIVATE_DISCLOSURE` |
| Injection or RCE reachable from untrusted input | `PRIVATE_DISCLOSURE` |
| Denial of service reachable by an unauthenticated actor | `PRIVATE_DISCLOSURE` |
| Hardening with no known exploit path | Normal public contribution |
| Insecure default with documented risk already known | Normal public contribution, referencing the existing discussion |
| Defence in depth on an already-mitigated path | Normal public contribution |
| Dependency CVE with no project-specific reachability | Normal dependency-update process |
| The behaviour is a documented, intentional trust boundary | Not a finding |

When uncertain, choose `PRIVATE_DISCLOSURE`. The cost of a private report that
turns out to be low severity is a small amount of maintainer time. The cost of
a public disclosure of a real vulnerability is borne by every user.

---

## 3. What goes in the report - and what does not

**Include:**

- affected component, version range, and configuration preconditions;
- the vulnerability class and root cause;
- the input-to-impact chain at a level a maintainer can follow and verify;
- impact assessment and realistic attacker model;
- existing mitigations and honest false-positive analysis;
- suggested remediation direction;
- your proposed disclosure timeline and willingness to help.

**Exclude from any artefact that could be shared publicly:**

- working exploit code or copy-pasteable payloads;
- a weaponised proof of concept;
- reconnaissance of live third-party deployments;
- any testing against systems you do not own.

Never test a suspected vulnerability against a production instance operated by
someone else. Local reproduction against a checkout you control only.

---

## 4. Handling `PRIVATE_DISCLOSURE` candidates in the output

1. The candidate file (`SEC-nnn.md`) is written to
   `contribution-discovery/candidates/` like any other, with disposition
   `PRIVATE_DISCLOSURE` at the top and a clear handling banner.
2. The candidate contains the mechanism, not a weaponised exploit.
3. `05-final-recommendation.md` names the candidate and its severity band but
   **must not** restate the vulnerable path in detail. It says: "see
   `candidates/SEC-001.md`, handle privately".
4. `machine-readable/candidates.json` includes the ID, category, disposition,
   and score, but not the technical detail.
5. Tell the user explicitly, in the completion summary, that
   `contribution-discovery/` now contains sensitive material and should not be
   committed to a public repository or pasted into a public issue.

---

## 5. Severity is not contribution suitability

Score these separately and say both:

| | Contribution score (this system) | Security severity (CVSS-style reasoning) |
|---|---|---|
| Measures | Likelihood the *public contribution* succeeds | How bad the issue is for users |
| Low + High | Do not open a PR; disclose privately | Still urgent |
| High + Low | A fine public hardening PR | Not urgent |

A critical vulnerability scoring 30 on the contribution rubric is not a
contradiction. It means: report it privately, do not open a pull request.

---

## 6. Coordination before implementation

For any `PRIVATE_DISCLOSURE` candidate, the correct next action is
**contact the maintainers first**, never "write the patch and open a PR".

Reasons a fix must be coordinated:

- maintainers may want to bundle it into a coordinated release;
- they may need to request a CVE and prepare an advisory;
- they may need to backport across supported branches;
- a public PR would disclose the issue before users can patch;
- they may already know and be working on it privately.

Offer the patch privately. Let maintainers choose the timing and the mechanism.

---

## 7. Suggested private report structure

Keep it to one page. Maintainers are usually volunteers.

```text
Subject: Security report - <component> - <class> (<project>)

Summary:      One or two sentences.
Affected:     Versions / configurations / platforms.
Preconditions:What an attacker needs.
Impact:       Concrete consequence.
Details:      Root cause and the input-to-impact chain, with file references.
Reproduction: Minimal steps against a local checkout.
Mitigation:   Suggested direction; note if you can supply a patch privately.
Disclosure:   Your proposed timeline, and a statement that you will follow
              the project's policy.
Contact:      How to reach you.
```

Default to the project's stated timeline. Where none exists, 90 days is the
common industry norm, and it is a starting point for discussion, not an
ultimatum. Be explicit that you will not publish before coordinating.

---

## 8. Hard rules for this skill

- Never open a public issue or PR for a `PRIVATE_DISCLOSURE` candidate. The skill
  cannot open either in any case - but neither may it *recommend* one.
- Never include a weaponised exploit in any generated document.
- Never test against infrastructure you do not own.
- Never claim a CVE-worthy severity without the reachability analysis to support
  it.
- Always state when a finding is `Low` or `Medium` confidence - inflated security
  claims are the fastest way to lose a maintainer's trust permanently.
- Always tell the user when the output directory contains sensitive findings.
