"""
빈티지 코인 세탁소 - FastAPI 앱 메인
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, SessionLocal
from app import models
from app.auth import hash_password
from app.routers import laundry_line, products, popup, guestbook, admin, reservations
from app.routers import qr, waiting, sns, inventory


# ──────────────────────────────────────────
# 앱 시작 시 DB 초기화 + 관리자 계정 생성
# ──────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 테이블 생성
    models.Base.metadata.create_all(bind=engine)

    # uploads 폴더 생성
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # 관리자 계정 자동 생성 (최초 실행 시)
    db = SessionLocal()
    try:
        existing = db.query(models.Admin).filter(
            models.Admin.email == settings.ADMIN_EMAIL
        ).first()
        if not existing:
            admin_user = models.Admin(
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
            )
            db.add(admin_user)
            db.commit()
            print(f"✅ 관리자 계정 생성: {settings.ADMIN_EMAIL}")
    finally:
        db.close()

    yield


# ──────────────────────────────────────────
# FastAPI 앱 인스턴스
# ──────────────────────────────────────────
app = FastAPI(
    title="🧺 크래커하우스 X 스너글 콜라보 팝업 API",
    description="""
## 크래커하우스(Cracker House) X 스너글(Snuggle) 팝업스토어 백엔드

> *"포근한 빈티지 세탁소에 놀러오세요~"*

스타필드 빌리지 입점을 가정한 **크래커하우스 X 스너글** 콜라보레이션 팝업스토어 디지털 허브입니다.

### 핵심 기능
- 🧺 **빨랫줄**: 방문객 폴라로이드 사진을 빨랫줄에 집게로 달기
- 👕 **상품**: 브랜드별 상품 (크래커하우스 패션웨어 & 스너글 섬유유연제/홈케어)
- ☕ **팝업 정보**: 스타필드 빌리지 팝업 정보 및 콜라보 체험존 소개
- 📬 **방명록**: 방문객 메시지 방명록
- 📅 **예약 및 대기**: 웹 사전예약 및 오프라인 출입구 키오스크 현장 대기열 관리
- 🚀 **팝업 3대 자동화**: 1. QR 웨이팅, 2. SNS DM 쿠폰, 3. POS 재고 발주
- 🔐 **관리자**: 예약 목록 및 미승인 콘텐츠 관리
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ──────────────────────────────────────────
# CORS
# ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────
# 정적 파일 (업로드 이미지)
# ──────────────────────────────────────────
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ──────────────────────────────────────────
# 라우터 등록
# ──────────────────────────────────────────
app.include_router(laundry_line.router)
app.include_router(products.router)
app.include_router(popup.router)
app.include_router(guestbook.router)
app.include_router(admin.router)
app.include_router(qr.router)
app.include_router(reservations.router)
app.include_router(waiting.router)
app.include_router(sns.router)
app.include_router(inventory.router)


# ──────────────────────────────────────────
# 헬스체크
# ──────────────────────────────────────────
@app.get("/", tags=["상태"], summary="서버 상태 확인")
def health_check():
    return {
        "status": "🟢 running",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "빨래가 마르기를 기다리는 중... ☕",
        "docs": "/docs",
    }
