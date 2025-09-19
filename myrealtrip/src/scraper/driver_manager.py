"""
브라우저 드라이버 관리 시스템
- 드라이버 초기화 및 설정
- 브라우저 제어 및 페이지 네비게이션
- 자연스러운 사용자 행동 시뮬레이션
"""

import time
import random

# Selenium 및 관련 라이브러리 import
try:
    import undetected_chromedriver as uc
    import chromedriver_autoinstaller
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium.webdriver.common.keys import Keys
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# 내부 모듈 import
from . import human_scroll_patterns

# 임시 CONFIG (나중에 src.config에서 가져오도록 수정)
CONFIG = {
    "WAIT_TIMEOUT": 10,
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
}

def setup_driver():
    """Undetected-Chromedriver를 설정하고 시작합니다."""
    if not SELENIUM_AVAILABLE:
        raise ImportError("Selenium/Undetected-Chromedriver가 설치되지 않았습니다.")
    
    print("🚀 Chrome 드라이버 설정 중...")
    try:
        chromedriver_autoinstaller.install()
        options = uc.ChromeOptions()
        options.add_argument(f"--user-agent={CONFIG['USER_AGENT']}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(60)
        print("✅ 드라이버 초기화 완료")
        return driver
    except Exception as e:
        print(f"❌ 드라이버 초기화 실패: {e}")
        raise

def go_to_main_page(driver):
    """마이리얼트립 메인 페이지로 이동합니다."""
    print("🌍 마이리얼트립 메인 페이지로 이동합니다...")
    driver.get("https://www.myrealtrip.com/")
    time.sleep(random.uniform(2, 4))
    return True

def find_and_fill_search(driver, city_name):
    """검색창을 찾아 도시명을 입력합니다."""
    print(f"  🔍 '{city_name}' 검색 중...")
    try:
        search_input = WebDriverWait(driver, CONFIG["WAIT_TIMEOUT"]).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-cy='SearchInput-input']"))
        )
        search_input.clear()
        for char in city_name:
            search_input.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        search_input.send_keys(Keys.ENTER)
        print(f"  ✅ '{city_name}' 입력 및 검색 완료!")
        return True
    except TimeoutException:
        print("  ❌ 검색창을 찾을 수 없습니다!")
        return False

def smart_scroll_selector(driver, scroll_type="random"):
    """인간 행동 기반 스크롤 패턴을 실행합니다."""
    print("   - 🤖 인간 행동 기반 스크롤 시작...")
    try:
        human_scroll_patterns.simulate_human_scroll(driver, scroll_type)
    except Exception as e:
        print(f"   - ⚠️ 스크롤 패턴 실행 중 오류 발생:{e}")

print("✅ driver_manager.py 리팩토링 완료: 지능형 스크롤 시스템 탑재 완료!")
