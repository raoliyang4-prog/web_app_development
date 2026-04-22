"""
app/routes/__init__.py
Blueprint 定義集中於此，避免循環匯入。
路由完整路徑由各路由模組的裝飾器自行定義，Blueprint 不設 url_prefix。
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
event_bp = Blueprint('event', __name__)
registration_bp = Blueprint('registration', __name__)
