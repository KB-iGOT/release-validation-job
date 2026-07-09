#!/usr/bin/env python3
import argparse, subprocess, sys, tempfile, shutil
BASE="https://github.com"
def run(cmd,cwd=None):
    return subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
p=argparse.ArgumentParser()
p.add_argument("--repo",required=True)
p.add_argument("--old",required=True)
p.add_argument("--current",required=True)
a=p.parse_args()
url=f"{BASE}/{a.repo}.git"
tmp=tempfile.mkdtemp()
try:
    print(f"Repository : {a.repo}")
    print(f"URL        : {url}")
    if run(["git","clone",url,tmp]).returncode!=0:
        sys.exit("Clone failed")
    subprocess.run(["git","fetch","--all","--tags"],cwd=tmp)
    for ref in [a.old,a.current]:
        if run(["git","rev-parse","--verify",ref],cwd=tmp).returncode!=0:
            sys.exit(f"Reference not found: {ref}")
    log=run(["git","log",f"{a.current}..{a.old}","--pretty=format:%H|%an|%ad|%s","--date=short"],cwd=tmp)
    if not log.stdout.strip():
        print("SUCCESS: No missing commits")
        sys.exit(0)
    print("Missing commits:")
    print(log.stdout)
    sys.exit(1)
finally:
    shutil.rmtree(tmp,ignore_errors=True)
