"""
app/models/__init__.py
資料庫連線初始化。
從環境變數 DATABASE_URL 讀取 PostgreSQL 連線字串。
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:password@localhost:5432/event_registration'
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """產生 SQLAlchemy Session，使用完畢後自動關閉。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
