"""
📅 예약 및 현장 대기 라우터
- POST   /api/reservations/pre             : 사전예약 신청
- POST   /api/reservations/onsite          : 현장 키오스크 대기 등록
- GET    /api/reservations/waiting-status/{phone} : 대기 상태 확인 (현장용)
- GET    /api/reservations/my              : 내 사전예약 조회 (전화번호 기준)
- GET    /api/reservations                 : 예약 전체 조회 (관리자)
- PATCH  /api/reservations/{id}/status     : 예약 상태 변경 (관리자)
"""
from datetime import datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_admin
from app.database import get_db

router = APIRouter(prefix="/api/reservations", tags=["📅 예약 및 대기"])


@router.post("/pre", response_model=schemas.ReservationResponse, status_code=status.HTTP_201_CREATED, summary="사전예약 신청")
def create_pre_reservation(data: schemas.ReservationCreate, db: Session = Depends(get_db)):
    """웹사이트를 통해 사전예약을 접수합니다."""
    # 동일한 날짜/시간에 동일 전화번호 중복 예약 방지
    existing = db.query(models.Reservation).filter(
        models.Reservation.phone == data.phone,
        models.Reservation.reservation_date == data.reservation_date,
        models.Reservation.reservation_time == data.reservation_time,
        models.Reservation.status == models.ReservationStatus.WAITING
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="이미 해당 시간대에 예약이 되어 있습니다.")

    reservation = models.Reservation(
        name=data.name,
        phone=data.phone,
        email=data.email,
        reservation_type=models.ReservationType.PRE_REGISTRATION,
        reservation_date=data.reservation_date,
        reservation_time=data.reservation_time,
        people_count=data.people_count,
        status=models.ReservationStatus.WAITING
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.post("/onsite", response_model=schemas.ReservationResponse, status_code=status.HTTP_201_CREATED, summary="현장 대기 등록 (키오스크)")
def create_onsite_reservation(data: schemas.OnsiteRegistration, db: Session = Depends(get_db)):
    """현장 입구 키오스크를 통해 대기를 등록합니다. 당일 대기 번호가 자동으로 발급됩니다."""
    # 이미 대기 중인 동일 전화번호 확인
    existing = db.query(models.Reservation).filter(
        models.Reservation.phone == data.phone,
        models.Reservation.reservation_type == models.ReservationType.ONSITE_KIOSK,
        models.Reservation.status == models.ReservationStatus.WAITING
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"이미 현장 대기 등록이 완료되어 있습니다. 대기번호는 {existing.waiting_number}번 입니다."
        )

    # 오늘 생성된 현장 대기 건수를 기준으로 대기번호 생성 (1부터 시작)
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    today_end = datetime.combine(datetime.utcnow().date(), time.max)
    
    today_count = db.query(models.Reservation).filter(
        models.Reservation.reservation_type == models.ReservationType.ONSITE_KIOSK,
        models.Reservation.created_at >= today_start,
        models.Reservation.created_at <= today_end
    ).count()

    waiting_number = today_count + 1

    reservation = models.Reservation(
        name=data.name,
        phone=data.phone,
        reservation_type=models.ReservationType.ONSITE_KIOSK,
        reservation_date=datetime.utcnow(),
        waiting_number=waiting_number,
        people_count=data.people_count,
        status=models.ReservationStatus.WAITING
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.get("/waiting-status/{phone}", response_model=schemas.WaitingStatusResponse, summary="대기 상태 조회")
def get_waiting_status(phone: str, db: Session = Depends(get_db)):
    """핸드폰 번호로 현장 대기 상태 및 내 앞에 몇 팀이 남았는지 확인합니다."""
    # 당일 대기 중인 번호 조회
    today_start = datetime.combine(datetime.utcnow().date(), time.min)
    today_end = datetime.combine(datetime.utcnow().date(), time.max)

    reservation = db.query(models.Reservation).filter(
        models.Reservation.phone == phone,
        models.Reservation.reservation_type == models.ReservationType.ONSITE_KIOSK,
        models.Reservation.status == models.ReservationStatus.WAITING,
        models.Reservation.created_at >= today_start,
        models.Reservation.created_at <= today_end
    ).first()

    if not reservation:
        raise HTTPException(status_code=404, detail="현재 대기 대열에 등록된 정보가 없습니다.")

    # 내 앞에 있는 대기 팀 수 (대기 상태이면서 나보다 등록 시간이 빠른 팀)
    people_ahead = db.query(models.Reservation).filter(
        models.Reservation.reservation_type == models.ReservationType.ONSITE_KIOSK,
        models.Reservation.status == models.ReservationStatus.WAITING,
        models.Reservation.created_at < reservation.created_at,
        models.Reservation.created_at >= today_start
    ).count()

    return {
        "waiting_number": reservation.waiting_number,
        "people_ahead": people_ahead,
        "status": reservation.status,
        "name": reservation.name
    }


@router.get("/my", response_model=schemas.ReservationList, summary="내 사전예약 목록 조회")
def get_my_reservations(phone: str = Query(..., description="조회할 전화번호"), db: Session = Depends(get_db)):
    """전화번호로 본인의 사전예약 목록을 조회합니다."""
    reservations = db.query(models.Reservation).filter(
        models.Reservation.phone == phone,
        models.Reservation.reservation_type == models.ReservationType.PRE_REGISTRATION
    ).order_by(models.Reservation.reservation_date.desc()).all()
    
    return {"total": len(reservations), "items": reservations}


@router.get("", response_model=schemas.ReservationList, summary="예약 전체 목록 조회 (관리자)")
def get_reservations(
    reservation_type: Optional[models.ReservationType] = Query(None, description="예약 방식 필터"),
    status: Optional[models.ReservationStatus] = Query(None, description="상태 필터"),
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    """관리자용 전체 예약 및 현장 대기 목록 조회"""
    query = db.query(models.Reservation)
    
    if reservation_type:
        query = query.filter(models.Reservation.reservation_type == reservation_type)
    if status:
        query = query.filter(models.Reservation.status == status)
        
    # 대기 번호 순, 또는 생성 일자 순으로 정렬
    items = query.order_by(models.Reservation.created_at.asc()).all()
    return {"total": len(items), "items": items}


@router.patch("/{reservation_id}/status", response_model=schemas.ReservationResponse, summary="예약 상태 수정 (관리자)")
def update_reservation_status(
    reservation_id: str,
    data: schemas.ReservationStatusUpdate,
    db: Session = Depends(get_db),
    _: models.Admin = Depends(get_current_admin),
):
    """관리자가 방문객의 입장완료(`COMPLETED`) 또는 취소(`CANCELLED`) 상태를 업데이트합니다."""
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="예약 내역을 찾을 수 없습니다.")

    reservation.status = data.status
    db.commit()
    db.refresh(reservation)
    return reservation
