#!/usr/bin/env python3

import argparse
import csv
import os
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote

GITHUB_BASE = "https://github.com"


def run(cmd, cwd=None, check=True):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True
    )

    if check and result.returncode != 0:
        if result.stderr.strip():
            print(result.stderr.strip())
        sys.exit(result.returncode)

    return result


def resolve_ref(repo_dir, ref):
    """
    Resolve whether the supplied ref is
    - local branch
    - remote branch
    - tag
    """

    # local branch
    r = run(
        ["git", "rev-parse", "--verify", ref],
        cwd=repo_dir,
        check=False
    )

    if r.returncode == 0:
        return ref

    # remote branch
    r = run(
        ["git", "rev-parse", "--verify", f"origin/{ref}"],
        cwd=repo_dir,
        check=False
    )

    if r.returncode == 0:
        return f"origin/{ref}"

    # tag
    r = run(
        ["git", "rev-parse", "--verify", f"refs/tags/{ref}"],
        cwd=repo_dir,
        check=False
    )

    if r.returncode == 0:
        return f"refs/tags/{ref}"

    return None


def print_header():
    return ["=" * 70, "RELEASE VALIDATION REPORT", "=" * 70]


def get_github_credentials():
    username = os.environ.get("GITHUB_USERNAME") or os.environ.get("GITHUB_USER")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
    return username, token


def build_repo_url(repo, username=None, token=None):
    if repo.startswith(("http://", "https://", "ssh://", "git@")):
        return repo

    expanded_repo = os.path.expanduser(repo)
    if os.path.exists(expanded_repo) or repo.startswith("/"):
        return os.path.abspath(expanded_repo)

    repo_url = f"{GITHUB_BASE}/{repo}.git"

    if username and token:
        encoded_user = quote(username, safe="")
        encoded_token = quote(token, safe="")
        return f"https://{encoded_user}:{encoded_token}@github.com/{repo}.git"

    return repo_url


def format_repo_display(repo):
    if repo.startswith(("http://", "https://", "ssh://", "git@")):
        return repo

    expanded_repo = os.path.expanduser(repo)
    if os.path.exists(expanded_repo) or repo.startswith("/"):
        return os.path.abspath(expanded_repo)

    return f"{GITHUB_BASE}/{repo}.git"


def parse_comparison_rows(csv_path):
    comparisons = []

    with open(csv_path, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))

    if not rows:
        return comparisons

    first_row = [cell.strip() for cell in rows[0]]
    normalized_header = [cell.lower().replace(" ", "_") for cell in first_row]

    if any(name in normalized_header for name in ["repo", "repository", "repo_name"]):
        header = normalized_header
        data_rows = rows[1:]
    else:
        header = ["repo", "old", "current"]
        data_rows = rows

    repo_index = None
    old_index = None
    current_index = None

    for name in ["repo", "repository", "repo_name"]:
        if name in header:
            repo_index = header.index(name)
            break

    for name in ["old", "old_release", "previous", "previous_release"]:
        if name in header:
            old_index = header.index(name)
            break

    for name in ["current", "current_release", "new", "new_release"]:
        if name in header:
            current_index = header.index(name)
            break

    if repo_index is None:
        repo_index = 0
    if old_index is None:
        old_index = 1 if len(header) > 1 else None
    if current_index is None:
        current_index = 2 if len(header) > 2 else None

    for row in data_rows:
        if not row:
            continue

        values = [cell.strip() for cell in row]
        repo = values[repo_index] if repo_index is not None and repo_index < len(values) else ""
        old_release = values[old_index] if old_index is not None and old_index < len(values) else ""
        current_release = values[current_index] if current_index is not None and current_index < len(values) else ""

        if repo and old_release and current_release:
            comparisons.append({
                "repo": repo,
                "old": old_release,
                "current": current_release,
            })

    return comparisons


def get_cherry_pick_statuses(repo_dir, current_ref, old_ref, commit_shas):
    statuses = {}

    if not commit_shas:
        return statuses

    cherry_output = run(
        ["git", "cherry", current_ref, old_ref],
        cwd=repo_dir,
        check=False
    )

    if cherry_output.returncode != 0:
        for sha in commit_shas:
            statuses[sha] = "unknown"
        return statuses

    for line in cherry_output.stdout.splitlines():
        line = line.strip()
        if not line:
            continue

        marker = line[0]
        if marker not in {"-", "+"}:
            continue

        parts = line[1:].strip().split(None, 1)
        if not parts:
            continue

        sha = parts[0]
        statuses[sha] = "cherry-picked" if marker == "-" else "not-cherry-picked"

    for sha in commit_shas:
        statuses.setdefault(sha, "unknown")

    return statuses


def compare_repo(repo, old_release, current_release, username=None, token=None):
    report_lines = []

    def add(line):
        report_lines.append(line)

    repo_url = build_repo_url(repo, username, token)
    display_repo_url = format_repo_display(repo)

    add("\n".join(print_header()))
    add(f"Repository      : {repo}")
    add(f"Repository URL  : {display_repo_url}")
    add(f"Old Release     : {old_release}")
    add(f"Current Release : {current_release}")
    add("")

    tempdir = tempfile.mkdtemp(prefix="release_validation_")

    try:
        add("Cloning repository...")
        clone_result = run(
            [
                "git",
                "clone",
                "--quiet",
                "--no-single-branch",
                repo_url,
                tempdir
            ],
            check=False
        )

        if clone_result.returncode != 0:
            add("ERROR: Unable to clone the repository.")
            if clone_result.stderr.strip():
                add(clone_result.stderr.strip())
            return {"status": "error", "report_lines": report_lines}

        add("Fetching latest branches and tags...")
        fetch_result = run(
            [
                "git",
                "fetch",
                "--all",
                "--tags",
                "--prune"
            ],
            cwd=tempdir,
            check=False
        )

        if fetch_result.returncode != 0:
            add("ERROR: Unable to fetch branches and tags.")
            if fetch_result.stderr.strip():
                add(fetch_result.stderr.strip())
            return {"status": "error", "report_lines": report_lines}

        old_ref = resolve_ref(tempdir, old_release)
        current_ref = resolve_ref(tempdir, current_release)

        if old_ref is None:
            add(f"ERROR: {old_release} not found.")
            return {"status": "error", "report_lines": report_lines}

        if current_ref is None:
            add(f"ERROR: {current_release} not found.")
            return {"status": "error", "report_lines": report_lines}

        add(f"Old Ref     : {old_ref}")
        add(f"Current Ref : {current_ref}")

        ancestor = subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                old_ref,
                current_ref
            ],
            cwd=tempdir,
            capture_output=True,
            text=True
        )

        if ancestor.returncode == 0:
            add("✓ Previous release is ancestor of current release")
        else:
            add("✗ Previous release is NOT ancestor of current release")

        add("")
        add("Checking missing commits...")
        add("")

        log = run(
            [
                "git",
                "log",
                f"{current_ref}..{old_ref}",
                "--pretty=format:%H|%an|%ad|%s",
                "--date=short"
            ],
            cwd=tempdir,
            check=False
        )

        if not log.stdout.strip():
            add("SUCCESS")
            add("No missing commits found.")
            return {"status": "success", "report_lines": report_lines}

        add("Missing Commits")
        add("-" * 70)

        commit_rows = [line for line in log.stdout.splitlines() if line.strip()]
        commit_shas = []

        for line in commit_rows:
            sha, author, date, message = line.split("|", 3)
            commit_shas.append(sha)

        cherry_pick_statuses = get_cherry_pick_statuses(
            tempdir,
            current_ref,
            old_ref,
            commit_shas
        )

        for line in commit_rows:
            sha, author, date, message = line.split("|", 3)
            status = cherry_pick_statuses.get(sha, "unknown")

            add(f"Commit : {sha}")
            add(f"Author : {author}")
            add(f"Date   : {date}")
            add(f"Message: {message}")
            add(f"Cherry-pick status : {status}")

            files = run(
                [
                    "git",
                    "show",
                    "--pretty=",
                    "--name-only",
                    sha
                ],
                cwd=tempdir,
                check=False
            )

            add("Files Changed")

            for file_name in files.stdout.splitlines():
                if file_name.strip():
                    add(f"   - {file_name}")

            add("-" * 70)

        add("Cherry-pick summary")
        add("-" * 70)
        add(f"Cherry-picked        : {sum(1 for value in cherry_pick_statuses.values() if value == 'cherry-picked')}")
        add(f"Not cherry-picked    : {sum(1 for value in cherry_pick_statuses.values() if value == 'not-cherry-picked')}")
        add(f"Unknown status       : {sum(1 for value in cherry_pick_statuses.values() if value == 'unknown')}")

        return {"status": "missing_commits", "report_lines": report_lines}

    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--repo")
    parser.add_argument("--old")
    parser.add_argument("--current")
    parser.add_argument("--csv", help="CSV file with repo, old, current columns")
    parser.add_argument("--report-file", help="Optional file to write the combined report")

    args = parser.parse_args()

    username, token = get_github_credentials()

    if args.csv:
        comparisons = parse_comparison_rows(args.csv)
        if not comparisons:
            print("ERROR: No repositories found in CSV input.")
            sys.exit(2)
    else:
        if not args.repo or not args.old or not args.current:
            parser.error("Provide --repo, --old, and --current, or use --csv")
        comparisons = [{"repo": args.repo, "old": args.old, "current": args.current}]

    report_lines = []
    success_count = 0
    missing_commits_count = 0
    error_count = 0

    for index, item in enumerate(comparisons, start=1):
        if index > 1:
            report_lines.append("")

        result = compare_repo(item["repo"], item["old"], item["current"], username, token)
        report_lines.extend(result["report_lines"])

        if result["status"] == "success":
            success_count += 1
        elif result["status"] == "missing_commits":
            missing_commits_count += 1
        else:
            error_count += 1

    report_lines.append("")
    report_lines.append("SUMMARY")
    report_lines.append("-" * 70)
    report_lines.append(f"Total repositories: {len(comparisons)}")
    report_lines.append(f"Successful: {success_count}")
    report_lines.append(f"Missing commits: {missing_commits_count}")
    report_lines.append(f"Errors: {error_count}")

    for line in report_lines:
        print(line)

    if args.report_file:
        with open(args.report_file, "w", encoding="utf-8") as handle:
            handle.write("\n".join(report_lines))
        print(f"Report written to {args.report_file}")

    if error_count:
        sys.exit(2)

    if missing_commits_count:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()