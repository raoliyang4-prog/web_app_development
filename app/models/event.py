from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.exc import OperationalError
from . import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    max_capacity = Column(Integer, nullable=False)
    current_capacity = Column(Integer, default=0, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    def create(cls, db, **kwargs):
        event = cls(**kwargs)
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @classmethod
    def get_by_id(cls, db, event_id: int):
        return db.query(cls).filter(cls.id == event_id).first()

    @classmethod
    def get_all(cls, db):
        return db.query(cls).all()

    def update(self, db, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()

    @classmethod
    def register_with_lock(cls, db, event_id: int):
        """
        高併發防護：使用悲觀鎖 (SELECT ... FOR UPDATE)
        確認活動名額後，將 current_capacity + 1。
        """
        # 使用 with_for_update() 鎖定該筆紀錄
        event = db.query(cls).filter(cls.id == event_id).with_for_update().first()
        
        if not event:
            raise ValueError("活動不存在")
            
        if event.current_capacity >= event.max_capacity:
            raise ValueError("活動已額滿")
            
        event.current_capacity += 1
        db.commit()
        db.refresh(event)
        return event
