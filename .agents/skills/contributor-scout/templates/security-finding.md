<!--
SECURITY CANDIDATE TEMPLATE - Contributor Scout

Extends templates/candidate-finding.md. Every heading from the canonical
template must be present, plus the security-specific sections below.

HANDLING: if disposition is PRIVATE_DISCLOSURE, this file contains sensitive
material. It must not be committed to a public repository, pasted into a public
issue, or included verbatim in 05-final-recommendation.md.

Never include a weaponised exploit. Describe the mechanism precisely enough for
a maintainer to reproduce locally, and no further.
-->

# SEC-<nnn>: <Vulnerability class> in <component>

> **HANDLING: <PUBLIC CONTRIBUTION | PRIVATE DISCLOSURE - DO NOT PUBLISH>**
> <If private: this document must be shared only through the channel named in
> "Disclosure recommendation".>

| Field | Value |
|---|---|
| Candidate ID | `SEC-<nnn>` |
| Category | `security` |
| Vulnerability class | `<CWE-nnn / class name>` |
| Repository | `<owner/name>` |
| Analysed at commit | `<short SHA>` on `<branch>` |
| Generated | `<YYYY-MM-DD>` |

## Classification and disposition

- **Disposition:** `PRIVATE_DISCLOSURE` / `SHORTLIST` / `NEEDS_MAINTAINER_INPUT` / `HOLD` / `REJECT`
- **Category:** security
- **Vulnerability class:** <e.g. path traversal (CWE-22)>
- **Severity band:** `Critical` / `High` / `Medium` / `Low` - <one line of reasoning>
- **Security confidence:** `Confirmed` / `High` / `Medium` / `Low`
- **Contribution score:** `<nn>`/100 - band `<band>`
- **Affected component:** `<module>`

> Severity and contribution suitability are separate. A critical finding may
> score low as a *public contribution* because private disclosure is the correct
> route.

## Executive summary

<Two to four sentences: the class, where, who can trigger it, and the impact.>

## Project and user impact

- **Who is affected:** <deployments/configurations>
- **Attacker model:** <unauthenticated remote / authenticated user / local / co-tenant / CI actor>
- **Preconditions:** <what must be true>
- **Concrete consequence:** <confidentiality / integrity / availability effect>
- **Prevalence of the vulnerable configuration:** <high / moderate / rare> - <reasoning>

## Threat model

<Complete `references/threat-model-template.md` here: asset, attacker model,
trust boundary crossed, attack path table, preconditions, impact, existing
mitigations, false-positive analysis, severity reasoning.>

## Affected components and exact source locations

| Location | Role | Evidence |
|---|---|---|
| `path:line` | entry point | `[CODE]` |
| `path:line` | missing validation | `[CODE]` |
| `path:line` | sink | `[CODE]` |

## Current behaviour

<Factual description of the code path as it exists, with citations.>

## Expected behaviour

<What a secure implementation would do, and the basis: project docs, a similar
guard elsewhere in the codebase, a framework convention, or a standard.>

## Root cause or capability gap

<The single underlying defect: a missing check, a wrong trust assumption, an
unsafe default, an incorrect API usage.>

## Proof chain

```text
Attacker-controlled input   -> <what and where, file:line>
Missing/insufficient control-> <what should stop it, file:line>
Reachable sensitive op      -> <the sink, file:line>
Security impact             -> <concrete consequence>
Conditions                  -> <configuration, version, platform>
```

Every hop must carry a `file:line` verified in this run. A gap here means the
finding is not shortlistable.

## Evidence

| # | Claim | Tag | Source |
|---|---|---|---|

## Reproduction, benchmark, or demand evidence

<Minimal local reproduction: setup, the shape of the input, the observed effect.
Mechanism only - no weaponised payload. State clearly that reproduction was
performed only against a local checkout.>

## Existing mitigations and false-positive analysis

**Existing mitigations**

| Mitigation | Location | Effect | Bypassable? |
|---|---|---|---|

**Why this might not be a real vulnerability**

1. <framework-level protection that may already neutralise it>
2. <documented trust assumption that may exclude this attacker>
3. <reachability doubt>

**Why it survives**

<Reasoning with evidence.>

## Related issues, PRs, discussions, and recent commits

| Type | Ref | Title | State | Relationship |
|---|---|---|---|---|

Also checked: published security advisories (`gh api repos/{o}/{r}/security-advisories`),
`CHANGELOG` security entries, and dependency advisories.

## Introducing commit and original PR

- **Introducing commit:** `<sha>` - <subject> (<date>) `[HISTORY]`
- **Introducing PR:** #<n>, or `not identified`
- **Original objective:** <what it was solving>

## Historical design constraints

<Why the original implementation was reasonable then. No blame.>

## Changed assumptions

| Assumption at introduction | Evidence | Still true? | What changed |
|---|---|---|---|

## Proposed solution direction

<Remediation direction. Prefer the project's existing validation or sanitisation
utilities over a new mechanism. Note defence-in-depth options separately from the
primary fix.>

## Alternative solutions considered

| Alternative | Pros | Cons | Why not chosen |
|---|---|---|---|

## Minimum PR scope

<Only if the route is a public contribution. For `PRIVATE_DISCLOSURE`, write:
"Not applicable - coordinate with maintainers before any patch is proposed.">

## Optional follow-ups

<Hardening beyond the immediate fix.>

## Explicit exclusions

<Adjacent hardening, unrelated validation, refactors. Security PRs must be
minimal and reviewable.>

## Backward compatibility and maintenance cost

- **Behaviour change:** <what previously-accepted input would now be rejected>
- **Risk of breaking legitimate use:** <assessment>
- **Public API impact:** <none / additive / breaking>
- **Ongoing cost:** <new validation surface, tests>

## Required tests and documentation

| Test | Type | What it proves |
|---|---|---|
| <name> | regression | The malicious input is now rejected |
| <name> | regression | Legitimate input still works |

- **Documentation impact:** <security docs, configuration notes>
- **Advisory / changelog:** <does this warrant an advisory entry?>

## Maintainer-facing pitch

<For private disclosure, use the report structure in
`references/responsible-disclosure.md` §7 instead of a PR-style pitch.>

## Duplicate status and confidence

- **Status:** `<status>`
- **Duplicate-detection confidence:** `HIGH` / `MEDIUM` / `LOW`
- **Advisories checked:** yes/no
- **Query variants run:** <list>
- **Reasoning:** <why>

## Overall score

<Table from templates/candidate-finding.md, produced by
`scripts/calculate_candidate_score.py`.>

## Confidence

- **Security confidence:** `Confirmed` / `High` / `Medium` / `Low`
- **What would raise it:** <specific action>
- **What would falsify it:** <specific observation>

## Disclosure recommendation

- **Route:** `PRIVATE_DISCLOSURE` / public contribution / not a finding
- **Channel:** <from SECURITY.md, GitHub private reporting, maintainer contact>
- **Rationale:** <why this route>
- **Proposed timeline:** <project policy, or 90 days as a starting point>
- **What may appear publicly:** <nothing / a generic hardening description>
- **Coordination needed before implementation:** yes/no - <why>

## Recommended next action

<e.g. "Report privately via security@example.org using the structure in
references/responsible-disclosure.md §7. Do not open an issue or PR. Offer a
patch privately once maintainers respond.">

## Open questions

| # | Question | Who can answer | What it blocks |
|---|---|---|---|

## Rejection conditions

- <e.g. a guard is found upstream of the sink>
- <e.g. maintainers state the input is trusted by design>
- <e.g. an advisory shows this is already fixed in an unreleased branch>
