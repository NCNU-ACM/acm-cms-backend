import subprocess
import os
import shutil

CONTENT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "acm-website", "content")
BACKUP_REPO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "acm-backup")

def sync_to_backup():
    for item in os.listdir(CONTENT_ROOT):
        src = os.path.join(CONTENT_ROOT, item)
        dst = os.path.join(BACKUP_REPO_PATH, item)

        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def commit_change(message: str) -> bool:
    try:
        sync_to_backup()

        subprocess.run(
            ["git", "add", "."],
            cwd=BACKUP_REPO_PATH,
            check=True,
            capture_output=True,
        )
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=BACKUP_REPO_PATH,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"Git commit 警告: {result.stdout} {result.stderr}")

        push_result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=BACKUP_REPO_PATH,
            capture_output=True,
            text=True,
        )
        if push_result.returncode != 0:
            print(f"Git push 警告: {push_result.stderr}")

        return True
    except subprocess.CalledProcessError as e:
        print(f"Git 備份失敗: {e}")
        return False