from flask import render_template, request, redirect, url_for, flash, session
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    處理使用者登入。
    GET: 渲染 auth/login.html
    POST: 接收 username, password，驗證後寫入 session。
    """
    pass

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    處理使用者登出。清除 session 並重導向至首頁。
    """
    pass

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    處理使用者註冊。
    GET: 渲染 auth/register.html
    POST: 接收註冊資訊，建立新 User 紀錄，重導向至登入頁。
    """
    pass
