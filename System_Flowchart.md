# 系統流程圖 (System Flowcharts)

本文件根據 PRD 與系統架構文件產出，詳細說明了系統的操作動線以及後端處理報名的核心邏輯。

## 1. 整體系統操作流程圖 (Overall User Flow)
描述一般學生與管理者進入系統後的操作路徑與可執行功能。

```mermaid
flowchart TD
    Start([進入系統首頁]) --> IsLogin{使用者是否已登入?}
    
    IsLogin -- 否 --> ViewPublicEvents[瀏覽公開活動列表]
    ViewPublicEvents --> ViewEventDetail[查看單一活動詳情]
    ViewEventDetail --> ClickRegister[點擊報名按鈕]
    ClickRegister --> LoginPrompt[提示登入]
    LoginPrompt --> LoginScreen[登入頁面]
    
    IsLogin -- 是 --> CheckRole{判斷使用者身分}
    
    CheckRole -- 學生 --> StudentFlow[學生操作區]
    StudentFlow --> BrowseEvents[瀏覽活動列表]
    BrowseEvents --> Detail[查看活動詳情]
    Detail --> Register[點擊報名]
    Register --> BackendProcess((後端報名驗證流程))
    
    CheckRole -- 管理者 --> AdminFlow[管理者後台]
    AdminFlow --> SelectAction{選擇管理動作}
    
    SelectAction -- 建立 --> CreateEvent[填寫活動資訊並發布]
    SelectAction -- 編輯 --> EditEvent[修改現有活動]
    SelectAction -- 刪除 --> DeleteEvent[下架/刪除活動]
    SelectAction -- 查看名單 --> ViewAttendees[檢視特定活動報名名單]
```

---

## 2. 報名機制與併發處理流程 (Registration Concurrency Flow)
描述當學生點擊報名後，後端與資料庫如何透過 **Transaction** 與 **Row-level Lock** 確保在高併發（多人同時搶票）的情況下不會發生「超賣」問題。

```mermaid
sequenceDiagram
    participant Student as 學生 (Frontend)
    participant API as 後端 API Server
    participant DB as 資料庫 (PostgreSQL/MySQL)

    Student->>API: 發送報名請求 (POST /api/events/{id}/register)
    
    Note over API, DB: 開始處理高併發防護
    API->>DB: 1. 開啟交易 (BEGIN TRANSACTION)
    API->>DB: 2. 查詢並鎖定活動紀錄 (SELECT ... FOR UPDATE)
    
    Note over DB: 鎖定該活動資料，直到交易結束
    DB-->>API: 回傳 current_capacity 與 max_capacity
    
    alt 若已額滿 (current_capacity >= max_capacity)
        API->>DB: 3a. 取消交易 (ROLLBACK)
        Note over DB: 釋放鎖定
        API-->>Student: 回傳錯誤：報名失敗 (400 - 活動已額滿)
        
    else 若尚有名額
        API->>DB: 3b. 新增報名紀錄 (INSERT INTO registrations)
        API->>DB: 4. 更新活動人數 (UPDATE events SET current_capacity += 1)
        API->>DB: 5. 提交交易 (COMMIT)
        Note over DB: 寫入完成並釋放鎖定
        API-->>Student: 回傳成功：報名成功 (200 OK)
    end
```

> [!TIP]
> **流程圖解說**：
> 第一張圖展示了前端介面的動線，確保了**管理者**與**學生**有各自獨立的操作邏輯；第二張圖則是系統架構中提到的防護機制，確保了資料的**一致性 (Consistency)** 與 **原子性 (Atomicity)**。
