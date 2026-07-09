#!/usr/bin/env python3
import argparse
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

REPOS = {
    "KB-iGOT/cbp-ai-ui": "git@github.com:KB-iGOT/cbp-ai-ui.git",
    "KB-iGOT/SunbirdEd-portal": "git@github.com:KB-iGOT/SunbirdEd-portal.git",
}

def run(cmd, cwd=None, check=True):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and p.returncode != 0:
        print(p.stderr)
        sys.exit(p.returncode)
    return p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--old", required=True)
    ap.add_argument("--current", required=True)
    args = ap.parse_args()

    if args.repo not in REPOS:
        print(f"Unknown repo: {args.repo}")
        print("Update REPOS dictionary in release_validation.py")
        sys.exit(1)

    work = tempfile.mkdtemp(prefix="release_validation_")
    try:
        print("="*60)
        print("RELEASE VALIDATION REPORT")
        print("="*60)
        print(f"Repository      : {args.repo}")
        print(f"Old Release     : {args.old}")
        print(f"Current Release : {args.current}")
        print()

        run(["git","clone","--quiet",REPOS[args.repo],work])

        run(["git","fetch","--all","--tags"], cwd=work)

        for ref in (args.old,args.current):
            run(["git","rev-parse","--verify",ref], cwd=work)

        anc = subprocess.run(
            ["git","merge-base","--is-ancestor",args.old,args.current],
            cwd=work
        )

        if anc.returncode == 0:
            print("✓ Current release contains previous release history.\n")
        else:
            print("✗ Current release is NOT a descendant of previous release.\n")

        res = run([
            "git","log",
            f"{args.current}..{args.old}",
            "--pretty=format:%h|%an|%ad|%s",
            "--date=short"
        ], cwd=work, check=False)

        if not res.stdout.strip():
            print("SUCCESS: No missing commits detected.")
            sys.exit(0)

        print("Missing commits:\n")
        for line in res.stdout.splitlines():
            sha, author, date, msg = line.split("|",3)
            print("-"*60)
            print("Commit :", sha)
            print("Author :", author)
            print("Date   :", date)
            print("Message:", msg)

        print("\nFAILED: Missing commits detected.")
        sys.exit(2)

    finally:
        shutil.rmtree(work, ignore_errors=True)

if __name__ == "__main__":
    main()
