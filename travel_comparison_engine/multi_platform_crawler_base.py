"""
🌐 다중 플랫폼 크롤러 기본 구조
- KKday, GetYourGuide, MyRealTrip 크롤러 기본 틀
- 통합 스키마 호환성 보장
- 플랫폼별 특화 로직 분리

작성일: 2024-08-24
기반: 통합 스키마 & KLOOK 크롤러 구조
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import hashlib
from datetime import datetime
import re


class BasePlatformCrawler(ABC):
    """모든 플랫폼 크롤러의 기본 클래스"""
    
    def __init__(self, driver: webdriver.Chrome, wait_timeout: int = 10):
        """
        기본 크롤러 초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            wait_timeout: 대기 시간 (초)
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        self.platform_name = self.get_platform_name()
        self.base_selectors = self.get_platform_selectors()
        
    @abstractmethod
    def get_platform_name(self) -> str:
        """플랫폼 이름 반환"""
        pass
    
    @abstractmethod
    def get_platform_selectors(self) -> Dict[str, List[str]]:
        """플랫폼별 CSS/XPath 셀렉터 정의"""
        pass
    
    @abstractmethod
    def get_search_url(self, city: str, **kwargs) -> str:
        """검색 URL 생성"""
        pass
    
    @abstractmethod
    def extract_product_list(self) -> List[Dict[str, Any]]:
        """상품 목록 추출"""
        pass
    
    @abstractmethod
    def extract_product_details(self, product_url: str) -> Dict[str, Any]:
        """개별 상품 상세 정보 추출"""
        pass
    
    def normalize_to_unified_schema(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """원시 데이터를 통합 스키마로 변환"""
        
        # 상품 해시 생성
        core_fields = [
            str(raw_data.get('title', '')),
            str(raw_data.get('url', '')),
            str(raw_data.get('price', ''))
        ]
        product_hash = hashlib.sha1(''.join(core_fields).encode()).hexdigest()
        
        return {
            # ⭐ 필수 식별 정보
            "provider": self.platform_name,
            "provider_product_id": self.extract_product_id(raw_data.get('url', '')),
            "fetch_ts": datetime.utcnow().isoformat() + "Z",
            "fx_rate": None,  # TODO: 환율 API
            
            # ⭐ 필수 목적지/분류  
            "destination_city": raw_data.get('city', ''),
            "country": raw_data.get('country', ''),
            "theme_tags": json.dumps(raw_data.get('themes', []), ensure_ascii=False),
            
            # ⭐ 필수 상품 정보
            "title": raw_data.get('title', ''),
            "subtitle": raw_data.get('subtitle', ''),
            "supplier_name": raw_data.get('supplier', ''),
            "duration_hours": self.parse_duration(raw_data.get('duration', '')),
            "pickup": 1 if raw_data.get('pickup', False) else 0,
            "language": json.dumps(raw_data.get('languages', ['en']), ensure_ascii=False),
            
            # 포함/불포함
            "included": json.dumps(raw_data.get('included', []), ensure_ascii=False),
            "excluded": json.dumps(raw_data.get('excluded', []), ensure_ascii=False),
            "meeting_point": raw_data.get('meeting_point', ''),
            
            # ⭐ 필수 가격 정보
            "price_value": self.parse_price(raw_data.get('price', '')),
            "price_currency": self.normalize_currency(raw_data.get('currency', 'USD')),
            "option_list": json.dumps(raw_data.get('options', []), ensure_ascii=False),
            "price_basis": raw_data.get('price_basis', 'adult'),
            
            # 평점/리뷰
            "rating_value": self.normalize_rating(raw_data.get('rating', '')),
            "rating_count": raw_data.get('review_count', 0),
            
            # 취소/환불 정책
            "cancel_policy": json.dumps(raw_data.get('cancel_policy', {}), ensure_ascii=False),
            
            # 가용성
            "availability_calendar": json.dumps(raw_data.get('availability', []), ensure_ascii=False),
            
            # 노출/순위
            "rank_position": raw_data.get('rank', 999),
            
            # ⭐ 필수 링크/이미지
            "landing_url": raw_data.get('url', ''),
            "affiliate_url": self.generate_affiliate_url(raw_data.get('url', '')),
            "images": json.dumps(raw_data.get('images', []), ensure_ascii=False),
            
            # 메타데이터
            "product_hash": product_hash,
            "data_source_meta": json.dumps({
                "crawler_version": "1.0.0",
                "platform": self.platform_name,
                "raw_fields": list(raw_data.keys())
            }, ensure_ascii=False)
        }
    
    # 공통 유틸리티 함수들
    def extract_product_id(self, url: str) -> str:
        """URL에서 상품 ID 추출 (플랫폼별 오버라이드 가능)"""
        try:
            # 일반적인 패턴 시도
            match = re.search(r'/(\d+)', url)
            if match:
                return match.group(1)
            return hashlib.md5(url.encode()).hexdigest()[:12]
        except:
            return hashlib.md5(str(url).encode()).hexdigest()[:12]
    
    def parse_duration(self, duration_str: str) -> Optional[float]:
        """소요시간 파싱"""
        if not duration_str:
            return None
        try:
            duration_str = str(duration_str).lower()
            if 'hour' in duration_str or '시간' in duration_str:
                match = re.search(r'(\d+)', duration_str)
                return float(match.group(1)) if match else None
            elif 'day' in duration_str or '일' in duration_str:
                match = re.search(r'(\d+)', duration_str)
                return float(match.group(1)) * 24 if match else None
            return None
        except:
            return None
    
    def parse_price(self, price_str: str) -> float:
        """가격 파싱"""
        try:
            price_clean = re.sub(r'[^\d.]', '', str(price_str))
            return float(price_clean) if price_clean else 0.0
        except:
            return 0.0
    
    def normalize_currency(self, currency: str) -> str:
        """통화 정규화"""
        currency_map = {
            "$": "USD", "dollar": "USD", "usd": "USD",
            "€": "EUR", "euro": "EUR", "eur": "EUR", 
            "£": "GBP", "pound": "GBP", "gbp": "GBP",
            "¥": "JPY", "yen": "JPY", "jpy": "JPY",
            "₩": "KRW", "won": "KRW", "krw": "KRW"
        }
        return currency_map.get(currency.lower(), currency.upper())
    
    def normalize_rating(self, rating_str: str) -> Optional[float]:
        """평점을 0~5 스케일로 정규화"""
        try:
            rating = float(str(rating_str).replace(',', ''))
            if 0 <= rating <= 5:
                return round(rating, 2)
            elif 5 < rating <= 10:
                return round(rating / 2, 2)
            elif 10 < rating <= 100:
                return round(rating / 20, 2)
            return None
        except:
            return None
    
    def generate_affiliate_url(self, original_url: str) -> Optional[str]:
        """제휴 URL 생성 (플랫폼별 오버라이드)"""
        return None  # 기본적으로 None, 각 플랫폼에서 구현


class KKdayCrawler(BasePlatformCrawler):
    """KKday 플랫폼 크롤러"""
    
    def get_platform_name(self) -> str:
        return "KKday"
    
    def get_platform_selectors(self) -> Dict[str, List[str]]:
        return {
            "product_cards": [
                ".product-card",
                "[data-testid='product-card']",
                ".product-item"
            ],
            "product_title": [
                ".product-name", 
                ".card-title",
                "h3", "h4"
            ],
            "product_price": [
                ".price",
                ".product-price", 
                "[data-testid='price']"
            ],
            "product_rating": [
                ".rating",
                ".score",
                "[data-testid='rating']"
            ],
            "product_link": [
                "a[href*='/product/']",
                ".product-link"
            ],
            "next_page": [
                ".pagination-next",
                "[aria-label='Next']",
                ".next-page"
            ]
        }
    
    def get_search_url(self, city: str, **kwargs) -> str:
        """KKday 검색 URL 생성"""
        base_url = "https://www.kkday.com"
        # KKday는 도시별 URL 구조가 다를 수 있음
        return f"{base_url}/ko/product/productlist/{city}"
    
    def extract_product_list(self) -> List[Dict[str, Any]]:
        """KKday 상품 목록 추출"""
        products = []
        
        try:
            # 상품 카드 요소들 찾기
            card_selectors = self.base_selectors["product_cards"]
            product_cards = []
            
            for selector in card_selectors:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        product_cards = cards
                        break
                except:
                    continue
            
            for i, card in enumerate(product_cards[:20], 1):  # 상위 20개만
                try:
                    product_data = {
                        'rank': i,
                        'title': self._extract_text_from_card(card, self.base_selectors["product_title"]),
                        'price': self._extract_text_from_card(card, self.base_selectors["product_price"]),
                        'rating': self._extract_text_from_card(card, self.base_selectors["product_rating"]),
                        'url': self._extract_link_from_card(card),
                        'platform': self.platform_name
                    }
                    products.append(product_data)
                except Exception as e:
                    print(f"⚠️ KKday 상품 {i} 추출 실패: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ KKday 상품 목록 추출 실패: {e}")
        
        return products
    
    def extract_product_details(self, product_url: str) -> Dict[str, Any]:
        """KKday 상품 상세 정보 추출"""
        details = {}
        
        try:
            self.driver.get(product_url)
            time.sleep(2)
            
            # TODO: KKday 상세 페이지 정보 추출 로직
            details = {
                'url': product_url,
                'title': self._safe_extract(".product-title", "h1"),
                'subtitle': self._safe_extract(".product-subtitle"),
                'price': self._safe_extract(".price-current", ".price"),
                'currency': 'USD',  # KKday 기본 통화 (지역에 따라 다름)
                'rating': self._safe_extract(".rating-score"),
                'review_count': self._safe_extract(".review-count"),
                'duration': self._safe_extract(".duration"),
                'included': [],  # TODO: 포함항목 파싱
                'excluded': [],  # TODO: 불포함항목 파싱
                'images': self._extract_images(),
                'supplier': self._safe_extract(".supplier-name"),
                'meeting_point': self._safe_extract(".meeting-point")
            }
            
        except Exception as e:
            print(f"❌ KKday 상세 정보 추출 실패: {e}")
        
        return details
    
    def _extract_text_from_card(self, card, selectors: List[str]) -> str:
        """카드에서 텍스트 추출"""
        for selector in selectors:
            try:
                element = card.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
            except:
                continue
        return ""
    
    def _extract_link_from_card(self, card) -> str:
        """카드에서 링크 추출"""
        try:
            link = card.find_element(By.CSS_SELECTOR, "a")
            href = link.get_attribute("href")
            if href and not href.startswith("http"):
                href = f"https://www.kkday.com{href}"
            return href
        except:
            return ""
    
    def _safe_extract(self, *selectors) -> str:
        """안전한 텍스트 추출"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
            except:
                continue
        return ""
    
    def _extract_images(self) -> List[str]:
        """이미지 URL 추출"""
        images = []
        try:
            img_elements = self.driver.find_elements(By.CSS_SELECTOR, ".product-images img, .gallery img")
            for img in img_elements[:5]:  # 상위 5개만
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src:
                    images.append(src)
        except:
            pass
        return images


class GetYourGuideCrawler(BasePlatformCrawler):
    """GetYourGuide 플랫폼 크롤러"""
    
    def get_platform_name(self) -> str:
        return "GetYourGuide"
    
    def get_platform_selectors(self) -> Dict[str, List[str]]:
        return {
            "product_cards": [
                "[data-testid='activity-card']",
                ".activity-card",
                ".product-card"
            ],
            "product_title": [
                "[data-testid='activity-card-title']",
                ".activity-title",
                "h3"
            ],
            "product_price": [
                "[data-testid='activity-card-price']", 
                ".price-from",
                ".price"
            ],
            "product_rating": [
                "[data-testid='activity-card-rating']",
                ".rating"
            ],
            "next_page": [
                "[aria-label='Go to next page']",
                ".pagination-next"
            ]
        }
    
    def get_search_url(self, city: str, **kwargs) -> str:
        """GetYourGuide 검색 URL 생성"""
        return f"https://www.getyourguide.com/s/?q={city}&sort=popularity"
    
    def extract_product_list(self) -> List[Dict[str, Any]]:
        """GetYourGuide 상품 목록 추출 (KKday와 유사하지만 셀렉터 다름)"""
        # KKday와 유사한 구조지만 GetYourGuide 특화 셀렉터 사용
        # TODO: 구체적인 구현
        return []
    
    def extract_product_details(self, product_url: str) -> Dict[str, Any]:
        """GetYourGuide 상품 상세 정보 추출"""
        # TODO: GetYourGuide 특화 구현
        return {}


class MyRealTripCrawler(BasePlatformCrawler):
    """MyRealTrip 플랫폼 크롤러 (한국어 특화)"""
    
    def get_platform_name(self) -> str:
        return "MyRealTrip"
    
    def get_platform_selectors(self) -> Dict[str, List[str]]:
        return {
            "product_cards": [
                ".product-item",
                ".tour-card", 
                "[data-testid='product']"
            ],
            "product_title": [
                ".tour-name",
                ".product-title",
                "h3", "h4"
            ],
            "product_price": [
                ".price-info",
                ".tour-price",
                ".price"
            ],
            "product_rating": [
                ".rating",
                ".review-score"
            ],
            "next_page": [
                ".btn-next",
                ".pagination-next",
                "[aria-label='다음']"
            ]
        }
    
    def get_search_url(self, city: str, **kwargs) -> str:
        """MyRealTrip 검색 URL 생성 (한국어)"""
        return f"https://www.myrealtrip.com/search?keyword={city}&sort=popular"
    
    def extract_product_list(self) -> List[Dict[str, Any]]:
        """MyRealTrip 상품 목록 추출 (한국어 특화)"""
        # TODO: MyRealTrip 특화 구현 (한국어 처리 포함)
        return []
    
    def extract_product_details(self, product_url: str) -> Dict[str, Any]:
        """MyRealTrip 상품 상세 정보 추출"""
        # TODO: MyRealTrip 특화 구현
        return {}


class MultiPlatformCrawlerManager:
    """다중 플랫폼 크롤러 통합 관리자"""
    
    def __init__(self, driver: webdriver.Chrome):
        """
        다중 플랫폼 크롤러 매니저 초기화
        
        Args:
            driver: 공유 WebDriver 인스턴스
        """
        self.driver = driver
        self.crawlers = {
            "Klook": None,  # 기존 KLOOK 크롤러 연동
            "KKday": KKdayCrawler(driver),
            "GetYourGuide": GetYourGuideCrawler(driver),
            "MyRealTrip": MyRealTripCrawler(driver)
        }
    
    def crawl_all_platforms(self, city: str, max_products_per_platform: int = 20) -> Dict[str, List[Dict]]:
        """모든 플랫폼에서 상품 수집"""
        all_results = {}
        
        for platform_name, crawler in self.crawlers.items():
            if crawler is None:
                continue
                
            try:
                print(f"🔄 {platform_name} 크롤링 시작...")
                
                # 검색 페이지로 이동
                search_url = crawler.get_search_url(city)
                self.driver.get(search_url)
                time.sleep(3)
                
                # 상품 목록 추출
                products = crawler.extract_product_list()
                
                # 통합 스키마로 변환
                unified_products = []
                for product in products[:max_products_per_platform]:
                    try:
                        unified_data = crawler.normalize_to_unified_schema(product)
                        unified_products.append(unified_data)
                    except Exception as e:
                        print(f"   ⚠️ {platform_name} 상품 변환 실패: {e}")
                        continue
                
                all_results[platform_name] = unified_products
                print(f"   ✅ {platform_name}: {len(unified_products)}개 상품 수집 완료")
                
            except Exception as e:
                print(f"   ❌ {platform_name} 크롤링 실패: {e}")
                all_results[platform_name] = []
        
        return all_results
    
    def get_crawler(self, platform: str) -> Optional[BasePlatformCrawler]:
        """특정 플랫폼 크롤러 반환"""
        return self.crawlers.get(platform)


def create_multi_platform_manager(driver: webdriver.Chrome) -> MultiPlatformCrawlerManager:
    """다중 플랫폼 매니저 생성 편의 함수"""
    return MultiPlatformCrawlerManager(driver)


if __name__ == "__main__":
    print("🌐 다중 플랫폼 크롤러 기본 구조")
    print("   ✅ 추상화된 기본 크롤러 클래스")
    print("   ✅ KKday 크롤러 기본 구현")
    print("   ✅ GetYourGuide 크롤러 틀")
    print("   ✅ MyRealTrip 크롤러 틀") 
    print("   ✅ 통합 스키마 자동 변환")
    print("   ✅ 다중 플랫폼 매니저")