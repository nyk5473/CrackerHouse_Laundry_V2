# 스너글 향 취향테스트 — 핸드오프 문서

디자인 소스: `스너글 향 테스트 앱.dc.html` (모바일 앱 레이아웃, 390×844 기준)
에셋: `assets/*.webp` (마스코트 8종, 480px 폭 WebP)

---

## 1. 화면 구조

| 화면 | 진입 | 이탈 |
|---|---|---|
| `intro` | 앱 시작 | CTA 「테스트 시작하기」 → `question` (qIndex 0) |
| `question` | — | 옵션 탭 → 340ms 후 다음 문항 / 마지막 문항이면 `matching` · 뒤로 → 이전 문항, 첫 문항에서는 `intro` |
| `matching` | 6번째 답변 | 1400ms 후 `result` |
| `result` | — | 「다시」 → `intro` (상태 초기화) · 「결과 공유하기」 → 토스트 2200ms |

모든 화면은 기기 프레임 안에서 `position:absolute; inset:0` 로 정확히 844px를 채움. 상태바(52px)·홈 인디케이터는 프레임 레벨에서 항상 렌더.

### 화면별 레이아웃 요점
- **intro** — 상단 392px 히어로(방사형 그라디언트 + 상승하는 버블 3개 + 마스코트 `bob` 5s), 본문 텍스트, 향 7색 도트, 하단 고정 CTA(라운드 20px) + 캡션 「약 40초 · 6문항」.
- **question** — 상단바: 원형 뒤로가기(38px) + 6분할 세그먼트 진행바(높이 5px, gap 4px) + `n / 6` 카운터. 본문은 스크롤 영역, 질문 24px, 옵션 카드 최소 높이 56px(터치 타겟 충족), 라운드 18px.
- **matching** — 62px 스피너(`spin` 1s linear) + 문구 2줄, 중앙 정렬.
- **result** — 스크롤 시트: 틴트 그라디언트 히어로(하단 라운드 34px, 마스코트 236px) → 카드 3종(향 노트 / 향 취향 분포 / 추천 동선, 라운드 22px, `margin-top:-24px` 로 히어로에 겹침) → 하단 고정 액션바(그라디언트 페이드 + 공유 버튼 + 56px 「다시」). 결과 화면에서는 상태바 색이 흰색으로 전환.

---

## 2. 상태 모델

```
state = { screen, qIndex, answers[], picked, toast, toastText }
```

- `answers[i]` = i번째 문항에서 선택한 향 id (문자열). 뒤로가기 후 재선택 시 `answers.slice(0, qIndex)` 로 잘라내고 덮어씀 → 재답변이 중복 집계되지 않음.
- `picked` = 현재 문항에서 하이라이트할 옵션 인덱스(전환 애니메이션용). 다음 문항으로 넘어갈 때 `null`.
- 진행 계산: `tally` = 향 id별 선택 횟수 → 내림차순 정렬. 1위가 결과 향.
- **틴트(tint)** = 현재 1위 향의 색. 아직 답이 없으면 `#F25C05`. 진행바·옵션 선택 상태·스피너가 이 값을 따라가며, 답변이 쌓일수록 결과 색으로 물듦.
- 동점 처리: `Object.entries(tally)` 순서(= SCENTS 선언 순서, vanilla 우선) 기준 첫 항목이 승자.
- 타이머는 인스턴스에 보관(`_advance`, `_match`, `_tt`)하고 새 예약 전·언마운트 시 `clearTimeout`. 이걸 빠뜨리면 전환이 유실되어 matching에서 멈춤(실제로 겪은 버그).

---

## 3. 디자인 토큰

### 색
| 용도 | 값 |
|---|---|
| 배경 | `#F2E9DE` |
| 카드/서피스 | `#FFFFFF` |
| 서피스-2 (트랙) | `#F4EBE1` |
| 본문 잉크 | `#2B1F17` |
| 보조 텍스트 | `#8A7663` |
| 라인 | `#E5D6C5` (옵션 테두리 `#E9DBCB`) |
| 딥 브라운 (제목) | `#4A362A` |
| 프라이머리 오렌지 | `#F25C05` |
| 기기 베젤 | `#241C16 → #0E0B09` |
| 데스크 배경 | `#E4DACD` |

### 향(캐릭터) 색 — 결과 틴트
`vanilla #BC5B4C` · `cotton #2F7DA8` · `bouquet #A85A6B` · `citrus #4C8977` · `sparkle #5FA8CE` · `mellow #E28A94` · `sunshine #D6923A`

파생 규칙: 선택 옵션 배경 = 틴트 10% 알파, 그림자 = 틴트 16%, 노트 태그 배경 = 틴트 14%, 히어로 = `linear-gradient(158deg, 틴트, 틴트 72% 60%, #6B4A38)`, 버튼 그림자 = 틴트 34%.

### 타이포
- 디스플레이: **Bricolage Grotesque** (fallback Gothic A1) — 제목 30~33px / 질문 24px / 카드 제목 15.5px, weight 700, letter-spacing -0.01em
- 본문: **Gothic A1** — 13~14px, line-height 1.6~1.72, weight 600~700 (옵션 라벨 14px/600)
- 모노: **IBM Plex Mono** — 10~12.5px, 카운터·태그·캡션·상태바. tabular-nums.
- 한국어 줄바꿈: `word-break: keep-all` + `overflow-wrap: break-word`, 문단은 `text-wrap: pretty`.

### 형태·모션
- 라운드: 기기 44 / 히어로 하단 34 / 카드 22 / CTA·버튼 20 / 옵션 18 / 태그 8 / 도트·진행바 999
- 그림자: 카드 `0 1px 2px rgba(43,31,23,.04)`, 선택 옵션 `0 6px 16px 틴트16%`, 기기 `0 40px 90px rgba(30,20,12,.45)`
- 전환: 화면 진입 `slideUp .38s cubic-bezier(.16,1,.3,1)`, 탭 피드백 `scale(.975) .12s`, 진행바/옵션 색 `.18~.3s ease`, 분포 바 `width .8s cubic-bezier(.16,1,.3,1)`
- 키프레임: `rise`(버블 6s, delay 0/1.6/3.1s), `bob`(마스코트 5s), `spin`, `slideUp`, `fadeIn`

---

## 4. 콘텐츠 데이터

두 배열이 전체 콘텐츠를 담고 있으며, 그대로 JSON으로 떼어내 쓸 수 있습니다. 원본은 `스너글 향 테스트 앱.dc.html` 의 로직 상단 `SCENTS`, `QUESTIONS` 입니다.

```
SCENTS[] : { id, name, short, exclusive, color, desc, notes: [{tag, text}] | null, pairing }
QUESTIONS[] : { prompt, options: [{ label, scent }] }   // 6문항 × 7옵션
```

- 향 7종 중 `vanilla`(빈티지 바닐라)만 `exclusive: true` → 결과 히어로에 「POP-UP EXCLUSIVE · 콜라보 단독」 칩, 그리고 유일하게 `notes` 3단(TOP/MIDDLE/BASE)을 가짐. 나머지 6종은 `notes: null` → 향 노트 카드 자체를 렌더하지 않음.
- 각 문항의 7개 옵션은 향 7종과 1:1 대응(순서: cotton, bouquet, citrus, sparkle, mellow, sunshine, vanilla).
- 마스코트 매핑: `assets/{id}.webp`, intro는 `assets/guide.webp`.

---

## 5. 구현 시 주의점

1. **이미지 src에 미해결 템플릿 값을 넣지 말 것** — 스트리밍 중 리터럴 URL로 요청이 나가 404가 남습니다. 결과 마스코트는 `background-image` 로 렌더 중.
2. **틴트 파생색은 알파 합성으로** — hex → rgba 헬퍼 하나(`hexA(hex, a)`)로 모든 파생값을 계산. 별도 색 상수를 만들지 않습니다.
3. **터치 타겟** — 옵션 56px, 뒤로가기 38px(주변 여백 포함 44px 이상 확보), 하단 액션바 버튼 56px.
4. **다크모드** — 원본 웹 버전에는 `prefers-color-scheme` 팔레트가 있었으나 앱 버전에서는 제외했습니다. 필요하면 배경/서피스/라인/잉크 4개 토큰만 스왑하면 됩니다.
5. **공유** — 현재는 토스트만. 실제 구현은 Web Share API(`navigator.share`) 또는 클립보드 복사 + 결과 이미지 생성.
