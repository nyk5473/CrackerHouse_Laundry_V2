"""
크래커하우스 X 스너글 팝업스토어 - 백엔드 진입점

실행:
    uvicorn app.main:app --reload

최초 1회 데이터 세팅:
    python -m app.seed
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import models
from .database import Base, engine
from .routers import admin, auth, brands, guestbook, pages, popup, products, reservations

# 테이블이 없으면 생성 (데모/개발 편의용. 운영에서는 Alembic 등 마이그레이션 도구 권장)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="크래커하우스 X 스너글 팝업스토어 API",
    description="스타필드 빌리지 팝업스토어 - 브랜드소개 / 팝업정보 / 상품 / 방명록 / 사전등록(사전예약·현장예약) 백엔드",
    version="1.0.0",
)

# 앱(모바일)이나 별도 프론트엔드에서 API를 호출할 수 있도록 CORS 허용.
# 운영 배포 시 allow_origins를 실제 도메인으로 제한하세요.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ---- REST API ----
app.include_router(brands.router)
app.include_router(popup.router)
app.include_router(products.router)
app.include_router(guestbook.router)
app.include_router(reservations.router)
app.include_router(auth.router)
app.include_router(admin.router)

# ---- 데모용 프론트엔드 페이지 (서버 렌더링) ----
app.include_router(pages.router)


@app.get("/api/health", tags=["헬스체크"])
def health_check():
    return {"status": "ok"}
