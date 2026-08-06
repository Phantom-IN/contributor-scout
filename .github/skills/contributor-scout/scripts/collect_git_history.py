#!/usr/bin/env python3
"""Collect Git history evidence for a candidate's source locations.

Part of the Contributor Scout skill (Phase 4: historical investigation).

Given a file path and an optional line range, this script gathers blame
information, the commits that touched that range, the full file history, a
ranked list of *introducing commit candidates*, and branch/tag containment for
the strongest candidate.

Deliberate limitation
---------------------
The script does NOT claim to find the introducing pull request unless the
evidence is unambiguous. It reports:

    verified   - the PR number came from a merge-commit subject, a GitHub
                 squash-merge subject `(#123)`, or a commit trailer.
    unverified - a number appeared somewhere in the message but the form is
                 ambiguous.
    none       - nothing usable was found.

A wrong PR reference in a contribution proposal destroys credibility, so an
honest "not identified" is the correct output when evidence is thin.

Every Git subcommand used here is read-only.

Usage
-----
    python3 collect_git_history.py --repo . --path src/config/loader.py
    python3 collect_git_history.py --repo . --path src/config/loader.py \\
        --start-line 41 --end-line 67 \\
        --output contribution-discovery/evidence/history-PERF-001.json

Exit codes
----------
    0  history collected
    1  bad arguments, not a Git repository, or path not tracked
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_VERSION = "1.0.0"
FIELD_SEP = "\x1f"
RECORD_SEP = "\x1e"

# Subject forms that reliably identify a pull request.
MERGE_PR_RE = re.compile(r"Merge pull request #(\d+)")
SQUASH_PR_RE = re.compile(r"\(#(\d+)\)\s*$")
TRAILER_PR_RE = re.compile(
    r"^(?:Closes|Fixes|Resolves|Close|Fix|Resolve|PR|Pull-request|PR-URL)"
    r"[:\s#]+.*?#?(\d+)",
    re.IGNORECASE | re.MULTILINE,
)
LOOSE_HASH_RE = re.compile(r"#(\d+)")


def run(cmd: List[str], cwd: Path, timeout: int = 60) -> Tuple[int, str, str]:
    """Run a read-only git command. Returns (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except FileNotFoundError:
        return 127, "", "git not found on PATH"
    except subprocess.TimeoutExpired:
        return 124, "", "command timed out: {0}".format(" ".join(cmd))
    except OSError as exc:
        return 1, "", str(exc)
    return proc.returncode, proc.stdout, proc.stderr


def parse_commits(raw: str) -> List[Dict[str, str]]:
    """Parse `git log` output written with our field/record separators."""
    commits: List[Dict[str, str]] = []
    for record in raw.split(RECORD_SEP):
        record = record.strip("\n")
        if not record.strip():
            continue
        fields = record.split(FIELD_SEP)
        if len(fields) < 5:
            continue
        commits.append({
            "sha": fields[0],
            "short_sha": fields[0][:9],
            "author": fields[1],
            "date": fields[2],
            "subject": fields[3],
            "body": fields[4].strip(),
        })
    return commits


LOG_FORMAT = "--pretty=format:%H{f}%an{f}%aI{f}%s{f}%b{r}".format(f=FIELD_SEP, r=RECORD_SEP)


def collect_blame(repo: Path, path: str,
                  start: Optional[int], end: Optional[int]) -> Dict[str, Any]:
    """Blame the range, following moves and copies, ignoring whitespace."""
    cmd = ["git", "blame", "--line-porcelain", "-w", "-C", "-C"]
    if start is not None and end is not None:
        cmd += ["-L", "{0},{1}".format(start, end)]
    cmd += ["HEAD", "--", path]

    code, out, err = run(cmd, repo)
    if code != 0:
        return {"available": False, "error": err.strip() or "git blame failed"}

    lines: List[Dict[str, Any]] = []
    per_commit: Dict[str, int] = {}
    current: Dict[str, Any] = {}
    for line in out.splitlines():
        header = re.match(r"^([0-9a-f]{7,40}) (\d+) (\d+)", line)
        if header:
            current = {"sha": header.group(1), "original_line": int(header.group(2)),
                       "final_line": int(header.group(3))}
            continue
        if line.startswith("author "):
            current["author"] = line[len("author "):]
        elif line.startswith("author-time "):
            try:
                ts = int(line[len("author-time "):])
                current["date"] = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            except ValueError:
                pass
        elif line.startswith("summary "):
            current["subject"] = line[len("summary "):]
        elif line.startswith("\t"):
            current["content"] = line[1:]
            if "sha" in current:
                lines.append(current)
                per_commit[current["sha"]] = per_commit.get(current["sha"], 0) + 1
            current = {}

    return {
        "available": True,
        "line_count": len(lines),
        "lines": lines,
        "commits_touching_range": [
            {"sha": sha, "short_sha": sha[:9], "lines_attributed": count}
            for sha, count in sorted(per_commit.items(), key=lambda kv: -kv[1])
        ],
        "note": "blame shows the LAST change to each line, not necessarily the "
                "commit that introduced the behaviour - follow it backwards.",
    }


def collect_range_log(repo: Path, path: str, start: int, end: int,
                      limit: int) -> Dict[str, Any]:
    """`git log -L` over a line range: the evolution of exactly those lines."""
    code, out, err = run(
        ["git", "log", "-L", "{0},{1}:{2}".format(start, end, path),
         "--max-count={0}".format(limit), "--no-patch", LOG_FORMAT],
        repo, timeout=120,
    )
    if code != 0:
        return {"available": False, "error": err.strip() or "git log -L failed"}
    return {"available": True, "commits": parse_commits(out)}


def collect_file_log(repo: Path, path: str, limit: int) -> Dict[str, Any]:
    """Full file history, following renames."""
    code, out, err = run(
        ["git", "log", "--follow", "--max-count={0}".format(limit), LOG_FORMAT,
         "--", path],
        repo, timeout=120,
    )
    if code != 0:
        return {"available": False, "error": err.strip() or "git log --follow failed"}
    return {"available": True, "commits": parse_commits(out)}


def extract_pr_reference(commit: Dict[str, str]) -> Dict[str, Any]:
    """Map a commit to a PR number, reporting how confident the mapping is."""
    subject = commit.get("subject", "")
    body = commit.get("body", "")

    match = MERGE_PR_RE.search(subject)
    if match:
        return {"pull_request": int(match.group(1)), "confidence": "verified",
                "source": "merge commit subject"}

    match = SQUASH_PR_RE.search(subject)
    if match:
        return {"pull_request": int(match.group(1)), "confidence": "verified",
                "source": "squash-merge subject convention"}

    match = TRAILER_PR_RE.search(body)
    if match:
        return {"pull_request": int(match.group(1)), "confidence": "verified",
                "source": "commit trailer"}

    match = LOOSE_HASH_RE.search(subject) or LOOSE_HASH_RE.search(body)
    if match:
        return {
            "pull_request": int(match.group(1)), "confidence": "unverified",
            "source": "loose '#n' reference - may be an issue, not a PR",
            "note": "verify with `gh api repos/{owner}/{repo}/commits/<sha>/pulls` "
                    "before citing this number",
        }

    return {"pull_request": None, "confidence": "none",
            "source": None,
            "note": "no PR reference found - report as 'introducing PR not identified'"}


def rank_introducing_candidates(blame: Dict[str, Any],
                                range_log: Dict[str, Any],
                                file_log: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Rank commits by how likely they introduced the behaviour.

    Heuristic, deliberately transparent:
      +3 per blame-attributed line (capped)
      +5 if the commit appears in the line-range log (it changed these lines)
      +1 if it appears in the file history
      -2 if the subject looks like a pure formatting/lint/rename change
    """
    scores: Dict[str, float] = {}
    details: Dict[str, Dict[str, Any]] = {}

    for entry in blame.get("commits_touching_range", []) or []:
        sha = entry["sha"]
        scores[sha] = scores.get(sha, 0) + min(entry["lines_attributed"], 5) * 3
        details.setdefault(sha, {})["lines_attributed"] = entry["lines_attributed"]

    for commit in range_log.get("commits", []) or []:
        sha = commit["sha"]
        scores[sha] = scores.get(sha, 0) + 5
        details.setdefault(sha, {}).update(commit)
        details[sha]["in_range_log"] = True

    for commit in file_log.get("commits", []) or []:
        sha = commit["sha"]
        if sha in scores:
            scores[sha] += 1
        details.setdefault(sha, {}).update(commit)

    noise = re.compile(
        r"\b(format|formatting|lint|style|whitespace|typo|rename|move|reindent|"
        r"prettier|black|gofmt|rustfmt|clang-format)\b", re.IGNORECASE)

    ranked: List[Dict[str, Any]] = []
    for sha, score in scores.items():
        info = details.get(sha, {})
        subject = info.get("subject", "")
        adjusted = score - 2 if noise.search(subject) else score
        ranked.append({
            "sha": sha,
            "short_sha": sha[:9],
            "author": info.get("author"),
            "date": info.get("date"),
            "subject": subject,
            "body": info.get("body", ""),
            "heuristic_score": adjusted,
            "likely_cosmetic": bool(noise.search(subject)),
            "pull_request_reference": extract_pr_reference({
                "subject": subject, "body": info.get("body", "")}),
        })

    ranked.sort(key=lambda c: -c["heuristic_score"])
    return ranked[:10]


def collect_containment(repo: Path, sha: str) -> Dict[str, Any]:
    """Which branches and tags contain a commit - i.e. when it shipped."""
    result: Dict[str, Any] = {"sha": sha}

    code, out, _ = run(["git", "branch", "-a", "--contains", sha], repo)
    result["branches"] = (
        [b.strip().lstrip("* ") for b in out.splitlines()][:20] if code == 0 else []
    )

    code, out, _ = run(["git", "tag", "--contains", sha, "--sort=creatordate"], repo)
    tags = out.splitlines() if code == 0 else []
    result["tags"] = tags[:20]
    result["first_release_containing"] = tags[0] if tags else None

    code, out, _ = run(["git", "show", "--stat", "--format=%H%n%an%n%aI%n%s", sha], repo)
    if code == 0:
        result["stat"] = out[:6000]
    return result


def build_history(repo: Path, path: str, start: Optional[int], end: Optional[int],
                  limit: int) -> Dict[str, Any]:
    blame = collect_blame(repo, path, start, end)
    range_log: Dict[str, Any] = {"available": False,
                                 "reason": "no line range supplied"}
    if start is not None and end is not None:
        range_log = collect_range_log(repo, path, start, end, limit)
    file_log = collect_file_log(repo, path, limit)

    candidates = rank_introducing_candidates(blame, range_log, file_log)
    containment = collect_containment(repo, candidates[0]["sha"]) if candidates else None

    is_shallow = run(["git", "rev-parse", "--is-shallow-repository"], repo)[1].strip() == "true"

    warnings: List[str] = []
    if is_shallow:
        warnings.append(
            "repository is a shallow clone - history is incomplete. Historical "
            "justification should be rated low, or run `git fetch --unshallow` "
            "with the user's approval.")
    if candidates and candidates[0]["likely_cosmetic"]:
        warnings.append(
            "the top-ranked commit looks like a formatting or rename change - "
            "follow blame backwards through it to find the semantic change.")
    if not candidates:
        warnings.append("no introducing-commit candidates found - state "
                        "'history unavailable' in the candidate document.")

    return {
        "schema": "contributor-scout/git-history",
        "schema_version": "1.0.0",
        "script_version": SCRIPT_VERSION,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(repo),
        "target": {"path": path, "start_line": start, "end_line": end},
        "is_shallow_clone": is_shallow,
        "blame": blame,
        "line_range_log": range_log,
        "file_log": file_log,
        "introducing_commit_candidates": candidates,
        "containment_of_top_candidate": containment,
        "warnings": warnings,
        "notes": [
            "Introducing-commit ranking is a heuristic - verify the top candidate "
            "by reading `git show <sha>`.",
            "A pull-request reference is only 'verified' when it comes from a "
            "merge subject, a squash-merge subject, or a commit trailer.",
            "Never cite an 'unverified' PR number in a contribution proposal "
            "without confirming it.",
            "History is explanation, not blame - never name an author as the "
            "cause of a defect.",
        ],
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Git history evidence for a candidate's source "
                    "locations (Contributor Scout, Phase 4).",
        epilog="Read-only. Never modifies the repository or the working tree.",
    )
    parser.add_argument("--repo", default=".", help="Repository root (default: .)")
    parser.add_argument("--path", required=True,
                        help="File path relative to the repository root")
    parser.add_argument("--start-line", type=int, help="First line of the range")
    parser.add_argument("--end-line", type=int, help="Last line of the range")
    parser.add_argument("--limit", type=int, default=40,
                        help="Maximum commits per log query (default: 40)")
    parser.add_argument("--output", help="Write JSON here (default: stdout)")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent (default: 2)")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    repo = Path(args.repo).expanduser()
    if not repo.is_dir():
        print("error: --repo is not a directory: {0}".format(repo), file=sys.stderr)
        return 1
    if not (repo / ".git").exists():
        print("error: not a Git repository: {0}".format(repo), file=sys.stderr)
        return 1

    if (args.start_line is None) != (args.end_line is None):
        print("error: --start-line and --end-line must be used together",
              file=sys.stderr)
        return 1
    if args.start_line is not None:
        if args.start_line < 1 or args.end_line < args.start_line:
            print("error: invalid line range", file=sys.stderr)
            return 1
    if args.limit < 1:
        print("error: --limit must be positive", file=sys.stderr)
        return 1

    code, out, _ = run(["git", "ls-files", "--error-unmatch", "--", args.path], repo)
    if code != 0 or not out.strip():
        print("error: path is not tracked by git: {0}".format(args.path),
              file=sys.stderr)
        print("hint: use a path relative to the repository root", file=sys.stderr)
        return 1

    history = build_history(repo.resolve(), args.path,
                            args.start_line, args.end_line, args.limit)
    payload = json.dumps(history, indent=args.indent)

    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
        print("wrote {0}".format(output_path))
        for warning in history["warnings"]:
            print("warning: " + warning, file=sys.stderr)
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
