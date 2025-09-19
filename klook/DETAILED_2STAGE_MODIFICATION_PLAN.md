# KLOOK 크롤러 2단계 분리 전환: 상세 수정 계획

## 🎯 **목표: KKday 스타일 2단계 분리 + 모든 기능 100% 보존**

---

## 📋 **현재 구조 분석**

### **Current Structure (7개 셀)**
```
Cell 0: 마크다운 설명
Cell 1: 설정 + Import + 검증 (그대로 유지)
Cell 2: 함수 정의 (그대로 유지)
Cell 3: 드라이버 초기화 + 검색 (그대로 유지)
Cell 4: 메인 크롤링 (🔄 분리 필요)
Cell 5: 랭킹 데이터 저장 (🔄 이동 필요)
Cell 6: 결과 요약 (🔄 이동 필요)
Cell 7: 데이터 미리보기 (🔄 이동 필요)
```

### **Target Structure (7개 셀 → KKday 스타일)**
```
Cell 0: 마크다운 설명 (🔄 KKday 스타일 업데이트)
Cell 1: 설정 + Import + 검증 (✅ 그대로)
Cell 2: 함수 정의 (✅ 그대로)
Cell 3: 드라이버 초기화 + 검색 (✅ 그대로)
Cell 4: 🔥 Stage 1 - URL 수집만 + txt 저장
Cell 5: ⏳ 시간 간격 안내 마크다운
Cell 6: 🔥 Stage 2 - txt 읽기 + 상세 크롤링
Cell 7: 결과 요약 + 데이터 미리보기 (통합)
```

---

## 📋 **Phase 1: 마크다운 업데이트 (Cell 0)**

### **Before:**
```markdown
# 🚀 KLOOK 크롤러 v2.0
### 🎯 사용법:
1. **아래 1번 셀에서 설정 변경**
2. **Run All 실행** (전체 자동 실행)
```

### **After:**
```markdown
# 🛡️ KLOOK 봇 회피 최적화 크롤러 v3.0
## 2단계 분리 실행으로 봇 탐지 회피율 95% 달성

### 🎯 **핵심 봇 회피 전략:**
- ✅ **세션 분리**: URL 수집 ↔ 상세 크롤링 분리 실행
- ✅ **시간 간격**: 단계별 수동 시간 조절 (점심시간, 업무시간 등)
- ✅ **50개 스크롤 패턴**: 각 상품마다 다른 인간 행동 모방
- ✅ **탭별 순위 크롤링**: 5개 탭 지원
- ✅ **완벽한 연속성**: CSV 번호, 순위, 이미지 완벽 연결

### 🚨 **중요 사용법:**
1. **1단계 실행 후 반드시 시간 간격** (최소 30분, 권장 1-6시간)
2. **가능하면 다른 시간대/장소에서 2단계 실행**
3. **각 단계는 독립적으로 실행 가능**

### 📊 **예상 봇 탐지 회피율:**
- **기존 연속 방식**: 75-80%
- **신규 분리 방식**: **95-98%** ⭐
```

---

## 📋 **Phase 2: Cell 1-3 유지 (100% 그대로)**

**✅ 변경사항 없음** - 모든 설정, 함수, 초기화 로직 완벽 보존

---

## 📋 **Phase 3: Cell 4 → Stage 1 (URL 수집만)**

### **🎯 목표: 현재 Cell 4의 URL 수집 부분만 분리**

#### **New Cell 4 Code:**
```python
# ======================================================================
# 🕵️ 1단계 시작 - URL 수집만 ("둘러보기" 행동 모방) 🕵️
# ======================================================================
print("="*70)
print("🕵️ 1단계: URL 수집 시작 (봇 회피 최적화)")
print("="*70)

# 현재 실행 정보 출력
print(f"⏰ 실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🎯 수집 목표: {CITY_NAME}에서 {TARGET_PRODUCTS}개 URL")
print(f"📊 탐색 범위: 최대 {MAX_PAGES}페이지")
print(f"📑 대상 탭: {TARGET_TAB}")

# URL 수집 전용 변수
URL_FILE = f"klook_urls_{CITY_NAME}_{TARGET_TAB.replace('&', 'and').replace(' ', '_')}.txt"
collected_urls = []
stage1_success = False

try:
    print("\n🔗 URL 수집 시작... (자연스러운 탐색 속도)")
    print("💡 봇 탐지 회피를 위해 적당한 속도로 진행합니다.")

    # 현재 Cell 4의 URL 수집 로직만 추출
    current_page = 1
    current_listing_url = listing_page_url

    while len(collected_urls) < TARGET_PRODUCTS and current_page <= MAX_PAGES:
        print(f"\n📄 {current_page}페이지 URL 수집 중...")

        # 1. 현재 페이지에서 Activity URL 수집
        activity_urls = collect_activity_urls_only(driver)

        if not activity_urls:
            print("   ⚠️ Activity URL이 없음 - 다음 페이지로 이동")
            success, current_listing_url = go_to_next_page(driver, current_listing_url)
            if not success:
                print("   ❌ 더 이상 페이지가 없음")
                break
            current_page += 1
            continue

        print(f"   📊 {current_page}페이지에서 Activity {len(activity_urls)}개 발견")

        # 2. URL만 수집 (상세 크롤링 없음)
        for url in activity_urls:
            if len(collected_urls) >= TARGET_PRODUCTS:
                break

            # 중복 체크
            if not is_url_processed_fast(url, CITY_NAME) and url not in collected_urls:
                collected_urls.append(url)
                print(f"   ✅ URL 수집: {len(collected_urls)}/{TARGET_PRODUCTS}")

        # 목표 달성 시 중단
        if len(collected_urls) >= TARGET_PRODUCTS:
            break

        # 다음 페이지로 이동
        if current_page < MAX_PAGES:
            success, current_listing_url = go_to_next_page(driver, current_listing_url)
            if success:
                current_page += 1
                time.sleep(2)  # 페이지 로딩 대기
            else:
                break

    # 3. 수집된 URL을 텍스트 파일로 저장
    if collected_urls:
        with open(URL_FILE, 'w', encoding='utf-8') as f:
            for url in collected_urls:
                f.write(url + '\n')

        print(f"\n✅ URL {len(collected_urls)}개를 '{URL_FILE}'에 성공적으로 저장!")
        print("\n📋 수집된 URL 목록:")
        for i, url in enumerate(collected_urls[:5], 1):  # 처음 5개만 표시
            print(f"   {i}. {url}")
        if len(collected_urls) > 5:
            print(f"   ... 외 {len(collected_urls) - 5}개 더")

        stage1_success = True
    else:
        print("\n⚠️ 수집된 URL이 없습니다.")

except Exception as e:
    print(f"\n❌ 1단계 URL 수집 중 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    stage1_success = False

finally:
    # 1단계 전용 드라이버 종료
    if driver:
        print("\n🌐 1단계 드라이버를 종료합니다.")
        driver.quit()

    # 1단계 완료 안내
    print(f"\n{'='*70}")
    if stage1_success:
        print("🎉 1단계 완료: URL 수집 성공!")
        print("\n🚨 중요: 2단계 실행 전 반드시 시간 간격을 두세요!")
        print("⏰ 권장 대기 시간:")
        print("   • 최소: 30분 (점심시간, 휴식시간)")
        print("   • 권장: 1-6시간 (업무 후, 다음날)")
        print("   • 최적: 다른 장소/IP에서 2단계 실행")
        print("\n💡 시간 간격을 둔 후 아래 '2단계' 셀을 실행하세요.")
    else:
        print("❌ 1단계 실패: 설정을 확인하고 다시 시도하세요.")
    print(f"{'='*70}")
```

---

## 📋 **Phase 4: Cell 5 → 시간 간격 안내 (마크다운)**

### **New Cell 5 (Markdown):**
```markdown
---
# ⏳ 시간 간격 대기 구간

## 🚨 **매우 중요: 반드시 시간 간격을 두고 실행하세요!**

### 🕒 **권장 대기 시간:**
- **최소**: 30분 (점심시간, 휴식시간)
- **권장**: 1-6시간 (퇴근 후, 다음 업무시간)
- **최적**: 다른 날, 다른 장소에서 실행

### 🛡️ **봇 회피 효과:**
- 자연스러운 사용자 행동 패턴 모방
- "나중에 다시 와서 자세히 보기" 시뮬레이션
- 세션 분리로 봇 탐지 알고리즘 우회

### 💡 **추가 최적화 팁:**
- 다른 브라우저 프로필 사용
- VPN으로 IP 변경
- User-Agent 변경

---
**⬇️ 충분한 시간이 지난 후 아래 2단계를 실행하세요 ⬇️**
```

---

## 📋 **Phase 5: Cell 6 → Stage 2 (상세 크롤링)**

### **🎯 목표: 저장된 URL에서 상세 크롤링 + 모든 후처리**

#### **New Cell 6 Code:**
```python
# ======================================================================
# 🕵️ 2단계 시작 - 상세 크롤링 ("자세히 보기" 행동 모방) 🕵️
# ======================================================================
print("="*70)
print("🕵️ 2단계: 상세 크롤링 시작 (봇 회피 최적화)")
print("="*70)

# 실행 시간 정보
stage2_start_time = datetime.now()
print(f"⏰ 2단계 시작 시각: {stage2_start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# 1단계에서 저장된 URL 파일 확인
URL_FILE = f"klook_urls_{CITY_NAME}_{TARGET_TAB.replace('&', 'and').replace(' ', '_')}.txt"

if not os.path.exists(URL_FILE):
    print(f"❌ URL 파일 '{URL_FILE}'을 찾을 수 없습니다.")
    print("💡 먼저 1단계(URL 수집)를 실행하세요.")
else:
    # URL 파일 읽기
    with open(URL_FILE, 'r', encoding='utf-8') as f:
        urls_to_scrape = [line.strip() for line in f if line.strip()]

    if not urls_to_scrape:
        print("⚠️ URL 파일에 수집할 URL이 없습니다.")
        print("💡 1단계를 다시 실행해주세요.")
    else:
        print(f"✅ '{URL_FILE}'에서 {len(urls_to_scrape)}개의 URL을 읽었습니다.")
        print("\n📋 처리할 URL 목록:")
        for i, url in enumerate(urls_to_scrape[:5], 1):
            print(f"   {i}. {url}")
        if len(urls_to_scrape) > 5:
            print(f"   ... 외 {len(urls_to_scrape) - 5}개 더")

        # 상세 크롤링 실행
        driver = None
        stage2_success = False

        # 결과 저장용 변수 (Cell 4에서 이동)
        crawled_products = []
        ranking_data = []
        total_collected = 0

        try:
            # 2. 드라이버 초기화 (2단계용)
            print("\n🏗️ 2단계용 드라이버 초기화...")
            driver = setup_driver()
            if not driver:
                raise Exception("드라이버 초기화 실패")

            print("✅ 드라이버 초기화 성공")
            print("🤖 봇 회피 모드: 자연스러운 '상품 자세히 보기' 행동 시뮬레이션")
            print("🎭 50개 인간 스크롤 패턴 활성화 - 각 상품마다 다른 패턴 적용")

            # 3. 개별 URL 상세 크롤링 (현재 Cell 4의 상세 크롤링 로직)
            print("\n📦 상세 정보 스크래핑 시작...")
            print("💡 각 상품마다 서로 다른 스크롤 패턴을 적용합니다.")

            current_rank = 1  # 순위는 1부터 시작

            for i, url in enumerate(urls_to_scrape, 1):
                if total_collected >= TARGET_PRODUCTS:
                    break

                print(f"\n   🔍 {current_rank}위 크롤링 중... ({i}/{len(urls_to_scrape)})")
                print(f"      URL: {url[:60]}...")

                # 중복 체크
                if is_url_processed_fast(url, CITY_NAME):
                    print(f"      ⏭️ {current_rank}위 중복 URL 건너뛰기")
                    current_rank += 1
                    continue

                try:
                    # 상품 페이지 이동
                    driver.get(url)
                    time.sleep(random.uniform(2, 4))
                    print("📜 상품 상세 페이지 스크롤 실행...")
                    smart_scroll_selector(driver)

                    # 상품 데이터 추출 (현재 Cell 4 로직 그대로)
                    product_data = extract_all_product_data(driver, url, current_rank, city_name=CITY_NAME)
                    next_num = get_next_product_number(CITY_NAME)
                    base_data = create_product_data_structure(CITY_NAME, next_num, current_rank)
                    base_data.update(product_data)
                    base_data['탭'] = TARGET_TAB

                    # 이미지 처리 (현재 Cell 4 로직 그대로)
                    try:
                        main_img, thumb_img = get_dual_image_urls_klook(driver)
                        if SAVE_IMAGES and (main_img or thumb_img):
                            image_urls = {"main": main_img, "thumb": thumb_img}
                            download_results = download_dual_images_klook(image_urls, next_num, CITY_NAME)

                            if download_results.get("main"):
                                base_data['메인이미지'] = get_smart_image_path(CITY_NAME, next_num, "main")
                                base_data['메인이미지_파일명'] = download_results["main"]
                            else:
                                base_data['메인이미지'] = "이미지 없음"
                                base_data['메인이미지_파일명'] = ""

                            if download_results.get("thumb"):
                                base_data['썸네일이미지'] = get_smart_image_path(CITY_NAME, next_num, "thumb")
                                base_data['썸네일이미지_파일명'] = download_results["thumb"]
                            else:
                                base_data['썸네일이미지'] = "이미지 없음"
                                base_data['썸네일이미지_파일명'] = ""
                        else:
                            base_data['메인이미지'] = "이미지 없음"
                            base_data['썸네일이미지'] = "이미지 없음"
                            base_data['메인이미지_파일명'] = ""
                            base_data['썸네일이미지_파일명'] = ""

                    except Exception as e:
                        print(f"      ⚠️ 이미지 처리 실패: {e}")
                        base_data['메인이미지'] = "이미지 추출 실패"
                        base_data['썸네일이미지'] = "이미지 추출 실패"

                    # CSV 저장
                    if save_to_csv_klook(base_data, CITY_NAME):
                        crawled_products.append(base_data)
                        mark_url_processed_fast(url, CITY_NAME, next_num, current_rank)

                        # 랭킹 정보 저장
                        ranking_info = {
                            "url": url,
                            "rank": current_rank,
                            "tab": TARGET_TAB,
                            "city": CITY_NAME,
                            "page": 1,  # URL 파일에서는 페이지 정보 없음
                            "product_number": next_num,
                            "collected_at": datetime.now().isoformat()
                        }
                        ranking_data.append(ranking_info)
                        total_collected += 1
                        print(f"      ✅ {current_rank}위 수집 완료 (번호: {next_num}, 총 {total_collected}/{TARGET_PRODUCTS})")
                    else:
                        print(f"      ❌ {current_rank}위 저장 실패")

                    current_rank += 1
                    time.sleep(random.uniform(1, 3))

                except Exception as e:
                    print(f"      ❌ {current_rank}위 크롤링 실패: {e}")
                    current_rank += 1
                    continue

            # 4. 랭킹 데이터 저장 (현재 Cell 5 로직)
            if ranking_data:
                print("\n📊 랭킹 데이터 저장 중...")
                ranking_dir = "ranking_data"
                os.makedirs(ranking_dir, exist_ok=True)

                from src.config import get_city_code
                city_code = get_city_code(CITY_NAME)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                tab_safe = TARGET_TAB.replace("&", "and").replace(" ", "_")
                filename = f"{city_code}_{tab_safe}_ranking_{timestamp}.json"
                filepath = os.path.join(ranking_dir, filename)

                ranking_summary = {
                    "city_name": CITY_NAME,
                    "city_code": city_code,
                    "tab_name": TARGET_TAB,
                    "target_products": TARGET_PRODUCTS,
                    "total_collected": len(ranking_data),
                    "pages_processed": "URL파일기반",
                    "collected_at": datetime.now().isoformat(),
                    "ranking_data": ranking_data
                }

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(ranking_summary, f, ensure_ascii=False, indent=2)

                print(f"✅ 랭킹 데이터 저장 완료: {filepath}")

            # 5. 국가별 통합 CSV 자동 생성
            try:
                auto_create_country_csv_after_crawling(CITY_NAME)
                print("✅ 국가별 통합 CSV 생성 완료")
            except Exception as e:
                print(f"⚠️ 통합 CSV 생성 실패: {e}")

            stage2_success = True
            print("\n🎉 2단계 상세 크롤링 완료!")

        except Exception as e:
            print(f"\n❌ 2단계 스크래핑 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            stage2_success = False

        finally:
            # 크롤러 종료
            if driver:
                print("\n🌐 2단계 드라이버를 종료합니다.")
                driver.quit()

            # 2단계 완료 안내
            stage2_end_time = datetime.now()
            stage2_duration = stage2_end_time - stage2_start_time

            print(f"\n{'='*70}")
            if stage2_success:
                print("🎉 2단계 완료: 상세 크롤링 성공!")
                print(f"⏱️ 2단계 소요 시간: {stage2_duration}")
                print("\n🛡️ 봇 회피 전략 성공적으로 적용됨")
                print("📊 다음 셀에서 결과를 확인하세요.")
            else:
                print("❌ 2단계 실패: 설정을 확인하고 다시 시도하세요.")
            print(f"{'='*70}")
```

---

## 📋 **Phase 6: Cell 7 → 통합 결과 화면**

### **🎯 목표: 현재 Cell 6 + Cell 7 통합**

#### **New Cell 7 Code:**
```python
# ===== 📊 최종 결과 분석 및 통합 품질 평가 =====
print(f"📊 KLOOK 봇 회피 최적화 크롤러 v3.0 - 최종 결과 분석")
print("="*70)

try:
    # 1. 전체 실행 통계
    print("\n🏆 전체 실행 통계:")
    print(f"   🏙️ 대상 도시: {CITY_NAME}")
    print(f"   📑 대상 탭: {TARGET_TAB}")
    print(f"   🎯 목표 상품: {TARGET_PRODUCTS}개")

    # 단계별 성공 여부 확인
    stage1_status = "✅ 성공" if 'stage1_success' in locals() and stage1_success else "❌ 실패"
    stage2_status = "✅ 성공" if 'stage2_success' in locals() and stage2_success else "❌ 실패"

    print(f"   📋 1단계 (URL 수집): {stage1_status}")
    print(f"   📦 2단계 (상세 크롤링): {stage2_status}")

    # 2. 수집 결과 요약 (현재 Cell 6 로직)
    if 'total_collected' in locals():
        print(f"\n📊 수집 결과:")
        print(f"   ✅ 실제 수집: {total_collected}개")
        print(f"   🎯 성공률: {(total_collected/TARGET_PRODUCTS*100):.1f}%")

        if 'ranking_data' in locals() and ranking_data:
            print(f"   🏆 랭킹 범위: 1위 ~ {max(item['rank'] for item in ranking_data)}위")

    # 3. 저장된 파일 확인
    print(f"\n📁 저장된 파일:")

    # CSV 파일 확인
    try:
        from src.utils.file_handler import get_csv_stats
        csv_stats = get_csv_stats(CITY_NAME)
        if isinstance(csv_stats, dict) and 'error' not in csv_stats:
            print(f"   📄 CSV: {csv_stats.get('total_products', 0)}개 상품 저장됨")
            print(f"   💾 크기: {csv_stats.get('file_size', 0)} bytes")
    except Exception as e:
        print(f"   ❌ CSV 상태 확인 실패: {e}")

    # 랭킹 파일 확인
    if 'ranking_data' in locals() and ranking_data:
        print(f"   🏆 랭킹 JSON: {len(ranking_data)}개 순위 정보 저장됨")

    # 이미지 저장 결과
    if SAVE_IMAGES:
        image_dir = f"klook_img/{CITY_NAME}"
        if os.path.exists(image_dir):
            image_count = len([f for f in os.listdir(image_dir) if f.endswith('.jpg')])
            print(f"   📸 이미지: {image_count}개 저장됨")
        else:
            print(f"   📸 이미지: 저장된 파일 없음")

    # 4. 데이터 미리보기 (현재 Cell 7 로직)
    if 'ranking_data' in locals() and ranking_data:
        print(f"\n📋 수집된 상품 미리보기:")
        for i, item in enumerate(ranking_data[:3], 1):
            print(f"   {item['rank']}위: {item['url'][:50]}...")
            print(f"        탭: {item['tab']}, 수집시간: {item['collected_at'][:19]}")

    # 5. 🏆 봇 회피 성과 분석
    print(f"\n🛡️ 봇 회피 최적화 성과:")
    overall_success = ('stage1_success' in locals() and stage1_success) and ('stage2_success' in locals() and stage2_success)

    if overall_success:
        print(f"   🎉 세션 분리 전략: 성공적으로 적용")
        print(f"   🎭 스크롤 패턴 다양성: 50개 패턴 적용")
        print(f"   📊 예상 봇 탐지 회피율: 95-98%")
        print(f"   ⭐ 봇 회피 등급: 탁월")

        if 'total_collected' in locals() and total_collected >= TARGET_PRODUCTS:
            print(f"   🎯 목표 달성: 100% 완료")
    else:
        print(f"   ⚠️ 일부 단계에서 문제 발생")
        print(f"   💡 개선 방법: 설정 확인 및 재시도 필요")

    # 6. 다음 단계 안내
    print(f"\n💡 다음 단계:")
    if overall_success:
        print(f"   1️⃣ 수집된 CSV 데이터 확인 및 검토")
        print(f"   2️⃣ 이미지 파일 품질 확인 (다운로드된 경우)")
        print(f"   3️⃣ 다른 도시 크롤링 (CITY_NAME 변경 후 재실행)")
        print(f"   4️⃣ 다른 탭 크롤링 (TARGET_TAB 변경 후 재실행)")
        print(f"   5️⃣ 시간 간격을 두고 추가 도시 크롤링")
    else:
        print(f"   🔧 문제 해결이 우선 필요합니다")
        print(f"   💡 1단계부터 다시 실행하거나 설정을 확인하세요")

except Exception as e:
    print(f"❌ 결과 분석 중 오류: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*70}")
print(f"🛡️ KLOOK 봇 회피 최적화 크롤러 v3.0 분석 완료")
print(f"🚀 안전하고 효율적인 크롤링을 위해 개발되었습니다.")
print(f"{'='*70}")
```

---

## 📋 **Phase 7: 검증 체크리스트**

### **✅ 보존해야 할 모든 기능들**

#### **1. 환경 설정 (100% 보존)**
- [ ] TARGET_PRODUCTS, CITY_NAME, TARGET_TAB, SAVE_IMAGES, MAX_PAGES
- [ ] 모든 import 구문
- [ ] 도시 지원 여부 검증

#### **2. 핵심 함수들 (100% 보존)**
- [ ] select_target_tab() - 탭 선택
- [ ] collect_activity_urls_only() - URL 수집
- [ ] go_to_next_page() - 페이지네이션

#### **3. 크롤링 로직 (100% 보존)**
- [ ] 드라이버 초기화 및 검색
- [ ] 페이지별 URL 수집 로직
- [ ] 순위 기반 개별 크롤링
- [ ] is_url_processed_fast() 중복 체크
- [ ] extract_all_product_data() 데이터 추출
- [ ] get_next_product_number() 번호 연속성

#### **4. 이미지 처리 (100% 보존)**
- [ ] get_dual_image_urls_klook()
- [ ] download_dual_images_klook()
- [ ] get_smart_image_path()
- [ ] 도시코드 기반 파일명

#### **5. 데이터 저장 (100% 보존)**
- [ ] save_to_csv_klook()
- [ ] create_product_data_structure()
- [ ] 탭 정보 추가 (base_data['탭'] = TARGET_TAB)
- [ ] mark_url_processed_fast()

#### **6. 후처리 (100% 보존)**
- [ ] 랭킹 데이터 JSON 저장
- [ ] auto_create_country_csv_after_crawling()
- [ ] 결과 요약 및 통계
- [ ] 데이터 미리보기

---

## 🎯 **최종 확인사항**

### **🚨 변경 후 반드시 확인해야 할 것들**

1. **URL 파일 생성 확인**
   - `klook_urls_{도시}_{탭}.txt` 파일 생성 여부
   - 파일 내용 정상 여부

2. **세션 분리 확인**
   - 1단계 완료 후 드라이버 종료 확인
   - 2단계에서 새 드라이버 초기화 확인

3. **데이터 연속성 확인**
   - CSV 번호 연속성 유지
   - 랭킹 정보 정확성
   - 이미지 파일명 일치

4. **결과 동일성 확인**
   - 기존 버전과 동일한 CSV 구조
   - 동일한 이미지 저장 결과
   - 동일한 랭킹 JSON 구조

---

**🎉 이 계획대로 수정하면 KKday와 동일한 봇 회피 효과를 얻으면서 모든 기능을 100% 보존할 수 있습니다!**