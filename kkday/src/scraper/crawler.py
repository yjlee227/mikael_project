"""
메인 크롤링 엔진
- 전체 크롤링 프로세스 통합 관리
- 페이지네이션 및 데이터 수집
- 에러 처리 및 복구 시스템
"""

import time
import random
import re
from datetime import datetime

from ..config import CONFIG, SELENIUM_AVAILABLE
from ..utils.file_handler import create_product_data_structure, save_to_csv_kkday, get_dual_image_urls_kkday, download_and_save_image_kkday, ensure_directory_structure
from .driver_manager import setup_driver, go_to_main_page, find_and_fill_search, click_search_button, handle_kkday_cookie_popup, handle_popup, smart_scroll_selector
from .url_manager import collect_urls_from_page, get_pagination_urls, is_url_already_processed, mark_url_as_processed, go_to_next_page
from .parsers import extract_all_product_data, validate_product_data
from .ranking import save_url_with_rank, get_next_start_rank
from . import human_scroll_patterns

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
            time.sleep(random.uniform(1, 3))
            
            # [수정] 도시별 상품 목록 URL로 직접 이동
            from urllib.parse import quote
            encoded_city_name = quote(self.city_name)
            target_url = f"https://www.kkday.com/ko/product/productlist/{encoded_city_name}"
            print(f"상품 목록 페이지로 직접 이동: {target_url}")
            
            self.driver.get(target_url)
            time.sleep(random.uniform(3, 5))  # 페이지 로드를 위한 최소 대기
            
            # 팝업 처리 및 스크롤
            handle_popup(self.driver)
            smart_scroll_selector(self.driver)
            time.sleep(random.uniform(2, 5))
            
            self.stats["start_time"] = datetime.now()
            print("✅ 크롤러 초기화 완료")
            return True
            
        except Exception as e:
            print(f"❌ 크롤러 초기화 실패: {e}")
            if self.driver:
                pass
            return False

    def collect_urls(self, max_pages=3, max_products=None):
        """URL 수집 (효율화 버전: max_products에 도달하면 중단)"""
        print(f"🔗 URL 수집 시작 (최대 {max_pages}페이지, 목표 상품: {max_products or '제한 없음'})")
        time.sleep(random.uniform(2, 4))

        all_product_urls = []
        seen_urls = set()
        current_page = 1

        try:
            while current_page <= max_pages:
                print(f"  📄 {current_page}페이지 탐색 중... (현재 수집: {len(all_product_urls)}개)")

                # 현재 페이지에서 URL 수집
                page_urls = collect_urls_from_page(self.driver, self.city_name)
                if not page_urls:
                    print("  ⚠️ 현재 페이지에서 URL을 찾을 수 없어 수집 중단")
                    break
                
                # 상품 URL만 필터링
                product_urls_on_page = self.filter_product_detail_urls(page_urls)

                # 새로운 상품 URL만 추가
                for url in product_urls_on_page:
                    if url not in seen_urls:
                        all_product_urls.append(url)
                        seen_urls.add(url)

                # 목표 상품 수에 도달했는지 확인
                if max_products and len(all_product_urls) >= max_products:
                    print(f"  🎯 목표 상품 수({max_products}개)에 도달하여 수집을 중단합니다.")
                    break

                # 다음 페이지로 이동
                if current_page < max_pages:
                    if not go_to_next_page(self.driver):
                        print("  ℹ️ 더 이상 다음 페이지가 없어 수집을 중단합니다.")
                        break
                
                current_page += 1
                # 페이지 로드 대기
                time.sleep(random.uniform(2, 5))

            # 미처리 URL 필터링
            unprocessed_urls = []
            for url in all_product_urls:
                if not is_url_already_processed(url, self.city_name):
                    unprocessed_urls.append(url)

            self.stats["urls_collected"] = len(all_product_urls)
            print(f"✅ URL 수집 완료: 총 {len(all_product_urls)}개 상품 URL, 미처리 {len(unprocessed_urls)}개")
            
            # max_products에 맞춰 최종 결과 슬라이싱 (안전장치)
            if max_products:
                return unprocessed_urls[:max_products]
            return unprocessed_urls

        except Exception as e:
            print(f"❌ URL 수집 실패: {e}")
            import traceback
            traceback.print_exc()
            return []

    def filter_product_detail_urls(self, urls):
        """상품 상세 페이지 URL만 필터링 (목록 페이지 제외)"""
        # 상품 상세 페이지 패턴 (더 포괄적으로 수정)
        product_detail_patterns = [
            r'/ko/product/\d+$',                           # /ko/product/287674
            r'/ko/product/\d+-[\w\-]+',                    # /ko/product/146520-krabi-kayaking
            r'/product/\d+',                               # /product/287674 (언어 생략)
            r'/product/\d+-[\w\-]+',                       # /product/146520-krabi-kayaking
        ]

        filtered_urls = []
        excluded_count = 0

        for url in urls:
            # 목록 페이지 패턴 제외
            if 'productlist' in url:
                excluded_count += 1
                print(f"  🚫 목록 페이지 제외: {url}")
                continue

            # 상품 상세 페이지 패턴 확인
            is_product_detail = any(re.search(pattern, url) for pattern in product_detail_patterns)

            if is_product_detail:
                filtered_urls.append(url)
            else:
                excluded_count += 1
                print(f"  🚫 비상품 페이지 제외: {url}")

        print(f"✅ URL 필터링 완료: {len(filtered_urls)}개 유지, {excluded_count}개 제외")
        return filtered_urls

    def get_next_available_rank(self):
        """도시별 다음 사용 가능한 순위 조회"""
        try:
            next_rank = get_next_start_rank(self.city_name)
            print(f"📊 {self.city_name} 다음 순위: {next_rank}")
            return next_rank
        except Exception as e:
            print(f"⚠️ 순위 조회 실패, 1부터 시작: {e}")
            return 1

    def crawl_product(self, url, rank=None):
        """개별 상품 크롤링"""
        print(f"🔍 상품 크롤링 시작: 순위 {rank}")
        try:
            # 상품 페이지 이동
            self.driver.get(url)
            time.sleep(random.uniform(3, 8))
            
            # [추가] 인간 행동 기반 스크롤 실행 
            print("   - 🤖 인간 행동 기반 스크롤 시작...")
            try:
                human_scroll_patterns.simulate_human_scroll(self.driver)
            except Exception as e:
                print(f"   - ⚠️ 스크롤 패턴 실행 중 오류 발생:{e}")
                # 스크롤에 실패해도 데이터 수집은 계속 시도
                pass 
            
            # 데이터 추출
            product_data = extract_all_product_data(self.driver, url, rank, city_name=self.city_name)
            time.sleep(random.uniform(4, 9))

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
                main_img_url, thumb_img_url = get_dual_image_urls_kkday(self.driver)
                # 파일명에 순차적인 rank를 사용 (없으면 0번)
                image_identifier = rank if rank is not None else 0
                
                if main_img_url:
                    if CONFIG.get("SAVE_IMAGES", False):
                        print("    📥 메인 이미지 다운로드 중...")
                        time.sleep(random.uniform(0.5, 1.5))  # 이미지 다운로드 전 짧은 대기

                        main_img_filename = download_and_save_image_kkday(
                            main_img_url,
                            image_identifier,
                            self.city_name,
                            image_type="main"
                        )
                        base_data["메인이미지"] = main_img_filename if main_img_filename else "다운로드 실패"
                        time.sleep(random.uniform(1, 2))

                    else:
                        base_data["메인이미지"] = main_img_url
                        
                if thumb_img_url:
                    if CONFIG.get("SAVE_IMAGES", False):
                        print("    📥 썸네일 이미지 다운로드 중...")
                        thumb_img_filename = download_and_save_image_kkday(
                            thumb_img_url,
                            image_identifier,
                            self.city_name,
                            image_type="thumb"
                        )
                        base_data["썸네일이미지"] = thumb_img_filename if thumb_img_filename else "다운로드 실패"
                        time.sleep(random.uniform(1, 2))
                    else:
                        base_data["썸네일이미지"] = thumb_img_url
                        
            except Exception as e:
                import traceback
                print(f"  ⚠️ 이미지 처리 실패: {e}")
                traceback.print_exc()
            
            # CSV 저장
            if save_to_csv_kkday(base_data, self.city_name):
                # 순위 정보 저장 (product_id 포함)
                save_url_with_rank(url, rank, self.city_name, base_data["상품번호"])
                
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
    
    def crawl_products_batch(self, urls):
        """배치 상품 크롤링"""
        # 시작 순위 자동 계산
        start_rank = self.get_next_available_rank()
        print(f"📦 배치 크롤링 시작: {len(urls)}개 상품 (시작 순위: {start_rank})")

        current_rank = start_rank

        for i, url in enumerate(urls):
            time.sleep(random.uniform(2, 4))
            print(f"\n{'='*50}")
            print(f"진행률: {i+1}/{len(urls)} ({((i+1)/len(urls)*100):.1f}%)")

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

            # 2.1 상품 상세 페이지 URL만 필터링 (목록 페이지 제외)
            product_urls = self.filter_product_detail_urls(urls)
            if not product_urls:
                print("⚠️ 상품 상세 페이지 URL이 없습니다.")
                return False

            print(f"📊 전체 URL: {len(urls)}개, 상품 상세 URL: {len(product_urls)}개")

            # 3. 최대 상품 수 제한
            max_products_config = CONFIG.get("MAX_PRODUCTS_PER_CITY", None)
            if max_products:
                product_urls = product_urls[:max_products]
            elif max_products_config:
                product_urls = product_urls[:max_products_config]

            print(f"📊 크롤링할 상품 수: {len(product_urls)}개")

            # 4. 배치 크롤링 실행 (순위는 내부에서 자동 계산)
            success = self.crawl_products_batch(product_urls)

            # 5. 최종 통계
            self.stats["end_time"] = datetime.now()
            self.print_final_stats()

            # 🆕 국가별 통합 CSV 자동 생성 (여기에 추가)
            from ..utils.file_handler import auto_create_country_csv_after_crawling
            auto_create_country_csv_after_crawling(self.city_name)

            return success

        except Exception as e:
            print(f"❌ 전체 크롤링 실패: {e}")
            return False
        finally:
            if self.driver:
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
