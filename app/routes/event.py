"""
app/routes/event.py
活動相關路由：列表、詳情、新增、編輯、刪除。

Blueprint: event_bp（無 url_prefix，定義於 app/routes/__init__.py）

權限規則：
  - GET  /          → 所有人（含未登入）
  - GET  /events/<id> → 所有人（含未登入）
  - GET/POST /admin/* → 需要管理員身份（admin_required）
"""
from flask import render_template, request, redirect, url_for, flash, session, abort

from app.routes import event_bp
from app.utils import login_required, admin_required
import app.models.event as EventModel


# ── 首頁 / 活動列表 ───────────────────────────────────────────────────────────

@event_bp.route('/')
@event_bp.route('/events')
def index():
    """
    GET → 取得所有活動並渲染 events/index.html。
    所有人（含未登入）皆可存取。
    """
    keyword = request.args.get('q', '').strip()
    events = EventModel.get_all(keyword)
    return render_template('events/index.html', events=events, keyword=keyword)


# ── 活動詳情 ──────────────────────────────────────────────────────────────────

@event_bp.route('/events/<int:id>')
def detail(id):
    """
    GET → 渲染 events/detail.html，顯示單筆活動詳情與剩餘名額。
    找不到活動時回傳 404。
    """
    event = EventModel.get_by_id(id)
    if event is None:
        abort(404)
    # 傳遞當前登入者角色，讓模板決定是否顯示管理員操作按鈕
    return render_template('events/detail.html', event=event)


# ── [管理員] 新增活動頁面 ─────────────────────────────────────────────────────

@event_bp.route('/admin/events/new')
@admin_required
def new_event():
    """
    GET → 渲染 events/form.html（空白表單，用於新增活動）。
    """
    return render_template('events/form.html', event=None, action='create')


# ── [管理員] 建立活動 ─────────────────────────────────────────────────────────

@event_bp.route('/admin/events', methods=['POST'])
@admin_required
def create_event():
    """
    POST → 接收新增活動表單，驗證後寫入資料庫，重導向至活動詳情頁。
    """
    title        = request.form.get('title', '').strip()
    description  = request.form.get('description', '').strip()
    max_capacity = request.form.get('max_capacity', '').strip()
    start_time   = request.form.get('start_time', '').strip()
    end_time     = request.form.get('end_time', '').strip()

    # ── 輸入驗證 ──
    errors = []
    if not title:
        errors.append('活動標題為必填欄位。')
    if not max_capacity or not max_capacity.isdigit() or int(max_capacity) <= 0:
        errors.append('報名人數上限必須為正整數。')
    if not start_time:
        errors.append('活動開始時間為必填欄位。')
    if not end_time:
        errors.append('活動結束時間為必填欄位。')
    if start_time and end_time and start_time >= end_time:
        errors.append('結束時間必須晚於開始時間。')

    if errors:
        for msg in errors:
            flash(msg, 'danger')
        return render_template('events/form.html', event=None, action='create')

    event_id = EventModel.create({
        'title':        title,
        'description':  description,
        'max_capacity': int(max_capacity),
        'start_time':   start_time,
        'end_time':     end_time,
        'created_by':   session['user_id'],
    })

    if event_id is None:
        flash('建立活動失敗，請稍後再試。', 'danger')
        return render_template('events/form.html', event=None, action='create')

    flash('活動已成功建立！', 'success')
    return redirect(url_for('event.detail', id=event_id))


# ── [管理員] 編輯活動頁面 ─────────────────────────────────────────────────────

@event_bp.route('/admin/events/<int:id>/edit')
@admin_required
def edit_event(id):
    """
    GET → 渲染 events/form.html（預填現有資料，用於編輯活動）。
    找不到活動時回傳 404。
    """
    event = EventModel.get_by_id(id)
    if event is None:
        abort(404)
    return render_template('events/form.html', event=event, action='update')


# ── [管理員] 更新活動 ─────────────────────────────────────────────────────────

@event_bp.route('/admin/events/<int:id>/update', methods=['POST'])
@admin_required
def update_event(id):
    """
    POST → 驗證並更新活動資料，重導向至活動詳情頁。
    """
    event = EventModel.get_by_id(id)
    if event is None:
        abort(404)

    title        = request.form.get('title', '').strip()
    description  = request.form.get('description', '').strip()
    max_capacity = request.form.get('max_capacity', '').strip()
    start_time   = request.form.get('start_time', '').strip()
    end_time     = request.form.get('end_time', '').strip()

    # ── 輸入驗證 ──
    errors = []
    if not title:
        errors.append('活動標題為必填欄位。')
    if not max_capacity or not max_capacity.isdigit() or int(max_capacity) <= 0:
        errors.append('報名人數上限必須為正整數。')
    if start_time and end_time and start_time >= end_time:
        errors.append('結束時間必須晚於開始時間。')

    if errors:
        for msg in errors:
            flash(msg, 'danger')
        return render_template('events/form.html', event=event, action='update')

    success = EventModel.update(id, {
        'title':        title,
        'description':  description,
        'max_capacity': int(max_capacity),
        'start_time':   start_time,
        'end_time':     end_time,
    })

    if not success:
        flash('更新失敗，請稍後再試。', 'danger')
        return render_template('events/form.html', event=event, action='update')

    flash('活動已成功更新！', 'success')
    return redirect(url_for('event.detail', id=id))


# ── [管理員] 刪除活動 ─────────────────────────────────────────────────────────

@event_bp.route('/admin/events/<int:id>/delete', methods=['POST'])
@admin_required
def delete_event(id):
    """
    POST → 刪除指定活動（CASCADE 同步刪除所有報名記錄），重導向至首頁。
    """
    event = EventModel.get_by_id(id)
    if event is None:
        abort(404)

    success = EventModel.delete(id)
    if success:
        flash('活動已成功刪除。', 'success')
    else:
        flash('刪除失敗，請稍後再試。', 'danger')

    return redirect(url_for('event.index'))
