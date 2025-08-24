#!/usr/bin/env python3
"""
🚀 단순화된 페이지네이션 크롤러
핵심 기능만 남긴 간단한 페이지네이션 기반 크롤링 시스템
"""

import os
import time
from datetime import datetime
from selenium.webdriver.common.by import By

class SimplePaginationCrawler:
    """단순화된 페이지네이션 크롤러"""
    
    def __init__(self, driver):
        self.driver = driver
        self.collected_urls = []
    
    def crawl_with_pagination(self, city_name, target_count=15, max_pages=5):
        """페이지네이션 기반 크롤링 - 핵심 기능만"""
        print(f"🚀 '{city_name}' 페이지네이션 크롤링 시작")
        print(f"🎯 목표: {target_count}개 상품, 최대 {max_pages}페이지")
        
        all_urls = []
        current_page = 1
        current_rank = 1
        
        while len(all_urls) < target_count and current_page <= max_pages:
            print(f"\n📖 페이지 {current_page} 처리 중...")
            
            # 1. 현재 페이지에서 URL 수집
            page_urls = self._get_urls_from_page()
            
            if not page_urls:
                print("❌ URL을 찾을 수 없음 - 종료")
                break
            
            # 2. 필요한 만큼만 추가 (순위 순서 보장)
            remaining = target_count - len(all_urls)
            for i, url in enumerate(page_urls[:remaining]):
                all_urls.append({
                    'url': url,
                    'rank': current_rank,
                    'page': current_page
                })
                current_rank += 1
            
            print(f"✅ 수집: {len(page_urls[:remaining])}개 URL ({len(all_urls)}/{target_count})")
            
            # 3. 목표 달성시 종료
            if len(all_urls) >= target_count:
                break
            
            # 4. 다음 페이지로 이동
            if not self._go_to_next_page():
                print("❌ 다음 페이지 이동 실패 - 종료")
                break
                
            current_page += 1
            time.sleep(2)
        
        # 5. 결과 저장
        if all_urls:
            self._save_results(all_urls, city_name)
        
        print(f"\n✅ 완료: {len(all_urls)}개 URL 수집 (1위~{len(all_urls)}위)")
        return all_urls
    
    def _get_urls_from_page(self):
        """현재 페이지에서 URL 수집"""
        try:
            time.sleep(2)  # 로딩 대기
            
            # KLOOK activity URL 찾기
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/activity/']")
            
            urls = []
            seen_urls = set()
            
            for element in elements:
                try:
                    url = element.get_attribute('href')
                    if url and '/activity/' in url and url not in seen_urls:
                        # 화면에 보이는 요소만 (순위 순서 보장)
                        location = element.location
                        if location.get('y', 0) > 0:
                            urls.append((url, location['y']))
                            seen_urls.add(url)
                except:
                    continue
            
            # Y 좌표 기준으로 정렬 (위에서 아래로 = 순위 순서)
            urls.sort(key=lambda x: x[1])
            return [url for url, _ in urls]
            
        except Exception as e:
            print(f"❌ URL 수집 실패: {e}")
            return []
    
    def _go_to_next_page(self):
        """다음 페이지로 이동 (통합 페이지네이션 매니저 사용)"""
        try:
            from .pagination_utils import KlookPageTool
            
            # 테스트 검증된 KLOOK 페이지 도구 사용
            page_tool = KlookPageTool(self.driver)
            
            # 부드러운 스크롤로 페이지네이션 영역 찾기
            page_tool.smooth_scroll_to_pagination()
            
            # 고급 다음 페이지 클릭
            current_url = self.driver.current_url
            result = page_tool.click_next_page(current_url)
            
            return result['success']
            
        except Exception as e:
            print(f"❌ 페이지 이동 실패: {e}")
            return False
    
    def _save_results(self, urls, city_name):
        """결과 저장 - 새로운 통합 세션 구조"""
        try:
            from .config import get_city_code
            city_code = get_city_code(city_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 세션 폴더 생성
            session_dir = f"crawl_sessions/{city_code}_{timestamp}"
            os.makedirs(session_dir, exist_ok=True)
            
            # 1. 세션 정보 저장
            session_info = {
                "city_name": city_name,
                "city_code": city_code,
                "session_date": datetime.now().strftime("%Y-%m-%d"),
                "session_time": datetime.now().strftime("%H:%M:%S"),
                "crawling_method": "simple_pagination",
                "total_urls_found": len(urls),
                "status": "url_collection_completed"
            }
            
            import json
            with open(f"{session_dir}/session_info.json", 'w', encoding='utf-8') as f:
                json.dump(session_info, f, ensure_ascii=False, indent=2)
            
            # 2. URL 목록 저장 (간단한 텍스트)
            with open(f"{session_dir}/url_list.txt", 'w', encoding='utf-8') as f:
                f.write(f"# {city_name} 페이지네이션 크롤링 결과\n")
                f.write(f"# 수집일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 총 {len(urls)}개 URL (순위별)\n\n")
                
                for url_data in urls:
                    f.write(f"{url_data['rank']:2d}위 | 페이지{url_data['page']} | {url_data['url']}\n")
            
            # 3. 상세 데이터 저장 (JSON)
            detailed_data = {
                "session_info": session_info,
                "urls_with_ranking": []
            }
            
            for url_data in urls:
                detailed_data["urls_with_ranking"].append({
                    "rank": url_data['rank'],
                    "page": url_data['page'],
                    "url": url_data['url'],
                    "collected_at": datetime.now().isoformat()
                })
            
            with open(f"{session_dir}/ranking_details.json", 'w', encoding='utf-8') as f:
                json.dump(detailed_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 통합 세션 저장: {session_dir}/")
            print(f"   📊 session_info.json: 기본 정보")
            print(f"   📝 url_list.txt: URL 목록")
            print(f"   📋 ranking_details.json: 상세 데이터")
            
        except Exception as e:
            print(f"❌ 저장 실패: {e}")

class SimplePaginationSystem:
    """단순화된 전체 시스템"""
    
    def __init__(self, driver):
        self.driver = driver
        self.crawler = SimplePaginationCrawler(driver)
    
    def run_full_crawl(self, city_name, target_count=15, max_pages=5):
        """전체 크롤링 실행"""
        print("🚀 단순화된 페이지네이션 크롤링 시스템")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            # 0. 도시명 별칭 처리
            from .city_alias_system import smart_city_search, get_search_variations
            
            print(f"🔍 도시명 검증: '{city_name}'")
            city_result = smart_city_search(city_name)
            
            if city_result['success']:
                standard_city = city_result['standard']
                search_variations = get_search_variations(standard_city)
                print(f"✅ 표준 도시명: '{standard_city}'")
                print(f"🔄 검색 변형: {search_variations}")
            else:
                print(f"⚠️ 도시명 검증 실패, 원본 사용: '{city_name}'")
                standard_city = city_name
                search_variations = [city_name]
            
            # 1. KLOOK 검색 페이지로 이동 (기존 함수 사용)
            from .driver_manager import go_to_main_page, find_and_fill_search, click_search_button
            
            print(f"🌐 KLOOK 메인 페이지 이동...")
            go_to_main_page(self.driver)
            
            # 2. 여러 검색 변형으로 시도
            search_success = False
            for i, search_term in enumerate(search_variations, 1):
                print(f"🔍 검색 시도 {i}/{len(search_variations)}: '{search_term}'")
                
                find_and_fill_search(self.driver, search_term)
                click_search_button(self.driver)
                time.sleep(5)
                
                # 검색 결과 확인
                if self._check_search_results():
                    print(f"✅ 검색 성공: '{search_term}'")
                    search_success = True
                    break
                else:
                    print(f"❌ 검색 결과 없음: '{search_term}'")
                    if i < len(search_variations):
                        print("🔄 다른 검색어로 재시도...")
                        time.sleep(2)
            
            if not search_success:
                print(f"❌ 모든 검색 변형 실패")
                return False
            
            # 3. 페이지네이션 크롤링 (표준 도시명 사용)
            collected_urls = self.crawler.crawl_with_pagination(
                standard_city, target_count, max_pages
            )
            
            # 3. 실제 크롤링 (기존 크롤러 사용)
            if collected_urls:
                print(f"\n🔥 상세 크롤링 시작...")
                success_count = self._crawl_products(collected_urls, city_name)
                
                print(f"\n🎉 크롤링 완료!")
                print(f"   URL 수집: {len(collected_urls)}개")
                print(f"   크롤링 성공: {success_count}개")
                print(f"   소요시간: {int((time.time() - start_time)//60)}분")
                
                return True
            else:
                print("❌ URL 수집 실패")
                return False
                
        except Exception as e:
            print(f"❌ 크롤링 실패: {e}")
            return False
    
    def _check_search_results(self):
        """검색 결과가 있는지 확인"""
        try:
            # KLOOK activity 결과가 있는지 확인
            elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/activity/']")
            return len(elements) > 0
        except:
            return False
    
    def _crawl_products(self, urls, city_name):
        """상품 상세 정보 크롤링"""
        try:
            from .crawler_engine import KlookCrawlerEngine
            
            crawler_engine = KlookCrawlerEngine(self.driver)
            success_count = 0
            
            for i, url_data in enumerate(urls, 1):
                url = url_data['url']
                rank = url_data['rank']
                
                print(f"\n📊 진행률: {i}/{len(urls)} | {rank}위")
                print(f"🔗 URL: {url[:60]}...")
                
                try:
                    # 상품 페이지로 이동
                    self.driver.get(url)
                    time.sleep(3)
                    
                    # 상품 정보 추출 (기존 엔진 사용)
                    result = crawler_engine._extract_product_info(url, city_name, i)
                    
                    if result:
                        # 랭킹 정보 추가
                        result['탭명'] = '전체'
                        result['탭내_랭킹'] = rank
                        result['페이지'] = url_data['page']
                        
                        # CSV 저장 (기존 함수 사용)
                        from .data_handler import save_to_csv_klook
                        if save_to_csv_klook(result, city_name):
                            product_name = result.get('상품명', 'N/A')[:30]
                            print(f"   ✅ 성공: {product_name}...")
                            success_count += 1
                        else:
                            print(f"   ❌ CSV 저장 실패")
                    else:
                        print(f"   ❌ 정보 추출 실패")
                        
                except Exception as e:
                    print(f"   💥 오류: {e}")
                    
                time.sleep(2)
            
            return success_count
            
        except Exception as e:
            print(f"❌ 상세 크롤링 실패: {e}")
            return 0

# 사용하기 쉬운 함수
def quick_pagination_crawl(driver, city_name, target_count=15):
    """빠른 페이지네이션 크롤링"""
    system = SimplePaginationSystem(driver)
    return system.run_full_crawl(city_name, target_count)

print("✅ 단순화된 페이지네이션 크롤러 로드 완료!")
print("🚀 사용법: quick_pagination_crawl(driver, '로마', 15)")