"""
app/routes/registration.py
報名相關路由：執行報名、我的報名清單、管理員檢視報名名單。

Blueprint: registration_bp（無 url_prefix，定義於 app/routes/__init__.py）

權限規則：
  - POST /events/<id>/register → 需要登入（student 角色）
  - GET  /registrations        → 需要登入
  - GET  /admin/events/<id>/registrations → 需要管理員身份
"""
import csv
import io
from flask import render_template, request, redirect, url_for, flash, session, abort, Response

from app.routes import registration_bp
from app.utils import login_required, admin_required
import app.models.event as EventModel
import app.models.registration as RegistrationModel


# ── [學生] 執行報名 ───────────────────────────────────────────────────────────

@registration_bp.route('/events/<int:id>/register', methods=['POST'])
@login_required
def register_event(id):
    """
    POST → 觸發悲觀鎖報名機制（BEGIN EXCLUSIVE），成功後寫入 registrations，
           重導向至我的報名清單；失敗則 flash 錯誤並導回活動詳情頁。

    防超賣流程：
      1. event.register_with_lock(id)  → 原子性 +1 current_capacity
      2. registration.create(...)      → 寫入報名記錄
    """
    # 管理員不允許報名活動
    if session.get('role') == 'admin':
        flash('管理員帳號無法報名活動。', 'warning')
        return redirect(url_for('event.detail', id=id))

    # 確認活動存在
    event = EventModel.get_by_id(id)
    if event is None:
        abort(404)

    # ── 檢查防衝堂 ──
    if RegistrationModel.check_time_conflict(session['user_id'], event['start_time'], event['end_time']):
        flash('防衝堂提醒：該活動時間與您已報名的其他活動時間重疊，無法報名。', 'danger')
        return redirect(url_for('event.detail', id=id))

    # ── 悲觀鎖報名（BEGIN EXCLUSIVE）──
    success, message = EventModel.register_with_lock(id)

    if not success:
        flash(message, 'danger')
        return redirect(url_for('event.detail', id=id))

    # ── 寫入報名記錄 ──
    reg_id = RegistrationModel.create({
        'event_id': id,
        'user_id':  session['user_id'],
        'status':   'success',
    })

    if reg_id is None:
        # 報名記錄寫入失敗（最常見：重複報名）
        # 回滾 current_capacity（-1）
        EventModel.update(id, {'current_capacity': event['current_capacity']})
        flash('您已報名此活動，無法重複報名。', 'warning')
        return redirect(url_for('event.detail', id=id))

    flash(f'成功報名「{event["title"]}」！', 'success')
    return redirect(url_for('registration.my_registrations'))


# ── [學生] 我的報名清單 ───────────────────────────────────────────────────────

@registration_bp.route('/registrations')
@login_required
def my_registrations():
    """
    GET → 取得登入使用者所有報名記錄（JOIN events）並渲染 registrations/index.html。
    """
    registrations = RegistrationModel.get_by_user(session['user_id'])
    return render_template('registrations/index.html', registrations=registrations)


# ── [管理員] 檢視特定活動報名名單 ─────────────────────────────────────────────

@registration_bp.route('/admin/events/<int:id>/registrations')
@admin_required
def event_registrations(id):
    """
    GET → 取得指定活動的所有報名名單（JOIN users）並渲染 registrations/list.html。
    找不到活動時回傳 404。
    """
    event = EventModel.get_by_id(id)
    if event is None:
        abort(404)

    registrations = RegistrationModel.get_by_event(id)
    return render_template(
        'registrations/list.html',
        event=event,
        registrations=registrations
    )


# ── [管理員] 匯出報名名單 (CSV) ───────────────────────────────────────────────

@registration_bp.route('/admin/events/<int:id>/export')
@admin_required
def export_registrations(id):
    """
    GET → 匯出指定活動的報名名單為 CSV 檔案。
    """
    event = EventModel.get_by_id(id)
    if event is None:
        abort(404)

    registrations = RegistrationModel.get_by_event(id)

    # 建立 CSV 內容
    output = io.StringIO()
    # 加入 UTF-8 BOM，讓 Excel 正常顯示中文
    output.write('\ufeff')
    writer = csv.writer(output)
    
    # 寫入標題列
    writer.writerow(['報名序號', '使用者帳號', '聯絡信箱', '狀態', '報名時間'])
    
    # 寫入資料
    for reg in registrations:
        writer.writerow([
            f"#{reg['id']}",
            reg['username'],
            reg['email'],
            '報名成功' if reg['status'] == 'success' else reg['status'],
            reg['created_at']
        ])

    csv_data = output.getvalue()
    
    # 回傳檔案
    filename = f"registrations_event_{id}.csv"
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
