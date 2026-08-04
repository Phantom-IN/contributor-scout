# Examples

Worked examples of Contributor Scout output.

> **All examples are fictional.** `example-org/fluxconf` is an invented
> repository. Every file path, line number, commit SHA, issue number, and
> measurement is fabricated to demonstrate the expected report style. None of it
> is a claim about any real project, and none of it was produced by running the
> skill against real code.

| File | Demonstrates |
|---|---|
| [sample-repository-profile.md](sample-repository-profile.md) | Phase 0 eligibility decision, activity signals, disclosure channel discovery, and honest limitation recording |
| [sample-candidate.md](sample-candidate.md) | A complete shortlisted candidate: evidence tagging, path-importance proof, benchmark design, historical reasoning, changed assumptions, duplicate classification, and scoring |
| [sample-rejected-candidate.md](sample-rejected-candidate.md) | Candidate rejection: falsifying evidence, what was learned, and reconsideration conditions |
| [sample-final-recommendation.md](sample-final-recommendation.md) | Final ranking, maintainer pitch, scope boundaries, private-disclosure handling, and the human approval gate |

## What to look at

**Evidence tagging.** Every material claim in `sample-candidate.md` carries a
tag, and the tags are not inflated. Note evidence item 7 (`[INFERENCE]`) and
item 8 (`[UNVERIFIED]`) - the aggregate CPU figure and the open behavioural
question are labelled honestly rather than dressed up as measurements.

**Historical reasoning.** The "Historical design constraints" and "Changed
assumptions" sections explain why the original implementation was correct at the
time and what specifically changed. No sentence blames the original author.

**Duplicate classification.** `CLEAR` at `HIGH` confidence is justified by 12
listed query variants and by explaining why the overlapping issue #412 is a
reference rather than a duplicate.

**Rejection.** `sample-rejected-candidate.md` is what a *good* rejection looks
like: the reachability walk killed the finding before it reached a maintainer,
and the three facts learned along the way are more valuable than the candidate
was.

**Scope discipline.** Both the candidate and the final recommendation carry an
explicit exclusions list. That list is what stops a focused PR turning into a
refactor.

## Validating the examples

`sample-candidate.md` and `sample-rejected-candidate.md` pass the schema
validator:

```bash
python3 ../skills/contributor-scout/scripts/validate_report_schema.py \
  --candidate sample-candidate.md --strict
python3 ../skills/contributor-scout/scripts/validate_report_schema.py \
  --candidate sample-rejected-candidate.md --strict
```
