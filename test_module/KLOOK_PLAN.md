---
  🔧 1단계: 실행 오류 수정 (즉시 실행 가능하게)

  1-1. 변수 정의 오류 해결

  # 문제: NameError: name '_csv_loading_lock' is not defined
  # 위치: 그룹 8 - collect_urls_with_csv_safety()
  # 해결방법: threading.Lock() 추가 또는 해당 로직 제거

  # 문제: join() argument must be str, bytes, or os.PathLike object, not 'set'
  # 위치: 그룹 8 - filter_new_urls_from_csv()
  # 해결방법: set을 list로 변환 후 join 호출

  1-2. 함수 호출 타입 불일치 해결

  # completed_urls가 set인데 join()에 전달되는 문제
  # filter_new_urls_from_csv() 함수 내부 로직 수정 필요

  ---
  🌐 2단계: KLOOK 웹사이트 구조 분석

  2-1. KLOOK 실제 셀렉터 확인 작업

  방법: 현재 활성 드라이버로 KLOOK 사이트 접속하여 실제 구조 확인

  # 확인해야 할 KLOOK 셀렉터들:
  KLOOK_SELECTORS_TO_FIND = {
      "search_input": "검색창 셀렉터",
      "search_button": "검색 버튼 셀렉터",
      "popup_close": "팝업 닫기 셀렉터",
      "view_all": "전체보기 버튼 셀렉터",
      "product_title": "상품명 셀렉터",
      "product_price": "가격 셀렉터",
      "product_rating": "평점 셀렉터",
      "product_image": "상품 이미지 셀렉터",
      "next_page": "다음페이지 버튼 셀렉터"
  }

  2-2. KLOOK vs MyRealTrip 구조 차이점 분석

  - URL 패턴 차이
  - 페이지네이션 방식 차이
  - 상품 상세페이지 구조 차이

  ---
  🔄 3단계: 핵심 함수별 KLOOK 전환

  3-1. 그룹 5: 브라우저 제어 함수 (최우선)

  # go_to_main_page() - URL 변경
  기존: "https://www.myrealtrip.com/ko/"
  수정: "https://www.klook.com/ko/"

  # find_and_fill_search() - 검색창 셀렉터 변경
  기존: MyRealTrip 검색창 셀렉터들
  수정: KLOOK 검색창 셀렉터들

  # click_search_button() - 검색 버튼 셀렉터 변경
  기존: MyRealTrip 검색 버튼 셀렉터들
  수정: KLOOK 검색 버튼 셀렉터들

  # handle_popup() - 팝업 셀렉터 변경
  기존: MyRealTrip 팝업 셀렉터들
  수정: KLOOK 팝업 셀렉터들

  # click_view_all() - 전체보기 버튼 셀렉터 변경
  기존: MyRealTrip 전체보기 셀렉터들
  수정: KLOOK 전체보기 셀렉터들

  3-2. 그룹 1: 상품 정보 수집 함수

  # get_product_name() - 상품명 셀렉터 변경
  기존:
  - (By.CSS_SELECTOR, "h1")
  - (By.CSS_SELECTOR, ".product-title")
  수정:
  - KLOOK 실제 상품명 셀렉터 적용

  # get_price() - 가격 셀렉터 변경
  기존:
  - (By.CSS_SELECTOR, "span[style*='color: rgb(255, 87, 87)']")
  수정:
  - KLOOK 실제 가격 셀렉터 적용

  # get_rating() - 평점 셀렉터 변경
  기존: MyRealTrip 평점 셀렉터들
  수정: KLOOK 실제 평점 셀렉터들

  3-3. 그룹 2: 이미지 및 데이터 수집 함수

  # download_image() - 이미지 셀렉터 변경
  기존: MyRealTrip 이미지 셀렉터들
  수정: KLOOK 실제 이미지 셀렉터들

  # get_review_count() - 리뷰 수 셀렉터 변경
  # get_language() - 언어 정보 셀렉터 변경

  3-4. 그룹 9-A: 페이지네이션 시스템

  # click_next_page_enhanced() - 다음페이지 버튼 셀렉터 변경
  기존: MyRealTrip 페이지네이션 셀렉터들 9개
  수정: KLOOK 실제 페이지네이션 셀렉터들

  # attempt_page_recovery() - 복구 URL 변경
  기존:
  - "https://www.myrealtrip.com/offers?t=llp&qct=Manila"
  수정:
  - "https://www.klook.com/ko/city/manila-activities/"

  # is_valid_list_page_url() - URL 패턴 변경
  기존: "/experiences", "/offers", "/search"
  수정: KLOOK URL 패턴으로 변경

  ---
  🔗 4단계: 통합 시스템 KLOOK 전환

  4-1. 그룹 3: URL 수집 시스템 통합

  # collect_urls_with_csv_safety()
  # - KLOOK sitemap 시스템과 기존 수집 방식 완전 통합
  # - MyRealTrip URL 패턴 제거, KLOOK 패턴으로 통일

  # fetch_klook_urls_from_sitemap()
  # - 이미 KLOOK 전용으로 구현됨 (그룹 3에서 확인)
  # - 다른 함수들과 연결 강화 필요

  4-2. 그룹 10: 적응형 시스템 KLOOK 대응

  # detect_search_system_type() - KLOOK 페이지 타입 감지 로직 추가
  # find_tour_ticket_buttons() - KLOOK 투어/티켓 버튼 셀렉터 변경
  # analyze_button() - KLOOK 도메인 체크로 변경

  기존: if 'www.myrealtrip.com' in href:
  수정: if 'www.klook.com' in href:

  ---
  🎨 5단계: 브랜딩 및 UI 통일

  5-1. 로그 메시지 통일

  # 그룹 7: 웹사이트 검색 단계
  기존: "✅ 마이리얼트립 페이지 열기 완료"
  수정: "✅ KLOOK 페이지 열기 완료"

  # 그룹 12: UI 컨트롤 패널
  기존: "🚀 KLOOK 크롤러 (간소화 버전)" (이미 맞음)
  유지: 현재 상태 그대로

  5-2. 변수명 및 주석 통일

  # 파일명 패턴 통일
  기존: "myrealtrip_", "klook_" 혼재
  수정: 모든 파일명을 "klook_"로 통일

  # 주석 및 문서화 통일
  기존: "MyRealTrip 크롤러를 KLOOK으로 전환"
  수정: "KLOOK 전문 크롤링 시스템"

  ---
  🧪 6단계: 범용성 확보 및 안정성 강화

  6-1. Fallback 시스템 구축

  # 이중 셀렉터 시스템 (KLOOK 우선, MyRealTrip fallback)
  def get_product_name_universal(driver, url_type="Product"):
      # 1순위: KLOOK 셀렉터들
      klook_selectors = [...]

      # 2순위: MyRealTrip 셀렉터들 (fallback)
      mrt_selectors = [...]

      # 3순위: 범용 셀렉터들
      universal_selectors = [...]

  6-2. 사이트 자동 감지 시스템

  def detect_site_type(driver):
      """현재 사이트가 KLOOK인지 MyRealTrip인지 자동 감지"""
      current_url = driver.current_url
      if "klook.com" in current_url:
          return "KLOOK"
      elif "myrealtrip.com" in current_url:
          return "MyRealTrip"
      else:
          return "Unknown"

  def get_selectors_by_site(site_type, element_type):
      """사이트 타입에 따른 셀렉터 반환"""
      SELECTORS = {
          "KLOOK": {
              "product_title": [...],
              "product_price": [...],
              # ...
          },
          "MyRealTrip": {
              "product_title": [...],
              "product_price": [...],
              # ...
          }
      }
      return SELECTORS.get(site_type, {}).get(element_type, [])

  ---
  🧹 7단계: 코드 정리 및 최적화

  7-1. 중복 코드 제거

  - 동일한 기능의 함수들 통합
  - 사용되지 않는 legacy 코드 제거

  7-2. 성능 최적화

  - hashlib 시스템 활용도 극대화
  - 불필요한 중복 체크 로직 제거

  7-3. 에러 처리 강화

  - try-catch 블록 정리
  - 명확한 에러 메시지 추가

  ---
  🧪 8단계: 테스트 및 검증

  8-1. 기능별 단위 테스트

  # 각 그룹별 핵심 함수 테스트
  test_functions = [
      "go_to_main_page()",
      "find_and_fill_search()",
      "get_product_name()",
      "get_price()",
      "collect_urls_with_csv_safety()",
      "click_next_page_enhanced()"
  ]

  8-2. 통합 테스트

  - 전체 크롤링 프로세스 테스트
  - 다양한 도시에서 안정성 확인
  - 정지 기능 정상 작동 확인

  ---
  📊 작업 우선순위 매트릭스

  | 우선순위   | 작업 영역           | 영향도 | 난이도 | 예상 시간 |
  |--------|-----------------|-----|-----|-------|
  | 🔥 1순위 | 실행 오류 수정        | 극고  | 중   | 30분   |
  | 🔥 1순위 | 그룹 5 (브라우저 제어)  | 극고  | 고   | 2시간   |
  | ⚡ 2순위  | 그룹 1-2 (상품 정보)  | 고   | 고   | 3시간   |
  | ⚡ 2순위  | 그룹 9-A (페이지네이션) | 고   | 중   | 1시간   |
  | 📋 3순위 | 그룹 10 (적응형)     | 중   | 중   | 1시간   |
  | 📋 3순위 | 브랜딩 통일          | 중   | 저   | 30분   |
  | 🔧 4순위 | 범용성 확보          | 고   | 고   | 4시간   |
  | 🧪 5순위 | 테스트 및 검증        | 중   | 중   | 2시간   |

  총 예상 작업 시간: 14시간

  ---
  🎯 완료 기준

  ✅ 필수 완료 조건

  1. ❌ → ✅ 모든 실행 오류 해결
  2. ❌ → ✅ KLOOK 사이트에서 정상 크롤링 작동
  3. ❌ → ✅ MyRealTrip 브랜딩 완전 제거
  4. ❌ → ✅ UI와 실제 동작 일치

  🎖️ 추가 완료 조건 (범용성)

  1. KLOOK/MyRealTrip 자동 감지 및 대응
  2. Fallback 시스템으로 안정성 보장
  3. 120개 도시에서 안정적 동작
  4. 새로운 사이트 추가 시 확장 용이성