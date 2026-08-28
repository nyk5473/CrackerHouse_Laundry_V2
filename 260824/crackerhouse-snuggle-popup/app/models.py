"""
SQLAlchemy 모델 정의

메뉴 구조와 매핑:
- 브랜드소개 (크래커하우스 / 스너글)      -> Brand
- 팝업정보 / 체험존                      -> PopupInfo, ExperienceZone
- 상품 (크래커하우스 / 스너글)            -> Product (brand_id로 구분)
- 방명록                                 -> GuestbookEntry
- 사전등록(메인) -> 사전예약(팝업)        -> TimeSlot + Reservation(type=PRE)
                  -> 현장예약(키오스크)   -> Reservation(type=ONSITE, queue_number)
- 관리자                                 -> AdminUser
"""
import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class BrandSlug(str, enum.Enum):
    CRACKERHOUSE = "crackerhouse"  # 크래커하우스 (패션 브랜드)
    SNUGGLE = "snuggle"            # 스너글 (세탁 세제 브랜드)


class ReservationType(str, enum.Enum):
    PRE = "PRE"        # 사전예약 (온라인, 날짜/시간대 지정)
    ONSITE = "ONSITE"  # 현장예약 (출입구 키오스크, 당일 대기번호)


class ReservationStatus(str, enum.Enum):
    PENDING = "PENDING"      # 대기/예약 접수
    CONFIRMED = "CONFIRMED"  # 확정 (사전예약이 관리자 확인을 거친 경우)
    CALLED = "CALLED"        # 현장예약: 입장 호출됨
    VISITED = "VISITED"      # 입장 완료
    CANCELLED = "CANCELLED"  # 취소
    NO_SHOW = "NO_SHOW"      # 노쇼


class Brand(Base):
    """크래커하우스 / 스너글 브랜드 소개 정보"""

    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(Enum(BrandSlug), unique=True, nullable=False, index=True)
    name_kr = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)  # 예: "패션 브랜드", "세탁 세제 브랜드"
    tagline = Column(String(255), nullable=True)    # 한 줄 소개
    description = Column(Text, nullable=True)        # 브랜드 스토리
    hero_image_url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    color_primary = Column(String(20), nullable=True)   # 브랜드 포인트 컬러 (hex)
    color_secondary = Column(String(20), nullable=True)
    instagram_url = Column(String(300), nullable=True)
    website_url = Column(String(300), nullable=True)
    sort_order = Column(Integer, default=0)

    products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")
    experience_zones = relationship("ExperienceZone", back_populates="brand")


class PopupInfo(Base):
    """팝업스토어 기본 정보 (기간/장소/시간 등) - 보통 1개 row만 사용"""

    __tablename__ = "popup_info"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, default="크래커하우스 X 스너글 팝업스토어")
    subtitle = Column(String(300), nullable=True)
    location_name = Column(String(200), nullable=False, default="스타필드 빌리지")
    address = Column(String(300), nullable=True)
    floor_info = Column(String(100), nullable=True)  # 예: "1층 팝업존 A-12"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)
    description = Column(Text, nullable=True)
    notice = Column(Text, nullable=True)  # 방문 시 유의사항
    hero_image_url = Column(String(500), nullable=True)


class ExperienceZone(Base):
    """팝업정보 > 체험존"""

    __tablename__ = "experience_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)  # null이면 콜라보 공용존
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=10)
    capacity_per_slot = Column(Integer, default=10)
    image_url = Column(String(500), nullable=True)
    sort_order = Column(Integer, default=0)

    brand = relationship("Brand", back_populates="experience_zones")


class Product(Base):
    """상품 > 크래커하우스 / 스너글 탭에 노출되는 상품(굿즈/MD 포함)"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False, default=0)  # KRW, 원 단위 정수
    currency = Column(String(10), default="KRW")
    image_url = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)  # 예: 의류, 액세서리, 세제, 콜라보 굿즈
    is_collab_exclusive = Column(Boolean, default=False)  # 팝업 단독/콜라보 한정 상품 여부
    stock_qty = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    brand = relationship("Brand", back_populates="products")


class GuestbookEntry(Base):
    """방명록 (브랜드 구분 없이 하나의 공용 방명록)"""

    __tablename__ = "guestbook_entries"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    sticker = Column(String(20), nullable=True)  # 이모지/스티커 선택 (예: "❤️", "🧺")
    is_visible = Column(Boolean, default=True)  # 관리자가 숨김 처리 가능
    created_at = Column(DateTime, default=datetime.utcnow)


class TimeSlot(Base):
    """사전예약용 날짜별 시간대 슬롯 (정원 관리)"""

    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    capacity = Column(Integer, nullable=False, default=15)
    booked_count = Column(Integer, nullable=False, default=0)

    reservations = relationship("Reservation", back_populates="time_slot")

    __table_args__ = (UniqueConstraint("date", "start_time", name="uq_slot_date_start"),)

    @property
    def remaining(self) -> int:
        return max(self.capacity - self.booked_count, 0)


class Reservation(Base):
    """사전예약(PRE) + 현장예약(ONSITE) 통합 테이블"""

    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ReservationType), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    party_size = Column(Integer, nullable=False, default=1)
    visit_date = Column(Date, nullable=False, index=True)

    # 사전예약(PRE)일 때만 사용
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=True)

    # 현장예약(ONSITE)일 때만 사용: 당일 대기번호
    queue_number = Column(Integer, nullable=True)

    status = Column(Enum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING)
    memo = Column(String(300), nullable=True)
    marketing_agree = Column(Boolean, default=False)  # 홍보/마케팅 정보 수신 동의

    created_at = Column(DateTime, default=datetime.utcnow)
    checked_in_at = Column(DateTime, nullable=True)

    time_slot = relationship("TimeSlot", back_populates="reservations")


class AdminUser(Base):
    """팝업 운영진 관리자 계정"""

    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    display_name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
