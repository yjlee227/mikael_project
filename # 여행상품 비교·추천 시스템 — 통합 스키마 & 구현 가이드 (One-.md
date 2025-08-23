# 여행상품 비교·추천 시스템 — 통합 스키마 & 구현 가이드 (One-Page Doc)

본 문서는 **Klook / KKday / GetYourGuide / MyRealTrip**(이하 4사)의 해외 현지투어 상품을
**수집 → 정규화 → 매칭 → 검색/랭킹 → 비교/추천**까지 일관되게 구현하기 위한
**복사-붙여넣기용** 단일 문서입니다.

---

## 0. 목표 & 범위

- **목표**: 각 사이트에서 **상위 노출되는 상품**을 수집·정규화하고,
  동일/유사 상품을 **클러스터링**하여 **가격/정책/언어/옵션**을 비교.
  사용자 조건(언어/픽업/날짜/예산)에 맞춰 **최적 상품을 추천**.
- **대상**: Klook, KKday, GetYourGuide(GYG), MyRealTrip(MRT)
- **시간/통화 규칙**
  - `fetch_ts`: **UTC ISO8601**
  - `fx_rate`: **기준통화 → price_currency** 환율 스냅샷(예: KRW→USD 0.00073)
- **문자**: UTF-8, 태그 제거(필요 시 `original_*` 보존)

---

## 1. 파이프라인 개요 (MVP 기준)

1) **수집**: 목적지/테마 쿼리 + 각사 “인기/기본/베스트셀러” 정렬로 **Top-K** 추출  
2) **정규화**: 통화/세금/옵션/취소정책/언어/픽업/평점 스케일 표준화  
3) **저장**: upsert(hashlib), 스냅샷/환율/정렬옵션 로깅  
4) **매칭**: 룰(도시/거리/시간/테마) + BM25 + 임베딩(다국어) → **클러스터ID**  
5) **검색/랭킹**: BM25/FTS + (선택) 벡터검색, **가중합 점수**로 Top-N  
6) **비교 UI**: 클러스터 카드(플랫폼별 가격/정책/언어/옵션/평점/링크)

---

## 2. 핵심 키 (중복 방지/버전 추적)

- `provider_key` = `provider` + `provider_product_id` (유니크)
- `product_hash` = `sha1(normalized_core_fields)`
- `snapshot_key` = `provider_key` + `fetch_ts`

---

## 3. 통합 스키마 (Unified Travel Product Schema)

> **필수 필드**는 ⭐로 표시

### 3.1 식별/출처 (Identification)
- ⭐ **provider**: `Klook | KKday | GetYourGuide | MyRealTrip`
- ⭐ **provider_product_id**: 원본 상품 ID (예: `"3880363"`)
- ⭐ **fetch_ts**: 수집 시각(UTC ISO8601)
- **fx_rate**: 기준통화→`price_currency` 환율 스냅샷  
  - (선택) `fx_base_currency` 예: `"KRW"`

### 3.2 목적지/분류 (Destination & Taxonomy)
- ⭐ **destination_city**: 도시명(내부 Canonical 사전 별도)
- ⭐ **country**: 국가명(영문 권장)
- **theme_tags[]**: 테마/키워드(소문자, 동의어 병합)

### 3.3 상품 기본 정보 (Core)
- ⭐ **title**: 상품명
- **subtitle**: 부제/보조설명
- **supplier_name**: 운영사/공급사(정규화 테이블 권장)
- **duration_hours**: 소요시간(시간), 범위 `0 < h ≤ 72`
- **pickup (bool)**: 픽업 제공 여부
- **language[]**: `["ko","en","ja","zh","th","fr","de","es","it","pt","ru","ar","vi"]`

### 3.4 포함/불포함 (Inclusions)
- **included[]**: 포함 항목(“가이드”, “입장권”, “픽업” 등)
- **excluded[]**: 불포함 항목
- **meeting_point**: 미팅 포인트(주소/POI)

### 3.5 가격 (Price)
- ⭐ **price_value**: 대표가(가능하면 **성인 1인 총액**)
- ⭐ **price_currency**: ISO4217 (예: KRW, USD, JPY)
- **option_list[]**:
  - `name`: 옵션명(성인/아동, 시간대, 코스)
  - `price`: 옵션가
  - `includes[]`: 옵션별 포함
  - `duration`: 옵션별 소요시간(시간)
- (권장) `price_basis`: `adult | child | group | option_min`

> **대표가 규칙**: 성인 1인 총액이 없으면 **최소가 옵션**을 대표로 사용하고  
> `price_basis="option_min"`로 마킹. 세금/수수료 포함이 기본(불가 시 breakdown 확장).

### 3.6 리뷰/평가 (Ratings)
- **rating_value**: 평균 평점(0~5 정규화)
- **rating_count**: 리뷰 개수(≥0)

> 스케일 차이는 0~5로 **선형 변환**, 랭킹 시 `log1p(rating_count)` 사용.

### 3.7 취소/환불 (Cancel Policy)
- **cancel_policy**:
  - `free_until_hours`(예: 48)
  - `partial_fee`(비율/금액; 내부 규칙 고정 필요)
  - `no_refund_window`(예: 24)

> 문장 파싱 가이드 예:  
> “이용일 24시간 전 무료취소” → `free_until_hours=24`  
> “24~12시간 전 50% 환불” → `partial_fee=0.5`, 구간모델 필요 시 `policy_rules[]` 확장

### 3.8 가용성 (Availability)
- **availability_calendar[]**:
  - `date` (date/datetime)
  - `status`: `available | sold_out | limited | unavailable`

### 3.9 노출/순위 (Exposure)
- **rank_position**: 해당 플랫폼에서 같은 쿼리/정렬로 수집된 **Top-K 내 순위**(1=최상단)  
  - 재현성 위해 **수집 파라미터**를 감사 로그로 별도 저장.

### 3.10 링크/이미지 (Links & Images)
- ⭐ **landing_url**: 원본 상품 링크
- **affiliate_url**: 제휴/트래킹 링크(UTM/파트너코드)
- **images[]**: 이미지 URL(대표 3~10장 권장)

### 3.11 확장/운영 (Optional)
- `index_version`, `data_source_meta`(정렬/쿼리/UA/지역)  
- `text_fingerprint`(SimHash/MinHash), `route_summary`, `geo_points[]`  
- `supplier_canonical_id`(공급사 통합키)

---

## 4. 정규화·매핑 규칙 (요약)

1) **언어코드**: 플랫폼 표기 → 2자 코드로 통일 (`Korean`→`ko`)  
2) **평점**: 플랫폼 스케일을 0~5로 선형 변환  
3) **가격 총액화**: 세금/수수료 포함값을 표준. 불가 시 breakdown 기록  
4) **취소정책**: 최소 `free_until_hours` 파생. 구간형은 확장필드  
5) **옵션 분리**: 대표가 외 모든 가격은 `option_list[]`에 명시  
6) **순위**: `rank_position` 저장 + 동일 쿼리/정렬옵션 비교  
7) **테마 태그**: 소문자·트림, 동의어 사전 통합(“후지산”=“mount fuji”)

---

## 5. 랭킹(추천) 점수식 & 설명가능성

### 5.1 점수식(가중합 모델)
score =
w1 * norm_price

w2 * norm_rating_value

w3 * log1p(rating_count)

w4 * policy_score(cancel_policy)

w5 * language_match(user_lang)

w6 * pickup_match(user_pickup)

w7 * availability_score(date_range)

w8 * platform_rank_position_score

w9 * inclusion_score(included[])

pgsql
복사
편집

- `norm_price`: 0~1 스케일(저렴할수록 1)
- `norm_rating_value`: 평점/5
- `log1p(rating_count)`: 리뷰수 로그 스케일
- `policy_score`: 무료취소/부분환불/불가를 0~1로 규칙화
- `language_match`: 사용자 언어 지원 매칭(0/1 또는 0~1)
- `pickup_match`: 픽업 필요 여부 매칭(0/1)
- `availability_score`: 날짜 가능 여부(0/1)
- `platform_rank_position_score`: `1 / rank_position` 또는 정규화
- `inclusion_score`: 포함 항목 가중치(교통/가이드/입장권/식사 등)

> **가중치 초기값 예**:  
> 가격 0.25, 평점 0.2, 리뷰수 0.1, 정책 0.1, 언어 0.1, 픽업 0.05, 가용성 0.1, 플랫폼순위 0.05, 포함항목 0.05  
> → A/B 테스트/로그 데이터로 점진 최적화(LTR 가능)

### 5.2 “왜 이 결과인가?”
- 각 항목의 부분 점수와 근거(예: “무료취소 48시간 전까지”, “한국어 지원”)를
  카드에 툴팁/메타 라벨로 노출(설명가능성 향상).

---

## 6. 동일/유사 상품 매칭 (Entity Matching)

1) **룰 기반 후보**: 같은 도시 & 거리<10km & `duration±20%` & 테마 overlap  
2) **텍스트 유사도**: 제목/서브/코스 요약 → BM25 스코어  
3) **임베딩 유사도**: 다국어 문장 임베딩 코사인(예: multilingual-e5)  
4) **중복 체크**: SimHash/MinHash  
5) **최종 판정**: 임계치 또는 간단 모델(Logistic/LightGBM)  
6) **클러스터링**: `product_cluster_id` 부여 → 플랫폼별 가격/정책 비교

**평가**: 수작업 레이블 200쌍으로 Precision/Recall/F1 산출 → 임계치 튜닝.

---

## 7. 저장소 스키마 예시 (SQLite)

```sql
CREATE TABLE products (
  provider TEXT NOT NULL,
  provider_product_id TEXT NOT NULL,
  destination_city TEXT NOT NULL,
  country TEXT NOT NULL,
  theme_tags TEXT,               -- JSON
  title TEXT NOT NULL,
  subtitle TEXT,
  supplier_name TEXT,
  duration_hours REAL,
  pickup INTEGER DEFAULT 0,
  language TEXT,                 -- JSON
  included TEXT,                 -- JSON
  excluded TEXT,                 -- JSON
  meeting_point TEXT,
  price_value NUMERIC NOT NULL,
  price_currency TEXT NOT NULL,
  option_list TEXT,              -- JSON
  rating_value REAL,
  rating_count INTEGER,
  cancel_policy TEXT,            -- JSON
  availability_calendar TEXT,    -- JSON
  rank_position INTEGER,
  fetch_ts TEXT NOT NULL,        -- ISO8601
  fx_rate NUMERIC,
  landing_url TEXT NOT NULL,
  affiliate_url TEXT,
  images TEXT,                   -- JSON
  product_hash TEXT,
  PRIMARY KEY (provider, provider_product_id)
);
운영 전환 시 Postgres 권장(파티셔닝/인덱스/동시성).

8. 수집 재현성 & 감사 로깅 (필수)
search_query, sort_option, date_scope, destination_norm

fx_base_currency, user_agent, region, fetch_ts

같은 파라미터로 재실행 시 동일 rank_position 기대(동적 노출 예외).

9. 품질 체크리스트
 필수 필드(provider, provider_product_id, destination_city, country, title, price_value, price_currency, landing_url, fetch_ts) 누락 없음

 가격/통화/환율 일관성(대표가 기준 명확, 세금/수수료 포함 여부 기록)

 평점 스케일 0~5 정규화 완료

 언어 코드 표준화(동일 사전 사용)

 취소정책 시간 단위 통일(시간), 파싱 실패율 모니터링

 옵션/대표가 분리 명확(price_basis)

 순위/감사 로그 저장(재현성)

 이미지/링크 유효성(HTTP 200, 확장자)

 중복 방지 키/해시 작동

 이상치 필터(가격 0/음수/비정상 상하위 0.5% 컷)

10. 예시 JSON (샘플 2건)
json
복사
편집
{
  "provider": "Klook",
  "provider_product_id": "3880363",
  "fetch_ts": "2025-08-16T12:34:56Z",
  "fx_rate": 0.00073,
  "destination_city": "도쿄",
  "country": "Japan",
  "theme_tags": ["도쿄디즈니", "day trip", "family"],
  "title": "도쿄 디즈니랜드 1일 패스",
  "subtitle": "공식 파트너 / QR 입장 / 날짜 지정",
  "supplier_name": "Klook Japan KK",
  "duration_hours": 8.0,
  "pickup": false,
  "language": ["ja", "en", "ko"],
  "included": ["입장권"],
  "excluded": ["식사", "교통"],
  "meeting_point": "Maihama Station",
  "price_value": 8900.00,
  "price_currency": "JPY",
  "option_list": [
    {"name": "성인", "price": 8900.00, "includes": ["입장권"], "duration": 8.0},
    {"name": "아동", "price": 6600.00, "includes": ["입장권"], "duration": 8.0}
  ],
  "rating_value": 4.6,
  "rating_count": 2153,
  "cancel_policy": {
    "free_until_hours": 24,
    "partial_fee": null,
    "no_refund_window": 12
  },
  "availability_calendar": [
    {"date": "2025-08-20", "status": "available"},
    {"date": "2025-08-21", "status": "limited"}
  ],
  "rank_position": 1,
  "landing_url": "https://www.klook.com/....",
  "affiliate_url": "https://www.klook.com/...?aff_id=XXXX",
  "images": [
    "https://images.klook.com/photo1.jpg",
    "https://images.klook.com/photo2.jpg"
  ]
}
json
복사
편집
{
  "provider": "GetYourGuide",
  "provider_product_id": "A1B2C3",
  "fetch_ts": "2025-08-16T12:36:10Z",
  "fx_rate": 1370.55,
  "destination_city": "파리",
  "country": "France",
  "theme_tags": ["eiffel tower", "river cruise", "romantic"],
  "title": "에펠탑 + 세느강 크루즈 콤보",
  "subtitle": "우선입장 + 보트 탑승권",
  "supplier_name": "GYG Paris Ltd.",
  "duration_hours": 3.0,
  "pickup": false,
  "language": ["fr", "en", "ko"],
  "included": ["에펠탑 우선입장", "세느강 크루즈"],
  "excluded": ["호텔 픽업", "식사"],
  "meeting_point": "5 Avenue Anatole France, 75007 Paris",
  "price_value": 75.00,
  "price_currency": "EUR",
  "option_list": [
    {"name": "일반", "price": 75.00, "includes": ["콤보 티켓"], "duration": 3.0}
  ],
  "rating_value": 4.7,
  "rating_count": 987,
  "cancel_policy": {
    "free_until_hours": 48,
    "partial_fee": 0.5,
    "no_refund_window": 12
  },
  "availability_calendar": [
    {"date": "2025-08-19", "status": "sold_out"},
    {"date": "2025-08-20", "status": "available"}
  ],
  "rank_position": 3,
  "landing_url": "https://www.getyourguide.com/....",
  "affiliate_url": "https://www.getyourguide.com/...?partner_id=YYYY",
  "images": [
    "https://cdn.gyg.com/p1.jpg",
    "https://cdn.gyg.com/p2.jpg"
  ]
}
11. 구현 우선순위 (Action Items)
 정렬옵션 매핑표(4사: 인기/기본/베스트셀러 파라미터) 작성

 정규화 어댑터(통화/옵션/정책/언어) 유닛테스트

 매칭 MVP: 룰 → BM25 → 임베딩(다국어) → 임계치

 랭킹 함수(가중합) + 근거 노출(툴팁/라벨)

 비교 테이블(클러스터 카드) 생성

 감사 로그/재현성 필수 필드 기록

12. 참고: 검색엔진 선택 가이드(요약)
라이트: In-memory BM25 또는 SQLite FTS5 (무설치, 수만건까지)

프로: Meilisearch / OpenSearch(+벡터 스토어: FAISS/Milvus)

하이브리드 권장: 키워드(BM25) + 의미(벡터) 병합 + Facet 필터(날짜/가격/언어/픽업)