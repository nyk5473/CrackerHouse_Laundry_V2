"""방명록"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_admin

router = APIRouter(prefix="/api/guestbook", tags=["방명록"])

# 아주 기본적인 도배/욕설 방지용 필터 (데모 수준)
_BANNED_WORDS = ["시발", "씨발", "개새끼"]


def _contains_banned_word(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in _BANNED_WORDS)


@router.get("", response_model=list[schemas.GuestbookOut])
def list_guestbook(
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.GuestbookEntry)
        .filter(models.GuestbookEntry.is_visible.is_(True))
        .order_by(models.GuestbookEntry.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("", response_model=schemas.GuestbookOut, status_code=201)
def create_guestbook_entry(payload: schemas.GuestbookCreate, db: Session = Depends(get_db)):
    if _contains_banned_word(payload.message) or _contains_banned_word(payload.nickname):
        raise HTTPException(status_code=400, detail="부적절한 표현이 포함되어 있어 등록할 수 없습니다.")

    entry = models.GuestbookEntry(
        nickname=payload.nickname.strip(),
        message=payload.message.strip(),
        sticker=payload.sticker,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_guestbook_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    """관리자 전용: 부적절한 글 숨김 처리(soft delete)"""
    entry = db.query(models.GuestbookEntry).filter(models.GuestbookEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="방명록 글을 찾을 수 없습니다.")
    entry.is_visible = False
    db.commit()
    return None
