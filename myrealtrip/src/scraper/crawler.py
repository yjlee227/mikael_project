"""
MyRealTrip 메인 크롤링 엔진
- 전체 크롤링 프로세스 통합 관리
- 객체 지향 설계를 통해 재사용성 및 유지보수성 향상
"""

import time
import random
from datetime import datetime

# 리팩토링된 모듈 import
from ..config import CONFIG
from ..utils.file_handler import create_product_data_structure, save_batch_data, get_last_product_number
from .driver_manager import setup_driver, go_to_main_page, find_and_fill_search
from .url_manager import collect_product_urls_from_page, hybrid_is_processed, mark_url_processed_fast
from .parsers import get_product_name, get_price, get_rating, get_review_count, clean_price, clean_rating

class MyRealTripCrawler:
    """MyRealTrip 크롤링을 위한 모든 로직을 캡슐화하는 클래스"""

    def __init__(self, city_name):
        self.city_name = city_name
        self.driver = None
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_processed": 0,
            "success_count": 0,
            "error_count": 0,
            "skipped_count": 0,
            "urls_collected": 0,
        }
        self.stop_flag = False

    def _initialize_driver(self):
        """드라이버를 설정하고 메인 페이지로 이동합니다."""
        try:
            self.driver = setup_driver()
            go_to_main_page(self.driver)
            return find_and_fill_search(self.driver, self.city_name)
        except Exception as e:
            print(f"❌ 드라이버 초기화 실패: {e}")
            return False

    def _collect_urls(self, use_infinite_scroll=True):
        """URL을 수집하고 중복을 필터링합니다."""
        print("🔗 URL 수집 시작...")
        all_urls = collect_product_urls_from_page(self.driver, use_infinite_scroll)
        
        new_urls = []
        for url in all_urls:
            if not hybrid_is_processed(url, self.city_name):
                new_urls.append(url)
        
        self.stats["urls_collected"] = len(new_urls)
        print(f"✅ {len(new_urls)}개의 새로운 URL 수집 완료.")
        return new_urls

    def _crawl_single_product(self, url, product_number):
        """단일 상품 페이지를 크롤링합니다."""
        if self.stop_flag: return None

        print(f"\n🔍 상품 처리 시작 (번호: {product_number}): {url[:70]}...")
        main_window = self.driver.current_window_handle
        self.driver.switch_to.new_window('tab')
        self.driver.get(url)
        time.sleep(random.uniform(3, 5))

        try:
            product_data = create_product_data_structure(self.city_name, product_number)
            product_data["URL"] = url
            product_data["상품명"] = get_product_name(self.driver)
            product_data["가격"] = clean_price(get_price(self.driver))
            product_data["평점"] = clean_rating(get_rating(self.driver))
            product_data["리뷰수"] = get_review_count(self.driver)
            
            # TODO: kkday 규격에 맞게 추가 데이터 추출 로직 구현

            self.stats["success_count"] += 1
            print(f"  ✅ 상품 정보 추출 성공: {product_data['상품명'][:30]}...")
            return product_data
        except Exception as e:
            print(f"  ❌ 상품 정보 추출 실패: {e}")
            self.stats["error_count"] += 1
            return None
        finally:
            self.driver.close()
            self.driver.switch_to.window(main_window)

    def run_crawling(self, max_products=10, use_infinite_scroll=True):
        """전체 크롤링 프로세스를 실행합니다."""
        self.stats["start_time"] = datetime.now()
        print(f"🚀 {self.city_name} 크롤링 시작 (목표: {max_products}개)")

        if not self._initialize_driver():
            return

        urls_to_crawl = self._collect_urls(use_infinite_scroll)
        if not urls_to_crawl:
            print("⚠️ 크롤링할 새로운 URL이 없습니다.")
            self.driver.quit()
            return

        product_number = get_last_product_number(self.city_name) + 1
        results = []

        for i, url in enumerate(urls_to_crawl):
            if i >= max_products:
                print(f"🎯 목표 수량({max_products}개) 달성. 크롤링을 중단합니다.")
                break
            if self.stop_flag:
                print("🛑 정지 신호 감지. 크롤링을 중단합니다.")
                break

            data = self._crawl_single_product(url, product_number + i)
            if data:
                results.append(data)
                mark_url_processed_fast(url, self.city_name, product_number + i)
            
            self.stats["total_processed"] += 1

        if results:
            save_batch_data(results, self.city_name)

        self.stats["end_time"] = datetime.now()
        print("🎉 크롤링 세션 완료.")
        self._print_stats()
        self.driver.quit()

    def _print_stats(self):
        duration = self.stats["end_time"] - self.stats["start_time"]
        print("\n--- 최종 통계 ---")
        print(f"소요 시간: {duration}")
        print(f"총 처리 시도: {self.stats['total_processed']}")
        print(f"성공: {self.stats['success_count']}")
        print(f"실패: {self.stats['error_count']}")
        print("---------------")

print("✅ crawler.py 생성 완료: MyRealTripCrawler 클래스 정의 완료!")
