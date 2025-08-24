"""
🚀 그룹 8: KLOOK URL 수집 시스템
- 페이지네이션 기반 URL 수집
- Sitemap 및 브라우저 수집 통합
- 다양한 수집 전략 지원
"""

import os
import time
import random
import json
import re
from datetime import datetime
from urllib.parse import urlparse, urljoin, parse_qs, urlunparse

# 조건부 import
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    print("⚠️ Selenium이 설치되지 않았습니다. URL 수집 기능이 제한됩니다.")
    SELENIUM_AVAILABLE = False

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    print("⚠️ requests 또는 beautifulsoup4가 설치되지 않았습니다. Sitemap 수집 기능이 제한됩니다.")
    REQUESTS_AVAILABLE = False

# config 모듈에서 필요한 함수들 import
from .config import CONFIG, get_city_code, get_city_info
from .url_manager import is_valid_klook_url, normalize_klook_url, save_urls_to_collection

# =============================================================================
# 🔍 페이지네이션 기반 URL 수집
# =============================================================================

def collect_urls_with_pagination(driver, city_name, max_pages=10, strategy="smart"):
    """🔍 페이지네이션을 통한 체계적 URL 수집"""
    if not SELENIUM_AVAILABLE:
        return []
    
    print(f"🔍 '{city_name}' 페이지네이션 URL 수집 시작 (최대 {max_pages}페이지)")
    print(f"📊 전략: {strategy}")
    
    collected_urls = []
    current_page = 1
    
    while current_page <= max_pages:
        print(f"\n📄 페이지 {current_page}/{max_pages} 수집 중...")
        
        try:
            # 현재 페이지에서 URL 수집 (좌표 기반 정렬)
            # KLOOK 페이지에서는 페이지당 15개 정도이므로 충분히 수집
            # 설정값 사용 (전역변수에서 가져오기)
            collect_limit = globals().get('MAX_COLLECT_LIMIT', 50)
            page_urls = collect_urls_from_current_page_by_coordinates(driver, limit=collect_limit)
            
            if not page_urls:
                print(f"    ⚠️ 페이지 {current_page}에서 URL을 찾지 못했습니다")
                if strategy == "strict":
                    break  # strict 모드에서는 빈 페이지 발견시 중단
                else:
                    current_page += 1
                    continue
            
            # 유효한 KLOOK URL만 필터링
            valid_urls = [url for url in page_urls if is_valid_klook_url(url)]
            collected_urls.extend(valid_urls)
            
            print(f"    ✅ 페이지 {current_page}: {len(valid_urls)}개 URL 수집")
            
            # 다음 페이지로 이동
            if current_page < max_pages:
                next_success = navigate_to_next_page(driver, current_page)
                if not next_success:
                    print(f"    ⚠️ 다음 페이지로 이동 실패 - 수집 중단")
                    break
            
            current_page += 1
            
            # 자연스러운 대기
            time.sleep(random.uniform(
                CONFIG.get("MEDIUM_MIN_DELAY", 2),
                CONFIG.get("MEDIUM_MAX_DELAY", 4)
            ))
            
        except Exception as e:
            print(f"    ❌ 페이지 {current_page} 수집 실패: {e}")
            if strategy == "strict":
                break
            current_page += 1
            continue
    
    # 중복 제거
    unique_urls = list(set(collected_urls))
    print(f"\n🎉 페이지네이션 수집 완료!")
    print(f"   📊 총 {current_page - 1}페이지 처리")
    print(f"   🔗 수집된 URL: {len(unique_urls)}개 (중복 제거 후)")
    
    return unique_urls

def collect_urls_from_current_page_by_coordinates(driver, limit=100):
    """현재 페이지에서 KLOOK URL 수집 (좌표 기반 정렬로 시각적 순서 보장)"""
    if not SELENIUM_AVAILABLE:
        return []
    
    print(f"      📍 좌표 기반 URL 수집 시작 (최대 {limit}개)")
    
    # 동적 로딩 대기
    try:
        print(f"      ⏱️ 페이지 로딩 대기 중...")
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "a[href*='/activity/']")) > 0
        )
        print(f"      ✅ 로딩 완료")
        time.sleep(3)  # 충분한 대기
    except Exception as e:
        print(f"      ⚠️ 로딩 대기 실패: {e}")
        time.sleep(2)
    
    # 페이지 스크롤로 모든 상품 로딩
    try:
        print(f"      📜 전체 상품 로딩을 위한 스크롤...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    except Exception as e:
        print(f"      ⚠️ 스크롤 실패: {e}")
    
    # 다양한 셀렉터로 모든 activity URL 수집
    selectors = [
        "a[href*='/activity/']",
        ".result-card-list a[href*='/activity/']", 
        ".search-result-list a[href*='/activity/']",
        "[data-testid*='product'] a[href*='/activity/']",
        ".product-card a[href*='/activity/']"
    ]
    
    all_elements_with_coords = []
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"      🔎 '{selector}': {len(elements)}개 요소 발견")
            
            for element in elements:
                try:
                    href = element.get_attribute('href')
                    if href and is_valid_klook_url(href):
                        normalized_url = normalize_klook_url(href)
                        
                        # 중복 체크
                        if any(item['url'] == normalized_url for item in all_elements_with_coords):
                            continue
                        
                        # 요소가 화면에 보이는지 확인
                        if element.is_displayed():
                            location = element.location
                            y_coord = location.get('y', 0)
                            x_coord = location.get('x', 0)
                            
                            # 화면에 실제로 표시된 요소만 선택
                            if y_coord > 0:
                                all_elements_with_coords.append({
                                    'url': normalized_url,
                                    'y': y_coord,
                                    'x': x_coord,
                                    'element': element
                                })
                        
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"      ⚠️ 셀렉터 '{selector}' 실패: {e}")
            continue
    
    # 좌표로 정렬: Y좌표 우선 (위→아래), 같으면 X좌표 (왼쪽→오른쪽)
    all_elements_with_coords.sort(key=lambda item: (item['y'], item['x']))
    
    # 정렬된 순서대로 URL 수집
    collected_urls = []
    for i, item in enumerate(all_elements_with_coords[:limit]):
        collected_urls.append(item['url'])
        url_name = item['url'].split('/')[-1].replace('-', ' ')[:40]
        print(f"        📍 {i+1}위: Y={item['y']:4d} | {url_name}")
    
    print(f"      ✅ 좌표 기반 정렬 완료: {len(collected_urls)}개 URL")
    return collected_urls

def collect_urls_from_current_page(driver, limit=100):
    """현재 페이지에서 KLOOK URL 수집 (페이지 순서대로)"""
    if not SELENIUM_AVAILABLE:
        return []
    
    collected_urls = []
    
    # KLOOK 상품 URL 셀렉터들 (페이지 순서 보장)
    # 실제 분석 결과를 바탕으로 한 정확한 셀렉터
    url_selectors = [
        # 🎯 KLOOK 2024 구조 기반 - result-card-list 내부 순서 보장
        ".result-card-list a[href*='/activity/']",
        ".search-result-list a[href*='/activity/']",
        
        # 기존 KLOOK 최적화 셀렉터들 (백업)
        "[data-testid*='product'] a[href*='/activity/']",
        ".product-card a[href*='/activity/']",
        ".activity-card a[href*='/activity/']",
        "[class*='card'] a[href*='/activity/']",
        
        # 순서 보장 셀렉터들 (DOM 트리 순서대로)
        "div[class*='product'] a[href*='/activity/'], div[class*='item'] a[href*='/activity/'], div[class*='card'] a[href*='/activity/']",
        
        # 일반적인 KLOOK 패턴 (순서 중요)
        "a[href*='/activity/']",
        "a[href*='/ko/activity/']",
        "a[href*='/en/activity/']",
        
        # 백업 셀렉터들
        "a[href*='klook.com'][href*='activity']",
        "[class*='product'] a",
        "[class*='item'] a",
        ".list-item a"
    ]
    
    print(f"      📍 페이지 순서대로 URL 수집 시작 (최대 {limit}개)")
    
    # 동적 로딩 대기 (KLOOK 페이지 최적화 - result-card-list 기반)
    try:
        print(f"      ⏱️ 페이지 동적 로딩 대기 중...")
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, ".result-card-list a[href*='/activity/']")) > 0
        )
        print(f"      ✅ 동적 로딩 완료")
        # 추가 안정화 대기
        time.sleep(2)
    except Exception as e:
        print(f"      ⚠️ 동적 로딩 대기 실패: {e}")
        # 백업 대기 - 일반 셀렉터로 재시도
        try:
            WebDriverWait(driver, 5).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "a[href*='/activity/']")) > 0
            )
            print(f"      ✅ 백업 동적 로딩 완료")
            time.sleep(2)
        except Exception as backup_e:
            print(f"      ⚠️ 백업 동적 로딩도 실패: {backup_e}")
    
    for selector in url_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"      🔎 '{selector}': {len(elements)}개 요소 발견")
            
            temp_urls = []
            for i, element in enumerate(elements):
                try:
                    href = element.get_attribute('href')
                    if href and is_valid_klook_url(href):
                        normalized_url = normalize_klook_url(href)
                        if normalized_url not in temp_urls and normalized_url not in collected_urls:
                            temp_urls.append(normalized_url)
                            print(f"        📍 순서 {i+1}: {normalized_url.split('/')[-1][:50]}...")
                            
                        if len(temp_urls) >= limit:
                            break
                            
                except Exception:
                    continue
            
            if temp_urls:
                collected_urls.extend(temp_urls[:limit])
                print(f"      ✅ 셀렉터에서 {len(temp_urls)}개 URL 수집 (페이지 순서 보장)")
                break  # 첫 번째 성공한 셀렉터에서 수집 완료
                
        except Exception as e:
            print(f"      ⚠️ 셀렉터 '{selector}' 실패: {e}")
            continue
    
    print(f"      📊 최종 수집: {len(collected_urls)}개 URL (순서 보장)")
    return collected_urls[:limit]

def navigate_to_next_page(driver, current_page):
    """다음 페이지로 이동 (통합 페이지네이션 매니저 사용)"""
    if not SELENIUM_AVAILABLE:
        return False
    
    try:
        from .pagination_utils import KlookPageTool
        
        # 테스트 검증된 KLOOK 페이지 도구 사용
        page_tool = KlookPageTool(driver)
        
        # 부드러운 스크롤로 페이지네이션 영역 찾기
        page_tool.smooth_scroll_to_pagination()
        
        # 고급 다음 페이지 클릭
        current_url = driver.current_url
        result = page_tool.click_next_page(current_url)
        
        if result['success']:
            print(f"    ✅ 페이지 {current_page + 1}로 이동 성공 (방법: {result['method']})")
            return True
        else:
            print(f"    ❌ 페이지 {current_page + 1}로 이동 실패")
            return False
            
    except Exception as e:
        print(f"    ❌ 페이지 이동 실패: {e}")
        return False

# =============================================================================
# 🗺️ Sitemap 기반 URL 수집
# =============================================================================

def collect_urls_from_sitemap(city_name, limit=1000):
    """Sitemap에서 KLOOK URL 수집"""
    if not REQUESTS_AVAILABLE:
        print("❌ requests/beautifulsoup4가 설치되지 않았습니다.")
        return []
    
    print(f"🗺️ '{city_name}' Sitemap URL 수집 시작...")
    
    # KLOOK sitemap URL들
    sitemap_urls = [
        "https://www.klook.com/sitemap.xml",
        "https://www.klook.com/sitemap-activities.xml",
        "https://www.klook.com/sitemap-ko.xml",
        f"https://www.klook.com/sitemap-{city_name.lower()}.xml"
    ]
    
    collected_urls = []
    
    for sitemap_url in sitemap_urls:
        try:
            print(f"  📋 Sitemap 처리 중: {sitemap_url}")
            
            response = requests.get(sitemap_url, timeout=30, headers={
                'User-Agent': CONFIG.get("USER_AGENT", "Mozilla/5.0")
            })
            
            if response.status_code == 200:
                # XML 파싱
                soup = BeautifulSoup(response.content, 'xml')
                
                # URL 추출
                urls = soup.find_all('url')
                for url_element in urls:
                    loc = url_element.find('loc')
                    if loc and loc.text:
                        url = loc.text.strip()
                        
                        # KLOOK activity URL 필터링
                        if is_valid_klook_url(url):
                            # 도시명과 관련된 URL 필터링 (선택적)
                            if city_name.lower() in url.lower() or len(collected_urls) < limit:
                                normalized_url = normalize_klook_url(url)
                                if normalized_url not in collected_urls:
                                    collected_urls.append(normalized_url)
                                    
                                    if len(collected_urls) >= limit:
                                        break
                
                print(f"    ✅ {len([u for u in collected_urls])}개 URL 발견")
                
            else:
                print(f"    ⚠️ Sitemap 접근 실패: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Sitemap 처리 실패: {e}")
            continue
    
    unique_urls = list(set(collected_urls))
    print(f"🎉 Sitemap 수집 완료: {len(unique_urls)}개 URL (중복 제거 후)")
    
    return unique_urls[:limit]

# =============================================================================
# 🔄 통합 URL 수집 시스템
# =============================================================================

def execute_comprehensive_url_collection(driver, city_name, strategy="hybrid"):
    """통합 URL 수집 시스템 실행"""
    print(f"🚀 '{city_name}' 통합 URL 수집 시작!")
    print(f"📊 전략: {strategy}")
    print("=" * 80)
    
    all_collected_urls = []
    collection_results = {}
    
    # 전략별 수집 실행
    if strategy == "browser_only":
        # 브라우저 수집만
        print("\n🌐 브라우저 기반 수집 실행...")
        browser_urls = collect_urls_with_pagination(driver, city_name, max_pages=5)
        all_collected_urls.extend(browser_urls)
        collection_results["browser"] = len(browser_urls)
        
    elif strategy == "sitemap_only":
        # Sitemap 수집만
        print("\n🗺️ Sitemap 기반 수집 실행...")
        sitemap_urls = collect_urls_from_sitemap(city_name, limit=500)
        all_collected_urls.extend(sitemap_urls)
        collection_results["sitemap"] = len(sitemap_urls)
        
    elif strategy == "hybrid":
        # 하이브리드 (브라우저 + Sitemap)
        print("\n🔀 하이브리드 수집 실행...")
        
        # 1. 브라우저 수집 (순위 정보 포함)
        print("\n  🌐 1단계: 브라우저 수집...")
        browser_urls = collect_urls_with_pagination(driver, city_name, max_pages=3)
        all_collected_urls.extend(browser_urls)
        collection_results["browser"] = len(browser_urls)
        
        # 2. Sitemap 수집 (대량 URL)
        print("\n  🗺️ 2단계: Sitemap 수집...")
        sitemap_urls = collect_urls_from_sitemap(city_name, limit=1000)
        all_collected_urls.extend(sitemap_urls)
        collection_results["sitemap"] = len(sitemap_urls)
        
    elif strategy == "comprehensive":
        # 포괄적 수집 (모든 방법 사용)
        print("\n⚡ 포괄적 수집 실행...")
        
        # 1. 브라우저 수집
        print("\n  🌐 1단계: 브라우저 수집...")
        browser_urls = collect_urls_with_pagination(driver, city_name, max_pages=10)
        all_collected_urls.extend(browser_urls)
        collection_results["browser"] = len(browser_urls)
        
        # 2. Sitemap 수집
        print("\n  🗺️ 2단계: Sitemap 수집...")
        sitemap_urls = collect_urls_from_sitemap(city_name, limit=2000)
        all_collected_urls.extend(sitemap_urls)
        collection_results["sitemap"] = len(sitemap_urls)
        
        # 3. 검색 기반 수집 (선택적)
        try:
            print("\n  🔍 3단계: 검색 기반 수집...")
            search_urls = collect_urls_from_search(driver, city_name)
            all_collected_urls.extend(search_urls)
            collection_results["search"] = len(search_urls)
        except Exception as e:
            print(f"    ⚠️ 검색 기반 수집 실패: {e}")
            collection_results["search"] = 0
    
    # 중복 제거 및 유효성 검증
    print(f"\n🧹 중복 제거 및 유효성 검증...")
    unique_urls = []
    for url in all_collected_urls:
        if is_valid_klook_url(url):
            normalized_url = normalize_klook_url(url)
            if normalized_url not in unique_urls:
                unique_urls.append(normalized_url)
    
    # 결과 저장
    if unique_urls:
        save_success = save_urls_to_collection(unique_urls, city_name, f"collection_{strategy}")
        print(f"💾 URL 저장: {'성공' if save_success else '실패'}")
    
    # 결과 정리
    print(f"\n🎉 === '{city_name}' URL 수집 완료 ===")
    print(f"📊 전략: {strategy}")
    print(f"🔗 최종 수집 URL: {len(unique_urls)}개 (중복 제거 후)")
    print(f"📈 수집 상세:")
    for source, count in collection_results.items():
        print(f"   📋 {source}: {count}개")
    
    return {
        "success": True,
        "strategy": strategy,
        "total_collected": len(unique_urls),
        "urls": unique_urls,
        "source_breakdown": collection_results,
        "city_name": city_name
    }

def collect_urls_from_search(driver, city_name):
    """검색 기반 URL 수집"""
    if not SELENIUM_AVAILABLE:
        return []
    
    print(f"  🔍 '{city_name}' 검색 기반 URL 수집...")
    
    try:
        # 검색 페이지로 이동
        search_url = f"https://www.klook.com/ko/search/result/?query={city_name}"
        driver.get(search_url)
        time.sleep(random.uniform(3, 5))
        
        # 검색 결과에서 URL 수집
        # 설정값 사용 (전역변수에서 가져오기)
        collect_limit = globals().get('MAX_COLLECT_LIMIT', 50)
        search_urls = collect_urls_from_current_page(driver, limit=collect_limit)
        
        print(f"    ✅ 검색에서 {len(search_urls)}개 URL 수집")
        return search_urls
        
    except Exception as e:
        print(f"    ❌ 검색 기반 수집 실패: {e}")
        return []

# =============================================================================
# 📊 URL 수집 분석 및 통계
# =============================================================================

def analyze_collection_results(results):
    """URL 수집 결과 분석"""
    if not results or not results.get("urls"):
        return {"error": "분석할 데이터가 없습니다"}
    
    urls = results["urls"]
    
    analysis = {
        "total_urls": len(urls),
        "unique_activity_ids": set(),
        "url_patterns": {},
        "domain_distribution": {},
        "language_distribution": {"ko": 0, "en": 0, "other": 0}
    }
    
    for url in urls:
        # Activity ID 추출
        activity_match = re.search(r'/activity/(\d+)', url)
        if activity_match:
            analysis["unique_activity_ids"].add(activity_match.group(1))
        
        # 도메인 분석
        parsed = urlparse(url)
        domain = parsed.netloc
        analysis["domain_distribution"][domain] = analysis["domain_distribution"].get(domain, 0) + 1
        
        # 언어 분석
        if '/ko/' in url:
            analysis["language_distribution"]["ko"] += 1
        elif '/en/' in url:
            analysis["language_distribution"]["en"] += 1
        else:
            analysis["language_distribution"]["other"] += 1
    
    analysis["unique_activities"] = len(analysis["unique_activity_ids"])
    analysis["unique_activity_ids"] = list(analysis["unique_activity_ids"])
    
    return analysis


# =============================================================================
# 🌀 스크롤 패턴 시스템 (원본에서 누락된 기능)
# =============================================================================

def human_like_scroll_patterns(driver):
    """순수 스크롤 패턴만 (인간과 유사한 자연스러운 패턴) - 항상 실행"""
    
    patterns = [
        # 패턴 1: 느린 독서 스타일
        {"type": "slow_reading", "scrolls": 3, "pause": (2, 4), "step": 300},
        # 패턴 2: 빠른 스캔
        {"type": "quick_scan", "scrolls": 5, "pause": (0.5, 1.5), "step": 500},
        # 패턴 3: 비교 검토 (위아래 움직임)
        {"type": "comparison", "scrolls": 4, "pause": (1, 3), "step": 200},
        # 패턴 4: 정밀 검토
        {"type": "detailed", "scrolls": 6, "pause": (1.5, 3), "step": 150},
        # 패턴 5: 자연스러운 탐색
        {"type": "natural", "scrolls": 4, "pause": (2, 5), "step": 400}
    ]
    
    # 랜덤 패턴 선택
    pattern = random.choice(patterns)
    print(f"    🌀 스크롤 패턴: {pattern['type']}")
    
    try:
        for i in range(pattern["scrolls"]):
            # 스크롤 실행
            driver.execute_script(f"window.scrollBy(0, {pattern['step']});")
            
            # 자연스러운 대기
            wait_time = random.uniform(pattern["pause"][0], pattern["pause"][1])
            time.sleep(wait_time)
            
            # 가끔 역방향 스크롤 (비교 검토)
            if pattern["type"] == "comparison" and random.random() < 0.3:
                driver.execute_script(f"window.scrollBy(0, -{pattern['step']//2});")
                time.sleep(random.uniform(0.5, 1.5))
                driver.execute_script(f"window.scrollBy(0, {pattern['step']});")
                
    except Exception as e:
        print(f"    ⚠️ 스크롤 패턴 실행 실패: {e}")

def enhanced_scroll_patterns(driver):
    """향상된 5가지 스크롤 패턴 (호환성 개선) - 항상 실행"""
    
    patterns = [
        {"name": "smooth_reading", "description": "부드러운 읽기 패턴"},
        {"name": "comparison_scroll", "description": "비교 스크롤"},
        {"name": "quick_scan", "description": "빠른 스캔"},
        {"name": "detailed_review", "description": "상세 검토"},
        {"name": "natural_browse", "description": "자연스러운 탐색"}
    ]
    
    selected = random.choice(patterns)
    print(f"    🌀 Enhanced 패턴: {selected['name']} - {selected['description']}")
    
    try:
        if selected["name"] == "smooth_reading":
            # 부드러운 읽기 패턴
            for _ in range(4):
                driver.execute_script("window.scrollBy(0, 250);")
                time.sleep(random.uniform(2, 4))
                
        elif selected["name"] == "comparison_scroll":
            # 비교 스크롤 (위아래 반복)
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 400);")
                time.sleep(random.uniform(1, 2))
                driver.execute_script("window.scrollBy(0, -200);")
                time.sleep(random.uniform(0.5, 1))
                driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(random.uniform(1.5, 3))
                
        elif selected["name"] == "quick_scan":
            # 빠른 스캔
            for _ in range(6):
                driver.execute_script("window.scrollBy(0, 600);")
                time.sleep(random.uniform(0.3, 1))
                
        elif selected["name"] == "detailed_review":
            # 상세 검토 (작은 단위로 천천히)
            for _ in range(8):
                driver.execute_script("window.scrollBy(0, 150);")
                time.sleep(random.uniform(1.5, 3))
                
        elif selected["name"] == "natural_browse":
            # 자연스러운 탐색 (불규칙한 패턴)
            scroll_amounts = [200, 350, 180, 450, 280, 320]
            for amount in scroll_amounts:
                driver.execute_script(f"window.scrollBy(0, {amount});")
                time.sleep(random.uniform(1, 4))
                
    except Exception as e:
        print(f"    ⚠️ Enhanced 스크롤 실행 실패: {e}")

def smart_scroll_selector(driver):
    """스마트 스크롤 선택기 (두 함수 중 랜덤 선택) - 항상 실행"""
    
    # 50% 확률로 각각 선택
    if random.random() < 0.5:
        print("    🎯 선택된 스크롤: human_like_scroll_patterns")
        human_like_scroll_patterns(driver)
    else:
        print("    🎯 선택된 스크롤: enhanced_scroll_patterns")
        enhanced_scroll_patterns(driver)

def collect_with_single_scan(driver):
    """통합 모드: 자동 스크롤과 함께 URL 수집 (조건 제거)"""
    
    print("    📋 통합 모드: 자동 스크롤 + URL 수집")
    
    all_urls = []
    
    # 1. 첫 번째 수집
    initial_urls = collect_urls_from_current_page(driver, limit=30)
    all_urls.extend(initial_urls)
    
    # 2. 자동 스크롤 실행 (항상 적용)
    smart_scroll_selector(driver)
    
    # 3. 스크롤 후 추가 수집
    # 설정값 사용 (전역변수에서 가져오기)
    collect_limit = globals().get('MAX_COLLECT_LIMIT', 50)
    additional_urls = collect_urls_from_current_page(driver, limit=collect_limit)
    all_urls.extend(additional_urls)
    
    # 4. 중복 제거
    unique_urls = list(set(all_urls))
    print(f"    ✅ 통합 수집 완료: {len(unique_urls)}개 URL")
    
    return unique_urls

def collect_with_infinite_scroll(driver):
    """레거시 호환성: collect_with_single_scan과 동일하게 작동"""
    return collect_with_single_scan(driver)

# =============================================================================
# ⏱️ 대기/타이밍 시스템 (원본에서 누락된 기능)
# =============================================================================

def smart_wait_for_page_load(driver, max_wait=8):
    """동적 대기시간 (페이지 로드 완료 감지)"""
    if not SELENIUM_AVAILABLE:
        return
    
    print(f"    ⏱️ 스마트 페이지 로드 대기 (최대 {max_wait}초)")
    
    try:
        # JavaScript를 통한 페이지 로드 상태 확인
        WebDriverWait(driver, max_wait).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # 추가로 DOM 요소 로딩 대기
        time.sleep(random.uniform(1, 2))
        print("    ✅ 페이지 로드 완료")
        
    except TimeoutException:
        print(f"    ⚠️ 페이지 로드 대기 시간 초과 ({max_wait}초)")
    except Exception as e:
        print(f"    ⚠️ 페이지 로드 대기 실패: {e}")

def wait_for_page_ready(driver, timeout=10):
    """페이지가 완전히 준비될 때까지 대기"""
    if not SELENIUM_AVAILABLE:
        return
    
    try:
        # 페이지 로드 완료 대기
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # jQuery가 있다면 AJAX 완료 대기
        try:
            WebDriverWait(driver, 3).until(
                lambda d: d.execute_script("return typeof jQuery !== 'undefined' ? jQuery.active == 0 : true")
            )
        except:
            pass
        
        print("    ✅ 페이지 준비 완료")
        
    except Exception as e:
        print(f"    ⚠️ 페이지 준비 대기 실패: {e}")

def adaptive_wait(base_time):
    """적응형 대기 시간 (시스템 부하에 따라 조정)"""
    try:
        # 기본 대기 시간에 랜덤 요소 추가
        actual_wait = base_time * random.uniform(0.8, 1.2)
        
        # 시스템 부하에 따른 추가 조정 (간단한 휴리스틱)
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > 80:
            actual_wait *= 1.5  # 높은 CPU 사용률일 때 더 긴 대기
        elif cpu_percent < 30:
            actual_wait *= 0.8  # 낮은 CPU 사용률일 때 짧은 대기
            
    except ImportError:
        # psutil이 없으면 기본 랜덤 대기
        actual_wait = base_time * random.uniform(0.8, 1.2)
    except:
        actual_wait = base_time
    
    time.sleep(actual_wait)
    return actual_wait

def safe_tab_operation(driver, operation_func, *args, **kwargs):
    """안전한 탭 작업 수행"""
    if not SELENIUM_AVAILABLE:
        return False
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = operation_func(driver, *args, **kwargs)
            return result
        except Exception as e:
            print(f"    ⚠️ 탭 작업 시도 {attempt + 1} 실패: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # 재시도 전 대기
            else:
                print("    ❌ 탭 작업 완전 실패")
                return False
    
    return False

print("✅ 그룹 8 완료: KLOOK URL 수집 시스템!")
print("   🔍 페이지네이션 수집:")
print("   - collect_urls_with_pagination(): 체계적 페이지 순회")
print("   - collect_urls_from_current_page(): 현재 페이지 URL 수집")
print("   - navigate_to_next_page(): 다음 페이지 이동")
print("   🗺️ Sitemap 수집:")
print("   - collect_urls_from_sitemap(): Sitemap 기반 대량 수집")
print("   🔄 통합 시스템:")
print("   - execute_comprehensive_url_collection(): 통합 수집 실행")
print("   - collect_urls_from_search(): 검색 기반 수집")
print("   🌀 스크롤 패턴 (추가됨):")
print("   - human_like_scroll_patterns(): 인간적 스크롤 패턴")
print("   - enhanced_scroll_patterns(): 향상된 5가지 패턴")
print("   - smart_scroll_selector(): 스마트 패턴 선택")
print("   - collect_with_single_scan(): 기본 스캔 모드")
print("   - collect_with_infinite_scroll(): 무한 스크롤 모드")
print("   ⏱️ 대기/타이밍 (추가됨):")
print("   - smart_wait_for_page_load(): 동적 페이지 로드 대기")
print("   - wait_for_page_ready(): 페이지 준비 완료 대기")
print("   - adaptive_wait(): 적응형 대기 시간")
print("   - safe_tab_operation(): 안전한 탭 작업")
print("   📊 분석 도구:")
print("   - analyze_collection_results(): 수집 결과 분석")
print("   🎯 지원 전략: browser_only, sitemap_only, hybrid, comprehensive")