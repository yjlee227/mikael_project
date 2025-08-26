"""
🎮 그룹 11,11.5: KLOOK 크롤링 제어 시스템 (완전 통합 버전)
- 전체 시스템 통합 관리 및 제어
- 사용자 인터페이스 및 실행 흐름 제어
- 에러 복구 및 시스템 모니터링
- 워크플로우 자동화 및 최적화
"""

import json
import time
import os
import traceback
from datetime import datetime

# 다른 모듈들 import
from .config import CONFIG, get_city_code, get_city_info, UNIFIED_CITY_INFO
from .driver_manager import initialize_group6_system, go_to_main_page, find_and_fill_search, click_search_button, handle_popup
from .url_collection import execute_comprehensive_url_collection
from .tab_selector import execute_integrated_tab_selector_system
from .crawler_engine import execute_klook_crawling_system, quick_crawl_test
from .category_system import execute_category_analysis_system
from .data_handler import get_csv_stats, backup_csv_data
from .system_utils import check_dependencies, get_system_info

# =============================================================================
# 🎮 메인 제어 시스템
# =============================================================================

class KlookMasterController:
    """KLOOK 크롤링 마스터 컨트롤러"""
    
    def __init__(self):
        self.driver = None
        self.current_city = None
        self.session_stats = {
            "start_time": None,
            "end_time": None,
            "cities_processed": [],
            "total_urls_collected": 0,
            "total_products_crawled": 0,
            "errors": []
        }
        self.workflow_results = {}
    
    def initialize_system(self, city_name="서울"):
        """시스템 초기화"""
        print(f"🚀 KLOOK 크롤링 시스템 초기화: {city_name}")
        print("=" * 80)
        
        self.session_stats["start_time"] = datetime.now()
        self.current_city = city_name
        
        try:
            # 1. 시스템 상태 확인
            print("1️⃣ 시스템 상태 확인...")
            status = self.check_system_health()
            if status["overall"] == "poor":
                raise Exception("시스템 상태가 불량합니다. 의존성을 확인해주세요.")
            
            # 2. 드라이버 초기화
            print("2️⃣ 웹드라이버 초기화...")
            self.driver, _ = initialize_group6_system()
            if not self.driver:
                raise Exception("웹드라이버 초기화 실패")
            
            # 3. 디렉토리 설정
            print("3️⃣ 디렉토리 구조 설정...")
            self._setup_directories()
            
            print("✅ 시스템 초기화 완료")
            return True
            
        except Exception as e:
            print(f"❌ 시스템 초기화 실패: {e}")
            self.session_stats["errors"].append({
                "stage": "initialization",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def execute_full_workflow(self, city_name, strategy="comprehensive", max_products=None):
        """전체 워크플로우 실행"""
        print(f"🎯 '{city_name}' 전체 워크플로우 실행")
        print(f"📊 전략: {strategy}")
        print("=" * 80)
        
        workflow_result = {
            "city_name": city_name,
            "strategy": strategy,
            "stages": {},
            "success": False,
            "start_time": datetime.now().isoformat()
        }
        
        try:
            # Stage 1: 시스템 초기화
            if not self.initialize_system(city_name):
                raise Exception("시스템 초기화 실패")
            
            workflow_result["stages"]["initialization"] = {"success": True}
            
            # Stage 2: 페이지 네비게이션
            print("\n🌐 Stage 2: KLOOK 페이지 네비게이션...")
            nav_result = self._execute_navigation(city_name)
            workflow_result["stages"]["navigation"] = nav_result
            
            if not nav_result["success"]:
                print("⚠️ 네비게이션 실패, 계속 진행...")
            
            # Stage 3: URL 수집
            print("\n🔍 Stage 3: URL 수집...")
            url_result = self._execute_url_collection(city_name, strategy)
            workflow_result["stages"]["url_collection"] = url_result
            
            if not url_result.get("success", False) or not url_result.get("urls"):
                raise Exception("URL 수집 실패 또는 수집된 URL 없음")
            
            # Stage 4: 크롤링 실행
            print("\n🚀 Stage 4: 상품 크롤링...")
            crawl_result = self._execute_crawling(url_result["urls"], city_name, max_products)
            workflow_result["stages"]["crawling"] = crawl_result
            
            # Stage 5: 데이터 분석
            print("\n📊 Stage 5: 데이터 분석...")
            analysis_result = self._execute_analysis(city_name)
            workflow_result["stages"]["analysis"] = analysis_result
            
            # 최종 결과 정리
            workflow_result["success"] = True
            workflow_result["end_time"] = datetime.now().isoformat()
            workflow_result["summary"] = self._generate_workflow_summary(workflow_result)
            
            # 세션 통계 업데이트
            self.session_stats["cities_processed"].append(city_name)
            if url_result.get("total_collected"):
                self.session_stats["total_urls_collected"] += url_result["total_collected"]
            if crawl_result.get("stats", {}).get("success_count"):
                self.session_stats["total_products_crawled"] += crawl_result["stats"]["success_count"]
            
            self.workflow_results[city_name] = workflow_result
            
            print(f"\n🎉 === '{city_name}' 워크플로우 완료 ===")
            self._print_workflow_summary(workflow_result)
            
            return workflow_result
            
        except Exception as e:
            print(f"\n❌ 워크플로우 실패: {e}")
            workflow_result["success"] = False
            workflow_result["error"] = str(e)
            workflow_result["end_time"] = datetime.now().isoformat()
            
            self.session_stats["errors"].append({
                "stage": "workflow",
                "city": city_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return workflow_result
    
    def _execute_navigation(self, city_name):
        """페이지 네비게이션 실행"""
        try:
            # 메인 페이지 이동
            go_to_main_page(self.driver)
            time.sleep(2)
            
            # 검색 및 필터링
            search_success = False
            if find_and_fill_search(self.driver, city_name):
                if click_search_button(self.driver):
                    time.sleep(3)
                    handle_popup(self.driver)
                    search_success = True
            
            return {
                "success": True,
                "search_performed": search_success,
                "current_url": self.driver.current_url
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_url_collection(self, city_name, strategy):
        """URL 수집 실행"""
        try:
            collection_strategy = self._map_strategy_to_collection(strategy)
            result = execute_comprehensive_url_collection(
                self.driver, 
                city_name, 
                strategy=collection_strategy
            )
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "urls": []
            }
    
    def _execute_crawling(self, urls, city_name, max_products):
        """크롤링 실행"""
        try:
            # URL 제한 적용
            if max_products and len(urls) > max_products:
                urls = urls[:max_products]
                print(f"   🎯 URL 제한 적용: {max_products}개")
            
            result = execute_klook_crawling_system(
                self.driver,
                urls,
                city_name,
                mode="advanced"
            )
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_analysis(self, city_name):
        """데이터 분석 실행"""
        try:
            # CSV 백업
            backup_csv_data(city_name)
            
            # 카테고리 분석
            analysis_result = execute_category_analysis_system(city_name)
            
            return {
                "success": True,
                "category_analysis": analysis_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _map_strategy_to_collection(self, strategy):
        """전략을 URL 수집 전략으로 매핑"""
        strategy_mapping = {
            "quick": "browser_only",
            "standard": "hybrid", 
            "comprehensive": "comprehensive",
            "sitemap": "sitemap_only"
        }
        return strategy_mapping.get(strategy, "hybrid")
    
    def _setup_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            "data", "klook_thumb_img", "url_collected", 
            "hash_index", "ranking_urls", "collection_reports",
            "category_analysis", "failed_urls"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _generate_workflow_summary(self, workflow_result):
        """워크플로우 요약 생성"""
        summary = {
            "total_stages": len(workflow_result["stages"]),
            "successful_stages": sum(1 for stage in workflow_result["stages"].values() if stage.get("success", False)),
            "urls_collected": 0,
            "products_crawled": 0,
            "execution_time": "계산 중"
        }
        
        # URL 수집 통계
        url_stage = workflow_result["stages"].get("url_collection", {})
        if url_stage.get("total_collected"):
            summary["urls_collected"] = url_stage["total_collected"]
        
        # 크롤링 통계
        crawl_stage = workflow_result["stages"].get("crawling", {})
        if crawl_stage.get("stats", {}).get("success_count"):
            summary["products_crawled"] = crawl_stage["stats"]["success_count"]
        
        # 실행 시간 계산
        if workflow_result.get("start_time") and workflow_result.get("end_time"):
            start = datetime.fromisoformat(workflow_result["start_time"])
            end = datetime.fromisoformat(workflow_result["end_time"])
            duration = end - start
            summary["execution_time"] = f"{duration.total_seconds():.1f}초"
        
        return summary
    
    def _print_workflow_summary(self, workflow_result):
        """워크플로우 요약 출력"""
        summary = workflow_result.get("summary", {})
        
        print(f"📊 실행 결과:")
        print(f"   🎯 도시: {workflow_result['city_name']}")
        print(f"   📈 성공 단계: {summary.get('successful_stages', 0)}/{summary.get('total_stages', 0)}")
        print(f"   🔗 수집 URL: {summary.get('urls_collected', 0)}개")
        print(f"   📦 크롤링 상품: {summary.get('products_crawled', 0)}개")
        print(f"   ⏱️ 실행 시간: {summary.get('execution_time', '알 수 없음')}")
    
    def check_system_health(self):
        """시스템 상태 종합 확인"""
        print("🔍 시스템 상태 확인...")
        
        status_report = {
            "overall": "unknown",
            "modules": {},
            "dependencies": {},
            "files": {},
            "config": {}
        }
        
        try:
            # 의존성 확인
            dependencies = check_dependencies()
            status_report["dependencies"] = dependencies
            
            # 시스템 정보
            system_info = get_system_info()
            status_report["config"] = system_info.get("config_settings", {})
            
            # 필요한 디렉토리 확인
            required_dirs = ["data", "klook_thumb_img", "url_collected"]
            for dir_name in required_dirs:
                status_report["files"][dir_name] = os.path.exists(dir_name)
            
            # 전체 상태 판정
            deps_ok = sum(dependencies.values()) >= 4  # 주요 의존성 4개 이상
            files_ok = all(status_report["files"].values())
            
            if deps_ok and files_ok:
                status_report["overall"] = "excellent"
            elif deps_ok:
                status_report["overall"] = "good"
            else:
                status_report["overall"] = "poor"
            
            return status_report
            
        except Exception as e:
            print(f"❌ 상태 확인 중 오류: {e}")
            status_report["overall"] = "error"
            status_report["error"] = str(e)
            return status_report
    
    def cleanup_system(self):
        """시스템 정리 및 리소스 해제"""
        print("🧹 시스템 정리 중...")
        
        try:
            # 세션 통계 업데이트
            self.session_stats["end_time"] = datetime.now()
            
            # 브라우저 유지 (종료하지 않음)
            if self.driver:
                try:
                    # self.driver.quit() - 제거됨: 브라우저 열어두기
                    print("  ✅ 웹드라이버 유지됨 (종료하지 않음)")
                except:
                    print("  ⚠️ 웹드라이버 상태 확인 실패")
                # finally: self.driver = None - 제거됨: 드라이버 레퍼런스 유지
            
            # 세션 결과 저장
            self._save_session_results()
            
            print("🎉 시스템 정리 완료!")
            
        except Exception as e:
            print(f"❌ 시스템 정리 중 오류: {e}")
    
    def _save_session_results(self):
        """세션 결과 저장"""
        try:
            session_dir = "session_reports"
            os.makedirs(session_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"klook_session_{timestamp}.json"
            filepath = os.path.join(session_dir, filename)
            
            session_data = {
                "session_stats": self.session_stats,
                "workflow_results": self.workflow_results
            }
            
            # datetime 객체를 문자열로 변환
            if self.session_stats["start_time"]:
                session_data["session_stats"]["start_time"] = self.session_stats["start_time"].isoformat()
            if self.session_stats["end_time"]:
                session_data["session_stats"]["end_time"] = self.session_stats["end_time"].isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            print(f"  💾 세션 결과 저장: {filename}")
            
        except Exception as e:
            print(f"  ⚠️ 세션 결과 저장 실패: {e}")

# =============================================================================
# 🚀 편의 함수들
# =============================================================================

def quick_start_klook_crawler(city_name="서울", target_products=10, strategy="quick"):
    """빠른 시작 함수"""
    print(f"🚀 KLOOK 크롤러 빠른 시작")
    print(f"🏙️ 도시: {city_name}")
    print(f"🎯 목표: {target_products}개 상품")
    print(f"📊 전략: {strategy}")
    print("=" * 60)
    
    controller = KlookMasterController()
    
    try:
        result = controller.execute_full_workflow(
            city_name, 
            strategy=strategy, 
            max_products=target_products
        )
        return result
        
    finally:
        controller.cleanup_system()

def system_status_check():
    """시스템 상태 확인"""
    controller = KlookMasterController()
    status = controller.check_system_health()
    
    print(f"🎯 전체 상태: {status['overall']}")
    
    if status.get("dependencies"):
        print("\n🔧 의존성 상태:")
        for dep, available in status["dependencies"].items():
            emoji = "✅" if available else "❌"
            print(f"  {emoji} {dep}")
    
    if status.get("files"):
        print("\n📁 디렉토리 상태:")
        for dir_name, exists in status["files"].items():
            emoji = "✅" if exists else "❌"
            print(f"  {emoji} {dir_name}")
    
    return status

def interactive_klook_crawler():
    """대화형 KLOOK 크롤러"""
    print("🎮 대화형 KLOOK 크롤러")
    print("=" * 40)
    
    try:
        # 도시 목록 표시
        print("🏙️ 사용 가능한 도시:")
        city_list = list(UNIFIED_CITY_INFO.keys())[:10]  # 상위 10개만 표시
        for i, city in enumerate(city_list, 1):
            print(f"  {i}. {city}")
        print("  ... (더 많은 도시 사용 가능)")
        
        # 도시 선택
        city_name = input("\n크롤링할 도시를 입력하세요 (기본값: 서울): ").strip()
        if not city_name:
            city_name = "서울"
        
        # 전략 선택
        print("\n📊 사용 가능한 전략:")
        print("  1. quick - 빠른 테스트 (브라우저만)")
        print("  2. standard - 표준 수집 (하이브리드)")
        print("  3. comprehensive - 완전 수집 (모든 방법)")
        
        strategy_input = input("전략을 선택하세요 (1-3, 기본값: 2): ").strip()
        strategy_map = {"1": "quick", "2": "standard", "3": "comprehensive"}
        strategy = strategy_map.get(strategy_input, "standard")
        
        # 목표 상품 수
        target_input = input("목표 상품 수 (기본값: 50): ").strip()
        try:
            target_products = int(target_input) if target_input else 50
        except:
            target_products = 50
        
        print(f"\n🎯 설정 확인:")
        print(f"  🏙️ 도시: {city_name}")
        print(f"  📊 전략: {strategy}")
        print(f"  🎯 목표: {target_products}개 상품")
        
        confirm = input("\n실행하시겠습니까? (y/N): ").strip().lower()
        if confirm in ['y', 'yes', '예']:
            return quick_start_klook_crawler(city_name, target_products, strategy)
        else:
            print("❌ 실행이 취소되었습니다.")
            return None
            
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
        return None
    except Exception as e:
        print(f"❌ 대화형 실행 중 오류: {e}")
        return None

def batch_city_crawler(city_list, strategy="standard", max_products=100):
    """다중 도시 배치 크롤링"""
    print(f"🏙️ 배치 크롤링: {len(city_list)}개 도시")
    print(f"📊 전략: {strategy}")
    print("=" * 60)
    
    controller = KlookMasterController()
    batch_results = {}
    
    try:
        for i, city_name in enumerate(city_list, 1):
            print(f"\n[{i}/{len(city_list)}] '{city_name}' 처리 중...")
            
            try:
                result = controller.execute_full_workflow(
                    city_name, 
                    strategy=strategy, 
                    max_products=max_products
                )
                batch_results[city_name] = result
                
                # 도시 간 대기
                if i < len(city_list):
                    wait_time = 30  # 30초 대기
                    print(f"⏱️ 다음 도시까지 {wait_time}초 대기...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                print(f"❌ '{city_name}' 처리 실패: {e}")
                batch_results[city_name] = {"success": False, "error": str(e)}
                continue
        
        # 배치 결과 요약
        print(f"\n🎉 배치 크롤링 완료!")
        successful = sum(1 for result in batch_results.values() if result.get("success", False))
        print(f"📊 성공: {successful}/{len(city_list)}개 도시")
        
        return batch_results
        
    finally:
        controller.cleanup_system()

def test_system_functionality():
    """시스템 기능 테스트"""
    print("🧪 KLOOK 크롤링 시스템 기능 테스트")
    print("=" * 60)
    
    test_results = {
        "system_health": False,
        "driver_init": False,
        "navigation": False,
        "url_collection": False,
        "data_extraction": False
    }
    
    controller = KlookMasterController()
    
    try:
        # 1. 시스템 상태 테스트
        print("1️⃣ 시스템 상태 테스트...")
        status = controller.check_system_health()
        test_results["system_health"] = status["overall"] in ["excellent", "good"]
        print(f"   결과: {'✅' if test_results['system_health'] else '❌'}")
        
        # 2. 드라이버 초기화 테스트
        print("2️⃣ 드라이버 초기화 테스트...")
        init_success = controller.initialize_system("서울")
        test_results["driver_init"] = init_success
        print(f"   결과: {'✅' if test_results['driver_init'] else '❌'}")
        
        if not init_success:
            return test_results
        
        # 3. 네비게이션 테스트
        print("3️⃣ 페이지 네비게이션 테스트...")
        nav_result = controller._execute_navigation("서울")
        test_results["navigation"] = nav_result["success"]
        print(f"   결과: {'✅' if test_results['navigation'] else '❌'}")
        
        # 4. 간단한 URL 수집 테스트
        print("4️⃣ URL 수집 테스트...")
        try:
            test_urls = controller.driver.find_elements("css selector", "a[href*='/activity/']")
            test_results["url_collection"] = len(test_urls) > 0
            print(f"   결과: {'✅' if test_results['url_collection'] else '❌'} ({len(test_urls)}개 URL 발견)")
        except:
            test_results["url_collection"] = False
            print(f"   결과: ❌")
        
        # 5. 데이터 추출 테스트 (첫 번째 URL로)
        if test_results["url_collection"] and len(test_urls) > 0:
            print("5️⃣ 데이터 추출 테스트...")
            try:
                test_url = test_urls[0].get_attribute('href')
                controller.driver.get(test_url)
                time.sleep(3)
                
                # 간단한 정보 추출 시도
                title = controller.driver.title
                test_results["data_extraction"] = bool(title and len(title) > 0)
                print(f"   결과: {'✅' if test_results['data_extraction'] else '❌'}")
            except:
                test_results["data_extraction"] = False
                print(f"   결과: ❌")
        
        # 테스트 요약
        print(f"\n🧪 테스트 요약:")
        passed = sum(test_results.values())
        total = len(test_results)
        
        for test_name, result in test_results.items():
            emoji = "✅" if result else "❌"
            print(f"   {emoji} {test_name}")
        
        print(f"\n📊 전체 결과: {passed}/{total} 통과")
        
        return test_results
        
    finally:
        controller.cleanup_system()

# 호환성을 위한 별칭 함수들
def execute_complete_klook_workflow(city_name, target_products=100, interactive_mode=False):
    """전체 워크플로우 실행 (호환성용)"""
    strategy = "standard" if target_products <= 100 else "comprehensive"
    return quick_start_klook_crawler(city_name, target_products, strategy)

def cleanup_system():
    """시스템 정리 (호환성용)"""
    controller = KlookMasterController()
    controller.cleanup_system()

# =============================================================================
# 📄 페이지네이션 고급 기능 (원본에서 누락된 기능)
# =============================================================================

def analyze_pagination(driver):
    """페이지네이션 정보 분석 (총 페이지 수, 상품 수 파악)"""
    try:
        from selenium.webdriver.common.by import By
        
        print("📄 페이지네이션 정보 분석 중...")
        
        analysis = {
            "total_pages": 0,
            "current_page": 1,
            "total_products": 0,
            "products_per_page": 0,
            "pagination_type": "unknown"
        }
        
        # 페이지 정보 셀렉터들
        page_info_selectors = [
            # KLOOK 페이지네이션 패턴들
            "[data-testid='pagination-info']",
            ".pagination-info",
            ".page-info",
            "[class*='pagination'][class*='info']"
        ]
        
        # 총 페이지 수 찾기
        page_number_selectors = [
            ".pagination .page-link:last-child",
            ".pagination a:last-child",
            "[data-testid='last-page']",
            ".pager .last"
        ]
        
        for selector in page_number_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text.isdigit():
                        analysis["total_pages"] = int(text)
                        break
                if analysis["total_pages"] > 0:
                    break
            except:
                continue
        
        # 상품 수 정보 찾기
        product_count_selectors = [
            "[data-testid='total-count']",
            ".total-count",
            ".results-count",
            "[class*='count']"
        ]
        
        for selector in product_count_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    # 숫자 추출
                    import re
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        analysis["total_products"] = int(numbers[0])
                        break
                if analysis["total_products"] > 0:
                    break
            except:
                continue
        
        # 현재 페이지의 상품 수 계산
        try:
            product_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/activity/']")
            analysis["products_per_page"] = len(product_elements)
        except:
            pass
        
        print(f"    📊 페이지네이션 분석 결과:")
        print(f"       총 페이지: {analysis['total_pages']}")
        print(f"       현재 페이지: {analysis['current_page']}")
        print(f"       총 상품 수: {analysis['total_products']}")
        print(f"       페이지당 상품: {analysis['products_per_page']}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ 페이지네이션 분석 실패: {e}")
        return {"error": str(e)}

def check_next_button(driver):
    """KLOOK 다음 페이지 버튼 작동 확인"""
    try:
        from selenium.webdriver.common.by import By
        
        next_selectors = [
            "[data-testid='pagination-next']",
            "[aria-label='다음']",
            "[aria-label='Next']",
            ".pagination .next",
            ".pager .next"
        ]
        
        for selector in next_selectors:
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, selector)
                if next_button.is_displayed() and next_button.is_enabled():
                    # disabled 클래스 확인
                    classes = next_button.get_attribute("class") or ""
                    if "disabled" not in classes.lower():
                        print("    ✅ 다음 페이지 버튼 사용 가능")
                        return True
            except:
                continue
        
        print("    ❌ 다음 페이지 버튼 없음 또는 비활성화")
        return False
        
    except Exception as e:
        print(f"    ⚠️ 다음 버튼 확인 실패: {e}")
        return False

def click_next_page_enhanced(driver, current_page):
    """향상된 다음 페이지 클릭"""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        print(f"    🔄 페이지 {current_page + 1}로 이동 시도...")
        
        # 현재 URL 저장 (변경 확인용)
        current_url = driver.current_url
        
        # 다음 페이지 버튼 찾기 및 클릭
        next_selectors = [
            "[data-testid='pagination-next']",
            "[aria-label='다음']",
            "[aria-label='Next']",
            ".pagination .next:not(.disabled)",
            ".pager .next:not(.disabled)"
        ]
        
        for selector in next_selectors:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                # JavaScript 클릭 시도
                driver.execute_script("arguments[0].click();", next_button)
                
                # 페이지 변경 대기 (URL 변경 또는 로딩 완료)
                WebDriverWait(driver, 10).until(
                    lambda d: d.current_url != current_url or 
                    d.execute_script("return document.readyState") == "complete"
                )
                
                print(f"    ✅ 페이지 {current_page + 1} 이동 완료")
                return True
                
            except Exception as e:
                continue
        
        print(f"    ❌ 페이지 {current_page + 1} 이동 실패")
        return False
        
    except Exception as e:
        print(f"    ❌ Enhanced 페이지 이동 실패: {e}")
        return False

def save_pagination_state(city_name, current_page, current_list_url, total_crawled, target_products):
    """페이지네이션 상태 저장"""
    try:
        state_dir = "pagination_states"
        os.makedirs(state_dir, exist_ok=True)
        
        city_code = get_city_code(city_name)
        state_file = os.path.join(state_dir, f"{city_code}_pagination_state.json")
        
        state_data = {
            "city_name": city_name,
            "current_page": current_page,
            "current_list_url": current_list_url,
            "total_crawled": total_crawled,
            "target_products": target_products,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 페이지네이션 상태 저장: 페이지 {current_page}")
        return True
        
    except Exception as e:
        print(f"❌ 페이지네이션 상태 저장 실패: {e}")
        return False

def load_pagination_state(city_name):
    """페이지네이션 상태 로드"""
    try:
        state_dir = "pagination_states"
        city_code = get_city_code(city_name)
        state_file = os.path.join(state_dir, f"{city_code}_pagination_state.json")
        
        if not os.path.exists(state_file):
            return None
        
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        print(f"📂 페이지네이션 상태 로드: 페이지 {state_data.get('current_page', 1)}")
        return state_data
        
    except Exception as e:
        print(f"❌ 페이지네이션 상태 로드 실패: {e}")
        return None

def clear_pagination_state(city_name):
    """페이지네이션 상태 초기화"""
    try:
        state_dir = "pagination_states"
        city_code = get_city_code(city_name)
        state_file = os.path.join(state_dir, f"{city_code}_pagination_state.json")
        
        if os.path.exists(state_file):
            os.remove(state_file)
            print(f"🗑️ 페이지네이션 상태 초기화 완료")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ 페이지네이션 상태 초기화 실패: {e}")
        return False

def generate_crawling_plan(pagination_info, city_name):
    """크롤링 계획 생성 및 보고"""
    try:
        print(f"📋 '{city_name}' 크롤링 계획 생성 중...")
        
        plan = {
            "city_name": city_name,
            "pagination_analysis": pagination_info,
            "estimated_time": 0,
            "recommended_strategy": "unknown",
            "warnings": [],
            "optimizations": []
        }
        
        total_pages = pagination_info.get("total_pages", 0)
        products_per_page = pagination_info.get("products_per_page", 20)
        total_products = pagination_info.get("total_products", 0)
        
        # 예상 시간 계산 (페이지당 평균 30초)
        if total_pages > 0:
            plan["estimated_time"] = total_pages * 30  # 초 단위
        
        # 전략 추천
        if total_products <= 100:
            plan["recommended_strategy"] = "quick"
        elif total_products <= 500:
            plan["recommended_strategy"] = "standard"
        else:
            plan["recommended_strategy"] = "comprehensive"
        
        # 경고 및 최적화 제안
        if total_pages > 50:
            plan["warnings"].append("페이지 수가 많아 시간이 오래 걸릴 수 있습니다")
            plan["optimizations"].append("배치 크기를 줄이거나 병렬 처리를 고려하세요")
        
        if products_per_page > 50:
            plan["optimizations"].append("페이지당 상품 수가 많아 로딩 시간이 길 수 있습니다")
        
        print(f"    📊 계획 완료:")
        print(f"       추천 전략: {plan['recommended_strategy']}")
        print(f"       예상 시간: {plan['estimated_time']//60}분 {plan['estimated_time']%60}초")
        print(f"       경고사항: {len(plan['warnings'])}개")
        
        return plan
        
    except Exception as e:
        print(f"❌ 크롤링 계획 생성 실패: {e}")
        return {"error": str(e)}

# =============================================================================
# 🏃 빠른 실행 모듈 (원본에서 누락된 기능)
# =============================================================================

def quick_start_ranking_collection(city_name, driver, strategy="hybrid"):
    """빠른 시작: 순위 수집만"""
    print(f"🏃 빠른 순위 수집 시작: {city_name}")
    print(f"📊 전략: {strategy}")
    print("=" * 60)
    
    try:
        # 탭 시스템을 통한 순위 수집
        from .tab_selector import execute_integrated_tab_selector_system
        
        result = execute_integrated_tab_selector_system(city_name, driver, interactive_mode=False)
        
        if result.get("success", False):
            print(f"✅ 빠른 순위 수집 완료: {result.get('total_collected', 0)}개 URL")
            return result
        else:
            print("❌ 빠른 순위 수집 실패")
            return {"success": False, "error": "Tab selector failed"}
            
    except Exception as e:
        print(f"❌ 빠른 순위 수집 실패: {e}")
        return {"success": False, "error": str(e)}

def quick_start_full_system(city_name, driver):
    """빠른 시작: 전체 시스템"""
    print(f"🚀 빠른 전체 시스템 시작: {city_name}")
    print("=" * 60)
    
    controller = KlookMasterController()
    
    try:
        # 시스템 상태 확인
        status = controller.check_system_health()
        if status["overall"] in ["poor", "error"]:
            print("⚠️ 시스템 상태가 불량합니다. 계속 진행하시겠습니까?")
        
        # 전체 워크플로우 실행 (표준 모드)
        result = controller.execute_full_workflow(city_name, strategy="standard", max_products=50)
        
        return result
        
    except Exception as e:
        print(f"❌ 빠른 전체 시스템 실패: {e}")
        return {"success": False, "error": str(e)}
    finally:
        controller.cleanup_system()

def validate_system_integration(driver, test_city="서울"):
    """시스템 통합 검증"""
    print(f"🧪 시스템 통합 검증 시작: {test_city}")
    print("=" * 60)
    
    validation_results = {
        "driver_health": False,
        "config_loaded": False,
        "modules_imported": False,
        "basic_navigation": False,
        "url_collection": False,
        "data_extraction": False,
        "overall_status": "failed"
    }
    
    try:
        # 1. 드라이버 상태 확인
        try:
            driver.execute_script("return document.readyState;")
            validation_results["driver_health"] = True
            print("✅ 드라이버 상태: 정상")
        except:
            print("❌ 드라이버 상태: 비정상")
        
        # 2. 설정 확인
        try:
            from .config import CONFIG, UNIFIED_CITY_INFO
            validation_results["config_loaded"] = True
            print("✅ 설정 로드: 성공")
        except:
            print("❌ 설정 로드: 실패")
        
        # 3. 모듈 import 확인
        try:
            from .url_collection import collect_urls_from_current_page
            from .crawler_engine import KlookCrawlerEngine
            from .data_handler import save_to_csv_klook
            validation_results["modules_imported"] = True
            print("✅ 모듈 import: 성공")
        except Exception as e:
            print(f"❌ 모듈 import: 실패 - {e}")
        
        # 4. 기본 네비게이션 테스트
        try:
            from .driver_manager import go_to_main_page
            go_to_main_page(driver)
            validation_results["basic_navigation"] = True
            print("✅ 기본 네비게이션: 성공")
        except Exception as e:
            print(f"❌ 기본 네비게이션: 실패 - {e}")
        
        # 5. URL 수집 테스트
        try:
            test_urls = collect_urls_from_current_page(driver, limit=5)
            if test_urls:
                validation_results["url_collection"] = True
                print(f"✅ URL 수집: 성공 ({len(test_urls)}개)")
            else:
                print("❌ URL 수집: 실패 (URL 없음)")
        except Exception as e:
            print(f"❌ URL 수집: 실패 - {e}")
        
        # 6. 데이터 추출 테스트 (간단)
        try:
            from .system_utils import get_product_name
            test_name = get_product_name(driver)
            if test_name and test_name != "정보 없음":
                validation_results["data_extraction"] = True
                print("✅ 데이터 추출: 성공")
            else:
                print("❌ 데이터 추출: 실패")
        except Exception as e:
            print(f"❌ 데이터 추출: 실패 - {e}")
        
        # 전체 상태 판정
        passed_tests = sum(validation_results.values() if isinstance(v, bool) else 0 for v in validation_results.values())
        total_tests = len([k for k in validation_results.keys() if k != "overall_status"])
        
        if passed_tests >= total_tests * 0.8:
            validation_results["overall_status"] = "excellent"
        elif passed_tests >= total_tests * 0.6:
            validation_results["overall_status"] = "good"
        else:
            validation_results["overall_status"] = "poor"
        
        print(f"\n🎯 통합 검증 결과: {validation_results['overall_status']}")
        print(f"📊 통과: {passed_tests}/{total_tests} 테스트")
        
        return validation_results
        
    except Exception as e:
        print(f"❌ 시스템 통합 검증 실패: {e}")
        validation_results["overall_status"] = "error"
        return validation_results

def generate_system_report(city_name, execution_result):
    """시스템 실행 보고서 생성"""
    try:
        report_dir = "system_reports"
        os.makedirs(report_dir, exist_ok=True)
        
        city_code = get_city_code(city_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{city_code}_system_report_{timestamp}.json"
        filepath = os.path.join(report_dir, filename)
        
        # 보고서 데이터 구성
        report_data = {
            "city_name": city_name,
            "city_code": city_code,
            "execution_result": execution_result,
            "generated_at": datetime.now().isoformat(),
            "system_info": get_system_info(),
            "performance_metrics": {
                "total_execution_time": execution_result.get("summary", {}).get("execution_time", "알 수 없음"),
                "urls_collected": execution_result.get("summary", {}).get("urls_collected", 0),
                "products_crawled": execution_result.get("summary", {}).get("products_crawled", 0),
                "success_rate": "계산 중"
            }
        }
        
        # 성공률 계산
        stages = execution_result.get("stages", {})
        successful_stages = sum(1 for stage in stages.values() if stage.get("success", False))
        total_stages = len(stages)
        if total_stages > 0:
            success_rate = (successful_stages / total_stages) * 100
            report_data["performance_metrics"]["success_rate"] = f"{success_rate:.1f}%"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 시스템 보고서 저장: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ 시스템 보고서 생성 실패: {e}")
        return False

def run_complete_klook_system(city_name, driver, config=None):
    """완전한 KLOOK 시스템 실행"""
    print(f"🎯 완전한 KLOOK 시스템 실행: {city_name}")
    print("=" * 80)
    
    if not config:
        config = {
            "strategy": "comprehensive",
            "max_products": 1000,
            "enable_pagination": True,
            "enable_analysis": True,
            "save_reports": True
        }
    
    controller = KlookMasterController()
    
    try:
        # 1. 시스템 통합 검증
        print("🧪 1단계: 시스템 통합 검증...")
        validation_result = validate_system_integration(driver, city_name)
        
        if validation_result["overall_status"] in ["poor", "error"]:
            print("⚠️ 시스템 검증 실패. 계속 진행하시겠습니까?")
        
        # 2. 페이지네이션 분석
        if config.get("enable_pagination", True):
            print("\n📄 2단계: 페이지네이션 분석...")
            pagination_info = analyze_pagination(driver)
            
            # 크롤링 계획 생성
            crawling_plan = generate_crawling_plan(pagination_info, city_name)
            print(f"📋 크롤링 계획: {crawling_plan.get('recommended_strategy', 'standard')}")
        
        # 3. 전체 워크플로우 실행
        print("\n🚀 3단계: 전체 워크플로우 실행...")
        execution_result = controller.execute_full_workflow(
            city_name, 
            strategy=config.get("strategy", "comprehensive"),
            max_products=config.get("max_products", 1000)
        )
        
        # 4. 시스템 보고서 생성
        if config.get("save_reports", True):
            print("\n📊 4단계: 시스템 보고서 생성...")
            generate_system_report(city_name, execution_result)
        
        print(f"\n🎉 완전한 KLOOK 시스템 실행 완료!")
        return execution_result
        
    except Exception as e:
        print(f"❌ 완전한 KLOOK 시스템 실행 실패: {e}")
        return {"success": False, "error": str(e)}
    finally:
        controller.cleanup_system()

print("✅ 그룹 11,11.5 완료: KLOOK 크롤링 제어 시스템 (완전 통합 버전)!")
print("   🎮 마스터 컨트롤:")
print("   - KlookMasterController: 전체 시스템 통합 관리")
print("   - execute_full_workflow(): 완전 워크플로우 실행")
print("   🚀 편의 함수:")
print("   - quick_start_klook_crawler(): 빠른 시작")
print("   - interactive_klook_crawler(): 대화형 실행")
print("   - batch_city_crawler(): 다중 도시 배치 크롤링")
print("   📄 페이지네이션 고급 (추가됨):")
print("   - analyze_pagination(): 페이지네이션 정보 분석")
print("   - check_next_button(): 다음 페이지 버튼 확인")
print("   - click_next_page_enhanced(): 향상된 페이지 이동")
print("   - save/load/clear_pagination_state(): 페이지네이션 상태 관리")
print("   - generate_crawling_plan(): 크롤링 계획 생성")
print("   🏃 빠른 실행 (추가됨):")
print("   - quick_start_ranking_collection(): 빠른 순위 수집")
print("   - quick_start_full_system(): 빠른 전체 시스템")
print("   - validate_system_integration(): 시스템 통합 검증")
print("   - generate_system_report(): 시스템 보고서 생성")
print("   - run_complete_klook_system(): 완전한 시스템 실행")
print("   🧪 테스트 및 모니터링:")
print("   - test_system_functionality(): 시스템 기능 테스트")
print("   - system_status_check(): 시스템 상태 확인")
print("   ⚙️ 지원 전략: quick, standard, comprehensive")