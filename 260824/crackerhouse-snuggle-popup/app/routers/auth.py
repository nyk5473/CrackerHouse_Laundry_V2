"""관리자 로그인/로그아웃"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_admin
from ..security import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    create_session_token,
    verify_password,
)

router = APIRouter(prefix="/api/admin", tags=["관리자 인증"])


@router.post("/login", response_model=schemas.AdminOut)
def login(payload: schemas.AdminLogin, response: Response, db: Session = Depends(get_db)):
    admin = db.query(models.AdminUser).filter(models.AdminUser.username == payload.username).first()
    if not admin or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    token = create_session_token(admin.id, admin.username)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
    )
    return schemas.AdminOut(id=admin.id, username=admin.username, display_name=admin.display_name)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=schemas.AdminOut)
def me(admin: models.AdminUser = Depends(get_current_admin)):
    return schemas.AdminOut(id=admin.id, username=admin.username, display_name=admin.display_name)
