"""
🚀 그룹 10: KLOOK 카테고리 시스템
- 카테고리별 상품 분류 및 관리
- 동적 카테고리 감지 및 매핑
- 카테고리 기반 크롤링 전략
"""

import os
import json
import re
from datetime import datetime
from collections import defaultdict

# 조건부 import
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    print("⚠️ Selenium이 설치되지 않았습니다. 카테고리 시스템 기능이 제한됩니다.")
    SELENIUM_AVAILABLE = False

# config 모듈에서 필요한 함수들 import
from .config import CONFIG, get_city_code, get_city_info

# =============================================================================
# 📂 KLOOK 카테고리 정의 및 매핑
# =============================================================================

KLOOK_CATEGORY_MAPPING = {
    # 한국어 카테고리
    "투어&액티비티": {
        "english": "Tours & Activities",
        "keywords": ["투어", "액티비티", "체험", "관광", "tour", "activity", "experience"],
        "priority": 1,
        "subcategories": ["시티투어", "자연체험", "문화체험", "어드벤처"]
    },
    "티켓&입장권": {
        "english": "Tickets & Admission",
        "keywords": ["티켓", "입장권", "표", "ticket", "admission", "entrance"],
        "priority": 2,
        "subcategories": ["테마파크", "박물관", "전망대", "공연"]
    },
    "교통": {
        "english": "Transportation",
        "keywords": ["교통", "버스", "기차", "지하철", "택시", "transport", "bus", "train"],
        "priority": 3,
        "subcategories": ["공항셔틀", "시티패스", "렌터카", "크루즈"]
    },
    "숙박": {
        "english": "Accommodation",
        "keywords": ["숙박", "호텔", "펜션", "accommodation", "hotel", "stay"],
        "priority": 4,
        "subcategories": ["호텔", "리조트", "펜션", "게스트하우스"]
    },
    "음식&음료": {
        "english": "Food & Drinks",
        "keywords": ["음식", "음료", "레스토랑", "카페", "food", "drink", "restaurant"],
        "priority": 5,
        "subcategories": ["파인다이닝", "로컬푸드", "디저트", "바"]
    },
    "쇼핑": {
        "english": "Shopping",
        "keywords": ["쇼핑", "쇼핑몰", "마켓", "shopping", "market", "mall"],
        "priority": 6,
        "subcategories": ["면세점", "아울렛", "로컬마켓", "전통시장"]
    },
    "스파&웰니스": {
        "english": "Spa & Wellness",
        "keywords": ["스파", "마사지", "웰니스", "사우나", "spa", "massage", "wellness"],
        "priority": 7,
        "subcategories": ["전통스파", "데이스파", "마사지", "찜질방"]
    },
    "기타": {
        "english": "Others",
        "keywords": ["기타", "특별", "이벤트", "others", "special", "event"],
        "priority": 8,
        "subcategories": ["특별이벤트", "시즌상품", "패키지"]
    }
}

CATEGORY_DETECTION_PATTERNS = {
    # URL 기반 패턴
    "url_patterns": {
        "투어&액티비티": [r"tour", r"activity", r"experience", r"sightseeing"],
        "티켓&입장권": [r"ticket", r"admission", r"entrance", r"pass"],
        "교통": [r"transport", r"transfer", r"bus", r"train", r"subway"],
        "숙박": [r"hotel", r"accommodation", r"stay", r"lodge"],
        "음식&음료": [r"food", r"dining", r"restaurant", r"meal"],
        "쇼핑": [r"shopping", r"market", r"mall", r"shop"],
        "스파&웰니스": [r"spa", r"massage", r"wellness", r"relax"]
    },
    
    # 제목 기반 패턴
    "title_patterns": {
        "투어&액티비티": [r"투어", r"체험", r"관광", r"액티비티"],
        "티켓&입장권": [r"티켓", r"입장권", r"패스", r"표"],
        "교통": [r"셔틀", r"버스", r"기차", r"교통"],
        "숙박": [r"호텔", r"숙박", r"펜션", r"리조트"],
        "음식&음료": [r"레스토랑", r"음식", r"디너", r"런치"],
        "쇼핑": [r"쇼핑", r"시장", r"마켓", r"몰"],
        "스파&웰니스": [r"스파", r"마사지", r"사우나", r"온천"]
    }
}

# =============================================================================
# 🔍 카테고리 감지 및 분류 시스템
# =============================================================================

class KlookCategoryDetector:
    """KLOOK 카테고리 감지 시스템"""
    
    def __init__(self):
        self.detected_categories = {}
        self.category_stats = defaultdict(int)
        
    def detect_category_from_url(self, url):
        """URL에서 카테고리 감지"""
        if not url:
            return "기타"
        
        url_lower = url.lower()
        
        for category, patterns in CATEGORY_DETECTION_PATTERNS["url_patterns"].items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return category
        
        return "기타"
    
    def detect_category_from_title(self, title):
        """제목에서 카테고리 감지"""
        if not title:
            return "기타"
        
        title_lower = title.lower()
        
        # 한국어 패턴 우선 검사
        for category, patterns in CATEGORY_DETECTION_PATTERNS["title_patterns"].items():
            for pattern in patterns:
                if re.search(pattern, title_lower):
                    return category
        
        # 영어 패턴 검사
        for category, patterns in CATEGORY_DETECTION_PATTERNS["url_patterns"].items():
            for pattern in patterns:
                if re.search(pattern, title_lower):
                    return category
        
        return "기타"
    
    def detect_category_from_page(self, driver):
        """페이지에서 카테고리 감지"""
        if not SELENIUM_AVAILABLE:
            return "기타"
        
        try:
            # 1. 브레드크럼에서 카테고리 감지
            breadcrumb_category = self._detect_from_breadcrumb(driver)
            if breadcrumb_category != "기타":
                return breadcrumb_category
            
            # 2. 메타데이터에서 카테고리 감지
            meta_category = self._detect_from_metadata(driver)
            if meta_category != "기타":
                return meta_category
            
            # 3. 페이지 제목에서 카테고리 감지
            title = driver.title
            title_category = self.detect_category_from_title(title)
            if title_category != "기타":
                return title_category
            
            # 4. URL에서 카테고리 감지
            current_url = driver.current_url
            url_category = self.detect_category_from_url(current_url)
            return url_category
            
        except Exception as e:
            print(f"⚠️ 페이지 카테고리 감지 실패: {e}")
            return "기타"
    
    def _detect_from_breadcrumb(self, driver):
        """브레드크럼에서 카테고리 감지"""
        breadcrumb_selectors = [
            ".breadcrumb a",
            "[data-testid='breadcrumb'] a",
            ".breadcrumb-item",
            ".navigation-path a"
        ]
        
        for selector in breadcrumb_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text:
                        category = self.detect_category_from_title(text)
                        if category != "기타":
                            return category
            except:
                continue
        
        return "기타"
    
    def _detect_from_metadata(self, driver):
        """메타데이터에서 카테고리 감지"""
        try:
            # 메타태그 확인
            meta_selectors = [
                "meta[name='category']",
                "meta[property='product:category']",
                "meta[name='keywords']"
            ]
            
            for selector in meta_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    content = element.get_attribute("content")
                    if content:
                        category = self.detect_category_from_title(content)
                        if category != "기타":
                            return category
                except:
                    continue
                    
        except:
            pass
        
        return "기타"
    
    def classify_product_data(self, product_data):
        """상품 데이터 분류"""
        if not product_data:
            return "기타"
        
        # 1. URL 기반 분류
        url = product_data.get("URL", "")
        url_category = self.detect_category_from_url(url)
        
        # 2. 제목 기반 분류
        title = product_data.get("상품명", "")
        title_category = self.detect_category_from_title(title)
        
        # 3. 기존 카테고리 정보 확인
        existing_category = product_data.get("카테고리", "")
        if existing_category and existing_category != "기타":
            mapped_category = self._map_to_standard_category(existing_category)
            if mapped_category != "기타":
                return mapped_category
        
        # 우선순위: 제목 > URL
        if title_category != "기타":
            return title_category
        elif url_category != "기타":
            return url_category
        else:
            return "기타"
    
    def _map_to_standard_category(self, category_text):
        """임의 카테고리 텍스트를 표준 카테고리로 매핑"""
        if not category_text:
            return "기타"
        
        category_lower = category_text.lower()
        
        for standard_category, info in KLOOK_CATEGORY_MAPPING.items():
            keywords = info["keywords"]
            for keyword in keywords:
                if keyword in category_lower:
                    return standard_category
        
        return "기타"

# =============================================================================
# 📊 카테고리 통계 및 분석
# =============================================================================

class CategoryAnalyzer:
    """카테고리 분석 시스템"""
    
    def __init__(self):
        self.category_stats = defaultdict(lambda: {
            "count": 0,
            "urls": [],
            "price_range": {"min": float('inf'), "max": 0, "avg": 0},
            "ratings": []
        })
    
    def analyze_city_categories(self, city_name):
        """도시별 카테고리 분석"""
        try:
            from .data_handler import get_csv_stats
            
            csv_stats = get_csv_stats(city_name)
            if not csv_stats.get("exists", False):
                return {"error": "CSV 데이터 없음"}
            
            # CSV 데이터 읽기
            continent, country = get_city_info(city_name)
            
            if city_name in ["마카오", "홍콩", "싱가포르"]:
                csv_path = os.path.join("data", continent, f"klook_{city_name}_products.csv")
            else:
                csv_path = os.path.join("data", continent, country, city_name, f"klook_{city_name}_products.csv")
            
            if not os.path.exists(csv_path):
                return {"error": "CSV 파일 없음"}
            
            # pandas로 데이터 분석
            try:
                import pandas as pd
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                
                # 카테고리 감지기 초기화
                detector = KlookCategoryDetector()
                
                # 각 상품에 대해 카테고리 분류
                categories = []
                for _, row in df.iterrows():
                    product_data = row.to_dict()
                    category = detector.classify_product_data(product_data)
                    categories.append(category)
                    
                    # 통계 업데이트
                    self._update_category_stats(category, product_data)
                
                # 카테고리별 통계 생성
                category_summary = self._generate_category_summary()
                
                return {
                    "city_name": city_name,
                    "total_products": len(df),
                    "category_distribution": dict(pd.Series(categories).value_counts()),
                    "category_details": category_summary,
                    "analysis_time": datetime.now().isoformat()
                }
                
            except ImportError:
                return {"error": "pandas 라이브러리가 필요합니다"}
                
        except Exception as e:
            return {"error": f"분석 실패: {e}"}
    
    def _update_category_stats(self, category, product_data):
        """카테고리 통계 업데이트"""
        stats = self.category_stats[category]
        stats["count"] += 1
        
        # URL 추가
        url = product_data.get("URL", "")
        if url:
            stats["urls"].append(url)
        
        # 가격 분석
        price_text = product_data.get("가격", "")
        if price_text and price_text != "정보 없음":
            try:
                # 가격에서 숫자 추출
                price_numbers = re.findall(r'\d+', price_text.replace(',', ''))
                if price_numbers:
                    price = int(price_numbers[0])
                    stats["price_range"]["min"] = min(stats["price_range"]["min"], price)
                    stats["price_range"]["max"] = max(stats["price_range"]["max"], price)
            except:
                pass
        
        # 평점 분석
        rating = product_data.get("평점", "")
        if rating and rating != "정보 없음":
            try:
                rating_value = float(rating)
                stats["ratings"].append(rating_value)
            except:
                pass
    
    def _generate_category_summary(self):
        """카테고리 요약 생성"""
        summary = {}
        
        for category, stats in self.category_stats.items():
            if stats["count"] > 0:
                # 평균 가격 계산
                if stats["price_range"]["min"] != float('inf'):
                    avg_price = (stats["price_range"]["min"] + stats["price_range"]["max"]) / 2
                    stats["price_range"]["avg"] = avg_price
                else:
                    stats["price_range"] = {"min": 0, "max": 0, "avg": 0}
                
                # 평균 평점 계산
                if stats["ratings"]:
                    avg_rating = sum(stats["ratings"]) / len(stats["ratings"])
                    stats["avg_rating"] = round(avg_rating, 2)
                else:
                    stats["avg_rating"] = 0
                
                # URL은 샘플만 저장 (최대 5개)
                stats["sample_urls"] = stats["urls"][:5]
                del stats["urls"]  # 메모리 절약
                
                summary[category] = stats
        
        return summary

# =============================================================================
# 🎯 카테고리 기반 크롤링 전략
# =============================================================================

def get_category_crawling_strategy(category):
    """카테고리별 크롤링 전략 반환"""
    strategies = {
        "투어&액티비티": {
            "priority": "높음",
            "image_required": True,
            "max_pages": 10,
            "wait_time_multiplier": 1.0,
            "retry_count": 3
        },
        "티켓&입장권": {
            "priority": "높음",
            "image_required": True,
            "max_pages": 8,
            "wait_time_multiplier": 1.0,
            "retry_count": 3
        },
        "교통": {
            "priority": "중간",
            "image_required": False,
            "max_pages": 5,
            "wait_time_multiplier": 0.8,
            "retry_count": 2
        },
        "숙박": {
            "priority": "중간",
            "image_required": True,
            "max_pages": 6,
            "wait_time_multiplier": 1.2,
            "retry_count": 3
        },
        "음식&음료": {
            "priority": "중간",
            "image_required": True,
            "max_pages": 5,
            "wait_time_multiplier": 1.0,
            "retry_count": 2
        },
        "쇼핑": {
            "priority": "낮음",
            "image_required": False,
            "max_pages": 3,
            "wait_time_multiplier": 0.8,
            "retry_count": 2
        },
        "스파&웰니스": {
            "priority": "낮음",
            "image_required": True,
            "max_pages": 3,
            "wait_time_multiplier": 1.0,
            "retry_count": 2
        },
        "기타": {
            "priority": "낮음",
            "image_required": False,
            "max_pages": 2,
            "wait_time_multiplier": 0.8,
            "retry_count": 1
        }
    }
    
    return strategies.get(category, strategies["기타"])

def save_category_analysis(analysis_data, city_name):
    """카테고리 분석 결과 저장"""
    try:
        analysis_dir = "category_analysis"
        os.makedirs(analysis_dir, exist_ok=True)
        
        city_code = get_city_code(city_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{city_code}_category_analysis_{timestamp}.json"
        filepath = os.path.join(analysis_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 카테고리 분석 저장: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 카테고리 분석 저장 실패: {e}")
        return False

def execute_category_analysis_system(city_name):
    """카테고리 분석 시스템 실행"""
    print(f"📂 '{city_name}' 카테고리 분석 시작!")
    print("=" * 60)
    
    # 카테고리 분석 실행
    analyzer = CategoryAnalyzer()
    analysis_result = analyzer.analyze_city_categories(city_name)
    
    if "error" in analysis_result:
        print(f"❌ 분석 실패: {analysis_result['error']}")
        return analysis_result
    
    # 결과 출력
    print(f"🏙️ 도시: {city_name}")
    print(f"📊 총 상품 수: {analysis_result['total_products']}개")
    print(f"\n📂 카테고리별 분포:")
    
    for category, count in analysis_result["category_distribution"].items():
        percentage = (count / analysis_result["total_products"]) * 100
        print(f"   {category}: {count}개 ({percentage:.1f}%)")
    
    # 분석 결과 저장
    save_success = save_category_analysis(analysis_result, city_name)
    
    print(f"\n🎉 카테고리 분석 완료!")
    print(f"💾 결과 저장: {'성공' if save_success else '실패'}")
    
    return analysis_result

print("✅ 그룹 10 완료: KLOOK 카테고리 시스템!")
print("   📂 카테고리 감지:")
print("   - KlookCategoryDetector: 동적 카테고리 감지")
print("   - detect_category_from_url(): URL 기반 분류")
print("   - detect_category_from_title(): 제목 기반 분류")
print("   - detect_category_from_page(): 페이지 기반 분류")
print("   📊 카테고리 분석:")
print("   - CategoryAnalyzer: 카테고리 통계 분석")
print("   - analyze_city_categories(): 도시별 카테고리 분석")
print("   🎯 크롤링 전략:")
print("   - get_category_crawling_strategy(): 카테고리별 최적화 전략")
print("   - execute_category_analysis_system(): 통합 분석 실행")
print("   📂 지원 카테고리: 투어&액티비티, 티켓&입장권, 교통, 숙박, 음식&음료, 쇼핑, 스파&웰니스, 기타")