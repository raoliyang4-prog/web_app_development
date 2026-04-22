"""
app/__init__.py
Flask Application Factory。

負責：
  1. 初始化 Flask 應用程式
  2. 載入環境設定（SECRET_KEY）
  3. 呼叫 init_db() 確保資料庫與資料表已建立
  4. 透過 Blueprint 註冊所有路由
"""
import os
import sqlite3
from flask import Flask


def init_db(app: Flask) -> None:
    """
    初始化 SQLite 資料庫。

    讀取 database/schema.sql 並執行，在 instance/database.db 建立
    所有資料表（若尚未存在）。

    Args:
        app (Flask): Flask 應用程式實例（用於取得根目錄路徑）。
    """
    # schema.sql 路徑（相對於專案根目錄）
    schema_path = os.path.join(app.root_path, '..', 'database', 'schema.sql')
    db_dir = os.path.join(app.root_path, '..', 'instance')
    db_path = os.path.join(db_dir, 'database.db')

    os.makedirs(db_dir, exist_ok=True)

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print(f"[init_db] 資料庫已初始化：{db_path}")


def create_app() -> Flask:
    """
    Flask Application Factory。
    初始化 Flask 應用程式、載入設定、初始化資料庫、註冊所有 Blueprint。

    Returns:
        Flask: 設定完成的 Flask 應用程式實例。
    """
    app = Flask(
        __name__,
        template_folder='templates',   # app/templates/
        static_folder='static',        # app/static/
    )

    # ── 設定 ──────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY', 'dev-secret-key-change-in-production'
    )

    # ── 初始化資料庫 ──────────────────────────────────────
    init_db(app)

    # ── 註冊 Blueprints ───────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.event import event_bp
    from app.routes.registration import registration_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(registration_bp)

    return app
