"""
📄 페이지네이션 기반 순위별 크롤링 시스템
- 전체 탭에서 페이지를 넘어가면서 순위 연속성 유지
- 랭킹 정보와 크롤링 데이터 분리 저장
- CSV, 이미지, 랭킹 정보의 연속성 보장
"""

import os
import json
import time
from datetime import datetime
from .config import get_city_code, get_city_info

class PaginationRankingSystem:
    """페이지네이션 기반 순위별 크롤링 시스템"""
    
    def __init__(self):
        self.ranking_continuity = {}  # 페이지 간 순위 연속성 추적
        self.collected_urls = []      # 수집된 URL 목록
        self.current_global_rank = 1  # 전체적인 순위 추적
        
    def collect_urls_with_pagination(self, driver, city_name, target_count=15, max_pages=5):
        """페이지네이션을 통한 순위별 URL 수집"""
        print(f"📄 페이지네이션 기반 URL 수집 시작")
        print(f"🎯 목표: {target_count}개 URL, 최대 {max_pages}페이지")
        
        city_code = get_city_code(city_name)
        all_collected_urls = []
        current_page = 1
        global_rank = 1
        
        try:
            while len(all_collected_urls) < target_count and current_page <= max_pages:
                print(f"\n📖 페이지 {current_page} 처리 중...")
                
                # 현재 페이지에서 URL 수집 (순위 순서대로)
                page_urls = self._collect_urls_from_current_page(driver, global_rank)
                
                if not page_urls:
                    print(f"   ❌ 페이지 {current_page}에서 URL을 찾을 수 없음")
                    break
                
                print(f"   ✅ 페이지 {current_page}: {len(page_urls)}개 URL 수집")
                
                # 목표 개수만큼만 추가
                remaining_needed = target_count - len(all_collected_urls)
                urls_to_add = page_urls[:remaining_needed]
                
                for url_data in urls_to_add:
                    all_collected_urls.append({
                        'url': url_data['url'],
                        'global_rank': global_rank,
                        'page': current_page,
                        'page_position': url_data['page_position'],
                        'collected_at': datetime.now().isoformat()
                    })
                    global_rank += 1
                
                print(f"   📊 누적 수집: {len(all_collected_urls)}개/{target_count}개")
                
                # 목표 달성 시 중단
                if len(all_collected_urls) >= target_count:
                    print(f"🎯 목표 달성: {len(all_collected_urls)}개 URL 수집 완료")
                    break
                
                # 다음 페이지로 이동
                if current_page < max_pages:
                    next_success = self._navigate_to_next_page(driver)
                    if not next_success:
                        print(f"   ⚠️ 다음 페이지로 이동 실패 - 수집 종료")
                        break
                    
                    current_page += 1
                    time.sleep(3)  # 페이지 로딩 대기
                else:
                    print(f"   📄 최대 페이지 수 도달 ({max_pages}페이지)")
                    break
            
            # 수집 결과 저장
            if all_collected_urls:
                self._save_pagination_ranking_data(all_collected_urls, city_name)
            
            print(f"\n✅ 페이지네이션 수집 완료:")
            print(f"   📊 총 수집: {len(all_collected_urls)}개 URL")
            print(f"   📄 처리 페이지: {current_page}페이지")
            print(f"   🏆 순위 범위: 1위 ~ {len(all_collected_urls)}위")
            
            return all_collected_urls
            
        except Exception as e:
            print(f"❌ 페이지네이션 수집 실패: {e}")
            return all_collected_urls
    
    def _collect_urls_from_current_page(self, driver, start_rank):
        """현재 페이지에서 순위 순서대로 URL 수집"""
        try:
            from selenium.webdriver.common.by import By
            import time
            
            # 페이지 완전 로딩 대기
            time.sleep(3)
            
            # 다양한 셀렉터로 URL 수집
            selectors = [
                "a[href*='/activity/']",
                ".result-card a[href*='/activity/']",
                ".search-result a[href*='/activity/']",
                "[data-testid*='product'] a[href*='/activity/']",
                ".product-card a[href*='/activity/']",
                ".card a[href*='/activity/']"
            ]
            
            all_elements = []
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            href = element.get_attribute('href')
                            if href and '/activity/' in href and href not in [e['url'] for e in all_elements]:
                                # 화면상 위치 확인 (순위 결정용)
                                location = element.location
                                y_coord = location.get('y', 0)
                                x_coord = location.get('x', 0)
                                
                                if y_coord > 0:  # 화면에 보이는 요소만
                                    all_elements.append({
                                        'url': href,
                                        'y': y_coord,
                                        'x': x_coord,
                                        'element': element
                                    })
                        except:
                            continue
                except:
                    continue
            
            # Y좌표 기준으로 정렬 (위에서 아래로 = 순위 순서)
            all_elements.sort(key=lambda x: (x['y'], x['x']))
            
            # 페이지별 위치와 함께 반환
            page_urls = []
            for idx, element_data in enumerate(all_elements, 1):
                page_urls.append({
                    'url': element_data['url'],
                    'page_position': idx,
                    'y_coord': element_data['y'],
                    'x_coord': element_data['x']
                })
            
            return page_urls
            
        except Exception as e:
            print(f"   ❌ 현재 페이지 URL 수집 실패: {e}")
            return []
    
    def _navigate_to_next_page(self, driver):
        """다음 페이지로 이동"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time
            
            # 다양한 다음 페이지 버튼 셀렉터
            next_selectors = [
                "button[aria-label*='다음']",
                "button[aria-label*='Next']", 
                ".pagination .next",
                ".pagination button:contains('>'))",
                "[data-testid*='next']",
                "button:contains('>'))",
                ".pagination a[rel='next']"
            ]
            
            for selector in next_selectors:
                try:
                    # CSS 선택자와 XPath 구분
                    if 'contains' in selector:
                        # XPath 방식
                        next_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '>')]"))
                        )
                    else:
                        # CSS 선택자 방식
                        next_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    # 버튼이 활성화되어 있는지 확인
                    if next_button.is_enabled() and not next_button.get_attribute('disabled'):
                        print(f"   🔄 다음 페이지 버튼 클릭: {selector}")
                        
                        # JavaScript로 클릭 (더 안정적)
                        driver.execute_script("arguments[0].click();", next_button)
                        
                        # 페이지 변화 대기
                        time.sleep(3)
                        
                        print(f"   ✅ 다음 페이지로 이동 성공")
                        return True
                        
                except Exception as e:
                    continue
            
            print(f"   ❌ 다음 페이지 버튼을 찾을 수 없음")
            return False
            
        except Exception as e:
            print(f"   ❌ 다음 페이지 이동 실패: {e}")
            return False
    
    def _save_pagination_ranking_data(self, collected_urls, city_name):
        """페이지네이션 수집 결과를 랭킹 데이터로 저장"""
        try:
            city_code = get_city_code(city_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 1. 순위별 URL 저장 (ranking_urls/)
            ranking_urls_data = {
                "city_name": city_name,
                "city_code": city_code,
                "collection_method": "pagination_ranking",
                "collected_at": datetime.now().isoformat(),
                "total_urls": len(collected_urls),
                "max_page": max(url_data['page'] for url_data in collected_urls),
                "ranking_continuity": True,  # 페이지 간 순위 연속성 보장
                "urls_with_ranking": []
            }
            
            for url_data in collected_urls:
                ranking_urls_data["urls_with_ranking"].append({
                    "global_rank": url_data['global_rank'],
                    "url": url_data['url'],
                    "page": url_data['page'],
                    "page_position": url_data['page_position'],
                    "collected_at": url_data['collected_at']
                })
            
            # ranking_urls 저장
            os.makedirs("ranking_urls", exist_ok=True)
            ranking_urls_file = f"ranking_urls/{city_code}_전체_pagination_{timestamp}.json"
            
            with open(ranking_urls_file, 'w', encoding='utf-8') as f:
                json.dump(ranking_urls_data, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 순위 URL 저장: {ranking_urls_file}")
            
            # 2. 누적 랭킹 데이터 업데이트 (ranking_data/)
            self._update_accumulated_rankings(collected_urls, city_name)
            
            # 3. 크롤링용 단순 URL 목록 저장 (url_collected/)
            self._save_crawling_url_list(collected_urls, city_name)
            
        except Exception as e:
            print(f"   ❌ 랭킹 데이터 저장 실패: {e}")
    
    def _update_accumulated_rankings(self, collected_urls, city_name):
        """누적 랭킹 데이터 업데이트"""
        try:
            from .ranking_manager import ranking_manager
            
            # URL과 순위 정보로 변환
            urls_with_ranking = []
            for url_data in collected_urls:
                urls_with_ranking.append(url_data['url'])
            
            # 기존 랭킹 매니저 사용해서 저장
            success = ranking_manager.save_tab_ranking(
                urls_with_ranking, city_name, "전체", "pagination"
            )
            
            if success:
                print(f"   💾 누적 랭킹 업데이트 완료")
            
            # 추가로 순위 정보 직접 저장
            city_code = get_city_code(city_name)
            accumulated_file = f"ranking_data/{city_code}_accumulated_rankings.json"
            
            if os.path.exists(accumulated_file):
                with open(accumulated_file, 'r', encoding='utf-8') as f:
                    accumulated = json.load(f)
            else:
                accumulated = {
                    "city_name": city_name,
                    "city_code": city_code,
                    "last_updated": datetime.now().isoformat(),
                    "url_rankings": {},
                    "stats": {
                        "total_urls": 0,
                        "tabs_processed": [],
                        "duplicate_urls": 0
                    }
                }
            
            # 순위 정보 업데이트
            import hashlib
            for url_data in collected_urls:
                url = url_data['url']
                url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
                
                if url_hash not in accumulated["url_rankings"]:
                    accumulated["url_rankings"][url_hash] = {
                        "url": url,
                        "url_hash": url_hash,
                        "first_found": url_data['collected_at'],
                        "tab_rankings": {},
                        "is_duplicate": False,
                        "pagination_info": {
                            "page": url_data['page'],
                            "page_position": url_data['page_position']
                        }
                    }
                
                # 전체 탭 순위 정보 추가
                accumulated["url_rankings"][url_hash]["tab_rankings"]["전체"] = {
                    "ranking": url_data['global_rank'],
                    "found_at": url_data['collected_at'],
                    "collection_method": "pagination"
                }
            
            # 통계 업데이트
            accumulated["last_updated"] = datetime.now().isoformat()
            accumulated["stats"]["total_urls"] = len(accumulated["url_rankings"])
            if "전체" not in accumulated["stats"]["tabs_processed"]:
                accumulated["stats"]["tabs_processed"].append("전체")
            
            # 파일 저장
            with open(accumulated_file, 'w', encoding='utf-8') as f:
                json.dump(accumulated, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 누적 랭킹 직접 업데이트 완료")
            
        except Exception as e:
            print(f"   ❌ 누적 랭킹 업데이트 실패: {e}")
    
    def _save_crawling_url_list(self, collected_urls, city_name):
        """크롤링용 단순 URL 목록 저장"""
        try:
            city_code = get_city_code(city_name)
            os.makedirs("url_collected", exist_ok=True)
            
            # 기존 로그에 추가
            log_file = f"url_collected/{city_code}_pagination_log.txt"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"# 페이지네이션 기반 순위별 URL 수집\n")
                f.write(f"# 수집일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 총 {len(collected_urls)}개 URL (순위별)\n\n")
                
                for url_data in collected_urls:
                    f.write(f"{url_data['global_rank']:2d}위 | 페이지{url_data['page']} | {url_data['url']}\n")
            
            print(f"   📝 크롤링용 URL 목록 저장: {log_file}")
            
        except Exception as e:
            print(f"   ❌ 크롤링 URL 목록 저장 실패: {e}")

class RankingDataMatcher:
    """랭킹 정보와 크롤링 데이터 매칭 시스템"""
    
    def __init__(self):
        self.ranking_cache = {}
    
    def get_ranking_info_for_url(self, url, city_name):
        """특정 URL의 랭킹 정보 조회"""
        try:
            city_code = get_city_code(city_name)
            accumulated_file = f"ranking_data/{city_code}_accumulated_rankings.json"
            
            if not os.path.exists(accumulated_file):
                return None
            
            # 캐시 확인
            cache_key = f"{city_code}_{url}"
            if cache_key in self.ranking_cache:
                return self.ranking_cache[cache_key]
            
            # 파일에서 조회
            with open(accumulated_file, 'r', encoding='utf-8') as f:
                accumulated = json.load(f)
            
            import hashlib
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
            
            if url_hash in accumulated["url_rankings"]:
                ranking_info = accumulated["url_rankings"][url_hash]
                
                # 캐시에 저장
                self.ranking_cache[cache_key] = ranking_info
                
                return ranking_info
            
            return None
            
        except Exception as e:
            print(f"❌ 랭킹 정보 조회 실패: {e}")
            return None
    
    def create_ranking_csv_mapping(self, city_name):
        """랭킹 정보와 CSV 매핑 테이블 생성"""
        try:
            city_code = get_city_code(city_name)
            continent, country = get_city_info(city_name)
            
            # CSV 파일 경로
            csv_path = f"data/{continent}/{country}/{country}_klook_products_all.csv"
            if not os.path.exists(csv_path):
                print(f"❌ CSV 파일을 찾을 수 없음: {csv_path}")
                return None
            
            # 랭킹 정보 로드
            accumulated_file = f"ranking_data/{city_code}_accumulated_rankings.json"
            if not os.path.exists(accumulated_file):
                print(f"❌ 랭킹 파일을 찾을 수 없음: {accumulated_file}")
                return None
            
            with open(accumulated_file, 'r', encoding='utf-8') as f:
                ranking_data = json.load(f)
            
            # 매핑 테이블 생성
            mapping_table = []
            
            for url_hash, url_info in ranking_data["url_rankings"].items():
                url = url_info["url"]
                tab_rankings = url_info.get("tab_rankings", {})
                pagination_info = url_info.get("pagination_info", {})
                
                mapping_entry = {
                    "url": url,
                    "url_hash": url_hash,
                    "global_rank": tab_rankings.get("전체", {}).get("ranking", 0),
                    "page": pagination_info.get("page", 0),
                    "page_position": pagination_info.get("page_position", 0),
                    "csv_present": False,  # CSV에서 확인 후 업데이트
                    "csv_row_number": None,
                    "crawled": url_info.get("crawled", False),
                    "first_found": url_info.get("first_found"),
                    "last_updated": ranking_data.get("last_updated")
                }
                
                mapping_table.append(mapping_entry)
            
            # 순위순으로 정렬
            mapping_table.sort(key=lambda x: x['global_rank'])
            
            # 매핑 테이블 저장
            mapping_file = f"ranking_data/{city_code}_ranking_csv_mapping.json"
            mapping_data = {
                "city_name": city_name,
                "city_code": city_code,
                "created_at": datetime.now().isoformat(),
                "total_rankings": len(mapping_table),
                "mapping_table": mapping_table
            }
            
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 랭킹-CSV 매핑 테이블 생성: {mapping_file}")
            print(f"   📊 총 {len(mapping_table)}개 URL 매핑")
            
            return mapping_file
            
        except Exception as e:
            print(f"❌ 랭킹-CSV 매핑 테이블 생성 실패: {e}")
            return None

class ContinuityManager:
    """연속성 관리자 - CSV, 이미지, 랭킹의 연속성 보장"""
    
    def __init__(self):
        self.sequences = {
            'csv_sequence': 0,
            'image_sequence': 0, 
            'ranking_sequence': 0
        }
    
    def get_next_csv_number(self, city_name):
        """다음 CSV 번호 획득"""
        try:
            continent, country = get_city_info(city_name)
            csv_path = f"data/{continent}/{country}/{country}_klook_products_all.csv"
            
            if os.path.exists(csv_path):
                # 기존 파일에서 마지막 번호 확인
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    lines = f.readlines()
                    if len(lines) > 1:  # 헤더 제외
                        last_line = lines[-1].strip()
                        if last_line:
                            parts = last_line.split(',')
                            try:
                                last_number = int(parts[0])
                                return last_number + 1
                            except:
                                pass
            
            return 1
            
        except Exception as e:
            print(f"❌ CSV 번호 획득 실패: {e}")
            return 1
    
    def get_next_image_number(self, city_name):
        """다음 이미지 번호 획득"""
        try:
            city_code = get_city_code(city_name)
            continent, country = get_city_info(city_name)
            
            img_dir = f"klook_thumb_img/{continent}/{country}/{city_name}"
            if os.path.exists(img_dir):
                image_files = [f for f in os.listdir(img_dir) if f.startswith(f"{city_code}_")]
                if image_files:
                    # 파일명에서 번호 추출
                    numbers = []
                    for filename in image_files:
                        try:
                            # FCO_0001.jpg 에서 0001 추출
                            number_str = filename.split('_')[1].split('.')[0].split('_')[0]
                            numbers.append(int(number_str))
                        except:
                            continue
                    
                    if numbers:
                        return max(numbers) + 1
            
            return 1
            
        except Exception as e:
            print(f"❌ 이미지 번호 획득 실패: {e}")
            return 1
    
    def ensure_continuity_consistency(self, city_name):
        """연속성 일관성 검사 및 보정"""
        try:
            print(f"🔄 '{city_name}' 연속성 일관성 검사...")
            
            csv_next = self.get_next_csv_number(city_name)
            img_next = self.get_next_image_number(city_name)
            
            print(f"   📊 다음 CSV 번호: {csv_next}")
            print(f"   📸 다음 이미지 번호: {img_next}")
            
            # 불일치 감지
            if abs(csv_next - img_next) > 1:
                print(f"   ⚠️ 연속성 불일치 감지: CSV({csv_next}) vs 이미지({img_next})")
                
                # 보정 방안 제시
                max_number = max(csv_next, img_next)
                print(f"   💡 권장 다음 번호: {max_number}")
                
                return {
                    'consistent': False,
                    'csv_next': csv_next,
                    'image_next': img_next,
                    'recommended_next': max_number
                }
            else:
                print(f"   ✅ 연속성 일관성 양호")
                return {
                    'consistent': True,
                    'next_number': max(csv_next, img_next)
                }
                
        except Exception as e:
            print(f"❌ 연속성 검사 실패: {e}")
            return None

# 전역 인스턴스
pagination_ranking_system = PaginationRankingSystem()
ranking_data_matcher = RankingDataMatcher()
continuity_manager = ContinuityManager()

print("✅ 페이지네이션 순위 시스템 로드 완료!")
print("   📄 기능:")
print("   - collect_urls_with_pagination(): 페이지별 순위 연속성 URL 수집")
print("   - get_ranking_info_for_url(): URL별 랭킹 정보 조회")
print("   - create_ranking_csv_mapping(): 랭킹-CSV 매핑 테이블 생성")
print("   - ensure_continuity_consistency(): 연속성 일관성 보장")