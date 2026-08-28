"""팝업정보 + 체험존"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/popup", tags=["팝업정보"])


@router.get("", response_model=schemas.PopupInfoOut)
def get_popup_info(db: Session = Depends(get_db)):
    info = db.query(models.PopupInfo).order_by(models.PopupInfo.id.desc()).first()
    if not info:
        raise HTTPException(status_code=404, detail="팝업 정보가 아직 등록되지 않았습니다.")
    return info


@router.get("/experience-zones", response_model=list[schemas.ExperienceZoneOut])
def list_experience_zones(db: Session = Depends(get_db)):
    return (
        db.query(models.ExperienceZone)
        .order_by(models.ExperienceZone.sort_order)
        .all()
    )
