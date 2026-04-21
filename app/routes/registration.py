from flask import render_template, request, redirect, url_for, flash
from . import registration_bp

@registration_bp.route('/events/<int:id>/register', methods=['POST'])
def register_event(id):
    """
    [學生限定] 處理報名請求。
    觸發 Event.register_with_lock() 悲觀鎖機制，防超賣。
    成功後重導向至我的報名清單，失敗則 flash() 錯誤訊息並導回詳情頁。
    """
    pass

@registration_bp.route('/registrations', methods=['GET'])
def my_registrations():
    """
    [學生限定] 顯示登入者所有成功報名的活動清單。
    渲染: registrations/index.html
    """
    pass

@registration_bp.route('/admin/events/<int:id>/registrations', methods=['GET'])
def event_registrations(id):
    """
    [管理員限定] 檢視特定活動的所有報名名單與狀態。
    渲染: registrations/list.html
    """
    pass
