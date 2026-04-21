# 路由設計文件 (Routes Design)

本文件依據 `ARCHITECTURE.md` 中定義的 Flask + Jinja2 伺服器端渲染架構進行規劃，確保每個功能的 URL、HTTP 方法與對應模板都符合標準的網頁互動流程。

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 / 重導向 | 說明 |
| --- | --- | --- | --- | --- |
| 首頁 / 活動列表 | GET | `/` 或 `/events` | `templates/events/index.html` | 顯示所有公開活動 |
| 登入頁面 | GET | `/auth/login` | `templates/auth/login.html` | 顯示登入表單 |
| 執行登入 | POST | `/auth/login` | 重導向至 `/` | 驗證帳號密碼，寫入 Session |
| 登出 | GET/POST | `/auth/logout` | 重導向至 `/` | 清除 Session |
| 註冊頁面 | GET | `/auth/register` | `templates/auth/register.html` | 顯示註冊表單 |
| 執行註冊 | POST | `/auth/register` | 重導向至 `/auth/login` | 建立新使用者帳號 |
| 活動詳情 | GET | `/events/<id>` | `templates/events/detail.html` | 顯示單筆活動與目前報名狀況 |
| 新增活動頁面 | GET | `/admin/events/new` | `templates/events/form.html` | 管理員：顯示新增表單 |
| 建立活動 | POST | `/admin/events` | 重導向至 `/events/<id>` | 管理員：接收表單並寫入 DB |
| 編輯活動頁面 | GET | `/admin/events/<id>/edit`| `templates/events/form.html` | 管理員：顯示編輯表單 |
| 更新活動 | POST | `/admin/events/<id>/update`| 重導向至 `/events/<id>` | 管理員：更新 DB 中的活動 |
| 刪除活動 | POST | `/admin/events/<id>/delete`| 重導向至 `/` | 管理員：刪除活動 |
| 執行報名 | POST | `/events/<id>/register` | 重導向至 `/registrations` | 學生：觸發悲觀鎖，執行報名 |
| 我的報名清單 | GET | `/registrations` | `templates/registrations/index.html` | 學生：檢視自己報名成功的活動 |
| 檢視活動報名名單| GET | `/admin/events/<id>/registrations`| `templates/registrations/list.html` | 管理員：檢視特定活動的報名名單 |

---

## 2. 路由詳細說明

### Auth 路由 (`app/routes/auth.py`)

*   **`GET /auth/login`**
    *   **輸出**：渲染 `auth/login.html`。
*   **`POST /auth/login`**
    *   **輸入**：表單欄位 `username`, `password`。
    *   **邏輯**：查詢 `User` 模型，比對密碼。成功則將 `user_id` 存入 session。
    *   **錯誤處理**：若失敗，利用 `flash()` 顯示錯誤並重新渲染 `auth/login.html`。
*   **`GET /auth/register`**
    *   **輸出**：渲染 `auth/register.html`。
*   **`POST /auth/register`**
    *   **輸入**：表單欄位 `username`, `password`, `email`。
    *   **邏輯**：建立新 `User` (預設角色為 student)。
    *   **錯誤處理**：帳號或信箱重複時，`flash()` 顯示錯誤並重繪表單。

### Event 路由 (`app/routes/event.py`)

*   **`GET /events`**
    *   **邏輯**：呼叫 `Event.get_all()`。
    *   **輸出**：將活動列表傳入 `events/index.html` 渲染。
*   **`GET /events/<id>`**
    *   **邏輯**：呼叫 `Event.get_by_id(id)`。
    *   **輸出**：渲染 `events/detail.html`。找不到則回傳 404 頁面。
*   **`GET /admin/events/new`**
    *   **邏輯**：檢查管理員權限。
    *   **輸出**：渲染 `events/form.html` (表單為空)。
*   **`POST /admin/events`**
    *   **輸入**：表單 `title`, `description`, `max_capacity`, `start_time`, `end_time`。
    *   **邏輯**：檢查管理員權限，呼叫 `Event.create()`。
*   **`POST /admin/events/<id>/update`**
    *   **邏輯**：使用 POST 更新活動資料。
*   **`POST /admin/events/<id>/delete`**
    *   **邏輯**：從 DB 刪除活動並重導向回首頁。

### Registration 路由 (`app/routes/registration.py`)

*   **`POST /events/<id>/register`**
    *   **邏輯**：檢查學生登入狀態。呼叫 `Event.register_with_lock(id)` 進行防超賣報名，接著建立 `Registration` 紀錄。
    *   **錯誤處理**：若捕捉到額滿例外，`flash()` 提示已額滿並重導回活動頁面。
*   **`GET /registrations`**
    *   **邏輯**：依據 session 中的 `user_id` 呼叫 `Registration.get_by_user()`。
    *   **輸出**：渲染 `registrations/index.html`。
*   **`GET /admin/events/<id>/registrations`**
    *   **邏輯**：檢查管理員權限。取得該活動的所有報名紀錄與對應使用者資訊。
    *   **輸出**：渲染 `registrations/list.html`。

---

## 3. Jinja2 模板清單

所有模板預設繼承 `templates/base.html`，以共用導覽列 (Navbar) 與 Flash 訊息區塊。

*   `templates/base.html`：全局框架。
*   `templates/auth/login.html`：登入表單。
*   `templates/auth/register.html`：註冊表單。
*   `templates/events/index.html`：首頁/活動列表卡片視圖。
*   `templates/events/detail.html`：活動詳細資訊與報名按鈕。
*   `templates/events/form.html`：新增/編輯共用表單。
*   `templates/registrations/index.html`：學生的個人報名紀錄清單。
*   `templates/registrations/list.html`：管理員檢視單一活動的報名人員清單。
