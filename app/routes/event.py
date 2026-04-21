from flask import render_template, request, redirect, url_for, flash
from . import event_bp

@event_bp.route('/', methods=['GET'])
@event_bp.route('/events', methods=['GET'])
def index():
    """
    顯示所有公開活動的列表。
    渲染: events/index.html
    """
    pass

@event_bp.route('/events/<int:id>', methods=['GET'])
def detail(id):
    """
    顯示特定活動的詳細資訊與目前剩餘名額。
    渲染: events/detail.html
    """
    pass

@event_bp.route('/admin/events/new', methods=['GET'])
def new_event():
    """
    [管理員限定] 顯示新增活動的表單。
    渲染: events/form.html
    """
    pass

@event_bp.route('/admin/events', methods=['POST'])
def create_event():
    """
    [管理員限定] 接收新增活動的表單提交，存入資料庫後重導向至活動詳情頁。
    """
    pass

@event_bp.route('/admin/events/<int:id>/edit', methods=['GET'])
def edit_event(id):
    """
    [管理員限定] 顯示編輯活動的表單。
    渲染: events/form.html
    """
    pass

@event_bp.route('/admin/events/<int:id>/update', methods=['POST'])
def update_event(id):
    """
    [管理員限定] 接收編輯表單提交，更新活動資料後重導向至活動詳情頁。
    """
    pass

@event_bp.route('/admin/events/<int:id>/delete', methods=['POST'])
def delete_event(id):
    """
    [管理員限定] 刪除特定活動，並重導向回活動列表頁面。
    """
    pass
