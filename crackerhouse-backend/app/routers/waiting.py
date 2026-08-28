"""
1단계: 현장 QR 웨이팅 & 실시간 순번/취향테스트 연동 라우터
"""
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/waiting", tags=["1단계: QR 웨이팅 자동화"])


# 1. 현장 QR 대기 등록
@router.post("/register", response_model=schemas.WaitingQueueResponse, summary="현장 QR 대기 등록")
def register_waiting(
    payload: schemas.WaitingQueueCreate,
    db: Session = Depends(get_db)
):
    today_start = datetime.combine(date.today(), datetime.min.time())
    
    # 오늘 생성된 마지막 번호 구하기
    max_num = db.query(func.max(models.WaitingQueue.waiting_number)).filter(
        models.WaitingQueue.created_at >= today_start
    ).scalar() or 100

    next_number = max_num + 1

    # 대기 등록 생성
    item = models.WaitingQueue(
        waiting_number=next_number,
        name=payload.name,
        phone=payload.phone,
        people_count=payload.people_count,
        status=models.WaitingQueueStatus.WAITING
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    # 내 앞에 대기 팀 수 계산
    people_ahead = db.query(models.WaitingQueue).filter(
        models.WaitingQueue.created_at >= today_start,
        models.WaitingQueue.status == models.WaitingQueueStatus.WAITING,
        models.WaitingQueue.waiting_number < item.waiting_number
    ).count()

    res = schemas.WaitingQueueResponse.from_orm(item)
    res.people_ahead = people_ahead
    return res


# 2. 내 실시간 순번 조회
@router.get("/status/{phone}", response_model=schemas.WaitingQueueResponse, summary="대기자 순번 실시간 조회")
def get_waiting_status(phone: str, db: Session = Depends(get_db)):
    today_start = datetime.combine(date.today(), datetime.min.time())
    
    item = db.query(models.WaitingQueue).filter(
        models.WaitingQueue.phone == phone,
        models.WaitingQueue.created_at >= today_start,
        models.WaitingQueue.status.in_([models.WaitingQueueStatus.WAITING, models.WaitingQueueStatus.CALLED])
    ).order_by(models.WaitingQueue.created_at.desc()).first()

    if not item:
        raise HTTPException(status_code=404, detail="진행 중인 대기 내역이 없습니다.")

    people_ahead = db.query(models.WaitingQueue).filter(
        models.WaitingQueue.created_at >= today_start,
        models.WaitingQueue.status == models.WaitingQueueStatus.WAITING,
        models.WaitingQueue.waiting_number < item.waiting_number
    ).count()

    res = schemas.WaitingQueueResponse.from_orm(item)
    res.people_ahead = people_ahead
    return res


# 2-1. ID 기반 개별 순번 상세 조회
@router.get("/detail/{waiting_id}", response_model=schemas.WaitingQueueResponse, summary="ID 기반 대기표 상세 조회")
def get_waiting_detail(waiting_id: str, db: Session = Depends(get_db)):
    today_start = datetime.combine(date.today(), datetime.min.time())
    
    item = db.query(models.WaitingQueue).filter(models.WaitingQueue.id == waiting_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="대기 정보를 찾을 수 없습니다.")

    people_ahead = db.query(models.WaitingQueue).filter(
        models.WaitingQueue.created_at >= today_start,
        models.WaitingQueue.status == models.WaitingQueueStatus.WAITING,
        models.WaitingQueue.waiting_number < item.waiting_number
    ).count()

    res = schemas.WaitingQueueResponse.from_orm(item)
    res.people_ahead = people_ahead
    return res


# 2-2. 고객 본인 대기 취소
@router.put("/cancel/{waiting_id}", summary="고객 본인 대기 취소")
def cancel_waiting(waiting_id: str, db: Session = Depends(get_db)):
    item = db.query(models.WaitingQueue).filter(models.WaitingQueue.id == waiting_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="대기 정보를 찾을 수 없습니다.")

    item.status = models.WaitingQueueStatus.CANCELLED
    db.commit()
    return {"message": f"순번 {item.waiting_number}번 대기가 취소되었습니다."}


# 3. 대기 중 취향테스트 결과 저장 연동
@router.post("/quiz/{waiting_id}", summary="대기자 취향테스트 결과 저장")
def update_quiz_result(
    waiting_id: str,
    payload: schemas.WaitingQueueQuizUpdate,
    db: Session = Depends(get_db)
):
    item = db.query(models.WaitingQueue).filter(models.WaitingQueue.id == waiting_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="대기 정보를 찾을 수 없습니다.")

    item.quiz_taken = True
    item.quiz_result = payload.quiz_result
    db.commit()
    return {"message": "취향테스트 결과가 연동되었습니다!", "quiz_result": item.quiz_result}


# 4. [스태프용] 전체 대기 목록 조회
@router.get("/list", response_model=List[schemas.WaitingQueueResponse], summary="[스태프] 전체 대기열 목록")
def list_waiting_queue(db: Session = Depends(get_db)):
    today_start = datetime.combine(date.today(), datetime.min.time())
    items = db.query(models.WaitingQueue).filter(
        models.WaitingQueue.created_at >= today_start
    ).order_by(models.WaitingQueue.waiting_number.asc()).all()

    results = []
    for item in items:
        ahead = db.query(models.WaitingQueue).filter(
            models.WaitingQueue.created_at >= today_start,
            models.WaitingQueue.status == models.WaitingQueueStatus.WAITING,
            models.WaitingQueue.waiting_number < item.waiting_number
        ).count()
        r = schemas.WaitingQueueResponse.from_orm(item)
        r.people_ahead = ahead
        results.append(r)
    return results


# 5. [스태프용] 상태 변경 (호출 / 입장 완료 / 노쇼 처리)
@router.put("/status/{waiting_id}", summary="[스태프] 대기 상태 업데이트 (CALLED, ENTERED, NO_SHOW)")
def update_queue_status(
    waiting_id: str,
    status: models.WaitingQueueStatus = Query(...),
    db: Session = Depends(get_db)
):
    item = db.query(models.WaitingQueue).filter(models.WaitingQueue.id == waiting_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="대기 정보를 찾을 수 없습니다.")

    item.status = status
    if status == models.WaitingQueueStatus.CALLED:
        item.called_at = datetime.utcnow()
    elif status == models.WaitingQueueStatus.ENTERED:
        item.entered_at = datetime.utcnow()

    db.commit()

    # 카카오 알림톡 모의 전송 텍스트 생성
    alimtalk_msg = ""
    if status == models.WaitingQueueStatus.CALLED:
        alimtalk_msg = f"[카카오 알림톡 전송] {item.name} 님! [KRACKER LAUNDRY] 입장 순서입니다. 5분 이내 입구로 오셔서 순번 #{item.waiting_number}를 보여주세요!"

    return {
        "message": f"순번 {item.waiting_number}번 상태가 '{status}'(으)로 변경되었습니다.",
        "alimtalk_preview": alimtalk_msg
    }

