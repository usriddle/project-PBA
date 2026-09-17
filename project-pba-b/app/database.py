from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()
# MySQL 접속 정보
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# MySQL 연결 객체
engine = create_engine(
    DATABASE_URL,
    echo=True,
)


# DB 세션
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# ORM 기본 클래스
class Base(DeclarativeBase):
    pass


# FastAPI에서 사용할 DB 세션
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()