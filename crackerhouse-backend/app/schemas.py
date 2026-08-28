"""
Pydantic 스키마 — 요청/응답 데이터 검증
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.models import PinType, ProductCategory, BrandType, ReservationType, ReservationStatus


# ──────────────────────────────────────────
# 🧺 빨랫줄 집게
# ──────────────────────────────────────────
class LaundryPinCreate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=30, description="닉네임")
    message: Optional[str] = Field(None, max_length=100, description="짧은 메모")
    pin_type: PinType = Field(default=PinType.PHOTO)


class LaundryPinResponse(BaseModel):
    id: str
    image_url: str
    nickname: str
    message: Optional[str]
    pin_type: PinType
    position_x: float
    position_y: float
    created_at: datetime

    class Config:
        from_attributes = True


class LaundryPinList(BaseModel):
    total: int
    items: List[LaundryPinResponse]


# ──────────────────────────────────────────
# 👕 상품
# ──────────────────────────────────────────
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: int = Field(..., ge=0)
    brand: BrandType = Field(default=BrandType.CRACKER_HOUSE)
    category: ProductCategory
    stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    brand: Optional[BrandType] = None
    category: Optional[ProductCategory] = None
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: int
    image_url: str
    brand: BrandType
    category: ProductCategory
    stock: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductList(BaseModel):
    total: int
    items: List[ProductResponse]


# ──────────────────────────────────────────
# ☕ 팝업 정보
# ──────────────────────────────────────────
class PopupInfoCreate(BaseModel):
    title: str
    location: str
    address: Optional[str] = None
    start_date: datetime
    end_date: datetime
    operating_hours: str
    description: Optional[str] = None
    hashtags: Optional[str] = None
    instagram_url: Optional[str] = None


class PopupInfoResponse(BaseModel):
    id: str
    title: str
    location: str
    address: Optional[str]
    start_date: datetime
    end_date: datetime
    operating_hours: str
    description: Optional[str]
    hashtags: Optional[str]
    instagram_url: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# 📬 방명록
# ──────────────────────────────────────────
class GuestbookCreate(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=30)
    message: str = Field(..., min_length=1, max_length=200)


class GuestbookResponse(BaseModel):
    id: str
    nickname: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class GuestbookList(BaseModel):
    total: int
    items: List[GuestbookResponse]


# ──────────────────────────────────────────
# 🔐 관리자 인증
# ──────────────────────────────────────────
class AdminLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PendingItem(BaseModel):
    id: str
    type: str   # "pin" | "guestbook"
    nickname: str
    content: str   # 메시지 or 이미지 URL
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# 공통 응답
# ──────────────────────────────────────────
class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ──────────────────────────────────────────
# 📅 예약 및 현장 대기
# ──────────────────────────────────────────
class ReservationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=9, max_length=20)
    email: Optional[str] = None
    reservation_date: datetime
    reservation_time: str
    people_count: int = Field(default=1, ge=1, le=10)


class OnsiteRegistration(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=9, max_length=20)
    people_count: int = Field(default=1, ge=1, le=10)


class ReservationResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: Optional[str]
    reservation_type: ReservationType
    reservation_date: datetime
    reservation_time: Optional[str]
    waiting_number: Optional[int]
    people_count: int
    status: ReservationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class ReservationStatusUpdate(BaseModel):
    status: ReservationStatus


class ReservationList(BaseModel):
    total: int
    items: List[ReservationResponse]


class WaitingStatusResponse(BaseModel):
    waiting_number: int
    people_ahead: int
    status: ReservationStatus
    name: str


# ──────────────────────────────────────────
# 🎪 팝업 체험존
# ──────────────────────────────────────────
class PopupZoneCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: str
    brand: BrandType


class PopupZoneResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    image_url: str
    brand: BrandType
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────
# 🚀 팝업 자동화 3대 시스템 스키마
# ──────────────────────────────────────────
class WaitingQueueCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=9, max_length=20)
    people_count: int = Field(default=1, ge=1, le=10)


class WaitingQueueQuizUpdate(BaseModel):
    quiz_result: str


class WaitingQueueResponse(BaseModel):
    id: str
    waiting_number: int
    name: str
    phone: str
    people_count: int
    status: str
    quiz_taken: bool
    quiz_result: Optional[str]
    people_ahead: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class SnsCouponCreate(BaseModel):
    insta_handle: str = Field(..., min_length=2, max_length=50)
    story_url: Optional[str] = None


class SnsCouponRedeem(BaseModel):
    coupon_code: str


class SnsCouponResponse(BaseModel):
    id: str
    coupon_code: str
    insta_handle: str
    reward_name: str
    is_redeemed: bool
    redeemed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class StockOrderCalculateRequest(BaseModel):
    raw_sales_csv: str # Base64 or JSON string


class StockOrderLogResponse(BaseModel):
    id: str
    product_name: str
    category: str
    current_stock: int
    safe_stock: int
    daily_sales: int
    recommended_order: int
    status_alert: str
    updated_at: datetime

    class Config:
        from_attributes = True

