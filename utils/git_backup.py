import subprocess
import os

CONTENT_REPO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "acm-website")


def commit_change(message: str) -> bool:
    try:
        subprocess.run(
            ["git", "add", "content"],
            cwd=CONTENT_REPO_PATH,
            check=True,
            capture_output=True,
        )
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=CONTENT_REPO_PATH,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"Git commit 警告: {result.stdout} {result.stderr}")

        push_result = subprocess.run(
            ["git", "push", "origin", "master"],
            cwd=CONTENT_REPO_PATH,
            capture_output=True,
            text=True,
        )
        if push_result.returncode != 0:
            print(f"Git push 警告: {push_result.stderr}")

        return True
    except subprocess.CalledProcessError as e:
        print(f"Git 備份失敗: {e}")
        return False