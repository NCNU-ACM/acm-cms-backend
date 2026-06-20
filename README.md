# NCNU ACM CMS 後端

ACM 官網內容管理系統（CMS）的後端 API，使用 FastAPI 建置，負責讀寫官網內容資料（[acm-website](https://github.com/NCNU-ACM/acm-website) 的 `content/` 資料夾）。

## 專案架構

本專案是 ACM 官網系統的其中一部分，整體系統由四個獨立 repo 組成：

| Repo | 說明 |
|---|---|
| [acm-website](https://github.com/NCNU-ACM/acm-website) | 官網前台 |
| [acm-cms-backend](https://github.com/NCNU-ACM/acm-cms-backend)（本專案） | CMS 後端 API |
| [acm-cms-frontend](https://github.com/NCNU-ACM/acm-cms-frontend) | CMS 後台介面 |
| [acm-backup](https://github.com/NCNU-ACM/acm-backup) | 內容資料獨立備份 |

本專案預期跟 `acm-website` 放在同一層目錄下，因為會直接讀寫 `acm-website/content/` 資料夾：
ACM/

├── acm-website/

│   └── content/        ← 本專案讀寫的目標

├── acm-cms-backend/     ← 本專案

├── acm-cms-frontend/

└── acm-backup/          ← 本專案會自動同步備份到這裡

## 功能

提供五個 collection 的 CRUD API：`groups`（小組）、`events`（活動）、`members`（幹部）、`showcase`（成果展示）、`announcements`（全體通知）。每次新增/編輯/刪除資料後，會自動：

1. 把變更寫入對應的 Markdown 檔案（`acm-website/content/`）
2. 同步複製一份到獨立備份 repo（`acm-backup`）並 commit + push
3. 觸發官網重新 build（正式環境）

## API 端點

所有端點皆以 `/groups`、`/events`、`/members`、`/showcase`、`/announcements` 為前綴，提供標準 CRUD：

| Method | 路徑 | 說明 | 需要驗證 |
|---|---|---|---|
| GET | `/{collection}` | 列出所有資料 | 否 |
| GET | `/groups/{slug}` | 讀取單一小組 | 否 |
| POST | `/{collection}` | 新增資料 | 是 |
| PUT | `/{collection}/{id}` | 更新資料 | 是 |
| DELETE | `/{collection}/{id}` | 刪除資料 | 是 |

另外提供：

| Method | 路徑 | 說明 |
|---|---|---|
| POST | `/auth/login` | 登入，回傳 token |
| GET | `/auth/verify` | 驗證 token 是否有效 |

完整 API 文件可在啟動服務後造訪 `http://localhost:8000/docs`（FastAPI 自動產生的 Swagger UI）。

## 認證機制

採用簡單的帳號密碼登入，登入成功後取得一組 token（有效期 24 小時），需要驗證的端點透過 `Authorization: Bearer {token}` header 帶入 token。

帳密透過環境變數設定：
CMS_USERNAME=admin

CMS_PASSWORD=your_password

> 目前 token 儲存在記憶體中（`active_tokens` 字典），服務重啟後所有 token 會失效，需要重新登入。

## 本機開發

### 環境需求
- Python 3.10 以上

### 安裝與啟動

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate    # macOS/Linux

pip install -r requirements.txt

uvicorn main:app --reload
```

服務預設啟動在 `http://127.0.0.1:8000`。

## 資料儲存邏輯

`utils/file_io.py` 負責讀寫 Markdown 檔案，採用 YAML frontmatter 格式：

```markdown
---
title: 範例標題
event_date: 2026-07-01
group: system
---

```

> 不使用 `python-frontmatter` 套件的 `Post` 物件解析/寫入，改用手動的 `yaml.safe_load` 解析與字串拼接寫入，原因是欄位名稱 `content` 會與 `frontmatter.Post` 建構子的 `content` 參數（代表文章本文）衝突。

`generate_timestamp_id()` 產生格式為 `YYYYMMDDHHmmss` 的字串，同時作為檔名與 `created_at` 欄位的值。

## Git 備份機制

`utils/git_backup.py` 的 `commit_change()` 會在每次資料異動後，把 `acm-website/content/` 整個同步複製到 `acm-backup` 並執行 commit + push，作為內容資料的獨立版本記錄與備份。

## 技術棧

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/) — 資料驗證
- PyYAML — frontmatter 解析

## 相關專案

- [acm-website](https://github.com/NCNU-ACM/acm-website) — 官網前台
- [acm-cms-frontend](https://github.com/NCNU-ACM/acm-cms-frontend) — CMS 後台介面
- [acm-backup](https://github.com/NCNU-ACM/acm-backup) — 內容資料獨立備份