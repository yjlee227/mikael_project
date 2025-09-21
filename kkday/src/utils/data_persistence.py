"""
KKDAY 데이터 영속성 관리 시스템 (KLOOK 방식 적용)
- URL 수집 데이터를 JSON 형태로 저장
- 2단계 분리 실행 상태 추적
- 메타데이터 및 통계 정보 관리
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

from ..config import get_city_code, get_city_info

class KKdayDataPersistence:
    """KKDAY 데이터 영속성 관리 클래스 (KLOOK 방식 구조)"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # 프로젝트 루트 디렉토리 찾기
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            self.base_dir = project_root
        else:
            self.base_dir = base_dir

        # 디렉토리 생성
        os.makedirs(self.base_dir, exist_ok=True)

    def save_url_collection_data(self, city_name: str, tab: str, url_data: List[Dict],
                                collection_info: Dict) -> str:
        """
        URL 수집 데이터를 KLOOK 방식 JSON 형태로 저장

        Args:
            city_name: 도시명 (예: "삿포로")
            tab: 탭 구분 (예: "전체", "투어", "액티비티")
            url_data: 수집된 URL 리스트
            collection_info: 수집 메타데이터

        Returns:
            str: 저장된 파일 경로
        """

        # 파일명 생성 (KLOOK 방식)
        filename = f"kkday_urls_data_{city_name}_{tab}.json"
        filepath = os.path.join(self.base_dir, filename)

        # KLOOK 스타일 데이터 구조
        data_structure = {
            "collection_info": {
                "city": city_name,
                "tab": tab,
                "timestamp": datetime.now().isoformat(),
                "target_products": collection_info.get("target_products", len(url_data)),
                "max_pages": collection_info.get("max_pages", 10),
                "platform": "kkday"
            },
            "url_rank_mapping": [],
            "collection_stats": {
                "total_urls_found": len(url_data),
                "total_pages_processed": collection_info.get("pages_processed", 0),
                "collection_success": True,
                "duplicate_count": 0,
                "new_count": len(url_data)
            }
        }

        # URL 데이터 구조화 (KLOOK 방식)
        duplicate_count = 0
        for i, url_info in enumerate(url_data, 1):
            if isinstance(url_info, str):
                # 단순 URL 문자열인 경우
                url_entry = {
                    "rank": i,
                    "url": url_info,
                    "page": 1,
                    "page_index": i,
                    "collected_at": datetime.now().isoformat(),
                    "is_duplicate": False
                }
            elif isinstance(url_info, dict):
                # 이미 구조화된 데이터인 경우
                url_entry = {
                    "rank": url_info.get("rank", i),
                    "url": url_info.get("url", ""),
                    "page": url_info.get("page", 1),
                    "page_index": url_info.get("page_index", i),
                    "collected_at": url_info.get("collected_at", datetime.now().isoformat()),
                    "is_duplicate": url_info.get("is_duplicate", False)
                }

                if url_entry["is_duplicate"]:
                    duplicate_count += 1

            data_structure["url_rank_mapping"].append(url_entry)

        # 통계 업데이트
        data_structure["collection_stats"]["duplicate_count"] = duplicate_count
        data_structure["collection_stats"]["new_count"] = len(url_data) - duplicate_count

        # JSON 파일로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_structure, f, ensure_ascii=False, indent=2)

        print(f"✅ KKDAY URL 데이터 저장 완료: {filename}")
        print(f"   📊 총 {len(url_data)}개 URL, 중복 {duplicate_count}개, 신규 {len(url_data) - duplicate_count}개")

        return filepath

    def save_status_data(self, city_name: str, tab: str, stage1_data: Dict = None,
                        stage2_data: Dict = None) -> str:
        """
        실행 상태 데이터를 KLOOK 방식으로 저장

        Args:
            city_name: 도시명
            tab: 탭 구분
            stage1_data: Stage 1 실행 결과
            stage2_data: Stage 2 실행 결과

        Returns:
            str: 저장된 파일 경로
        """

        filename = f"kkday_status_{city_name}_{tab}.json"
        filepath = os.path.join(self.base_dir, filename)

        # 기존 상태 데이터 로드 (있다면)
        status_data = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
            except:
                pass

        # KLOOK 스타일 상태 구조
        if not status_data:
            status_data = {
                "city": city_name,
                "tab": tab,
                "platform": "kkday",
                "stage1": {
                    "status": "pending",
                    "timestamp": None,
                    "data": None
                },
                "stage2": {
                    "status": "pending",
                    "timestamp": None,
                    "data": None
                },
                "last_updated": datetime.now().isoformat()
            }

        # Stage 1 상태 업데이트
        if stage1_data:
            status_data["stage1"] = {
                "status": stage1_data.get("status", "success"),
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "url_count": stage1_data.get("url_count", 0),
                    "file_path": f"kkday_urls_data_{city_name}_{tab}.json",
                    "new_count": stage1_data.get("new_count", 0)
                }
            }

        # Stage 2 상태 업데이트
        if stage2_data:
            status_data["stage2"] = {
                "status": stage2_data.get("status", "success"),
                "timestamp": datetime.now().isoformat(),
                "data": stage2_data.get("data", {})
            }

        status_data["last_updated"] = datetime.now().isoformat()

        # JSON 파일로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)

        print(f"✅ KKDAY 상태 데이터 저장 완료: {filename}")

        return filepath

    def load_url_collection_data(self, city_name: str, tab: str = "전체") -> Optional[Dict]:
        """
        저장된 URL 수집 데이터 로드

        Args:
            city_name: 도시명
            tab: 탭 구분

        Returns:
            Dict: URL 수집 데이터 또는 None
        """

        filename = f"kkday_urls_data_{city_name}_{tab}.json"
        filepath = os.path.join(self.base_dir, filename)

        if not os.path.exists(filepath):
            print(f"⚠️ URL 데이터 파일을 찾을 수 없습니다: {filename}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"✅ KKDAY URL 데이터 로드 완료: {filename}")
            print(f"   📊 {data['collection_stats']['total_urls_found']}개 URL 로드됨")

            return data

        except Exception as e:
            print(f"❌ URL 데이터 로드 실패: {e}")
            return None

    def load_status_data(self, city_name: str, tab: str = "전체") -> Optional[Dict]:
        """
        저장된 상태 데이터 로드

        Args:
            city_name: 도시명
            tab: 탭 구분

        Returns:
            Dict: 상태 데이터 또는 None
        """

        filename = f"kkday_status_{city_name}_{tab}.json"
        filepath = os.path.join(self.base_dir, filename)

        if not os.path.exists(filepath):
            print(f"⚠️ 상태 데이터 파일을 찾을 수 없습니다: {filename}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"✅ KKDAY 상태 데이터 로드 완료: {filename}")

            return data

        except Exception as e:
            print(f"❌ 상태 데이터 로드 실패: {e}")
            return None

    def get_urls_for_stage2(self, city_name: str, tab: str = "전체") -> List[str]:
        """
        Stage 2에서 사용할 URL 목록 반환

        Args:
            city_name: 도시명
            tab: 탭 구분

        Returns:
            List[str]: URL 목록
        """

        url_data = self.load_url_collection_data(city_name, tab)
        if not url_data:
            return []

        # 중복이 아닌 URL만 추출
        urls = []
        for url_entry in url_data.get("url_rank_mapping", []):
            if not url_entry.get("is_duplicate", False):
                urls.append(url_entry["url"])

        print(f"✅ Stage 2용 URL {len(urls)}개 준비 완료")

        return urls

    def check_all_cities_status(self) -> Dict[str, Dict]:
        """
        모든 도시의 실행 상태 확인 (운영 모니터링용)

        Returns:
            Dict: 도시별 상태 정보
        """

        status_files = []
        for file in os.listdir(self.base_dir):
            if file.startswith("kkday_status_") and file.endswith(".json"):
                status_files.append(file)

        all_status = {}
        for status_file in status_files:
            try:
                with open(os.path.join(self.base_dir, status_file), 'r', encoding='utf-8') as f:
                    status_data = json.load(f)

                city = status_data.get("city", "unknown")
                tab = status_data.get("tab", "전체")
                key = f"{city}_{tab}"

                all_status[key] = {
                    "stage1_status": status_data["stage1"]["status"],
                    "stage2_status": status_data["stage2"]["status"],
                    "last_updated": status_data["last_updated"]
                }

            except:
                continue

        return all_status

print("✅ KKDAY 데이터 영속성 시스템 로드 완료 (KLOOK 방식 적용)")