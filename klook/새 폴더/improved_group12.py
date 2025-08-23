# =============================================================================
# 🎯 그룹 12: 개선된 KLOOK 크롤링 위젯 (기존 함수 활용)
# =============================================================================

import ipywidgets as widgets
from IPython.display import display, clear_output

def create_improved_klook_crawler_widget():
    """개선된 KLOOK 크롤링 위젯 생성"""

    # 위젯 컴포넌트들
    city_input = widgets.Text(
        value='서울',
        placeholder='도시명을 입력하세요 (예: 서울, 부산, 제주)',
        description='🌍 도시:',
        style={'description_width': 'initial'}
    )

    products_input = widgets.IntSlider(
        value=50,
        min=10,
        max=200,
        step=10,
        description='🎯 탭당 상품 수:',
        style={'description_width': 'initial'}
    )

    start_button = widgets.Button(
        description='🚀 크롤링 시작',
        button_style='success',
        layout=widgets.Layout(width='200px')
    )

    stop_button = widgets.Button(
        description='🛑 정지',
        button_style='danger',
        layout=widgets.Layout(width='100px'),
        disabled=True
    )

    output = widgets.Output()

    def safe_function_call(func_name, *args, **kwargs):
        """안전한 함수 호출"""
        try:
            func = globals().get(func_name)
            if callable(func):
                return func(*args, **kwargs)
            else:
                with output:
                    print(f"⚠️ 함수 '{func_name}'를 찾을 수 없습니다")
                return None
        except Exception as e:
            with output:
                print(f"❌ 함수 '{func_name}' 실행 오류: {e}")
            return None

    def execute_simple_tab_crawling(city, target_per_tab, driver):
        """간단한 탭별 크롤링 실행"""
        with output:
            print(f"🎯 {city} 탭별 크롤링 시작 (탭당 {target_per_tab}개)")
            print("=" * 50)
            
            # 탭 순서 정의
            tabs = ["전체", "투어&액티비티", "티켓&입장권", "교통", "기타"]
            
            # 도시 정보
            continent, country = safe_function_call('get_city_info', city) or ("아시아", "대한민국")
            
            # 탭 감지
            print("🔍 탭 감지 중...")
            detected_tabs = safe_function_call('detect_tabs_with_enhanced_fallback', driver)
            if not detected_tabs:
                print("❌ 탭 감지 실패")
                return
            
            total_results = []
            product_number = 1
            
            # 각 탭별 처리
            for tab_index, tab_name in enumerate(tabs):
                if safe_function_call('check_stop_flag'):
                    print("🛑 정지 신호 감지 - 중단")
                    break
                    
                print(f"\n🔄 [{tab_index+1}/5] '{tab_name}' 탭 처리 중...")
                
                # 탭 클릭
                if not safe_function_call('click_tab_enhanced', driver, tab_name, detected_tabs):
                    print(f"❌ '{tab_name}' 탭 클릭 실패")
                    continue
                
                # 해당 탭 크롤링
                tab_results = crawl_current_tab(driver, city, tab_name, target_per_tab, 
                                              continent, country, product_number)
                
                total_results.extend(tab_results)
                product_number += len(tab_results)
                
                print(f"✅ '{tab_name}' 탭 완료: {len(tab_results)}개")
            
            print(f"\n🎉 전체 크롤링 완료! 총 {len(total_results)}개 상품")

    def crawl_current_tab(driver, city, tab_name, target_count, continent, country, start_number):
        """현재 탭에서 크롤링"""
        tab_results = []
        current_page = 1
        current_number = start_number
        
        while len(tab_results) < target_count:
            if safe_function_call('check_stop_flag'):
                print("🛑 정지 신호 감지")
                break
                
            print(f"  📄 페이지 {current_page} 처리...")
            
            # 현재 페이지 URL 수집
            page_urls = safe_function_call('collect_basic_urls_from_current_view', driver)
            if not page_urls:
                print(f"  ⚠️ URL 없음, 다음 페이지로...")
                break
            
            print(f"  ✅ {len(page_urls)}개 URL 수집")
            
            # 각 URL 크롤링
            for url in page_urls:
                if len(tab_results) >= target_count:
                    break
                    
                print(f"    📦 [{current_number}] 상품 크롤링...")
                
                result = safe_function_call('crawl_single_product_with_stop_check',
                                          driver, url, current_number, city, 
                                          continent, country, current_page)
                
                if result:
                    result['탭명'] = tab_name
                    tab_results.append(result)
                    print(f"    ✅ 완료: {result.get('상품명', 'Unknown')[:20]}...")
                    
                    # 10개마다 저장
                    if len(tab_results) % 10 == 0:
                        safe_function_call('save_batch_data', tab_results[-10:], f"{city}_{tab_name}")
                        print(f"    💾 중간저장: {len(tab_results)}개")
                
                current_number += 1
                time.sleep(2)
            
            # 다음 페이지
            if len(tab_results) < target_count:
                next_result = safe_function_call('click_next_page_enhanced', driver, current_page)
                if not next_result or not next_result[0]:
                    print("  ⚠️ 마지막 페이지")
                    break
                current_page += 1
                time.sleep(3)
        
        # 나머지 저장
        remaining = len(tab_results) % 10
        if remaining > 0:
            safe_function_call('save_batch_data', tab_results[-remaining:], f"{city}_{tab_name}")
        
        return tab_results

    def on_start_click(b):
        """시작 버튼 클릭"""
        city = city_input.value.strip()
        target_per_tab = products_input.value
        
        if not city:
            with output:
                print("❌ 도시명을 입력해주세요!")
                return

        # UI 상태 변경
        start_button.disabled = True
        stop_button.disabled = False
        
        with output:
            clear_output(wait=True)

        try:
            # 브라우저 초기화
            print("🔧 브라우저 초기화...")
            driver = safe_function_call('setup_driver')
            if not driver:
                print("❌ 브라우저 초기화 실패")
                return

            # 검색 과정
            print("🔍 KLOOK 검색...")
            safe_function_call('go_to_main_page', driver)
            safe_function_call('find_and_fill_search', driver, city)
            safe_function_call('click_search_button', driver)
            safe_function_call('handle_popup', driver)
            safe_function_call('smart_wait_for_page_load', driver)
            
            # 정지 플래그 초기화
            safe_function_call('reset_stop_flag')
            
            # 탭별 크롤링 실행
            execute_simple_tab_crawling(city, target_per_tab, driver)
            
        finally:
            if 'driver' in locals() and driver:
                try:
                    driver.quit()
                    print("🔚 브라우저 정리 완료")
                except:
                    pass
            
            start_button.disabled = False
            stop_button.disabled = True

    def on_stop_click(b):
        """정지 버튼 클릭"""
        safe_function_call('set_stop_flag')
        with output:
            print("🛑 정지 신호 전송...")
        stop_button.disabled = True

    # 이벤트 바인딩
    start_button.on_click(on_start_click)
    stop_button.on_click(on_stop_click)

    # 위젯 레이아웃
    widget_box = widgets.VBox([
        widgets.HTML("<h2>🎯 개선된 KLOOK 크롤링 시스템</h2>"),
        widgets.HTML("<p>✅ 기존 함수 활용 + 탭별 순차 크롤링</p>"),
        widgets.HTML("<hr>"),
        city_input,
        products_input,
        widgets.HBox([start_button, stop_button]),
        output
    ])

    return widget_box

def run_improved_klook_crawler():
    """개선된 KLOOK 크롤러 실행"""
    widget = create_improved_klook_crawler_widget()
    display(widget)
    return widget

print("✅ 개선된 Group 12 완성!")
print("🔧 기존 함수들 직접 활용")
print("⚡ 간단하고 가벼운 구조")
print("💡 사용법: run_improved_klook_crawler()")