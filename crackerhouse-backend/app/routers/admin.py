"""
🔐 관리자 라우터
- POST  /api/admin/login            : 로그인 → JWT 발급
- GET   /api/admin/pending          : 미승인 콘텐츠 목록
- PATCH /api/admin/approve/{type}/{id} : 콘텐츠 승인
- GET   /api/admin/stats            : 간단 통계
"""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_password, create_access_token, get_current_admin, hash_password
from app import models, schemas
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["🔐 관리자"])


@router.post("/login", response_model=schemas.TokenResponse, summary="관리자 로그인")
def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """이메일/비밀번호로 로그인하면 JWT 토큰을 발급합니다."""
    admin = db.query(models.Admin).filter(models.Admin.email == form_data.username).first()
    if not admin or not verify_password(form_data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )
    token = create_access_token({"sub": admin.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/pending", summary="미승인 콘텐츠 목록 (관리자)")
def get_pending(
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    """승인 대기 중인 빨랫줄 집게 + 방명록을 반환합니다."""
    pins = db.query(models.LaundryPin).filter(models.LaundryPin.is_approved == False).all()
    guestbooks = db.query(models.Guestbook).filter(models.Guestbook.is_approved == False).all()

    pending = []
    for p in pins:
        pending.append({
            "id": p.id,
            "type": "pin",
            "nickname": p.nickname,
            "content": p.image_url,
            "message": p.message,
            "pin_type": p.pin_type,
            "created_at": p.created_at,
        })
    for g in guestbooks:
        pending.append({
            "id": g.id,
            "type": "guestbook",
            "nickname": g.nickname,
            "content": g.message,
            "message": None,
            "pin_type": None,
            "created_at": g.created_at,
        })

    pending.sort(key=lambda x: x["created_at"], reverse=True)
    return {"total": len(pending), "items": pending}


@router.patch("/approve/{content_type}/{content_id}", response_model=schemas.MessageResponse,
              summary="콘텐츠 승인 (관리자)")
def approve_content(
    content_type: str,
    content_id: str,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    """
    content_type: "pin" | "guestbook"
    """
    if content_type == "pin":
        obj = db.query(models.LaundryPin).filter(models.LaundryPin.id == content_id).first()
        label = "집게"
    elif content_type == "guestbook":
        obj = db.query(models.Guestbook).filter(models.Guestbook.id == content_id).first()
        label = "방명록"
    else:
        raise HTTPException(status_code=400, detail="content_type은 'pin' 또는 'guestbook' 이어야 합니다.")

    if not obj:
        raise HTTPException(status_code=404, detail=f"{label}을 찾을 수 없습니다.")

    obj.is_approved = True
    db.commit()
    return {"message": f"{label}이 승인됐습니다! 🎉", "success": True}


@router.get("/stats", summary="통계 (관리자)")
def get_stats(
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    """간단한 대시보드 통계를 반환합니다."""
    return {
        "total_pins": db.query(models.LaundryPin).count(),
        "approved_pins": db.query(models.LaundryPin).filter(models.LaundryPin.is_approved == True).count(),
        "pending_pins": db.query(models.LaundryPin).filter(models.LaundryPin.is_approved == False).count(),
        "total_guestbook": db.query(models.Guestbook).count(),
        "approved_guestbook": db.query(models.Guestbook).filter(models.Guestbook.is_approved == True).count(),
        "pending_guestbook": db.query(models.Guestbook).filter(models.Guestbook.is_approved == False).count(),
        "total_products": db.query(models.Product).count(),
    }
