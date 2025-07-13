# myrealtrip_functions.py
# 마이리얼트립 크롤링 - 모든 함수 및 설정

import pandas as pd
import warnings, os, time, shutil, urllib, random
warnings.filterwarnings(action='ignore')

from PIL import Image
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

import chromedriver_autoinstaller
import undetected_chromedriver as uc
from user_agents import parse

# 🚀 설정값 분리 - 모든 설정을 한 곳에서 관리
CONFIG = {
    "WAIT_TIMEOUT": 10,
    "RETRY_COUNT": 3,
    "MIN_DELAY": 3,
    "MAX_DELAY": 8,
    "POPUP_WAIT": 5,
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Whale/4.32.315.22 Safari/537.36",
    "SAVE_IMAGES": True,
    "SAVE_INTERMEDIATE": True,  # 중간 저장 여부
    "MAX_PRODUCT_NAME_LENGTH": 30,  # 파일명에 사용할 상품명 최대 길이
    
    # ⭐⭐⭐ 중요 설정: 도시당 크롤링할 상품 개수 ⭐⭐⭐
    # 여기서 숫자를 변경하세요! (예: 5개, 10개, 24개 등)
    "MAX_PRODUCTS_PER_CITY": 2,  # 🔢 도시당 크롤링할 상품 개수 설정
}

# 🎯 검색할 도시들 설정 - 여기서 원하는 도시로 변경하세요!
# ⭐⭐⭐ 중요 설정: 검색할 도시들 ⭐⭐⭐
CITIES_TO_SEARCH = ["방콕"]  # 🏙️ 여기서 도시를 변경하세요!
# 예시:
# CITIES_TO_SEARCH = ["방콕"]  # 1개 도시
# CITIES_TO_SEARCH = ["방콕", "도쿄"]  # 2개 도시 
# CITIES_TO_SEARCH = ["방콕", "도쿄", "파리", "뉴욕", "런던"]  # 5개 도시

# 🌏 도시별 대륙 및 국가 정보 매핑
CITY_INFO = {
    # 아시아
    "방콕": {"대륙": "아시아", "국가": "태국"},
    "도쿄": {"대륙": "아시아", "국가": "일본"},
    "오사카": {"대륙": "아시아", "국가": "일본"},
    "교토": {"대륙": "아시아", "국가": "일본"},
    "싱가포르": {"대륙": "아시아", "국가": "싱가포르"},
    "홍콩": {"대륙": "아시아", "국가": "홍콩"},
    "타이베이": {"대륙": "아시아", "국가": "대만"},
    "상하이": {"대륙": "아시아", "국가": "중국"},
    "베이징": {"대륙": "아시아", "국가": "중국"},
    "푸켓": {"대륙": "아시아", "국가": "태국"},
    "파타야": {"대륙": "아시아", "국가": "태국"},
    "치앙마이": {"대륙": "아시아", "국가": "태국"},
    "호치민": {"대륙": "아시아", "국가": "베트남"},
    "하노이": {"대륙": "아시아", "국가": "베트남"},
    "다낭": {"대륙": "아시아", "국가": "베트남"},
    "세부": {"대륙": "아시아", "국가": "필리핀"},
    "보라카이": {"대륙": "아시아", "국가": "필리핀"},
    "발리": {"대륙": "아시아", "국가": "인도네시아"},
    "자카르타": {"대륙": "아시아", "국가": "인도네시아"},
    "쿠알라룸푸르": {"대륙": "아시아", "국가": "말레이시아"},
    "코타키나발루": {"대륙": "아시아", "국가": "말레이시아"},
    "랑카위": {"대륙": "아시아", "국가": "말레이시아"},
    "페낭": {"대륙": "아시아", "국가": "말레이시아"},
    
    # 유럽
    "파리": {"대륙": "유럽", "국가": "프랑스"},
    "런던": {"대륙": "유럽", "국가": "영국"},
    "로마": {"대륙": "유럽", "국가": "이탈리아"},
    "밀라노": {"대륙": "유럽", "국가": "이탈리아"},
    "베니스": {"대륙": "유럽", "국가": "이탈리아"},
    "바르셀로나": {"대륙": "유럽", "국가": "스페인"},
    "마드리드": {"대륙": "유럽", "국가": "스페인"},
    "암스테르담": {"대륙": "유럽", "국가": "네덜란드"},
    "베를린": {"대륙": "유럽", "국가": "독일"},
    "뮌헨": {"대륙": "유럽", "국가": "독일"},
    "프라하": {"대륙": "유럽", "국가": "체코"},
    "비엔나": {"대륙": "유럽", "국가": "오스트리아"},
    "취리히": {"대륙": "유럽", "국가": "스위스"},
    "제네바": {"대륙": "유럽", "국가": "스위스"},
    "스톡홀름": {"대륙": "유럽", "국가": "스웨덴"},
    "코펜하겐": {"대륙": "유럽", "국가": "덴마크"},
    "헬싱키": {"대륙": "유럽", "국가": "핀란드"},
    "모스크바": {"대륙": "유럽", "국가": "러시아"},
    "상트페테르부르크": {"대륙": "유럽", "국가": "러시아"},
    "아테네": {"대륙": "유럽", "국가": "그리스"},
    "리스본": {"대륙": "유럽", "국가": "포르투갈"},
    "부다페스트": {"대륙": "유럽", "국가": "헝가리"},
    "바르샤바": {"대륙": "유럽", "국가": "폴란드"},
    
    # 북미
    "뉴욕": {"대륙": "북미", "국가": "미국"},
    "로스앤젤레스": {"대륙": "북미", "국가": "미국"},
    "라스베이거스": {"대륙": "북미", "국가": "미국"},
    "샌프란시스코": {"대륙": "북미", "국가": "미국"},
    "시카고": {"대륙": "북미", "국가": "미국"},
    "보스턴": {"대륙": "북미", "국가": "미국"},
    "마이애미": {"대륙": "북미", "국가": "미국"},
    "시애틀": {"대륙": "북미", "국가": "미국"},
    "하와이": {"대륙": "북미", "국가": "미국"},
    "밴쿠버": {"대륙": "북미", "국가": "캐나다"},
    "토론토": {"대륙": "북미", "국가": "캐나다"},
    "몬트리올": {"대륙": "북미", "국가": "캐나다"},
    "멕시코시티": {"대륙": "북미", "국가": "멕시코"},
    "칸쿤": {"대륙": "북미", "국가": "멕시코"},
    
    # 남미
    "리우데자네이루": {"대륙": "남미", "국가": "브라질"},
    "상파울루": {"대륙": "남미", "국가": "브라질"},
    "부에노스아이레스": {"대륙": "남미", "국가": "아르헨티나"},
    "리마": {"대륙": "남미", "국가": "페루"},
    "산티아고": {"대륙": "남미", "국가": "칠레"},
    "보고타": {"대륙": "남미", "국가": "콜롬비아"},
    "키토": {"대륙": "남미", "국가": "에콰도르"},
    
    # 오세아니아
    "시드니": {"대륙": "오세아니아", "국가": "호주"},
    "멜버른": {"대륙": "오세아니아", "국가": "호주"},
    "골드코스트": {"대륙": "오세아니아", "국가": "호주"},
    "퍼스": {"대륙": "오세아니아", "국가": "호주"},
    "애들레이드": {"대륙": "오세아니아", "국가": "호주"},
    "케언즈": {"대륙": "오세아니아", "국가": "호주"},
    "오클랜드": {"대륙": "오세아니아", "국가": "뉴질랜드"},
    "크라이스트처치": {"대륙": "오세아니아", "국가": "뉴질랜드"},
    "웰링턴": {"대륙": "오세아니아", "국가": "뉴질랜드"},
    
    # 중동
    "두바이": {"대륙": "중동", "국가": "UAE"},
    "아부다비": {"대륙": "중동", "국가": "UAE"},
    "도하": {"대륙": "중동", "국가": "카타르"},
    "이스탄불": {"대륙": "중동", "국가": "터키"},
    "텔아비브": {"대륙": "중동", "국가": "이스라엘"},
    "예루살렘": {"대륙": "중동", "국가": "이스라엘"},
    
    # 아프리카
    "카이로": {"대륙": "아프리카", "국가": "이집트"},
    "케이프타운": {"대륙": "아프리카", "국가": "남아프리카공화국"},
    "요하네스버그": {"대륙": "아프리카", "국가": "남아프리카공화국"},
    "카사블랑카": {"대륙": "아프리카", "국가": "모로코"},
    "마라케시": {"대륙": "아프리카", "국가": "모로코"},
    "나이로비": {"대륙": "아프리카", "국가": "케냐"},
    "다르에스살람": {"대륙": "아프리카", "국가": "탄자니아"},
    
    # 기타 (특별 지역)
    "몰디브": {"대륙": "아시아", "국가": "몰디브"},
    "괌": {"대륙": "오세아니아", "국가": "괌"},
    "사이판": {"대륙": "오세아니아", "국가": "사이판"},
    "제주도": {"대륙": "아시아", "국가": "한국"},
    "부산": {"대륙": "아시아", "국가": "한국"},
    "강릉": {"대륙": "아시아", "국가": "한국"},
    
    # 새로 추가된 태국 도시들
    "아유타야": {"대륙": "아시아", "국가": "태국"},
    "수코타이": {"대륙": "아시아", "국가": "태국"},
    "카오야이": {"대륙": "아시아", "국가": "태국"},
    "후아힌": {"대륙": "아시아", "국가": "태국"},
    "코사무이": {"대륙": "아시아", "국가": "태국"},
    "크라비": {"대륙": "아시아", "국가": "태국"}
}

# 🚀 진행률 표시 함수
def print_progress(current, total, city_name, status="진행중"):
    """진행률을 시각적으로 표시하는 함수"""
    percentage = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    # 상태에 따른 이모지 변경
    emoji = "🔍" if status == "진행중" else "✅" if status == "완료" else "❌"
    
    print(f"\n{emoji} 진행률: [{bar}] {percentage:.1f}% ({current}/{total})")
    print(f"📍 현재 작업: {city_name} - {status}")
    print("-" * 50)

def print_product_progress(current, total, product_name):
    """상품별 진행률 표시 함수"""
    percentage = (current / total) * 100
    bar_length = 20
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    safe_name = str(product_name)[:30] + "..." if len(str(product_name)) > 30 else str(product_name)
    print(f"    🎯 상품 진행률: [{bar}] {percentage:.1f}% ({current}/{total})")
    print(f"    📦 현재 상품: {safe_name}")

# 🚀 중간 저장 함수
def save_intermediate_results(results, city_name):
    """중간 결과를 임시 파일로 저장하는 함수 (데이터 손실 방지)"""
    if results and CONFIG["SAVE_INTERMEDIATE"]:
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            temp_filename = f"temp_중간저장_{city_name}_{timestamp}.csv"
            pd.DataFrame(results).to_csv(temp_filename, index=False, encoding='utf-8-sig')
            print(f"  💾 중간 결과 저장: {temp_filename}")
            return temp_filename
        except Exception as e:
            print(f"  ⚠️ 중간 저장 실패: {e}")
            return None
    return None

# 🚀 재시도 메커니즘 함수
def retry_operation(func, operation_name, max_retries=None):
    """실패한 작업을 재시도하는 함수"""
    if max_retries is None:
        max_retries = CONFIG["RETRY_COUNT"]
    
    for attempt in range(max_retries):
        try:
            return func()
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            if attempt == max_retries - 1:
                print(f"  ❌ {operation_name} 최종 실패: {type(e).__name__}")
                raise e
            print(f"  🔄 {operation_name} 재시도 {attempt + 1}/{max_retries} (오류: {type(e).__name__})")
            time.sleep(2)
        except Exception as e:
            print(f"  ❌ {operation_name} 예상치 못한 오류: {type(e).__name__}: {e}")
            raise e

def get_city_info(city_name):
    """도시명으로 대륙과 국가 정보를 가져오는 함수"""
    info = CITY_INFO.get(city_name, {"대륙": "기타", "국가": "기타"})
    return info["대륙"], info["국가"]

def make_safe_filename(filename):
    """파일명에 사용할 수 없는 문자 제거 및 안전성 강화"""
    if not filename:  # 빈 문자열이나 None 처리
        return "기본파일명"
    
    # 문자열로 변환 (숫자나 다른 타입이 들어올 경우 대비)
    safe_filename = str(filename)
    
    # 위험한 문자들 제거
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\r', '\t']
    for char in unsafe_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    # 파일명이 너무 길면 자르기 (OS 제한 고려)
    if len(safe_filename) > 200:
        safe_filename = safe_filename[:200]
    
    # 점(.)으로 시작하는 숨김 파일 방지
    if safe_filename.startswith('.'):
        safe_filename = '_' + safe_filename[1:]
    
    return safe_filename

# 🚀 드라이버 설정 함수들
def make_user_agent(ua, is_mobile):
    user_agent = parse(ua)
    model = user_agent.device.model
    platform = user_agent.os.family
    platform_version = user_agent.os.version_string + ".0.0"
    version = user_agent.browser.version[0]
    ua_full_version = user_agent.browser.version_string
    architecture = "x86"
    print(platform)
    if is_mobile:
        platform_info = "Linux armv8l"
        architecture= ""
    else: # Window
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
            "mobile":is_mobile #True, False
        }
    }
    return RET_USER_AGENT

def generate_random_geolocation():
    ltop_lat = 37.75415601640249
    ltop_long = 126.86767642302573
    rbottom_lat = 37.593829172663945
    rbottom_long = 127.15276051439332

    targetLat = random.uniform(rbottom_lat, ltop_lat)
    targetLong = random.uniform(ltop_long,rbottom_long)
    return {"latitude":targetLat, "longitude" : targetLong, "accuracy":100}

def setup_driver():
    """크롬 드라이버 설정 및 실행"""
    chromedriver_autoinstaller.install()
    
    options = uc.ChromeOptions()
    
    UA = CONFIG["USER_AGENT"]
    options.add_argument(f"--user-agent={UA}")
    
    rand_user_folder = random.randrange(1,100)
    raw_path = os.path.abspath("cookies")
    try:
        shutil.rmtree(raw_path)
    except:
        pass
    os.makedirs(raw_path, exist_ok=True)
    user_cookie_name = f"{raw_path}/{rand_user_folder}"
    if os.path.exists(user_cookie_name) == False:
        os.makedirs(user_cookie_name, exist_ok=True)
    
    try:
        driver = uc.Chrome(user_data_dir=user_cookie_name, options=options)
        print("✅ 크롬 드라이버 실행 성공!")
    except Exception as e:
        print('\n',"-"*50,"\n","-"*50,"\n")
        print("# 키홈 메세지 : 혹시 여기서 에러 발생시 [아래 블로그 참고 -> 재부팅 -> 다시 코드실행] 해보시길 바랍니다! \n (구글크롬 버젼 업그레이드 문제)")
        print('https://appfollow.tistory.com/102')
        print('\n',"-"*50,"\n","-"*50,"\n")
        raise RuntimeError
        
    UA_Data = make_user_agent(UA,False)
    driver.execute_cdp_cmd("Network.setUserAgentOverride",UA_Data)
    
    GEO_DATA = generate_random_geolocation()
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", GEO_DATA)
    driver.execute_cdp_cmd("Emulation.setUserAgentOverride", UA_Data)
    driver.execute_cdp_cmd("Emulation.setNavigatorOverrides",{"platform":"Linux armv8l"})
    
    return driver

# 🚀 크롤링 함수들
def go_to_main_page(driver):
    """메인 페이지로 이동"""
    driver.get("https://www.myrealtrip.com/experiences/")
    time.sleep(random.uniform(CONFIG["MIN_DELAY"], CONFIG["MAX_DELAY"]))
    return True

def find_and_fill_search(driver, city_name):
    """검색창 찾기 및 입력"""
    print(f"  🔍 '{city_name}' 검색창 찾는 중...")
    search_selectors = [
        (By.CSS_SELECTOR, "input[placeholder*='어디로']"),
        (By.CSS_SELECTOR, "input[type='text']"),
        (By.XPATH, "//input[contains(@placeholder, '어디로')]"),
        (By.XPATH, "/html/body/main/div/div[2]/section[1]/div[1]/div/div/input")
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

    if not search_input:
        raise NoSuchElementException("검색창을 찾을 수 없습니다")

    # 검색어 입력
    search_input.clear()
    search_input.send_keys(city_name)
    time.sleep(random.uniform(CONFIG["MIN_DELAY"], CONFIG["MIN_DELAY"]+2))
    print(f"  📝 '{city_name}' 키워드 입력 완료")
    return True

def click_search_button(driver):
    """검색 버튼 클릭"""
    print(f"  🔎 검색 버튼 찾는 중...")
    search_button_selectors = [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.CSS_SELECTOR, ".search-btn"),
        (By.XPATH, "//button[contains(@class, 'search')]"),
        (By.XPATH, "//img[contains(@alt, '검색')]//parent::*"),
        (By.XPATH, "/html/body/main/div/div[2]/section[1]/div[1]/div/div/div/img")
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
            time.sleep(random.uniform(CONFIG["MIN_DELAY"], CONFIG["MAX_DELAY"]))
            break
        except TimeoutException:
            continue

    if not search_clicked:
        raise NoSuchElementException("검색 버튼을 찾을 수 없습니다")
    return True

def handle_popup(driver):
    """팝업 처리"""
    popup_selectors = [
        (By.CSS_SELECTOR, ".popup-close"),
        (By.CSS_SELECTOR, ".modal-close"),
        (By.XPATH, "//button[contains(@aria-label, '닫기')]"),
        (By.XPATH, "//button[contains(text(), '닫기')]"),
        (By.XPATH, "/html/body/div[15]/div[2]/button")
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
            time.sleep(random.uniform(1, 4))
            break
        except TimeoutException:
            continue

    if not popup_closed:
        print(f"  ℹ️ 팝업창이 없거나 이미 닫혀있습니다.")
    return True

def click_view_all(driver):
    """전체 상품 보기 버튼 클릭"""
    print(f"  📋 전체 상품 보기 버튼 찾는 중...")
    view_all_selectors = [
        (By.XPATH, "//button[contains(text(), '전체')]"),
        (By.XPATH, "//span[contains(text(), '전체')]//parent::button"),
        (By.CSS_SELECTOR, "button[aria-label*='전체']"),
        (By.XPATH, "/html/body/div[4]/div[2]/div/div/div/span[21]/button")
    ]

    view_all_clicked = False
    for selector_type, selector_value in view_all_selectors:
        try:
            view_all_button = WebDriverWait(driver, CONFIG["WAIT_TIMEOUT"]).until(
                EC.element_to_be_clickable((selector_type, selector_value))
            )
            view_all_button.click()
            print(f"  ✅ 전체 상품 보기 클릭 성공!")
            view_all_clicked = True
            time.sleep(random.uniform(CONFIG["MIN_DELAY"], CONFIG["MIN_DELAY"]+3))
            break
        except TimeoutException:
            continue

    if not view_all_clicked:
        print(f"  ⚠️ 전체 상품 보기 버튼을 찾을 수 없습니다. 현재 상품으로 진행...")
    return True

# 🚀 새로운 함수: 페이지에서 모든 상품 URL 수집
def collect_page_urls(driver):
    """현재 페이지의 모든 상품 URL 수집"""
    print(f"  📊 현재 페이지의 상품 URL들을 수집 중...")
    
    # 페이지가 완전히 로드될 때까지 대기
    time.sleep(random.uniform(3, 5))
    
    product_url_selectors = [
        "a[href*='/experiences/']",
        "a[href*='/experience/']",
        ".product-item a",
        ".experience-card a"
    ]
    
    collected_urls = []
    
    for selector in product_url_selectors:
        try:
            # 상품 링크 요소들 찾기
            product_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in product_elements:
                try:
                    url = element.get_attribute('href')
                    if url and '/experiences/' in url and url not in collected_urls:
                        collected_urls.append(url)
                except Exception as e:
                    continue
            
            if collected_urls:
                break
                
        except Exception as e:
            continue
    
    # 중복 제거 및 유효성 검사
    valid_urls = []
    for url in collected_urls:
        if url and url.startswith('http') and '/experiences/' in url:
            valid_urls.append(url)
    
    print(f"  ✅ {len(valid_urls)}개의 상품 URL을 수집했습니다!")
    
    if len(valid_urls) == 0:
        print("  ⚠️ 상품 URL을 찾을 수 없습니다. 페이지 구조를 확인해주세요.")
    
    return valid_urls

# 🚀 상품 정보 수집 함수들
def get_product_name(driver):
    """상품명 수집"""
    print(f"  📊 상품 정보 수집 중...")
    title_selectors = [
        (By.CSS_SELECTOR, "h1"),
        (By.CSS_SELECTOR, ".product-title"),
        (By.XPATH, "//h1[contains(@class, 'title')]"),
        (By.XPATH, "/html/body/div[1]/main/div[1]/section/div[1]/h1")
    ]

    for selector_type, selector_value in title_selectors:
        try:
            title_element = WebDriverWait(driver, CONFIG["WAIT_TIMEOUT"]).until(
                EC.presence_of_element_located((selector_type, selector_value))
            )
            found_name = title_element.text
            time.sleep(random.uniform(CONFIG["MIN_DELAY"], CONFIG["MIN_DELAY"]+2))
            return found_name
        except TimeoutException:
            continue
    
    raise NoSuchElementException("상품명을 찾을 수 없습니다")

def get_price(driver):
    """가격 정보 수집"""
    price_selectors = [
        (By.CSS_SELECTOR, ".price"),
        (By.CSS_SELECTOR, "[class*='price']"),
        (By.XPATH, "//span[contains(text(), '원')]"),
        (By.XPATH, "/html/body/div[1]/main/div[1]/div[4]/div/div/div[2]/span[2]")
    ]

    for selector_type, selector_value in price_selectors:
        try:
            price_element = WebDriverWait(driver, CONFIG["WAIT_TIMEOUT"]).until(
                EC.presence_of_element_located((selector_type, selector_value))
            )
            found_price = price_element.text
            time.sleep(random.uniform(CONFIG["MIN_DELAY"], CONFIG["MIN_DELAY"]+2))
            return found_price
        except TimeoutException:
            continue
    
    return "정보 없음"  # 가격은 필수가 아니므로 기본값 반환

def get_rating(driver):
    """평점 정보 수집"""
    rating_selectors = [
        (By.CSS_SELECTOR, ".rating"),
        (By.CSS_SELECTOR, "[class*='rating']"),
        (By.XPATH, "//span[contains(@class, 'rating')]"),
        (By.XPATH, "/html/body/div[1]/main/div[1]/section/div[1]/span/span[2]")
    ]

    for selector_type, selector_value in rating_selectors:
        try:
            rating_element = WebDriverWait(driver, CONFIG["WAIT_TIMEOUT"]).until(
                EC.presence_of_element_located((selector_type, selector_value))
            )
            found_rating = rating_element.text
            time.sleep(random.uniform(2, 4))
            return found_rating
        except TimeoutException:
            continue
    
    return "정보 없음"

def get_review_count(driver):
    """리뷰 수 정보 수집"""
    print(f"  📝 리뷰 수 정보 찾는 중...")
    review_count_selectors = [
        (By.XPATH, "//span[contains(text(), '리뷰')]"),
        (By.XPATH, "//span[contains(text(), 'review')]"),
        (By.XPATH, "//span[contains(text(), '후기')]"),
        (By.XPATH, "//span[contains(text(), '개')]//preceding-sibling::span"),
        (By.XPATH, "//span[contains(text(), '건')]"),
        (By.CSS_SELECTOR, "[class*='review']"),
        (By.CSS_SELECTOR, "[class*='count']"),
        (By.XPATH, "//div[contains(@class, 'review')]//span"),
        (By.XPATH, "//div[contains(@class, 'rating')]//span[contains(text(), '개')]"),
        (By.XPATH, "//span[contains(@class, 'rating')]//following-sibling::span"),
        (By.XPATH, "//span[contains(text(), '개') and contains(text(), '리뷰')]"),
        (By.XPATH, "//span[contains(text(), '건') and contains(text(), '후기')]"),
        (By.XPATH, "//span[text()[contains(., '개') or contains(., '건') or contains(., 'review')]]"),
    ]

    for selector_type, selector_value in review_count_selectors:
        try:
            review_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((selector_type, selector_value))
            )
            review_text = review_element.text.strip()
            
            review_keywords = ['리뷰', '후기', 'review', '개', '건']
            has_number = any(char.isdigit() for char in review_text)
            has_keyword = any(keyword in review_text.lower() for keyword in review_keywords)
            
            if has_number and has_keyword and len(review_text) < 50:
                print(f"  ✅ 리뷰 수 정보 발견: {review_text}")
                return review_text
                
        except TimeoutException:
            continue

    print(f"  ℹ️ 리뷰 수 정보를 찾을 수 없습니다.")
    return ""

def get_language(driver):
    """언어 정보 수집"""
    print(f"  🌐 언어 정보 찾는 중...")
    language_selectors = [
        (By.XPATH, "//span[contains(text(), '언어')]//following-sibling::span"),
        (By.XPATH, "//div[contains(text(), '언어')]//following-sibling::div"),
        (By.CSS_SELECTOR, "[class*='language']"),
        (By.XPATH, "//span[contains(@class, 'language')]"),
        (By.XPATH, "//div[contains(@class, 'language')]"),
        (By.XPATH, "//span[contains(text(), '한국어')]"),
        (By.XPATH, "//span[contains(text(), '영어')]"),
        (By.XPATH, "//span[contains(text(), '중국어')]"),
        (By.XPATH, "//span[contains(text(), '일본어')]"),
        (By.XPATH, "//span[contains(text(), '태국어')]"),
        (By.XPATH, "//li[contains(text(), '언어')]"),
        (By.XPATH, "//p[contains(text(), '언어')]"),
        (By.XPATH, "//span[contains(text(), 'Korean')]"),
        (By.XPATH, "//span[contains(text(), 'English')]"),
        (By.XPATH, "//span[contains(text(), 'Chinese')]"),
        (By.XPATH, "//span[contains(text(), 'Japanese')]"),
        (By.XPATH, "//span[contains(text(), 'Thai')]"),
    ]

    for selector_type, selector_value in language_selectors:
        try:
            language_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((selector_type, selector_value))
            )
            language_text = language_element.text.strip()
            
            language_keywords = ['언어', '한국어', '영어', '중국어', '일본어', '태국어', 
                               'Korean', 'English', 'Chinese', 'Japanese', 'Thai',
                               '중문', '일문', '한글', 'Language']
            
            if any(keyword in language_text for keyword in language_keywords):
                print(f"  ✅ 언어 정보 발견: {language_text}")
                return language_text
                
        except TimeoutException:
            continue

    print(f"  ℹ️ 언어 정보를 찾을 수 없습니다.")
    return ""

def download_image(driver, product_name, city_name):
    """이미지 다운로드"""
    if not CONFIG["SAVE_IMAGES"]:
        return "이미지 저장 비활성화"
        
    print(f"  🖼️ 상품 이미지 다운로드 중...")
    image_selectors = [
        (By.CSS_SELECTOR, ".product-image img"),
        (By.CSS_SELECTOR, ".gallery img:first-child"),
        (By.XPATH, "//img[contains(@alt, '상품')]"),
        (By.XPATH, "/html/body/div[1]/main/div[1]/section/div[3]/div/div/div/div[1]/div/div/div/div/img")
    ]

    img_url = None
    for selector_type, selector_value in image_selectors:
        try:
            img_element = WebDriverWait(driver, CONFIG["WAIT_TIMEOUT"]).until(
                EC.presence_of_element_located((selector_type, selector_value))
            )
            img_url = img_element.get_attribute('src')
            break
        except TimeoutException:
            continue

    if img_url:
        try:
            # 안전한 문자열 처리 추가
            safe_product_name_raw = str(product_name) if product_name else "상품명없음"
            safe_product_name = make_safe_filename(f"{city_name}_{safe_product_name_raw[:CONFIG['MAX_PRODUCT_NAME_LENGTH']]}")
            img_download_path = os.path.abspath("") + "/myrealtripthumb_img/" + safe_product_name + ".png"
            urllib.request.urlretrieve(img_url, img_download_path)
            print(f"  ✅ 이미지 다운로드 완료!")
            return img_download_path
        except Exception as e:
            print(f"  ⚠️ 이미지 다운로드 실패: {type(e).__name__}: {e}")
            return "다운로드 실패"
    else:
        return "이미지 없음"

# 🚀 메인 크롤링 함수 (1페이지의 설정된 개수만큼 상품 크롤링)
def crawl_all_products_in_page(driver, city_name, continent, country):
    """1페이지에서 설정된 개수만큼 상품을 순차적으로 크롤링하는 함수"""
    print(f"\n🎯 {city_name} - 1페이지에서 {CONFIG['MAX_PRODUCTS_PER_CITY']}개 상품 크롤링 시작!")
    
    # 1단계: 현재 페이지의 모든 상품 URL 수집
    try:
        product_urls = retry_operation(
            lambda: collect_page_urls(driver), 
            "상품 URL 수집"
        )
        
        if not product_urls:
            print(f"  ❌ {city_name}: 상품 URL을 찾을 수 없습니다.")
            return []
            
    except Exception as e:
        print(f"  ❌ {city_name}: URL 수집 실패 - {type(e).__name__}")
        return []
    
    # 🔢 설정된 개수만큼만 선택 (⭐ 중요 부분 ⭐)
    max_products = CONFIG["MAX_PRODUCTS_PER_CITY"]
    selected_urls = product_urls[:max_products]  # 처음 N개만 선택
    
    print(f"  📊 총 {len(product_urls)}개 상품 중 {len(selected_urls)}개를 크롤링합니다!")
    
    # 2단계: 선택된 URL들을 순차적으로 방문하여 정보 수집
    page_results = []
    total_products = len(selected_urls)
    
    print("  " + "="*60)
    
    for product_index, product_url in enumerate(selected_urls, 1):
        # 상품별 진행률 표시
        print_product_progress(product_index, total_products, f"상품 {product_index}")
        
        # 기본값 설정
        product_name = "정보 없음"
        price = "정보 없음"
        grade_review = "정보 없음"
        review_count = ""
        language = ""
        img_path = "처리 안됨"
        current_url = product_url
        
        try:
            # 상품 상세 페이지로 이동
            print(f"    🔗 상품 {product_index} URL로 이동 중...")
            driver.get(product_url)
            time.sleep(random.uniform(CONFIG["MIN_DELAY"], CONFIG["MAX_DELAY"]))
            
            # 상품 정보 수집
            try:
                product_name = retry_operation(
                    lambda: get_product_name(driver), 
                    f"상품 {product_index} 이름 수집"
                )
            except Exception as e:
                print(f"    ⚠️ 상품명 수집 실패: {type(e).__name__}")
                product_name = f"수집실패_{product_index}"

            try:
                price = get_price(driver)
            except Exception as e:
                print(f"    ⚠️ 가격 정보 수집 실패: {type(e).__name__}")
                price = "정보 없음"

            try:
                grade_review = get_rating(driver)
            except Exception as e:
                print(f"    ⚠️ 평점 정보 수집 실패: {type(e).__name__}")
                grade_review = "정보 없음"

            try:
                review_count = get_review_count(driver)
            except Exception as e:
                print(f"    ⚠️ 리뷰 수 정보 수집 실패: {type(e).__name__}")
                review_count = ""

            try:
                language = get_language(driver)
            except Exception as e:
                print(f"    ⚠️ 언어 정보 수집 실패: {type(e).__name__}")
                language = ""

            try:
                img_path = download_image(driver, product_name, city_name)
            except Exception as e:
                print(f"    ⚠️ 이미지 처리 실패: {type(e).__name__}")
                img_path = "처리 실패"

            # 결과 저장
            result = {
                '번호': len(page_results) + 1,
                '대륙': continent,
                '국가': country,
                '도시': city_name,
                '상품번호': product_index,
                '상품명': product_name,
                '가격': price,
                '평점': grade_review,
                '리뷰수': review_count,
                '언어': language,
                '이미지_경로': img_path,
                'URL': current_url,
                '수집_시간': time.strftime('%Y-%m-%d %H:%M:%S'),
                '상태': '완전수집'
            }

            page_results.append(result)

            # 상품 정보 출력
            safe_name = str(product_name)[:40] + "..." if len(str(product_name)) > 40 else str(product_name)
            print(f"    ✅ 상품 {product_index} 크롤링 완료!")
            print(f"       상품명: {safe_name}")
            print(f"       가격: {price}")
            print(f"       평점: {grade_review}")
            print(f"       리뷰수: {review_count if review_count else '정보 없음'}")
            print(f"       언어: {language if language else '정보 없음'}")
            
            # 다음 상품을 위한 휴식 (마지막 상품이 아닌 경우)
            if product_index < total_products:
                wait_time = random.uniform(2, 5)
                print(f"    ⏰ 다음 상품까지 {wait_time:.1f}초 대기...")
                time.sleep(wait_time)

        except TimeoutException as e:
            print(f"    ⏰ 상품 {product_index}: 페이지 로딩 시간 초과")
            # 부분 결과라도 저장
            if product_name != "정보 없음":
                result = {
                    '번호': len(page_results) + 1,
                    '대륙': continent,
                    '국가': country,
                    '도시': city_name,
                    '상품번호': product_index,
                    '상품명': product_name,
                    '가격': price,
                    '평점': grade_review,
                    '리뷰수': review_count,
                    '언어': language,
                    '이미지_경로': img_path,
                    'URL': current_url,
                    '수집_시간': time.strftime('%Y-%m-%d %H:%M:%S'),
                    '상태': '부분수집(시간초과)'
                }
                page_results.append(result)
            continue
            
        except Exception as e:
            print(f"    ❌ 상품 {product_index}: 예상치 못한 오류 - {type(e).__name__}")
            # 부분 결과라도 저장
            if product_name != "정보 없음":
                result = {
                    '번호': len(page_results) + 1,
                    '대륙': continent,
                    '국가': country,
                    '도시': city_name,
                    '상품번호': product_index,
                    '상품명': product_name,
                    '가격': price,
                    '평점': grade_review,
                    '리뷰수': review_count,
                    '언어': language,
                    '이미지_경로': img_path,
                    'URL': current_url,
                    '수집_시간': time.strftime('%Y-%m-%d %H:%M:%S'),
                    '상태': f'부분수집({type(e).__name__})'
                }
                page_results.append(result)
            continue
    
    print(f"\n  🎉 {city_name} - {len(selected_urls)}개 상품 크롤링 완료!")
    print(f"  📊 총 {len(page_results)}개 상품 정보를 수집했습니다.")
    print("  " + "="*60)
    
    return page_results