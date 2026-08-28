"""브랜드소개: 크래커하우스 / 스너글"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/brands", tags=["브랜드소개"])


@router.get("", response_model=list[schemas.BrandOut])
def list_brands(db: Session = Depends(get_db)):
    return db.query(models.Brand).order_by(models.Brand.sort_order).all()


@router.get("/{slug}", response_model=schemas.BrandOut)
def get_brand(slug: models.BrandSlug, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(models.Brand.slug == slug).first()
    if not brand:
        raise HTTPException(status_code=404, detail="해당 브랜드를 찾을 수 없습니다.")
    return brand
