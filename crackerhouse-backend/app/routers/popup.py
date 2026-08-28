"""
☕ 팝업 정보 및 체험존 라우터
- GET  /api/popup        : 현재 팝업 정보 조회
- PUT  /api/popup        : 팝업 정보 생성/수정 (관리자)
- GET  /api/popup/zones  : 체험존 목록 조회
- POST /api/popup/zones  : 체험존 등록 (관리자)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_admin
from app import models, schemas

router = APIRouter(prefix="/api/popup", tags=["☕ 팝업 정보"])


@router.get("", response_model=schemas.PopupInfoResponse, summary="팝업 정보 조회")
def get_popup_info(db: Session = Depends(get_db)):
    """현재 운영 중인 팝업스토어 정보를 반환합니다."""
    info = db.query(models.PopupInfo).first()
    if not info:
        raise HTTPException(status_code=404, detail="등록된 팝업 정보가 없습니다.")
    return info


@router.put("", response_model=schemas.PopupInfoResponse, summary="팝업 정보 등록/수정 (관리자)")
def upsert_popup_info(
    data: schemas.PopupInfoCreate,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    """팝업 정보가 없으면 생성, 있으면 수정합니다."""
    info = db.query(models.PopupInfo).first()

    if info:
        for field, value in data.model_dump().items():
            setattr(info, field, value)
    else:
        info = models.PopupInfo(**data.model_dump())
        db.add(info)

    db.commit()
    db.refresh(info)
    return info


@router.get("/zones", response_model=List[schemas.PopupZoneResponse], summary="체험존 목록 조회")
def get_popup_zones(db: Session = Depends(get_db)):
    """팝업스토어 내 브랜드별 체험존 목록을 반환합니다."""
    zones = db.query(models.PopupZone).order_by(models.PopupZone.created_at.asc()).all()
    return zones


@router.post("/zones", response_model=schemas.PopupZoneResponse, status_code=status.HTTP_201_CREATED, summary="체험존 등록 (관리자)")
def create_popup_zone(
    data: schemas.PopupZoneCreate,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    """관리자가 체험존 정보를 새롭게 등록합니다."""
    zone = models.PopupZone(**data.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone
