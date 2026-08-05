#!/usr/bin/env python3
"""Run read-only GitHub searches for duplicate detection.

Part of the Contributor Scout skill (Phases 2 and 5: duplicate detection).

Runs a set of query variants against issues and pull requests using the GitHub
CLI (`gh`) and normalises the results into a single JSON document that records
*every* query executed - including the ones that returned nothing. The empty
queries are what make a "no duplicate found" claim auditable.

Read-only guarantee
-------------------
Only `gh auth status`, `gh repo view`, `gh search issues`, `gh search prs`, and
read-only `gh api` GET requests are ever invoked. The script contains no code
path that can create, edit, comment on, or close anything. Any attempt to pass a
mutating subcommand is impossible: the subcommands are hard-coded.

Degraded mode
-------------
If `gh` is missing or unauthenticated, the script does not fail. It emits a
document with `remote_access.available = false` and
`duplicate_detection_confidence = "LOW"`, which the skill must carry into every
candidate as duplicate status `UNKNOWN`.

Usage
-----
    python3 search_github_candidates.py --repo-slug owner/name \\
        --query "cache parsed config" --query "slow startup" \\
        --query "ConfigLoader" \\
        --output contribution-discovery/evidence/github-searches.json

    # Infer the slug from the local clone's origin remote:
    python3 search_github_candidates.py --repo . --query "startup performance"

Exit codes
----------
    0  searches completed (possibly in degraded mode)
    1  bad arguments
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_VERSION = "1.0.0"

ISSUE_FIELDS = "number,title,state,url,createdAt,updatedAt,labels,repository"
PR_FIELDS = "number,title,state,url,createdAt,updatedAt,labels,isDraft,repository"


def have(binary: str) -> bool:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if directory and (Path(directory) / binary).exists():
            return True
    return False


def run(cmd: List[str], timeout: int = 60,
        cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            check=False, cwd=str(cwd) if cwd else None,
        )
    except FileNotFoundError:
        return 127, "", "{0} not found on PATH".format(cmd[0])
    except subprocess.TimeoutExpired:
        return 124, "", "timed out: {0}".format(" ".join(cmd))
    except OSError as exc:
        return 1, "", str(exc)
    return proc.returncode, proc.stdout, proc.stderr


def check_gh_auth() -> Dict[str, Any]:
    """Establish whether `gh` is usable before running any search."""
    if not have("gh"):
        return {
            "available": False, "authenticated": False,
            "reason": "gh (GitHub CLI) is not installed",
            "remedy": "install from https://cli.github.com/ then run `gh auth login`",
        }
    code, out, err = run(["gh", "auth", "status"], timeout=25)
    if code != 0:
        return {
            "available": True, "authenticated": False,
            "reason": (err or out).strip()[:400] or "gh is not authenticated",
            "remedy": "run `gh auth login`",
        }
    return {"available": True, "authenticated": True,
            "detail": (err or out).strip()[:400]}


def derive_slug_from_clone(repo: Path) -> Optional[str]:
    code, out, _ = run(["git", "remote", "get-url", "origin"], cwd=repo, timeout=15)
    if code != 0:
        return None
    match = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", out.strip())
    if not match:
        return None
    return "{0}/{1}".format(match.group(1), match.group(2))


def search(kind: str, slug: str, query: str, state: str,
           limit: int) -> Dict[str, Any]:
    """Run one `gh search issues|prs` query. Hard-coded read-only subcommand."""
    assert kind in ("issues", "prs"), "kind must be 'issues' or 'prs'"

    cmd = ["gh", "search", kind, query, "--repo", slug,
           "--limit", str(limit), "--json",
           ISSUE_FIELDS if kind == "issues" else PR_FIELDS]
    if state in ("open", "closed"):
        cmd += ["--state", state]

    started = datetime.now(timezone.utc).isoformat()
    code, out, err = run(cmd, timeout=90)

    record: Dict[str, Any] = {
        "kind": kind,
        "query": query,
        "state": state,
        "command": " ".join(cmd),
        "executed_at": started,
    }
    if code != 0:
        record["ok"] = False
        record["error"] = (err or out).strip()[:500]
        record["result_count"] = None
        record["results"] = []
        return record

    try:
        parsed = json.loads(out) if out.strip() else []
    except ValueError as exc:
        record["ok"] = False
        record["error"] = "could not parse gh output: {0}".format(exc)
        record["result_count"] = None
        record["results"] = []
        return record

    record["ok"] = True
    record["result_count"] = len(parsed)
    record["results"] = [normalise(item, kind) for item in parsed]
    return record


def normalise(item: Dict[str, Any], kind: str) -> Dict[str, Any]:
    labels = item.get("labels") or []
    label_names = [
        lbl.get("name") for lbl in labels if isinstance(lbl, dict) and lbl.get("name")
    ]
    normalised = {
        "type": "issue" if kind == "issues" else "pull_request",
        "number": item.get("number"),
        "title": item.get("title"),
        "state": item.get("state"),
        "url": item.get("url"),
        "created_at": item.get("createdAt"),
        "updated_at": item.get("updatedAt"),
        "labels": label_names,
    }
    if kind == "prs":
        normalised["is_draft"] = item.get("isDraft")
    return normalised


def fetch_advisories(slug: str) -> Dict[str, Any]:
    """Read-only GET for published security advisories."""
    cmd = ["gh", "api", "repos/{0}/security-advisories".format(slug),
           "--method", "GET", "--paginate"]
    code, out, err = run(cmd, timeout=60)
    if code != 0:
        return {"ok": False, "error": (err or out).strip()[:300], "advisories": []}
    try:
        data = json.loads(out) if out.strip() else []
    except ValueError:
        return {"ok": False, "error": "unparseable advisory response", "advisories": []}
    if not isinstance(data, list):
        data = []
    return {
        "ok": True,
        "count": len(data),
        "advisories": [
            {"ghsa_id": a.get("ghsa_id"), "summary": a.get("summary"),
             "severity": a.get("severity"), "published_at": a.get("published_at")}
            for a in data if isinstance(a, dict)
        ][:50],
    }


def fetch_repo_facts(slug: str) -> Dict[str, Any]:
    """Read-only repository metadata relevant to eligibility and disclosure."""
    fields = ("name,owner,isArchived,isFork,isMirror,visibility,pushedAt,"
              "hasDiscussionsEnabled,hasIssuesEnabled,licenseInfo,"
              "openIssuesCount,defaultBranchRef")
    code, out, err = run(["gh", "repo", "view", slug, "--json", fields], timeout=45)
    if code != 0:
        return {"ok": False, "error": (err or out).strip()[:300]}
    try:
        return {"ok": True, "data": json.loads(out)}
    except ValueError:
        return {"ok": False, "error": "unparseable repo view response"}


def assess_confidence(records: List[Dict[str, Any]], auth: Dict[str, Any],
                      discussions_checked: bool) -> Tuple[str, List[str]]:
    """Derive a duplicate-detection confidence level and explain it."""
    notes: List[str] = []
    if not auth.get("authenticated"):
        notes.append("GitHub CLI unavailable or unauthenticated - only local "
                     "evidence is possible.")
        notes.append("Every candidate from this run must use duplicate status "
                     "UNKNOWN, never CLEAR.")
        return "LOW", notes

    successful = [r for r in records if r.get("ok")]
    failed = [r for r in records if not r.get("ok")]
    distinct_queries = len({r["query"] for r in successful})
    kinds = {r["kind"] for r in successful}

    if failed:
        notes.append("{0} of {1} queries failed - see the 'error' field on each."
                     .format(len(failed), len(records)))

    if distinct_queries >= 8 and {"issues", "prs"} <= kinds and not failed:
        confidence = "HIGH"
    elif distinct_queries >= 3 and kinds:
        confidence = "MEDIUM"
        notes.append("Fewer than 8 distinct query variants, or a source was "
                     "unavailable - run more variants for HIGH confidence.")
    else:
        confidence = "LOW"
        notes.append("Too few successful queries to support a CLEAR "
                     "classification.")

    if not discussions_checked:
        notes.append("Discussions were not checked - confirm they are disabled, "
                     "or check them via the web UI.")
    return confidence, notes


def build_document(slug: str, records: List[Dict[str, Any]], auth: Dict[str, Any],
                   repo_facts: Optional[Dict[str, Any]],
                   advisories: Optional[Dict[str, Any]],
                   queries: List[str], states: List[str]) -> Dict[str, Any]:
    discussions_checked = bool(
        repo_facts and repo_facts.get("ok")
        and repo_facts.get("data", {}).get("hasDiscussionsEnabled") is False
    )
    confidence, notes = assess_confidence(records, auth, discussions_checked)

    hits = [
        {"query": r["query"], "kind": r["kind"], "state": r["state"],
         "match": item}
        for r in records if r.get("ok")
        for item in r.get("results", [])
    ]

    return {
        "schema": "contributor-scout/github-searches",
        "schema_version": "1.0.0",
        "script_version": SCRIPT_VERSION,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "repository": slug,
        "remote_access": auth,
        "repository_facts": repo_facts,
        "security_advisories": advisories,
        "queries_requested": queries,
        "states_searched": states,
        "query_count": len(records),
        "queries_with_results": len([r for r in records if r.get("result_count")]),
        "queries_with_zero_results": len(
            [r for r in records if r.get("ok") and not r.get("result_count")]),
        "searches": records,
        "all_matches": hits,
        "duplicate_detection_confidence": confidence,
        "confidence_notes": notes,
        "guidance": [
            "CLEAR requires a successful remote check of BOTH issues and pull "
            "requests in this run.",
            "Where remote access failed, use status UNKNOWN with confidence LOW.",
            "Zero-result queries are evidence - keep them in the record.",
            "Discussions are not covered by `gh search`; check them separately "
            "where enabled.",
        ],
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run read-only GitHub issue and pull-request searches for "
                    "duplicate detection (Contributor Scout, Phases 2 and 5).",
        epilog="Read-only: only `gh auth status`, `gh repo view`, `gh search`, "
               "and GET `gh api` calls are invoked. Nothing is ever created, "
               "edited, or commented on.",
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--repo-slug", help="Target repository as owner/name")
    source.add_argument("--repo", default=".",
                        help="Local clone to derive owner/name from (default: .)")
    parser.add_argument("--query", action="append", default=[], required=False,
                        help="Query variant; repeat for each variant "
                             "(8 or more is recommended)")
    parser.add_argument("--queries-file",
                        help="File with one query variant per line, added to --query")
    parser.add_argument("--state", default="all", choices=["all", "open", "closed"],
                        help="Issue/PR state to search (default: all)")
    parser.add_argument("--include-issues", dest="issues", action="store_true",
                        default=None, help="Search issues (default: on)")
    parser.add_argument("--no-issues", dest="issues", action="store_false",
                        help="Skip issue search")
    parser.add_argument("--include-prs", dest="prs", action="store_true",
                        default=None, help="Search pull requests (default: on)")
    parser.add_argument("--no-prs", dest="prs", action="store_false",
                        help="Skip pull-request search")
    parser.add_argument("--advisories", action="store_true",
                        help="Also fetch published security advisories")
    parser.add_argument("--limit", type=int, default=25,
                        help="Results per query (default: 25, max 100)")
    parser.add_argument("--output", help="Write JSON here (default: stdout)")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    queries: List[str] = list(args.query)
    if args.queries_file:
        path = Path(args.queries_file).expanduser()
        if not path.is_file():
            print("error: --queries-file not found: {0}".format(path), file=sys.stderr)
            return 1
        queries += [
            line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]

    # De-duplicate, preserving order.
    seen = set()
    queries = [q for q in queries if not (q in seen or seen.add(q))]

    if not queries:
        print("error: at least one --query or a --queries-file is required",
              file=sys.stderr)
        return 1
    if not 1 <= args.limit <= 100:
        print("error: --limit must be between 1 and 100", file=sys.stderr)
        return 1

    search_issues = True if args.issues is None else args.issues
    search_prs = True if args.prs is None else args.prs
    if not (search_issues or search_prs):
        print("error: nothing to search - do not pass both --no-issues and --no-prs",
              file=sys.stderr)
        return 1

    slug = args.repo_slug
    if not slug:
        repo_path = Path(args.repo).expanduser()
        if not repo_path.is_dir():
            print("error: --repo is not a directory: {0}".format(repo_path),
                  file=sys.stderr)
            return 1
        slug = derive_slug_from_clone(repo_path)
    if not slug:
        print("error: could not determine owner/name. Pass --repo-slug explicitly.",
              file=sys.stderr)
        return 1
    if not re.match(r"^[\w.-]+/[\w.-]+$", slug):
        print("error: --repo-slug must look like owner/name (got '{0}')".format(slug),
              file=sys.stderr)
        return 1

    auth = check_gh_auth()

    records: List[Dict[str, Any]] = []
    repo_facts: Optional[Dict[str, Any]] = None
    advisories: Optional[Dict[str, Any]] = None

    if auth.get("authenticated"):
        repo_facts = fetch_repo_facts(slug)
        for query in queries:
            if search_issues:
                records.append(search("issues", slug, query, args.state, args.limit))
            if search_prs:
                records.append(search("prs", slug, query, args.state, args.limit))
        if args.advisories:
            advisories = fetch_advisories(slug)
    else:
        print("warning: {0}".format(auth.get("reason")), file=sys.stderr)
        print("warning: running in degraded mode - duplicate status must be "
              "UNKNOWN with confidence LOW", file=sys.stderr)
        if auth.get("remedy"):
            print("hint: {0}".format(auth["remedy"]), file=sys.stderr)

    document = build_document(slug, records, auth, repo_facts, advisories,
                              queries, [args.state])
    payload = json.dumps(document, indent=args.indent)

    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
        print("wrote {0} ({1} queries, confidence {2})".format(
            output_path, document["query_count"],
            document["duplicate_detection_confidence"]))
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
