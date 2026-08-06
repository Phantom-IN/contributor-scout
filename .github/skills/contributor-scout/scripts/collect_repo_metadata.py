#!/usr/bin/env python3
"""Collect read-only structural metadata about a cloned repository.

Part of the Contributor Scout skill (Phase 0: repository eligibility).

Emits a JSON document describing the repository root, detected languages,
manifests, build/test/CI configuration, contribution policy files, licence,
Git head/tags/branches, and the commands the project most likely uses for
testing, linting, and benchmarking.

The script is strictly read-only:
  * it never writes inside the analysed repository (output goes to --output or
    stdout, and --output is rejected if it resolves inside the repo unless
    --allow-output-inside-repo is passed for the discovery directory);
  * it never runs build, test, install, or network commands - it only *detects*
    which commands exist;
  * the only external process it invokes is `git`, with read-only subcommands.

Usage
-----
    python3 collect_repo_metadata.py --repo .
    python3 collect_repo_metadata.py --repo /path/to/clone \\
        --output contribution-discovery/machine-readable/repository-profile.json

Exit codes
----------
    0  metadata collected
    1  bad arguments or unreadable repository
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
from typing import Any, Dict, List, Optional

SCRIPT_VERSION = "1.0.0"

# Directories never worth walking for language/manifest detection.
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "third_party", "dist",
    "build", "target", "out", ".venv", "venv", "__pycache__", ".tox", ".nox",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".gradle", ".idea",
    ".next", ".nuxt", "coverage", "site-packages", ".terraform",
    "contribution-discovery",
}

LANGUAGE_BY_EXT = {
    ".py": "Python", ".pyi": "Python", ".js": "JavaScript", ".mjs": "JavaScript",
    ".cjs": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".go": "Go", ".rs": "Rust", ".java": "Java",
    ".kt": "Kotlin", ".rb": "Ruby", ".php": "PHP", ".c": "C", ".h": "C/C++ header",
    ".cc": "C++", ".cpp": "C++", ".cxx": "C++", ".hpp": "C++ header",
    ".cs": "C#", ".swift": "Swift", ".m": "Objective-C", ".scala": "Scala",
    ".ex": "Elixir", ".exs": "Elixir", ".erl": "Erlang", ".hs": "Haskell",
    ".lua": "Lua", ".pl": "Perl", ".r": "R", ".dart": "Dart", ".zig": "Zig",
    ".sh": "Shell", ".bash": "Shell", ".ps1": "PowerShell", ".sql": "SQL",
}

# filename -> (category, ecosystem)
KNOWN_FILES = {
    # manifests
    "package.json": ("manifest", "node"),
    "pyproject.toml": ("manifest", "python"),
    "setup.py": ("manifest", "python"),
    "setup.cfg": ("manifest", "python"),
    "requirements.txt": ("manifest", "python"),
    "Pipfile": ("manifest", "python"),
    "go.mod": ("manifest", "go"),
    "Cargo.toml": ("manifest", "rust"),
    "pom.xml": ("manifest", "java"),
    "build.gradle": ("manifest", "java"),
    "build.gradle.kts": ("manifest", "java"),
    "Gemfile": ("manifest", "ruby"),
    "composer.json": ("manifest", "php"),
    "mix.exs": ("manifest", "elixir"),
    "pubspec.yaml": ("manifest", "dart"),
    "CMakeLists.txt": ("manifest", "cmake"),
    # lockfiles
    "package-lock.json": ("lockfile", "node"),
    "yarn.lock": ("lockfile", "node"),
    "pnpm-lock.yaml": ("lockfile", "node"),
    "poetry.lock": ("lockfile", "python"),
    "uv.lock": ("lockfile", "python"),
    "Cargo.lock": ("lockfile", "rust"),
    "go.sum": ("lockfile", "go"),
    "Gemfile.lock": ("lockfile", "ruby"),
    "composer.lock": ("lockfile", "php"),
    # build / task runners
    "Makefile": ("build", "make"),
    "makefile": ("build", "make"),
    "justfile": ("build", "just"),
    "Justfile": ("build", "just"),
    "Taskfile.yml": ("build", "task"),
    "noxfile.py": ("build", "nox"),
    "tox.ini": ("build", "tox"),
    "Rakefile": ("build", "rake"),
    "meson.build": ("build", "meson"),
    "BUILD.bazel": ("build", "bazel"),
    "WORKSPACE": ("build", "bazel"),
    # test configuration
    "pytest.ini": ("test-config", "python"),
    "conftest.py": ("test-config", "python"),
    "jest.config.js": ("test-config", "node"),
    "jest.config.ts": ("test-config", "node"),
    "vitest.config.ts": ("test-config", "node"),
    "karma.conf.js": ("test-config", "node"),
    "phpunit.xml": ("test-config", "php"),
    # lint / type / format
    ".eslintrc": ("lint", "node"),
    ".eslintrc.js": ("lint", "node"),
    ".eslintrc.json": ("lint", "node"),
    "eslint.config.js": ("lint", "node"),
    ".flake8": ("lint", "python"),
    ".pylintrc": ("lint", "python"),
    "ruff.toml": ("lint", "python"),
    ".ruff.toml": ("lint", "python"),
    "mypy.ini": ("types", "python"),
    ".golangci.yml": ("lint", "go"),
    ".golangci.yaml": ("lint", "go"),
    "rustfmt.toml": ("lint", "rust"),
    "clippy.toml": ("lint", "rust"),
    ".rubocop.yml": ("lint", "ruby"),
    ".pre-commit-config.yaml": ("lint", "generic"),
    # contribution / policy
    "CONTRIBUTING.md": ("policy", "contributing"),
    "CONTRIBUTING.rst": ("policy", "contributing"),
    "CONTRIBUTING": ("policy", "contributing"),
    "CODE_OF_CONDUCT.md": ("policy", "code-of-conduct"),
    "SECURITY.md": ("policy", "security"),
    "SECURITY.rst": ("policy", "security"),
    "GOVERNANCE.md": ("policy", "governance"),
    "MAINTAINERS.md": ("policy", "maintainers"),
    "MAINTAINERS": ("policy", "maintainers"),
    "CODEOWNERS": ("policy", "codeowners"),
    "CHANGELOG.md": ("policy", "changelog"),
    "CHANGELOG.rst": ("policy", "changelog"),
    "CHANGES.md": ("policy", "changelog"),
    "ROADMAP.md": ("policy", "roadmap"),
    "README.md": ("policy", "readme"),
    "README.rst": ("policy", "readme"),
    # static analysis
    ".semgrep.yml": ("static-analysis", "semgrep"),
    "codeql-config.yml": ("static-analysis", "codeql"),
    ".bandit": ("static-analysis", "bandit"),
    "sonar-project.properties": ("static-analysis", "sonar"),
}

LICENCE_PATTERNS = [
    ("Apache-2.0", r"Apache License\s*\n?\s*Version 2\.0"),
    ("MIT", r"\bMIT License\b|Permission is hereby granted, free of charge"),
    ("BSD-3-Clause", r"Redistributions of source code must retain.*3\.|BSD 3-Clause"),
    ("BSD-2-Clause", r"BSD 2-Clause"),
    ("GPL-3.0", r"GNU GENERAL PUBLIC LICENSE\s*\n?\s*Version 3"),
    ("GPL-2.0", r"GNU GENERAL PUBLIC LICENSE\s*\n?\s*Version 2"),
    ("LGPL-3.0", r"GNU LESSER GENERAL PUBLIC LICENSE\s*\n?\s*Version 3"),
    ("AGPL-3.0", r"GNU AFFERO GENERAL PUBLIC LICENSE"),
    ("MPL-2.0", r"Mozilla Public License Version 2\.0"),
    ("ISC", r"\bISC License\b"),
    ("Unlicense", r"This is free and unencumbered software released into the public domain"),
]


# --------------------------------------------------------------------------- #
# process helpers
# --------------------------------------------------------------------------- #

def run(cmd: List[str], cwd: Path, timeout: int = 20) -> Optional[str]:
    """Run a read-only command, returning stripped stdout or None on failure."""
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def have(binary: str) -> bool:
    """True if a binary is on PATH."""
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if directory and (Path(directory) / binary).exists():
            return True
    return False


# --------------------------------------------------------------------------- #
# collectors
# --------------------------------------------------------------------------- #

def collect_git(repo: Path) -> Dict[str, Any]:
    """Read-only Git facts. Every subcommand here is non-mutating."""
    if not (repo / ".git").exists():
        return {"is_git_repository": False}

    info: Dict[str, Any] = {"is_git_repository": True}
    info["head"] = run(["git", "rev-parse", "HEAD"], repo)
    info["head_short"] = run(["git", "rev-parse", "--short", "HEAD"], repo)
    info["branch"] = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo)
    info["is_shallow"] = (run(["git", "rev-parse", "--is-shallow-repository"], repo) == "true")

    remotes_raw = run(["git", "remote", "-v"], repo) or ""
    remotes: Dict[str, str] = {}
    for line in remotes_raw.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            remotes.setdefault(parts[0], parts[1])
    info["remotes"] = remotes
    info["owner_repo"] = derive_owner_repo(remotes.get("origin", ""))

    last = run(["git", "log", "-1", "--format=%H%x1f%an%x1f%aI%x1f%s"], repo)
    if last:
        fields = last.split("\x1f")
        if len(fields) == 4:
            info["last_commit"] = {
                "sha": fields[0], "author": fields[1],
                "date": fields[2], "subject": fields[3],
            }

    for key, since in (("commits_last_90_days", "90 days ago"),
                       ("commits_last_180_days", "180 days ago"),
                       ("commits_last_365_days", "365 days ago")):
        out = run(["git", "rev-list", "--count", "--since=" + since, "HEAD"], repo)
        info[key] = int(out) if out and out.isdigit() else None

    shortlog = run(
        ["git", "shortlog", "-sne", "--since=365 days ago", "HEAD"], repo
    )
    if shortlog is not None:
        authors = []
        for line in shortlog.splitlines()[:25]:
            m = re.match(r"\s*(\d+)\s+(.*)", line)
            if m:
                authors.append({"commits": int(m.group(1)), "author": m.group(2)})
        info["active_authors_last_365_days"] = len(authors)
        info["top_authors"] = authors[:10]

    tags = run(["git", "tag", "--sort=-creatordate"], repo)
    tag_list = tags.splitlines() if tags else []
    info["tag_count"] = len(tag_list)
    info["recent_tags"] = tag_list[:10]

    branches = run(["git", "branch", "-r", "--sort=-committerdate"], repo)
    info["recent_remote_branches"] = (
        [b.strip() for b in branches.splitlines()[:15]] if branches else []
    )

    # Churn: files changed most in the last year - a proxy for "what matters".
    churn_raw = run(
        ["git", "log", "--since=365 days ago", "--name-only",
         "--pretty=format:", "--no-merges"], repo, timeout=60,
    )
    if churn_raw:
        counts: Dict[str, int] = {}
        for line in churn_raw.splitlines():
            name = line.strip()
            if name:
                counts[name] = counts.get(name, 0) + 1
        info["highest_churn_files"] = [
            {"path": p, "commits": c}
            for p, c in sorted(counts.items(), key=lambda kv: -kv[1])[:20]
        ]
    return info


def derive_owner_repo(remote_url: str) -> Optional[str]:
    """Extract 'owner/name' from an https or ssh remote URL."""
    if not remote_url:
        return None
    m = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", remote_url.strip())
    if not m:
        return None
    return "{0}/{1}".format(m.group(1), m.group(2))


def walk_repo(repo: Path, max_files: int) -> Dict[str, Any]:
    """Single filesystem walk collecting languages, known files, and size."""
    languages: Dict[str, int] = {}
    known: Dict[str, List[str]] = {}
    ci_files: List[str] = []
    test_dirs: List[str] = []
    total_files = 0
    truncated = False

    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        rel_dir = Path(dirpath).relative_to(repo)

        base = rel_dir.name.lower()
        if base in {"test", "tests", "spec", "specs", "__tests__", "testing"}:
            test_dirs.append(str(rel_dir))

        in_ci_dir = str(rel_dir).replace(os.sep, "/") in {
            ".github/workflows", ".circleci", ".gitlab", ".buildkite",
        }

        for filename in filenames:
            total_files += 1
            if total_files > max_files:
                truncated = True
                break

            rel_path = str(rel_dir / filename) if str(rel_dir) != "." else filename
            rel_path = rel_path.replace(os.sep, "/")

            ext = Path(filename).suffix.lower()
            if ext in LANGUAGE_BY_EXT:
                lang = LANGUAGE_BY_EXT[ext]
                languages[lang] = languages.get(lang, 0) + 1

            if filename in KNOWN_FILES:
                category = KNOWN_FILES[filename][0]
                known.setdefault(category, []).append(rel_path)

            if in_ci_dir and ext in {".yml", ".yaml"}:
                ci_files.append(rel_path)
            elif filename in {".gitlab-ci.yml", "azure-pipelines.yml", ".travis.yml",
                              "appveyor.yml", "Jenkinsfile", ".drone.yml"}:
                ci_files.append(rel_path)

        if truncated:
            break

    return {
        "total_files_scanned": total_files,
        "scan_truncated": truncated,
        "languages": dict(sorted(languages.items(), key=lambda kv: -kv[1])),
        "primary_language": next(iter(sorted(languages.items(), key=lambda kv: -kv[1])), (None, 0))[0],
        "known_files": {k: sorted(v) for k, v in sorted(known.items())},
        "ci_files": sorted(ci_files),
        "test_directories": sorted(set(test_dirs)),
    }


def detect_licence(repo: Path) -> Dict[str, Any]:
    """Identify the licence file and take a conservative guess at the SPDX id."""
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE",
                 "LICENCE.md", "COPYING", "COPYING.txt", "LICENSE-MIT",
                 "LICENSE-APACHE"):
        path = repo / name
        if not path.is_file():
            continue
        try:
            head = path.read_text(encoding="utf-8", errors="replace")[:4000]
        except OSError:
            return {"file": name, "detected": None, "note": "unreadable"}
        for spdx, pattern in LICENCE_PATTERNS:
            if re.search(pattern, head, re.IGNORECASE):
                return {"file": name, "detected": spdx, "confidence": "heuristic"}
        return {"file": name, "detected": None, "confidence": "heuristic",
                "note": "licence file present but not recognised"}
    return {"file": None, "detected": None,
            "note": "no licence file found at repository root - verify manually"}


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def detect_commands(repo: Path, walked: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """Detect likely test/lint/build/benchmark commands. Never runs them."""
    commands: Dict[str, List[Dict[str, str]]] = {
        "test": [], "lint": [], "typecheck": [], "build": [],
        "benchmark": [], "static_analysis": [],
    }

    def add(kind: str, command: str, source: str) -> None:
        entry = {"command": command, "source": source}
        if entry not in commands[kind]:
            commands[kind].append(entry)

    known = walked.get("known_files", {})
    manifests = set(known.get("manifest", []))
    build_files = set(known.get("build", []))
    test_configs = set(known.get("test-config", []))

    # Real root filenames, so case-insensitive filesystems do not report both
    # "Makefile" and "makefile" for the same file.
    try:
        root_names = set(os.listdir(repo))
    except OSError:
        root_names = set()

    # Node: read the scripts block rather than guessing.
    if "package.json" in manifests:
        pkg = read_json(repo / "package.json") or {}
        scripts = pkg.get("scripts") or {}
        runner = "npm run"
        if (repo / "pnpm-lock.yaml").exists():
            runner = "pnpm run"
        elif (repo / "yarn.lock").exists():
            runner = "yarn"
        for name in scripts:
            lowered = name.lower()
            target = None
            if lowered in {"test", "tests"} or lowered.startswith("test:"):
                target = "test"
            elif "bench" in lowered:
                target = "benchmark"
            elif lowered.startswith("lint") or lowered == "format:check":
                target = "lint"
            elif lowered in {"typecheck", "types", "tsc"} or "typecheck" in lowered:
                target = "typecheck"
            elif lowered in {"build", "compile"}:
                target = "build"
            if target:
                add(target, "{0} {1}".format(runner, name), "package.json scripts.{0}".format(name))

    if manifests & {"pyproject.toml", "setup.py", "setup.cfg"} or "pytest.ini" in test_configs:
        add("test", "python -m pytest", "python project layout")
    if "tox.ini" in build_files:
        add("test", "tox", "tox.ini")
    if "noxfile.py" in build_files:
        add("test", "nox", "noxfile.py")
    if (repo / "ruff.toml").exists() or (repo / ".ruff.toml").exists():
        add("lint", "ruff check .", "ruff configuration")
    if (repo / "mypy.ini").exists():
        add("typecheck", "mypy .", "mypy.ini")
    if (repo / ".pre-commit-config.yaml").exists():
        add("lint", "pre-commit run --all-files", ".pre-commit-config.yaml")

    if "go.mod" in manifests:
        add("test", "go test ./...", "go.mod")
        add("benchmark", "go test -bench=. ./...", "go.mod")
        add("lint", "go vet ./...", "go.mod")
    if "Cargo.toml" in manifests:
        add("test", "cargo test", "Cargo.toml")
        add("benchmark", "cargo bench", "Cargo.toml")
        add("lint", "cargo clippy", "Cargo.toml")
        add("build", "cargo build", "Cargo.toml")
    if "Gemfile" in manifests:
        add("test", "bundle exec rspec", "Gemfile")
    if "pom.xml" in manifests:
        add("test", "mvn test", "pom.xml")
    if any(g in manifests for g in ("build.gradle", "build.gradle.kts")):
        add("test", "./gradlew test", "gradle build file")
    if "composer.json" in manifests:
        add("test", "vendor/bin/phpunit", "composer.json")
    if "mix.exs" in manifests:
        add("test", "mix test", "mix.exs")

    # Makefile / justfile targets, parsed textually.
    for build_name, pattern, prefix in (
        ("Makefile", r"^([a-zA-Z0-9_.-]+):(?!=)", "make "),
        ("makefile", r"^([a-zA-Z0-9_.-]+):(?!=)", "make "),
        ("justfile", r"^([a-zA-Z0-9_-]+)(?:\s+[^:]*)?:", "just "),
        ("Justfile", r"^([a-zA-Z0-9_-]+)(?:\s+[^:]*)?:", "just "),
    ):
        if build_name not in root_names:
            continue
        path = repo / build_name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[:60000]
        except OSError:
            continue
        for target in re.findall(pattern, text, re.MULTILINE):
            lowered = target.lower()
            if lowered in {"test", "check", "tests"}:
                add("test", prefix + target, build_name)
            elif "bench" in lowered:
                add("benchmark", prefix + target, build_name)
            elif lowered in {"lint", "fmt-check", "format-check"}:
                add("lint", prefix + target, build_name)
            elif lowered in {"typecheck", "mypy", "types"}:
                add("typecheck", prefix + target, build_name)
            elif lowered in {"build", "all", "compile"}:
                add("build", prefix + target, build_name)

    if known.get("static-analysis"):
        for path in known["static-analysis"]:
            add("static_analysis", "(configured) " + path, path)

    return commands


def find_security_policy(repo: Path, walked: Dict[str, Any]) -> Dict[str, Any]:
    """Locate a security policy and extract a plausible contact line."""
    candidates = [
        p for p in walked.get("known_files", {}).get("policy", [])
        if Path(p).name.upper().startswith("SECURITY")
    ]
    for extra in ("SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md"):
        if (repo / extra).is_file() and extra not in candidates:
            candidates.append(extra)
    if not candidates:
        return {"present": False, "path": None, "contacts": [],
                "note": "no SECURITY policy found - use a private channel anyway; "
                        "do not default to a public issue"}

    path = repo / candidates[0]
    contacts: List[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:20000]
        contacts += re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
        contacts += re.findall(r"https?://[^\s)>\]]+", text)
    except OSError:
        text = ""
    # De-duplicate while preserving order.
    seen = set()
    unique = [c for c in contacts if not (c in seen or seen.add(c))]
    return {"present": True, "path": candidates[0], "contacts": unique[:10]}


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def build_metadata(repo: Path, max_files: int) -> Dict[str, Any]:
    walked = walk_repo(repo, max_files)
    return {
        "schema": "contributor-scout/repository-profile",
        "schema_version": "1.0.0",
        "script_version": SCRIPT_VERSION,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(repo),
        "git": collect_git(repo),
        "licence": detect_licence(repo),
        "security_policy": find_security_policy(repo, walked),
        "inventory": walked,
        "likely_commands": detect_commands(repo, walked),
        "tooling_available": {
            "git": have("git"),
            "gh": have("gh"),
            "python3": True,
        },
        "notes": [
            "All detected commands are candidates only - none were executed.",
            "Read what a command does before running it (see SKILL.md sandbox check).",
            "Licence detection is heuristic; confirm the SPDX identifier manually.",
        ],
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect read-only metadata about a cloned repository "
                    "(Contributor Scout, Phase 0).",
        epilog="This script never modifies the analysed repository and never "
               "runs build, test, or install commands.",
    )
    parser.add_argument("--repo", default=".", help="Repository root (default: .)")
    parser.add_argument("--output", help="Write JSON here (default: stdout)")
    parser.add_argument("--max-files", type=int, default=200000,
                        help="Cap on files walked (default: 200000)")
    parser.add_argument("--indent", type=int, default=2, help="JSON indent (default: 2)")
    parser.add_argument("--allow-output-inside-repo", action="store_true",
                        help="Permit --output inside the repository. Only use this "
                             "for paths under contribution-discovery/.")
    return parser.parse_args(argv)


def validate_output_path(output: Path, repo: Path, allow_inside: bool) -> Optional[str]:
    """Refuse to write into the analysed repository outside the discovery dir."""
    try:
        relative = output.resolve().relative_to(repo.resolve())
    except ValueError:
        return None  # outside the repository - always fine
    first = relative.parts[0] if relative.parts else ""
    if first == "contribution-discovery" or allow_inside:
        return None
    return (
        "refusing to write inside the analysed repository at '{0}'. Write to "
        "contribution-discovery/ or pass --allow-output-inside-repo.".format(relative)
    )


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    repo = Path(args.repo).expanduser()
    if not repo.is_dir():
        print("error: --repo is not a directory: {0}".format(repo), file=sys.stderr)
        return 1
    if args.max_files < 1:
        print("error: --max-files must be positive", file=sys.stderr)
        return 1

    output_path: Optional[Path] = None
    if args.output:
        output_path = Path(args.output).expanduser()
        problem = validate_output_path(output_path, repo, args.allow_output_inside_repo)
        if problem:
            print("error: " + problem, file=sys.stderr)
            return 1

    metadata = build_metadata(repo.resolve(), args.max_files)
    payload = json.dumps(metadata, indent=args.indent, sort_keys=False)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
        print("wrote {0}".format(output_path))
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
