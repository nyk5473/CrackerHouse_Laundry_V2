"""상품: 크래커하우스 / 스너글 탭"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_admin

router = APIRouter(prefix="/api/products", tags=["상품"])


@router.get("", response_model=list[schemas.ProductOut])
def list_products(
    brand: models.BrandSlug | None = Query(default=None, description="crackerhouse | snuggle"),
    only_active: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    q = db.query(models.Product).join(models.Brand)
    if brand:
        q = q.filter(models.Brand.slug == brand)
    if only_active:
        q = q.filter(models.Product.is_active.is_(True))
    return q.order_by(models.Product.sort_order).all()


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return product


@router.post("", response_model=schemas.ProductOut, status_code=201)
def create_product(
    payload: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    """관리자 전용: 신규 상품/굿즈 등록"""
    brand = db.query(models.Brand).filter(models.Brand.slug == payload.brand_slug).first()
    if not brand:
        raise HTTPException(status_code=404, detail="브랜드를 찾을 수 없습니다.")

    product = models.Product(
        brand_id=brand.id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        image_url=payload.image_url,
        category=payload.category,
        is_collab_exclusive=payload.is_collab_exclusive,
        stock_qty=payload.stock_qty,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}/stock", response_model=schemas.ProductOut)
def update_stock(
    product_id: int,
    payload: schemas.ProductStockUpdate,
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    """관리자 전용: 재고 수량 수정"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    product.stock_qty = payload.stock_qty
    db.commit()
    db.refresh(product)
    return product
