from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# MySQL 접속 정보
DB_USER = "root"
DB_PASSWORD = "123456"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "pdf_summary"


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