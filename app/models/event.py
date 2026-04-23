"""
app/models/event.py
活動 (events) 資料表的 CRUD 操作模組。

資料表欄位：id, title, description, max_capacity, current_capacity,
             start_time, end_time, created_by, created_at

特別說明：
  register_with_lock() 使用 SQLite 的 BEGIN EXCLUSIVE 交易，
  模擬悲觀鎖效果，防止活動名額超賣。
"""
import sqlite3
from . import get_db_connection


def create(data: dict) -> int | None:
    """
    新增一筆活動記錄。

    Args:
        data (dict): 必須包含以下鍵值：
            - title (str): 活動標題
            - description (str): 活動描述（可為空字串）
            - max_capacity (int): 報名人數上限
            - start_time (str): 活動開始時間（ISO 8601 格式）
            - end_time (str): 活動結束時間（ISO 8601 格式）
            - created_by (int): 建立此活動的管理員 user.id

    Returns:
        int | None: 新增成功回傳 lastrowid，失敗回傳 None。
    """
    sql = """
        INSERT INTO events
            (title, description, max_capacity, current_capacity,
             start_time, end_time, created_by)
        VALUES
            (:title, :description, :max_capacity, 0,
             :start_time, :end_time, :created_by)
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute(sql, data)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"[Event.create] Error: {e}")
        return None
    finally:
        conn.close()


def get_all(keyword: str = None) -> list:
    """
    取得所有活動記錄，依建立時間降序排列。支援關鍵字搜尋。

    Args:
        keyword (str, optional): 搜尋關鍵字。預設為 None。

    Returns:
        list[sqlite3.Row]: 所有活動列表，失敗時回傳空列表。
    """
    try:
        conn = get_db_connection()
        if keyword:
            sql = "SELECT * FROM events WHERE title LIKE ? OR description LIKE ? ORDER BY created_at DESC"
            search_term = f"%{keyword}%"
            rows = conn.execute(sql, (search_term, search_term)).fetchall()
        else:
            sql = "SELECT * FROM events ORDER BY created_at DESC"
            rows = conn.execute(sql).fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"[Event.get_all] Error: {e}")
        return []
    finally:
        conn.close()


def get_by_id(event_id: int):
    """
    根據 ID 取得單筆活動記錄。

    Args:
        event_id (int): 活動主鍵 ID。

    Returns:
        sqlite3.Row | None: 找到時回傳該筆記錄，否則回傳 None。
    """
    sql = "SELECT * FROM events WHERE id = ?"
    try:
        conn = get_db_connection()
        row = conn.execute(sql, (event_id,)).fetchone()
        return row
    except sqlite3.Error as e:
        print(f"[Event.get_by_id] Error: {e}")
        return None
    finally:
        conn.close()


def update(event_id: int, data: dict) -> bool:
    """
    更新指定 ID 的活動記錄。

    Args:
        event_id (int): 要更新的活動 ID。
        data (dict): 包含要更新的欄位，可包含：
                     title, description, max_capacity, start_time, end_time。

    Returns:
        bool: 更新成功回傳 True，失敗回傳 False。
    """
    allowed_fields = {'title', 'description', 'max_capacity', 'start_time', 'end_time'}
    fields = {k: v for k, v in data.items() if k in allowed_fields}
    if not fields:
        return False

    set_clause = ", ".join(f"{k} = :{k}" for k in fields)
    sql = f"UPDATE events SET {set_clause} WHERE id = :id"
    fields['id'] = event_id

    try:
        conn = get_db_connection()
        conn.execute(sql, fields)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[Event.update] Error: {e}")
        return False
    finally:
        conn.close()


def delete(event_id: int) -> bool:
    """
    刪除指定 ID 的活動記錄（關聯的 registrations 會因 CASCADE 一併刪除）。

    Args:
        event_id (int): 要刪除的活動 ID。

    Returns:
        bool: 刪除成功回傳 True，失敗回傳 False。
    """
    sql = "DELETE FROM events WHERE id = ?"
    try:
        conn = get_db_connection()
        conn.execute(sql, (event_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[Event.delete] Error: {e}")
        return False
    finally:
        conn.close()


def register_with_lock(event_id: int) -> tuple[bool, str]:
    """
    高併發防護：使用 SQLite BEGIN EXCLUSIVE 交易模擬悲觀鎖，
    確保同一時間只有一個連線能讀寫該活動的 current_capacity，
    防止活動名額「超賣」。

    流程：
        1. 以 EXCLUSIVE 模式開啟交易（鎖定整個資料庫寫入）
        2. 查詢活動的 max_capacity 與 current_capacity
        3. 若 current_capacity < max_capacity，執行 +1 並 COMMIT
        4. 否則 ROLLBACK，回傳已額滿錯誤

    Args:
        event_id (int): 要報名的活動 ID。

    Returns:
        tuple[bool, str]: (成功與否, 訊息)
            - (True, '報名成功') 或
            - (False, '錯誤原因')
    """
    try:
        conn = get_db_connection()
        # BEGIN EXCLUSIVE：鎖定資料庫，強制其他連線等待
        conn.execute("BEGIN EXCLUSIVE")

        row = conn.execute(
            "SELECT max_capacity, current_capacity FROM events WHERE id = ?",
            (event_id,)
        ).fetchone()

        if row is None:
            conn.rollback()
            return False, "活動不存在"

        if row['current_capacity'] >= row['max_capacity']:
            conn.rollback()
            return False, "活動已額滿，無法報名"

        conn.execute(
            "UPDATE events SET current_capacity = current_capacity + 1 WHERE id = ?",
            (event_id,)
        )
        conn.commit()
        return True, "報名成功"

    except sqlite3.Error as e:
        print(f"[Event.register_with_lock] Error: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False, "系統錯誤，請稍後再試"
    finally:
        conn.close()
