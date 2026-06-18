import frontmatter
import os
from datetime import datetime
from typing import Optional


CONTENT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "acm-website", "content")


def get_collection_path(collection: str, semester: Optional[str] = None) -> str:
    if collection == "members" and semester:
        return os.path.join(CONTENT_ROOT, collection, semester)
    return os.path.join(CONTENT_ROOT, collection)


def generate_timestamp_id() -> str:
    """產生時間戳當作檔名，格式: 20240615143022"""
    return datetime.now().strftime("%Y%m%d%H%M%S")


def list_entries(collection: str, semester: Optional[str] = None) -> list[dict]:
    """讀取某個 collection 底下所有 .md 檔案"""
    folder = get_collection_path(collection, semester)
    if not os.path.exists(folder):
        return []

    entries = []
    for filename in os.listdir(folder):
        if filename.endswith(".md"):
            filepath = os.path.join(folder, filename)
            post = frontmatter.load(filepath)
            data = dict(post.metadata)
            data["id"] = filename.replace(".md", "")
            if semester:
                data["semester"] = semester
            entries.append(data)
    return entries


def read_entry(collection: str, entry_id: str, semester: Optional[str] = None) -> Optional[dict]:
    """讀取單筆資料"""
    folder = get_collection_path(collection, semester)
    filepath = os.path.join(folder, f"{entry_id}.md")
    if not os.path.exists(filepath):
        return None

    post = frontmatter.load(filepath)
    data = dict(post.metadata)
    data["id"] = entry_id
    if semester:
        data["semester"] = semester
    return data


def write_entry(collection: str, entry_id: str, data: dict, semester: Optional[str] = None, body: str = "") -> str:
    """寫入或更新一筆資料，回傳檔案路徑"""
    folder = get_collection_path(collection, semester)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{entry_id}.md")

    clean_data = {k: v for k, v in data.items() if v is not None}

    post = frontmatter.Post(content=body, **clean_data)
    output = frontmatter.dumps(post)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output)

    return filepath


def delete_entry(collection: str, entry_id: str, semester: Optional[str] = None) -> bool:
    """刪除一筆資料，如果資料夾因此變空則一併移除"""
    folder = get_collection_path(collection, semester)
    filepath = os.path.join(folder, f"{entry_id}.md")
    if not os.path.exists(filepath):
        return False

    os.remove(filepath)

    if os.path.exists(folder) and not os.listdir(folder):
        os.rmdir(folder)

    return True


def list_semesters(collection: str) -> list[str]:
    """列出某個 collection 目前有哪些學期資料夾"""
    folder = get_collection_path(collection)
    if not os.path.exists(folder):
        return []
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]