from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from . import Base, SessionLocal

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    def create(cls, db, **kwargs):
        user = cls(**kwargs)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def get_by_id(cls, db, user_id: int):
        return db.query(cls).filter(cls.id == user_id).first()

    @classmethod
    def get_by_username(cls, db, username: str):
        return db.query(cls).filter(cls.username == username).first()

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
