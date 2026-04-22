"""
app/models/__init__.py
SQLite 資料庫連線模組。

提供 get_db_connection() 供所有 Model 使用，
設定 row_factory = sqlite3.Row，讓查詢結果可用欄位名稱取值。
"""
import sqlite3
import os

# 資料庫檔案路徑：instance/database.db（相對於專案根目錄）
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'instance',
    'database.db'
)


def get_db_connection():
    """
    建立並回傳 SQLite 資料庫連線。

    設定：
    - row_factory = sqlite3.Row：讓查詢結果可用欄位名稱 (row['column']) 取值
    - PRAGMA foreign_keys = ON：啟用外鍵約束（SQLite 預設關閉）

    使用完畢後，呼叫端需自行呼叫 conn.close()。
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
