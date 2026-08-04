**CONTRIBUTOR SCOUT**

**AI-Assisted Open-Source Contribution Discovery System**

A structured, evidence-first framework for identifying security fixes, performance improvements, and roadmap-aligned features before implementation.

| **DISCOVER** | **VALIDATE** | **HAND OFF** |
|---|---|---|
| Understand the repository and identify contribution opportunities. | Prove impact, non-duplication, project alignment, and historical context. | Generate implementation-ready discovery dossiers without changing code. |

**Prepared for**

Internal Team Review and Implementation Planning

**Prepared by**

Vaibhav Vanage

**Document date**

28 July 2026

# Document Purpose and Control

This document defines the proposed design, governance model, workflows, outputs, and delivery roadmap for Contributor Scout. It is intended to be forwarded directly to engineering, security, developer-experience, and open-source contributors for review and implementation planning.

| **Field**              | **Value**                                                                        |
|------------------------|----------------------------------------------------------------------------------|
| Document type          | Solution proposal and implementation plan                                        |
| Proposed system        | Contributor Scout                                                                |
| Primary interface      | Claude Code skill, supported by specialised subagents and deterministic scripts  |
| Initial operating mode | Read-only discovery and documentation                                            |
| Primary users          | Engineers contributing to third-party open-source repositories                   |
| Decision requested     | Approve V1 scope, select pilot repositories, and assign implementation ownership |
| Version                | 1.0                                                                              |
| Status                 | Ready for team review                                                            |

# Contents

1. Executive Summary
2. Background and Problem Statement
3. Vision, Objectives, and Non-Goals
4. Design Principles
5. Proposed Architecture
6. End-to-End Operating Workflow
7. Repository Eligibility and Intelligence
8. Duplicate and Existing-Work Detection
9. Security Contribution Discovery
10. Performance Contribution Discovery
11. Feature Contribution Discovery
12. Git History and Maintainer-Intent Analysis
13. Candidate Validation and Ranking
14. Discovery Documents and Output Contract
15. Claude Code Skill and Agent Design
16. Permissions, Safety, and Responsible Disclosure
17. Human Review and Implementation Handoff
18. Delivery Roadmap
19. Evaluation Framework and Success Metrics
20. Risks and Mitigations
21. Team Operating Model
22. Recommended Pilot
23. Decisions Required

# 1. Executive Summary

Contributor Scout is a proposed AI-assisted system for discovering high-quality open-source contribution opportunities before any code is written. It will be implemented initially as a Claude Code skill and supporting subagents. A user will clone a target repository, invoke the system, and receive evidence-backed discovery documents covering three contribution categories: security fixes, performance improvements, and new or extended features.

The system is deliberately not an autonomous code generator. Its purpose is to reduce the most expensive and failure-prone part of open-source contribution: deciding what is worth contributing, proving that the opportunity is real, confirming that it is not duplicate work, understanding why the current code exists, and building a convincing maintainer-facing case for change.

> **Core proposition**
>
> Contributor Scout should be rewarded for rejecting weak ideas, not for producing the largest number of findings. A successful run may conclude that no contribution currently meets the required evidence, alignment, and non-duplication threshold.

## Expected outcome

- **Higher acceptance probability:** Proposals are aligned with project scope, maintainer intent, current roadmap, and repository conventions before implementation begins.

- **Lower duplication risk:** Current issues, pull requests, discussions, recent commits, and historical decisions are checked using semantic and exact searches.

- **Stronger technical justification:** Every shortlisted candidate includes source evidence, impact reasoning, history, alternatives, tests, compatibility analysis, and a maintainer-facing pitch.

- **Safer security research:** Potential vulnerabilities follow the repository’s disclosure policy and are separated from normal public contribution workflows.

- **More efficient use of AI:** Claude performs repository analysis and structured reasoning, while scripts handle repeatable data collection, scoring, and report validation.

## Proposed delivery model

```text
Repository clone
        ↓
Contributor Scout orchestrator
        ↓
Repository intelligence and existing-work map
        ↓
Security reviewer | Performance reviewer | Feature scout
        ↓
Duplicate and history validator
        ↓
Adversarial candidate validation and ranking
        ↓
Human-approved discovery dossier
        ↓
Separate implementation workflow
```

## Recommended initial decision

Approve a constrained V1 consisting of one orchestrator skill, three review playbooks, GitHub CLI integration, Git history analysis, standard report templates, and a manual approval gate. Pilot the system on three active repositories before adding autonomous subagents or broad static-analysis integrations.

# 2. Background and Problem Statement

## Why open-source contribution discovery is difficult

Writing code is only one part of a successful open-source contribution. The more difficult step is finding a change that is technically valid, valuable to users, aligned with project direction, small enough to review, and not already being addressed. AI code assistants can generate patches quickly, but without disciplined discovery they can also produce duplicate, low-impact, historically uninformed, or maintainership-heavy pull requests.

| **Common failure**      | **Why it happens**                                                                                           | **Impact on maintainers**                                                  |
|-------------------------|--------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| Duplicate contribution  | Only issue titles are searched; draft PRs, discussions, synonyms, and recent commits are missed.             | Maintainer time is wasted reviewing work that already exists.              |
| False security finding  | A dangerous-looking pattern is reported without reachability, threat model, or existing mitigation analysis. | Noise, reputational damage, or accidental public disclosure.               |
| Unmeasured optimisation | Code appears inefficient, but the path is not important or no benchmark proves meaningful impact.            | Complexity increases with little user benefit.                             |
| Random feature proposal | The AI infers a capability gap without confirming user demand, roadmap alignment, or maintenance cost.       | Scope creep and long-term support burden.                                  |
| Historically naive fix  | The proposed change ignores why the original implementation was chosen.                                      | The patch reintroduces previously solved problems or violates constraints. |
| Oversized first PR      | Unrelated refactors, dependency upgrades, and API changes are bundled into one contribution.                 | Review becomes slow and rejection becomes more likely.                     |

## Opportunity created by Claude Code

Claude Code can inspect a full repository, follow references across files, run commands, use Git history, query GitHub through the command-line interface, and produce structured documents. The opportunity is to codify a repeatable contribution-discovery method around those capabilities rather than allowing each engineer to improvise prompts for every repository.

## Problem statement

> **Problem to solve**
>
> How can we use AI to systematically identify high-value, non-duplicate, maintainer-aligned open-source contributions and generate implementation-ready evidence, while preserving human judgement and avoiding premature code changes?

# 3. Vision, Objectives, and Non-Goals

## Vision

Create a reusable contribution-intelligence layer that helps engineers move from “I want to contribute to this repository” to “this is the strongest contribution opportunity, this is why it matters, this is why it is not duplicate work, and this is how we should approach maintainers.”

## Primary objectives

1. Understand the target repository before producing findings.

2. Identify credible opportunities in security, performance, and feature development.

3. Check current issues, pull requests, discussions, roadmap items, and recent commits for overlap.

4. Trace the code’s historical origin and identify the pull request or design rationale that introduced the behaviour.

5. Generate a defensible contribution dossier with evidence, alternatives, tests, risks, and maintainer-facing justification.

6. Rank candidates by expected contribution success, not only technical severity.

7. Stop before implementation and require explicit human approval.

## Non-goals for V1

- Automatically editing project source code.

- Opening issues, comments, branches, commits, or pull requests.

- Publishing sensitive vulnerability details.

- Replacing the engineer’s responsibility to understand and defend a contribution.

- Guaranteeing maintainer acceptance.

- Running arbitrary installation or build scripts without approval.

- Performing exhaustive formal verification of an entire repository.

- Generating large speculative feature roadmaps for projects that have not requested them.

# 4. Design Principles

| **Principle**                                | **Meaning in the system**                                                                                               |
|----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Evidence before recommendation               | A code pattern is a hypothesis until reachability, impact, context, and existing work are verified.                     |
| Discovery and implementation are separate    | The first workflow generates documents only. A different workflow implements an approved candidate.                     |
| One strong candidate beats ten weak findings | The system should narrow aggressively and may recommend no contribution.                                                |
| Maintainer context is a first-class input    | Roadmaps, contribution guides, discussions, rejected proposals, and historical PR comments influence ranking.           |
| History is explanation, not blame            | The introducing commit is analysed to understand past constraints and frame a respectful change proposal.               |
| Smallest acceptable PR                       | Each proposal defines minimum scope, optional follow-ups, and explicit exclusions.                                      |
| Deterministic work belongs in scripts        | Metadata collection, scoring, schema validation, and repeated searches should not rely entirely on model improvisation. |
| Read-only by default                         | The discovery process has narrow permissions and cannot mutate the repository or remote platform.                       |
| Uncertainty must be visible                  | Claims are labelled by evidence source and confidence; missing remote access lowers duplicate-detection confidence.     |

# 5. Proposed Architecture

## Logical architecture

```text
┌──────────────────────────────────────────────┐
│ Contributor Scout Orchestrator Skill │
└──────────────────────┬───────────────────────┘
│
┌──────────────────────▼───────────────────────┐
│ Repository Intelligence Agent │
│ Scope, architecture, policies, critical paths│
└──────────────────────┬───────────────────────┘
│
┌──────────────┼──────────────┐
│ │ │
┌───────▼───────┐ ┌────▼────────┐ ┌──▼────────────┐
│ Security │ │ Performance │ │ Feature Scout │
│ Reviewer │ │ Reviewer │ │ │
└───────┬───────┘ └────┬────────┘ └──┬────────────┘
└──────────────┼──────────────┘
│
┌──────────────────────▼───────────────────────┐
│ Duplicate and History Validator │
└──────────────────────┬───────────────────────┘
│
┌──────────────────────▼───────────────────────┐
│ Adversarial Validator and Contribution Ranker│
└──────────────────────┬───────────────────────┘
│
┌──────────────────────▼───────────────────────┐
│ Discovery Documents and Human Approval Gate │
└──────────────────────────────────────────────┘
```

## Why a multi-agent design

A single, very large skill prompt would mix repository comprehension, security analysis, performance reasoning, product judgement, Git history, duplicate detection, and report writing in one context. That increases inconsistency and makes it difficult to assign specialised tools and permissions. The recommended design uses one orchestrator plus narrowly defined reviewers. Each reviewer produces hypotheses; the validation layer tries to disprove them before ranking.

## Core components

| **Component**                   | **Responsibility**                                                                         | **Primary output**                       |
|---------------------------------|--------------------------------------------------------------------------------------------|------------------------------------------|
| Orchestrator skill              | Controls stages, enforces gates, delegates work, and stops before implementation.          | Run manifest and final report            |
| Repository intelligence agent   | Builds architecture, policy, lifecycle, and critical-path context.                         | Repository profile and architecture map  |
| Security reviewer               | Finds reachable security weaknesses with threat models and disclosure guidance.            | Security candidate reports               |
| Performance reviewer            | Finds measurable bottlenecks and designs benchmarks.                                       | Performance candidate reports            |
| Feature scout                   | Finds demand-backed, scope-aligned feature opportunities.                                  | Feature candidate reports                |
| Duplicate and history validator | Searches issues, PRs, discussions, recent commits, blame, and introducing PRs.             | Existing-work map and historical context |
| Adversarial validator           | Attempts to falsify each candidate and assigns a disposition.                              | Validation verdicts                      |
| Contribution ranker             | Scores candidates by expected acceptance and implementation quality.                       | Shortlist and primary recommendation     |
| Deterministic scripts           | Collect metadata, normalise GitHub results, calculate scores, and validate report schemas. | JSON evidence and quality checks         |

# 6. End-to-End Operating Workflow

1. The engineer selects and clones an active open-source repository.

2. Contributor Scout verifies the repository root, local status, remote origin, and available GitHub authentication.

3. A repository eligibility assessment decides whether the project is worth further investment.

4. The repository intelligence stage maps purpose, architecture, policies, critical paths, and development commands.

5. An initial existing-work map collects issues, pull requests, discussions, roadmap items, TODOs, and recent changes.

6. Security, performance, and feature reviewers independently generate raw candidates.

7. Promising candidates undergo Git history analysis to locate introducing commits, related pull requests, and original design constraints.

8. The duplicate validator performs a second, candidate-specific search using symptoms, components, function names, errors, synonyms, and proposed solutions.

9. The adversarial validator tries to disprove each candidate by checking reachability, impact, expected behaviour, mitigation, alignment, and feasibility.

10. The contribution ranker scores survivors and selects no more than three final candidates, with one recommended primary candidate.

11. The system writes all discovery artefacts under a dedicated output directory and stops without modifying source code.

12. A human reviews the dossier, rechecks current remote activity, and decides whether to implement, discuss, disclose privately, hold, or reject the opportunity.

## Stage gates

| **Gate**        | **Question**                                                                   | **Possible outcome**                                                        |
|-----------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Repository gate | Is this project active, contribution-friendly, and compatible with our skills? | Proceed, proceed with limitations, or do not invest                         |
| Finding gate    | Does the problem or opportunity actually exist?                                | Retain as hypothesis or reject                                              |
| Impact gate     | Does it matter to users, maintainers, cost, reliability, or security?          | Continue or reject as low value                                             |
| Duplicate gate  | Is someone already working on the same problem or solution?                    | Clear, related, partially covered, claimed, duplicate, rejected, or unknown |
| Alignment gate  | Does the proposal fit project scope and maintainer direction?                  | Implement, discuss first, hold, or reject                                   |
| Safety gate     | Does the finding require private security disclosure?                          | Private disclosure workflow or normal contribution workflow                 |
| Human gate      | Can the engineer personally explain and defend the proposal?                   | Approve implementation or return for more research                          |

# 7. Repository Eligibility and Intelligence

## Repository eligibility assessment

The system should avoid spending significant review effort on repositories that are archived, inactive, hostile to external contributions, undergoing a complete rewrite, or impossible to build locally. The first stage therefore produces a repository viability decision.

| **Positive signals**                               | **Negative signals**                                     |
|----------------------------------------------------|----------------------------------------------------------|
| Recent commits, releases, and maintainer responses | Archived repository, mirror, or no meaningful activity   |
| External pull requests are reviewed and merged     | Open pull requests remain untouched for long periods     |
| Clear CONTRIBUTING and SECURITY policies           | No development setup or unclear contribution route       |
| Tests and CI can be run locally                    | Main branch is consistently broken                       |
| Roadmap, help-wanted, or good-first-issue signals  | Maintainers explicitly reject external feature proposals |
| Project scope matches contributor expertise        | Mandatory legal or CLA constraints cannot be satisfied   |

## Required repository reading

- README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CHANGELOG, ROADMAP, and architectural documentation.

- Package manifests, lockfiles, build scripts, test configuration, CI workflows, issue templates, and pull-request templates.

- Primary entry points, public APIs, storage boundaries, network interfaces, authentication flows, plugin systems, and extension points.

- Recent Git history, releases, tags, contributor activity, and repeated areas of change.

## Repository intelligence output

- **Purpose and users:** What the project does, who depends on it, and which behaviours are central.

- **Architecture:** Major modules, data flow, trust boundaries, critical dependencies, and test structure.

- **Contribution environment:** Build, test, lint, benchmark, and static-analysis commands.

- **Maintainer preferences:** Documented scope, non-goals, accepted design patterns, and rejected directions.

- **Critical paths:** Code paths where security, latency, throughput, memory, reliability, or compatibility matter most.

- **Decision:** PROCEED, PROCEED_WITH_LIMITATIONS, or DO_NOT_INVEST.

# 8. Duplicate and Existing-Work Detection

## Why duplicate detection must happen twice

A broad search before code review helps reviewers avoid known work. A second search after a candidate is understood is more precise because it can use the exact symptom, file path, function name, error message, root cause, and proposed remedy. Both stages are required.

## Sources to inspect

- Open, closed, assigned, and labelled issues.

- Open, draft, closed, and recently merged pull requests.

- Repository discussions, requests for comments, design proposals, and roadmap boards.

- Release notes, changelogs, security advisories, TODO and FIXME comments, and documentation limitations.

- Recent commits on the default branch and active feature branches where visible.

## Search strategy

The validator should search semantically, not only by exact title. Query variants should include the component, function, file path, user-visible symptom, error message, root cause, feature terminology, synonyms, and the proposed solution pattern.

```text
Example finding: repeated configuration parsing
Search variants:
- "configuration parsing performance"
- "cache parsed config"
- "repeated file parsing"
- exact function name
- exact file path
- "slow startup"
- "startup performance"
- parser class name + cache
- config reload + invalidation
```

## Duplicate status taxonomy

| **Status**        | **Meaning**                                                                 | **Default action**                          |
|-------------------|-----------------------------------------------------------------------------|---------------------------------------------|
| CLEAR             | No materially related issue, PR, discussion, or recent change found.        | Candidate may proceed                       |
| RELATED           | Similar topic exists, but the candidate has a distinct root cause or scope. | Document relationship and proceed carefully |
| PARTIALLY_COVERED | Existing work solves only part of the problem.                              | Clarify non-overlapping scope               |
| CLAIMED           | Another contributor appears to be actively implementing the same change.    | Do not duplicate; coordinate or drop        |
| DUPLICATE         | Same problem and materially same solution already exists.                   | Reject                                      |
| REJECTED          | Maintainers previously rejected this direction.                             | Reject unless assumptions changed           |
| SUPERSEDED        | A newer architecture or branch makes the finding obsolete.                  | Reject                                      |
| UNKNOWN           | Current remote activity could not be checked adequately.                    | Do not classify as clear; lower confidence  |

# 9. Security Contribution Discovery

## Security review objective

The security reviewer must identify exploitable or materially risky behaviour, not merely suspicious syntax. Every finding requires a threat model, an attacker-controlled input path, a reachable sensitive operation, impact analysis, existing mitigation review, and a disclosure recommendation.

## Review layers

| **Layer**                  | **Review focus**                                                                                                                                                                                                                                                   |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Attack-surface mapping     | Network entry points, APIs, command-line input, file parsing, archive extraction, templates, database queries, deserialisation, plugin loading, shell execution, authentication, secrets, crypto, CI workflows, and update mechanisms.                             |
| Trust-boundary analysis    | Input source, expected trust, validation, privilege transition, and attacker control.                                                                                                                                                                              |
| Vulnerability-class review | Injection, path traversal, unsafe deserialisation, SSRF, auth bypass, authorisation failures, race conditions, command execution, symlink attacks, ReDoS, resource exhaustion, secret exposure, insecure temporary files, workflow injection, and unsafe defaults. |
| Reachability validation    | Prove the complete input-to-impact chain and identify all preconditions.                                                                                                                                                                                           |
| Expected-behaviour review  | Check sandboxing, configuration assumptions, privilege requirements, documentation, and other validation layers.                                                                                                                                                   |

## Required proof chain

```text
Attacker-controlled input
↓
Missing or insufficient validation
↓
Reachable sensitive operation
↓
Security impact
↓
Reproducible conditions and affected configurations
```

## Confidence levels

| **Confidence** | **Minimum requirement**                                      | **Shortlist policy**                        |
|----------------|--------------------------------------------------------------|---------------------------------------------|
| Confirmed      | Reproducible with a clear input-to-impact path.              | Eligible                                    |
| High           | Strong source evidence with minor environmental assumptions. | Eligible with assumptions stated            |
| Medium         | Plausible but runtime or deployment assumptions remain.      | Research further; normally do not shortlist |
| Low            | Pattern-based suspicion without validated reachability.      | Reject or retain only as a research note    |

## Responsible disclosure

> **Security handling rule**
>
> Before preparing any public issue or pull request, inspect `SECURITY.md`, advisory instructions, private disclosure contacts, and bug-bounty rules. Findings with meaningful exploitability should be marked `PRIVATE_DISCLOSURE` and excluded from normal public contribution output.

## Security candidate dossier

- Classification and executive summary.

- Affected component, source locations, preconditions, and code path.

- Threat model, root cause, reproduction approach, and actual impact.

- Severity reasoning, existing mitigations, and false-positive analysis.

- Related issues, PRs, advisories, introducing commit, and original PR.

- Proposed remediation, alternatives, compatibility considerations, and required tests.

- Disclosure recommendation, confidence level, and unresolved questions.

# 10. Performance Contribution Discovery

## Performance review objective

The performance reviewer should identify changes that can produce measurable improvement on important execution paths. A code fragment that looks inefficient is not enough. The reviewer must explain why the path matters, how the cost scales, how to measure it, and what trade-offs the optimisation introduces.

## Target categories

- Algorithmic complexity and unsuitable data structures.

- Repeated I/O, parsing, network calls, schema compilation, or initialisation.

- N+1 queries, missing batching, serial work that can safely be concurrent, and unbounded concurrency.

- Excessive allocations, copies of large objects, lock contention, memory growth, and resource leaks.

- Cache opportunities with explicit lifecycle and invalidation analysis.

- Cold-start cost, expensive regular expressions, excessive hot-path logging, retries, and redundant work.

## Required proof chain

```text
Important execution path
↓
Identified cost centre
↓
Scaling or frequency explanation
↓
Benchmark or profiling plan
↓
Proposed improvement
↓
Expected measurable effect
↓
Correctness, memory, latency, and complexity trade-offs
```

## Rejection criteria

- No realistic benchmark or profile can be created.

- The code is not on a meaningful path.

- The likely gain is negligible relative to complexity.

- The change creates unsafe caching or invalidation behaviour.

- The workload assumptions are artificial or unrepresentative.

- The repository has explicitly chosen clarity or compatibility over the proposed optimisation.

- An active pull request or newer branch already addresses the bottleneck.

## Benchmark design standard

| **Element**       | **Required content**                                                                                      |
|-------------------|-----------------------------------------------------------------------------------------------------------|
| Scenario          | Representative data size, invocation pattern, concurrency level, platform, and configuration.             |
| Baseline          | Current default-branch behaviour and exact command.                                                       |
| Measurements      | Median, p95 or throughput as appropriate; CPU, memory, allocations, I/O, or request count where relevant. |
| Comparison        | Current main, proposed approach, correctness edge cases, and invalidation or fallback path.               |
| Success criterion | A justified threshold based on the project’s context, not an arbitrary universal percentage.              |
| Correctness guard | Tests proving identical output, stable API behaviour, and no resource leak or race regression.            |

# 11. Feature Contribution Discovery

## Feature review objective

Feature discovery is the most likely area for speculative AI output. The system must therefore begin with evidence of demand or project direction, define the smallest useful scope, and explicitly assess maintenance cost and architectural fit.

## Evidence hierarchy

| **Tier** | **Source of opportunity**                                                                                                                     | **Default approach**                                      |
|----------|-----------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------|
| Tier 1   | Roadmap item, help-wanted issue, accepted proposal, maintainer request, documented limitation, or repeated explicit user demand.              | Strong candidate for implementation after duplicate check |
| Tier 2   | Repeated workaround, missing compatibility, natural extension of an existing subsystem, or ecosystem requirement strongly supported by usage. | Validate with maintainers if scope is material            |
| Tier 3   | AI-inferred capability gap or developer-experience improvement without explicit project demand.                                               | Discussion first; high evidence threshold                 |

## Feature-alignment checks

- Does the feature fit the project’s stated scope and non-goals?

- Have maintainers or users expressed demand?

- Is another plugin, integration, or external project the correct home?

- Can an MVP be delivered without introducing a broad new subsystem?

- Does the feature create a new dependency, API commitment, migration, or long-term support burden?

- Can it be implemented incrementally and tested deterministically?

- Does it preserve backward compatibility and established configuration patterns?

## Feature proposal contract

- User problem and evidence of demand.

- Current workaround and why it is insufficient.

- Project and roadmap alignment.

- Related issues, PRs, discussions, and rejected alternatives.

- Minimum viable scope, explicit non-goals, suggested API or behaviour.

- Architectural fit, backward compatibility, maintenance cost, tests, and documentation impact.

- Recommended first action: implement, comment on an issue, request design confirmation, submit a proposal, or do not pursue.

# 12. Git History and Maintainer-Intent Analysis

## Purpose

Tracing the change that introduced a behaviour gives the contributor context that static review cannot provide. The objective is not to blame an earlier author. It is to understand the requirement and constraints that made the current design reasonable at the time, then determine whether those assumptions still hold.

## Investigation sequence

```bash
git blame <file>
git show <commit>
git log -L <start>,<end>:<file>
git log --follow -- <file>
git show --stat <commit>
git branch --contains <commit>
git tag --contains <commit>
```

Then map the commit to its issue or pull request using merge metadata, squash references, commit pages, issue references, and repository search.

## Historical questions

- What problem was the original pull request solving?

- What compatibility, lifecycle, API, or deployment constraints existed?

- Was the behaviour deliberate or a side effect?

- Did reviewers note follow-up work, limitations, or a future migration?

- Have later releases removed the original constraint?

- Does the proposed fix preserve the original intent while adapting to the current architecture?

## Recommended maintainer framing

> **Respectful change narrative**
>
> “The original implementation was appropriate under constraint X. Since the project changed Y, the same approach now causes Z. This proposal preserves the original intent while adapting the implementation to the current architecture.”

# 13. Candidate Validation and Ranking

## Adversarial validation

Each reviewer produces hypotheses. A separate validation step must actively try to reject them. This avoids reviewer confirmation bias and reduces the chance that a persuasive but incomplete report reaches implementation.

| **Dimension** | **Questions**                                                                                                  |
|---------------|----------------------------------------------------------------------------------------------------------------|
| Reality       | Is the path reachable? Can behaviour be reproduced? Is there hidden validation? Is the interpretation correct? |
| Impact        | Who is affected, under what conditions, how often, and with what consequence?                                  |
| Duplication   | Is there an issue, draft PR, merged fix, assigned contributor, or semantically equivalent proposal?            |
| Alignment     | Does the change fit project goals, architecture, non-goals, dependencies, and compatibility expectations?      |
| Feasibility   | Can the change be delivered in a focused PR with clear tests and reviewable scope?                             |
| Communication | Is the historical explanation and maintainer-facing argument respectful and convincing?                        |

## Candidate dispositions

| **Disposition**        | **Meaning**                                                                                       |
|------------------------|---------------------------------------------------------------------------------------------------|
| SHORTLIST              | Evidence, impact, alignment, and feasibility are sufficient for human review.                     |
| NEEDS_MAINTAINER_INPUT | The problem is credible, but scope or design direction requires discussion before implementation. |
| HOLD                   | Potentially valuable, but blocked by missing evidence, active project change, or timing.          |
| REJECT                 | Duplicate, low-value, misaligned, unproven, superseded, or impractical.                           |
| PRIVATE_DISCLOSURE     | Security-sensitive and unsuitable for public issue or PR workflow.                                |

## 100-point contribution-success score

| **Category**                                     | **Weight** |
|--------------------------------------------------|------------|
| Evidence that the problem or opportunity is real | 15         |
| User or project impact                           | 15         |
| Maintainer and roadmap alignment                 | 15         |
| Non-duplication confidence                       | 15         |
| Technical solution confidence                    | 10         |
| Scope clarity                                    | 10         |
| Testability                                      | 5          |
| Backward compatibility                           | 5          |
| Historical justification                         | 5          |
| Contributor ability to implement and explain     | 5          |

## Risk deductions

| **Risk**                                          | **Deduction** |
|---------------------------------------------------|---------------|
| Open or draft PR materially overlaps              | -30           |
| Maintainers previously rejected the same approach | -30           |
| No reproducible evidence                          | -20           |
| Repository appears inactive                       | -20           |
| Breaking public API change required               | -15           |
| Major new dependency required                     | -10           |
| Unclear ownership or scope                        | -10           |

## Score interpretation

| **Score** | **Recommendation**                             |
|-----------|------------------------------------------------|
| 85-100    | Excellent contribution candidate               |
| 70-84     | Strong candidate                               |
| 55-69     | Discuss with maintainers before implementation |
| 40-54     | Weak candidate; pursue only with new evidence  |
| Below 40  | Do not pursue                                  |

Security severity and contribution feasibility must be assessed separately. A critical vulnerability can be highly important while still being inappropriate for a normal public pull request.

# 14. Discovery Documents and Output Contract

## Output directory

```text
contribution-discovery/
├── 00-repository-profile.md
├── 01-architecture-and-context.md
├── 02-existing-work-map.md
├── 03-review-coverage.md
├── 04-candidate-scorecard.md
├── 05-final-recommendation.md
├── candidates/
│   ├── SEC-001.md
│   ├── PERF-001.md
│   ├── FEAT-001.md
│   └── REJECTED-001.md
├── evidence/
│   ├── commands-run.md
│   ├── source-locations.json
│   ├── github-searches.json
│   ├── benchmark-plan.md
│   └── unresolved-questions.md
└── machine-readable/
    ├── repository-profile.json
    ├── candidates.json
    └── final-ranking.json
```

## Why rejected findings are retained

Rejected findings prevent the system from rediscovering the same weak idea on a later run. Each rejection should record why it was rejected and the condition under which it may become worth reconsidering, such as a lifecycle change, new maintainer request, or removal of a compatibility constraint.

## Evidence labels

| **Label**      | **Meaning**                                       |
|----------------|---------------------------------------------------|
| \[CODE\]       | Directly verified in source.                      |
| \[TEST\]       | Reproduced through a test, benchmark, or command. |
| \[HISTORY\]    | Supported by commit or pull-request history.      |
| \[MAINTAINER\] | Supported by a maintainer statement.              |
| \[DOCS\]       | Supported by project documentation.               |
| \[INFERENCE\]  | Reasoned conclusion that is not directly stated.  |
| \[UNVERIFIED\] | Requires additional validation.                   |

## Final recommendation content

- One primary candidate and no more than two alternatives.

- Why the primary candidate is strongest.

- Evidence summary with exact files, functions, commits, PRs, issues, and benchmark or reproduction plans.

- Maintainer-facing pitch and historical rationale.

- Required pre-implementation checks.

- Minimum PR scope, optional follow-ups, and explicit exclusions.

- Final recommendation: implement, discuss, privately disclose, hold, or drop.

# 15. Claude Code Skill and Agent Design

## Recommended personal skill layout

```text
~/.claude/skills/contributor-scout/
├── SKILL.md
├── references/
│   ├── contribution-quality-rubric.md
│   ├── security-review-playbook.md
│   ├── performance-review-playbook.md
│   ├── feature-discovery-playbook.md
│   ├── duplicate-detection-playbook.md
│   ├── git-history-playbook.md
│   ├── maintainer-alignment-playbook.md
│   └── threat-model-template.md
├── templates/
│   ├── repository-profile.md
│   ├── candidate-finding.md
│   ├── security-finding.md
│   ├── performance-finding.md
│   ├── feature-proposal.md
│   ├── contribution-dossier.md
│   └── executive-summary.md
└── scripts/
    ├── collect_repo_metadata.py
    ├── collect_git_history.py
    ├── search_github_candidates.py
    ├── normalize_findings.py
    ├── calculate_candidate_score.py
    └── validate_report_schema.py
```

## Recommended subagents

```text
~/.claude/agents/
├── repository-intelligence.md
├── security-reviewer.md
├── performance-reviewer.md
├── feature-scout.md
├── duplicate-validator.md
└── contribution-ranker.md
```

## Orchestrator modes

| **Invocation**                            | **Purpose**                                                         |
|-------------------------------------------|---------------------------------------------------------------------|
| /contributor-scout profile                | Repository viability and architecture only.                         |
| /contributor-scout full                   | Complete discovery workflow across all three categories.            |
| /contributor-scout security               | Security-focused review with disclosure checks.                     |
| /contributor-scout performance            | Performance-focused review and benchmark design.                    |
| /contributor-scout features               | Roadmap and demand-backed feature discovery.                        |
| /contributor-scout validate \<candidate\> | Adversarial revalidation of a specific dossier.                     |
| /contributor-scout refresh                | Refresh issues, PRs, recent commits, duplicate status, and ranking. |

## Role of deterministic scripts

- **Repository metadata:** Collect languages, manifests, test commands, CI workflows, tags, repository size, and policy files.

- **Git history:** Given a file and line range, collect blame, introducing commits, related messages, and structured evidence.

- **GitHub search:** Return issue, PR, author, status, label, date, and relationship data for multiple query variants.

- **Scoring:** Apply the rubric and deductions consistently.

- **Schema validation:** Fail a report that lacks impact, evidence, duplicate status, history, tests, confidence, or next action.

# 16. Permissions, Safety, and Responsible Disclosure

## Default permissions

| **Class**               | **Examples**                                                                                                                                                               |
|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Allowed                 | Read, search, Git status/log/show/blame/diff/tag, GitHub read-only queries, existing tests, static analysis, safe benchmarks, and writes under contribution-discovery/.    |
| Approval required       | Package installation, dependency changes, Docker builds from untrusted repositories, network services, database migrations, credentials, or download-and-execute commands. |
| Denied during discovery | Source edits, branch creation, commits, pushes, resets, deployments, releases, issue creation, PR creation, comments, or public disclosure actions.                        |

## Enforcement mechanism

Claude Code hooks should enforce that write operations are permitted only inside contribution-discovery/ while the skill is active. Commands such as git commit, git push, gh issue create, gh pr create, and source-file writes should be denied. This converts the “discovery only” principle into a technical control rather than relying solely on prompt compliance.

## Untrusted repository handling

- Do not execute arbitrary setup scripts automatically.

- Inspect package scripts, Makefiles, container definitions, and CI commands before running them.

- Prefer existing non-destructive tests and static checks.

- Require explicit approval for installation, services, privileged commands, network access, or credential use.

- Record every command run in the evidence directory.

# 17. Human Review and Implementation Handoff

## Human approval gates

1. The engineer must be able to explain the current behaviour, root cause, impact, proposed solution, alternatives, and risks without relying on hidden AI reasoning.

2. Immediately before implementation, current issues, pull requests, and default-branch commits must be refreshed.

3. The engineer selects the correct route: implement directly, discuss on an existing issue, request design confirmation, privately disclose, hold, or drop.

4. Only an explicitly approved discovery dossier may be passed to an implementation workflow.

5. Every generated code change remains subject to line-by-line human review and project-specific tests.

## Separate implementation workflow

```text
Contributor Scout
“What should we contribute, and why?”
↓
Human approval
“Is this correct, valuable, non-duplicate, and defensible?”
↓
Contribution Implementer
“Implement exactly the approved scope.”
↓
Human submission
“Review, communicate, and submit responsibly.”
```

## Implementation skill responsibilities

- Read the approved dossier as the source of truth.

- Revalidate the current default branch and duplicate status.

- Create a focused branch only after approval.

- Add a failing regression test or benchmark before the change where practical.

- Implement the minimum required scope.

- Run targeted and broader tests, compare benchmarks, and document results.

- Generate a project-style pull-request description.

- Stop before pushing or opening the pull request unless explicitly authorised.

# 18. Delivery Roadmap

## V1 - Structured discovery foundation

| **Capability**      | **Included in V1**                                                     |
|---------------------|------------------------------------------------------------------------|
| Orchestrator        | One Contributor Scout skill with explicit stages and stop conditions   |
| Review methods      | Security, performance, and feature reference playbooks                 |
| Remote intelligence | GitHub CLI read-only searches for issues and pull requests             |
| History             | Git blame, log, commit, and introducing-PR analysis                    |
| Outputs             | Markdown dossiers, evidence JSON, scorecard, and final recommendation  |
| Validation          | Manual scoring plus mandatory report completeness checks               |
| Safety              | Read-only permissions and writes restricted to the discovery directory |

V1 should be tested on three repositories with different languages or architectures. The team should examine whether findings are real, whether duplicate detection is sufficient, and whether the final dossier genuinely reduces implementation and communication effort.

## V2 - Specialised agents and automation

- Introduce specialised subagents and an adversarial validator.

- Add machine-readable report schemas and automated scoring.

- Add candidate-specific semantic query generation and duplicate classification.

- Add refresh mode and stale-candidate detection.

- Store rejected findings and reasons for future runs.

## V3 - Language and ecosystem depth

- Language-specific security and performance playbooks.

- Optional Semgrep, CodeQL, profiler, benchmark, and dependency-analysis integrations.

- Repository-specific heuristics for frameworks, build systems, and CI platforms.

- Historical calibration using accepted, rejected, and revised contribution proposals.

## V4 - Open-source productisation

- Package the system as a reusable Claude Code plugin.

- Publish report schemas, agents, scripts, and example repositories.

- Create an evaluation dataset linking discovery proposals to maintainer outcomes.

- Add support for other repository hosts and coding agents.

- Position the project as an evidence-first contribution discovery framework rather than an automated pull-request generator.

# 19. Evaluation Framework and Success Metrics

## What to evaluate during pilots

| **Metric**                | **Definition**                                                                         | **Suggested V1 target**                       |
|---------------------------|----------------------------------------------------------------------------------------|-----------------------------------------------|
| True-positive rate        | Shortlisted findings independently confirmed as real and correctly understood.         | At least 70%                                  |
| Duplicate avoidance       | Candidates incorrectly shortlisted despite existing equivalent work.                   | Below 10%                                     |
| Evidence completeness     | Final dossiers containing all mandatory sections and source references.                | 100%                                          |
| Human approval rate       | Shortlisted candidates approved for discussion or implementation.                      | At least 50%                                  |
| Scope quality             | Approved candidates that can be expressed as a focused PR without unrelated refactors. | At least 80%                                  |
| Maintainer outcome        | Implemented proposals accepted, positively discussed, or constructively redirected.    | Track during pilots; no hard target initially |
| Unsafe action count       | Unauthorised source edits, public posts, pushes, or destructive commands.              | Zero                                          |
| Reviewer usefulness score | Internal engineer rating of whether the dossier reduced research effort.               | Average 4/5 or higher                         |

## Quality review questions

- Could an engineer reproduce the finding using only the dossier?

- Does the report distinguish facts, tests, history, maintainer statements, inference, and uncertainty?

- Would the suggested maintainer pitch remain respectful if read by the original author?

- Does the proposed PR solve one coherent problem?

- Are alternatives and compatibility risks represented fairly?

- Would the team still recommend the contribution if no AI had been involved?

# 20. Risks and Mitigations

| **Risk**                       | **Impact**                                     | **Mitigation**                                                                                                     |
|--------------------------------|------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| Security over-reporting        | False vulnerability claims and wasted effort.  | Require reachability, threat model, false-positive analysis, confidence threshold, and private disclosure checks.  |
| Semantic duplicate missed      | Redundant contribution.                        | Search twice using symptoms, source names, errors, synonyms, solutions, discussions, and recent commits.           |
| Performance micro-optimisation | Complexity with little value.                  | Require an important path, benchmark plan, scaling explanation, and trade-off analysis.                            |
| Speculative feature generation | Scope creep and maintenance burden.            | Use evidence hierarchy, require demand and non-goals, and default Tier 3 ideas to discussion-first.                |
| Misread maintainer intent      | Proposal conflicts with project direction.     | Read contribution policies, historical PR comments, rejected issues, roadmap, and mark inference explicitly.       |
| Excessive Claude usage         | High subscription consumption and slow review. | Use early repository rejection, staged modes, targeted modules, deterministic scripts, and progressive references. |
| Unsafe repository execution    | Credential, host, or environment risk.         | Read-only mode, command allowlist, explicit approvals, and command logging.                                        |
| Engineer cannot defend output  | Low-quality PR and reputational risk.          | Mandatory human comprehension gate and no direct submission automation.                                            |
| Stale discovery report         | Candidate becomes duplicate or obsolete.       | Refresh mode immediately before implementation.                                                                    |
| Bias toward finding something  | Weak candidates are forced into the shortlist. | Allow “no suitable contribution found” as a successful outcome.                                                    |

# 21. Team Operating Model

## Suggested roles

| **Role**                     | **Responsibilities**                                                                        |
|------------------------------|---------------------------------------------------------------------------------------------|
| Skill owner                  | Maintains SKILL.md, workflow stages, permissions, and release versions.                     |
| Security reviewer            | Owns security playbooks, disclosure rules, and validation thresholds.                       |
| Performance reviewer         | Owns benchmark standards, profiler integrations, and performance evidence quality.          |
| Feature and product reviewer | Owns roadmap analysis, demand evidence, maintenance-cost evaluation, and scope quality.     |
| Tooling engineer             | Builds GitHub, Git history, scoring, schema validation, and report-generation scripts.      |
| Pilot contributors           | Run the system on selected repositories, verify candidates, and record maintainer outcomes. |
| Approver                     | Authorises implementation and confirms that the engineer can defend the proposal.           |

## Review cadence

- Review every completed pilot report as a team.

- Track false positives, missed duplicates, unclear evidence, and maintainer feedback.

- Update playbooks only from observed failure patterns, not from speculative complexity.

- Version the skill and report schema so historical pilot results remain comparable.

# 22. Recommended Pilot

## Repository selection

Select three repositories that are active, accept external contributions, have working tests, and match team expertise. Prefer diversity in language or architecture so the workflow is not overfitted to one ecosystem. Avoid extremely large repositories for the first pilot.

## Pilot sequence

1. Run profile mode and validate the repository viability decision manually.

2. Run one category-specific review before full mode to calibrate depth and token use.

3. Run full mode and produce no more than three final candidates.

4. Assign a second engineer to independently verify the primary candidate.

5. Classify the candidate as implement, discuss, disclose, hold, or reject.

6. For approved candidates, use a separate implementation workflow and submit a focused contribution.

7. Record maintainer outcome and update the rubric based on actual feedback.

## Pilot exit criteria

- At least two repositories produce a useful, independently verified candidate or a well-justified “no candidate” result.

- No unauthorised source or remote changes occur.

- Duplicate classification is demonstrably better than exact-title search alone.

- The discovery dossier materially reduces implementation and PR-writing effort.

- The team can identify which components should be automated in V2 and which should remain human-controlled.

# 23. Decisions Required from the Team

| **Decision**                            | **Recommended position**                                               |
|-----------------------------------------|------------------------------------------------------------------------|
| Approve discovery-only architecture     | Yes. Preserve a hard separation between discovery and implementation.  |
| Approve three primary review categories | Yes: security, performance, and evidence-backed feature opportunities. |
| Approve multi-agent target design       | Yes, but implement a simpler single-orchestrator V1 first.             |
| Approve GitHub CLI dependency           | Yes, with degraded mode when authentication is unavailable.            |
| Approve read-only permission model      | Yes, enforced by hooks and command restrictions.                       |
| Approve report directory and schemas    | Yes, to make results reviewable and machine-readable.                  |
| Select pilot repositories               | Choose three active projects aligned with team expertise.              |
| Assign owners                           | Name a skill owner, tooling engineer, and category reviewers.          |
| Approve success metrics                 | Adopt the V1 metrics and review after the first three pilots.          |

> **Recommended approval statement**
>
> Proceed with V1 of Contributor Scout as a read-only, evidence-first Claude Code workflow. Pilot it on three repositories, require human approval before implementation, and use pilot outcomes to decide which specialised agents and deterministic integrations should enter V2.

# Appendix A - Minimum Candidate Report Template

```markdown
# <TYPE-ID>: <Candidate title>
## Classification and disposition
## Executive summary
## Project and user impact
## Affected components and exact source locations
## Current behaviour
## Expected behaviour
## Root cause or capability gap
## Reproduction, benchmark, or demand evidence
## Existing mitigations and false-positive analysis
## Related issues, PRs, discussions, and recent commits
## Introducing commit and original PR
## Historical design constraints
## Proposed solution direction
## Alternative solutions considered
## Minimum PR scope
## Optional follow-ups
## Explicit exclusions
## Backward compatibility and maintenance cost
## Required tests and documentation
## Maintainer-facing pitch
## Duplicate status and confidence
## Overall score
## Recommended next action
## Open questions
```

# Appendix B - Example Final Recommendation

> **Illustrative candidate**
>
> `PERF-002` - Avoid repeated schema compilation during validation. This is an example of the expected report style and is not a claim about any specific repository.

- **Why it is strong:** The behaviour is reproduced on the current default branch, affects a common path, has no active overlapping PR, and can be changed without altering the public API.

- **Historical context:** The implementation predates the project’s current schema lifecycle cache, so reusing the existing lifecycle boundary may now be appropriate.

- **Proposed first step:** Add a benchmark and regression test, then confirm cache lifecycle expectations with maintainers.

- **Minimum scope:** Reuse the existing cache boundary and preserve error behaviour.

- **Excluded scope:** Validator redesign, unrelated typing cleanup, new cache backends, and configuration changes.

# Appendix C - Sample Skill Contract

```markdown
---
name: contributor-scout
description: Discover evidence-backed open-source contribution opportunities in a cloned repository. Produce discovery documents only.
---

# Contributor Scout

## Hard constraints

- Discovery only.
- Do not modify application source.
- Do not create branches, commits, issues, comments, or pull requests.
- Treat findings as hypotheses until validated.
- Search existing issues, PRs, discussions, and recent commits.
- Trace introducing commits and related PRs where discoverable.
- Follow the repository security disclosure policy.
- Prefer one strong candidate over many weak findings.

## Completion requirements

Each final candidate must include source evidence, impact, duplicate status, historical context, proposed fix direction, alternatives, tests, compatibility risks, confidence, and recommended next action.
```

# Appendix D - Practical Contributor Workflow

1. Select an active repository aligned with personal expertise.

2. Clone and build it manually once.

3. Run /contributor-scout profile.

4. Stop if repository viability is poor.

5. Run /contributor-scout full or one category-specific mode.

6. Review the primary dossier and independently reproduce its evidence.

7. Refresh issues, PRs, and recent commits.

8. Contact maintainers first when scope or direction is uncertain.

9. Pass only an approved dossier to the implementation skill.

10. Review every changed line and submit a focused contribution.

11. Record maintainer feedback to improve the system.

# Conclusion

Contributor Scout is designed to make AI-assisted open-source contribution more disciplined, respectful, and effective. It does not optimise for the number of generated pull requests. It optimises for the quality of the decision that precedes a pull request. By combining repository intelligence, specialised review, duplicate detection, historical analysis, adversarial validation, strict read-only controls, and a human approval gate, the system can help the team contribute faster without transferring research burden to maintainers.

The recommended next step is to approve the V1 scope, assign owners, select three pilot repositories, and evaluate the system using independently verified findings and real maintainer outcomes.
