"""
시드 데이터 스크립트 - 크래커하우스 X 스너글 콜라보 팝업 데이터 구축
실행: python seed.py
"""
from datetime import datetime, timedelta
from app.database import SessionLocal, engine
from app import models
from app.auth import hash_password
from app.config import settings


def seed():
    # 테이블 리프레시 생성
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ── 1. 관리자 계정 생성 ──
        if not db.query(models.Admin).first():
            db.add(models.Admin(
                email=settings.ADMIN_EMAIL,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
            ))
            print(f"✅ 관리자 계정 생성: {settings.ADMIN_EMAIL}")

        # ── 2. 팝업 기본 정보 등록 (스타필드 빌리지) ──
        if not db.query(models.PopupInfo).first():
            db.add(models.PopupInfo(
                title="크래커하우스 X 스너글: 포근한 세탁소 팝업스토어",
                location="스타필드 빌리지 1F 중앙 광장",
                address="스타필드 빌리지 (기획 제안 입점 가상 위치)",
                start_date=datetime(2026, 9, 1),
                end_date=datetime(2026, 9, 14),
                operating_hours="매일 10:30 – 22:00 (스타필드 운영시간 기준)",
                description=(
                    "러프하고 빈티지한 워크웨어 브랜드 '크래커하우스'와 세상에서 가장 부드럽고 포근한 "
                    "세제 브랜드 '스너글'의 특별한 동행! 🧺\n"
                    "지루하게만 느껴지는 세탁 대기 시간을 향긋한 커피와 패션 스타일링, "
                    "오감 체험존으로 채운 포근한 코인 세탁소 팝업스토어입니다. 스타필드 빌리지에서 만나요!"
                ),
                hashtags="#크래커하우스,#스너글,#스타필드빌리지,#포근한세탁소,#팝업스토어,#콜라보레이션,#가을패션,#섬유유연제",
                instagram_url="https://www.instagram.com/crackerhouse_kr",
            ))
            print("✅ 팝업 정보 등록 완료")

        # ── 3. 체험존(PopupZone) 데이터 등록 ──
        if not db.query(models.PopupZone).first():
            zones = [
                {
                    "name": "스너글 블루스파클 센트룸 (Snuggle Scent Room)",
                    "description": "거대한 세탁기 드럼 속으로 들어온 듯한 360도 거울 공간. 스너글의 시그니처 향인 '블루 스파클' 유연제 향과 푹신푹신한 구름 쿠션 속에서 오감으로 포근함을 느껴보세요.",
                    "image_url": "/uploads/zone_snuggle.jpg",
                    "brand": models.BrandType.SNUGGLE
                },
                {
                    "name": "크래커하우스 데님 아틀리에 (Denim Atelier)",
                    "description": "바이오 세탁 공정으로 한층 더 부드럽고 자연스러운 워싱감을 자랑하는 크래커하우스의 가을 데님 컬렉션 쇼룸. 현장에서 나만의 이니셜 데님 패치를 핫프레싱으로 제작해드립니다.",
                    "image_url": "/uploads/zone_cracker.jpg",
                    "brand": models.BrandType.CRACKER_HOUSE
                },
                {
                    "name": "포근한 빨랫줄 포토스팟 (Laundry Photo Spot)",
                    "description": "갓 세탁한 부드러운 콜라보 의류와 귀여운 스너글 곰인형이 빨랫줄에 널려 있는 가든 포토존. 즉석 폴라로이드 사진을 찍어 빨랫줄에 집게로 걸고 소셜 미디어 이벤트에 참여해보세요.",
                    "image_url": "/uploads/zone_collab.jpg",
                    "brand": models.BrandType.CRACKER_HOUSE
                }
            ]
            for z in zones:
                db.add(models.PopupZone(**z))
            print("✅ 체험존 데이터 등록 완료")

        # ── 4. 브랜드별 콜라보 상품 등록 ──
        if not db.query(models.Product).first():
            sample_products = [
                # 👕 크래커하우스 (패션) 상품
                {
                    "name": "크래커하우스 X 스너글 허그 볼륨 후디",
                    "description": "스너글 곰인형이 크래커 데님 자켓을 걸친 귀여운 부클 자수가 새겨진 루즈핏 후디. 실크 바이오 세탁 워싱으로 한층 포근한 착용감.",
                    "price": 89000,
                    "image_url": "/uploads/placeholder.jpg",
                    "brand": models.BrandType.CRACKER_HOUSE,
                    "category": models.ProductCategory.VINTAGE_WEAR,
                    "stock": 30,
                },
                {
                    "name": "바이오 워싱 피그먼트 워크 셔츠",
                    "description": "자연스러운 물빠짐과 탄탄한 스티치 마감의 빈티지 아메리칸 스타일 셔츠. 런드리 테마의 가을 아우터 셔츠.",
                    "price": 79000,
                    "image_url": "/uploads/placeholder.jpg",
                    "brand": models.BrandType.CRACKER_HOUSE,
                    "category": models.ProductCategory.VINTAGE_WEAR,
                    "stock": 25,
                },
                {
                    "name": "콜라보 런드리 볼캡",
                    "description": "빈티지 세탁 세제 라벨을 자수 그래픽으로 위트 있게 살려낸 딥블루 세탁 가공 6패널 캡.",
                    "price": 38000,
                    "image_url": "/uploads/placeholder.jpg",
                    "brand": models.BrandType.CRACKER_HOUSE,
                    "category": models.ProductCategory.VINTAGE_WEAR,
                    "stock": 50,
                },
                # 🧺 스너글 (세제 및 케어) 상품
                {
                    "name": "스너글 허거블 코코아 & 오트밀 유연제 (1.8L)",
                    "description": "크래커하우스 워싱 마감을 기념해 한정판 패키지로 출시된 유기농 고농축 섬유유연제. 은은하고 달콤포근한 향.",
                    "price": 18500,
                    "image_url": "/uploads/placeholder.jpg",
                    "brand": models.BrandType.SNUGGLE,
                    "category": models.ProductCategory.FABRIC_SOFTER,
                    "stock": 100,
                },
                {
                    "name": "스너글 패브릭 퍼퓸 스프레이 (블루 스파클)",
                    "description": "세탁기에서 갓 나온 듯한 깨끗하고 시원한 런드리 향을 언제 어디서나 입힐 수 있는 휴대용 의류 향수.",
                    "price": 12000,
                    "image_url": "/uploads/placeholder.jpg",
                    "brand": models.BrandType.SNUGGLE,
                    "category": models.ProductCategory.FRAGRANCE,
                    "stock": 120,
                },
                {
                    "name": "세탁 코인 & 곰돌이 메탈 키링",
                    "description": "세탁 건조기 전용 메탈 코인 모형과 미니 스너글 베어 펜던트가 조합된 레트로 메탈 키링 굿즈.",
                    "price": 15000,
                    "image_url": "/uploads/placeholder.jpg",
                    "brand": models.BrandType.SNUGGLE,
                    "category": models.ProductCategory.GOODS,
                    "stock": 80,
                },
                {
                    "name": "포근한 드립백 커피 세트 (런드리 에디션)",
                    "description": "빨래가 돌아가는 45분 동안 느긋하게 드립하여 마시는 세탁소 전용 스페셜티 드립백 4개입 세트.",
                    "price": 10000,
                    "image_url": "/uploads/placeholder.jpg",
                    "brand": models.BrandType.SNUGGLE,
                    "category": models.ProductCategory.COFFEE,
                    "stock": 200,
                }
            ]
            for p in sample_products:
                db.add(models.Product(**p))
            print(f"✅ 콜라보 상품 {len(sample_products)}개 등록 완료")

        # ── 5. 사전예약 및 현장 대기 데모 시드 데이터 등록 ──
        if not db.query(models.Reservation).first():
            tomorrow = datetime.utcnow() + timedelta(days=1)
            
            # 사전예약 2건
            pre_res1 = models.Reservation(
                name="김철수",
                phone="010-1234-5678",
                email="chulsoo@gmail.com",
                reservation_type=models.ReservationType.PRE_REGISTRATION,
                reservation_date=tomorrow,
                reservation_time="14:00",
                people_count=2,
                status=models.ReservationStatus.WAITING
            )
            pre_res2 = models.Reservation(
                name="이영희",
                phone="010-9876-5432",
                email="younghee@naver.com",
                reservation_type=models.ReservationType.PRE_REGISTRATION,
                reservation_date=tomorrow,
                reservation_time="16:30",
                people_count=1,
                status=models.ReservationStatus.WAITING
            )
            db.add(pre_res1)
            db.add(pre_res2)

            # 현장 대기 3건 (오늘 날짜)
            onsite1 = models.Reservation(
                name="박지민",
                phone="010-5555-1234",
                reservation_type=models.ReservationType.ONSITE_KIOSK,
                reservation_date=datetime.utcnow(),
                waiting_number=1,
                people_count=3,
                status=models.ReservationStatus.COMPLETED  # 이미 입장한 팀
            )
            onsite2 = models.Reservation(
                name="최민수",
                phone="010-4444-5678",
                reservation_type=models.ReservationType.ONSITE_KIOSK,
                reservation_date=datetime.utcnow() - timedelta(minutes=10),
                waiting_number=2,
                people_count=2,
                status=models.ReservationStatus.WAITING  # 현재 대기 1순위
            )
            onsite3 = models.Reservation(
                name="정수아",
                phone="010-3333-9999",
                reservation_type=models.ReservationType.ONSITE_KIOSK,
                reservation_date=datetime.utcnow(),
                waiting_number=3,
                people_count=4,
                status=models.ReservationStatus.WAITING  # 현재 대기 2순위
            )
            db.add(onsite1)
            db.add(onsite2)
            db.add(onsite3)
            print("✅ 사전예약 및 현장 대기 테스트 데이터 등록 완료")

        db.commit()
        print("\n🧺 크래커하우스 X 스너글 시드 데이터 완료! 서버를 실행하세요: python run.py")

    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
