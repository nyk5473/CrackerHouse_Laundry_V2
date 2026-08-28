"""Pydantic 스키마: API 요청/응답 형식 정의"""
from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import BrandSlug, ReservationStatus, ReservationType


# ---------- Brand ----------
class BrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: BrandSlug
    name_kr: str
    name_en: Optional[str] = None
    category: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    hero_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    instagram_url: Optional[str] = None
    website_url: Optional[str] = None


class BrandUpdate(BaseModel):
    name_kr: Optional[str] = None
    name_en: Optional[str] = None
    category: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    hero_image_url: Optional[str] = None
    logo_url: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    instagram_url: Optional[str] = None
    website_url: Optional[str] = None


# ---------- Popup / Experience zone ----------
class ExperienceZoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    brand_id: Optional[int] = None
    description: Optional[str] = None
    duration_minutes: int
    capacity_per_slot: int
    image_url: Optional[str] = None


class PopupInfoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    subtitle: Optional[str] = None
    location_name: str
    address: Optional[str] = None
    floor_info: Optional[str] = None
    start_date: date
    end_date: date
    open_time: time
    close_time: time
    description: Optional[str] = None
    notice: Optional[str] = None
    hero_image_url: Optional[str] = None


# ---------- Product ----------
class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_id: int
    name: str
    description: Optional[str] = None
    price: int
    currency: str
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_collab_exclusive: bool
    stock_qty: int
    is_active: bool


class ProductCreate(BaseModel):
    brand_slug: BrandSlug
    name: str
    description: Optional[str] = None
    price: int = 0
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_collab_exclusive: bool = False
    stock_qty: int = 0


class ProductStockUpdate(BaseModel):
    stock_qty: int = Field(ge=0)


# ---------- Guestbook ----------
class GuestbookCreate(BaseModel):
    nickname: str = Field(min_length=1, max_length=50)
    message: str = Field(min_length=1, max_length=500)
    sticker: Optional[str] = Field(default=None, max_length=20)


class GuestbookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str
    message: str
    sticker: Optional[str] = None
    is_visible: bool = True
    created_at: datetime


# ---------- Reservation ----------
class TimeSlotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    start_time: time
    end_time: time
    capacity: int
    booked_count: int
    remaining: int


class PreReservationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=9, max_length=20)
    party_size: int = Field(ge=1, le=20)
    time_slot_id: int
    marketing_agree: bool = False
    memo: Optional[str] = Field(default=None, max_length=300)


class OnsiteReservationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=9, max_length=20)
    party_size: int = Field(ge=1, le=20)
    marketing_agree: bool = False


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: ReservationType
    name: str
    phone: str
    party_size: int
    visit_date: date
    time_slot_id: Optional[int] = None
    queue_number: Optional[int] = None
    status: ReservationStatus
    memo: Optional[str] = None
    created_at: datetime
    checked_in_at: Optional[datetime] = None


class ReservationStatusUpdate(BaseModel):
    status: ReservationStatus


# ---------- Admin ----------
class AdminLogin(BaseModel):
    username: str
    password: str


class AdminOut(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None


class DashboardSummary(BaseModel):
    today: date
    pre_reservations_today: int
    onsite_waiting: int
    onsite_visited_today: int
    guestbook_total: int
    guestbook_hidden: int
    products_low_stock: int
