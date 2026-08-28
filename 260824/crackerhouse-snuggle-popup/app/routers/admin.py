"""관리자 대시보드: 예약/방명록/재고 현황 요약 + 방명록 전체 관리"""
from datetime import date as date_cls

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["관리자"])


@router.get("/dashboard", response_model=schemas.DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    today = date_cls.today()

    pre_today = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.type == models.ReservationType.PRE,
            models.Reservation.visit_date == today,
            models.Reservation.status != models.ReservationStatus.CANCELLED,
        )
        .count()
    )
    onsite_waiting = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.type == models.ReservationType.ONSITE,
            models.Reservation.visit_date == today,
            models.Reservation.status.in_([models.ReservationStatus.PENDING, models.ReservationStatus.CALLED]),
        )
        .count()
    )
    onsite_visited = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.type == models.ReservationType.ONSITE,
            models.Reservation.visit_date == today,
            models.Reservation.status == models.ReservationStatus.VISITED,
        )
        .count()
    )
    guestbook_total = db.query(models.GuestbookEntry).count()
    guestbook_hidden = (
        db.query(models.GuestbookEntry).filter(models.GuestbookEntry.is_visible.is_(False)).count()
    )
    low_stock = db.query(models.Product).filter(models.Product.stock_qty <= 5).count()

    return schemas.DashboardSummary(
        today=today,
        pre_reservations_today=pre_today,
        onsite_waiting=onsite_waiting,
        onsite_visited_today=onsite_visited,
        guestbook_total=guestbook_total,
        guestbook_hidden=guestbook_hidden,
        products_low_stock=low_stock,
    )


@router.get("/guestbook", response_model=list[schemas.GuestbookOut])
def admin_list_guestbook(
    include_hidden: bool = True,
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    q = db.query(models.GuestbookEntry)
    if not include_hidden:
        q = q.filter(models.GuestbookEntry.is_visible.is_(True))
    return q.order_by(models.GuestbookEntry.created_at.desc()).all()


@router.post("/guestbook/{entry_id}/restore", response_model=schemas.GuestbookOut)
def restore_guestbook_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    entry = db.query(models.GuestbookEntry).filter(models.GuestbookEntry.id == entry_id).first()
    if not entry:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="방명록 글을 찾을 수 없습니다.")
    entry.is_visible = True
    db.commit()
    db.refresh(entry)
    return entry
