"""
브라우저 드라이버 관리 시스템
- 드라이버 초기화 및 설정
- 브라우저 제어 및 페이지 네비게이션
- 자연스러운 사용자 행동 시뮬레이션
"""

import os
import random
import time
import platform

from ..config import CONFIG, WEBDRIVER_AVAILABLE

# 조건부 import
if WEBDRIVER_AVAILABLE:
    import chromedriver_autoinstaller
    import undetected_chromedriver as uc
    from user_agents import parse
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
else:
    uc = None
    parse = None

# =============================================================================
# 드라이버 설정 및 초기화
# =============================================================================

def make_user_agent(ua, is_mobile):
    """User Agent 생성 함수"""
    if not WEBDRIVER_AVAILABLE or not parse:
        return {}
        
    user_agent = parse(ua)
    model = user_agent.device.model
    platform_name = user_agent.os.family
    platform_version = user_agent.os.version_string + ".0.0"
    version = user_agent.browser.version[0]
    ua_full_version = user_agent.browser.version_string
    architecture = "x86"
    
    if is_mobile:
        platform_info = "Linux armv8l"
        architecture = ""
    else:
        platform_info = "Win32"
        model = ""
    
    sec_ch_ua = f'"Chromium";v="{version}", "Google Chrome";v="{version}", "Not=A?Brand";v="24"'
    
    return {
        "userAgent": ua,
        "platform": platform_info,
        "acceptLanguage": "ko-KR,ko;q=0.9,en;q=0.8",
        "sec-ch-ua": sec_ch_ua,
        "sec-ch-ua-mobile": "?1" if is_mobile else "?0",
        "sec-ch-ua-platform": f'"{platform_name}"',
        "sec-ch-ua-platform-version": f'"{platform_version}"',
        "sec-ch-ua-arch": f'"{architecture}"',
        "sec-ch-ua-model": f'"{model}"' if model else "",
        "sec-ch-ua-full-version": f'"{ua_full_version}"'
    }

def setup_driver():
    """드라이버 설정 및 시작"""
    if not WEBDRIVER_AVAILABLE:
        raise Exception("웹드라이버 라이브러리가 설치되지 않았습니다.")
    
    print("🚀 Chrome 드라이버 설정 중...")
    
    try:
        # ChromeDriver 자동 설치
        chromedriver_autoinstaller.install()
        
        # Chrome 옵션 설정
        options = uc.ChromeOptions()
        
        # 기본 안정성 옵션들
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--window-size=1920,1080")
        
        # 동적 User-Agent 설정
        from ..config import get_random_user_agent
        user_agent = get_random_user_agent()
        options.add_argument(f"--user-agent={user_agent}")
        print(f"   🎭 User-Agent: {user_agent[:50]}...")
        
        # 보안 및 제약 해제
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-gpu-sandbox")
        
        # 봇 탐지 회피 (검증된 안전한 옵션)
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 브라우저 동작 설정
        prefs = {
            "profile.default_content_setting_values": {
                "images": 1,  # 이미지 허용 (크롤링에 필수)
                "plugins": 2,  # 플러그인 차단
                "popups": 2,   # 팝업 차단
                "geolocation": 2,  # 위치 정보 차단
                "notifications": 2,  # 알림 차단
                "media_stream": 2,  # 미디어 스트림 차단
            },
            "profile.managed_default_content_settings": {
                "images": 1  # 이미지 허용으로 통일
            }
        }
        options.add_experimental_option("prefs", prefs)
        
        # 드라이버 생성
        driver = uc.Chrome(options=options)
        
        # 페이지 로드 타임아웃 설정 (더 긴 시간)
        driver.set_page_load_timeout(60)  # 60초로 증가
        
        # 스크립트 타임아웃 설정
        driver.set_script_timeout(30)  # 30초로 증가
        
        print("✅ 드라이버 초기화 완료")
        return driver
        
    except Exception as e:
        print(f"❌ 드라이버 초기화 실패: {e}")
        raise

def go_to_main_page(driver):
    """KKday 메인 페이지로 이동 및 기본 처리"""
    print("KKday 메인 페이지로 이동합니다...")
    driver.get("https://www.kkday.com/ko/product/productlist/%EC%84%9C%EC%9A%B8")
    time.sleep(random.uniform(2, 4)) # 페이지 로드를 위한 최소 대기

    # [수정됨] 팝업 처리를 먼저 실행합니다.
    handle_popup(driver)

    # [수정됨] 팝업 처리가 끝난 후 스크롤을 실행합니다.
    print("페이지 로드 후 자연스러운 스크롤을 실행합니다.")
    smart_scroll_selector(driver)

    return True

def find_and_fill_search(driver, city_name):
    """검색창 찾기 및 인간적인 타이핑 적용 (원본 코드)"""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
    except ImportError:
        print("❌ Selenium이 설치되지 않았습니다.")
        return False
    
    print(f"  🔍 '{city_name}' 검색창 찾는 중...")
    search_selectors = [
        (By.CSS_SELECTOR, "#search_experience_value"),
        (By.CSS_SELECTOR, "input.form-control[placeholder*='가고 싶은 곳']"),
        (By.CSS_SELECTOR, "input[placeholder*='검색해보세요']"),
        (By.XPATH, "//input[@placeholder='가고 싶은 곳, 하고 싶은 것을 검색해보세요.']"),
    ]
    

    search_input = None
    for selector_type, selector_value in search_selectors:
        try:
            search_input = WebDriverWait(driver, CONFIG.get("WAIT_TIMEOUT", 10)).until(
                EC.presence_of_element_located((selector_type, selector_value))
            )
            print(f"  ✅ 검색창을 찾았습니다!")
            break
        except TimeoutException:
            continue

    if search_input:
        search_input.clear()
        # 인간적인 타이핑 시뮬레이션
        for char in city_name:
            search_input.send_keys(char)
            time.sleep(random.uniform(CONFIG.get("SHORT_MIN_DELAY", 0.1), CONFIG.get("SHORT_MAX_DELAY", 0.3)))
        print(f"  ✅ '{city_name}' 입력 완료!")
        return True
    else:
        print(f"  ❌ 검색창을 찾을 수 없습니다!")
        return False

def click_search_button(driver):
    """검색 버튼 클릭 (원본 코드)"""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
    except ImportError:
        print("❌ Selenium이 설치되지 않았습니다.")
        return False
    
    print(f"  🔎 검색 버튼 찾는 중...")
    search_button_selectors = [
        (By.CSS_SELECTOR, "#headerApp > div.container > div > div.header-search > div > div.kksearch-exp > div > div.input-group > span.input-group-btn > button"),
        (By.CSS_SELECTOR, "button.btn.btn-primary"),
        (By.CSS_SELECTOR, ".input-group-btn button"),
        (By.XPATH, "//button[contains(@class, 'btn-primary')]"),
    ]
 
    search_clicked = False
    for selector_type, selector_value in search_button_selectors:
        try:
            search_button = WebDriverWait(driver, CONFIG.get("WAIT_TIMEOUT", 10)).until(
                EC.element_to_be_clickable((selector_type, selector_value))
            )
            # KKday는 두 번 클릭 필요
            search_button.click()
            time.sleep(2) 
            search_button.click()

            print(f"  ✅ 검색 버튼 클릭 성공!")    

            search_clicked = True
            time.sleep(random.uniform(CONFIG.get("MEDIUM_MIN_DELAY", 2), CONFIG.get("MEDIUM_MAX_DELAY", 4)))
            break
        except TimeoutException:
            continue

    return search_clicked

def handle_kkday_cookie_popup(driver):
    """KKday 쿠키 팝업 자동 처리"""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        import time
        
        print("🍪 쿠키 팝업 확인 중...")
        
        # 우선순위 순서로 정렬된 셀렉터
        cookie_selectors = [
            (By.CSS_SELECTOR, "#c-right > a"),                   # 가장 확실함
            (By.XPATH, "/html/body/div[1]/div[2]/a"),            # Full XPath
            (By.XPATH, "//a[contains(@onclick, 'submitConsent')]"),  # onclick 이벤트
            (By.CSS_SELECTOR, ".c-button"),                      # 클래스 기반
            (By.CSS_SELECTOR, "#c-right a"),                     # 약간 덜 구체적
            (By.XPATH, "//a[text()='OK']"),                      # 텍스트 "OK"
            (By.XPATH, "//a[contains(@class, 'c-button')]"),     # 클래스 포함
            (By.XPATH, "//div[@id='cookiebanner']//a"),          # 쿠키배너 내 모든 링크
            (By.XPATH, "//div[contains(@id, 'cookie')]//a"),     # cookie 포함 ID의 링크
        ]
        
        for selector_type, selector_value in cookie_selectors:
            try:
                cookie_button = WebDriverWait(driver, 4).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                cookie_button.click()
                print("✅ 쿠키 동의 완료!")
                time.sleep(1)
                return True
            except TimeoutException:
                continue
                
        print("ℹ️ 쿠키 팝업 없음 - 계속 진행")
        return False
        
    except Exception as e:
        print(f"⚠️ 쿠키 처리 중 오류: {e}")
        return False

def handle_popup(driver):
    """팝업 처리 (쿠키 팝업 포함)"""
    print("🔔 팝업 확인 중...")      
    time.sleep(3)  # 3초 대기

    # 먼저 쿠키 팝업 처리
    try:                                                        
        handle_kkday_cookie_popup(driver)
    except Exception as e:
        print(f"⚠️ 쿠키 팝업 처리 중 오류: {e}")

    popup_selectors = [
        ".modal-close",
        ".popup-close",
        ".close-button",
        "button:contains('닫기')",
        "button:contains('Close')",
        ".btn-close",
        "[data-dismiss='modal']"
    ]
    
    try:
        for selector in popup_selectors:
            try:
                popup_element = driver.find_element(By.CSS_SELECTOR, selector)
                if popup_element.is_displayed():
                    popup_element.click()
                    time.sleep(1)
                    print("✅ 팝업 닫기 완료")
                    return True
            except:
                continue
        
        print("ℹ️ 팝업 없음")
        return True
        
    except Exception as e:
        print(f"⚠️ 팝업 처리 중 오류: {e}")
        return False

# =============================================================================
# 자연스러운 사용자 행동 시뮬레이션
# =============================================================================
def smart_scroll_selector(driver):
    """스마트 스크롤 선택기 - 두 함수 중 랜덤 선택"""
    scroll_functions = [
        ("기본", human_like_scroll_patterns),
        ("향상", enhanced_scroll_patterns)
    ]
    _, selected_function = random.choice(scroll_functions)
    print(f"   - 스크롤 패턴: '{selected_function.__name__}' 실행")
    selected_function(driver)

def human_like_scroll_patterns(driver):
    """기본 스크롤 패턴 (3가지)"""
    patterns = ["smooth_reading", "comparison_scroll", "quick_scan"]
    selected = random.choice(patterns)

    try:
        if selected == "smooth_reading":
            for i in range(random.randint(3, 5)):
                scroll_amount = random.randint(250, 500)
                driver.execute_script(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.8, 2.0))

        elif selected == "comparison_scroll":
            for i in range(random.randint(2, 3)):
                driver.execute_script(f"window.scrollBy({{top: {random.randint(400, 700)}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.8, 1.5))
                driver.execute_script(f"window.scrollBy({{top: -{random.randint(100, 300)}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.8, 1.5))

        elif selected == "quick_scan":
            for i in range(random.randint(4, 7)):
                driver.execute_script(f"window.scrollBy({{top: {random.randint(300, 600)}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.3, 1.0))
    except Exception as e:
        print(f"  스크롤 오류 (human_like): {e}")

def enhanced_scroll_patterns(driver):
    """향상된 스크롤 패턴 (5가지)"""
    patterns = [
        "natural_reading", "search_and_compare", "rapid_overview",
        "detailed_inspection", "hesitant_browsing"
    ]
    selected = random.choice(patterns)

    try:
        if selected == "natural_reading":
            for _ in range(random.randint(4, 6)):
                driver.execute_script(f"window.scrollBy({{top: {random.randint(200, 400)}, behavior: 'smooth'}});")
                time.sleep(random.uniform(1.5, 3.0))
                if random.random() < 0.25:
                    driver.execute_script(f"window.scrollBy({{top: -{random.randint(50, 150)}, behavior: 'smooth'}});")
                    time.sleep(random.uniform(0.5, 1.0))

        elif selected == "search_and_compare":
            for _ in range(random.randint(3, 5)):
                driver.execute_script(f"window.scrollBy({{top: {random.randint(500, 800)}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.8, 1.5))
                if random.random() < 0.5:
                    driver.execute_script(f"window.scrollBy({{top: -{random.randint(200, 400)}, behavior: 'smooth'}});")
                    time.sleep(random.uniform(2.0, 3.5))

        elif selected == "rapid_overview":
            for _ in range(random.randint(6, 9)):
                driver.execute_script(f"window.scrollBy({{top: {random.randint(400, 700)}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.3, 0.8))

        elif selected == "detailed_inspection":
            for _ in range(random.randint(3, 4)):
                driver.execute_script(f"window.scrollBy({{top: {random.randint(150, 300)}, behavior: 'smooth'}});")
                time.sleep(random.uniform(3.0, 5.0))

        elif selected == "hesitant_browsing":
            for _ in range(random.randint(4, 7)):
                driver.execute_script(f"window.scrollBy({{top: {random.randint(200, 400)}, behavior: 'smooth'}});")
                time.sleep(random.uniform(1.0, 2.0))
                if random.random() < 0.5:
                    driver.execute_script(f"window.scrollBy({{top: -{random.randint(100, 200)}, behavior: 'smooth'}});")
                    time.sleep(random.uniform(0.8, 1.5))
    except Exception as e:
        print(f"  스크롤 오류 (enhanced): {e}")

def random_delay(min_seconds=1, max_seconds=3):
    """무작위 대기"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def initialize_group6_system(city_name="서울"):
    """그룹6 시스템 초기화 (기존 코드 호환성)"""
    print("🚀 그룹6 드라이버 시스템 초기화...")
    
    try:
        driver = setup_driver()
        
        if go_to_main_page(driver):
            handle_popup(driver)
            
            if find_and_fill_search(driver, city_name):
                if click_search_button(driver):
                    print("✅ 그룹6 시스템 초기화 완료")
                    return driver
        
        # driver.quit() - 제거됨: 브라우저 열어두기
        return None
        
    except Exception as e:
        print(f"❌ 그룹6 시스템 초기화 실패: {e}")
        return None

print("✅ driver_manager.py 로드 완료: 드라이버 관리 시스템 준비!")