"""
DB 연결 설정
- 기본은 SQLite 파일(popup.db)을 사용합니다. (팀 프로젝트 데모/발표용으로 충분)
- 나중에 실제 서버에 배포할 때는 DATABASE_URL 환경변수만 바꿔서
  PostgreSQL 등으로 쉽게 교체할 수 있도록 구성했습니다.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "popup.db")

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI 의존성: 요청마다 DB 세션을 열고 끝나면 닫아준다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
