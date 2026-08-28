"""
사전등록(메인) 관련 예약 API

- 사전예약(팝업): 날짜/시간대(TimeSlot)를 선택해서 온라인으로 미리 예약 -> type=PRE
- 현장예약(출입구 앞 키오스크): 당일 방문객이 키오스크에서 바로 등록 -> type=ONSITE, 대기번호(queue_number) 발급
"""
from datetime import date as date_cls, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_admin

router = APIRouter(prefix="/api/reservations", tags=["사전등록/예약"])


# ---------------------------------------------------------------------------
# 사전예약 (PRE) - 시간대 슬롯 조회 & 예약
# ---------------------------------------------------------------------------
@router.get("/slots", response_model=list[schemas.TimeSlotOut])
def list_time_slots(
    date: date_cls = Query(..., description="조회할 날짜 (YYYY-MM-DD)"),
    only_available: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    q = db.query(models.TimeSlot).filter(models.TimeSlot.date == date)
    slots = q.order_by(models.TimeSlot.start_time).all()
    if only_available:
        slots = [s for s in slots if s.remaining > 0]
    return slots


@router.post("/pre", response_model=schemas.ReservationOut, status_code=201)
def create_pre_reservation(payload: schemas.PreReservationCreate, db: Session = Depends(get_db)):
    slot = db.query(models.TimeSlot).filter(models.TimeSlot.id == payload.time_slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="선택한 시간대를 찾을 수 없습니다.")
    if slot.remaining < payload.party_size:
        raise HTTPException(status_code=409, detail="해당 시간대는 잔여 인원이 부족합니다. 다른 시간대를 선택해주세요.")

    reservation = models.Reservation(
        type=models.ReservationType.PRE,
        name=payload.name.strip(),
        phone=payload.phone.strip(),
        party_size=payload.party_size,
        visit_date=slot.date,
        time_slot_id=slot.id,
        status=models.ReservationStatus.CONFIRMED,
        memo=payload.memo,
        marketing_agree=payload.marketing_agree,
    )
    slot.booked_count += payload.party_size
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


# ---------------------------------------------------------------------------
# 현장예약 (ONSITE) - 출입구 앞 키오스크에서 등록, 대기번호 발급
# ---------------------------------------------------------------------------
@router.post("/onsite", response_model=schemas.ReservationOut, status_code=201)
def create_onsite_reservation(payload: schemas.OnsiteReservationCreate, db: Session = Depends(get_db)):
    today = date_cls.today()

    last_number = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.type == models.ReservationType.ONSITE,
            models.Reservation.visit_date == today,
        )
        .order_by(models.Reservation.queue_number.desc())
        .first()
    )
    next_number = (last_number.queue_number + 1) if (last_number and last_number.queue_number) else 1

    reservation = models.Reservation(
        type=models.ReservationType.ONSITE,
        name=payload.name.strip(),
        phone=payload.phone.strip(),
        party_size=payload.party_size,
        visit_date=today,
        queue_number=next_number,
        status=models.ReservationStatus.PENDING,
        marketing_agree=payload.marketing_agree,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.get("/onsite/queue-status")
def onsite_queue_status(db: Session = Depends(get_db)):
    """키오스크/현장 안내 화면용: 오늘 호출된 번호, 대기 인원 수"""
    today = date_cls.today()
    base_q = db.query(models.Reservation).filter(
        models.Reservation.type == models.ReservationType.ONSITE,
        models.Reservation.visit_date == today,
    )
    waiting_count = base_q.filter(models.Reservation.status == models.ReservationStatus.PENDING).count()
    last_called = (
        base_q.filter(
            models.Reservation.status.in_(
                [models.ReservationStatus.CALLED, models.ReservationStatus.VISITED]
            )
        )
        .order_by(models.Reservation.queue_number.desc())
        .first()
    )
    return {
        "date": today,
        "now_serving": last_called.queue_number if last_called else None,
        "waiting_count": waiting_count,
    }


# ---------------------------------------------------------------------------
# 관리자 전용: 예약 조회 / 상태 변경 / 다음 대기번호 호출
# ---------------------------------------------------------------------------
@router.get("", response_model=list[schemas.ReservationOut])
def list_reservations(
    type: models.ReservationType | None = Query(default=None),
    status: models.ReservationStatus | None = Query(default=None),
    date: date_cls | None = Query(default=None),
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    q = db.query(models.Reservation)
    if type:
        q = q.filter(models.Reservation.type == type)
    if status:
        q = q.filter(models.Reservation.status == status)
    if date:
        q = q.filter(models.Reservation.visit_date == date)
    return q.order_by(models.Reservation.visit_date, models.Reservation.created_at).all()


@router.patch("/{reservation_id}/status", response_model=schemas.ReservationOut)
def update_reservation_status(
    reservation_id: int,
    payload: schemas.ReservationStatusUpdate,
    db: Session = Depends(get_db),
    _admin: models.AdminUser = Depends(get_current_admin),
):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다.")

    # 사전예약을 취소하면 해당 시간대 슬롯의 잔여 정원을 다시 돌려준다.
    if (
        payload.status == models.ReservationStatus.CANCELLED
        and reservation.status != models.ReservationStatus.CANCELLED
        and reservation.type == models.ReservationType.PRE
        and reservation.time_slot_id
    ):
        slot = db.query(models.TimeSlot).filter(models.TimeSlot.id == reservation.time_slot_id).first()
        if slot:
            slot.booked_count = max(slot.booked_count - reservation.party_size, 0)

    reservation.status = payload.status
    if payload.status == models.ReservationStatus.VISITED:
        reservation.checked_in_at = datetime.utcnow()

    db.commit()
    db.refresh(reservation)
    return reservation


@router.post("/onsite/call-next", response_model=schemas.ReservationOut)
def call_next_onsite(db: Session = Depends(get_db), _admin: models.AdminUser = Depends(get_current_admin)):
    """관리자(입구 스태프)가 다음 대기번호를 호출"""
    today = date_cls.today()
    next_res = (
        db.query(models.Reservation)
        .filter(
            models.Reservation.type == models.ReservationType.ONSITE,
            models.Reservation.visit_date == today,
            models.Reservation.status == models.ReservationStatus.PENDING,
        )
        .order_by(models.Reservation.queue_number.asc())
        .first()
    )
    if not next_res:
        raise HTTPException(status_code=404, detail="대기 중인 현장예약이 없습니다.")

    next_res.status = models.ReservationStatus.CALLED
    db.commit()
    db.refresh(next_res)
    return next_res
