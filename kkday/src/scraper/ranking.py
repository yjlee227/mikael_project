"""
순위 관리 및 매핑 시스템
- 상품 순위 정보 수집 및 저장
- URL별 순위 매핑 관리
- 순위 데이터 분석 및 조회
"""

import os
import json
import hashlib
from datetime import datetime
from collections import defaultdict

from ..config import get_city_code, is_url_processed_fast, mark_url_processed_fast

# =============================================================================
# 순위 데이터 구조 관리
# =============================================================================

class RankingManager:
    """순위 관리 시스템"""
    
    def __init__(self):
        self.ranking_dir = "ranking_data"
        self.ranking_cache = {}
        
    def save_tab_ranking(self, urls_with_ranking, city_name, tab_name, strategy="default"):
        """탭에서 수집한 URL들과 순위 정보 저장"""
        if not urls_with_ranking:
            return False
        
        try:
            os.makedirs(self.ranking_dir, exist_ok=True)
            
            city_code = get_city_code(city_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{city_code}_{tab_name}_{strategy}_{timestamp}.json"
            filepath = os.path.join(self.ranking_dir, filename)
            
            # URL별 순위 정보 구조화
            ranking_data = {
                "city_name": city_name,
                "city_code": city_code,
                "tab_name": tab_name,
                "strategy": strategy,
                "collected_at": datetime.now().isoformat(),
                "total_urls": len(urls_with_ranking),
                "url_rankings": []
            }
            
            for url, rank in urls_with_ranking:
                ranking_data["url_rankings"].append({
                    "url": url,
                    "rank": rank,
                    "tab": tab_name,
                    "hash": hashlib.md5(url.encode()).hexdigest()[:12]
                })
            
            # JSON 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(ranking_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 순위 데이터 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 순위 데이터 저장 실패: {e}")
            return False
    
    def get_url_rankings(self, city_name, url=None):
        """URL의 모든 순위 정보 조회"""
        try:
            city_code = get_city_code(city_name)
            
            # 해당 도시의 모든 순위 파일 검색
            ranking_files = []
            if os.path.exists(self.ranking_dir):
                for file in os.listdir(self.ranking_dir):
                    if file.startswith(city_code) and file.endswith('.json'):
                        ranking_files.append(os.path.join(self.ranking_dir, file))
            
            url_rankings = defaultdict(list)
            
            for file_path in ranking_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    for item in data.get('url_rankings', []):
                        item_url = item['url']
                        
                        # 특정 URL이 지정된 경우 필터링
                        if url and item_url != url:
                            continue
                        
                        url_rankings[item_url].append({
                            'rank': item['rank'],
                            'tab': item['tab'],
                            'collected_at': data['collected_at'],
                            'strategy': data.get('strategy', 'default')
                        })
                        
                except Exception:
                    continue
            
            return dict(url_rankings)
            
        except Exception as e:
            print(f"⚠️ 순위 조회 실패: {e}")
            return {}
    
    def get_next_available_range(self, city_name, count=3, tab_name=None, fill_gaps=True):
        """다음 수집할 순위 범위 계산"""
        try:
            # 기존 순위 데이터 조회
            url_rankings = self.get_url_rankings(city_name)
            
            collected_ranks = set()
            for url, rankings in url_rankings.items():
                for ranking_info in rankings:
                    # 특정 탭이 지정된 경우 필터링
                    if tab_name and ranking_info['tab'] != tab_name:
                        continue
                    collected_ranks.add(ranking_info['rank'])
            
            if not collected_ranks:
                return 1, count
            
            # 갭 채우기 모드
            if fill_gaps:
                max_rank = max(collected_ranks)
                for i in range(1, max_rank + 1):
                    if i not in collected_ranks:
                        # 갭 발견
                        return i, min(i + count - 1, max_rank + count)
            
            # 연속 모드: 다음 순위부터 시작
            next_start = max(collected_ranks) + 1
            return next_start, next_start + count - 1
            
        except Exception as e:
            print(f"⚠️ 순위 범위 계산 실패: {e}")
            return 1, count

# =============================================================================
# 순위 매핑 시스템
# =============================================================================

class RankMapper:
    """순위 매핑 관리"""
    
    def __init__(self):
        self.mapping_file = "rank_mapping.json"
        self.load_mappings()
    
    def load_mappings(self):
        """순위 매핑 로드"""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    self.mappings = json.load(f)
            else:
                self.mappings = {}
        except Exception:
            self.mappings = {}
    
    def save_mappings(self):
        """순위 매핑 저장"""
        try:
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.mappings, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def add_mapping(self, url, rank, city_name, tab_name="default"):
        """순위 매핑 추가"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        
        if url not in self.mappings:
            self.mappings[url] = {
                "hash": url_hash,
                "city": city_name,
                "rankings": []
            }
        
        # 새 순위 정보 추가
        new_ranking = {
            "rank": rank,
            "tab": tab_name,
            "added_at": datetime.now().isoformat()
        }
        
        self.mappings[url]["rankings"].append(new_ranking)
        return self.save_mappings()
    
    def get_url_rank(self, url, tab_name=None):
        """URL의 순위 조회"""
        if url not in self.mappings:
            return None
        
        rankings = self.mappings[url]["rankings"]
        
        if tab_name:
            # 특정 탭의 순위 조회
            for ranking in rankings:
                if ranking["tab"] == tab_name:
                    return ranking["rank"]
            return None
        else:
            # 가장 최근 순위 반환
            if rankings:
                return rankings[-1]["rank"]
            return None
    
    def get_ranks_in_range(self, city_name, start_rank, end_rank, tab_name=None):
        """특정 범위의 순위에 해당하는 URL들 조회"""
        urls_in_range = []
        
        for url, mapping_info in self.mappings.items():
            if mapping_info["city"] != city_name:
                continue
            
            for ranking in mapping_info["rankings"]:
                if tab_name and ranking["tab"] != tab_name:
                    continue
                
                rank = ranking["rank"]
                if start_rank <= rank <= end_rank:
                    urls_in_range.append({
                        "url": url,
                        "rank": rank,
                        "tab": ranking["tab"]
                    })
                    break  # 하나의 매핑만 추가
        
        return sorted(urls_in_range, key=lambda x: x["rank"])

# =============================================================================
# 통합 순위 시스템
# =============================================================================

# 전역 인스턴스 생성
ranking_manager = RankingManager()
rank_mapper = RankMapper()

def save_url_with_rank(url, rank, city_name, tab_name="default"):
    """URL과 순위 정보를 모든 시스템에 저장"""
    success = True
    
    try:
        # 1. RankMapper에 저장
        if not rank_mapper.add_mapping(url, rank, city_name, tab_name):
            success = False
        
        # 2. hashlib 시스템에 저장 (config.py 함수 사용)
        if not mark_url_processed_fast(url, city_name, rank=rank):
            success = False
        
        if success:
            print(f"✅ 순위 정보 저장 완료: URL={url[:50]}..., Rank={rank}")
        else:
            print(f"⚠️ 순위 정보 저장 부분 실패: Rank={rank}")
        
        return success
        
    except Exception as e:
        print(f"❌ 순위 정보 저장 실패: {e}")
        return False

def get_collected_ranks_summary(city_name, tab_name=None):
    """수집된 순위 요약 정보"""
    try:
        url_rankings = ranking_manager.get_url_rankings(city_name)
        
        if not url_rankings:
            return {
                "total_urls": 0,
                "collected_ranks": [],
                "rank_range": "없음",
                "missing_ranks": []
            }
        
        collected_ranks = set()
        for url, rankings in url_rankings.items():
            for ranking_info in rankings:
                if tab_name and ranking_info['tab'] != tab_name:
                    continue
                collected_ranks.add(ranking_info['rank'])
        
        if not collected_ranks:
            return {
                "total_urls": 0,
                "collected_ranks": [],
                "rank_range": "없음",
                "missing_ranks": []
            }
        
        sorted_ranks = sorted(collected_ranks)
        min_rank = min(sorted_ranks)
        max_rank = max(sorted_ranks)
        
        # 누락된 순위 찾기
        expected_ranks = set(range(min_rank, max_rank + 1))
        missing_ranks = sorted(expected_ranks - collected_ranks)
        
        return {
            "total_urls": len(url_rankings),
            "collected_ranks": sorted_ranks,
            "rank_range": f"{min_rank}-{max_rank}",
            "missing_ranks": missing_ranks
        }
        
    except Exception as e:
        print(f"⚠️ 순위 요약 생성 실패: {e}")
        return {"error": str(e)}

def find_next_collection_target(city_name, preferred_count=5, tab_name=None):
    """다음 수집 대상 순위 범위 추천"""
    try:
        summary = get_collected_ranks_summary(city_name, tab_name)
        
        if summary.get("error"):
            return 1, preferred_count
        
        missing_ranks = summary.get("missing_ranks", [])
        collected_ranks = summary.get("collected_ranks", [])
        
        if not collected_ranks:
            # 첫 수집
            return 1, preferred_count
        
        if missing_ranks:
            # 갭 채우기 우선
            start_missing = missing_ranks[0]
            end_missing = min(start_missing + preferred_count - 1, missing_ranks[-1])
            return start_missing, end_missing
        
        # 연속 수집
        next_start = max(collected_ranks) + 1
        return next_start, next_start + preferred_count - 1
        
    except Exception as e:
        print(f"⚠️ 수집 대상 추천 실패: {e}")
        return 1, preferred_count

print("✅ ranking.py 로드 완료: 순위 관리 시스템 준비!")