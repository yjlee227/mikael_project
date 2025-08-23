"""
🚀 그룹 4,5: 확장성 개선 시스템 + 고급 셀렉터 및 가격/평점 수집
- 웹 요소 수집 최적화 및 오류 복구
- 가격/평점 정제 시스템 강화
- 시스템 안정성 및 확장성 개선
"""

import os
import time
import random
import platform
import shutil
import re
import json
from datetime import datetime
from urllib.parse import urlparse

# config 모듈에서 모든 설정과 라이브러리 상태 import
from .config import CONFIG, UNIFIED_CITY_INFO, CITIES_TO_SEARCH, get_city_code, get_city_info, ensure_config_directory, PANDAS_AVAILABLE, WEBDRIVER_AVAILABLE

# 조건부 import - config에서 확인된 상태에 따라
if PANDAS_AVAILABLE:
    import pandas as pd

# Selenium은 이 모듈에서만 필요하므로 로컬 체크
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
    SELENIUM_AVAILABLE = True
except ImportError:
    print("⚠️ Selenium 라이브러리가 없습니다. 일부 기능이 제한됩니다.")
    SELENIUM_AVAILABLE = False

if WEBDRIVER_AVAILABLE:
    import chromedriver_autoinstaller
    import undetected_chromedriver as uc

# =============================================================================
# 🚀 그룹 4: 확장성 개선 시스템
# =============================================================================


def get_system_info():
    """시스템 정보 수집"""
    try:
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "current_directory": os.getcwd(),
            "available_cities": len(UNIFIED_CITY_INFO),
            "config_settings": {
                "use_hash_system": CONFIG.get("USE_HASH_SYSTEM", False),
                "use_v2_url_system": CONFIG.get("USE_V2_URL_SYSTEM", False),
                "save_images": CONFIG.get("SAVE_IMAGES", False),
                "wait_timeout": CONFIG.get("WAIT_TIMEOUT", 10)
            }
        }
        
        # 디스크 사용량 (선택적)
        try:
            total, used, free = shutil.disk_usage(os.getcwd())
            info["disk_usage"] = {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2)
            }
        except:
            info["disk_usage"] = "unavailable"
        
        return info
        
    except Exception as e:
        print(f"⚠️ 시스템 정보 수집 실패: {e}")
        return {"error": str(e)}

def check_dependencies():
    """의존성 라이브러리 체크"""
    dependencies = {
        "selenium": False,
        "chromedriver_autoinstaller": False,
        "undetected_chromedriver": False,
        "user_agents": False,
        "pandas": False,
        "requests": False,
        "pillow": False,
        "beautifulsoup4": False
    }
    
    # 각 라이브러리 체크
    for lib_name in dependencies.keys():
        try:
            if lib_name == "pillow":
                import PIL
            elif lib_name == "beautifulsoup4":
                import bs4
            else:
                __import__(lib_name)
            dependencies[lib_name] = True
        except ImportError:
            dependencies[lib_name] = False
    
    # 결과 출력
    print("🔍 의존성 라이브러리 체크:")
    for lib, available in dependencies.items():
        status = "✅" if available else "❌"
        print(f"  {status} {lib}")
    
    return dependencies

def setup_driver():
    """크롬 드라이버 설정 및 실행 (안정성 강화 버전)"""
    if not SELENIUM_AVAILABLE:
        raise RuntimeError("Selenium이 설치되지 않았습니다. pip install selenium을 실행하세요.")
    
    try:
        chromedriver_autoinstaller.install()
        
        options = uc.ChromeOptions()
        
        # 기본 설정
        UA = CONFIG["USER_AGENT"]
        options.add_argument(f"--user-agent={UA}")
        
        # 쿠키 폴더 설정
        rand_user_folder = random.randrange(1, 100)
        raw_path = os.path.abspath("cookies")
        os.makedirs(raw_path, exist_ok=True)
        user_cookie_name = f"{raw_path}/{rand_user_folder}"
        os.makedirs(user_cookie_name, exist_ok=True)
        
        # 호환성 문제를 해결한 안전한 옵션들
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-extensions')
        
        # 성능 최적화
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        driver = uc.Chrome(user_data_dir=user_cookie_name, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_window_size(1920, 1080)  # Full HD 크기로 변경
        
        print("✅ 크롬 드라이버 실행 성공!")
        return driver
        
    except Exception as e:
        print(f"❌ 드라이버 초기화 실패: {type(e).__name__}: {str(e)}")
        raise RuntimeError(f"드라이버 초기화 실패: {e}")

# =============================================================================
# 🎯 그룹 5: 고급 셀렉터 및 가격/평점 수집 시스템
# =============================================================================

def get_product_name(driver, url_type="Product"):
    """✅ 상품명 수집 (KLOOK 최적화)"""
    if not SELENIUM_AVAILABLE:
        return "정보 없음"
    
    print(f"  📊 {url_type} 상품명 수집 중...")

    title_selectors = [
        (By.CSS_SELECTOR, "#activity_title > h1 > span"),    # KLOOK 최우선 (100% 확인됨)
        (By.CSS_SELECTOR, "#activity_title .vam"),           # KLOOK 백업
        (By.CSS_SELECTOR, "#activity_title h1"),             # KLOOK 백업2
        (By.CSS_SELECTOR, "h1"),                             # 범용 백업
        (By.CSS_SELECTOR, "[data-testid='activity-title']"), # 새로운 KLOOK 구조
        (By.CSS_SELECTOR, ".activity-title"),                # 클래스 기반
        (By.XPATH, "//h1[contains(@class, 'title')]"),       # 일반적인 제목
    ]

    for selector_type, selector_value in title_selectors:
        try:
            title_element = WebDriverWait(driver, CONFIG["WAIT_TIMEOUT"]).until(
                EC.presence_of_element_located((selector_type, selector_value))
            )
            found_name = title_element.text.strip()
            if found_name and len(found_name) > 1:
                print(f"    ✅ 상품명 발견: '{found_name[:50]}...'")
                return found_name
        except TimeoutException:
            continue
        except Exception as e:
            print(f"    ⚠️ 상품명 수집 중 오류: {type(e).__name__}")
            continue
    
    print("    ❌ 상품명을 찾을 수 없습니다")
    return "정보 없음"

def get_price(driver, logger=None):
    """✅ 가격 수집 - KLOOK 최적화 버전 (로깅 강화)"""
    if not SELENIUM_AVAILABLE:
        return "정보 없음"
    
    log = logger if logger else print
    log("  💰 가격 정보 수집 중...")

    price_selectors = [
        (By.CSS_SELECTOR, "#banner_atlas .salling-price span"),     # 판매가 (최우선)
        (By.CSS_SELECTOR, "#banner_atlas .market-price b"),         # 정가
        (By.CSS_SELECTOR, "#banner_atlas .price-box span"),         # 범용 백업
        (By.CSS_SELECTOR, "span[data-v-7d296880]"),                 # data-v 속성
        (By.CSS_SELECTOR, ".price"),
        (By.CSS_SELECTOR, "[class*='price']"),
        (By.CSS_SELECTOR, "[data-testid*='price']"),                # 새로운 구조
        (By.XPATH, "//span[contains(text(), '₩') and string-length(text()) < 30]"),
        (By.XPATH, "//span[contains(text(), '원') and contains(text(), ',') and string-length(text()) < 30]"),
        (By.XPATH, "//div[contains(@class, 'price')]//span"),       # 가격 컨테이너 내 span
    ]

    invalid_keywords = [
        '쿠폰', '받기', '다운', '할인', '적립', '포인트',
        '최소', '인원', '명', '최대', '선택', '옵션',
        '예약', '신청', '문의', '상담', '확인', '명부터',
        '시간', '일정', '코스', '투어', '여행',
        '언어', '가이드', '포함', '불포함', '이상',
        '취소', '환불', '변경', '안내', '모집'
    ]

    price_patterns = [
        r'₩\s*\d{1,3}(?:,\d{3})+',        # ₩ 35,400
        r'\d{1,3}(?:,\d{3})+원[~-]?',     # 10,000원~
        r'\d+,\d+원[~-]?',                # 간단한 천단위
        r'\d{4,}원[~-]?',                 # 10000원~
        r'KRW\s*\d{1,3}(?:,\d{3})+',     # KRW 표기
    ]

    for selector_type, selector_value in price_selectors:
        try:
            log(f"  🔎 셀렉터 시도: {selector_type} | {selector_value}")
            price_elements = driver.find_elements(selector_type, selector_value)
            if not price_elements:
                log("    ↪ 요소 없음")
                continue

            for idx, price_element in enumerate(price_elements[:5], start=1):  # 최대 5개만 확인
                try:
                    found_price = price_element.text.strip()
                except (StaleElementReferenceException, WebDriverException) as e:
                    log(f"    ⚠️ 요소#{idx} 접근 실패: {type(e).__name__}")
                    continue

                if not found_price:
                    log(f"    ↪ 요소#{idx} 빈 텍스트 -> 스킵")
                    continue

                if any(keyword in found_price for keyword in invalid_keywords):
                    log(f"    ↪ 요소#{idx} 금지 키워드 포함('{found_price}') -> 스킵")
                    continue

                if len(found_price) > 30:
                    log(f"    ↪ 요소#{idx} 길이 초과('{found_price}') -> 스킵")
                    continue

                is_valid_price = any(re.search(pattern, found_price) for pattern in price_patterns)
                if is_valid_price and ('원' in found_price or '₩' in found_price or 'KRW' in found_price):
                    log(f"    ✅ 유효한 가격 발견: '{found_price}'")
                    return found_price
                else:
                    log(f"    ↪ 요소#{idx} 패턴 불일치('{found_price}') -> 스킵")

        except Exception as e:
            log(f"  ❌ 셀렉터 실패: {type(e).__name__} | {selector_value}")
            continue

    log("    ❌ 가격 정보를 찾을 수 없습니다")
    return "정보 없음"

def get_rating(driver, logger=None):
    """✅ 평점 수집 (KLOOK 최적화)"""
    if not SELENIUM_AVAILABLE:
        return "정보 없음"
    
    log = logger if logger else print
    log("  ⭐ 평점 정보 수집 중...")

    rating_selectors = [
        (By.CSS_SELECTOR, ".rating-score"),                    # KLOOK 최우선
        (By.CSS_SELECTOR, "[data-testid='rating-score']"),     # 새로운 구조
        (By.CSS_SELECTOR, ".review-score"),                    # 리뷰 점수
        (By.CSS_SELECTOR, "[class*='rating']"),                # 평점 관련 클래스
        (By.CSS_SELECTOR, "[class*='score']"),                 # 점수 관련 클래스
        (By.XPATH, "//span[contains(text(), '.') and string-length(text()) < 10]"),  # 점수 형태
        (By.XPATH, "//div[contains(@class, 'rating')]//span"), # 평점 컨테이너 내
    ]

    rating_patterns = [
        r'(\d+\.?\d*)\s*/\s*5',           # 4.5/5
        r'(\d+\.?\d*)\s*점',              # 4.5점
        r'^(\d+\.?\d*)$',                 # 4.5
        r'(\d+\.?\d*)\s*stars?',          # 4.5 stars
    ]

    for selector_type, selector_value in rating_selectors:
        try:
            rating_elements = driver.find_elements(selector_type, selector_value)
            
            for rating_element in rating_elements[:3]:  # 최대 3개만 확인
                try:
                    found_rating = rating_element.text.strip()
                    
                    if not found_rating or len(found_rating) > 20:
                        continue
                    
                    # 패턴 매칭
                    for pattern in rating_patterns:
                        match = re.search(pattern, found_rating)
                        if match:
                            rating_value = float(match.group(1))
                            if 0 <= rating_value <= 5:  # 합리적인 평점 범위
                                log(f"    ✅ 평점 발견: {rating_value}")
                                return str(rating_value)
                    
                except Exception:
                    continue
                    
        except Exception:
            continue

    log("    ❌ 평점 정보를 찾을 수 없습니다")
    return "정보 없음"

def clean_price(price_text):
    """✅ 가격 정제 (모든 사이트 통일: 77,900원 형태)"""
    if not price_text or price_text == "정보 없음":
        return "정보 없음"
    
    # 모든 가격 패턴 (₩, 원, $ 등 모두 지원)
    price_patterns = [
        r'₩\s*(\d{1,3}(?:,\d{3})*)',           # ₩ 77,900
        r'\$\s*(\d{1,3}(?:,\d{3})*)',          # $ 100
        r'KRW\s*(\d{1,3}(?:,\d{3})*)',         # KRW 77,900
        r'(\d{1,3}(?:,\d{3})*)\s*원[~-]?',     # 77,900원
        r'(\d{1,3}(?:,\d{3})*)'                # 77900 (숫자만)
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, price_text)
        if match:
            # 모든 경우에 "77,900원" 형태로 통일
            return f"{match.group(1)}원"
    
    return price_text

def clean_rating(rating_text):
    """✅ 평점 정제"""
    if not rating_text or rating_text == "정보 없음":
        return "정보 없음"
    
    rating_pattern = r'(\d+\.?\d*)'
    match = re.search(rating_pattern, rating_text)
    
    if match:
        try:
            rating_value = float(match.group(1))
            # 5.0 이하의 합리적인 평점만 반환
            if 0 <= rating_value <= 5:
                return rating_value
        except ValueError:
            pass
    
    return rating_text

# =============================================================================
# 🔧 시스템 유틸리티 함수들
# =============================================================================

def wait_with_progress(seconds, message="대기 중"):
    """진행률과 함께 대기"""
    print(f"⏰ {message}: {seconds}초")
    for i in range(seconds):
        remaining = seconds - i
        progress = "█" * (i + 1) + "░" * remaining
        print(f"\r   [{progress}] {remaining}초 남음", end="", flush=True)
        time.sleep(1)
    print("\n   ✅ 대기 완료")

def safe_get_attribute(element, attribute, default=""):
    """안전한 속성 가져오기"""
    if not SELENIUM_AVAILABLE:
        return default
    
    try:
        value = element.get_attribute(attribute)
        return value if value else default
    except Exception:
        return default

def safe_get_text(element, default=""):
    """안전한 텍스트 가져오기"""
    if not SELENIUM_AVAILABLE:
        return default
    
    try:
        text = element.text.strip()
        return text if text else default
    except Exception:
        return default

def create_safe_filename(filename, max_length=200):
    """안전한 파일명 생성"""
    if not filename:
        return "기본파일명"
    
    safe_filename = str(filename)
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\r', '\t']
    for char in unsafe_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    if len(safe_filename) > max_length:
        safe_filename = safe_filename[:max_length]
    
    if safe_filename.startswith('.'):
        safe_filename = '_' + safe_filename[1:]
    
    return safe_filename.strip()

# =============================================================================
# 📊 상세 상품 정보 수집 (원본에서 누락된 기능)
# =============================================================================

def get_categories(driver, logger=None):
    """KLOOK 브레드크럼 최적화 카테고리 수집"""
    if not SELENIUM_AVAILABLE:
        return "정보 없음"
    
    log = logger if logger else print
    log("  📂 카테고리 정보 수집 중...")
    
    category_selectors = [
        # KLOOK 브레드크럼 셀렉터들
        ".breadcrumb a",
        "[data-testid='breadcrumb'] a", 
        ".breadcrumb-item",
        ".navigation-path a",
        "[class*='breadcrumb'] span",
        "[class*='category'] span"
    ]
    
    found_categories = []
    
    for selector in category_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                try:
                    category_text = element.text.strip()
                    if category_text and category_text not in found_categories and len(category_text) < 50:
                        found_categories.append(category_text)
                except:
                    continue
                    
            if found_categories:
                break
                
        except Exception:
            continue
    
    if found_categories:
        # 상위 3개 카테고리만 반환
        categories_str = " > ".join(found_categories[:3])
        log(f"    ✅ 카테고리 발견: {categories_str}")
        return categories_str
    else:
        log("    ❌ 카테고리 정보를 찾을 수 없습니다")
        return "정보 없음"

def get_highlights(driver, logger=None):
    """KLOOK 토글 모달 최적화 하이라이트 수집"""
    if not SELENIUM_AVAILABLE:
        return "정보 없음"
    
    log = logger if logger else print
    log("  ✨ 하이라이트 정보 수집 중...")
    
    highlight_selectors = [
        # KLOOK 하이라이트/특징 셀렉터들
        "[data-testid='highlights'] li",
        ".highlights li",
        ".features li",
        "[class*='highlight'] span",
        "[class*='feature'] span",
        ".description ul li"
    ]
    
    found_highlights = []
    
    for selector in highlight_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements[:5]:  # 최대 5개만
                try:
                    highlight_text = element.text.strip()
                    if highlight_text and len(highlight_text) < 200:
                        found_highlights.append(highlight_text)
                except:
                    continue
                    
            if found_highlights:
                break
                
        except Exception:
            continue
    
    if found_highlights:
        highlights_str = " | ".join(found_highlights[:3])  # 상위 3개만
        log(f"    ✅ 하이라이트 발견: {highlights_str[:100]}...")
        return highlights_str
    else:
        log("    ❌ 하이라이트 정보를 찾을 수 없습니다")
        return "정보 없음"

def get_review_count(driver, logger=None):
    """KLOOK 최적화 리뷰수 수집"""
    if not SELENIUM_AVAILABLE:
        return "정보 없음"
    
    log = logger if logger else print
    log("  📝 리뷰수 정보 수집 중...")
    
    review_selectors = [
        # KLOOK 리뷰수 셀렉터들
        "[data-testid='review-count']",
        ".review-count",
        "[class*='review'][class*='count']",
        "[class*='rating'] .count",
        "span:contains('reviews')",
        "span:contains('리뷰')"
    ]
    
    for selector in review_selectors:
        try:
            if ":contains(" in selector:
                # XPath로 변환
                if "리뷰" in selector:
                    xpath = "//span[contains(text(), '리뷰')]"
                else:
                    xpath = "//span[contains(text(), 'reviews')]"
                elements = driver.find_elements(By.XPATH, xpath)
            else:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in elements:
                try:
                    review_text = element.text.strip()
                    # 숫자가 포함된 리뷰수 텍스트 찾기
                    if review_text and any(char.isdigit() for char in review_text):
                        log(f"    ✅ 리뷰수 발견: {review_text}")
                        return review_text
                except:
                    continue
                    
        except Exception:
            continue
    
    log("    ❌ 리뷰수 정보를 찾을 수 없습니다")
    return "정보 없음"

def get_language(driver, logger=None):
    """KLOOK 최적화 언어 정보 수집"""
    if not SELENIUM_AVAILABLE:
        return "정보 없음"
    
    log = logger if logger else print
    log("  🌐 언어 정보 수집 중...")
    
    try:
        # URL에서 언어 확인
        current_url = driver.current_url
        if "/ko/" in current_url:
            log("    ✅ 언어: 한국어 (URL 기반)")
            return "한국어"
        elif "/en/" in current_url:
            log("    ✅ 언어: 영어 (URL 기반)")
            return "영어"
        
        # HTML lang 속성 확인
        try:
            html_element = driver.find_element(By.TAG_NAME, "html")
            lang_attr = html_element.get_attribute("lang")
            if lang_attr:
                if lang_attr.startswith("ko"):
                    log(f"    ✅ 언어: 한국어 (HTML lang: {lang_attr})")
                    return "한국어"
                elif lang_attr.startswith("en"):
                    log(f"    ✅ 언어: 영어 (HTML lang: {lang_attr})")
                    return "영어"
                else:
                    log(f"    ✅ 언어: {lang_attr}")
                    return lang_attr
        except:
            pass
        
        log("    ❌ 언어 정보를 확인할 수 없습니다")
        return "정보 없음"
        
    except Exception as e:
        log(f"    ❌ 언어 정보 수집 실패: {e}")
        return "정보 없음"

# =============================================================================
# 🔄 세션 상태 관리 (원본에서 누락된 기능)
# =============================================================================

def save_crawler_state(state, new_url):
    """hashlib 통합 버전 크롤링 상태 저장"""
    try:
        state_dir = "crawler_state"
        os.makedirs(state_dir, exist_ok=True)
        
        state_file = os.path.join(state_dir, "current_state.json")
        
        # 현재 상태 정보
        current_state = {
            "timestamp": datetime.now().isoformat(),
            "current_url": new_url,
            "state_data": state,
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(current_state, f, ensure_ascii=False, indent=2)
        
        print(f"💾 크롤링 상태 저장 완료: {new_url}")
        return True
        
    except Exception as e:
        print(f"❌ 크롤링 상태 저장 실패: {e}")
        return False

def load_crawler_state():
    """크롤링 상태 로드"""
    try:
        state_file = os.path.join("crawler_state", "current_state.json")
        
        if not os.path.exists(state_file):
            return None
        
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        print(f"📂 크롤링 상태 로드 완료: {state_data.get('current_url', 'N/A')}")
        return state_data
        
    except Exception as e:
        print(f"❌ 크롤링 상태 로드 실패: {e}")
        return None

def load_session_state(city_name):
    """hashlib 통합 버전 이전 세션 상태 복원"""
    try:
        from .config import get_city_code
        
        state_dir = "session_states"
        if not os.path.exists(state_dir):
            return None
        
        city_code = get_city_code(city_name)
        session_files = [f for f in os.listdir(state_dir) if f.startswith(city_code)]
        
        if not session_files:
            return None
        
        # 가장 최근 세션 파일 찾기
        latest_file = max(session_files, key=lambda f: os.path.getmtime(os.path.join(state_dir, f)))
        session_path = os.path.join(state_dir, latest_file)
        
        with open(session_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        print(f"🔄 이전 세션 상태 복원: {latest_file}")
        return session_data
        
    except Exception as e:
        print(f"❌ 세션 상태 복원 실패: {e}")
        return None

def get_last_product_number(city_name):
    """기존 CSV에서 마지막 번호 확인"""
    try:
        from .config import get_city_info
        
        continent, country = get_city_info(city_name)
        
        # 도시국가 특별 처리
        if city_name in ["마카오", "홍콩", "싱가포르"]:
            csv_path = os.path.join("data", continent, f"klook_{city_name}_products.csv")
        else:
            csv_path = os.path.join("data", continent, country, city_name, f"klook_{city_name}_products.csv")
        
        if not os.path.exists(csv_path):
            return 0
        
        if not PANDAS_AVAILABLE:
            return 0
        
        import pandas as pd
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        if '번호' in df.columns and len(df) > 0:
            last_number = df['번호'].max()
            print(f"📊 마지막 상품 번호: {last_number}")
            return int(last_number) if not pd.isna(last_number) else 0
        
        return len(df)  # 번호 컬럼이 없으면 총 개수 반환
        
    except Exception as e:
        print(f"❌ 마지막 번호 확인 실패: {e}")
        return 0

# =============================================================================
# 📈 해시 시스템 고급 기능 (원본에서 누락된 기능)
# =============================================================================

def get_hash_stats(city_name):
    """해시 시스템 통계 (0.01초)"""
    try:
        from .config import get_city_code
        
        hash_dir = os.path.join("hash_index", city_name)
        if not os.path.exists(hash_dir):
            return {"processed_count": 0, "latest_hash": None}
        
        hash_files = [f for f in os.listdir(hash_dir) if f.endswith('.done')]
        
        stats = {
            "processed_count": len(hash_files),
            "latest_hash": None,
            "hash_directory": hash_dir
        }
        
        if hash_files:
            # 가장 최근 해시 파일 찾기
            latest_file = max(hash_files, key=lambda f: os.path.getmtime(os.path.join(hash_dir, f)))
            stats["latest_hash"] = latest_file.replace('.done', '')
        
        return stats
        
    except Exception as e:
        print(f"❌ 해시 통계 조회 실패: {e}")
        return {"error": str(e)}

def migrate_csv_to_hash(city_name):
    """기존 CSV 데이터를 해시 시스템으로 마이그레이션"""
    try:
        from .config import get_completed_urls_from_csv, mark_url_processed_fast
        
        print(f"🔄 '{city_name}' CSV → 해시 시스템 마이그레이션 시작...")
        
        # CSV에서 완료된 URL 가져오기
        completed_urls = get_completed_urls_from_csv(city_name)
        
        if not completed_urls:
            print("  ℹ️ 마이그레이션할 CSV 데이터가 없습니다")
            return 0
        
        migrated_count = 0
        for url in completed_urls:
            if mark_url_processed_fast(url, city_name, "csv_migration"):
                migrated_count += 1
        
        print(f"  ✅ 마이그레이션 완료: {migrated_count}개 URL")
        return migrated_count
        
    except Exception as e:
        print(f"❌ CSV 마이그레이션 실패: {e}")
        return 0

print("✅ 그룹 4,5 완료: 확장성 개선 시스템 + 고급 셀렉터 및 가격/평점 수집!")
print("   🔧 시스템 관리:")
print("   - get_system_info(): 시스템 정보 수집")
print("   - check_dependencies(): 의존성 체크")
print("   - setup_driver(): 안정성 강화된 드라이버 설정")
print("   🎯 고급 수집:")
print("   - get_product_name(): KLOOK 상품명 수집")
print("   - get_price(): 가격 정보 수집 (로깅 강화)")
print("   - get_rating(): 평점 정보 수집")
print("   - clean_price()/clean_rating(): 데이터 정제")
print("   📊 상세 정보 수집 (추가됨):")
print("   - get_categories(): 브레드크럼 카테고리 수집")
print("   - get_highlights(): 토글 모달 하이라이트 수집")
print("   - get_review_count(): 리뷰수 수집")
print("   - get_language(): 언어 정보 수집")
print("   🔄 세션 상태 관리 (추가됨):")
print("   - save_crawler_state(): 크롤링 상태 저장")
print("   - load_crawler_state(): 크롤링 상태 로드")
print("   - load_session_state(): 이전 세션 상태 복원")
print("   - get_last_product_number(): 마지막 번호 확인")
print("   📈 해시 시스템 (추가됨):")
print("   - get_hash_stats(): 해시 시스템 통계")
print("   - migrate_csv_to_hash(): CSV → 해시 마이그레이션")
print("   🛠️ 유틸리티:")
print("   - wait_with_progress(): 진행률 표시 대기")
print("   - safe_get_attribute()/safe_get_text(): 안전한 요소 접근")
print("   - create_safe_filename(): 안전한 파일명 생성")