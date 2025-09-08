"""
메인 크롤링 엔진
- 전체 크롤링 프로세스 통합 관리
- 페이지네이션 및 데이터 수집
- 에러 처리 및 복구 시스템
"""

import time
import random
from datetime import datetime

from ..config import CONFIG, SELENIUM_AVAILABLE
from ..utils.file_handler import create_product_data_structure, save_to_csv_kkday, get_dual_image_urls_kkday, download_and_save_image_kkday, ensure_directory_structure
from .driver_manager import setup_driver, go_to_main_page, find_and_fill_search, click_search_button, handle_popup, smart_scroll_selector
from .url_manager import collect_urls_from_page, get_pagination_urls, is_url_already_processed, mark_url_as_processed
from .parsers import extract_all_product_data, validate_product_data
from .ranking import save_url_with_rank, ranking_manager, get_collected_ranks_summary

if SELENIUM_AVAILABLE:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

# =============================================================================
# 메인 크롤링 클래스
# =============================================================================

class KKdayCrawler:
    """KKday 크롤링 통합 시스템"""
    
    def __init__(self, city_name="서울"):
        self.city_name = city_name
        self.driver = None
        self.stats = {
            "start_time": None,
            "end_time": None,
            "total_processed": 0,
            "success_count": 0,
            "error_count": 0,
            "skip_count": 0,
            "urls_collected": 0,
            "current_rank": 0
        }
        
    def initialize(self):
        """크롤러 초기화"""
        print(f"🚀 KKday 크롤러 초기화: {self.city_name}")
        
        try:
            # 디렉토리 구조 확보
            ensure_directory_structure(self.city_name)
            
            # 드라이버 설정
            self.driver = setup_driver()
            if not self.driver:
                raise Exception("드라이버 초기화 실패")
            
            # 메인 페이지 이동 및 검색
            if not go_to_main_page(self.driver):
                raise Exception("메인 페이지 이동 실패")
            
            handle_popup(self.driver)
            
            search_input = find_and_fill_search(self.driver, self.city_name)
            if not search_input:
                raise Exception("검색창 입력 실패")
            
            if not click_search_button(self.driver):
                raise Exception("검색 실행 실패")
            
            self.stats["start_time"] = datetime.now()
            print("✅ 크롤러 초기화 완료")
            return True
            
        except Exception as e:
            print(f"❌ 크롤러 초기화 실패: {e}")
            if self.driver:
                # self.driver.quit() - 제거됨: 브라우저 열어두기
                pass
            return False
    
    def collect_urls(self, max_pages=3):
        """URL 수집"""
        print(f"🔗 URL 수집 시작 (최대 {max_pages}페이지)")
        
        try:
            urls = get_pagination_urls(self.driver, max_pages)
            
            # 미처리 URL 필터링
            unprocessed_urls = []
            for url in urls:
                if not is_url_already_processed(url, self.city_name):
                    unprocessed_urls.append(url)
            
            self.stats["urls_collected"] = len(urls)
            print(f"✅ URL 수집 완료: 총 {len(urls)}개, 미처리 {len(unprocessed_urls)}개")
            return unprocessed_urls
            
        except Exception as e:
            print(f"❌ URL 수집 실패: {e}")
            return []
    
    def crawl_product(self, url, rank=None):
        """개별 상품 크롤링"""
        print(f"🔍 상품 크롤링 시작: 순위 {rank}")
        
        try:
            # 상품 페이지 이동
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            # 데이터 추출
            product_data = extract_all_product_data(self.driver, url, rank, city_name=self.city_name)
            
            # 데이터 검증
            if not validate_product_data(product_data):
                print(f"⚠️ 데이터 검증 실패: 순위 {rank}")
                self.stats["error_count"] += 1
                return False
            
            # 기본 구조에 맞춰 데이터 병합
            base_data = create_product_data_structure(self.city_name, self.stats["total_processed"] + 1, rank)
            base_data.update(product_data)
            
            # 이미지 처리
            try:
                main_img, thumb_img = get_dual_image_urls_kkday(self.driver)
                if main_img:
                    base_data["메인이미지"] = main_img
                    
                    # 이미지 다운로드 (선택적)
                    if CONFIG.get("SAVE_IMAGES", False):
                        img_path = f"images/{self.city_name}/rank_{rank}_main.jpg"
                        download_and_save_image_kkday(main_img, img_path)
                
                if thumb_img:
                    base_data["썸네일이미지"] = thumb_img
                    
            except Exception as e:
                print(f"  ⚠️ 이미지 처리 실패: {e}")
            
            # CSV 저장
            if save_to_csv_kkday(base_data, self.city_name):
                # 순위 정보 저장
                save_url_with_rank(url, rank, self.city_name)
                
                # URL 처리 완료 표시
                mark_url_as_processed(url, self.city_name, base_data["상품번호"], rank)
                
                self.stats["success_count"] += 1
                self.stats["current_rank"] = rank
                print(f"✅ 상품 크롤링 완료: 순위 {rank}")
                return True
            else:
                self.stats["error_count"] += 1
                return False
                
        except Exception as e:
            print(f"❌ 상품 크롤링 실패 (순위 {rank}): {e}")
            self.stats["error_count"] += 1
            return False
        finally:
            self.stats["total_processed"] += 1
    
    def crawl_products_batch(self, urls, start_rank=1):
        """배치 상품 크롤링"""
        print(f"📦 배치 크롤링 시작: {len(urls)}개 상품")
        
        current_rank = start_rank
        
        for i, url in enumerate(urls):
            print(f"\n{'='*50}")
            print(f"진행률: {i+1}/{len(urls)} ({((i+1)/len(urls)*100):.1f}%)")
            print(f"URL: {url}")
            
            # 이미 처리된 URL인지 확인
            if is_url_already_processed(url, self.city_name):
                print(f"⏭️ 이미 처리된 URL, 건너뜀")
                self.stats["skip_count"] += 1
                continue
            
            # 상품 크롤링
            success = self.crawl_product(url, current_rank)
            
            if success:
                current_rank += 1
            
            # 진행상황 출력
            self.print_progress()
            
            # 자연스러운 대기
            delay = random.uniform(
                CONFIG.get("MEDIUM_MIN_DELAY", 3),
                CONFIG.get("MEDIUM_MAX_DELAY", 8)
            )
            print(f"⏳ {delay:.1f}초 대기 중...")
            time.sleep(delay)
            
            # 중간 휴식 (10개마다)
            if (i + 1) % 10 == 0:
                long_delay = random.uniform(
                    CONFIG.get("LONG_MIN_DELAY", 15),
                    CONFIG.get("LONG_MAX_DELAY", 30)
                )
                print(f"😴 긴 휴식: {long_delay:.1f}초...")
                time.sleep(long_delay)
        
        print("\n📦 배치 크롤링 완료")
        return True
    
    def run_full_crawling(self, max_pages=3, max_products=None):
        """전체 크롤링 실행"""
        print(f"🎯 {self.city_name} 전체 크롤링 시작")
        
        try:
            # 1. 초기화
            if not self.initialize():
                return False
            
            # 2. URL 수집
            urls = self.collect_urls(max_pages)
            if not urls:
                print("⚠️ 수집할 URL이 없습니다.")
                return False
            
            # 3. 최대 상품 수 제한
            max_products_config = CONFIG.get("MAX_PRODUCTS_PER_CITY", None)
            if max_products:
                urls = urls[:max_products]
            elif max_products_config:
                urls = urls[:max_products_config]
            
            print(f"📊 크롤링할 상품 수: {len(urls)}개")
            
            # 4. 배치 크롤링 실행
            success = self.crawl_products_batch(urls)
            
            # 5. 최종 통계
            self.stats["end_time"] = datetime.now()
            self.print_final_stats()
            
            return success
            
        except Exception as e:
            print(f"❌ 전체 크롤링 실패: {e}")
            return False
        finally:
            if self.driver:
                # self.driver.quit() - 제거됨: 브라우저 열어두기
                pass
    
    def print_progress(self):
        """진행상황 출력"""
        total = self.stats["total_processed"]
        success = self.stats["success_count"]
        error = self.stats["error_count"]
        skip = self.stats["skip_count"]
        
        if total > 0:
            success_rate = (success / total) * 100
            print(f"📊 진행상황: 성공 {success}, 실패 {error}, 건너뜀 {skip}, 성공률 {success_rate:.1f}%")
    
    def print_final_stats(self):
        """최종 통계 출력"""
        print("\n" + "="*60)
        print(f"🎉 {self.city_name} 크롤링 완료!")
        print("="*60)
        
        if self.stats["start_time"] and self.stats["end_time"]:
            duration = self.stats["end_time"] - self.stats["start_time"]
            print(f"⏱️ 소요시간: {duration}")
        
        print(f"📊 처리 통계:")
        print(f"   • 전체 처리: {self.stats['total_processed']}개")
        print(f"   • 성공: {self.stats['success_count']}개")
        print(f"   • 실패: {self.stats['error_count']}개")
        print(f"   • 건너뜀: {self.stats['skip_count']}개")
        print(f"   • URL 수집: {self.stats['urls_collected']}개")
        print(f"   • 마지막 순위: {self.stats['current_rank']}")
        
        if self.stats["total_processed"] > 0:
            success_rate = (self.stats["success_count"] / self.stats["total_processed"]) * 100
            print(f"   • 성공률: {success_rate:.1f}%")

# =============================================================================
# 편의 함수들 (기존 코드 호환성)
# =============================================================================

def execute_kkday_crawling_system(city_name="서울", max_pages=3, max_products=None):
    """KKday 크롤링 시스템 실행 (기존 함수명 호환)"""
    crawler = KKdayCrawler(city_name)
    return crawler.run_full_crawling(max_pages, max_products)

def quick_crawl_test(city_name="서울", max_products=3):
    """빠른 크롤링 테스트"""
    print(f"🧪 빠른 테스트 크롤링: {city_name}")
    
    crawler = KKdayCrawler(city_name)
    return crawler.run_full_crawling(max_pages=1, max_products=max_products)

def get_crawling_status(city_name):
    """크롤링 상태 조회"""
    try:
        summary = get_collected_ranks_summary(city_name)
        
        print(f"\n📊 {city_name} 크롤링 현황:")
        print(f"   • 수집된 URL: {summary.get('total_urls', 0)}개")
        print(f"   • 순위 범위: {summary.get('rank_range', '없음')}")
        print(f"   • 누락 순위: {len(summary.get('missing_ranks', []))}개")
        
        missing = summary.get('missing_ranks', [])
        if missing:
            print(f"   • 누락 상세: {missing[:10]}{'...' if len(missing) > 10 else ''}")
        
        return summary
        
    except Exception as e:
        print(f"⚠️ 상태 조회 실패: {e}")
        return {}

print("✅ crawler.py 로드 완료: 메인 크롤링 엔진 준비!")