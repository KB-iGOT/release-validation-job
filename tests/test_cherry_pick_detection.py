import subprocess
import tempfile
import unittest
from pathlib import Path

import release_validation


class CherryPickDetectionTests(unittest.TestCase):
    def test_marks_commit_as_cherry_picked_when_equivalent_patch_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = Path(tmpdir)
            subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True, text=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)

            (repo_dir / "file.txt").write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "add", "file.txt"], cwd=repo_dir, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=repo_dir, check=True, capture_output=True, text=True)

            subprocess.run(["git", "branch", "old-release"], cwd=repo_dir, check=True)

            (repo_dir / "file.txt").write_text("base\nfeature\n", encoding="utf-8")
            subprocess.run(["git", "add", "file.txt"], cwd=repo_dir, check=True)
            result = subprocess.run(["git", "commit", "-m", "feature commit"], cwd=repo_dir, check=True, capture_output=True, text=True)
            original_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True).stdout.strip()

            subprocess.run(["git", "checkout", "-b", "current-release"], cwd=repo_dir, check=True, capture_output=True, text=True)
            subprocess.run(["git", "cherry-pick", original_sha], cwd=repo_dir, check=True, capture_output=True, text=True)

            statuses = release_validation.get_cherry_pick_statuses(repo_dir, "current-release", "old-release", [original_sha])

            self.assertEqual(statuses[original_sha], "cherry-picked")


if __name__ == "__main__":
    unittest.main()
