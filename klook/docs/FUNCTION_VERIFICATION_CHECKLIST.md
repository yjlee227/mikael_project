# KLOOK → KKday 2단계 전환: 기능 보존 검증 체크리스트

## 🎯 목표: 모든 기능 100% 보존하여 2단계 분리 구조로 전환

---

## 📋 **1. 환경 설정 및 Import 함수들** (Cell 1)

### ✅ **사용자 설정 변수**
- [ ] `TARGET_PRODUCTS` - 수집할 상품 수
- [ ] `CITY_NAME` - 도시명
- [ ] `TARGET_TAB` - 크롤링할 탭
- [ ] `SAVE_IMAGES` - 이미지 저장 여부
- [ ] `MAX_PAGES` - 최대 페이지 수
- [ ] `PRODUCTS_PER_PAGE` - 페이지당 상품 수

### ✅ **Config 모듈 함수들**
- [ ] `CONFIG` - 전역 설정
- [ ] `UNIFIED_CITY_INFO` - 도시 정보
- [ ] `is_url_processed_fast(url, city)` - 중복 체크
- [ ] `mark_url_processed_fast(url, city, num, rank)` - 처리 완료 마킹

### ✅ **City Manager 함수들**
- [ ] `normalize_city_name(city)` - 도시명 정규화
- [ ] `is_city_supported(city)` - 도시 지원 여부 확인

### ✅ **Driver Manager 함수들**
- [ ] `setup_driver()` - 드라이버 초기화
- [ ] `go_to_main_page(driver)` - 메인 페이지 이동
- [ ] `find_and_fill_search(driver, city)` - 검색창 입력
- [ ] `click_search_button(driver)` - 검색 버튼 클릭
- [ ] `handle_popup(driver)` - 팝업 처리
- [ ] `smart_scroll_selector(driver)` - 스크롤 패턴

### ✅ **Parser 함수들**
- [ ] `extract_all_product_data(driver, url, rank, city_name)` - 상세 데이터 추출

### ✅ **File Handler 함수들**
- [ ] `create_product_data_structure(city, num, rank)` - 데이터 구조 생성
- [ ] `save_to_csv_klook(data, city)` - CSV 저장
- [ ] `get_dual_image_urls_klook(driver)` - 이미지 URL 추출
- [ ] `download_dual_images_klook(urls, num, city)` - 이미지 다운로드
- [ ] `auto_create_country_csv_after_crawling(city)` - 국가별 통합 CSV
- [ ] `get_next_product_number(city)` - 번호 연속성
- [ ] `get_smart_image_path(city, num, type)` - 이미지 경로
- [ ] `get_csv_stats(city)` - CSV 통계
- [ ] `get_city_info(city)` - 도시 정보
- [ ] `get_city_code(city)` - 도시 코드

---

## 📋 **2. 사용자 정의 함수들** (Cell 2)

### ✅ **탭 선택 함수**
- [ ] `select_target_tab(driver, tab_name)` - 지정된 탭 선택
  - [ ] 탭 선택자 매핑: "전체", "투어&액티비티", "티켓&입장권", "교통", "기타"
  - [ ] XPath 기반 탭 클릭
  - [ ] 페이지 로딩 대기

### ✅ **URL 수집 함수**
- [ ] `collect_activity_urls_only(driver)` - Activity URL만 순위대로 수집
  - [ ] 9개 다양한 CSS 셀렉터 시도
  - [ ] Activity URL 패턴 필터링 (`/activity/` 포함)
  - [ ] 중복 제거
  - [ ] 페이지당 최대 15개 제한

### ✅ **페이지네이션 함수**
- [ ] `go_to_next_page(driver, current_listing_url)` - 다음 페이지 이동
  - [ ] 8개 화살표 버튼 셀렉터 시도
  - [ ] 화살표 클릭 방식 우선 시도
  - [ ] URL 직접 변경 방식 fallback
  - [ ] 페이지 변화 검증
  - [ ] 스크롤 실행

---

## 📋 **3. 드라이버 초기화 및 검색** (Cell 3)

### ✅ **초기화 시퀀스**
- [ ] `setup_driver()` - Chrome 드라이버 설정
- [ ] `go_to_main_page(driver)` - KLOOK 메인 페이지 이동
- [ ] `handle_popup(driver)` - 팝업 처리
- [ ] `find_and_fill_search(driver, CITY_NAME)` - 도시 검색
- [ ] `click_search_button(driver)` - 검색 실행
- [ ] `select_target_tab(driver, TARGET_TAB)` - 탭 선택
- [ ] `listing_page_url` 저장 - 목록 페이지 URL 백업

---

## 📋 **4. 메인 크롤링 로직** (Cell 4)

### ✅ **페이지 루프 로직**
- [ ] `while total_collected < TARGET_PRODUCTS and current_page <= MAX_PAGES`
- [ ] 페이지별 진행 상황 표시
- [ ] 페이지당 처리 상품 수 제한

### ✅ **URL 수집 단계**
- [ ] `collect_activity_urls_only(driver)` 호출
- [ ] Activity URL 존재 여부 확인
- [ ] 빈 페이지 시 다음 페이지로 이동

### ✅ **개별 상품 크롤링 루프**
- [ ] URL 순차 처리 (순위 기반)
- [ ] `is_url_processed_fast(url, CITY_NAME)` - 중복 체크
- [ ] 상품 페이지 이동 (`driver.get(url)`)
- [ ] `smart_scroll_selector(driver)` - 스크롤 패턴 실행

### ✅ **데이터 추출 시퀀스**
- [ ] `extract_all_product_data(driver, url, current_rank, city_name=CITY_NAME)`
- [ ] `get_next_product_number(CITY_NAME)` - 번호 연속성
- [ ] `create_product_data_structure(CITY_NAME, next_num, current_rank)` - 기본 구조
- [ ] 데이터 병합 (`base_data.update(product_data)`)
- [ ] 탭 정보 추가 (`base_data['탭'] = TARGET_TAB`)

### ✅ **이미지 처리 시퀀스**
- [ ] `get_dual_image_urls_klook(driver)` - 이미지 URL 추출
- [ ] `download_dual_images_klook(image_urls, next_num, CITY_NAME)` - 다운로드
- [ ] `get_smart_image_path(CITY_NAME, next_num, "main")` - 메인 이미지 경로
- [ ] `get_smart_image_path(CITY_NAME, next_num, "thumb")` - 썸네일 경로
- [ ] 파일명 저장 (`메인이미지_파일명`, `썸네일이미지_파일명`)

### ✅ **데이터 저장 시퀀스**
- [ ] `save_to_csv_klook(base_data, CITY_NAME)` - CSV 저장
- [ ] `mark_url_processed_fast(url, CITY_NAME, next_num, current_rank)` - 처리 완료
- [ ] 랭킹 정보 수집 (ranking_data 배열)
- [ ] 수집 카운터 증가 (`total_collected += 1`)

### ✅ **페이지네이션 로직**
- [ ] `go_to_next_page(driver, current_listing_url)` - 다음 페이지
- [ ] URL 업데이트 (`current_listing_url = new_listing_url`)
- [ ] 페이지 카운터 증가 (`current_page += 1`)

### ✅ **최종 정리**
- [ ] `auto_create_country_csv_after_crawling(CITY_NAME)` - 국가별 통합 CSV
- [ ] 드라이버 종료 처리

---

## 📋 **5. 랭킹 데이터 저장** (Cell 5)

### ✅ **랭킹 JSON 생성**
- [ ] `get_city_code(CITY_NAME)` - 도시 코드 추출
- [ ] 타임스탬프 생성 (`datetime.now().strftime("%Y%m%d_%H%M%S")`)
- [ ] 파일명 생성 (`{city_code}_{tab_safe}_ranking_{timestamp}.json`)
- [ ] 랭킹 요약 구조화
  - [ ] `city_name`, `city_code`, `tab_name`
  - [ ] `target_products`, `total_collected`, `pages_processed`
  - [ ] `collected_at`, `ranking_data`
- [ ] JSON 파일 저장 (`json.dump`)

---

## 📋 **6. 결과 요약** (Cell 6)

### ✅ **수집 통계 표시**
- [ ] 목표 vs 실제 수집 비교
- [ ] 처리한 페이지 수
- [ ] 순위 범위 표시

### ✅ **파일 상태 확인**
- [ ] `get_csv_stats(CITY_NAME)` - CSV 파일 통계
- [ ] CSV 파일 크기 표시
- [ ] 랭킹 JSON 파일 확인
- [ ] 이미지 파일 개수 확인 (`klook_img/{CITY_NAME}` 폴더)

### ✅ **성공률 계산**
- [ ] `(total_collected/TARGET_PRODUCTS*100)` 계산
- [ ] 미달 시 참고사항 표시

---

## 📋 **7. 데이터 미리보기 및 품질 분석** (Cell 7)

### ✅ **랭킹 데이터 미리보기**
- [ ] 수집된 상품 처음 5개 표시
- [ ] URL, 탭, 페이지, 수집시간 정보

### ✅ **CSV 데이터 미리보기**
- [ ] `get_city_info(CITY_NAME)` - 도시 정보
- [ ] CSV 파일 경로 결정 (대륙/국가/도시 구조)
- [ ] `pandas.read_csv()` - CSV 로드
- [ ] 컬럼 목록 및 행 수 표시
- [ ] 상위 3개 상품 미리보기

### ✅ **데이터 품질 분석**
- [ ] 필수 필드 완성도 확인 (`상품명`, `가격`, `평점`, `URL`)
- [ ] v2.0 신규 필드 완성도 (`하이라이트`, `언어`)
- [ ] 언어별 분포 분석
- [ ] 가격 범위 분석 (최저가, 최고가, 평균가, 중간가)

### ✅ **최종 수집 결과 요약**
- [ ] 전체 상품 수집 개수
- [ ] 목표 달성률
- [ ] Sitemap 보완 사용 여부
- [ ] 하이라이트 수집 여부
- [ ] 언어 정보 수집 여부

---

## 🎯 **2단계 분리 매핑 계획**

### 🔍 **Stage 1 (URL 수집)에 포함될 기능들**
```
Cell 1: 환경 설정 (그대로)
Cell 2: 함수 정의 (그대로)
Cell 3: 드라이버 초기화 및 검색 (그대로)
Cell 4: URL 수집만 분리
  - collect_activity_urls_only()
  - go_to_next_page() (페이지네이션)
  - txt 파일 저장
  - 드라이버 종료
```

### 🔍 **Stage 2 (상세 크롤링)에 포함될 기능들**
```
Cell 5: 상세 크롤링만 분리
  - txt 파일 로드
  - extract_all_product_data()
  - 이미지 처리 전체 시퀀스
  - CSV 저장 전체 시퀀스
  - 랭킹 데이터 저장
  - 국가별 통합 CSV
Cell 6: 결과 요약 (그대로)
Cell 7: 데이터 미리보기 (그대로)
```

---

## ✅ **검증 완료 기준**

### 📋 **기능 보존 검증**
- [ ] 모든 import된 함수 100% 사용
- [ ] 모든 사용자 정의 함수 100% 사용
- [ ] 모든 설정 변수 100% 적용
- [ ] 모든 데이터 처리 로직 100% 보존

### 📋 **데이터 무결성 검증**
- [ ] 동일한 CSV 컬럼 구조
- [ ] 동일한 이미지 저장 로직
- [ ] 동일한 랭킹 JSON 구조
- [ ] 동일한 번호 연속성

### 📋 **사용자 경험 검증**
- [ ] 동일한 설정 변수들
- [ ] 동일한 진행 상황 표시
- [ ] 동일한 결과 요약 화면
- [ ] 동일한 데이터 미리보기

---

**🎯 이 체크리스트의 모든 항목이 ✅ 완료되어야만 2단계 전환이 성공적으로 완료됨**