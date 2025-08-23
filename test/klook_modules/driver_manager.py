"""
🚀 그룹 6: 드라이버 초기화 및 기본 설정
- 드라이버 시작, 이미지 폴더 설정, 기본 환경 구축
- 브라우저 제어, 페이지 네비게이션, 자연스러운 스크롤 패턴
"""

import os
import random
import time
import platform

# 조건부 import (라이브러리가 없어도 모듈은 로드되도록)
try:
    import chromedriver_autoinstaller
    import undetected_chromedriver as uc
    from user_agents import parse
    WEBDRIVER_AVAILABLE = True
except ImportError:
    print("⚠️ 웹드라이버 라이브러리가 없습니다. setup_driver는 사용할 수 없습니다.")
    WEBDRIVER_AVAILABLE = False
    uc = None
    parse = None

# config 모듈에서 필요한 함수들 import
from .config import CONFIG

# =============================================================================
# 🚀 드라이버 설정 및 초기화 함수
# =============================================================================

def make_user_agent(ua, is_mobile):
    """User Agent 생성 함수"""
    if not WEBDRIVER_AVAILABLE or not parse:
        return {}
        
    user_agent = parse(ua)
    model = user_agent.device.model
    platform = user_agent.os.family
    platform_version = user_agent.os.version_string + ".0.0"
    version = user_agent.browser.version[0]
    ua_full_version = user_agent.browser.version_string
    architecture = "x86"
    
    if is_mobile:
        platform_info = "Linux armv8l"
        architecture= ""
    else:
        platform_info = "Win32"
        model = ""
        
    RET_USER_AGENT = {
        "appVersion" : ua.replace("Mozilla/", ""),
        "userAgent": ua,
        "platform" : f"{platform_info}",
        "acceptLanguage" : "ko-KR, kr, en-US, en",
        "userAgentMetadata":{
            "brands" : [
                {"brand":"Google Chrome", "version":f"{version}"},
                {"brand":"Chromium", "version":f"{version}"},
                {"brand":" Not A;Brand", "version":"99"}
            ],
            "fullVersionList" : [
                {"brand":"Google Chrome", "version":f"{version}"},
                {"brand":"Chromium", "version":f"{version}"},
                {"brand":" Not A;Brand", "version":"99"}
            ],
            "fullVersion":f"{ua_full_version}",
            "platform" :platform,
            "platformVersion":platform_version,
            "architecture":architecture,
            "model" : model,
            "mobile":is_mobile
        }
    }
    return RET_USER_AGENT

def generate_random_geolocation():
    """랜덤 지리적 위치 생성"""
    ltop_lat = 37.75415601640249
    ltop_long = 126.86767642302573
    rbottom_lat = 37.593829172663945
    rbottom_long = 127.15276051439332

    targetLat = random.uniform(rbottom_lat, ltop_lat)
    targetLong = random.uniform(ltop_long,rbottom_long)
    return {"latitude":targetLat, "longitude" : targetLong, "accuracy":100}

def setup_driver():
    """크롬 드라이버 설정 및 실행 (호환성 개선 버전)"""
    if not WEBDRIVER_AVAILABLE:
        raise RuntimeError("웹드라이버 라이브러리가 설치되지 않았습니다. pip install setuptools undetected-chromedriver를 실행하세요.")
    
    chromedriver_autoinstaller.install()
    
    options = uc.ChromeOptions()
    
    UA = CONFIG["USER_AGENT"]
    options.add_argument(f"--user-agent={UA}")
    
    rand_user_folder = random.randrange(1,100)
    raw_path = os.path.abspath("cookies")
    os.makedirs(raw_path, exist_ok=True)
    user_cookie_name = f"{raw_path}/{rand_user_folder}"
    if not os.path.exists(user_cookie_name):
        os.makedirs(user_cookie_name, exist_ok=True)
    
    # 호환성 문제를 해결한 안전한 옵션들만 사용
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-extensions')
    
    try:
        driver = uc.Chrome(user_data_dir=user_cookie_name, options=options)
        print("✅ 크롬 드라이버 실행 성공!")
    except Exception as e:
        print(f"❌ 드라이버 초기화 실패: {type(e).__name__}: {str(e)}")
        print("💡 Chrome 브라우저를 최신 버전으로 업데이트하거나 재부팅을 시도해보세요.")
        raise RuntimeError(f"드라이버 초기화 실패: {e}")
    
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # User Agent 설정
    UA_Data = make_user_agent(UA, False)
    if UA_Data:
        driver.execute_cdp_cmd("Network.setUserAgentOverride", UA_Data)
        
        # 지리적 위치 설정
        GEO_DATA = generate_random_geolocation()
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", GEO_DATA)
        driver.execute_cdp_cmd("Emulation.setUserAgentOverride", UA_Data)
        driver.execute_cdp_cmd("Emulation.setNavigatorOverrides", {"platform":"Linux armv8l"})
    
    # 브라우저 창 크기 설정 (자연스러운 크기로)
    driver.set_window_size(1366, 768)
    
    return driver

def go_to_main_page(driver):
    """KLOOK 메인 페이지로 이동"""
    driver.get("https://www.klook.com/ko/search/result/?query=%EC%84%9C%EC%9A%B8")
    time.sleep(random.uniform(CONFIG["MEDIUM_MIN_DELAY"], CONFIG["MEDIUM_MAX_DELAY"]))
    return True

def find_and_fill_search(driver, city_name):
    """검색창 찾기 및 인간적인 타이핑 적용"""
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
        (By.CSS_SELECTOR, "#js-header-search-box input"),
        (By.CSS_SELECTOR, "input[name='klkHeadSearch']"),
        (By.CSS_SELECTOR, ".search-box_input"),
        (By.XPATH, "//input[@placeholder='어디로 놀러 가세요?']"),
    ]

    search_input = None
    for selector_type, selector_value in search_selectors:
        try:
            search_input = WebDriverWait(driver, CONFIG["WAIT_TIMEOUT"]).until(
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
            time.sleep(random.uniform(CONFIG["SHORT_MIN_DELAY"], CONFIG["SHORT_MAX_DELAY"]))
        print(f"  ✅ '{city_name}' 입력 완료!")
        return True
    else:
        print(f"  ❌ 검색창을 찾을 수 없습니다!")
        return False

def click_search_button(driver):
    """검색 버튼 클릭"""
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
        (By.CSS_SELECTOR, "#js-header-search-box button"),
        (By.CSS_SELECTOR, "#js-header-search-box > button"),
        (By.XPATH, "//div[@id='js-header-search-box']//button"),
    ]
    search_clicked = False
    for selector_type, selector_value in search_button_selectors:
        try:
            search_button = WebDriverWait(driver, CONFIG["WAIT_TIMEOUT"]).until(
                EC.element_to_be_clickable((selector_type, selector_value))
            )
            search_button.click()
            print(f"  ✅ 검색 버튼 클릭 성공!")
            search_clicked = True
            time.sleep(random.uniform(CONFIG["MEDIUM_MIN_DELAY"], CONFIG["MEDIUM_MAX_DELAY"]))
            break
        except TimeoutException:
            continue

    return search_clicked

def handle_popup(driver):
    """팝업 처리"""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
    except ImportError:
        print("❌ Selenium이 설치되지 않았습니다.")
        return False
    
    popup_selectors = [
        (By.CSS_SELECTOR, ".popup-close"),
        (By.CSS_SELECTOR, ".modal-close"),
        (By.XPATH, "//button[contains(@aria-label, '닫기')]"),
        (By.XPATH, "//button[contains(text(), '닫기')]"),
    ]

    popup_closed = False
    for selector_type, selector_value in popup_selectors:
        try:
            popup_button = WebDriverWait(driver, CONFIG["POPUP_WAIT"]).until(
                EC.element_to_be_clickable((selector_type, selector_value))
            )
            popup_button.click()
            print(f"  ✅ 팝업창을 닫았습니다.")
            popup_closed = True
            time.sleep(random.uniform(1, 3))
            break
        except TimeoutException:
            continue

    if not popup_closed:
        print(f"  ℹ️ 팝업이 없거나 이미 닫혀 있습니다.")
    return popup_closed

def initialize_group6_system():
    """그룹 6: 드라이버 초기화 및 기본 설정 실행"""
    print("🚀 KLOOK 크롤링 시스템 시작!")
    print("=" * 80)

    # 결과 저장소 초기화
    all_results = []
    print("🔄 결과 저장소 초기화 완료")

    # 드라이버 초기화
    driver = None
    
    # 1단계: 기존 드라이버 확인
    try:
        if 'driver' in globals() and globals().get('driver'):
            existing_driver = globals()['driver']
            existing_driver.execute_script("return document.readyState;")
            print("✅ 기존 드라이버 재사용")
            driver = existing_driver
    except Exception:
        pass
    
    # 2단계: 새 드라이버 생성
    if not driver:
        print("🆕 새로운 드라이버 생성 중...")
        try:
            driver = setup_driver()
            print("✅ 드라이버 생성 완료!")
        except Exception as e:
            print(f"❌ 드라이버 생성 실패: {e}")
            raise RuntimeError(f"드라이버 생성 완전 실패: {e}")

    # 드라이버 확인
    if not driver:
        raise RuntimeError("드라이버가 None입니다 - 초기화 실패")

    # 이미지 폴더 설정
    if CONFIG["SAVE_IMAGES"]:
        img_folder_path = os.path.join(os.path.abspath(""), "klook_thumb_img")
        os.makedirs(img_folder_path, exist_ok=True)
        print(f"📁 이미지 폴더 확인 완료: {img_folder_path}")

    return driver, all_results

print("✅ 그룹 6 완료: 드라이버 초기화 및 기본 설정 함수들 정의 완료!")
print("   🔧 핵심 함수: setup_driver(), initialize_group6_system()")
print("   🌐 네비게이션: go_to_main_page(), find_and_fill_search(), click_search_button()")