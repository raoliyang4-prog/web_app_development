"""
app/models/user.py
使用者 (users) 資料表的 CRUD 操作模組。

資料表欄位：id, role, username, password_hash, email, created_at
"""
import sqlite3
from . import get_db_connection


def create(data: dict) -> int | None:
    """
    新增一筆使用者記錄。

    Args:
        data (dict): 必須包含以下鍵值：
            - role (str): 'student' 或 'admin'
            - username (str): 登入帳號（唯一）
            - password_hash (str): 已雜湊的密碼
            - email (str): 電子信箱（唯一）

    Returns:
        int | None: 新增成功回傳 lastrowid，失敗回傳 None。
    """
    sql = """
        INSERT INTO users (role, username, password_hash, email)
        VALUES (:role, :username, :password_hash, :email)
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute(sql, data)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        # 帳號或 email 重複
        print(f"[User.create] IntegrityError: {e}")
        return None
    except sqlite3.Error as e:
        print(f"[User.create] Error: {e}")
        return None
    finally:
        conn.close()


def get_all() -> list:
    """
    取得所有使用者記錄。

    Returns:
        list[sqlite3.Row]: 所有使用者列表，失敗時回傳空列表。
    """
    sql = "SELECT * FROM users ORDER BY created_at DESC"
    try:
        conn = get_db_connection()
        rows = conn.execute(sql).fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"[User.get_all] Error: {e}")
        return []
    finally:
        conn.close()


def get_by_id(user_id: int):
    """
    根據 ID 取得單筆使用者記錄。

    Args:
        user_id (int): 使用者主鍵 ID。

    Returns:
        sqlite3.Row | None: 找到時回傳該筆記錄，否則回傳 None。
    """
    sql = "SELECT * FROM users WHERE id = ?"
    try:
        conn = get_db_connection()
        row = conn.execute(sql, (user_id,)).fetchone()
        return row
    except sqlite3.Error as e:
        print(f"[User.get_by_id] Error: {e}")
        return None
    finally:
        conn.close()


def get_by_username(username: str):
    """
    根據帳號名稱取得單筆使用者記錄（用於登入驗證）。

    Args:
        username (str): 使用者帳號。

    Returns:
        sqlite3.Row | None: 找到時回傳該筆記錄，否則回傳 None。
    """
    sql = "SELECT * FROM users WHERE username = ?"
    try:
        conn = get_db_connection()
        row = conn.execute(sql, (username,)).fetchone()
        return row
    except sqlite3.Error as e:
        print(f"[User.get_by_username] Error: {e}")
        return None
    finally:
        conn.close()


def update(user_id: int, data: dict) -> bool:
    """
    更新指定 ID 的使用者記錄。

    Args:
        user_id (int): 要更新的使用者 ID。
        data (dict): 包含要更新的欄位，可包含：role, username, password_hash, email。

    Returns:
        bool: 更新成功回傳 True，失敗回傳 False。
    """
    allowed_fields = {'role', 'username', 'password_hash', 'email'}
    fields = {k: v for k, v in data.items() if k in allowed_fields}
    if not fields:
        return False

    set_clause = ", ".join(f"{k} = :{k}" for k in fields)
    sql = f"UPDATE users SET {set_clause} WHERE id = :id"
    fields['id'] = user_id

    try:
        conn = get_db_connection()
        conn.execute(sql, fields)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[User.update] Error: {e}")
        return False
    finally:
        conn.close()


def delete(user_id: int) -> bool:
    """
    刪除指定 ID 的使用者記錄。

    Args:
        user_id (int): 要刪除的使用者 ID。

    Returns:
        bool: 刪除成功回傳 True，失敗回傳 False。
    """
    sql = "DELETE FROM users WHERE id = ?"
    try:
        conn = get_db_connection()
        conn.execute(sql, (user_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[User.delete] Error: {e}")
        return False
    finally:
        conn.close()
