"""
🎯 순위 매퍼: URL 배열 인덱스 → 실제 순위 매핑 시스템
URL 리스트에서의 위치와 실제 페이지 순위를 정확히 매핑
"""

import json
import hashlib
from .config import get_city_code

class RankMapper:
    """URL 배열 순서와 실제 순위 매핑 시스템"""
    
    def __init__(self, ranking_dir="ranking_data"):
        self.ranking_dir = ranking_dir
        self.cache = {}
    
    def get_actual_ranks_from_urls(self, urls, city_name, tab_name):
        """URL 리스트에서 각 URL의 실제 순위를 찾아서 매핑"""
        try:
            city_code = get_city_code(city_name)
            accumulated_file = f"{self.ranking_dir}/{city_code}_accumulated_rankings.json"
            
            # 캐시 키
            cache_key = f"{city_code}_{tab_name}"
            
            if cache_key not in self.cache:
                # 누적 랭킹 데이터 로드
                with open(accumulated_file, 'r', encoding='utf-8') as f:
                    accumulated = json.load(f)
                
                # URL 해시 → 실제 순위 매핑 생성
                self.cache[cache_key] = {}
                for url_hash, url_info in accumulated["url_rankings"].items():
                    if tab_name in url_info["tab_rankings"]:
                        actual_rank = url_info["tab_rankings"][tab_name]["ranking"]
                        self.cache[cache_key][url_hash] = actual_rank
            
            # URL 배열의 각 URL에 대해 실제 순위 찾기
            rank_mapping = []
            for array_index, url in enumerate(urls):
                url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
                actual_rank = self.cache[cache_key].get(url_hash, array_index + 1)  # 기본값: 배열 인덱스 + 1
                
                rank_mapping.append({
                    'array_index': array_index,
                    'url': url,
                    'url_hash': url_hash,
                    'actual_rank': actual_rank
                })
            
            return rank_mapping
            
        except Exception as e:
            print(f"❌ 순위 매핑 실패: {e}")
            # 실패 시 기본 매핑 (인덱스 기반)
            return [
                {
                    'array_index': i,
                    'url': url,
                    'url_hash': hashlib.md5(url.encode('utf-8')).hexdigest(),
                    'actual_rank': i + 1
                }
                for i, url in enumerate(urls)
            ]
    
    def map_range_to_actual_ranks(self, urls, city_name, tab_name, start_rank, end_rank):
        """지정된 순위 범위에 해당하는 URL들을 실제 순위와 함께 매핑"""
        try:
            # 모든 URL의 실제 순위 매핑 획득
            all_mappings = self.get_actual_ranks_from_urls(urls, city_name, tab_name)
            
            # 지정된 순위 범위에 해당하는 URL들만 필터링
            target_mappings = []
            for mapping in all_mappings:
                if start_rank <= mapping['actual_rank'] <= end_rank:
                    target_mappings.append(mapping)
            
            # 실제 순위 순으로 정렬
            target_mappings.sort(key=lambda x: x['actual_rank'])
            
            return target_mappings
            
        except Exception as e:
            print(f"❌ 범위 매핑 실패: {e}")
            return []
    
    def get_url_by_actual_rank(self, urls, city_name, tab_name, target_rank):
        """실제 순위로 URL 찾기"""
        try:
            rank_mappings = self.get_actual_ranks_from_urls(urls, city_name, tab_name)
            
            for mapping in rank_mappings:
                if mapping['actual_rank'] == target_rank:
                    return mapping
            
            return None
            
        except Exception as e:
            print(f"❌ 순위별 URL 조회 실패: {e}")
            return None
    
    def clear_cache(self):
        """매핑 캐시 초기화"""
        self.cache = {}

# 전역 순위 매퍼 인스턴스
rank_mapper = RankMapper()

print("✅ 순위 매퍼 시스템 로드 완료!")
print("   🎯 기능:")
print("   - get_actual_ranks_from_urls(): URL 배열에서 실제 순위 매핑")
print("   - map_range_to_actual_ranks(): 순위 범위별 URL 매핑") 
print("   - get_url_by_actual_rank(): 실제 순위로 URL 찾기")