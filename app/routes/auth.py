"""
app/routes/auth.py
身份驗證路由：登入、登出、註冊。

Blueprint: auth_bp（url_prefix='/auth'，定義於 app/routes/__init__.py）

使用 werkzeug.security 進行密碼雜湊與驗證。
使用 Flask session 保存登入狀態（user_id、role）。
"""
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from app.routes import auth_bp
import app.models.user as UserModel


# ── 登入 ──────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET  → 渲染 auth/login.html（顯示登入表單）
    POST → 驗證帳號密碼，成功則寫入 session 並重導向至首頁。
    """
    # 已登入者直接導回首頁
    if 'user_id' in session:
        return redirect(url_for('event.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # ── 輸入驗證 ──
        if not username or not password:
            flash('帳號與密碼為必填欄位。', 'danger')
            return render_template('auth/login.html')

        # ── 查詢使用者 ──
        user = UserModel.get_by_username(username)
        if user is None or not check_password_hash(user['password_hash'], password):
            flash('帳號或密碼錯誤，請重試。', 'danger')
            return render_template('auth/login.html')

        # ── 寫入 Session ──
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']

        flash(f'歡迎回來，{user["username"]}！', 'success')
        return redirect(url_for('event.index'))

    return render_template('auth/login.html')


# ── 登出 ──────────────────────────────────────────────────────────────────────

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    清除 Session 並重導向至首頁。
    """
    session.clear()
    flash('已成功登出。', 'info')
    return redirect(url_for('event.index'))


# ── 註冊 ──────────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET  → 渲染 auth/register.html（顯示註冊表單）
    POST → 建立新使用者（預設角色 student），重導向至登入頁。
    """
    if 'user_id' in session:
        return redirect(url_for('event.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # ── 輸入驗證 ──
        errors = []
        if not username:
            errors.append('帳號為必填欄位。')
        if not email:
            errors.append('電子信箱為必填欄位。')
        if not password:
            errors.append('密碼為必填欄位。')
        if len(password) < 6:
            errors.append('密碼長度至少需要 6 個字元。')

        if errors:
            for msg in errors:
                flash(msg, 'danger')
            return render_template('auth/register.html')

        # ── 建立使用者 ──
        user_id = UserModel.create({
            'role':          'student',
            'username':      username,
            'email':         email,
            'password_hash': generate_password_hash(password),
        })

        if user_id is None:
            flash('帳號或電子信箱已被使用，請更換後再試。', 'danger')
            return render_template('auth/register.html')

        flash('註冊成功！請登入。', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')
