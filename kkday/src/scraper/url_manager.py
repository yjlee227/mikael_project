"""
URL 수집 및 관리 시스템
- KKday URL 패턴 검증 및 수집
- URL 중복 방지 시스템
- URL 상태 관리 및 추적
"""

import os
import re
import hashlib
import json
import time
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from ..config import CONFIG, get_city_code, is_url_processed_fast, mark_url_processed_fast, SELENIUM_AVAILABLE, get_random_user_agent 

# 조건부 import (sitemap 기능용)
try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    print("⚠️ requests/beautifulsoup4가 설치되지 않았습니다. Sitemap 기능이 제한됩니다.")
    REQUESTS_AVAILABLE = False

if SELENIUM_AVAILABLE:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

# =============================================================================
# KKday URL 패턴 및 검증 시스템
# =============================================================================

def is_valid_kkday_url(url):
    """KKday URL 유효성 검사"""
    if not url or not isinstance(url, str):
        return False
    # KKday 도메인 체크
    kkday_domains = [
        'kkday.com/ko',
        'www.kkday.com/ko',
        'm.kkday.com'
    ]
    parsed = urlparse(url)
    domain_valid = any(domain in parsed.netloc.lower() + parsed.path.lower() for domain in kkday_domains)
    if not domain_valid:
        return False

    # KKday URL 패턴 체크 (상품 상세 + 목록 페이지) 
    product_patterns = [
        # 상품 상세 페이지 패턴
        r'/ko/product/\d+$',                           # /ko/product/287674
        r'/ko/product/\d+-[\w\-]+$',                   # /ko/product/146520-krabi-kayaking
        r'/ko/product/\d+-[\w\-]+-[\w\-]+$',           # /ko/product/138349-speedboat-transfer-service
        r'/ko/product/\d+-[\w\-]+-[\w\-]+-[\w\-]+',    # 더 긴 형태들
        r'/product/\d+',                               # 언어 생략된 형태
        # 상품 목록 페이지 패턴
        r'/ko/product/productlist/[%\w\-]+',           #/ko/product/productlist/%EB%B0%A9%EC%BD%95
        r'/ko/product/productlist$',                   # /ko/product/productlist
        r'/product/productlist',                       # 언어 생략된 형태
    ]    
    
    path_valid = any(re.search(pattern, url) for pattern in product_patterns)
    return path_valid

def normalize_kkday_url(url):
    """KKday URL 정규화"""
    if not url:
        return url
    try:
        parsed = urlparse(url)
        # 쿼리 파라미터 정리 (추적용 파라미터 제거)
        query_params = parse_qs(parsed.query)
        # 유지할 파라미터만 선택 (KKday 기준)
        keep_params = ['lang', 'currency', 'city', 'page', 'date']
        cleaned_params = {k: v for k, v in query_params.items() if k in keep_params}
        # URL 재구성
        cleaned_query = urlencode(cleaned_params, doseq=True)
        cleaned_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            cleaned_query,
            ''  # fragment 제거
        ))
        return cleaned_url
    except Exception:
        return url

def extract_product_id(url):
    """URL에서 product ID 추출"""
    if not url:
        return None
    # 숫자 ID 패턴 매칭 (KKday 기준)
    id_patterns = [
        r'/ko/product/(\d+)',              # /ko/product/287674
        r'/ko/product/(\d+)-[\w\-]+',      # /ko/product/146520-krabi-kayaking
        r'/product/(\d+)',                 # /product/287674 (언어 생략)
        r'/product/(\d+)-[\w\-]+',         # /product/146520-krabi-kayaking
    ]
    for pattern in id_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# =============================================================================
# URL 수집 시스템
# =============================================================================

def collect_urls_from_page(driver, city_name):
    """현재 페이지에서 KKday URL 수집"""
    print("🔗 페이지에서 URL 수집 중...")
    
    if not SELENIUM_AVAILABLE:
        print("⚠️ Selenium이 없어 URL 수집을 건너뜁니다.")
        return []
    
    try:
        # KKday 상품 URL을 찾는 CSS 선택자들
        url_selectors = [
            "a[href*='/ko/product/']",              # KKday 상품 링크
            ".product-card a",                      # 상품 카드 (공통)
            ".product-list-main__product-card-2 a", # KKday 셀렉터 문서 기준
            ".gtm-prod-card-element a",             # KKday 셀렉터 문서 기준
            ".card a[href*='kkday']",               # kkday 도메인 포함
            ".item a[href*='/ko/product/']",        # KKday 상품 링크 (다른 컨테이너)
        ]    
        
        found_urls = []      # 순서 유지를 위한 list
        seen_urls = set()    # 중복 체크를 위한 set
        
        for selector in url_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    try:
                        href = element.get_attribute("href")
                        if href and is_valid_kkday_url(href):           
                            normalized_url = normalize_kkday_url(href)  
                            if normalized_url not in seen_urls:
                                found_urls.append(normalized_url)
                                seen_urls.add(normalized_url)                 
                    except:
                        continue
                        
            except Exception:
                continue
        
        print(f"  ✅ 수집된 URL: {len(found_urls)}개")
        return found_urls
        
    except Exception as e:
        print(f"  ⚠️ URL 수집 실패: {e}")
        return []

def get_pagination_urls(driver, max_pages=5):
    """페이지네이션을 통한 URL 수집"""
    print(f"📄 페이지네이션 URL 수집 중 (최대 {max_pages}페이지)...")
    
    all_urls = []        # 순서 유지를 위한 list
    seen_urls = set()    # 중복 체크를 위한 set
    current_page = 1

    while current_page <= max_pages:
        print(f"  📄 {current_page}페이지 수집 중...")

        # 현재 페이지에서 URL 수집
        page_urls = collect_urls_from_page(driver, "")

        if not page_urls:
            print("  ⚠️ URL을 찾을 수 없어 수집 중단")
            break

        for url in page_urls:
            if url not in seen_urls:
                all_urls.append(url)
                seen_urls.add(url)

        # 다음 페이지로 이동
        if current_page < max_pages:
            if not go_to_next_page(driver):
                print("  ℹ️ 더 이상 페이지가 없음")
                break

        current_page += 1
        time.sleep(2)  # 페이지 로드 대기

    print(f"✅ 총 수집된 URL: {len(all_urls)}개")
    return all_urls
    
def go_to_next_page(driver):
    """KKday 숫자 페이지네이션으로 다음 페이지 이동"""
    if not SELENIUM_AVAILABLE:
        return False

    # KKday 페이지네이션 셀렉터 (문서 기반)
    kkday_pagination_selectors = [
        ".pagination .a-page a",
        ".pagination .fa-angle-right",
        "#productListApp > div > div > main > ul.pagination a",
        ".pagination li a",
        ".pagination a",
        "ul.pagination li a"
    ]

    print("  ➡️ KKday 다음 페이지로 이동 중...")

    try:
        # 1단계: 현재 페이지 번호 찾기
        current_page_num = get_current_page_number(driver)
        next_page_num = current_page_num + 1
        print(f"    📄 현재: {current_page_num}페이지 → 다음: {next_page_num}페이지")

        # 2단계: KKday 페이지네이션 링크 클릭 시도
        for selector in kkday_pagination_selectors:
            try:
                # 모든 페이지 링크 찾기
                page_links = driver.find_elements(By.CSS_SELECTOR, selector)

                for link in page_links:
                    try:
                        link_text = link.text.strip()
                        link_href = link.get_attribute("href") or ""

                        # 다음 페이지 번호와 매치되는 링크 찾기
                        if (link_text == str(next_page_num) or
                            f"page={next_page_num}" in link_href or
                            f"pageNumber={next_page_num}" in link_href):

                            if link.is_enabled() and link.is_displayed():
                                # 클릭 전 URL 저장
                                old_url = driver.current_url

                                # 링크 클릭
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", link)
                                time.sleep(1)
                                link.click()

                                # 페이지 로드 대기 및 변화 확인
                                time.sleep(3)
                                new_url = driver.current_url

                                if new_url != old_url:
                                    print(f"    ✅ {next_page_num}페이지 이동 성공")
                                    return True

                    except Exception:
                        continue

            except Exception:
                continue

        # 3단계: URL 직접 변경 (폴백)
        print("    🔄 링크 클릭 실패 - URL 직접 변경 시도")
        return go_to_next_page_by_url(driver, next_page_num)

    except Exception as e:
        print(f"  ❌ 페이지네이션 이동 실패: {e}")
        return False


def get_current_page_number(driver):
    """현재 페이지 번호 추출"""
    current_page_selectors = [
        ".pagination .active",
        ".pagination .current",
        ".a-page.current",
        "[aria-current='page']"
    ]

    try:
        # 활성 페이지 요소에서 번호 추출
        for selector in current_page_selectors:
            try:
                current_element = driver.find_element(By.CSS_SELECTOR, selector)
                page_text = current_element.text.strip()

                if page_text.isdigit():
                    return int(page_text)

            except Exception:
                continue

        # URL에서 페이지 번호 추출
        current_url = driver.current_url
        if 'page=' in current_url:
            import re
            match = re.search(r'page=(\d+)', current_url)
            if match:
                return int(match.group(1))

        # 기본값: 1페이지
        return 1

    except Exception:
        return 1


def go_to_next_page_by_url(driver, next_page_num):
    """URL 직접 변경으로 다음 페이지 이동"""
    try:
        current_url = driver.current_url

        if 'page=' in current_url:
            import re
            new_url = re.sub(r'page=\d+', f'page={next_page_num}', current_url)
        else:
            separator = '&' if '?' in current_url else '?'
            new_url = current_url + f'{separator}page={next_page_num}'

        print(f"    🔗 URL 직접 이동: page={next_page_num}")
        driver.get(new_url)
        time.sleep(4)

        # 이동 성공 확인
        final_url = driver.current_url
        if f'page={next_page_num}' in final_url or str(next_page_num) in final_url:
            print(f"    ✅ URL 직접 이동 성공")
            return True
        else:
            print(f"    ❌ URL 직접 이동 실패")
            return False

    except Exception as e:
        print(f"    ❌ URL 변경 실패: {e}")
        return False

# =============================================================================
# URL 상태 관리 시스템
# =============================================================================

def is_url_already_processed(url, city_name):
    """URL 처리 여부 확인"""
    # hashlib 시스템 우선 사용
    if CONFIG.get("USE_HASH_SYSTEM", True):
        return is_url_processed_fast(url, city_name)
    
    # 폴백: CSV 기반 확인 (기존 시스템과 호환)
    try:
        from ..utils.file_handler import get_csv_stats
        
        stats = get_csv_stats(city_name)
        if isinstance(stats, dict) and 'error' not in stats:
            # CSV에서 URL 확인 로직 (간단화)
            return False  # 일단 처리되지 않은 것으로 가정
            
    except Exception:
        pass
    
    return False

def mark_url_as_processed(url, city_name, product_number=None, rank=None):
    """URL을 처리 완료로 표시"""
    # hashlib 시스템 우선 사용
    if CONFIG.get("USE_HASH_SYSTEM", True):
        return mark_url_processed_fast(url, city_name, product_number, rank)
    
    return True

def get_unprocessed_urls(url_list, city_name):
    """처리되지 않은 URL 목록 반환"""
    unprocessed = []
    
    for url in url_list:
        if not is_url_already_processed(url, city_name):
            unprocessed.append(url)
    
    print(f"📊 전체 URL: {len(url_list)}개, 미처리 URL: {len(unprocessed)}개")
    return unprocessed

def save_urls_to_file(urls, city_name, filename_suffix="collected"):
    """URL 목록을 파일로 저장"""
    try:
        city_code = get_city_code(city_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 저장 디렉토리 생성
        save_dir = "url_logs"
        os.makedirs(save_dir, exist_ok=True)
        
        # 파일명 생성
        filename = f"{city_code}_{filename_suffix}_{timestamp}.txt"
        filepath = os.path.join(save_dir, filename)
        
        # URL 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {city_name} URL 목록\n")
            f.write(f"# 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 총 URL 개수: {len(urls)}\n\n")
            
            for i, url in enumerate(urls, 1):
                f.write(f"{i}. {url}\n")
        
        print(f"✅ URL 목록 저장 완료: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"⚠️ URL 목록 저장 실패: {e}")
        return None

def load_urls_from_file(filepath):
    """파일에서 URL 목록 로드"""
    try:
        urls = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 주석과 빈 줄 건너뛰기
                if line and not line.startswith('#'):
                    # 번호 제거 (예: "1. https://...")
                    if '. ' in line:
                        url = line.split('. ', 1)[1]
                    else:
                        url = line
                    
                    if is_valid_kkday_url(url):
                        urls.append(url)
        
        print(f"✅ URL 목록 로드 완료: {len(urls)}개")
        return urls
        
    except Exception as e:
        print(f"⚠️ URL 목록 로드 실패: {e}")
        return []

# =============================================================================
# 통합 URL 수집 시스템 (기존 코드 호환성)
# =============================================================================

def execute_comprehensive_url_collection(driver, city_name, max_pages=3):
    """종합적인 URL 수집 시스템"""
    print(f"🚀 {city_name} 종합 URL 수집 시작...")
    
    try:
        # 페이지네이션을 통한 URL 수집
        all_urls = get_pagination_urls(driver, max_pages)
        
        # 중복 제거 및 검증
        valid_urls = []
        for url in all_urls:
            if is_valid_kkday_url(url):
                normalized = normalize_kkday_url(url)
                valid_urls.append(normalized)
        
        # 중복 제거
        unique_urls = []
        seen_urls = set()
        for url in valid_urls:
            if url not in seen_urls:
                unique_urls.append(url)
                seen_urls.add(url)
        
        # 미처리 URL만 필터링
        unprocessed_urls = get_unprocessed_urls(unique_urls, city_name)
        
        # URL 저장
        if unprocessed_urls:
            save_urls_to_file(unprocessed_urls, city_name)
        
        print(f"✅ URL 수집 완료: 총 {len(unique_urls)}개, 미처리 {len(unprocessed_urls)}개")
        return unprocessed_urls
        
    except Exception as e:
        print(f"❌ URL 수집 실패: {e}")
        return []

# =============================================================================
# 🗺️ Sitemap 기반 URL 수집 (페이지네이션 보완용)
# =============================================================================

def collect_urls_from_sitemap(city_name, exclude_urls=None, limit=1000):
    """Sitemap에서 KKday URL 수집 (중복 제외)"""
    if not REQUESTS_AVAILABLE:
        print("❌ requests/beautifulsoup4가 설치되지 않았습니다.")
        return []
    
    print(f"🗺️ '{city_name}' Sitemap URL 수집 시작...")
    
    exclude_set = set(exclude_urls or [])
    print(f"   🚫 제외할 URL: {len(exclude_set)}개")
    
    # KKday sitemap URL들
    sitemap_urls = [
        "https://www.kkday.com/sitemap.xml",
        "https://www.kkday.com/sitemap-products.xml",
        "https://www.kkday.com/sitemap-ko.xml",
        f"https://www.kkday.com/sitemap-{city_name.lower()}.xml"
    ]
       
    collected_urls = []
    
    for sitemap_url in sitemap_urls:
        try:
            print(f"  📋 Sitemap 처리 중: {sitemap_url}")
            
            response = requests.get(sitemap_url, timeout=30, headers={
                'User-Agent': get_random_user_agent()
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
                        
                        # KKday 상품 URL 필터링
                        if is_valid_kkday_url(url):
                            normalized_url = normalize_kkday_url(url)
                            
                            # 중복 체크 (이미 수집한 URL 제외)
                            if normalized_url not in exclude_set and normalized_url not in collected_urls:
                                # 도시명과 관련된 URL 우선 (선택적)
                                if city_name.lower() in url.lower() or len(collected_urls) < limit:
                                    collected_urls.append(normalized_url)
                                    
                                    if len(collected_urls) >= limit:
                                        break
                
                print(f"    ✅ 새로운 URL {len([u for u in collected_urls if u not in exclude_set])}개 발견")
                
            else:
                print(f"    ⚠️ Sitemap 접근 실패: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Sitemap 처리 실패: {e}")
            continue
    
    # 최종 중복 제거 (안전장치)
    final_urls = [url for url in collected_urls if url not in exclude_set]
    
    print(f"🎉 Sitemap 수집 완료: {len(final_urls)}개 새로운 URL")
    return final_urls[:limit]

def save_urls_to_collection(urls, city_name, collection_type="sitemap"):
    """URL 컬렉션을 파일로 저장"""
    try:
        city_code = get_city_code(city_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 저장 디렉토리 생성
        save_dir = "url_collections"
        os.makedirs(save_dir, exist_ok=True)
        
        # 파일명 생성
        filename = f"{city_code}_{collection_type}_{timestamp}.json"
        filepath = os.path.join(save_dir, filename)
        
        # 컬렉션 데이터 구성
        collection_data = {
            "city_name": city_name,
            "city_code": city_code,
            "collection_type": collection_type,
            "collected_at": datetime.now().isoformat(),
            "total_urls": len(urls),
            "urls": urls
        }
        
        # JSON 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(collection_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ URL 컬렉션 저장 완료: {filepath}")
        return True
        
    except Exception as e:
        print(f"⚠️ URL 컬렉션 저장 실패: {e}")
        return False

print("✅ url_manager.py 로드 완료: KKday URL 관리 시스템 준비!")
print("   🗺️ Sitemap 기능 추가:")
print("   - collect_urls_from_sitemap(): KKday 중복 제외 Sitemap 수집")
print("   - save_urls_to_collection(): URL 컬렉션 저장")