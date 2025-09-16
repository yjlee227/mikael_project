"""
순위 관리 및 매핑 시스템 (도시별 분리 저장 방식)
- 도시별 순위 데이터 관리
- 순위 연속성 보장
"""
import os
import json
import hashlib
from datetime import datetime

from ..config import get_city_code, mark_url_processed_fast

# =============================================================================
# 도시별 순위 매핑 시스템
# =============================================================================

class RankMapper:
    """도시별 순위 매핑 관리"""

    def __init__(self, mapping_dir="ranking_data"):
        self.mapping_dir = mapping_dir
        self.city_mappings = {}  # 도시별 매핑 캐시
        os.makedirs(self.mapping_dir, exist_ok=True)

    def _get_city_filepath(self, city_name):
        """도시별 매핑 파일 경로 생성"""
        city_code = get_city_code(city_name)
        return os.path.join(self.mapping_dir, f"{city_code}_rank_mapping.json")

    def load_city_mappings(self, city_name):
        """도시별 순위 매핑 로드"""
        if city_name in self.city_mappings:
            return self.city_mappings[city_name]

        mapping_file = self._get_city_filepath(city_name)
        try:
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
            else:
                mappings = {}

            self.city_mappings[city_name] = mappings
            return mappings

        except Exception as e:
            print(f"⚠️ {city_name} 매핑 로드 실패: {e}")
            self.city_mappings[city_name] = {}
            return {}

    def save_city_mappings(self, city_name):
        """도시별 순위 매핑 저장"""
        mapping_file = self._get_city_filepath(city_name)
        try:
            mappings = self.city_mappings.get(city_name, {})
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mappings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ {city_name} 매핑 저장 실패: {e}")
            return False

    def add_mapping(self, url, rank, city_name, product_id, tab_name="default"):
        """순위 매핑 추가"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        mappings = self.load_city_mappings(city_name)

        # 기존에 같은 URL이 있으면 업데이트, 없으면 새로 추가
        entry = mappings.get(url, {
            "hash": url_hash,
            "city": city_name,
            "product_id": product_id,
            "rankings": []
        })

        # 순위 정보 업데이트 또는 추가
        existing_rank_info = next((r for r in entry["rankings"] if r["tab"] == tab_name), None)
        if existing_rank_info:
            existing_rank_info["rank"] = rank
            existing_rank_info["added_at"] = datetime.now().isoformat()
        else:
            entry["rankings"].append({
                "rank": rank,
                "tab": tab_name,
                "added_at": datetime.now().isoformat()
            })

        mappings[url] = entry
        self.city_mappings[city_name] = mappings
        return self.save_city_mappings(city_name)

    def get_next_rank(self, city_name):
        """도시의 마지막 순위를 찾아 다음 순위를 반환"""
        mappings = self.load_city_mappings(city_name)
        if not mappings:
            return 1  # 해당 도시에 데이터가 없으면 1부터 시작

        max_rank = 0
        for url_data in mappings.values():
            for ranking_info in url_data.get("rankings", []):
                if ranking_info.get("rank", 0) > max_rank:
                    max_rank = ranking_info["rank"]

        next_rank = max_rank + 1
        print(f"ℹ️ {city_name} 다음 시작 순위 계산됨: {next_rank}")
        return next_rank

# =============================================================================
# 통합 순위 시스템 인터페이스
# =============================================================================

# 전역 인스턴스 생성
rank_mapper = RankMapper()

def save_url_with_rank(url, rank, city_name, product_id, tab_name="default"):
    """URL과 순위 정보를 새 시스템에 저장"""
    try:
        success = rank_mapper.add_mapping(url, rank, city_name, product_id, tab_name)
        mark_url_processed_fast(url, city_name, rank=rank, product_id=product_id)

        if success:
            print(f"✅ 순위 정보 저장 완료: Rank={rank}")
        else:
            print(f"⚠️ 순위 정보 저장 실패: Rank={rank}")

        return success
    except Exception as e:
        print(f"❌ 순위 정보 저장 중 심각한 오류: {e}")
        return False

def get_next_start_rank(city_name):
    """크롤링 시작 전, 다음 순위를 가져오는 함수"""
    return rank_mapper.get_next_rank(city_name)

print("✅ ranking.py 로드 완료: 도시별 순위 관리 시스템 준비!")