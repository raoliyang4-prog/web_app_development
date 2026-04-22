"""
app/models/registration.py
報名記錄 (registrations) 資料表的 CRUD 操作模組。

資料表欄位：id, event_id, user_id, status, created_at

注意：實際的報名流程（含名額防超賣）應透過 event.register_with_lock()
      完成名額 +1 後，再呼叫本模組的 create() 寫入報名紀錄。
"""
import sqlite3
from . import get_db_connection


def create(data: dict) -> int | None:
    """
    新增一筆報名記錄。

    Args:
        data (dict): 必須包含以下鍵值：
            - event_id (int): 報名的活動 ID
            - user_id (int): 報名的使用者 ID
            - status (str): 報名狀態，預設 'success'

    Returns:
        int | None: 新增成功回傳 lastrowid，
                    失敗（如重複報名）回傳 None。
    """
    sql = """
        INSERT INTO registrations (event_id, user_id, status)
        VALUES (:event_id, :user_id, :status)
    """
    data.setdefault('status', 'success')
    try:
        conn = get_db_connection()
        cursor = conn.execute(sql, data)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        # UNIQUE 約束違反：同一使用者對同一活動重複報名
        print(f"[Registration.create] IntegrityError: {e}")
        return None
    except sqlite3.Error as e:
        print(f"[Registration.create] Error: {e}")
        return None
    finally:
        conn.close()


def get_all() -> list:
    """
    取得所有報名記錄。

    Returns:
        list[sqlite3.Row]: 所有報名記錄列表，失敗時回傳空列表。
    """
    sql = "SELECT * FROM registrations ORDER BY created_at DESC"
    try:
        conn = get_db_connection()
        rows = conn.execute(sql).fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"[Registration.get_all] Error: {e}")
        return []
    finally:
        conn.close()


def get_by_id(registration_id: int):
    """
    根據 ID 取得單筆報名記錄。

    Args:
        registration_id (int): 報名記錄主鍵 ID。

    Returns:
        sqlite3.Row | None: 找到時回傳該筆記錄，否則回傳 None。
    """
    sql = "SELECT * FROM registrations WHERE id = ?"
    try:
        conn = get_db_connection()
        row = conn.execute(sql, (registration_id,)).fetchone()
        return row
    except sqlite3.Error as e:
        print(f"[Registration.get_by_id] Error: {e}")
        return None
    finally:
        conn.close()


def get_by_user(user_id: int) -> list:
    """
    取得指定使用者的所有報名記錄，並 JOIN events 取得活動標題。

    Args:
        user_id (int): 使用者 ID。

    Returns:
        list[sqlite3.Row]: 該使用者所有報名記錄，失敗時回傳空列表。
    """
    sql = """
        SELECT r.*, e.title AS event_title, e.start_time, e.end_time
        FROM registrations r
        JOIN events e ON r.event_id = e.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
    """
    try:
        conn = get_db_connection()
        rows = conn.execute(sql, (user_id,)).fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"[Registration.get_by_user] Error: {e}")
        return []
    finally:
        conn.close()


def get_by_event(event_id: int) -> list:
    """
    取得指定活動的所有報名記錄，並 JOIN users 取得使用者帳號。

    Args:
        event_id (int): 活動 ID。

    Returns:
        list[sqlite3.Row]: 該活動所有報名記錄，失敗時回傳空列表。
    """
    sql = """
        SELECT r.*, u.username, u.email
        FROM registrations r
        JOIN users u ON r.user_id = u.id
        WHERE r.event_id = ?
        ORDER BY r.created_at ASC
    """
    try:
        conn = get_db_connection()
        rows = conn.execute(sql, (event_id,)).fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"[Registration.get_by_event] Error: {e}")
        return []
    finally:
        conn.close()


def update(registration_id: int, data: dict) -> bool:
    """
    更新指定報名記錄的狀態（如：success → cancelled）。

    Args:
        registration_id (int): 要更新的報名記錄 ID。
        data (dict): 包含要更新的欄位，目前僅支援 status。

    Returns:
        bool: 更新成功回傳 True，失敗回傳 False。
    """
    allowed_fields = {'status'}
    fields = {k: v for k, v in data.items() if k in allowed_fields}
    if not fields:
        return False

    set_clause = ", ".join(f"{k} = :{k}" for k in fields)
    sql = f"UPDATE registrations SET {set_clause} WHERE id = :id"
    fields['id'] = registration_id

    try:
        conn = get_db_connection()
        conn.execute(sql, fields)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[Registration.update] Error: {e}")
        return False
    finally:
        conn.close()


def delete(registration_id: int) -> bool:
    """
    刪除指定 ID 的報名記錄。

    Args:
        registration_id (int): 要刪除的報名記錄 ID。

    Returns:
        bool: 刪除成功回傳 True，失敗回傳 False。
    """
    sql = "DELETE FROM registrations WHERE id = ?"
    try:
        conn = get_db_connection()
        conn.execute(sql, (registration_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[Registration.delete] Error: {e}")
        return False
    finally:
        conn.close()
