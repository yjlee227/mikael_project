"""
🚀 랭킹 매니저: 중복 URL 랭킹 누적 및 관리 시스템
- 탭별 랭킹 정보 수집
- 중복 URL 랭킹 누적 저장
- 랭킹 데이터 조회 및 분석
"""

import os
import json
import hashlib
from datetime import datetime
from collections import defaultdict

# config 모듈에서 필요한 함수들 import
from .config import get_city_code

# =============================================================================
# 🏆 랭킹 데이터 구조
# =============================================================================

class RankingManager:
    """중복 URL 랭킹 누적 관리 시스템"""
    
    def __init__(self):
        self.ranking_dir = "ranking_data"
        self.ranking_cache = {}
        
    def save_tab_ranking(self, urls_with_ranking, city_name, tab_name, strategy):
        """탭에서 수집한 URL들과 랭킹 정보 저장"""
        if not urls_with_ranking:
            return False
        
        try:
            os.makedirs(self.ranking_dir, exist_ok=True)
            
            city_code = get_city_code(city_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{city_code}_{tab_name}_{strategy}_{timestamp}.json"
            filepath = os.path.join(self.ranking_dir, filename)
            
            # URL별 랭킹 정보 구조화
            ranking_data = {
                "city_name": city_name,
                "city_code": city_code,
                "tab_name": tab_name,
                "strategy": strategy,
                "collected_at": datetime.now().isoformat(),
                "total_urls": len(urls_with_ranking),
                "url_rankings": []
            }
            
            for idx, url in enumerate(urls_with_ranking, 1):
                url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
                
                ranking_data["url_rankings"].append({
                    "url": url,
                    "url_hash": url_hash,
                    "tab_name": tab_name,
                    "tab_ranking": idx,
                    "found_at": datetime.now().isoformat()
                })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(ranking_data, f, ensure_ascii=False, indent=2)
            
            print(f"    💾 랭킹 데이터 저장: {filename} ({len(urls_with_ranking)}개)")
            
            # 랭킹 누적 업데이트
            self._update_accumulated_rankings(ranking_data)
            
            return True
            
        except Exception as e:
            print(f"    ❌ 랭킹 데이터 저장 실패: {e}")
            return False
    
    def _update_accumulated_rankings(self, ranking_data):
        """중복 URL 랭킹 누적 업데이트"""
        try:
            city_code = ranking_data["city_code"]
            accumulated_file = os.path.join(self.ranking_dir, f"{city_code}_accumulated_rankings.json")
            
            # 기존 누적 데이터 로드
            if os.path.exists(accumulated_file):
                with open(accumulated_file, 'r', encoding='utf-8') as f:
                    accumulated = json.load(f)
            else:
                accumulated = {
                    "city_name": ranking_data["city_name"],
                    "city_code": city_code,
                    "last_updated": None,
                    "url_rankings": {},
                    "stats": {
                        "total_urls": 0,
                        "tabs_processed": [],
                        "duplicate_urls": 0
                    }
                }
            
            # 새 랭킹 데이터 누적
            tab_name = ranking_data["tab_name"]
            
            for url_info in ranking_data["url_rankings"]:
                url_hash = url_info["url_hash"]
                url = url_info["url"]
                
                if url_hash not in accumulated["url_rankings"]:
                    # 새로운 URL
                    accumulated["url_rankings"][url_hash] = {
                        "url": url,
                        "url_hash": url_hash,
                        "first_found": url_info["found_at"],
                        "tab_rankings": {},
                        "is_duplicate": False
                    }
                else:
                    # 중복 URL - 중복 표시
                    accumulated["url_rankings"][url_hash]["is_duplicate"] = True
                    accumulated["stats"]["duplicate_urls"] += 1
                
                # 탭별 랭킹 정보 추가
                accumulated["url_rankings"][url_hash]["tab_rankings"][tab_name] = {
                    "ranking": url_info["tab_ranking"],
                    "found_at": url_info["found_at"]
                }
            
            # 통계 업데이트
            accumulated["last_updated"] = datetime.now().isoformat()
            accumulated["stats"]["total_urls"] = len(accumulated["url_rankings"])
            if tab_name not in accumulated["stats"]["tabs_processed"]:
                accumulated["stats"]["tabs_processed"].append(tab_name)
            
            # 누적 데이터 저장
            with open(accumulated_file, 'w', encoding='utf-8') as f:
                json.dump(accumulated, f, ensure_ascii=False, indent=2)
            
            print(f"    📊 누적 랭킹 업데이트: 총 {accumulated['stats']['total_urls']}개 URL, 중복 {accumulated['stats']['duplicate_urls']}개")
            
        except Exception as e:
            print(f"    ❌ 누적 랭킹 업데이트 실패: {e}")
    
    def get_url_rankings(self, url, city_name):
        """특정 URL의 모든 탭 랭킹 정보 조회"""
        try:
            city_code = get_city_code(city_name)
            accumulated_file = os.path.join(self.ranking_dir, f"{city_code}_accumulated_rankings.json")
            
            if not os.path.exists(accumulated_file):
                return None
            
            with open(accumulated_file, 'r', encoding='utf-8') as f:
                accumulated = json.load(f)
            
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
            
            if url_hash in accumulated["url_rankings"]:
                return accumulated["url_rankings"][url_hash]
            
            return None
            
        except Exception as e:
            print(f"❌ URL 랭킹 조회 실패: {e}")
            return None
    
    def get_city_ranking_stats(self, city_name):
        """도시별 랭킹 통계 조회"""
        try:
            city_code = get_city_code(city_name)
            accumulated_file = os.path.join(self.ranking_dir, f"{city_code}_accumulated_rankings.json")
            
            if not os.path.exists(accumulated_file):
                return None
            
            with open(accumulated_file, 'r', encoding='utf-8') as f:
                accumulated = json.load(f)
            
            return accumulated["stats"]
            
        except Exception as e:
            print(f"❌ 랭킹 통계 조회 실패: {e}")
            return None
    
    def should_crawl_url(self, url, city_name):
        """URL이 크롤링 대상인지 확인 (첫 번째 발견된 탭에서만 크롤링)"""
        url_rankings = self.get_url_rankings(url, city_name)
        
        if not url_rankings:
            return True  # 새로운 URL은 크롤링
        
        # 이미 크롤링된 URL인지 확인
        return not url_rankings.get("crawled", False)
    
    def mark_url_crawled(self, url, city_name):
        """URL을 크롤링 완료로 표시"""
        try:
            city_code = get_city_code(city_name)
            accumulated_file = os.path.join(self.ranking_dir, f"{city_code}_accumulated_rankings.json")
            
            if not os.path.exists(accumulated_file):
                return False
            
            with open(accumulated_file, 'r', encoding='utf-8') as f:
                accumulated = json.load(f)
            
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
            
            if url_hash in accumulated["url_rankings"]:
                accumulated["url_rankings"][url_hash]["crawled"] = True
                accumulated["url_rankings"][url_hash]["crawled_at"] = datetime.now().isoformat()
                
                with open(accumulated_file, 'w', encoding='utf-8') as f:
                    json.dump(accumulated, f, ensure_ascii=False, indent=2)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ URL 크롤링 완료 표시 실패: {e}")
            return False
    
    def get_collected_ranks(self, city_name, tab_name=None):
        """🆕 특정 도시에서 이미 수집된 순위들 조회 (범용)"""
        try:
            city_code = get_city_code(city_name)
            accumulated_file = os.path.join(self.ranking_dir, f"{city_code}_accumulated_rankings.json")
            
            if not os.path.exists(accumulated_file):
                return []
            
            with open(accumulated_file, 'r', encoding='utf-8') as f:
                accumulated = json.load(f)
            
            collected_ranks = set()
            
            # 모든 URL의 랭킹 정보에서 수집된 순위 추출
            for url_hash, url_info in accumulated["url_rankings"].items():
                if url_info.get("crawled", False):  # 실제로 크롤링 완료된 것만
                    tab_rankings = url_info.get("tab_rankings", {})
                    
                    if tab_name:
                        # 특정 탭의 순위만
                        if tab_name in tab_rankings:
                            collected_ranks.add(tab_rankings[tab_name]["ranking"])
                    else:
                        # 모든 탭의 순위
                        for tab, ranking_info in tab_rankings.items():
                            collected_ranks.add(ranking_info["ranking"])
            
            return sorted(list(collected_ranks))
            
        except Exception as e:
            print(f"❌ 수집된 순위 조회 실패: {e}")
            return []
    
    def get_next_available_rank(self, city_name, tab_name=None, start_from=1):
        """🆕 다음 가용한 순위 찾기 (범용)"""
        try:
            collected_ranks = self.get_collected_ranks(city_name, tab_name)
            
            # start_from부터 시작해서 첫 번째 빈 순위 찾기
            next_rank = start_from
            while next_rank in collected_ranks:
                next_rank += 1
            
            return next_rank
            
        except Exception as e:
            print(f"❌ 다음 가용 순위 찾기 실패: {e}")
            return start_from
    
    def get_next_available_range(self, city_name, count=3, tab_name=None, fill_gaps=True):
        """🆕 다음 수집 가능한 순위 범위 계산 (범용 - 핵심 기능)"""
        try:
            collected_ranks = self.get_collected_ranks(city_name, tab_name)
            
            if not collected_ranks:
                # 아무것도 수집되지 않은 경우
                return 1, count
            
            available_ranks = []
            
            if fill_gaps:
                # 갭 채우기 모드: 1부터 시작해서 빈 순위들 찾기
                max_collected = max(collected_ranks)
                for rank in range(1, max_collected + count + 1):
                    if rank not in collected_ranks:
                        available_ranks.append(rank)
                    if len(available_ranks) >= count:
                        break
            else:
                # 연속 모드: 마지막 수집 순위 다음부터
                max_collected = max(collected_ranks)
                for rank in range(max_collected + 1, max_collected + count + 1):
                    available_ranks.append(rank)
            
            if available_ranks:
                return min(available_ranks), max(available_ranks)
            else:
                # 모든 순위가 채워진 경우
                max_collected = max(collected_ranks) if collected_ranks else 0
                return max_collected + 1, max_collected + count
                
        except Exception as e:
            print(f"❌ 다음 가용 범위 계산 실패: {e}")
            return 1, count
    
    def clear_city_data(self, city_name):
        """🆕 특정 도시의 랭킹 데이터 완전 초기화"""
        try:
            city_code = get_city_code(city_name)
            accumulated_file = os.path.join(self.ranking_dir, f"{city_code}_accumulated_rankings.json")
            
            if os.path.exists(accumulated_file):
                os.remove(accumulated_file)
                print(f"✅ '{city_name}' 랭킹 데이터 초기화 완료")
                return True
            else:
                print(f"ℹ️ '{city_name}' 랭킹 데이터가 없습니다")
                return True
                
        except Exception as e:
            print(f"❌ 랭킹 데이터 초기화 실패: {e}")
            return False

# 전역 랭킹 매니저 인스턴스
ranking_manager = RankingManager()

print("✅ 랭킹 매니저 시스템 로드 완료!")
print("   🏆 기능:")
print("   - save_tab_ranking(): 탭별 랭킹 데이터 저장")
print("   - get_url_rankings(): URL별 모든 탭 랭킹 조회")
print("   - should_crawl_url(): 중복 URL 크롤링 여부 확인")
print("   - mark_url_crawled(): 크롤링 완료 표시")