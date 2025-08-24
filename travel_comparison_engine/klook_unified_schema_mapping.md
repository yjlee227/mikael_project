# 🔄 KLOOK → 통합 스키마 매핑표

## 현재 KLOOK 32컬럼 구조 → 통합 스키마 변환

### ⭐ 필수 필드 매핑

| 통합 스키마 필드 | KLOOK 32컬럼 | 변환 규칙 | 우선순위 |
|---|---|---|---|
| **provider** | ❌ | `"Klook"` 고정값 | ⭐⭐⭐ |
| **provider_product_id** | `URL` | URL에서 ID 추출 | ⭐⭐⭐ |
| **fetch_ts** | ❌ | `datetime.utcnow().isoformat()` | ⭐⭐⭐ |
| **destination_city** | `도시명` | 도시 정규화 사전 적용 | ⭐⭐⭐ |
| **country** | `국가` | 영문 국가명으로 변환 | ⭐⭐⭐ |
| **title** | `상품명` | 직접 매핑 | ⭐⭐⭐ |
| **price_value** | `가격_정제` | 숫자 추출 후 float | ⭐⭐⭐ |
| **price_currency** | `통화` | ISO4217 변환 | ⭐⭐⭐ |
| **landing_url** | `URL` | 직접 매핑 | ⭐⭐⭐ |

### 📊 기본 정보 매핑

| 통합 스키마 필드 | KLOOK 32컬럼 | 변환 규칙 | 우선순위 |
|---|---|---|---|
| **subtitle** | `부제목/설명` | 직접 매핑 | ⭐⭐ |
| **supplier_name** | `공급사` | 정규화 테이블 적용 | ⭐⭐ |
| **duration_hours** | `소요시간` | 시간 단위로 변환 | ⭐⭐ |
| **pickup** | `픽업포함` | bool 변환 | ⭐⭐ |
| **rating_value** | `평점_정제` | 0~5 스케일 정규화 | ⭐⭐ |
| **rating_count** | `리뷰수` | int 변환 | ⭐⭐ |
| **images** | `메인이미지URL`, `썸네일URL` | JSON 배열로 결합 | ⭐⭐ |

### 🆕 새로 추가할 필드

| 통합 스키마 필드 | 구현 방법 | 우선순위 |
|---|---|---|
| **fx_rate** | 실시간 환율 API 연동 | ⭐ |
| **theme_tags[]** | 상품명/카테고리에서 키워드 추출 | ⭐ |
| **language[]** | 언어 정보 크롤링 추가 | ⭐ |
| **included[]** | 포함항목 파싱 | ⭐ |
| **excluded[]** | 불포함항목 파싱 | ⭐ |
| **meeting_point** | 미팅포인트 크롤링 | ⭐ |
| **option_list[]** | 옵션별 가격 크롤링 | ⭐ |
| **cancel_policy** | 취소정책 파싱 | ⭐ |
| **availability_calendar[]** | 날짜별 가용성 | 🔄 |
| **rank_position** | 현재 랭킹 시스템 활용 | ⭐⭐ |
| **affiliate_url** | UTM/파트너 코드 추가 | 🔄 |

## 🔧 구현 단계

### Phase 1: 기본 매핑 (즉시 가능)
1. **필수 9개 필드** 매핑 함수 구현
2. **SQLite 테이블** 생성
3. **CSV → SQLite** 변환 스크립트

### Phase 2: 크롤링 확장 (개발 필요)
1. **언어/포함항목/취소정책** 크롤링 추가
2. **옵션별 가격** 수집
3. **테마 태그** 자동 추출

### Phase 3: 고도화 (선택사항)
1. **환율 API** 연동
2. **가용성 캘린더** 수집
3. **제휴 링크** 생성

---

## 📋 변환 함수 예시

```python
def klook_to_unified_schema(klook_data):
    """KLOOK 32컬럼 데이터를 통합 스키마로 변환"""
    return {
        # ⭐ 필수 필드
        "provider": "Klook",
        "provider_product_id": extract_id_from_url(klook_data['URL']),
        "fetch_ts": datetime.utcnow().isoformat(),
        "destination_city": normalize_city_name(klook_data['도시명']),
        "country": convert_to_english_country(klook_data['국가']),
        "title": klook_data['상품명'],
        "price_value": float(klook_data['가격_정제']),
        "price_currency": convert_to_iso4217(klook_data['통화']),
        "landing_url": klook_data['URL'],
        
        # 📊 기본 정보
        "rating_value": normalize_rating(klook_data['평점_정제']),
        "rating_count": int(klook_data['리뷰수'] or 0),
        "images": [klook_data['메인이미지URL'], klook_data['썸네일URL']],
        
        # 🆕 확장 필드
        "rank_position": klook_data.get('탭내_랭킹', 999),
        "theme_tags": extract_themes_from_title(klook_data['상품명'])
    }
```

---

## 🎯 다음 단계: SQLite 통합 DB 구현