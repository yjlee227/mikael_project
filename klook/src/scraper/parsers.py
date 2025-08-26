"""
데이터 추출 및 정제 시스템
- 웹 요소에서 데이터 추출
- 가격, 평점, 텍스트 정제
- 카테고리 및 특징 분석
"""

import re
import time
import random
from datetime import datetime

from ..config import CONFIG, SELENIUM_AVAILABLE

if SELENIUM_AVAILABLE:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# =============================================================================
# 기본 데이터 추출 시스템
# =============================================================================

def get_product_name(driver):
    """상품명 추출 (원본 정교한 셀렉터 사용)"""
    print("  📝 상품명 추출 중...")
    
    if not SELENIUM_AVAILABLE:
        return "상품명 추출 불가"
    
    # 원본에서 실제 작동하는 정교한 셀렉터들
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
            element = driver.find_element(selector_type, selector_value)
            
            if element and element.text.strip():
                name = element.text.strip()
                print(f"    ✅ 상품명: {name[:50]}...")
                return name
                
        except Exception:
            continue
    
    print("    ⚠️ 상품명 추출 실패")
    return "상품명 없음"

def get_price(driver):
    """가격 정보 추출 (원본 정교한 셀렉터 사용)"""
    print("  💰 가격 추출 중...")
    
    if not SELENIUM_AVAILABLE:
        return "가격 추출 불가"
    
    # 원본에서 실제 작동하는 정교한 가격 셀렉터들
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
    
    for selector_type, selector_value in price_selectors:
        try:
            elements = driver.find_elements(selector_type, selector_value)
            
            for element in elements:
                try:
                    price_text = element.text.strip()
                    if price_text and ('₩' in price_text or 'KRW' in price_text or '원' in price_text or price_text.replace(',', '').replace('.', '').isdigit()):
                        cleaned_price = clean_price(price_text)
                        if cleaned_price != "가격 정보 없음":
                            print(f"    ✅ 가격: {cleaned_price}")
                            return cleaned_price
                except:
                    continue
                    
        except Exception:
            continue
    
    print("    ⚠️ 가격 추출 실패")
    return "가격 정보 없음"

def get_rating(driver):
    """평점 정보 추출 (원본 정교한 셀렉터 사용)"""
    print("  ⭐ 평점 추출 중...")
    
    if not SELENIUM_AVAILABLE:
        return "평점 추출 불가"
    
    # 원본에서 실제 작동하는 정교한 평점 셀렉터들
    rating_selectors = [
        (By.CSS_SELECTOR, ".rating-score"),                    # KLOOK 최우선
        (By.CSS_SELECTOR, "[data-testid='rating-score']"),     # 새로운 구조
        (By.CSS_SELECTOR, ".review-score"),                    # 리뷰 점수
        (By.CSS_SELECTOR, "[class*='rating']"),                # 평점 관련 클래스
        (By.CSS_SELECTOR, "[class*='score']"),                 # 점수 관련 클래스
        (By.XPATH, "//span[contains(text(), '.') and string-length(text()) < 10]"),  # 점수 형태
        (By.XPATH, "//div[contains(@class, 'rating')]//span"), # 평점 컨테이너 내
    ]
    
    for selector_type, selector_value in rating_selectors:
        try:
            elements = driver.find_elements(selector_type, selector_value)
            
            for element in elements:
                try:
                    rating_text = element.text.strip()
                    if rating_text and (rating_text.replace('.', '').isdigit() or '/' in rating_text):
                        cleaned_rating = clean_rating(rating_text)
                        if cleaned_rating != "평점 정보 없음":
                            print(f"    ✅ 평점: {cleaned_rating}")
                            return cleaned_rating
                except:
                    continue
                    
        except Exception:
            continue
    
    print("    ⚠️ 평점 추출 실패")
    return "평점 정보 없음"

def get_review_count(driver):
    """리뷰 수 추출"""
    print("  💬 리뷰 수 추출 중...")
    
    if not SELENIUM_AVAILABLE:
        return "리뷰 수 추출 불가"
    
    review_selectors = [
        ("css", "[class*='review'][class*='count']"),
        ("css", ".review-count"),
        ("css", "[data-testid*='review-count']"),
        ("css", ".reviews-count"),
        ("css", "[class*='rating'] .count"),
        ("css", ".comment-count")
    ]
    
    for selector_type, selector_value in review_selectors:
        try:
            if selector_type == "css":
                elements = driver.find_elements(By.CSS_SELECTOR, selector_value)
            else:  # xpath
                elements = driver.find_elements(By.XPATH, selector_value)
            
            for element in elements:
                try:
                    review_text = element.text.strip()
                    if review_text:
                        # 숫자 추출
                        numbers = re.findall(r'\d+', review_text)
                        if numbers:
                            review_count = numbers[0]
                            print(f"    ✅ 리뷰 수: {review_count}")
                            return review_count
                except:
                    continue
                    
        except Exception:
            continue
    
    print("    ⚠️ 리뷰 수 추출 실패")
    return "0"

def get_categories(driver):
    """카테고리 정보 추출"""
    print("  🏷️ 카테고리 추출 중...")
    
    if not SELENIUM_AVAILABLE:
        return "카테고리 추출 불가"
    
    category_selectors = [
        "[class*='breadcrumb'] span",
        "[class*='category'] span",
        ".breadcrumb a",
        ".category-tag",
        "[data-testid*='category']",
        ".tags span",
        ".labels span"
    ]
    
    categories = []
    
    for selector in category_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in elements:
                try:
                    category_text = element.text.strip()
                    if category_text and len(category_text) < 50:  # 너무 긴 텍스트는 제외
                        categories.append(category_text)
                except:
                    continue
                    
        except Exception:
            continue
    
    if categories:
        unique_categories = list(set(categories))[:3]  # 최대 3개까지
        category_str = " > ".join(unique_categories)
        print(f"    ✅ 카테고리: {category_str}")
        return category_str
    
    print("    ⚠️ 카테고리 추출 실패")
    return "기타"

def get_highlights(driver):
    """하이라이트 정보 수집 (두 가지 유형 대응 - 원본 소스 기반)"""
    print("  ✨ 하이라이트 정보 수집 중...")
    
    if not SELENIUM_AVAILABLE:
        return "정보 없음"
    
    try:
        # 1. 하이라이트 섹션 존재 확인
        try:
            highlight_section = driver.find_element(By.CSS_SELECTOR, "#highlight")
        except:
            print("    ⚠️ 하이라이트 섹션이 없습니다")
            return "정보 없음"
        
        # 2. 펼치기 버튼 상태 스마트 확인
        expand_buttons = driver.find_elements(By.CSS_SELECTOR, "#highlight .experience-view-more_text")
        
        has_expand_button = False
        if expand_buttons:
            button = expand_buttons[0]
            parent = button.find_element(By.XPATH, "./..")
            
            # 버튼과 부모 요소의 style 확인
            button_style = button.get_attribute("style") or ""
            parent_style = parent.get_attribute("style") or ""
            
            # visibility:hidden 또는 display:none 체크
            has_expand_button = (
                "visibility:hidden" not in button_style and 
                "visibility: hidden" not in button_style and
                "visibility:hidden" not in parent_style and 
                "visibility: hidden" not in parent_style and
                "display:none" not in button_style and
                "display: none" not in button_style and
                button.is_displayed()
            )
        
        print(f"    📊 펼치기 버튼 상태: {'있음' if has_expand_button else '없음'}")
        
        if has_expand_button:
            # 유형 1: 긴 내용 - 펼치기 버튼 클릭해서 모달 열기
            return get_long_highlight_content(driver)
        else:
            # 유형 2: 짧은 내용 - 바로 수집
            return get_short_highlight_content(driver)
            
    except Exception as e:
        print(f"    ❌ 하이라이트 수집 실패: {e}")
        return "정보 없음"

def get_long_highlight_content(driver):
    """유형 1: 긴 하이라이트 - 펼치기 버튼 클릭 후 모달에서 수집"""
    print("    🔽 긴 내용 - 펼치기 버튼 클릭 후 모달 수집")
    
    try:
        # 1. 펼치기 버튼 클릭 (원본 소스 기반 셀렉터)
        expand_button = driver.find_element(By.CSS_SELECTOR, "#highlight .experience-view-more_text")
        driver.execute_script("arguments[0].click();", expand_button)
        
        # 2. 모달 로드 대기 (정확한 원본 셀렉터)
        modal_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.klk-modal-wrapper > div > div.klk-modal-body"))
        )
        
        # 3. 모달이 완전히 표시될 때까지 추가 대기
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".klk-modal-wrapper"))
        )
        
        # 4. 모달 내 전체 내용 수집
        full_content = modal_body.text.strip()
        
        if not full_content:
            raise Exception("모달 내용이 비어있음")
        
        # 5. 모달 닫기 (원본 소스 기반 - 여러 방법 시도)
        try:
            # 방법 1: X 버튼 클릭
            close_button = driver.find_element(By.CSS_SELECTOR, "body > div.klk-modal-wrapper > div > i")
            driver.execute_script("arguments[0].click();", close_button)
            time.sleep(1)
        except:
            try:
                # 방법 2: ESC키로 모달 닫기
                from selenium.webdriver.common.keys import Keys
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(1)
            except:
                # 방법 3: 모달 배경 클릭
                try:
                    modal_wrapper = driver.find_element(By.CSS_SELECTOR, ".klk-modal-wrapper")
                    driver.execute_script("arguments[0].click();", modal_wrapper)
                except:
                    pass  # 모달 닫기 실패해도 계속 진행
        
        print(f"    ✅ 전체 하이라이트 수집 완료 (길이: {len(full_content)}자)")
        return full_content
        
    except Exception as e:
        print(f"    ⚠️ 모달 방식 실패: {e} - 기본 요약으로 fallback")
        # 실패 시 기본 요약이라도 수집
        return get_short_highlight_content(driver)

def get_short_highlight_content(driver):
    """유형 2: 짧은 하이라이트 - 직접 수집 (펼치기 버튼 없음)"""
    print("    📄 짧은 내용 - 직접 수집")
    
    try:
        # 원본 소스 기반 - 우선순위별 셀렉터 시도
        content_selectors = [
            "#highlight .exp-highlights-content",           # 최우선: 전체 하이라이트 내용
            "#highlight .exp-highlights-content-wrap",      # 백업 1: 래핑된 내용 
            "#highlight .klk-markdown",                     # 백업 2: 마크다운 내용
            "#highlight .activity-klk-markdown",            # 백업 3: 액티비티 마크다운
            "#highlight"                                    # 최종: 전체 영역
        ]
        
        for selector in content_selectors:
            try:
                content_element = driver.find_element(By.CSS_SELECTOR, selector)
                content_text = content_element.text.strip()

                if content_text and len(content_text) > 10:
                    # --- 이 부분이 수정되었습니다 ---
                    # 불필요한 "펼치기" 텍스트 제거
                    content_text = content_text.replace("펼치기", "").strip()

                    # 각 줄을 분리하고, 앞뒤 공백을 제거한 후, 다시 줄 바꿈 문자로 합칩니다.
                    # 이렇게 하면 원래의 줄 바꿈은 유지되면서도 가독성이 향상됩니다.
                    lines = [line.strip() for line in content_text.split('\n') if line.strip()]
                    cleaned_content = '\n'.join(lines)
                    # --- 여기까지 수정 ---

                    print(f"    ✅ 짧은 내용 수집 완료 (길이: {len(cleaned_content)}자)")
                    return cleaned_content
            except:
                continue
                
        print("    ⚠️ 하이라이트 내용을 찾을 수 없습니다")
        return "정보 없음"
        
    except Exception as e:
        print(f"    ❌ 짧은 내용 수집 실패: {e}")
        return "정보 없음"

def get_language_info(driver):
    """언어 정보 수집 (원본 코드 기반)"""
    print("  🌐 언어 정보 수집 중...")
    
    if not SELENIUM_AVAILABLE:
        return "한국어 (URL 기반)"
    
    # 원본과 동일한 언어 셀렉터 
    language_selectors = [
        ".language",
        ".guide-language",
        "[data-testid='language']",
        "[class*='language']",
        "[class*='lang']",
        ".languages li",
        ".supported-languages li",
        "[data-testid='languages'] li"
    ]
    
    try:
        for selector in language_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                language = element.text.strip()
                if language and len(language) < 50:
                    print(f"    ✅ 언어: {language}")
                    return language
            except:
                continue
                
    except Exception as e:
        print(f"    ⚠️ 언어 정보 수집 중 오류: {e}")
    
    # 기본값: URL 기반으로 한국어 추정
    print("    ✅ 언어: 한국어 (URL 기반)")
    return "한국어 (URL 기반)"

def get_features(driver):
    """상품 특징 추출 (하이라이트와 구분)"""
    print("  ✨ 상품 특징 추출 중...")
    
    if not SELENIUM_AVAILABLE:
        return "특징 추출 불가"
    
    feature_selectors = [
        ".product-features li",                  # 상품 특징
        ".key-points li",                        # 핵심 포인트
        ".benefits li",                          # 혜택
        ".inclusions li",                        # 포함사항
        ".tags span",                            # 태그
        "[data-testid*='feature']",             # 특징 테스트ID
        ".feature-list li",                      # 특징 리스트
        ".amenities li"                          # 편의시설
    ]
    
    features = []
    
    for selector in feature_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in elements:
                try:
                    feature_text = element.text.strip()
                    if feature_text and 10 < len(feature_text) < 100:  # 적절한 길이의 특징만
                        features.append(feature_text)
                except:
                    continue
                    
        except Exception:
            continue
    
    if features:
        unique_features = list(set(features))[:5]  # 최대 5개까지
        features_str = " | ".join(unique_features)
        print(f"    ✅ 특징: {features_str[:100]}...")
        return features_str
    
    print("    ⚠️ 특징 추출 실패")
    return "특징 정보 없음"

def get_language(driver):
    """KLOOK 언어 정보 수집 (원본 정교한 로직 사용)"""
    print("  🌐 언어 정보 수집 중...")
    
    if not SELENIUM_AVAILABLE:
        return "정보 없음"
    
    try:
        # URL에서 언어 확인 (가장 확실한 방법)
        current_url = driver.current_url
        if "/ko/" in current_url:
            print("    ✅ 언어: 한국어 (URL 기반)")
            return "한국어"
        elif "/en/" in current_url:
            print("    ✅ 언어: 영어 (URL 기반)")
            return "영어"
        elif "/ja/" in current_url:
            print("    ✅ 언어: 일본어 (URL 기반)")
            return "일본어"
        elif "/zh/" in current_url:
            print("    ✅ 언어: 중국어 (URL 기반)")
            return "중국어"
        
        # HTML lang 속성 확인
        try:
            html_element = driver.find_element(By.TAG_NAME, "html")
            lang_attr = html_element.get_attribute("lang")
            if lang_attr:
                if lang_attr.startswith("ko"):
                    print(f"    ✅ 언어: 한국어 (HTML lang: {lang_attr})")
                    return "한국어"
                elif lang_attr.startswith("en"):
                    print(f"    ✅ 언어: 영어 (HTML lang: {lang_attr})")
                    return "영어"
                elif lang_attr.startswith("ja"):
                    print(f"    ✅ 언어: 일본어 (HTML lang: {lang_attr})")
                    return "일본어"
                elif lang_attr.startswith("zh"):
                    print(f"    ✅ 언어: 중국어 (HTML lang: {lang_attr})")
                    return "중국어"
                else:
                    print(f"    ✅ 언어: {lang_attr}")
                    return lang_attr
        except:
            pass
        
        # 페이지 내용 기반 언어 감지 (백업)
        try:
            title_element = driver.find_element(By.TAG_NAME, "title")
            title_text = title_element.text
            
            # 한글이 포함되어 있는지 확인
            korean_chars = sum(1 for char in title_text if '\uAC00' <= char <= '\uD7A3')
            if korean_chars > 0:
                print("    ✅ 언어: 한국어 (내용 기반)")
                return "한국어"
        except:
            pass
        
        print("    ⚠️ 언어 정보를 확인할 수 없습니다")
        return "한국어"  # 기본값
        
    except Exception as e:
        print(f"    ❌ 언어 정보 수집 실패: {e}")
        return "한국어"  # 기본값

# =============================================================================
# 데이터 정제 시스템
# =============================================================================

def clean_price(price_text):
    """가격 텍스트 정제"""
    if not price_text:
        return "가격 정보 없음"
    
    try:
        # 숫자와 기본 기호만 추출
        cleaned = re.sub(r'[^\d,₩KRW원\.]', '', price_text)
        
        # 가격 패턴 찾기
        price_patterns = [
            r'₩([0-9,]+)',
            r'([0-9,]+)원',
            r'KRW\s*([0-9,]+)',
            r'([0-9,]+)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, cleaned)
            if match:
                price_num = match.group(1).replace(',', '')
                if price_num.isdigit() and int(price_num) > 0:
                    return f"₩{int(price_num):,}"
        
        return "가격 정보 없음"
        
    except Exception:
        return "가격 정보 없음"

def clean_rating(rating_text):
    """평점 텍스트 정제"""
    if not rating_text:
        return "평점 정보 없음"
    
    try:
        # 평점 패턴 찾기
        rating_patterns = [
            r'([0-9]\.?[0-9]*)\s*/\s*5',  # x.x/5
            r'([0-9]\.?[0-9]*)\s*/\s*10', # x.x/10
            r'([0-9]\.?[0-9]*)',          # 단순 숫자
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, rating_text)
            if match:
                rating = float(match.group(1))
                if 0 <= rating <= 10:
                    # 10점 만점을 5점 만점으로 변환
                    if rating > 5:
                        rating = rating / 2
                    return f"{rating:.1f}/5"
        
        return "평점 정보 없음"
        
    except Exception:
        return "평점 정보 없음"

def clean_text(text):
    """일반 텍스트 정제"""
    if not text:
        return ""
    
    try:
        # 불필요한 공백 제거
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # HTML 엔티티 디코딩
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }
        
        for entity, char in html_entities.items():
            cleaned = cleaned.replace(entity, char)
        
        return cleaned
        
    except Exception:
        return text

# =============================================================================
# 통합 데이터 추출 시스템
# =============================================================================

def extract_all_product_data(driver, url, rank=None):
    """상품 페이지에서 모든 데이터 추출 (하이라이트, 언어 정보 포함)"""
    print(f"📊 상품 데이터 추출 시작 (순위: {rank})")
    
    try:
        # 페이지 로드 대기
        time.sleep(random.uniform(2, 4))
        
        # 각 데이터 추출 (원본 정교한 기능들 포함)
        product_data = {
            "상품명": clean_text(get_product_name(driver)),
            "가격": get_price(driver),
            "평점": get_rating(driver),
            "리뷰수": get_review_count(driver),
            "카테고리": clean_text(get_categories(driver)),
            "하이라이트": get_highlights(driver),      # 🆕 원본 기능 추가
            "특징": clean_text(get_features(driver)),
            "언어": get_language(driver),                        # 🆕 원본 기능 추가
            "URL": url,
            "순위": rank,
            "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("✅ 상품 데이터 추출 완료")
        return product_data
        
    except Exception as e:
        print(f"❌ 상품 데이터 추출 실패: {e}")
        return {
            "상품명": "데이터 추출 실패",
            "가격": "추출 실패",
            "평점": "추출 실패",
            "리뷰수": "0",
            "카테고리": "기타",
            "하이라이트": "추출 실패",
            "특징": "추출 실패",
            "언어": "한국어",
            "URL": url,
            "순위": rank,
            "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def validate_product_data(product_data):
    """상품 데이터 유효성 검증"""
    required_fields = ["상품명", "가격", "평점", "URL"]
    
    for field in required_fields:
        if not product_data.get(field) or product_data[field] in ["추출 실패", "정보 없음", ""]:
            print(f"⚠️ 필수 필드 누락: {field}")
            return False
    
    print("✅ 상품 데이터 검증 통과")
    return True

print("✅ parsers.py 로드 완료: 데이터 추출 시스템 준비!")