import subprocess
import os
import shutil

WEBSITE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "acm-website")
DIST_PATH = os.path.join(WEBSITE_PATH, "dist")
NGINX_TARGET_PATH = "/var/www/acm-website"  # 之後依實際 server 路徑調整


def trigger_rebuild() -> bool:
    """執行 npm run build，並把結果複製到 Nginx 服務目錄"""
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=WEBSITE_PATH,
            capture_output=True,
            text=True,
            timeout=180,
        )

        if result.returncode != 0:
            print(f"Build 失敗: {result.stderr}")
            return False

        if not os.path.exists(DIST_PATH):
            print("找不到 dist 資料夾，build 可能沒有正確完成")
            return False

        if os.path.exists(NGINX_TARGET_PATH):
            shutil.rmtree(NGINX_TARGET_PATH)
        shutil.copytree(DIST_PATH, NGINX_TARGET_PATH)

        print("Build 完成並已部署")
        return True

    except subprocess.TimeoutExpired:
        print("Build 逾時，請檢查伺服器狀態")
        return False
    except Exception as e:
        print(f"Build 過程發生錯誤: {e}")
        return False