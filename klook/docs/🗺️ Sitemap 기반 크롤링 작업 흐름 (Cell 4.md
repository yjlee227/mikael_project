🗺️ Sitemap 기반 크롤링 작업 흐름 (Cell 4.5)

  📋 전체 작업 흐름:

  graph TD
      A[Cell 4.5 시작] --> B[기존 수집 URL 정리]
      B --> C[Sitemap에서 새 URL 수집]
      C --> D{새 URL 있음?}
      D -->|없음| E[종료]
      D -->|있음| F[드라이버 재초기화]
      F --> G[Sitemap URL 루프 시작]

      G --> H[URL 방문 전 중복 체크]
      H --> I{이미 처리됨?}
      I -->|예| J[건너뛰기 0.001초]
      I -->|아니오| K[페이지 방문 5-10초]

      J --> L[다음 URL]
      K --> M[데이터 추출]
      M --> N[번호 할당]
      N --> O[이미지 다운로드]
      O --> P[CSV 저장]
      P --> Q{저장 성공?}
      Q -->|성공| R[캐시 마킹]
      Q -->|실패| S[실패 처리]

      R --> L
      S --> L
      L --> T{더 많은 URL?}
      T -->|있음| H
      T -->|없음| U[완료]

  🔍 상세 단계별 분석:

  1단계: 초기 준비 (1-2초)

  # 기존 수집 URL 정리
  collected_urls = set()
  for item in ranking_data:
      collected_urls.add(item['url'])
  print(f"📊 현재까지 수집된 URL: {len(collected_urls)}개")

  2단계: Sitemap URL 수집 (3-5초)

  sitemap_urls = collect_urls_from_sitemap(
      city_name=CITY_NAME,
      exclude_urls=list(collected_urls),  # 중복 제외
      limit=200
  )
  print(f"🎉 Sitemap에서 {len(sitemap_urls)}개 새로운 URL 발견!")

  3단계: 드라이버 준비 (2-3초)

  driver = setup_driver()
  print("✅ 드라이버 재초기화 성공")

  4단계: URL별 처리 루프

  현재 버전 (비효율적):

  for i, url in enumerate(sitemap_urls):
      print(f"🔍 Sitemap {current_rank}위 크롤링 중...")

      # ❌ 중복 체크 없이 바로 방문
      driver.get(url)  # 5-10초 소요
      time.sleep(random.uniform(2, 4))

      # 데이터 추출 (5-10초)
      product_data = extract_all_product_data(driver, url, current_rank)

      # 번호 할당 및 저장
      next_num = get_next_product_number(CITY_NAME)
      base_data = create_product_data_structure(CITY_NAME, next_num, current_rank)

      # CSV 저장
      if save_to_csv_klook(base_data, CITY_NAME):
          # ❌ 캐시 마킹 없음
          print("✅ 저장 완료")

  개선된 버전 (효율적):

  for i, url in enumerate(sitemap_urls):
      print(f"🔍 Sitemap {current_rank}위 크롤링 중...")

      # ✅ 1. 방문 전 초고속 중복 체크 (0.001초)
      if is_url_processed_fast(url, CITY_NAME):
          print(f"⏭️ 중복 URL 건너뛰기")
          current_rank += 1
          continue

      # ✅ 2. 새로운 URL만 방문 (5-10초)
      driver.get(url)
      time.sleep(random.uniform(2, 4))

      # 데이터 추출 (5-10초)
      product_data = extract_all_product_data(driver, url, current_rank)

      # 번호 할당 및 저장
      next_num = get_next_product_number(CITY_NAME)
      base_data = create_product_data_structure(CITY_NAME, next_num, current_rank)

      # CSV 저장
      if save_to_csv_klook(base_data, CITY_NAME):
          # ✅ 3. 성공 후 캐시 마킹 (0.001초)
          mark_url_processed_fast(url, CITY_NAME, next_num, current_rank)
          print("✅ 저장 및 캐시 마킹 완료")

  ⚡ 성능 비교:

  시나리오: Sitemap에서 20개 URL 발견

  현재 버전 (중복 체크 없음):

  1일차: 20개 URL × 15초 = 300초 (5분)
  2일차: 20개 URL × 15초 = 300초 (5분) ← 같은 URL 재처리!
  3일차: 20개 URL × 15초 = 300초 (5분) ← 또 재처리!

  개선 버전 (중복 체크 있음):

  1일차: 20개 URL × 15초 = 300초 (5분)
  2일차: 20개 중복 × 0.001초 = 0.02초 (즉시 건너뛰기!)
  3일차: 20개 중복 × 0.001초 = 0.02초 (즉시 건너뛰기!)

  🎯 핵심 문제:

  현재 Cell 4.5는:
  - 🐌 매번 모든 Sitemap URL을 재방문
  - 💾 같은 데이터 중복 저장 위험
  - ⏰ 엄청난 시간 낭비
  - 🚫 캐시 시스템 미활용

  이것이 바로 중복 체크가 필수인 이유입니다! 🚨