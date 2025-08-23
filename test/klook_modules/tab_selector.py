"""
🚀 그룹 7: KLOOK 탭 셀렉터 시스템
- 동적 탭 감지 및 선택
- 순위 정보 수집 및 전략 선택
- Enhanced 탭 구조 감지 시스템
"""

import os
import time
import random
import json
from datetime import datetime

# 조건부 import
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    print("⚠️ Selenium이 설치되지 않았습니다. 탭 셀렉터 기능이 제한됩니다.")
    SELENIUM_AVAILABLE = False

# config 모듈에서 필요한 함수들 import
from .config import CONFIG, get_city_code

# url_collection 모듈에서 URL 수집 함수 import (중복 방지)
try:
    from .url_collection import collect_urls_from_current_page
    URL_COLLECTION_AVAILABLE = True
except ImportError:
    print("⚠️ url_collection 모듈을 찾을 수 없습니다. 기본 함수를 사용합니다.")
    URL_COLLECTION_AVAILABLE = False

# =============================================================================
# 🎯 KLOOK 탭 정보 및 전략 설정
# =============================================================================

KLOOK_TAB_INFO = {
    "전체": {
        "priority": 1,
        "description": "모든 카테고리 상품",
        "ranking_limit": lambda: globals().get('MAX_COLLECT_LIMIT', 100),
        "search_patterns": ["전체", "all", "All"],
        "selectors": [
            "//span[contains(text(), '전체')]//parent::*",
            "//button[contains(text(), '전체')]",
            "//a[contains(text(), '전체')]",
            "//div[contains(text(), '전체')]",
            "//*[contains(@class, 'tab') and contains(text(), '전체')]",
            "//*[contains(@data-testid, 'tab') and contains(text(), '전체')]",
            "//*[contains(@role, 'tab') and contains(text(), '전체')]"
        ]
    },
    "투어&액티비티": {
        "priority": 2,
        "description": "투어 및 액티비티 상품",
        "ranking_limit": lambda: globals().get('MAX_COLLECT_LIMIT', 50),
        "search_patterns": ["투어", "액티비티", "투어액티비티", "Tours", "Activities"],
        "selectors": [
            "//span[contains(text(), '투어')]//parent::*",
            "//span[contains(text(), '액티비티')]//parent::*",
            "//button[contains(text(), '투어')]",
            "//button[contains(text(), '액티비티')]",
            "//a[contains(text(), '투어')]",
            "//a[contains(text(), '액티비티')]",
            "//div[contains(text(), '투어')]",
            "//div[contains(text(), '액티비티')]",
            "//*[contains(@class, 'tab') and (contains(text(), '투어') or contains(text(), '액티비티'))]",
            "//*[contains(@data-testid, 'tab') and (contains(text(), '투어') or contains(text(), '액티비티'))]"
        ]
    },
    "티켓&입장권": {
        "priority": 3,
        "description": "티켓 및 입장권",
        "ranking_limit": lambda: globals().get('MAX_COLLECT_LIMIT', 30),
        "search_patterns": ["티켓", "입장권", "티켓입장권", "Tickets", "Admission"],
        "selectors": [
            "//span[contains(text(), '티켓')]//parent::*",
            "//span[contains(text(), '입장권')]//parent::*",
            "//button[contains(text(), '티켓')]",
            "//button[contains(text(), '입장권')]",
            "//a[contains(text(), '티켓')]",
            "//a[contains(text(), '입장권')]",
            "//div[contains(text(), '티켓')]",
            "//div[contains(text(), '입장권')]",
            "//*[contains(@class, 'tab') and (contains(text(), '티켓') or contains(text(), '입장권'))]",
            "//*[contains(@data-testid, 'tab') and (contains(text(), '티켓') or contains(text(), '입장권'))]"
        ]
    },
    "교통": {
        "priority": 4,
        "description": "교통 관련 상품",
        "ranking_limit": lambda: globals().get('MAX_COLLECT_LIMIT', 20),
        "search_patterns": ["교통", "Transportation", "Transport"],
        "selectors": [
            "//span[contains(text(), '교통')]//parent::*",
            "//button[contains(text(), '교통')]",
            "//a[contains(text(), '교통')]",
            "//div[contains(text(), '교통')]",
            "//*[contains(@class, 'tab') and contains(text(), '교통')]",
            "//*[contains(@data-testid, 'tab') and contains(text(), '교통')]"
        ]
    },
    "기타": {
        "priority": 5,
        "description": "기타 카테고리 상품",
        "ranking_limit": lambda: globals().get('MAX_COLLECT_LIMIT', 15),
        "search_patterns": ["기타", "Others", "Misc", "기타상품"],
        "selectors": [
            "//span[contains(text(), '기타')]//parent::*",
            "//button[contains(text(), '기타')]",
            "//a[contains(text(), '기타')]",
            "//div[contains(text(), '기타')]",
            "//*[contains(@class, 'tab') and contains(text(), '기타')]",
            "//*[contains(@data-testid, 'tab') and contains(text(), '기타')]"
        ]
    }
}

CRAWLING_STRATEGIES = {
    "전체_sitemap": {
        "name": "📋 전체 Sitemap 모드",
        "description": "Sitemap에서만 URL 수집 (가장 빠름)",
        "speed": "매우 빠름",
        "ranking_info": "없음",
        "use_tabs": False
    },
    "전체_hybrid": {
        "name": "🔀 전체 하이브리드 모드",
        "description": "순위 + Sitemap 조합 (권장)",
        "speed": "빠름",
        "ranking_info": "상위 순위",
        "use_tabs": True
    },
    "tab_select": {
        "name": "🎪 탭별 선택 모드",
        "description": "특정 탭 선택하여 크롤링",
        "speed": "보통",
        "ranking_info": "탭별 순위",
        "use_tabs": True
    },
    "ranking_only": {
        "name": "🏆 순위만 수집 모드",
        "description": "브라우저 순위 정보만 수집",
        "speed": "보통",
        "ranking_info": "전체 순위",
        "use_tabs": True
    },
    "enhanced_all": {
        "name": "⚡ Enhanced 전체 모드",
        "description": "모든 탭 + Enhanced 기능",
        "speed": "느림",
        "ranking_info": "모든 탭 순위",
        "use_tabs": True
    }
}

# =============================================================================
# 🔍 탭 감지 및 구조 분석
# =============================================================================

def detect_klook_tabs(driver):
    """Enhanced 탭 구조 감지 시스템 (강화된 패턴 매칭)"""
    if not SELENIUM_AVAILABLE:
        return {}
    
    print("🔍 Enhanced 탭 구조 감지 시작...")
    detected_tabs = {}
    
    # 각 탭에 대해 감지 시도
    for tab_name, tab_info in KLOOK_TAB_INFO.items():
        print(f"  🔎 '{tab_name}' 탭 감지 중...")
        
        tab_found = False
        search_patterns = tab_info.get("search_patterns", [tab_name])
        
        # 각 검색 패턴에 대해 시도
        for pattern in search_patterns:
            if tab_found:
                break
                
            print(f"    📍 패턴 '{pattern}' 검색 중...")
            
            # 해당 패턴에 대한 다양한 셀렉터 시도
            pattern_selectors = [
                f"//span[contains(text(), '{pattern}')]//parent::*",
                f"//button[contains(text(), '{pattern}')]",
                f"//a[contains(text(), '{pattern}')]",
                f"//div[contains(text(), '{pattern}')]",
                f"//*[contains(@class, 'tab') and contains(text(), '{pattern}')]",
                f"//*[contains(@data-testid, 'tab') and contains(text(), '{pattern}')]",
                f"//*[contains(@role, 'tab') and contains(text(), '{pattern}')]"
            ]
            
            # 기존 selectors도 추가
            if "selectors" in tab_info:
                pattern_selectors.extend(tab_info["selectors"])
            
            for selector in pattern_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    print(f"      셀렉터: '{selector}' → {len(elements)}개 요소")
                    
                    for element in elements:
                        try:
                            element_text = element.text.strip()
                            print(f"        요소 텍스트: '{element_text}'")
                            
                            # 요소가 실제로 클릭 가능한지 확인
                            if element.is_displayed() and element.is_enabled():
                                detected_tabs[tab_name] = {
                                    "element": element,
                                    "selector": selector,
                                    "pattern": pattern,
                                    "element_text": element_text,
                                    "method": "XPath_Enhanced",
                                    "priority": tab_info["priority"],
                                    "description": tab_info["description"],
                                    "search_patterns": search_patterns,
                                    "ranking_limit": tab_info["ranking_limit"]() if callable(tab_info["ranking_limit"]) else tab_info["ranking_limit"]
                                }
                                print(f"    ✅ '{tab_name}' 탭 감지됨! (패턴: '{pattern}', 텍스트: '{element_text}')")
                                tab_found = True
                                break
                        except Exception as elem_e:
                            print(f"        요소 처리 실패: {elem_e}")
                            continue
                            
                    if tab_found:
                        break
                        
                except Exception as sel_e:
                    print(f"      셀렉터 처리 실패: {sel_e}")
                    continue
        
        if not tab_found:
            print(f"    ❌ '{tab_name}' 탭을 찾을 수 없습니다")
    
    print(f"🎯 총 {len(detected_tabs)}개 탭 감지 완료")
    
    # 감지된 탭 정보 상세 출력
    for tab_name, tab_data in detected_tabs.items():
        print(f"  ✅ {tab_name}: '{tab_data['element_text']}' (패턴: {tab_data['pattern']})")
    
    return detected_tabs

def check_system_health():
    """시스템 상태 확인"""
    health_status = {
        "overall_health": "unknown",
        "components": {
            "selenium": SELENIUM_AVAILABLE,
            "config": True,
            "tab_info": len(KLOOK_TAB_INFO) > 0,
            "strategies": len(CRAWLING_STRATEGIES) > 0
        },
        "recommendations": []
    }
    
    # 전체 상태 판정
    working_components = sum(health_status["components"].values())
    total_components = len(health_status["components"])
    
    if working_components == total_components:
        health_status["overall_health"] = "excellent"
    elif working_components >= total_components * 0.75:
        health_status["overall_health"] = "good"
    elif working_components >= total_components * 0.5:
        health_status["overall_health"] = "fair"
    else:
        health_status["overall_health"] = "poor"
    
    # 권장사항 생성
    if not health_status["components"]["selenium"]:
        health_status["recommendations"].append("Selenium 라이브러리 설치 필요")
    
    return health_status

# =============================================================================
# 🎪 탭 처리 및 URL 수집
# =============================================================================

def process_tab(driver, tab_name, tab_info, city_name):
    """개별 탭 처리 및 URL 수집 (강화된 탭 클릭 지원)"""
    if not SELENIUM_AVAILABLE:
        return {"success": False, "error": "Selenium not available"}
    
    print(f"🔄 '{tab_name}' 탭 처리 중...")
    
    try:
        print(f"  🎯 '{tab_name}' 탭 처리 시작...")
        
        # 전체 탭의 경우 별도 클릭 없이 현재 페이지 사용
        if tab_name == "전체":
            print("    ℹ️ 전체 탭은 별도 클릭 없이 현재 페이지 사용")
        else:
            # 강화된 탭 클릭 로직
            tab_clicked = False
            
            # 전달된 element가 있으면 우선 사용
            if "element" in tab_info and tab_info["element"]:
                try:
                    element = tab_info["element"]
                    if element.is_displayed() and element.is_enabled():
                        # JavaScript 클릭 시도
                        driver.execute_script("arguments[0].click();", element)
                        tab_clicked = True
                        print(f"    ✅ '{tab_name}' 탭 기존 element로 클릭 성공")
                except Exception as e:
                    print(f"    ⚠️ 기존 element 클릭 실패: {e}")
            
            # 기존 element로 클릭 실패 시 다시 탭 찾기
            if not tab_clicked:
                print(f"    🔍 '{tab_name}' 탭 element 재탐색...")
                
                # tab_info에서 search_patterns 사용 또는 기본값 생성
                search_patterns = tab_info.get("search_patterns", [tab_name])
                selectors = tab_info.get("selectors", [])
                
                for pattern in search_patterns:
                    if tab_clicked:
                        break
                    
                    # 패턴별로 다양한 셀렉터 시도
                    pattern_selectors = [
                        f"//span[contains(text(), '{pattern}')]//parent::*",
                        f"//button[contains(text(), '{pattern}')]",
                        f"//a[contains(text(), '{pattern}')]",
                        f"//div[contains(text(), '{pattern}')]",
                        f"//*[contains(@class, 'tab') and contains(text(), '{pattern}')]",
                        f"//*[contains(@data-testid, 'tab') and contains(text(), '{pattern}')]"
                    ]
                    
                    for selector in pattern_selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            print(f"      📍 패턴 '{pattern}' 셀렉터: {len(elements)}개 요소")
                            
                            for element in elements:
                                try:
                                    if element.is_displayed() and element.is_enabled():
                                        # 일반 클릭 시도
                                        try:
                                            element.click()
                                            tab_clicked = True
                                            print(f"    ✅ '{tab_name}' 탭 일반 클릭 성공")
                                            break
                                        except:
                                            # JavaScript 클릭 시도
                                            try:
                                                driver.execute_script("arguments[0].click();", element)
                                                tab_clicked = True
                                                print(f"    ✅ '{tab_name}' 탭 JavaScript 클릭 성공")
                                                break
                                            except Exception as click_e:
                                                continue
                                except:
                                    continue
                                    
                            if tab_clicked:
                                break
                        except Exception as e:
                            continue
            
            if tab_clicked:
                time.sleep(random.uniform(2, 4))
                print(f"    ✅ '{tab_name}' 탭 클릭 완료 - 페이지 로딩 대기 중...")
            else:
                print(f"    ❌ '{tab_name}' 탭 클릭 실패 - 모든 방법 시도 완료")
                return {
                    "success": False,
                    "tab_name": tab_name,
                    "error": "Tab click failed - no clickable element found"
                }
        
        # URL 수집
        # 설정값 사용 - ranking_limit이 함수인 경우 실행
        ranking_limit_value = tab_info.get("ranking_limit", 50)
        if callable(ranking_limit_value):
            ranking_limit = ranking_limit_value()
        else:
            ranking_limit = ranking_limit_value
        print(f"    🔍 '{tab_name}' 탭에서 상위 {ranking_limit}개 URL 수집 중...")
        
        if URL_COLLECTION_AVAILABLE:
            collected_urls = collect_urls_from_current_page(driver, ranking_limit)
        else:
            # 폴백: 간단한 URL 수집
            collected_urls = []
            try:
                elements = driver.find_elements("css selector", "a[href*='/activity/']")
                for element in elements[:ranking_limit]:
                    href = element.get_attribute('href')
                    if href:
                        collected_urls.append(href)
            except Exception:
                pass
        
        if collected_urls:
            print(f"    ✅ '{tab_name}' 탭에서 {len(collected_urls)}개 URL 수집 완료")
            
            # URL 저장 (기존 방식)
            save_ranking_urls(collected_urls, city_name, tab_name, "전체_hybrid")
            
            # 랭킹 매니저에 랭킹 정보 저장 (신규)
            try:
                from .ranking_manager import ranking_manager
                ranking_manager.save_tab_ranking(collected_urls, city_name, tab_name, "전체_hybrid")
            except Exception as e:
                print(f"    ⚠️ 랭킹 매니저 저장 실패: {e}")
            
            return {
                "success": True,
                "tab_name": tab_name,
                "urls_collected": len(collected_urls),
                "urls": collected_urls
            }
        else:
            print(f"    ⚠️ '{tab_name}' 탭에서 URL을 찾지 못했습니다")
            return {
                "success": False,
                "tab_name": tab_name,
                "error": "No URLs found"
            }
            
    except Exception as e:
        print(f"    ❌ '{tab_name}' 탭 처리 실패: {e}")
        return {
            "success": False,
            "tab_name": tab_name,
            "error": str(e)
        }

# collect_urls_from_current_page는 url_collection 모듈에서 import됨 (중복 방지)

def save_ranking_urls(urls, city_name, tab_name, strategy):
    """순위 URL 저장"""
    if not urls:
        return False
    
    try:
        # ranking_urls 폴더에 저장
        ranking_dir = "ranking_urls"
        os.makedirs(ranking_dir, exist_ok=True)
        
        city_code = get_city_code(city_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{city_code}_{tab_name}_{strategy}_{timestamp}.json"
        filepath = os.path.join(ranking_dir, filename)
        
        data = {
            "city_name": city_name,
            "city_code": city_code,
            "tab_name": tab_name,
            "strategy": strategy,
            "collected_at": datetime.now().isoformat(),
            "total_urls": len(urls),
            "urls": urls
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"    💾 '{tab_name}' URL 저장 완료: {filename} ({len(urls)}개)")
        return True
        
    except Exception as e:
        print(f"    ❌ URL 저장 실패: {e}")
        return False

# =============================================================================
# 🎮 통합 탭 셀렉터 시스템
# =============================================================================

def execute_integrated_tab_selector_system(city_name, driver, interactive_mode=False):
    """통합 탭 셀렉터 시스템 실행"""
    if not SELENIUM_AVAILABLE:
        return {"success": False, "error": "Selenium not available"}
    
    print(f"🎯 '{city_name}' 도시의 통합 탭 셀렉터 시스템 시작!")
    print("=" * 80)
    
    # 사용 가능한 전략 표시
    print("\n🎯 사용 가능한 크롤링 전략:")
    print("=" * 70)
    for strategy_key, strategy_info in CRAWLING_STRATEGIES.items():
        print(f"{strategy_info['name']}")
        print(f"   📝 설명: {strategy_info['description']}")
        print(f"   ⚡ 속도: {strategy_info['speed']}")
        print(f"   📊 순위 정보: {strategy_info['ranking_info']}")
        print(f"   🎯 탭 사용: {'예' if strategy_info['use_tabs'] else '아니오'}")
        print()
    
    # KLOOK 탭 정보 표시
    print("\n📋 KLOOK 카테고리 탭:")
    print("=" * 50)
    for tab_name, tab_info in KLOOK_TAB_INFO.items():
        print(f"{tab_info['priority']}. {tab_name}")
        print(f"   📝 {tab_info['description']}")
        print(f"   🎯 우선순위: {tab_info['priority']}")
        print(f"   📊 순위 한계: {tab_info['ranking_limit']}개")
        print()
    
    # 자동 실행 (하이브리드 모드)
    print("🤖 자동 실행 모드: 기본 전략을 사용합니다")
    selected_strategy = "전체_hybrid"
    
    print(f"\n🚀 선택된 전략 실행: {selected_strategy}")
    print(f"🎯 선택된 탭: 전체")
    
    # 탭 구조 감지 및 처리
    print("🔍 탭 구조 감지 및 순위 정보 수집 시작...")
    detected_tabs = detect_klook_tabs(driver)
    
    total_collected = 0
    results = {}
    
    # 전체 탭만 처리 (기본 전략)
    if "전체" in detected_tabs:
        tab_result = process_tab(driver, "전체", detected_tabs["전체"], city_name)
        if tab_result["success"]:
            total_collected += tab_result["urls_collected"]
            results["전체"] = tab_result["urls_collected"]
    
    # 결과 정리
    print(f"\n🎉 === '{city_name}' 탭 셀렉터 시스템 실행 완료 ===")
    print(f"📊 전략: {selected_strategy}")
    print(f"🎯 처리된 탭: {len(results)}개")
    print(f"📈 총 수집 URL: {total_collected}개")
    print(f"✅ 성공: 예")
    
    print(f"\n📋 탭별 수집 결과:")
    for tab_name, count in results.items():
        print(f"   🎪 {tab_name}: {count}개")
    
    return {
        "success": True,
        "strategy": selected_strategy,
        "total_collected": total_collected,
        "tab_results": results,
        "city_name": city_name
    }

print("✅ 그룹 7 완료: KLOOK 탭 셀렉터 시스템!")
print("   🔍 탭 감지:")
print("   - detect_klook_tabs(): Enhanced 탭 구조 감지")
print("   - check_system_health(): 시스템 상태 확인")
print("   🎪 탭 처리:")
print("   - process_tab(): 개별 탭 처리 및 URL 수집")
print("   - collect_urls_from_current_page(): 현재 페이지 URL 수집")
print("   - save_ranking_urls(): 순위 URL 저장")
print("   🎮 통합 시스템:")
print("   - execute_integrated_tab_selector_system(): 통합 실행")
print("   📊 전략: 전체_sitemap, 전체_hybrid, tab_select, ranking_only, enhanced_all")
print("   🎯 지원 탭: 전체, 투어&액티비티, 티켓&입장권, 교통, 기타")