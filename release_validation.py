#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys
import tempfile

GITHUB_BASE = "https://github.com"


def run(cmd, cwd=None, check=True):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True
    )

    if check and result.returncode != 0:
        print(result.stderr)
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
    print("=" * 70)
    print("RELEASE VALIDATION REPORT")
    print("=" * 70)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--repo", required=True)
    parser.add_argument("--old", required=True)
    parser.add_argument("--current", required=True)

    args = parser.parse_args()

    repo_url = f"{GITHUB_BASE}/{args.repo}.git"

    print_header()

    print(f"Repository      : {args.repo}")
    print(f"Repository URL  : {repo_url}")
    print(f"Old Release     : {args.old}")
    print(f"Current Release : {args.current}")
    print()

    tempdir = tempfile.mkdtemp(prefix="release_validation_")

    try:

        print("Cloning repository...")

        run([
            "git",
            "clone",
            "--quiet",
            "--no-single-branch",
            repo_url,
            tempdir
        ])

        print("Fetching latest branches and tags...")

        run(
            [
                "git",
                "fetch",
                "--all",
                "--tags",
                "--prune"
            ],
            cwd=tempdir
        )

        old_ref = resolve_ref(tempdir, args.old)
        current_ref = resolve_ref(tempdir, args.current)

        if old_ref is None:
            print(f"\nERROR : {args.old} not found.")
            sys.exit(2)

        if current_ref is None:
            print(f"\nERROR : {args.current} not found.")
            sys.exit(2)

        print(f"\nOld Ref     : {old_ref}")
        print(f"Current Ref : {current_ref}")

        ancestor = subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                old_ref,
                current_ref
            ],
            cwd=tempdir
        )

        if ancestor.returncode == 0:
            print("\n✓ Previous release is ancestor of current release")
        else:
            print("\n✗ Previous release is NOT ancestor of current release")

        print("\nChecking missing commits...\n")

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
            print("SUCCESS")
            print("No missing commits found.")
            sys.exit(0)

        print("Missing Commits")
        print("-" * 70)

        for line in log.stdout.splitlines():

            sha, author, date, message = line.split("|", 3)

            print(f"Commit : {sha}")
            print(f"Author : {author}")
            print(f"Date   : {date}")
            print(f"Message: {message}")

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

            print("Files Changed")

            for f in files.stdout.splitlines():
                if f.strip():
                    print(f"   - {f}")

            print("-" * 70)

        sys.exit(1)

    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


if __name__ == "__main__":
    main()