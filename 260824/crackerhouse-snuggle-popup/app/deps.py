"""공통 FastAPI 의존성 (관리자 인증 등)"""
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .security import SESSION_COOKIE_NAME, read_session_token


def get_current_admin(
    popup_admin_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
) -> models.AdminUser:
    """관리자 전용 API를 보호하는 의존성.
    로그인 쿠키가 없거나 유효하지 않으면 401을 반환한다.
    """
    if not popup_admin_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")

    data = read_session_token(popup_admin_session)
    if not data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="세션이 만료되었습니다. 다시 로그인해주세요.")

    admin = db.query(models.AdminUser).filter(models.AdminUser.id == data.get("admin_id")).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="관리자 계정을 찾을 수 없습니다.")
    return admin


def get_current_admin_optional(
    popup_admin_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    db: Session = Depends(get_db),
) -> models.AdminUser | None:
    """페이지 렌더링 등에서 로그인 여부만 부드럽게 확인할 때 사용 (실패해도 예외를 던지지 않음)"""
    if not popup_admin_session:
        return None
    data = read_session_token(popup_admin_session)
    if not data:
        return None
    return db.query(models.AdminUser).filter(models.AdminUser.id == data.get("admin_id")).first()
