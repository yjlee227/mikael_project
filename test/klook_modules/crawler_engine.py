"""
🚀 그룹 9-A,9-B: KLOOK 크롤러 엔진 시스템 (분리 버전)
- 그룹 9-A: 핵심 크롤링 엔진 및 상품 정보 수집
- 그룹 9-B: 고급 크롤링 제어 및 에러 복구 시스템
- 통합된 크롤링 워크플로우 및 상태 관리
"""

import os
import time
import random
import json
from datetime import datetime
import traceback

# config 모듈에서 라이브러리 상태 import
from .config import CONFIG, get_city_code, get_city_info

# 조건부 import
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    print("⚠️ Selenium이 설치되지 않았습니다. 크롤링 엔진 기능이 제한됩니다.")
    SELENIUM_AVAILABLE = False

# 다른 모듈들 import
from .url_manager import is_url_already_processed, mark_url_as_processed, get_unprocessed_urls
from .data_handler import get_image_src_klook, download_and_save_image_klook, save_to_csv_klook, create_product_data_structure
from .system_utils import get_product_name, get_price, get_rating, clean_price, clean_rating

# =============================================================================
# 🚀 그룹 9-A: 핵심 크롤링 엔진
# =============================================================================

class KlookCrawlerEngine:
    """KLOOK 크롤링 엔진 핵심 클래스"""
    
    def __init__(self, driver):
        self.driver = driver
        self.stats = {
            "total_processed": 0,
            "success_count": 0,
            "error_count": 0,
            "skip_count": 0,
            "start_time": None,
            "current_city": None
        }
        self.error_log = []
        
    def reset_stats(self, city_name):
        """통계 초기화"""
        self.stats = {
            "total_processed": 0,
            "success_count": 0,
            "error_count": 0,
            "skip_count": 0,
            "start_time": datetime.now(),
            "current_city": city_name
        }
        self.error_log = []
        
    def final_backup(self, city_name):
        """최종 백업 실행"""
        try:
            if self.stats["success_count"] > 0:
                print(f"💾 최종 백업 실행 중... (총 {self.stats['success_count']}개 완료)")
                
                from .data_handler import backup_csv_data
                backup_suffix = f"final_{self.stats['success_count']}"
                backup_success = backup_csv_data(city_name, backup_suffix)
                
                # 국가별 CSV는 save_to_csv_klook에서 자동으로 처리됨 (원본 노트북과 동일)
                print(f"🌏 '{city_name}' 크롤링 완료 - 국가별 CSV는 각 상품 저장 시 자동 생성됨")
                
                if backup_success:
                    print(f"✅ 최종 백업 완료 (총 {self.stats['success_count']}개)")
                    return True
                else:
                    print(f"⚠️ 최종 백업 실패")
                    return False
            else:
                print(f"ℹ️ 백업할 데이터 없음 (0개 완료)")
                return True
                
        except Exception as e:
            print(f"❌ 최종 백업 실패: {e}")
            return False
        
    def process_single_url(self, url, city_name, product_number):
        """단일 URL 처리 (핵심 크롤링 로직)"""
        if not SELENIUM_AVAILABLE:
            return {"success": False, "error": "Selenium not available"}
        
        print(f"🔄 상품 {product_number}: URL 처리 중...")
        print(f"   🔗 {url}")
        
        try:
            # 1. URL 중복 체크 (기존 시스템 + 랭킹 매니저)
            if is_url_already_processed(url, city_name):
                print(f"   ⏭️ 이미 처리된 URL - 스킵")
                self.stats["skip_count"] += 1
                return {"success": True, "skipped": True, "reason": "already_processed"}
            
            # 랭킹 매니저에서 중복 URL 크롤링 여부 확인
            try:
                from .ranking_manager import ranking_manager
                if not ranking_manager.should_crawl_url(url, city_name):
                    print(f"   ⏭️ 랭킹 매니저: 중복 URL 스킵 (다른 탭에서 이미 크롤링)")
                    self.stats["skip_count"] += 1
                    return {"success": True, "skipped": True, "reason": "duplicate_in_ranking"}
            except Exception as e:
                print(f"   ⚠️ 랭킹 매니저 확인 실패: {e}")
            
            # 2. 페이지 이동
            self.driver.get(url)
            
            # 3. 스마트 페이지 로딩 대기
            self._smart_page_wait()
            
            # 4. 페이지 유효성 검사
            if not self._validate_page():
                print(f"   ❌ 페이지 유효성 검사 실패")
                self.stats["error_count"] += 1
                return {"success": False, "error": "invalid_page"}
            
            # 4.5. 자동 스크롤 실행 (고급 패턴 적용)
            self._apply_advanced_scroll()
            
            # 5. 상품 정보 수집
            product_data = self._extract_product_info(url, city_name, product_number)
            
            if not product_data:
                print(f"   ❌ 상품 정보 수집 실패")
                self.stats["error_count"] += 1
                return {"success": False, "error": "extraction_failed"}
            
            # 6. 데이터 저장
            save_success = save_to_csv_klook(product_data, city_name)
            
            # 6.5. 자동 백업 (일정 주기마다)
            self._check_auto_backup(city_name)
            
            # 7. URL 처리 완료 표시 (순위 정보 포함)
            mark_url_as_processed(url, city_name, product_number, product_number)
            
            # 랭킹 매니저에 크롤링 완료 표시
            try:
                from .ranking_manager import ranking_manager
                ranking_manager.mark_url_crawled(url, city_name)
            except Exception as e:
                print(f"   ⚠️ 랭킹 매니저 완료 표시 실패: {e}")
            
            if save_success:
                print(f"   ✅ 상품 {product_number} 처리 완료")
                self.stats["success_count"] += 1
                return {
                    "success": True,
                    "product_data": product_data,
                    "product_number": product_number
                }
            else:
                print(f"   ⚠️ 데이터 저장 실패")
                self.stats["error_count"] += 1
                return {"success": False, "error": "save_failed"}
                
        except Exception as e:
            error_info = {
                "url": url,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }
            self.error_log.append(error_info)
            
            print(f"   ❌ 처리 실패: {type(e).__name__}: {e}")
            self.stats["error_count"] += 1
            return {"success": False, "error": str(e)}
    
    def _validate_page(self):
        """페이지 유효성 검사"""
        try:
            # 페이지 제목 확인
            page_title = self.driver.title
            if not page_title or "error" in page_title.lower() or "404" in page_title:
                return False
            
            # KLOOK 활동 페이지인지 확인
            activity_indicators = [
                "#activity_title",
                ".activity-title",
                "[data-testid='activity-title']",
                ".product-title"
            ]
            
            for indicator in activity_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element and element.is_displayed():
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def _apply_advanced_scroll(self):
        """고급 스크롤 패턴 적용 (10가지 패턴 중 랜덤 선택)"""
        if not SELENIUM_AVAILABLE:
            return
        
        try:
            print(f"  🌀 고급 스크롤 패턴 적용 중...")
            
            # url_collection의 고급 스크롤 시스템 사용
            from .url_collection import smart_scroll_selector
            smart_scroll_selector(self.driver)
            
            # 페이지 상단으로 부드럽게 복귀
            self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
            time.sleep(1)
            
            print(f"    ✅ 고급 스크롤 패턴 완료 (탐지 방지 강화)")
            
        except Exception as e:
            print(f"    ⚠️ 고급 스크롤 실행 실패: {e}")
            # 폴백: 기본 스크롤 실행
            try:
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(2)
                self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
                time.sleep(1)
                print(f"    ✅ 폴백 스크롤 완료")
            except Exception as fallback_e:
                print(f"    ❌ 폴백 스크롤도 실패: {fallback_e}")
    
    def _smart_page_wait(self):
        """스마트 페이지 대기 (동적 로딩 감지)"""
        if not SELENIUM_AVAILABLE:
            return
        
        try:
            print(f"  ⏱️ 스마트 페이지 대기 중...")
            
            # url_collection의 고급 대기 시스템 사용
            from .url_collection import wait_for_page_ready, smart_wait_for_page_load
            
            # 페이지 준비 완료 대기 (jQuery, DOM 완료)
            wait_for_page_ready(self.driver, timeout=8)
            
            # 추가 로드 대기 (동적 컨텐츠)
            smart_wait_for_page_load(self.driver, max_wait=6)
            
            print(f"    ✅ 스마트 대기 완료")
            
        except Exception as e:
            print(f"    ⚠️ 스마트 대기 실패: {e}")
            # 폴백: 기본 대기
            try:
                wait_time = random.uniform(2, 4)
                time.sleep(wait_time)
                print(f"    ✅ 폴백 대기 완료 ({wait_time:.1f}초)")
            except Exception as fallback_e:
                print(f"    ❌ 폴백 대기도 실패: {fallback_e}")
    
    def _check_auto_backup(self, city_name):
        """자동 백업 체크 (20개마다 실행)"""
        try:
            # 20개마다 백업 실행 (자주 백업하여 데이터 안전성 확보)
            if self.stats["success_count"] > 0 and self.stats["success_count"] % 20 == 0:
                print(f"  💾 자동 백업 실행 중... ({self.stats['success_count']}개 완료)")
                
                from .data_handler import backup_csv_data
                backup_suffix = f"auto_{self.stats['success_count']}"
                backup_success = backup_csv_data(city_name, backup_suffix)
                
                if backup_success:
                    print(f"  ✅ 자동 백업 완료 (진행률: {self.stats['success_count']}개)")
                else:
                    print(f"  ⚠️ 자동 백업 실패")
                    
        except Exception as e:
            print(f"  ⚠️ 자동 백업 체크 실패: {e}")
    
    def _extract_product_info(self, url, city_name, product_number):
        """상품 정보 추출"""
        try:
            print(f"  📊 상품 정보 수집 중...")
            
            # 1. 기본 정보 수집
            product_name = get_product_name(self.driver, "Product")
            price = get_price(self.driver)
            rating = get_rating(self.driver)
            
            # 2. 데이터 정제
            clean_price_value = clean_price(price)
            clean_rating_value = clean_rating(rating)
            
            # 3. 이미지 처리 (듀얼 이미지 시스템)
            image_filename = None
            dual_images = None
            if CONFIG.get("SAVE_IMAGES", False):
                try:
                    # 먼저 듀얼 이미지 시스템 시도
                    from .data_handler import get_dual_image_urls_klook, download_dual_images_klook
                    
                    image_urls = get_dual_image_urls_klook(self.driver, "Product")
                    if image_urls and image_urls.get("main"):
                        dual_images = download_dual_images_klook(
                            image_urls, product_number, city_name
                        )
                        print(f"    ✅ 듀얼 이미지 처리: 메인={bool(dual_images.get('main'))}, 썸네일={bool(dual_images.get('thumb'))}")
                    else:
                        # 폴백: 기존 단일 이미지 시스템
                        img_src = get_image_src_klook(self.driver, "Product") 
                        image_filename = download_and_save_image_klook(
                            img_src, product_number, city_name
                        )
                        print(f"    ✅ 단일 이미지 처리: {image_filename}")
                except Exception as e:
                    print(f"    ⚠️ 이미지 처리 실패: {e}")
                    image_filename = None
                    dual_images = None
            
            # 4. 추가 정보 수집 (선택적)
            additional_data = self._extract_additional_info()
            
            # 원본 가격과 평점 정보 추가
            if price and price != clean_price_value:
                additional_data["가격_원본"] = price
            if rating and rating != clean_rating_value:
                additional_data["평점_원본"] = rating
            
            # URL 해시 생성
            import hashlib
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
            additional_data["URL_해시"] = url_hash
            
            # 5. 랭킹 정보 수집
            tab_info = {}
            try:
                from .ranking_manager import ranking_manager
                url_rankings = ranking_manager.get_url_rankings(url, city_name)
                if url_rankings and url_rankings.get("tab_rankings"):
                    # 가장 높은 랭킹(작은 숫자)을 가진 탭 정보 사용
                    best_tab = min(url_rankings["tab_rankings"].items(), 
                                 key=lambda x: x[1]["ranking"])
                    tab_info = {
                        "tab_name": best_tab[0],
                        "actual_ranking": best_tab[1]["ranking"],
                        "ranking": best_tab[1]["ranking"],
                        "tab_order": 1,  # 기본값
                        "is_duplicate": url_rankings.get("is_duplicate", False)
                    }
            except Exception as e:
                print(f"    ⚠️ 랭킹 정보 수집 실패: {e}")
            
            # 6. 데이터 구조 생성 (기존 32개 컬럼 구조)
            product_data = create_product_data_structure(
                product_number=product_number,
                product_name=product_name,
                price=clean_price_value,
                image_filename=image_filename,
                url=url,
                city_name=city_name,
                additional_data=additional_data,
                dual_images=dual_images,
                tab_info=tab_info
            )
            
            print(f"    ✅ 정보 수집 완료: {product_name[:30]}...")
            return product_data
            
        except Exception as e:
            print(f"    ❌ 정보 추출 실패: {e}")
            return None
    
    def _extract_additional_info(self):
        """추가 정보 추출 (카테고리, 태그 등)"""
        additional_data = {}
        
        try:
            # 카테고리 정보
            category_selectors = [
                ".breadcrumb a",
                "[data-testid='breadcrumb'] a",
                ".category-tag",
                ".tag"
            ]
            
            categories = []
            for selector in category_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and text not in categories:
                            categories.append(text)
                except:
                    continue
            
            if categories:
                additional_data["카테고리"] = " > ".join(categories[:3])  # 상위 3개만
            
            # 위치 정보 (디버깅 로그 추가)
            print(f"    🔍 위치 정보 검색 중...")
            try:
                location_selectors = [
                    "[data-testid='location']",
                    ".location",
                    ".address",
                    ".location-info",
                    "[class*='location']",
                    "[class*='address']"
                ]
                
                location_found = False
                for selector in location_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        print(f"      📍 셀렉터 '{selector}': {len(elements)}개 요소 발견")
                        
                        for i, element in enumerate(elements):
                            location = element.text.strip()
                            print(f"        - 요소 {i+1}: '{location}'")
                            if location and len(location) > 2:
                                additional_data["위치"] = location
                                print(f"      ✅ 위치 정보 수집 성공: '{location}'")
                                location_found = True
                                break
                        
                        if location_found:
                            break
                    except Exception as e:
                        print(f"      ❌ 셀렉터 '{selector}' 처리 실패: {e}")
                        continue
                
                if not location_found:
                    print(f"      ⚠️ 위치 정보를 찾지 못했습니다")
            except Exception as e:
                print(f"    ❌ 위치 정보 검색 전체 실패: {e}")
                pass
            
            # 하이라이트 정보
            try:
                highlight_selectors = [
                    ".highlight",
                    ".description",
                    ".product-description",
                    "[data-testid='description']",
                    ".activity-highlights",
                    ".tour-highlights"
                ]
                
                for selector in highlight_selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        highlight = element.text.strip()
                        if highlight and len(highlight) > 10:
                            # 긴 하이라이트 텍스트는 줄임
                            if len(highlight) > 200:
                                highlight = highlight[:200] + "..."
                            additional_data["하이라이트"] = highlight
                            break
                    except:
                        continue
            except:
                pass
            
            # 리뷰 수
            try:
                review_selectors = [
                    "[data-testid='review-count']",
                    ".review-count",
                    "[class*='review'][class*='count']"
                ]
                
                for selector in review_selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        review_text = element.text.strip()
                        if review_text and any(char.isdigit() for char in review_text):
                            additional_data["리뷰수"] = review_text
                            break
                    except:
                        continue
            except:
                pass
            
            # 언어 정보
            try:
                language_selectors = [
                    ".language",
                    ".guide-language",
                    "[data-testid='language']",
                    "[class*='language']",
                    "[class*='lang']"
                ]
                
                for selector in language_selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        language = element.text.strip()
                        if language and len(language) < 50:
                            additional_data["언어"] = language
                            break
                    except:
                        continue
            except:
                pass
                
        except Exception as e:
            print(f"    ⚠️ 추가 정보 수집 실패: {e}")
        
        return additional_data
    
    def get_stats_summary(self):
        """통계 요약 반환"""
        if self.stats["start_time"]:
            elapsed = datetime.now() - self.stats["start_time"]
            elapsed_seconds = elapsed.total_seconds()
        else:
            elapsed_seconds = 0
        
        return {
            "city": self.stats["current_city"],
            "total_processed": self.stats["total_processed"],
            "success_count": self.stats["success_count"],
            "error_count": self.stats["error_count"],
            "skip_count": self.stats["skip_count"],
            "success_rate": (self.stats["success_count"] / max(1, self.stats["total_processed"])) * 100,
            "elapsed_time": elapsed_seconds,
            "avg_time_per_url": elapsed_seconds / max(1, self.stats["total_processed"]),
            "error_log_count": len(self.error_log)
        }

# =============================================================================
# 🛡️ 그룹 9-B: 고급 크롤링 제어 및 에러 복구
# =============================================================================

class AdvancedCrawlerController:
    """고급 크롤링 제어 시스템"""
    
    def __init__(self, crawler_engine):
        self.engine = crawler_engine
        self.retry_queue = []
        self.failed_urls = []
        
    def process_url_list_with_recovery(self, urls, city_name, max_retries=2):
        """URL 리스트 처리 (에러 복구 포함)"""
        print(f"🛡️ 고급 크롤링 제어 시작: {len(urls)}개 URL")
        
        self.engine.reset_stats(city_name)
        
        # 1차 처리
        remaining_urls = self._process_urls_batch(urls, city_name, "1차")
        
        # 재시도 처리
        retry_count = 0
        while remaining_urls and retry_count < max_retries:
            retry_count += 1
            print(f"\n🔄 {retry_count}차 재시도: {len(remaining_urls)}개 URL")
            
            # 재시도 전 대기
            wait_time = min(30, retry_count * 10)
            print(f"⏱️ 재시도 전 {wait_time}초 대기...")
            time.sleep(wait_time)
            
            remaining_urls = self._process_urls_batch(remaining_urls, city_name, f"{retry_count}차 재시도")
        
        # 최종 실패 URL 기록
        if remaining_urls:
            self.failed_urls.extend(remaining_urls)
            self._save_failed_urls(city_name)
        
        return self.engine.get_stats_summary()
    
    def _process_urls_batch(self, urls, city_name, batch_name):
        """URL 배치 처리"""
        print(f"\n📦 {batch_name} 배치 처리 시작: {len(urls)}개 URL")
        
        failed_urls = []
        
        for idx, url in enumerate(urls, 1):
            try:
                print(f"\n[{idx}/{len(urls)}] 처리 중...")
                
                self.engine.stats["total_processed"] += 1
                
                result = self.engine.process_single_url(url, city_name, idx)
                
                if not result.get("success", False):
                    failed_urls.append(url)
                    
                    # 연속 실패 시 긴급 중단 체크
                    if self._should_emergency_stop():
                        print("⚠️ 연속 실패로 인한 긴급 중단")
                        failed_urls.extend(urls[idx:])  # 나머지 URL들도 실패 목록에 추가
                        break
                
                # 배치 간 대기
                if idx % 10 == 0:  # 10개마다 짧은 휴식
                    time.sleep(random.uniform(2, 5))
                
                # 진행률 표시
                if idx % 20 == 0:
                    progress = (idx / len(urls)) * 100
                    print(f"📊 진행률: {progress:.1f}% ({idx}/{len(urls)})")
                    
            except KeyboardInterrupt:
                print("\n⚠️ 사용자가 중단했습니다")
                failed_urls.extend(urls[idx-1:])  # 현재 및 나머지 URL들 실패 목록에 추가
                break
                
            except Exception as e:
                print(f"❌ 예상치 못한 오류: {e}")
                failed_urls.append(url)
                continue
        
        print(f"📦 {batch_name} 완료: 실패 {len(failed_urls)}개")
        return failed_urls
    
    def _should_emergency_stop(self):
        """긴급 중단 여부 판단"""
        stats = self.engine.stats
        
        # 최소 처리량 체크
        if stats["total_processed"] < 5:
            return False
        
        # 연속 실패율 체크 (최근 10개 중 8개 이상 실패)
        recent_success_rate = stats["success_count"] / stats["total_processed"]
        if recent_success_rate < 0.2:  # 성공률 20% 미만
            return True
        
        return False
    
    def _save_failed_urls(self, city_name):
        """실패한 URL 저장"""
        if not self.failed_urls:
            return
        
        try:
            failed_dir = "failed_urls"
            os.makedirs(failed_dir, exist_ok=True)
            
            city_code = get_city_code(city_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{city_code}_failed_urls_{timestamp}.json"
            filepath = os.path.join(failed_dir, filename)
            
            data = {
                "city_name": city_name,
                "city_code": city_code,
                "failed_at": datetime.now().isoformat(),
                "total_failed": len(self.failed_urls),
                "urls": self.failed_urls,
                "error_log": self.engine.error_log[-10:]  # 최근 10개 에러만
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 실패 URL 저장: {filename} ({len(self.failed_urls)}개)")
            
        except Exception as e:
            print(f"❌ 실패 URL 저장 실패: {e}")

# =============================================================================
# 🎮 통합 크롤링 시스템
# =============================================================================

def execute_klook_crawling_system(driver, urls, city_name, mode="advanced"):
    """KLOOK 크롤링 시스템 실행"""
    print(f"🚀 KLOOK 크롤링 시스템 시작!")
    print(f"🏙️ 도시: {city_name}")
    print(f"🔗 대상 URL: {len(urls)}개")
    print(f"⚙️ 모드: {mode}")
    print("=" * 80)
    
    # 미처리 URL만 필터링
    unprocessed_urls = get_unprocessed_urls(urls, city_name)
    
    if not unprocessed_urls:
        print("ℹ️ 처리할 새로운 URL이 없습니다")
        return {"success": True, "message": "no_new_urls"}
    
    print(f"📋 처리 대상: {len(unprocessed_urls)}개 URL (중복 제외 후)")
    
    # 크롤링 엔진 초기화
    engine = KlookCrawlerEngine(driver)
    
    if mode == "basic":
        # 기본 모드: 단순 순차 처리
        engine.reset_stats(city_name)
        
        for idx, url in enumerate(unprocessed_urls, 1):
            print(f"\n[{idx}/{len(unprocessed_urls)}] 기본 처리...")
            engine.stats["total_processed"] += 1
            engine.process_single_url(url, city_name, idx)
        
        final_stats = engine.get_stats_summary()
        
    elif mode == "advanced":
        # 고급 모드: 에러 복구 포함
        controller = AdvancedCrawlerController(engine)
        final_stats = controller.process_url_list_with_recovery(unprocessed_urls, city_name)
        
    else:
        print(f"❌ 알 수 없는 모드: {mode}")
        return {"success": False, "error": "unknown_mode"}
    
    # 최종 결과
    print(f"\n🎉 === KLOOK 크롤링 완료 ===")
    print(f"🏙️ 도시: {final_stats['city']}")
    print(f"📊 처리 결과:")
    print(f"   🔗 총 처리: {final_stats['total_processed']}개")
    print(f"   ✅ 성공: {final_stats['success_count']}개")
    print(f"   ❌ 실패: {final_stats['error_count']}개")
    print(f"   ⏭️ 스킵: {final_stats['skip_count']}개")
    print(f"   📈 성공률: {final_stats['success_rate']:.1f}%")
    print(f"   ⏱️ 총 소요시간: {final_stats['elapsed_time']:.1f}초")
    print(f"   ⚡ 평균 처리시간: {final_stats['avg_time_per_url']:.1f}초/URL")
    
    return {
        "success": True,
        "stats": final_stats,
        "mode": mode,
        "city_name": city_name
    }

def quick_crawl_test(driver, test_urls, city_name, max_test=3):
    """빠른 크롤링 테스트"""
    print(f"🧪 빠른 크롤링 테스트: {city_name} ({min(max_test, len(test_urls))}개 URL)")
    
    engine = KlookCrawlerEngine(driver)
    engine.reset_stats(city_name)
    
    test_results = []
    
    for idx, url in enumerate(test_urls[:max_test], 1):
        print(f"\n🧪 테스트 {idx}/{min(max_test, len(test_urls))}")
        engine.stats["total_processed"] += 1
        
        result = engine.process_single_url(url, city_name, f"test_{idx}")
        test_results.append({
            "url": url,
            "success": result.get("success", False),
            "error": result.get("error")
        })
    
    stats = engine.get_stats_summary()
    
    print(f"\n🧪 테스트 완료:")
    print(f"   ✅ 성공: {stats['success_count']}/{stats['total_processed']}")
    print(f"   📈 성공률: {stats['success_rate']:.1f}%")
    
    return {
        "test_results": test_results,
        "stats": stats
    }

print("✅ 그룹 9-A,9-B 완료: KLOOK 크롤러 엔진 시스템!")
print("   🚀 그룹 9-A (핵심 엔진):")
print("   - KlookCrawlerEngine: 핵심 크롤링 로직")
print("   - process_single_url(): 단일 URL 처리")
print("   - _extract_product_info(): 상품 정보 추출")
print("   🛡️ 그룹 9-B (고급 제어):")
print("   - AdvancedCrawlerController: 에러 복구 시스템")
print("   - process_url_list_with_recovery(): 복구 기능 포함 처리")
print("   🎮 통합 시스템:")
print("   - execute_klook_crawling_system(): 통합 크롤링 실행")
print("   - quick_crawl_test(): 빠른 테스트")
print("   ⚙️ 지원 모드: basic, advanced")