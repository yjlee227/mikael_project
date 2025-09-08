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
from ..utils.location_learning import LocationLearningSystem

# 학습 시스템 인스턴스는 함수 내에서 동적으로 생성

if SELENIUM_AVAILABLE:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# =============================================================================
# KKday 유연한 다중 셀렉터 전략 시스템
# =============================================================================

KKDAY_SELECTORS = {
    "상품명": [
        "#productDetailApp .product-title__name",     # 상세페이지 최우선
        "#productDetailApp h1.product-title__name",   # 상세페이지 백업
        ".product-card h3",                           # 목록페이지용
        ".product-card__title",                       # 목록페이지 백업
        "h1",                                         # 범용 백업
        "//h1[contains(@class, 'product-title')]"     # XPath 백업
    ],

    "가격": [
        "#productDetailApp .kk-price-local__normal",  # 상세페이지 최우선
        ".product-card .kk-price-local__normal",      # 목록페이지용
        ".product-card .price-text",                  # 목록페이지 백업
        ".product-card .price",                       # 목록페이지 백업2
        ".kk-price-local__normal",                    # 범용
        ".price",                                     # 범용 백업
        "[class*='price']"                            # 클래스 포함 백업
    ],

    "평점": [
        ".product-score span:first-child",            # 상세페이지 최우선
        "#productDetailApp .product-score span:first-child", # 컨테이너 포함
        ".product-card__info-score",                  # 목록페이지용
        ".product-score__count",                      # 대안 셀렉터
        "[class*='rating']",                          # 평점 관련 클래스
        "[class*='score']"                            # 점수 관련 클래스
    ]
}

def try_selectors_with_fallback(driver, selector_key, validation_func=None):
    """
    중앙화된 셀렉터 매핑을 사용하여 fallback 전략으로 요소 찾기
    Args:
        driver: Selenium WebDriver 인스턴스
        selector_key: KKDAY_SELECTORS의 키 (예: "상품명", "가격")
        validation_func: 찾은 텍스트 검증 함수 (선택적)
    Returns:
        str: 추출된 텍스트 또는 None
    """
    if not SELENIUM_AVAILABLE:
        return None
    
    selectors = KKDAY_SELECTORS.get(selector_key, [])
    
    # 동적 타임아웃 설정 (최적화된 값)
    base_timeout = CONFIG.get("WAIT_TIMEOUT", 5)  # 기본 5초로 단축
    
    for i, selector in enumerate(selectors):
        # 시도 횟수에 따른 동적 타임아웃 (첫 번째: 5초, 나머지: 2-3초)
        current_timeout = base_timeout if i == 0 else max(2, base_timeout // 2)
        
        try:
            print(f"    🔍 시도 중 ({i+1}/{len(selectors)}): {selector} (타임아웃: {current_timeout}초)")
            
            # 명시적 대기 사용
            wait = WebDriverWait(driver, current_timeout)
            try:
                # XPath와 CSS 셀렉터 구분 + 명시적 대기
                if selector.startswith("//"):
                    wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
            except TimeoutException:
                print(f"    ⏰ 타임아웃 ({current_timeout}초): {selector}")
                continue  # 다음 셀렉터로 넘어감
            except NoSuchElementException:
                print(f"    🔍 요소 없음: {selector}")
                continue
            
            for element in elements:
                retry_count = 0
                max_retries = 2
                while retry_count <= max_retries:
                    try:
                        text = element.text.strip()
                        if text:
                            # 검증 함수가 있으면 적용
                            if validation_func is None or validation_func(text):
                                print(f"    ✅ 성공 ({i+1}/{len(selectors)}): {text[:50]}...")
                                return text
                        break  # 성공하면 재시도 루프 종료
                    except StaleElementReferenceException:
                        retry_count += 1
                        if retry_count <= max_retries:
                            print(f"    🔄 StaleElement 재시도 ({retry_count}/{max_retries})")
                            time.sleep(0.5)  # 0.5초 대기 후 재시도
                            try:
                                # 요소 다시 찾기
                                if selector.startswith("//"):
                                    fresh_elements = driver.find_elements(By.XPATH, selector)
                                else:
                                    fresh_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                if fresh_elements:
                                    element = fresh_elements[0]  # 첫 번째 요소 사용
                            except:
                                break
                        else:
                            print(f"    ❌ StaleElement 최대 재시도 초과")
                            break
                    except Exception:
                        break
                        
        except Exception as e:
            print(f"    ❌ 실패 ({i+1}/{len(selectors)}): {selector} - {e}")
            continue
    
    print(f"    ⚠️ 모든 셀렉터 실패: {selector_key}")
    return None

# 필요한 import문 (사용시 추가)
# import time
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# =============================================================================
# 기본 데이터 추출 시스템
# =============================================================================

def get_product_name(driver):
    """상품명 추출 (중앙화된 다중 셀렉터 전략 사용)"""
    print("  📝 상품명 추출 중...")
    if not SELENIUM_AVAILABLE:
        return "상품명 추출 불가"
    
    # 상품명 검증 함수
    def validate_product_name(text):
        return text and len(text.strip()) > 3 and len(text.strip()) < 200
    
    # 중앙화된 셀렉터 시스템 사용
    product_name = try_selectors_with_fallback(driver, "상품명", validate_product_name)
    
    if product_name:
        print(f"    ✅ 상품명: {product_name[:50]}...")
        return product_name
    
    print("    ⚠️ 상품명 추출 실패")
    return "상품명 없음"

def get_price(driver):
    """가격 정보 추출 (중앙화된 다중 셀렉터 전략 사용)"""
    print("  💰 가격 추출 중...")
    if not SELENIUM_AVAILABLE:
        return "가격 추출 불가"
    
    # 가격 검증 함수
    def validate_price(text):
        return text and ('₩' in text or 'KRW' in text or '원' in text or 
                        text.replace(',', '').replace('.', '').isdigit())
    
    # 중앙화된 셀렉터 시스템 사용
    price_text = try_selectors_with_fallback(driver, "가격", validate_price)
    
    if price_text:
        cleaned_price = clean_price(price_text)
        if cleaned_price != "가격 정보 없음":
            print(f"    ✅ 가격: {cleaned_price}")
            return cleaned_price
    
    print("    ⚠️ 가격 추출 실패")
    return "가격 정보 없음"

def get_rating(driver):
    """평점 정보 추출 (중앙화된 다중 셀렉터 전략 사용)"""
    print("  ⭐ 평점 추출 중...")
    if not SELENIUM_AVAILABLE:
        return "평점 추출 불가"
    
    # 평점 검증 함수
    def validate_rating(text):
        return text and (text.replace('.', '').isdigit() or '/' in text)
    
    # 중앙화된 셀렉터 시스템 사용
    rating_text = try_selectors_with_fallback(driver, "평점", validate_rating)
    
    if rating_text:
        cleaned_rating = clean_rating(rating_text)
        if cleaned_rating != "평점 정보 없음":
            print(f"    ✅ 평점: {cleaned_rating}")
            return cleaned_rating
    
    print("    ⚠️ 평점 추출 실패")
    return "평점 정보 없음"


def get_review_count(driver):
    """리뷰 수 추출 (개별 셀렉터 방식)"""
    print("  💬 리뷰 수 추출 중...")
    if not SELENIUM_AVAILABLE:
        return "리뷰 수 추출 불가"
    
    # KKday 전용 리뷰 수 셀렉터들
    review_selectors = [
        ("css", ".product-card__info-number"),               # KKday 최우선 (200) 형태
        ("css", ".product-score__count"),                    # KKday 백업
        ("css", "#productDetailApp .product-score__count"), # 상세페이지용
        ("css", "[class*='review'][class*='count']"),        # 리뷰 카운트
        ("css", ".review-count"),                            # 범용
        ("css", ".reviews-count"),                           # 복수형
        ("css", "[class*='rating'] .count"),                 # 평점 내 카운트
        ("css", ".comment-count")                            # 댓글 수
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
    """카테고리 정보 추출 (개별 셀렉터 방식)"""
    print("  🏷️ 카테고리 추출 중...")
    if not SELENIUM_AVAILABLE:
        return "카테고리 추출 불가"
    
    # KKday 전용 카테고리 셀렉터들
    category_selectors = [
        ".product-location__text",                    # KKday 위치태그 최우선
        ".breadcrumb li a",                           # KKday breadcrumb
        "[class*='breadcrumb'] span",                 # breadcrumb 백업
        ".breadcrumb a",                              # breadcrumb 링크
        ".category-tag",                              # 카테고리 태그
        ".tags span",                                 # 일반 태그
        "[class*='category'] span",                   # 카테고리 클래스
        "[data-testid*='category']",                  # 테스트ID
        ".labels span"                                # 라벨
    ]
    
    categories = []
    for selector in category_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                try:
                    category_text = element.text.strip()
                    if category_text and len(category_text) < 50:  # 너무 긴 텍스트는 제외
                        if category_text not in categories:  # 중복 제거
                            categories.append(category_text)
                except:
                    continue
        except Exception:
            continue
    
    if categories:
        unique_categories = categories[:3]  # 최대 3개까지
        category_str = " > ".join(unique_categories)
        print(f"    ✅ 카테고리: {category_str}")
        return category_str
    
    print("    ⚠️ 카테고리 추출 실패")
    return "기타"

def get_highlights(driver):
    """KKday 하이라이트 정보 수집"""
    print("  ✨ 하이라이트 정보 수집 중...")
    if not SELENIUM_AVAILABLE:
        return "정보 없음"
    try:
        # KKday 하이라이트 섹션 확인
        highlight_selectors = [
            "#product-info-sec div p",              # KKday 메인 설명문
            "#product-info-sec ul li",              # KKday 하이라이트 리스트
            ".info-sec-collapsable div",            # KKday 접힌 섹션
            ".package-desc ul li",                  # 옵션별 특징
            ".critical-info-text",                  # 주요 특징
            "#product-info-sec",                    # 전체 섹션
        ]
        for selector in highlight_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # 여러 요소의 텍스트를 수집
                    highlights_list = []
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 10:
                            highlights_list.append(text)
                    if highlights_list:
                        # 중복 제거 및 정리
                        unique_highlights = list(set(highlights_list))
                        combined_highlights = '\n'.join(unique_highlights[:5])  # 최대 5개
                        print(f"    ✅ 하이라이트 수집 완료 (길이: {len(combined_highlights)}자)")
                        return combined_highlights
            except Exception:
                continue
        print("    ⚠️ 하이라이트 정보를 찾을 수 없습니다")
        return "정보 없음"
    except Exception as e:
        print(f"    ❌ 하이라이트 수집 실패: {e}")
        return "정보 없음"

def get_features(driver):
    """상품 특징 추출 (하이라이트와 구분)"""
    print("  ✨ 상품 특징 추출 중...")
    
    if not SELENIUM_AVAILABLE:
        return "특징 추출 불가"
    
    feature_selectors = [
        ".package-desc ul li",                   # KKday 옵션별 특징 (최우선)
        ".critical-info-text",                   # KKday 주요 특징
        ".kk-icon-with-text__text",              # KKday 아이콘 특징
        ".product-features li",                  # 상품 특징
        ".key-points li",                        # 핵심 포인트
        ".benefits li",                          # 혜택
        ".inclusions li",                        # 포함사항
        ".tags span",                            # 태그
        "[data-testid*='feature']",              # 특징 테스트ID
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

def get_activity_attributes(driver):
    """KKday 언어, 투어형태, 미팅방식, 소요시간을 한번에 수집"""
    print("  활동 속성 정보 수집 중...")
    if not SELENIUM_AVAILABLE:
        return {"언어": "", "투어형태": "", "미팅방식": "", "소요시간": ""}
    attributes = {
        "언어": "",
        "투어형태": "",
        "미팅방식": "",
        "소요시간": ""
    }
    try:
        # KKday 다중 셀렉터 전략
        selectors_to_try = [
            ".kk-icon-with-text__text",                    # 아이콘 포함 특징
            ".info-table td",                              # 정보 테이블
            ".critical-info span",                         # 주요 정보
            "#productDetailApp .kk-icon-with-text__text",  # 컨테이너 포함
        ]
        all_elements = []
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                all_elements.extend(elements)
            except Exception:
                continue
        for element in all_elements:
            try:
                text = element.text.strip()
                if not text:
                    continue
                # 언어 분류 (기존 로직 유지)
                language_keywords = [
                    '한국어', '영어', '중국어', '일본어', '태국어', '스페인어',
                    '러시아어', '독일어', '프랑스어', '폴란드어', '네덜란드어',
                    '이탈리아어', '포르투갈리어', '베트남어', '인도네시아어'
                ]
                if any(keyword in text for keyword in language_keywords):
                    attributes["언어"] = text
                    print(f"    투어 언어: {text}")
                    continue
                # 소요시간 분류 (기존 로직 유지)
                if (('소요' in text or '일정' in text or '총' in text) and '시간' in text) or ('일' in text and any(c.isdigit() for c in text)):
                    attributes["소요시간"] = text
                    print(f"    소요시간: {text}")
                    continue
                # 투어형태 분류 (KKday용 키워드 추가)
                tour_type_keywords = ['조인', '그룹', '프라이빗', '개별', '셔틀', '투어']
                if any(keyword in text for keyword in tour_type_keywords):
                    attributes["투어형태"] = text
                    print(f"    투어형태: {text}")
                    continue
                # 미팅방식 분류 (KKday용 키워드 추가)
                meeting_keywords = ['미팅', '픽업', '집합', '만남', '바우처', '현장', '전자']
                if any(keyword in text for keyword in meeting_keywords):
                    attributes["미팅방식"] = text
                    print(f"    미팅방식: {text}")
                    continue
            except Exception:
                continue
        return attributes
    except Exception as e:
        print(f"    활동 속성 수집 실패: {e}")
        return attributes

def get_location_tags(city_name, product_name, highlights):
    """자동 학습 시스템을 통해 위치 태그 추출"""
    print("  📍 위치 태그 추출 및 학습 중...")

    if not SELENIUM_AVAILABLE:
        return "위치 태그 추출 불가"

    # 상품명과 하이라이트 텍스트를 합쳐서 분석
    text_to_learn = f"{product_name} {highlights}"

    try:
        # 도시별 학습 시스템 인스턴스 생성
        learning_system = LocationLearningSystem(city_name=city_name)
        
        # 학습 시스템을 통해 태그 가져오기
        tags = learning_system.get_location_tags(city_name, text_to_learn)

        if tags:
            tag_str = ", ".join(tags)
            print(f"    ✅ 추출된 위치 태그: {tag_str}")
            return tag_str
        else:
            print("    ℹ️ 추출된 위치 태그 없음")
            return ""
    except Exception as e:
        print(f"    ⚠️ 위치 태그 추출 실패: {e}")
        return ""
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

def extract_all_product_data(driver, url, rank=None, city_name=None):
    """상품 페이지에서 모든 데이터 추출 (안정화 버전)"""
    print(f"상품 데이터 추출 시작 (순위: {rank})")
    try:
        # 페이지 로드 대기
        time.sleep(random.uniform(2, 4))
           
        # 각 데이터 추출
        product_name = clean_text(get_product_name(driver))
        highlights = get_highlights(driver)
        
        # 통합 속성 수집
        activity_attrs = get_activity_attributes(driver)
        
        product_data = {
            "상품명": product_name,
            "가격": get_price(driver),
            "평점": get_rating(driver),
            "리뷰수": get_review_count(driver),
            "카테고리": clean_text(get_categories(driver)),
            "하이라이트": highlights,
            "위치태그": get_location_tags(city_name, product_name, highlights),
            "특징": clean_text(get_features(driver)),
            "언어": activity_attrs["언어"],
            "투어형태": activity_attrs["투어형태"],
            "미팅방식": activity_attrs["미팅방식"],
            "소요시간": activity_attrs["소요시간"],
            "URL": url,
            "순위": rank,
            "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("상품 데이터 추출 완료")
        return product_data
        
    except Exception as e:
        print(f"상품 데이터 추출 실패: {e}")
        return {
            "상품명": "데이터 추출 실패",
            "가격": "추출 실패",
            "평점": "추출 실패",
            "리뷰수": "0",
            "카테고리": "기타",
            "하이라이트": "추출 실패",
            "위치태그": "",
            "특징": "추출 실패",
            "언어": "",
            "투어형태": "",
            "미팅방식": "",
            "소요시간": "",
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