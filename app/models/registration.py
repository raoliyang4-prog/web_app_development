from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from . import Base

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="success", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'event_id', name='uq_user_event'),
    )

    @classmethod
    def create(cls, db, **kwargs):
        registration = cls(**kwargs)
        db.add(registration)
        db.commit()
        db.refresh(registration)
        return registration

    @classmethod
    def get_by_id(cls, db, registration_id: int):
        return db.query(cls).filter(cls.id == registration_id).first()

    @classmethod
    def get_by_user(cls, db, user_id: int):
        return db.query(cls).filter(cls.user_id == user_id).all()

    @classmethod
    def get_by_event(cls, db, event_id: int):
        return db.query(cls).filter(cls.event_id == event_id).all()

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
