"""
📬 방명록 라우터
- GET  /api/guestbook       : 승인된 방명록 목록
- POST /api/guestbook       : 방명록 작성
- DELETE /api/guestbook/{id}: 삭제 (관리자)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_admin
from app import models, schemas

router = APIRouter(prefix="/api/guestbook", tags=["📬 방명록"])


@router.get("", response_model=schemas.GuestbookList, summary="방명록 목록")
def get_guestbook(db: Session = Depends(get_db)):
    entries = (
        db.query(models.Guestbook)
        .filter(models.Guestbook.is_approved == True)
        .order_by(models.Guestbook.created_at.desc())
        .all()
    )
    return {"total": len(entries), "items": entries}


@router.post("", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED,
             summary="방명록 작성")
def create_guestbook(
    data: schemas.GuestbookCreate,
    db: Session = Depends(get_db),
):
    """방명록을 작성합니다. 관리자 승인 후 공개됩니다."""
    entry = models.Guestbook(**data.model_dump())
    db.add(entry)
    db.commit()
    return {"message": "방명록이 작성됐어요! 승인 후 공개됩니다 ✍️", "success": True}


@router.delete("/{entry_id}", response_model=schemas.MessageResponse, summary="방명록 삭제 (관리자)")
def delete_guestbook(
    entry_id: str,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    entry = db.query(models.Guestbook).filter(models.Guestbook.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="방명록을 찾을 수 없습니다.")
    db.delete(entry)
    db.commit()
    return {"message": "방명록이 삭제됐습니다.", "success": True}
