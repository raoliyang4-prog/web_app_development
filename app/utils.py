"""
app/utils.py
共用 Helper 函式與裝飾器。

提供：
  - login_required  — 需要登入才能存取的路由裝飾器
  - admin_required  — 需要管理員角色才能存取的路由裝飾器
"""
from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    路由裝飾器：確認使用者已登入（session 中有 user_id）。
    未登入則 flash 提示並重導向至登入頁。
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入後再繼續。', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """
    路由裝飾器：確認使用者已登入且角色為 admin。
    非管理員則 flash 提示並重導向至首頁。
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入後再繼續。', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('此頁面僅限管理員存取。', 'danger')
            return redirect(url_for('event.index'))
        return f(*args, **kwargs)
    return decorated
