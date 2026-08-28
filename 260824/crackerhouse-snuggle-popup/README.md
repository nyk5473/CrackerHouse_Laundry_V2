# 크래커하우스 X 스너글 팝업스토어 — 백엔드 + 데모 프론트

스타필드 빌리지 팝업스토어 기획안(크래커하우스 X 스너글 콜라보)을 기준으로 만든
FastAPI 백엔드 + 데모용 서버렌더링 프론트엔드입니다.

## 메뉴 구조 ↔ 기능 매핑

| 메뉴 | 하위 | 구현 |
|---|---|---|
| 메인 (`/`) | - | 팝업 하이라이트 + 사전등록 CTA |
| 브랜드소개 (`/brand`) | 크래커하우스 / 스너글 | 브랜드별 소개 탭 |
| 팝업정보 (`/popup`) | 체험존 | 기간/장소/시간 + 체험존 목록 |
| 상품 (`/products`) | 크래커하우스 / 스너글 | 브랜드별 상품 탭 |
| 방명록 (`/guestbook`) | - | 공용 방명록 (작성/조회) |
| 사전등록 (`/register`) | 사전예약(팝업) / 현장예약(키오스크) | 사전예약: 날짜+시간대 선택 / 현장예약: `/kiosk` 링크 |
| 키오스크 (`/kiosk`) | - | 출입구 앞 태블릿용 현장예약 전용 화면, 대기번호 발급 |
| 관리자 (`/admin`) | - | 로그인 + 예약/방명록 관리 대시보드 |

## 폴더 구조

```
app/
  main.py            FastAPI 앱 진입점 (라우터 등록, CORS, static 마운트)
  database.py         SQLAlchemy 엔진/세션 (기본 SQLite 파일 DB)
  models.py            DB 모델 (Brand, PopupInfo, ExperienceZone, Product,
                        GuestbookEntry, TimeSlot, Reservation, AdminUser)
  schemas.py           API 요청/응답 Pydantic 스키마
  security.py          비밀번호 해시 + 로그인 세션 토큰
  deps.py               관리자 인증 의존성 (쿠키 기반)
  seed.py                초기 데이터 시딩 스크립트
  routers/
    brands.py           GET  /api/brands, /api/brands/{slug}
    popup.py             GET  /api/popup, /api/popup/experience-zones
    products.py         GET/POST /api/products, PATCH .../stock (관리자)
    guestbook.py       GET/POST /api/guestbook, DELETE(숨김) (관리자)
    reservations.py  사전예약/현장예약/관리자 예약관리 (아래 API 목록 참고)
    auth.py                POST /api/admin/login, /logout, GET /me
    admin.py              GET /api/admin/dashboard, 방명록 전체관리
    pages.py               데모용 화면(Jinja2 템플릿) 라우팅
  templates/            데모 프론트엔드 HTML (Jinja2)
  static/css, static/js, static/img
requirements.txt
```

## 실행 방법

```bash
# 1) 가상환경(선택) 후 패키지 설치
pip install -r requirements.txt

# 2) 초기 데이터 시딩 (브랜드/팝업정보/체험존/상품/시간대/관리자 계정)
python -m app.seed

# 3) 서버 실행
uvicorn app.main:app --reload
```

- 웹 데모: http://localhost:8000
- API 문서(Swagger): http://localhost:8000/docs
- 관리자: http://localhost:8000/admin (계정: `admin` / `popup1234!`, `app/seed.py`에서 변경 가능)
- 키오스크 전용 화면: http://localhost:8000/kiosk (출입구 태블릿에 이 URL을 띄워두면 됩니다)

기본 DB는 프로젝트 루트에 생성되는 `popup.db` (SQLite) 파일입니다. 완전히 초기화하려면
`popup.db`를 삭제하고 `python -m app.seed`를 다시 실행하세요.

## 주요 API 요약

### 공개 API
- `GET /api/brands`, `GET /api/brands/{crackerhouse|snuggle}`
- `GET /api/popup`, `GET /api/popup/experience-zones`
- `GET /api/products?brand=crackerhouse|snuggle`
- `GET /api/guestbook`, `POST /api/guestbook`
- `GET /api/reservations/slots?date=YYYY-MM-DD` — 사전예약 가능 시간대 조회
- `POST /api/reservations/pre` — 사전예약 (날짜/시간대/인원 선택)
- `POST /api/reservations/onsite` — 현장예약(키오스크), 대기번호 자동 발급
- `GET /api/reservations/onsite/queue-status` — 현재 호출번호/대기인원 (키오스크·안내화면용)

### 관리자 API (로그인 쿠키 필요)
- `POST /api/admin/login`, `POST /api/admin/logout`, `GET /api/admin/me`
- `GET /api/admin/dashboard` — 오늘 예약/방명록/재고 요약
- `GET /api/reservations?type=PRE|ONSITE&status=&date=` — 예약 목록/필터
- `PATCH /api/reservations/{id}/status` — 예약 상태 변경(확정/취소/입장완료 등)
- `POST /api/reservations/onsite/call-next` — 다음 대기번호 호출
- `DELETE /api/guestbook/{id}` — 방명록 숨김 처리, `POST /api/admin/guestbook/{id}/restore` — 복원
- `POST /api/products`, `PATCH /api/products/{id}/stock` — 상품 등록/재고 수정

## 설계 메모

- **사전예약(PRE)**: `TimeSlot`(날짜별 1시간 단위, 정원 15명)을 미리 생성해두고, 예약 시
  잔여 인원을 확인 후 `booked_count`를 늘립니다. 취소 시 자동으로 인원이 반환됩니다.
- **현장예약(ONSITE)**: 시간대 없이 당일 `queue_number`(대기번호)만 발급하는 대기열 방식입니다.
  운영진이 `call-next`로 다음 번호를 호출하고, 입장 시 `VISITED`로 상태를 바꿉니다.
- **인증**: JWT 대신 서명된 세션 쿠키(itsdangerous)를 사용한 단순 구조입니다. 발표/데모 목적에
  맞춘 것이며, 실제 운영 배포 전에는 비밀번호 정책, HTTPS, 세션 만료 정책 등을 보강해야 합니다.
- **방명록 필터**: 데모 수준의 금칙어 필터만 포함되어 있습니다. 운영 시 별도 모더레이션 정책이 필요합니다.

## 실제 서비스로 확장할 때 고려할 점

1. `DATABASE_URL` 환경변수만 바꾸면 PostgreSQL 등으로 교체 가능하도록 `database.py`를 구성해뒀습니다.
2. 지금의 Jinja2 템플릿(`app/templates`)은 데모/발표용입니다. 실제 서비스에서는 React/Next.js 등으로
   프론트엔드를 새로 만들고, 동일한 `/api/*` 엔드포인트를 그대로 재사용하면 됩니다.
3. 문자/카카오톡 알림, 결제(굿즈 구매), 실물 프린터 대기표 발급 등은 이번 범위에는 포함되어 있지 않습니다.
4. 재고(`stock_qty`)는 관리자가 수기로 조정하는 구조입니다. 실제 구매 플로우가 생기면 주문 테이블과
   연동해 자동 차감하도록 확장하면 됩니다.
