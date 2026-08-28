"""
초기 데이터 시딩 스크립트

실행:
    python -m app.seed

이미 데이터가 있으면 다시 실행해도 중복 생성하지 않습니다(브랜드/관리자 기준).
개발 중 데이터를 완전히 초기화하고 싶으면 popup.db 파일을 삭제하고 다시 실행하세요.
"""
from datetime import date, time, timedelta

from .database import Base, SessionLocal, engine
from .models import (
    AdminUser,
    Brand,
    BrandSlug,
    ExperienceZone,
    GuestbookEntry,
    PopupInfo,
    Product,
    TimeSlot,
)
from .security import hash_password

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        # ---------------- Brand ----------------
        crackerhouse = db.query(Brand).filter(Brand.slug == BrandSlug.CRACKERHOUSE).first()
        if not crackerhouse:
            crackerhouse = Brand(
                slug=BrandSlug.CRACKERHOUSE,
                name_kr="크래커하우스",
                name_en="CRACKERHOUSE",
                category="패션 브랜드",
                tagline="일상을 유쾌하게 바삭바삭 부수는 스트릿 패션",
                description=(
                    "크래커하우스는 가볍고 유쾌한 무드의 스트릿 캐주얼 브랜드입니다. "
                    "이번 팝업에서는 '세탁'이라는 일상적인 순간을 재치있게 재해석한 "
                    "콜라보 컬렉션을 처음으로 공개합니다."
                ),
                hero_image_url="/static/img/crackerhouse_hero.svg",
                logo_url="/static/img/crackerhouse_logo.svg",
                color_primary="#BC453C",
                color_secondary="#F25C05",
                instagram_url="https://instagram.com/crackerhouse",
                website_url="https://crackerhouse.example.com",
                sort_order=1,
            )
            db.add(crackerhouse)

        snuggle = db.query(Brand).filter(Brand.slug == BrandSlug.SNUGGLE).first()
        if not snuggle:
            snuggle = Brand(
                slug=BrandSlug.SNUGGLE,
                name_kr="스너글",
                name_en="SNUGGLE",
                category="세탁 세제 브랜드",
                tagline="포근하고 깨끗한 일상을 위한 세탁 파트너",
                description=(
                    "스너글은 산뜻하고 편안한 세탁 경험을 제안하는 세제 브랜드입니다. "
                    "이번 팝업에서는 크래커하우스와 함께 '나만의 옷을 오래도록 아끼는 방법'을 "
                    "체험존과 굿즈로 풀어냅니다."
                ),
                hero_image_url="/static/img/snuggle_hero.svg",
                logo_url="/static/img/snuggle_logo.svg",
                color_primary="#517EA6",
                color_secondary="#4E8B6E",
                instagram_url="https://instagram.com/snuggle",
                website_url="https://snuggle.example.com",
                sort_order=2,
            )
            db.add(snuggle)

        db.commit()
        db.refresh(crackerhouse)
        db.refresh(snuggle)

        # ---------------- Popup Info ----------------
        if db.query(PopupInfo).count() == 0:
            start = date.today() + timedelta(days=7)
            end = start + timedelta(days=13)
            db.add(
                PopupInfo(
                    title="크래커하우스 X 스너글 팝업스토어",
                    subtitle="바삭하게 입고, 포근하게 세탁하기",
                    location_name="스타필드 빌리지",
                    address="경기도 하남시 위례섬안로 130 스타필드 빌리지 1층",
                    floor_info="1층 팝업존 A-12",
                    start_date=start,
                    end_date=end,
                    open_time=time(10, 30),
                    close_time=time(21, 0),
                    description=(
                        "패션과 세탁, 서로 다른 두 브랜드가 만나 '옷을 즐기고 관리하는 순간'을 "
                        "하나의 공간에서 경험할 수 있는 팝업스토어입니다."
                    ),
                    notice="현장 방문 시 사전예약 또는 현장예약(키오스크) 중 하나를 이용해주세요. 반려동물 동반은 어렵습니다.",
                    hero_image_url="/static/img/popup_hero.svg",
                )
            )

        # ---------------- Experience Zones ----------------
        if db.query(ExperienceZone).count() == 0:
            db.add_all(
                [
                    ExperienceZone(
                        name="크래커하우스 포토부스",
                        brand_id=crackerhouse.id,
                        description="이번 콜라보 컬렉션을 입고 즉석 필름 사진을 남길 수 있는 포토존입니다.",
                        duration_minutes=10,
                        capacity_per_slot=4,
                        image_url="/static/img/zone_photobooth.svg",
                        sort_order=1,
                    ),
                    ExperienceZone(
                        name="스너글 세탁 클래스",
                        brand_id=snuggle.id,
                        description="좋아하는 옷을 오래 입는 세탁·보관 팁을 배우는 미니 클래스.",
                        duration_minutes=15,
                        capacity_per_slot=6,
                        image_url="/static/img/zone_laundry_class.svg",
                        sort_order=2,
                    ),
                    ExperienceZone(
                        name="콜라보 굿즈 각인존",
                        brand_id=None,
                        description="구매한 콜라보 굿즈에 이니셜을 각인해주는 체험존 (공용).",
                        duration_minutes=8,
                        capacity_per_slot=3,
                        image_url="/static/img/zone_engraving.svg",
                        sort_order=3,
                    ),
                ]
            )

        # ---------------- Products ----------------
        if db.query(Product).count() == 0:
            db.add_all(
                [
                    Product(
                        brand_id=crackerhouse.id,
                        name="크래커하우스 X 스너글 콜라보 티셔츠",
                        description="세탁 라벨을 그래픽 모티프로 활용한 팝업 단독 티셔츠.",
                        price=39000,
                        image_url="/static/img/product_tee.svg",
                        category="의류",
                        is_collab_exclusive=True,
                        stock_qty=80,
                        sort_order=1,
                    ),
                    Product(
                        brand_id=crackerhouse.id,
                        name="크래커하우스 캡모자",
                        description="가볍게 매치하기 좋은 시그니처 캡모자.",
                        price=29000,
                        image_url="/static/img/product_cap.svg",
                        category="액세서리",
                        is_collab_exclusive=False,
                        stock_qty=45,
                        sort_order=2,
                    ),
                    Product(
                        brand_id=snuggle.id,
                        name="스너글 미니 세제 세트 (팝업 한정)",
                        description="팝업 방문 기념 미니 사이즈 세제 3종 세트.",
                        price=15000,
                        image_url="/static/img/product_detergent_set.svg",
                        category="세제",
                        is_collab_exclusive=True,
                        stock_qty=120,
                        sort_order=1,
                    ),
                    Product(
                        brand_id=snuggle.id,
                        name="스너글 세탁볼 + 파우치",
                        description="향이 오래 지속되는 세탁볼과 콜라보 파우치 세트.",
                        price=22000,
                        image_url="/static/img/product_laundry_ball.svg",
                        category="세탁용품",
                        is_collab_exclusive=False,
                        stock_qty=60,
                        sort_order=2,
                    ),
                ]
            )

        db.commit()

        # ---------------- Time slots (사전예약용, 팝업 기간 앞 7일치 생성) ----------------
        if db.query(TimeSlot).count() == 0:
            popup = db.query(PopupInfo).first()
            if popup:
                slot_days = min((popup.end_date - popup.start_date).days + 1, 14)
                d = popup.start_date
                for _ in range(slot_days):
                    t = popup.open_time
                    while True:
                        start_dt = t
                        end_minutes = t.hour * 60 + t.minute + 60
                        end_t = time(end_minutes // 60, end_minutes % 60)
                        if start_dt >= popup.close_time:
                            break
                        db.add(
                            TimeSlot(
                                date=d,
                                start_time=start_dt,
                                end_time=min(end_t, popup.close_time),
                                capacity=15,
                                booked_count=0,
                            )
                        )
                        next_minutes = t.hour * 60 + t.minute + 60
                        if next_minutes >= 24 * 60:
                            break
                        t = time(next_minutes // 60, next_minutes % 60)
                    d += timedelta(days=1)
                db.commit()

        # ---------------- Guestbook sample ----------------
        if db.query(GuestbookEntry).count() == 0:
            db.add_all(
                [
                    GuestbookEntry(nickname="민지", message="티셔츠 그래픽이 진짜 귀여워요! 잘 보고 갑니다 :)", sticker="❤️"),
                    GuestbookEntry(nickname="현우", message="세탁 클래스 체험존 신선하고 좋았어요.", sticker="🧺"),
                ]
            )
            db.commit()

        # ---------------- Admin ----------------
        if db.query(AdminUser).count() == 0:
            db.add(
                AdminUser(
                    username="admin",
                    hashed_password=hash_password("popup1234!"),
                    display_name="팝업 운영진",
                )
            )
            db.commit()

        print("시드 데이터 생성 완료.")
        print("관리자 계정 -> username: admin / password: popup1234!  (실서비스 배포 전 반드시 변경하세요)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
