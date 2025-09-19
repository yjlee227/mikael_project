# 개선된 순위 연속성 시스템: 2단계 분리 전환

## 🎯 **목표: 완벽한 순위 연속성 보장**

### 🚨 **기존 문제점**
- 1단계 수집 순서 ≠ 2단계 처리 순위
- 중복 URL 건너뛰기로 인한 순위 누락
- 랭킹 데이터 불완전성

### ✅ **해결 방안: 3단계 순위 매핑 시스템**

---

## 📋 **Phase 1: 1단계 - 순위 정보 포함 URL 수집**

### **개선된 URL 저장 포맷 (JSON)**

```python
# ===== 1단계: URL 수집 + 순위 정보 저장 =====

def collect_urls_with_rank_info():
    """순위 정보를 포함한 URL 수집"""

    collected_data = {
        "collection_info": {
            "city": CITY_NAME,
            "tab": TARGET_TAB,
            "timestamp": datetime.now().isoformat(),
            "target_products": TARGET_PRODUCTS,
            "max_pages": MAX_PAGES
        },
        "url_rank_mapping": [],  # 순위-URL 매핑
        "collection_stats": {
            "total_urls_found": 0,
            "total_pages_processed": 0,
            "collection_success": False
        }
    }

    current_rank = 1  # 전역 순위 (페이지 간 연속)
    current_page = 1
    current_listing_url = listing_page_url

    while len(collected_data["url_rank_mapping"]) < TARGET_PRODUCTS and current_page <= MAX_PAGES:
        print(f"\n📄 {current_page}페이지 URL 수집 중...")

        # 현재 페이지에서 URL 수집
        activity_urls = collect_activity_urls_only(driver)

        if not activity_urls:
            # 페이지 이동 로직 (기존과 동일)
            success, current_listing_url = go_to_next_page(driver, current_listing_url)
            if not success:
                break
            current_page += 1
            continue

        print(f"   📊 {current_page}페이지에서 Activity {len(activity_urls)}개 발견")

        # 각 URL에 순위 할당 (페이지 내 순서대로)
        for page_index, url in enumerate(activity_urls):
            if len(collected_data["url_rank_mapping"]) >= TARGET_PRODUCTS:
                break

            # 순위-URL-페이지 정보 저장
            url_info = {
                "rank": current_rank,
                "url": url,
                "page": current_page,
                "page_index": page_index + 1,
                "collected_at": datetime.now().isoformat(),
                "is_duplicate": is_url_processed_fast(url, CITY_NAME)  # 중복 여부 미리 체크
            }

            collected_data["url_rank_mapping"].append(url_info)

            print(f"   ✅ {current_rank}위 URL 할당: {url[:50]}... {'(중복)' if url_info['is_duplicate'] else ''}")

            current_rank += 1

        # 목표 달성 시 중단
        if len(collected_data["url_rank_mapping"]) >= TARGET_PRODUCTS:
            break

        # 다음 페이지 이동
        if current_page < MAX_PAGES:
            success, current_listing_url = go_to_next_page(driver, current_listing_url)
            if success:
                current_page += 1
                time.sleep(2)
            else:
                break

    # 수집 통계 업데이트
    collected_data["collection_stats"] = {
        "total_urls_found": len(collected_data["url_rank_mapping"]),
        "total_pages_processed": current_page,
        "collection_success": len(collected_data["url_rank_mapping"]) > 0,
        "duplicate_count": sum(1 for item in collected_data["url_rank_mapping"] if item["is_duplicate"]),
        "new_count": sum(1 for item in collected_data["url_rank_mapping"] if not item["is_duplicate"])
    }

    return collected_data

# 1단계 실행 및 저장
URL_DATA_FILE = f"klook_urls_data_{CITY_NAME}_{TARGET_TAB.replace('&', 'and').replace(' ', '_')}.json"

try:
    collected_data = collect_urls_with_rank_info()

    if collected_data["collection_stats"]["collection_success"]:
        # JSON 파일로 저장
        with open(URL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(collected_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 순위-URL 데이터를 '{URL_DATA_FILE}'에 저장!")
        print(f"   📊 총 {collected_data['collection_stats']['total_urls_found']}개 URL")
        print(f"   🆕 신규: {collected_data['collection_stats']['new_count']}개")
        print(f"   🔄 중복: {collected_data['collection_stats']['duplicate_count']}개")

        stage1_success = True
    else:
        print("⚠️ URL 수집 실패")
        stage1_success = False

except Exception as e:
    print(f"❌ 1단계 실행 실패: {e}")
    stage1_success = False
```

---

## 📋 **Phase 2: 2단계 - 순위 기반 상세 크롤링**

### **개선된 순위 연속성 처리**

```python
# ===== 2단계: 순위 정보 기반 상세 크롤링 =====

def crawl_with_preserved_ranks():
    """순위 정보를 보존하면서 상세 크롤링"""

    URL_DATA_FILE = f"klook_urls_data_{CITY_NAME}_{TARGET_TAB.replace('&', 'and').replace(' ', '_')}.json"

    if not os.path.exists(URL_DATA_FILE):
        print(f"❌ URL 데이터 파일 '{URL_DATA_FILE}'을 찾을 수 없습니다.")
        return False

    # URL 데이터 로드
    with open(URL_DATA_FILE, 'r', encoding='utf-8') as f:
        url_data = json.load(f)

    collection_info = url_data["collection_info"]
    url_rank_mapping = url_data["url_rank_mapping"]

    print(f"✅ URL 데이터 로드 완료:")
    print(f"   🏙️ 도시: {collection_info['city']}")
    print(f"   📑 탭: {collection_info['tab']}")
    print(f"   📊 총 URL: {len(url_rank_mapping)}개")
    print(f"   🕐 수집 시간: {collection_info['timestamp'][:19]}")

    # 드라이버 초기화 (2단계용)
    driver = setup_driver()
    if not driver:
        raise Exception("드라이버 초기화 실패")

    # 크롤링 통계
    crawling_stats = {
        "total_urls": len(url_rank_mapping),
        "processed_count": 0,
        "success_count": 0,
        "skip_count": 0,
        "error_count": 0,
        "actual_ranks_saved": []  # 실제 저장된 순위 목록
    }

    ranking_data = []

    print(f"\n📦 순위 기반 상세 크롤링 시작...")

    for i, url_info in enumerate(url_rank_mapping, 1):
        rank = url_info["rank"]
        url = url_info["url"]
        page = url_info["page"]
        is_duplicate = url_info["is_duplicate"]

        print(f"\n   🔍 {rank}위 처리 중... ({i}/{len(url_rank_mapping)})")
        print(f"      URL: {url[:60]}...")
        print(f"      원본 페이지: {page}페이지")

        crawling_stats["processed_count"] += 1

        # 중복 URL 건너뛰기 (순위는 유지)
        if is_duplicate or is_url_processed_fast(url, CITY_NAME):
            print(f"      ⏭️ {rank}위 중복 URL 건너뛰기")
            crawling_stats["skip_count"] += 1
            continue

        try:
            # 상품 페이지 이동
            driver.get(url)
            time.sleep(random.uniform(2, 4))
            print("📜 상품 상세 페이지 스크롤 실행...")
            smart_scroll_selector(driver)

            # 상품 데이터 추출 (원본 순위 사용)
            product_data = extract_all_product_data(driver, url, rank, city_name=CITY_NAME)

            # CSV 번호는 연속성 보장
            next_num = get_next_product_number(CITY_NAME)

            # 기본 구조 생성 (원본 순위 사용)
            base_data = create_product_data_structure(CITY_NAME, next_num, rank)
            base_data.update(product_data)
            base_data['탭'] = TARGET_TAB
            base_data['원본페이지'] = page  # 추가 정보

            # 이미지 처리 (기존 로직 그대로)
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
                # 처리 완료 마킹
                mark_url_processed_fast(url, CITY_NAME, next_num, rank)

                # 랭킹 정보 저장 (원본 정보 포함)
                ranking_info = {
                    "url": url,
                    "rank": rank,  # 원본 순위 보존
                    "csv_number": next_num,  # CSV 번호
                    "tab": TARGET_TAB,
                    "city": CITY_NAME,
                    "original_page": page,  # 원본 페이지 정보
                    "page_index": url_info["page_index"],
                    "collected_at": url_info["collected_at"],
                    "processed_at": datetime.now().isoformat()
                }
                ranking_data.append(ranking_info)

                crawling_stats["success_count"] += 1
                crawling_stats["actual_ranks_saved"].append(rank)

                print(f"      ✅ {rank}위 수집 완료 (CSV번호: {next_num})")
            else:
                print(f"      ❌ {rank}위 저장 실패")
                crawling_stats["error_count"] += 1

            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"      ❌ {rank}위 크롤링 실패: {e}")
            crawling_stats["error_count"] += 1
            continue

    # 드라이버 종료
    if driver:
        driver.quit()

    # 최종 통계 출력
    print(f"\n📊 순위 연속성 크롤링 완료!")
    print(f"   • 총 처리: {crawling_stats['processed_count']}개")
    print(f"   • 성공: {crawling_stats['success_count']}개")
    print(f"   • 건너뜀: {crawling_stats['skip_count']}개")
    print(f"   • 실패: {crawling_stats['error_count']}개")

    if crawling_stats["actual_ranks_saved"]:
        saved_ranks = sorted(crawling_stats["actual_ranks_saved"])
        print(f"   • 저장된 순위: {saved_ranks[:5]}{'...' if len(saved_ranks) > 5 else ''}")
        print(f"   • 순위 범위: {min(saved_ranks)}위 ~ {max(saved_ranks)}위")

    return ranking_data, crawling_stats

# 2단계 실행
try:
    ranking_data, crawling_stats = crawl_with_preserved_ranks()
    stage2_success = crawling_stats["success_count"] > 0
except Exception as e:
    print(f"❌ 2단계 실행 실패: {e}")
    stage2_success = False
```

---

## 📋 **Phase 3: 순위 연속성 검증 시스템**

### **순위 무결성 체크**

```python
def verify_rank_continuity():
    """순위 연속성 및 데이터 무결성 검증"""

    print(f"\n🔍 순위 연속성 검증 시작...")

    # 1. URL 데이터 파일 검증
    URL_DATA_FILE = f"klook_urls_data_{CITY_NAME}_{TARGET_TAB.replace('&', 'and').replace(' ', '_')}.json"

    if os.path.exists(URL_DATA_FILE):
        with open(URL_DATA_FILE, 'r', encoding='utf-8') as f:
            url_data = json.load(f)

        expected_ranks = [item["rank"] for item in url_data["url_rank_mapping"]]
        expected_range = f"{min(expected_ranks)}위 ~ {max(expected_ranks)}위"

        print(f"   ✅ 1단계 수집 순위: {expected_range} ({len(expected_ranks)}개)")
    else:
        print(f"   ❌ URL 데이터 파일 없음")
        return False

    # 2. 랭킹 데이터 검증
    if 'ranking_data' in locals() and ranking_data:
        actual_ranks = [item["rank"] for item in ranking_data]
        actual_range = f"{min(actual_ranks)}위 ~ {max(actual_ranks)}위"

        print(f"   ✅ 2단계 저장 순위: {actual_range} ({len(actual_ranks)}개)")

        # 순위 연속성 체크
        missing_ranks = set(expected_ranks) - set(actual_ranks)
        if missing_ranks:
            missing_sorted = sorted(list(missing_ranks))
            print(f"   ⚠️ 누락된 순위: {missing_sorted[:10]}{'...' if len(missing_sorted) > 10 else ''}")
            print(f"   📊 누락 이유: 중복 URL 또는 크롤링 실패")
        else:
            print(f"   🎉 완벽한 순위 연속성 달성!")
    else:
        print(f"   ❌ 랭킹 데이터 없음")
        return False

    # 3. CSV 데이터 검증
    try:
        from src.utils.file_handler import get_csv_stats
        csv_stats = get_csv_stats(CITY_NAME)

        if csv_stats and 'error' not in csv_stats:
            print(f"   ✅ CSV 저장: {csv_stats.get('total_products', 0)}개 상품")

            # 순위-CSV번호 일치성 체크
            if 'ranking_data' in locals() and ranking_data:
                csv_numbers = [item["csv_number"] for item in ranking_data]
                print(f"   ✅ CSV 번호 범위: {min(csv_numbers)} ~ {max(csv_numbers)}")
        else:
            print(f"   ❌ CSV 데이터 확인 실패")

    except Exception as e:
        print(f"   ⚠️ CSV 검증 실패: {e}")

    print(f"   🎯 순위 연속성 검증 완료!")
    return True

# 검증 실행
verify_rank_continuity()
```

---

## 📊 **최종 결과: 완벽한 순위 연속성**

### ✅ **보장되는 것들**

1. **순위 정확성**: 1단계 수집 순서 = 실제 순위
2. **순위 연속성**: 중복 건너뛰기와 무관하게 순위 보존
3. **데이터 무결성**: 원본 페이지, 수집 시간 등 모든 메타데이터 보존
4. **추적 가능성**: 각 상품의 수집 경로 완전 추적

### 📋 **생성되는 데이터 구조**

#### **1단계 출력: JSON 파일**
```json
{
  "collection_info": {
    "city": "삿포로",
    "tab": "티켓&입장권",
    "timestamp": "2025-09-19T10:30:00",
    "target_products": 10
  },
  "url_rank_mapping": [
    {
      "rank": 1,
      "url": "https://www.klook.com/ko/activity/1304-sapporo...",
      "page": 1,
      "page_index": 1,
      "is_duplicate": false
    }
  ]
}
```

#### **2단계 출력: 완벽한 순위 매핑**
```json
{
  "rank": 1,
  "csv_number": 157,
  "url": "https://www.klook.com/ko/activity/1304-sapporo...",
  "original_page": 1,
  "collected_at": "2025-09-19T10:25:15",
  "processed_at": "2025-09-19T14:30:22"
}
```

### 🎯 **순위 연속성 완벽 보장!**

이 시스템으로 중복 URL이 있어도 순위는 절대 어긋나지 않습니다!