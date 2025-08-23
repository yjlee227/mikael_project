# 🛠️ KLOOK 크롤링 시스템 함수 참조 가이드

## 📋 목차
- [네이밍 컨벤션](#네이밍-컨벤션)
- [그룹별 함수 목록](#그룹별-함수-목록)
- [핵심 워크플로우 함수](#핵심-워크플로우-함수)
- [함수 사용 예시](#함수-사용-예시)

---

## 🏗️ 네이밍 컨벤션

### **접두사 규칙**
| 접두사 | 용도 | 예시 |
|--------|------|------|
| `get_` | 데이터 추출/조회 | `get_price()`, `get_rating()` |
| `save_` | 저장 작업 | `save_batch_data()`, `save_collected_urls()` |
| `load_` | 로드/불러오기 | `load_crawler_state()`, `load_collected_urls()` |
| `click_` | UI 클릭 작업 | `click_search_button()`, `click_tab_enhanced()` |
| `collect_` | 수집 작업 | `collect_product_urls_from_page()` |
| `execute_` | 복합 실행 작업 | `execute_integrated_tab_selector_system()` |
| `validate_` | 검증 작업 | `validate_city()`, `validate_pagination_environment()` |
| `detect_` | 감지/탐지 작업 | `detect_klook_page_type()` |

### **접미사 규칙**
| 접미사 | 의미 | 예시 |
|--------|------|------|
| `_enhanced` | 향상된 버전 | `click_tab_enhanced()` |
| `_optimized` | 최적화된 버전 | `crawl_single_product_optimized()` |
| `_with_stop_check` | 정지 기능 통합 | `crawl_single_product_with_stop_check()` |
| `_fast` | 고속 처리 버전 | `is_url_processed_fast()` |

---

## 📚 그룹별 함수 목록

### **그룹 1: 기본 설정 및 hashlib 통합 시스템**

#### 🔧 핵심 설정 함수
- `get_city_code(city_name)` → `str`
  - **용도**: 도시명을 공항 코드로 변환
  - **매개변수**: `city_name` (str) - 도시명
  - **반환값**: 공항 코드 (예: "SEL", "ICN")

- `get_city_info(city_name)` → `tuple[str, str]`
  - **용도**: 통합된 도시 정보 가져오기
  - **매개변수**: `city_name` (str) - 도시명
  - **반환값**: `(대륙, 국가)` 튜플

#### ⚡ hashlib 고속 처리 함수
- `get_url_hash(url)` → `str`
- `is_url_processed_fast(url, city_name)` → `bool`
- `mark_url_processed_fast(url, city_name, product_number=None)` → `bool`
- `hybrid_is_processed(url, city_name)` → `bool`

### **그룹 2: 이미지 처리 및 데이터 저장**

#### 💾 데이터 저장 함수
- `save_batch_data(batch_results, city_name)` → `dict`
  - **용도**: 배치 데이터를 CSV로 저장 (도시ID + 연속번호 포함)
  - **매개변수**: 
    - `batch_results` (list) - 크롤링 결과 리스트
    - `city_name` (str) - 도시명
  - **반환값**: 저장 정보 딕셔너리

#### 📊 정보 수집 함수 (통일된 네이밍)
- `get_product_name(driver, url_type="Product")` → `str`
- `get_price(driver, logger=None)` → `str`
- `get_rating(driver, logger=None)` → `str`
- `get_review_count(driver, logger=None)` → `str`
- `get_language(driver, logger=None)` → `str`
- `get_categories(driver, logger=None)` → `str`
- `get_highlights(driver, logger=None)` → `str`

#### 🔧 정제 함수
- `clean_price(price_text)` → `str`
- `clean_rating(rating_text)` → `float|str`

#### 🖼️ 이미지 처리 함수
- `download_image(driver, product_name, city_name, product_number)` → `dict`

### **그룹 3: 상태 관리 시스템**

#### 📂 상태 관리 함수
- `load_crawler_state()` → `tuple[dict, set]`
- `save_crawler_state(state, new_url=None)` → `bool`

#### 🔍 URL 수집 함수
- `collect_basic_urls_from_current_view(driver)` → `list[str]`
  - **용도**: 현재 화면에서 상품 URL 수집 (스크롤 없음)
  - **매개변수**: `driver` - WebDriver 인스턴스
  - **반환값**: URL 리스트

- `collect_with_single_scan(driver)` → `list[str]`
  - **용도**: 단일 스캔으로 URL 수집 (기본 15개 제한)
  - **매개변수**: `driver` - WebDriver 인스턴스
  - **반환값**: 유효한 URL 리스트

- `fetch_klook_urls_from_sitemap(city_name)` → `list[str]`
  - **용도**: KLOOK sitemap에서 도시별 URL 추출
  - **매개변수**: `city_name` (str) - 도시명
  - **반환값**: sitemap URL 리스트

### **그룹 4: 확장성 개선 시스템**

#### 📊 분석 함수
- `analyze_pagination(driver)` → `dict`
  - **용도**: 페이지네이션 정보 분석 (총 상품 수, 페이지 수 등)
  - **반환값**: pagination 정보 딕셔너리

- `check_next_button(driver)` → `bool`
  - **용도**: KLOOK 다음 페이지 버튼 작동 확인
  - **반환값**: 다음 페이지 존재 여부

#### 🏙️ 도시 관리 함수
- `validate_city(city_name)` → `tuple[bool, str]`
- `show_supported_cities()` → `None`

### **그룹 5: 브라우저 제어 및 유틸리티**

#### 🚗 브라우저 제어 함수
- `setup_driver()` → `WebDriver`
  - **용도**: 크롬 드라이버 초기화 및 설정
  - **반환값**: 설정된 WebDriver 인스턴스

- `go_to_main_page(driver)` → `bool`
- `find_and_fill_search(driver, city_name)` → `bool`
- `click_search_button(driver)` → `bool`
- `handle_popup(driver)` → `bool`
- `click_view_all(driver)` → `bool`

#### 🌊 스크롤 및 대기 함수
- `smart_scroll_selector(driver)` → `None`
  - **용도**: 자연스러운 스크롤 패턴 랜덤 실행
  - **매개변수**: `driver` - WebDriver 인스턴스

- `smart_wait_for_page_load(driver, max_wait=None)` → `bool`

#### 🔧 유틸리티 함수
- `make_safe_filename(filename)` → `str`
- `retry_operation(func, operation_name, max_retries=None)` → `Any`

### **그룹 7: 통합 KLOOK 탭 셀렉터 & 전략 시스템**

#### 🎯 탭 시스템 핵심 함수
- `detect_tabs_with_enhanced_fallback(driver)` → `list[dict]`
  - **용도**: KLOOK 페이지의 카테고리 탭 감지
  - **반환값**: 탭 정보 딕셔너리 리스트

- `click_tab_enhanced(driver, tab_name, detected_tabs=None)` → `bool`
  - **용도**: 특정 탭을 안전하게 클릭
  - **매개변수**: 
    - `tab_name` (str) - 클릭할 탭명 (예: "전체", "투어&액티비티")
    - `detected_tabs` (list) - 감지된 탭 리스트
  - **반환값**: 클릭 성공 여부

- `collect_ranking_urls_enhanced(driver, limit=50, tab_name="")` → `list[str]`
  - **용도**: 현재 탭에서 상위 순위 URL 수집
  - **매개변수**:
    - `limit` (int) - 수집할 최대 URL 수
    - `tab_name` (str) - 탭 이름 (로깅용)
  - **반환값**: 순위 URL 리스트

#### 🚀 통합 실행 함수
- `execute_integrated_tab_selector_system(city_name, driver, interactive_mode=False)` → `dict`
  - **용도**: 전체 탭 시스템 통합 실행
  - **반환값**: 실행 결과 딕셔너리 (success, ranking_urls, strategy 등)

### **그룹 8: 최적화된 URL 수집 및 페이지네이션 분석**

#### 🔍 메인 실행 함수
- `execute_optimized_url_collection(driver, city_name, start_number, completed_urls, config=None)` → `dict`
- `run_optimized_group8()` → `dict`

### **그룹 9: 페이지네이션 크롤링 시스템**

#### 🔄 페이지네이션 제어 함수 (그룹 9-A)
- `save_pagination_state(city_name, current_page, current_list_url, total_crawled, target_products)` → `bool`
- `load_pagination_state(city_name)` → `dict|None`
- `click_next_page_enhanced(driver, current_page=None)` → `tuple[bool, str, str]`

#### 🎯 메인 크롤링 엔진 (그룹 9-B)
- `crawl_with_full_pagination(city_name, target_products=100, resume_session=True, pre_collected_urls=None)` → `list[dict]`
  - **용도**: URL 캐시를 활용한 지능형 크롤링 엔진
  - **매개변수**:
    - `target_products` (int) - 목표 상품 수
    - `pre_collected_urls` (list) - 사전 수집된 URL 리스트 (우선 사용)
  - **반환값**: 크롤링 결과 리스트

- `crawl_single_product_optimized(driver, product_url, product_number, city_name, continent, country, page_num)` → `dict|None`
  - **용도**: 단일 상품 상세 정보 크롤링
  - **반환값**: 상품 정보 딕셔너리 (26개 필드 포함)

### **그룹 10: KLOOK 전용 적응형 카테고리 시스템**

#### 🔍 페이지 분석 함수
- `detect_klook_page_type(driver)` → `str`
  - **반환값**: "product_detail" | "product_list" | "tab_based" | "non_klook"

- `find_klook_category_tabs(driver)` → `list[dict]`
- `navigate_to_klook_category(driver, city_name, target_category="투어")` → `tuple[bool, str]`

### **그룹 11: 정리된 크롤링 정지 시스템**

#### 🛑 정지 제어 함수
- `set_stop_flag()` → `None`
- `check_stop_flag()` → `bool`
- `reset_stop_flag()` → `None`

#### 🎯 정지 지원 크롤링 함수
- `crawl_single_product_with_stop_check(driver, product_url, product_number, city_name, continent, country, page_num)` → `dict|None`
  - **용도**: 정지 신호를 체크하며 단일 상품 크롤링
  - **특징**: 각 단계마다 정지 신호 확인

- `run_crawler_with_stop_support(city, num_products_to_crawl, use_group10=False, resume_session=True)` → `None`
  - **용도**: 정지 기능이 완전히 통합된 크롤링 실행

---

## 🚀 핵심 워크플로우 함수

### **1단계: 초기화 및 설정**
```python
# 브라우저 초기화
driver = setup_driver()

# 도시 정보 확인
continent, country = get_city_info("서울")
city_code = get_city_code("서울")
```

### **2단계: 검색 및 페이지 이동**
```python
# 검색 수행
go_to_main_page(driver)
find_and_fill_search(driver, "서울")
click_search_button(driver)
handle_popup(driver)
```

### **3단계: 탭 시스템 및 URL 수집**
```python
# 통합 탭 시스템 실행
result = execute_integrated_tab_selector_system("서울", driver)

# 또는 개별 제어
tabs = detect_tabs_with_enhanced_fallback(driver)
for tab in tabs:
    success = click_tab_enhanced(driver, tab)
    urls = collect_ranking_urls_enhanced(driver, 50)
```

### **4단계: 상품 크롤링**
```python
# 메인 크롤링 엔진 (URL 캐시 활용)
results = crawl_with_full_pagination(
    city_name="서울",
    target_products=100,
    pre_collected_urls=cached_urls
)

# 또는 개별 상품 크롤링
product_info = crawl_single_product_optimized(
    driver, url, 1, "서울", "아시아", "대한민국", 1
)
```

### **5단계: 데이터 저장**
```python
# 배치 데이터 저장
save_info = save_batch_data(results, "서울")
```

---

## 📖 함수 사용 예시

### **기본 크롤링 워크플로우**
```python
# 1. 초기화
driver = setup_driver()
city = "서울"

# 2. 검색
go_to_main_page(driver)
find_and_fill_search(driver, city)
click_search_button(driver)

# 3. URL 수집
tabs = detect_tabs_with_enhanced_fallback(driver)
all_urls = []
for tab in tabs:
    if click_tab_enhanced(driver, tab):
        urls = collect_ranking_urls_enhanced(driver, 50)
        all_urls.extend(urls)

# 4. 크롤링 실행
results = []
for i, url in enumerate(all_urls):
    result = crawl_single_product_optimized(
        driver, url, i+1, city, "아시아", "대한민국", 1
    )
    if result:
        results.append(result)

# 5. 저장
save_batch_data(results, city)
```

### **정지 기능 지원 크롤링**
```python
# 정지 지원 크롤링 실행
run_crawler_with_stop_support(
    city="서울",
    num_products_to_crawl=100,
    use_group10=False,
    resume_session=True
)

# 크롤링 중 정지
set_stop_flag()  # 다른 스레드에서 호출
```

### **URL 캐시 활용 크롤링**
```python
# 사전 URL 수집
sitemap_urls = fetch_klook_urls_from_sitemap("서울")

# 캐시된 URL로 직접 크롤링
results = crawl_with_full_pagination(
    city_name="서울",
    target_products=50,
    pre_collected_urls=sitemap_urls[:50]
)
```

---

## ⚠️ 주의사항

### **함수 호출 순서**
1. 반드시 `setup_driver()` 먼저 호출
2. 페이지 이동 후 `smart_scroll_selector()` 권장
3. URL 수집 전 `handle_popup()` 실행
4. 크롤링 후 `save_batch_data()` 로 즉시 저장

### **에러 처리**
- 모든 주요 함수는 예외 처리 내장
- `None` 또는 `False` 반환 시 실패로 간주
- 로그를 통해 상세 오류 정보 확인

### **성능 최적화**
- `hybrid_is_processed()` 로 중복 URL 사전 체크
- `collect_ranking_urls_enhanced()` 는 limit 매개변수로 수집량 제한
- 대용량 처리 시 `save_batch_data()` 로 주기적 저장

---

*📅 최종 업데이트: 2025-08-18*  
*🔧 총 함수 수: 120개 이상*  
*📊 네이밍 일관성: 95%*