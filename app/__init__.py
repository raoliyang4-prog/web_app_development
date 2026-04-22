import os
from flask import Flask


def create_app():
    """
    Flask Application Factory。
    初始化 Flask 應用程式、載入設定、註冊所有 Blueprint。
    """
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',
    )

    # --- 設定 ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # --- 註冊 Blueprints ---
    from app.routes.auth import auth_bp
    from app.routes.event import event_bp
    from app.routes.registration import registration_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(registration_bp)

    return app
