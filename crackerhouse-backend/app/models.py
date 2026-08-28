"""
빈티지 코인 세탁소 - 데이터베이스 모델 정의
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Float, Text, Enum, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base


def generate_id():
    return str(uuid.uuid4())


# ──────────────────────────────────────────
# 🧺 빨랫줄 집게 (방문객 참여 폴라로이드)
# ──────────────────────────────────────────
class PinType(str, PyEnum):
    PHOTO = "PHOTO"       # 폴라로이드 사진
    RECEIPT = "RECEIPT"   # 레트로 영수증
    KEYRING = "KEYRING"   # 키링 사진


class LaundryPin(Base):
    __tablename__ = "laundry_pins"

    id = Column(String, primary_key=True, default=generate_id)
    image_url = Column(String, nullable=False)
    nickname = Column(String(30), nullable=False)
    message = Column(String(100), nullable=True)
    pin_type = Column(Enum(PinType), default=PinType.PHOTO, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)
    position_x = Column(Float, default=0.0)   # 빨랫줄 내 가로 위치 (0~100%)
    position_y = Column(Float, default=0.0)   # 빨랫줄 내 세로 위치 (레이어용)
    created_at = Column(DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────
# 👕 상품 (빈티지 옷 / 굿즈)
# ──────────────────────────────────────────
class BrandType(str, PyEnum):
    CRACKER_HOUSE = "CRACKER_HOUSE"
    SNUGGLE = "SNUGGLE"


class ProductCategory(str, PyEnum):
    VINTAGE_WEAR = "VINTAGE_WEAR"   # 빈티지 옷
    COFFEE = "COFFEE"               # 커피 굿즈
    FRAGRANCE = "FRAGRANCE"         # 향기
    ETC = "ETC"                     # 기타
    FABRIC_SOFTER = "FABRIC_SOFTER" # 섬유유연제 / 세제
    GOODS = "GOODS"                 # 콜라보 굿즈


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=generate_id)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    image_url = Column(String, nullable=False)
    brand = Column(Enum(BrandType), default=BrandType.CRACKER_HOUSE, nullable=False)
    category = Column(Enum(ProductCategory), nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ──────────────────────────────────────────
# ☕ 팝업 정보
# ──────────────────────────────────────────
class PopupInfo(Base):
    __tablename__ = "popup_info"

    id = Column(String, primary_key=True, default=generate_id)
    title = Column(String, nullable=False)
    location = Column(String, nullable=False)
    address = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    operating_hours = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    hashtags = Column(String, nullable=True)    # 콤마 구분 (e.g. "#빈티지,#크래커하우스")
    instagram_url = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ──────────────────────────────────────────
# 📬 방명록
# ──────────────────────────────────────────
class Guestbook(Base):
    __tablename__ = "guestbook"

    id = Column(String, primary_key=True, default=generate_id)
    nickname = Column(String(30), nullable=False)
    message = Column(String(200), nullable=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────
# 🔐 관리자
# ──────────────────────────────────────────
class Admin(Base):
    __tablename__ = "admins"

    id = Column(String, primary_key=True, default=generate_id)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────
# 📅 예약 및 현장 대기
# ──────────────────────────────────────────
class ReservationType(str, PyEnum):
    PRE_REGISTRATION = "PRE_REGISTRATION"  # 사전예약
    ONSITE_KIOSK = "ONSITE_KIOSK"          # 현장 키오스크 예약


class ReservationStatus(str, PyEnum):
    WAITING = "WAITING"        # 대기 중
    COMPLETED = "COMPLETED"    # 입장 완료
    CANCELLED = "CANCELLED"    # 취소 완료


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(String, primary_key=True, default=generate_id)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    reservation_type = Column(Enum(ReservationType), nullable=False)
    reservation_date = Column(DateTime, nullable=False)
    reservation_time = Column(String, nullable=True)  # 예: "12:00"
    waiting_number = Column(Integer, nullable=True)    # 현장 대기용 번호
    people_count = Column(Integer, default=1, nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.WAITING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────
# 🎪 팝업 체험존
# ──────────────────────────────────────────
class PopupZone(Base):
    __tablename__ = "popup_zones"

    id = Column(String, primary_key=True, default=generate_id)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=False)
    brand = Column(Enum(BrandType), default=BrandType.CRACKER_HOUSE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────
# 🚀 팝업 자동화 3대 시스템 모델
# ──────────────────────────────────────────
class WaitingQueueStatus(str, PyEnum):
    WAITING = "WAITING"        # 대기 중
    CALLED = "CALLED"          # 알림 호출됨
    ENTERED = "ENTERED"        # 입장 완료
    NO_SHOW = "NO_SHOW"        # 노쇼/미입장
    CANCELLED = "CANCELLED"    # 취소됨


class WaitingQueue(Base):
    __tablename__ = "waiting_queues"

    id = Column(String, primary_key=True, default=generate_id)
    waiting_number = Column(Integer, nullable=False)     # 당일 순번 (e.g. 101, 102...)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    people_count = Column(Integer, default=1, nullable=False)
    status = Column(Enum(WaitingQueueStatus), default=WaitingQueueStatus.WAITING, nullable=False)
    quiz_taken = Column(Boolean, default=False)          # 대기 중 취향테스트 참여 여부
    quiz_result = Column(String, nullable=True)          # 향/크래커 취향결과 (e.g. "허거블 코튼 x 바삭 크래커")
    called_at = Column(DateTime, nullable=True)
    entered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SnsCoupon(Base):
    __tablename__ = "sns_coupons"

    id = Column(String, primary_key=True, default=generate_id)
    coupon_code = Column(String(20), unique=True, nullable=False) # e.g. "SNUG-7X9A"
    insta_handle = Column(String(50), nullable=False)            # e.g. "@cracker_fan"
    reward_name = Column(String(100), nullable=False)            # e.g. "스너글 포근이 키링 교환권"
    is_redeemed = Column(Boolean, default=False)
    redeemed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StockOrderLog(Base):
    __tablename__ = "stock_order_logs"

    id = Column(String, primary_key=True, default=generate_id)
    product_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    current_stock = Column(Integer, default=0)
    safe_stock = Column(Integer, default=10)
    daily_sales = Column(Integer, default=0)
    recommended_order = Column(Integer, default=0)
    status_alert = Column(String, default="NORMAL") # "NORMAL", "WARNING", "CRITICAL"
    updated_at = Column(DateTime, default=datetime.utcnow)


