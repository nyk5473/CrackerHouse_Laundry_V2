"""
👕 상품 라우터
- GET    /api/products            : 상품 목록 (카테고리 필터)
- GET    /api/products/{id}       : 상품 상세
- POST   /api/products            : 상품 등록 (관리자)
- PATCH  /api/products/{id}       : 상품 수정 (관리자)
- DELETE /api/products/{id}       : 상품 삭제 (관리자)
"""
import os
import uuid
import aiofiles

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_admin
from app import models, schemas
from app.config import settings

router = APIRouter(prefix="/api/products", tags=["👕 상품"])


@router.get("", response_model=schemas.ProductList, summary="상품 목록")
def get_products(
    brand: Optional[models.BrandType] = Query(None, description="브랜드 필터"),
    category: Optional[models.ProductCategory] = Query(None, description="카테고리 필터"),
    db: Session = Depends(get_db),
):
    """활성화된 상품 목록을 반환합니다. brand 및 category 파라미터로 필터링 가능."""
    query = db.query(models.Product).filter(models.Product.is_active == True)
    if brand:
        query = query.filter(models.Product.brand == brand)
    if category:
        query = query.filter(models.Product.category == category)
    products = query.order_by(models.Product.created_at.desc()).all()
    return {"total": len(products), "items": products}


@router.get("/{product_id}", response_model=schemas.ProductResponse, summary="상품 상세")
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return product


@router.post("", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED,
             summary="상품 등록 (관리자)")
async def create_product(
    name: str = Form(...),
    description: str = Form(None),
    price: int = Form(...),
    brand: models.BrandType = Form(models.BrandType.CRACKER_HOUSE),
    category: models.ProductCategory = Form(...),
    stock: int = Form(0),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    # 이미지 저장
    ext = image.filename.rsplit(".", 1)[-1].lower()
    content = await image.read()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"product_{uuid.uuid4()}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    product = models.Product(
        name=name,
        description=description,
        price=price,
        image_url=f"/uploads/{filename}",
        brand=brand,
        category=category,
        stock=stock,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=schemas.ProductResponse, summary="상품 수정 (관리자)")
def update_product(
    product_id: str,
    data: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", response_model=schemas.MessageResponse, summary="상품 삭제 (관리자)")
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    db.delete(product)
    db.commit()
    return {"message": "상품이 삭제됐습니다.", "success": True}
