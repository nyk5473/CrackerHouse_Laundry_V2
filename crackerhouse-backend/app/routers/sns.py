"""
2단계: 인스타그램 DM & 이벤트 자동화 라우터
"""
import random
import string
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/sns", tags=["2단계: SNS DM 자동화"])


def generate_coupon_code() -> str:
    """SNUG-XXXX 형식의 8자리 랜덤 바코드/쿠폰 코드 생성"""
    chars = string.ascii_uppercase + string.digits
    rand_str = ''.join(random.choices(chars, k=4))
    return f"SNUG-{rand_str}"


# 1. 인스타그램 스토리 태그 시뮬레이션 및 자동 DM 쿠폰 발급
@router.post("/trigger-story-event", response_model=schemas.SnsCouponResponse, summary="인스타그램 스토리 태그 트리거 & DM 쿠폰 발급")
def trigger_story_event(
    payload: schemas.SnsCouponCreate,
    db: Session = Depends(get_db)
):
    handle = payload.insta_handle if payload.insta_handle.startswith("@") else f"@{payload.insta_handle}"
    
    # 이미 발급받았는지 검사
    existing = db.query(models.SnsCoupon).filter(
        models.SnsCoupon.insta_handle == handle
    ).first()

    if existing:
        return existing

    # 리워드 무작위/단일 할당 (스너글 포근이 키링 or 크래커 세트 10% 할인권)
    rewards = [
        "스너글 포근이 리미티드 키링 교환권",
        "크래커하우스 X 스너글 콜라보 디저트 1+1 쿠폰",
        "KRACKER LAUNDRY 섬유유연제 미니 샘플링 키트"
    ]
    selected_reward = random.choice(rewards)

    code = generate_coupon_code()
    coupon = models.SnsCoupon(
        coupon_code=code,
        insta_handle=handle,
        reward_name=selected_reward,
        is_redeemed=False
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


# 2. 쿠폰 코드 검증 및 리딤 (현장 스태프용)
@router.post("/redeem", summary="[스태프] 쿠폰 바코드 리딤(사용) 처리")
def redeem_coupon(
    payload: schemas.SnsCouponRedeem,
    db: Session = Depends(get_db)
):
    coupon = db.query(models.SnsCoupon).filter(
        models.SnsCoupon.coupon_code == payload.coupon_code
    ).first()

    if not coupon:
        raise HTTPException(status_code=404, detail="유효하지 않은 쿠폰 코드입니다.")

    if coupon.is_redeemed:
        raise HTTPException(
            status_code=400,
            detail=f"이미 사용된 쿠폰입니다. (사용일시: {coupon.redeemed_at.strftime('%Y-%m-%d %H:%M:%S')})"
        )

    coupon.is_redeemed = True
    coupon.redeemed_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": f"🎉 [{coupon.reward_name}] 수령 완료 처리되었습니다! ({coupon.insta_handle} 님)",
        "coupon_code": coupon.coupon_code,
        "reward_name": coupon.reward_name,
        "insta_handle": coupon.insta_handle
    }


# 3. 전체 SNS 이벤트 참여 및 쿠폰 발급 내역 조회
@router.get("/coupons", response_model=List[schemas.SnsCouponResponse], summary="전체 SNS DM 이벤트 내역")
def list_sns_coupons(db: Session = Depends(get_db)):
    return db.query(models.SnsCoupon).order_by(models.SnsCoupon.created_at.desc()).all()
