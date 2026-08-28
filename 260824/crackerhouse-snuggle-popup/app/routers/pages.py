"""
데모용 프론트엔드 페이지 (서버사이드 렌더링, Jinja2)

목록/조회는 서버에서 바로 렌더링하고, 글쓰기/예약/관리자 액션 등
'제출' 이 필요한 동작은 화면의 JS가 위의 /api/* 엔드포인트를 fetch로 호출합니다.
실제 서비스에서는 이 템플릿들을 React/Vue 등으로 교체하고 /api/* 는 그대로 재사용하면 됩니다.
"""
from datetime import date as date_cls, timedelta

from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..deps import get_current_admin_optional

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


def _popup_info(db: Session):
    return db.query(models.PopupInfo).order_by(models.PopupInfo.id.desc()).first()


@router.get("/")
def page_index(request: Request, db: Session = Depends(get_db)):
    popup = _popup_info(db)
    brands = db.query(models.Brand).order_by(models.Brand.sort_order).all()
    guestbook_preview = (
        db.query(models.GuestbookEntry)
        .filter(models.GuestbookEntry.is_visible.is_(True))
        .order_by(models.GuestbookEntry.created_at.desc())
        .limit(4)
        .all()
    )
    return templates.TemplateResponse(
        request,
        "index.html",
        {"popup": popup, "brands": brands, "guestbook_preview": guestbook_preview},
    )


@router.get("/brand")
def page_brand(request: Request, brand: str = Query(default="crackerhouse"), db: Session = Depends(get_db)):
    brands = db.query(models.Brand).order_by(models.Brand.sort_order).all()
    active = next((b for b in brands if b.slug.value == brand), brands[0] if brands else None)
    return templates.TemplateResponse(request, "brand.html", {"brands": brands, "active": active})


@router.get("/popup")
def page_popup(request: Request, db: Session = Depends(get_db)):
    popup = _popup_info(db)
    zones = db.query(models.ExperienceZone).order_by(models.ExperienceZone.sort_order).all()
    return templates.TemplateResponse(request, "popup.html", {"popup": popup, "zones": zones})


@router.get("/products")
def page_products(request: Request, brand: str = Query(default="crackerhouse"), db: Session = Depends(get_db)):
    brands = db.query(models.Brand).order_by(models.Brand.sort_order).all()
    active_brand = next((b for b in brands if b.slug.value == brand), brands[0] if brands else None)
    products = []
    if active_brand:
        products = (
            db.query(models.Product)
            .filter(models.Product.brand_id == active_brand.id, models.Product.is_active.is_(True))
            .order_by(models.Product.sort_order)
            .all()
        )
    return templates.TemplateResponse(
        request,
        "products.html",
        {"brands": brands, "active": active_brand, "products": products},
    )


@router.get("/guestbook")
def page_guestbook(request: Request, db: Session = Depends(get_db)):
    entries = (
        db.query(models.GuestbookEntry)
        .filter(models.GuestbookEntry.is_visible.is_(True))
        .order_by(models.GuestbookEntry.created_at.desc())
        .limit(100)
        .all()
    )
    return templates.TemplateResponse(request, "guestbook.html", {"entries": entries})


@router.get("/register")
def page_register(request: Request, db: Session = Depends(get_db)):
    popup = _popup_info(db)
    today = date_cls.today()
    start = max(popup.start_date, today) if popup else today
    end = popup.end_date if popup else today + timedelta(days=14)
    dates = []
    d = start
    while d <= end:
        dates.append(d)
        d += timedelta(days=1)
    return templates.TemplateResponse(request, "register.html", {"popup": popup, "dates": dates})


@router.get("/kiosk")
def page_kiosk(request: Request):
    """출입구 앞 키오스크 전용 화면 (현장예약)"""
    return templates.TemplateResponse(request, "kiosk.html", {})


@router.get("/admin")
def page_admin(request: Request, admin=Depends(get_current_admin_optional)):
    if not admin:
        return templates.TemplateResponse(request, "admin_login.html", {})
    return templates.TemplateResponse(request, "admin_dashboard.html", {"admin": admin})
