import sqlite3
import uuid
from datetime import datetime

def generate_id():
    return uuid.uuid4().hex[:12]

def run():
    conn = sqlite3.connect("crackerhouse.db")
    cursor = conn.cursor()

    products = [
        (
            generate_id(),
            "카페인 링거 반팔 티셔츠 (핑크)",
            "러프하고 캐주얼한 스트리트 무드의 핑크 링거 티셔츠. Kaffeine 프린팅 자수 마감 디자인.",
            59000,
            "/uploads/kaffeine_t_shirts_pink.jpg",
            "CRACKER_HOUSE",
            "VINTAGE_WEAR",
            30,
            1,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ),
        (
            generate_id(),
            "크래커 베이직 링거 티셔츠 (레드)",
            "오렌지 빛 레드 컬러 칼라 배색이 돋보이는 크래커하우스 베이직 코튼 링거 반팔 티셔츠.",
            59000,
            "/uploads/kracker_basic_t_shirts_red.jpg",
            "CRACKER_HOUSE",
            "VINTAGE_WEAR",
            30,
            1,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ),
        (
            generate_id(),
            "크래커 베이직 링거 티셔츠 (옐로우)",
            "레몬 옐로우와 화사한 레트로 배색 칼라 라인 디자인의 가벼운 링거 반팔 티셔츠.",
            59000,
            "/uploads/kracker_basic_t_shirts_yellow.jpg",
            "CRACKER_HOUSE",
            "VINTAGE_WEAR",
            30,
            1,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        )
    ]

    for p in products:
        cursor.execute(
            """
            INSERT INTO products (id, name, description, price, image_url, brand, category, stock, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            p
        )
        print(f"Added product: {p[1]}")

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    run()
