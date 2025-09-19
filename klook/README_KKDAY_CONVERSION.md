# Klook → KKday 실행방식 전환 프로젝트

## 1. 프로젝트 개요

본 프로젝트는 **Klook 크롤러를 KKday의 2단계 분리 실행 방식으로 전환**하여 봇 탐지 회피 능력을 극대화하고 시스템 안정성을 향상시키는 것을 목표로 합니다.

### 현재 Klook 실행 방식 (Before)
```python
# 6개 셀로 구성된 단일 세션 실행
# Cell 1-2: 설정 및 드라이버 초기화
# Cell 3-4: URL 수집 (2단계)
# Cell 5-6: 상세 데이터 크롤링 (즉시 실행)
```

### 목표 KKday 실행 방식 (After)
```python
# Stage 1: URL 수집 전용 (별도 세션)
collector = KlookURLCollector(city="도쿄")
collector.collect_urls(max_urls=100)
# → 시스템 종료, 시간 간격 대기

# Stage 2: 상세 크롤링 전용 (별도 세션, 시간차 실행)
crawler = KlookDetailCrawler(city="도쿄")
crawler.crawl_details_from_saved_urls()
```

## 2. 핵심 전환 이점

### 2.1 봇 탐지 회피 강화
- **시간차 실행**: URL 수집과 상세 크롤링 사이에 자연스러운 시간 간격 확보
- **세션 분리**: 각 단계별로 독립적인 브라우저 세션 사용
- **행동 패턴 다양화**: 단계별로 다른 인간 행동 패턴 적용

### 2.2 시스템 안정성 향상
- **메모리 관리**: 각 단계 완료 후 리소스 완전 해제
- **오류 격리**: 한 단계의 문제가 다른 단계에 영향 미치지 않음
- **재시작 가능**: 각 단계를 독립적으로 재실행 가능

### 2.3 운영 효율성 증대
- **스케줄링**: 각 단계를 최적 시간대에 실행 가능
- **모니터링**: 단계별 성과 측정 및 최적화
- **확장성**: 단계별 병렬 처리 가능

## 3. 아키텍처 설계

### 3.1 새로운 클래스 구조

#### KlookURLCollector (Stage 1 전용)
```python
class KlookURLCollector:
    def __init__(self, city_name: str):
        self.city_name = city_name
        self.config = CONFIG['klook']

    def collect_urls(self, max_urls: int) -> None:
        """URL 수집만 수행하고 저장 후 종료"""

    def save_collected_urls(self) -> None:
        """수집된 URL을 파일로 저장"""
```

#### KlookDetailCrawler (Stage 2 전용)
```python
class KlookDetailCrawler:
    def __init__(self, city_name: str):
        self.city_name = city_name
        self.config = CONFIG['klook']

    def load_saved_urls(self) -> List[str]:
        """저장된 URL 목록 로드"""

    def crawl_details_from_saved_urls(self) -> None:
        """저장된 URL로부터 상세 정보 크롤링"""
```

### 3.2 데이터 연속성 보장

#### URL 저장 포맷
```json
{
    "collection_timestamp": "2025-09-19T10:30:00",
    "city_name": "도쿄",
    "total_urls": 150,
    "urls": [
        {
            "url": "https://www.klook.com/activity/12345/",
            "collected_at": "2025-09-19T10:25:15"
        }
    ]
}
```

#### 진행 상태 추적
```json
{
    "stage1_completed": true,
    "stage1_timestamp": "2025-09-19T10:30:00",
    "stage2_started": false,
    "urls_collected": 150,
    "details_crawled": 0
}
```

### 3.3 함수 재활용 매핑

| 기존 함수/기능 | Stage 1 (URL수집) | Stage 2 (상세크롤링) |
|---|---|---|
| `setup_driver()` | ✅ 활용 | ✅ 활용 |
| `navigate_to_search()` | ✅ 활용 | ❌ 불필요 |
| `collect_activity_urls()` | ✅ 핵심기능 | ❌ 불필요 |
| `extract_product_details()` | ❌ 불필요 | ✅ 핵심기능 |
| `download_images()` | ❌ 불필요 | ✅ 활용 |
| `save_to_csv()` | ❌ 불필요 | ✅ 활용 |
| `human_scroll_patterns()` | ✅ 활용 | ✅ 활용 |
| `city_manager` | ✅ 활용 | ✅ 활용 |
| `hash_checker` | ✅ 활용 | ✅ 활용 |

## 4. 실행 시나리오

### 4.1 표준 실행 순서

```python
# === Stage 1: URL 수집 (klook_stage1_runner.ipynb) ===
from src.scraper.url_collector import KlookURLCollector

# 설정
TARGET_CITY = "도쿄"
MAX_URLS = 200

# URL 수집 실행
collector = KlookURLCollector(city_name=TARGET_CITY)
collector.collect_urls(max_urls=MAX_URLS)

print(f"Stage 1 완료: {MAX_URLS}개 URL 수집 완료")
print("권장 대기시간: 30분 ~ 2시간")

# === 시간 간격 대기 (30분 ~ 2시간) ===

# === Stage 2: 상세 크롤링 (klook_stage2_runner.ipynb) ===
from src.scraper.detail_crawler import KlookDetailCrawler

# 상세 크롤링 실행
crawler = KlookDetailCrawler(city_name=TARGET_CITY)
crawler.crawl_details_from_saved_urls()

print("Stage 2 완료: 모든 상세 정보 크롤링 완료")
```

### 4.2 고급 운영 시나리오

#### 분산 실행 (여러 도시)
```python
# 오전: 여러 도시 URL 수집
cities = ["도쿄", "오사카", "교토"]
for city in cities:
    collector = KlookURLCollector(city_name=city)
    collector.collect_urls(max_urls=100)

# 오후: 순차적 상세 크롤링
for city in cities:
    crawler = KlookDetailCrawler(city_name=city)
    crawler.crawl_details_from_saved_urls()
```

#### 스케줄링 실행
```python
# 평일 오전 9시: URL 수집 (트래픽 낮은 시간)
# 평일 오후 3시: 상세 크롤링 (6시간 간격)
```

## 5. 기술적 구현 요구사항

### 5.1 필수 구현 기능

1. **URL 저장/로드 시스템**
   - JSON 포맷 URL 저장
   - 중복 URL 자동 제거
   - 진행 상태 추적

2. **오류 복구 메커니즘**
   - 단계별 재시작 지원
   - 부분 완료 지점부터 재개
   - 실패 URL 재시도 로직

3. **데이터 무결성 보장**
   - Hash 기반 중복 체크
   - CSV 데이터 검증
   - 이미지 다운로드 검증

### 5.2 성능 최적화

1. **메모리 관리**
   - 배치 처리 (URL 100개씩)
   - 정기적 가비지 컬렉션
   - 드라이버 리소스 완전 해제

2. **네트워크 최적화**
   - 요청 간 딜레이 조절
   - 실패 시 지수 백오프
   - 세션 풀 관리

## 6. 품질 보증

### 6.1 테스트 시나리오

```python
# 테스트 1: 소규모 URL 수집 (10개)
# 테스트 2: 중간 규모 실행 (50개)
# 테스트 3: 대규모 실행 (200개)
# 테스트 4: 오류 복구 테스트
# 테스트 5: 재시작 테스트
```

### 6.2 성공 기준

- ✅ 모든 기존 함수 100% 활용
- ✅ URL 수집률 95% 이상
- ✅ 상세 크롤링 성공률 90% 이상
- ✅ 메모리 누수 없음
- ✅ 봇 탐지 회피 성공

## 7. 마이그레이션 가이드

### 7.1 기존 사용자 대상

```python
# 기존 방식 (6개 셀 연속 실행)
# → 새 방식 (2개 노트북 시간차 실행)

# Before: KLOOK_Crawler_v2.ipynb (6 cells)
# After: klook_stage1_runner.ipynb + klook_stage2_runner.ipynb
```

### 7.2 설정 마이그레이션

```python
# config.py 업데이트 필요 항목
KLOOK_CONFIG = {
    'stage1_output_path': './data/collected_urls/',
    'stage2_output_path': './data/crawled_data/',
    'recommended_delay_hours': 2,
    'max_retry_attempts': 3
}
```

---

*이 문서는 Klook → KKday 실행방식 전환 프로젝트의 기술 명세서입니다. (최종 업데이트: 2025-09-19)*