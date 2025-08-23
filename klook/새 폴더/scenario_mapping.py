# =============================================================================
# 🎯 우리 시나리오에 맞는 함수 매핑 및 로직 설계
# =============================================================================

def execute_tab_based_sequential_crawling(city_name, driver, target_products_per_tab=50):
    """
    🚀 탭별 순차 페이지네이션 크롤링 (우리 시나리오 완벽 구현)
    
    시나리오:
    1. 전체→투어&액티비티→티켓&입장권→교통→기타 순서
    2. 각 탭마다 페이지별 15개 URL 수집 → 즉시 상세크롤링
    3. 10개마다 CSV 저장
    4. 랭킹 순서 보장
    """
    print(f"🎯 {city_name} 탭별 순차 크롤링 시작!")
    print("=" * 60)
    
    # 탭 순서 정의 (랭킹 우선순위)
    tab_sequence = [
        ("전체", 50),
        ("투어&액티비티", 50), 
        ("티켓&입장권", 50),
        ("교통", 50),
        ("기타", 50)
    ]
    
    all_results = []
    overall_rank = 1  # 전체 랭킹
    
    # 1. 탭 감지
    print("🔍 탭 구조 감지...")
    detected_tabs = detect_tabs_with_enhanced_fallback(driver)
    if not detected_tabs:
        print("❌ 탭 감지 실패")
        return []
    
    continent, country = get_city_info(city_name) or ("아시아", "대한민국")
    
    # 2. 각 탭별 순차 처리
    for tab_index, (tab_name, target_count) in enumerate(tab_sequence):
        print(f"\n🔄 [{tab_index+1}/5] '{tab_name}' 탭 크롤링 시작 (목표: {target_count}개)")
        
        # 2-1. 탭 클릭
        if not click_tab_enhanced(driver, tab_name, detected_tabs):
            print(f"❌ '{tab_name}' 탭 클릭 실패, 건너뜀")
            continue
        
        # 2-2. 해당 탭에서 페이지네이션 크롤링
        tab_results = crawl_single_tab_with_ranking(
            driver, city_name, tab_name, target_count, 
            continent, country, overall_rank
        )
        
        all_results.extend(tab_results)
        overall_rank += len(tab_results)
        
        print(f"✅ '{tab_name}' 탭 완료: {len(tab_results)}개 크롤링")
    
    print(f"\n🎉 전체 탭별 크롤링 완료! 총 {len(all_results)}개 상품")
    return all_results


def crawl_single_tab_with_ranking(driver, city_name, tab_name, target_count, continent, country, start_rank):
    """
    🎯 단일 탭에서 랭킹 순서 보장 페이지네이션 크롤링
    
    핵심:
    - 페이지당 15개 URL 수집
    - 화면 순서대로 크롤링 (랭킹 보장)
    - 10개마다 CSV 저장
    - 상세→목록 반복
    """
    print(f"📋 '{tab_name}' 탭 상세 크롤링 시작")
    
    tab_results = []
    current_page = 1
    current_rank = start_rank
    
    while len(tab_results) < target_count:
        print(f"  📄 페이지 {current_page} 처리 중...")
        
        # Step 1: 현재 페이지 URL 수집 (15개)
        page_urls = collect_basic_urls_from_current_view(driver)
        if not page_urls:
            print(f"  ⚠️ 페이지 {current_page}에서 URL 없음, 중단")
            break
        
        print(f"  ✅ {len(page_urls)}개 URL 수집 (KLOOK 페이지당 15개 기준)")
        
        # Step 2: URL들을 화면 순서대로 크롤링 (랭킹 보장)
        for url_index, product_url in enumerate(page_urls):
            if len(tab_results) >= target_count:
                print(f"  🎯 목표 {target_count}개 달성!")
                break
            
            print(f"    📦 [{current_rank}위] 상품 크롤링 ({current_page}페이지 {url_index+1}번째)")
            
            # Step 3: 상세페이지 크롤링
            result = crawl_single_product_with_stop_check(
                driver, product_url, current_rank, city_name, 
                continent, country, current_page
            )
            
            if result:
                # 메타데이터 추가
                result['탭명'] = tab_name
                result['탭내_랭킹'] = len(tab_results) + 1
                result['전체_랭킹'] = current_rank
                result['페이지'] = current_page
                
                tab_results.append(result)
                print(f"    ✅ 완료: {result.get('상품명', 'Unknown')[:25]}...")
                
                # Step 4: 10개마다 중간 저장
                if len(tab_results) % 10 == 0:
                    save_batch_data(tab_results[-10:], f"{city_name}_{tab_name}")
                    print(f"    💾 중간 저장: {len(tab_results)}개")
            
            current_rank += 1
            time.sleep(2)  # 요청 간격
        
        # Step 5: 다음 페이지 이동
        if len(tab_results) < target_count:
            print(f"  🔄 다음 페이지로 이동...")
            next_result = click_next_page_enhanced(driver, current_page)
            
            if not next_result[0]:  # 다음 페이지 없음
                print(f"  ⚠️ 다음 페이지 없음: {next_result[1]}")
                break
            
            current_page += 1
            time.sleep(3)  # 페이지 로딩 대기
    
    # 최종 저장 (나머지)
    remaining = len(tab_results) % 10
    if remaining > 0:
        save_batch_data(tab_results[-remaining:], f"{city_name}_{tab_name}")
        print(f"  💾 최종 저장: {remaining}개")
    
    return tab_results


# =============================================================================
# 🎯 Group 12에서 사용할 통합 함수
# =============================================================================

def execute_unified_klook_crawling_workflow(city_name, driver, total_target=250):
    """
    Group 12 위젯에서 호출할 통합 워크플로우
    
    Args:
        city_name (str): 도시명
        driver: 웹드라이버
        total_target (int): 전체 목표 상품 수 (기본 250개 = 탭당 50개씩)
    
    Returns:
        dict: 실행 결과
    """
    print(f"🚀 통합 KLOOK 크롤링 워크플로우 시작: {city_name}")
    print(f"🎯 목표: {total_target}개 상품 (탭당 {total_target//5}개씩)")
    
    try:
        # 1. 브라우저 초기화는 이미 완료된 상태
        
        # 2. 메인페이지 → 검색 → 결과페이지 (이미 완료된 상태)
        
        # 3. 탭별 순차 크롤링 실행
        all_results = execute_tab_based_sequential_crawling(
            city_name, driver, target_target//5
        )
        
        # 4. 결과 반환
        return {
            "success": True,
            "total_crawled": len(all_results),
            "results": all_results,
            "execution_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ 통합 워크플로우 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_crawled": 0,
            "results": []
        }


# =============================================================================
# 🎯 기존 함수들과의 매핑 (FUNCTION_REFERENCE.md 기준)
# =============================================================================

FUNCTION_MAPPING = {
    # 우리 시나리오 -> 기존 함수명
    "브라우저_초기화": "setup_driver",
    "메인페이지_이동": "go_to_main_page", 
    "검색어_입력": "find_and_fill_search",
    "검색_버튼_클릭": "click_search_button",
    "팝업_처리": "handle_popup",
    "탭_감지": "detect_tabs_with_enhanced_fallback",
    "탭_클릭": "click_tab_enhanced",
    "URL_수집": "collect_basic_urls_from_current_view",
    "상품_크롤링": "crawl_single_product_with_stop_check",
    "다음페이지_클릭": "click_next_page_enhanced", 
    "데이터_저장": "save_batch_data",
    "정지_체크": "check_stop_flag",
    "도시_정보": "get_city_info"
}

print("✅ 시나리오 매핑 완료!")
print("🔧 기존 함수들을 활용한 완벽한 워크플로우 설계")
print("💡 Group 12에서 execute_unified_klook_crawling_workflow() 호출하면 됩니다!")