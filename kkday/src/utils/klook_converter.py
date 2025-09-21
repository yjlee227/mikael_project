"""
KLOOK 스타일 파일 생성 및 관리
- KKDAY URL 데이터를 KLOOK 방식 JSON으로 변환
- 상태 추적 및 관리
- Stage 2에서 JSON 데이터 로드
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


def create_klook_style_files(city_name: str, urls: List[str], tab: str = "전체") -> tuple:
    """
    KLOOK 스타일 JSON 파일 2개 생성

    Args:
        city_name: 도시명 (예: "삿포로", "도쿄")
        urls: URL 리스트
        tab: 탭 구분 (기본값: "전체")

    Returns:
        tuple: (url_file_path, status_file_path)
    """
    print(f"\n🔄 KLOOK 스타일 JSON 파일 생성 중...")
    print(f"   🏙️ 도시: {city_name}")
    print(f"   🏷️ 탭: {tab}")
    print(f"   📊 URL 개수: {len(urls)}개")

    try:
        # 1. URL 데이터 파일 구조 (KLOOK 방식)
        url_data = {
            "collection_info": {
                "city": city_name,
                "tab": tab,
                "timestamp": datetime.now().isoformat(),
                "target_products": len(urls),
                "max_pages": 10,  # 기본값
                "platform": "kkday"
            },
            "url_rank_mapping": [],
            "collection_stats": {
                "total_urls_found": len(urls),
                "total_pages_processed": 1,  # 기본값
                "collection_success": True,
                "duplicate_count": 0,
                "new_count": len(urls)
            }
        }

        # URL 데이터 구조화
        for i, url in enumerate(urls, 1):
            url_entry = {
                "rank": i,
                "url": url,
                "page": 1,
                "page_index": i,
                "collected_at": datetime.now().isoformat(),
                "is_duplicate": False
            }
            url_data["url_rank_mapping"].append(url_entry)

        # 2. 상태 파일 구조 (KLOOK 방식)
        status_data = {
            "city": city_name,
            "tab": tab,
            "platform": "kkday",
            "stage1": {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "url_count": len(urls),
                    "file_path": f"kkday_urls_data_{city_name}_{tab}.json",
                    "new_count": len(urls)
                }
            },
            "stage2": {
                "status": "pending",
                "timestamp": None,
                "data": None
            },
            "last_updated": datetime.now().isoformat()
        }

        # 3. 파일 저장
        url_file = f"kkday_urls_data_{city_name}_{tab}.json"
        status_file = f"kkday_status_{city_name}_{tab}.json"

        # URL 데이터 파일 저장
        with open(url_file, 'w', encoding='utf-8') as f:
            json.dump(url_data, f, ensure_ascii=False, indent=2)

        # 상태 파일 저장
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)

        print(f"✅ KLOOK 스타일 JSON 파일 생성 완료!")
        print(f"   📄 URL 데이터: {url_file}")
        print(f"   📊 상태 파일: {status_file}")
        print(f"   🎯 총 {len(urls)}개 URL 저장됨")

        return url_file, status_file

    except Exception as e:
        print(f"❌ KLOOK 스타일 파일 생성 실패: {e}")
        return None, None


def load_urls_for_stage2(city_name: str, tab: str = "전체") -> List[str]:
    """
    Stage 2용 URL 로드 (JSON 전용)

    Args:
        city_name: 도시명
        tab: 탭 구분

    Returns:
        List[str]: URL 리스트
    """
    print(f"\n📥 Stage 2용 URL 로드 중...")

    json_file = f"kkday_urls_data_{city_name}_{tab}.json"

    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # URL 추출
            urls = []
            for url_entry in data.get("url_rank_mapping", []):
                if not url_entry.get("is_duplicate", False):
                    urls.append(url_entry["url"])

            print(f"✅ JSON에서 {len(urls)}개 URL 로드 완료")
            print(f"   📄 파일: {json_file}")
            print(f"   🔄 KLOOK 방식 메타데이터 포함")

            return urls

        except Exception as e:
            print(f"❌ JSON 파일 읽기 실패: {e}")

    # JSON 파일이 없거나 실패한 경우
    print(f"❌ URL 파일을 찾을 수 없습니다:")
    print(f"   📄 파일: {json_file}")
    print(f"💡 먼저 Stage 1(URL 수집)을 실행하세요.")

    return []


def update_stage2_status(city_name: str, stage2_data: Dict, tab: str = "전체") -> bool:
    """
    Stage 2 완료 시 상태 파일 업데이트

    Args:
        city_name: 도시명
        stage2_data: Stage 2 실행 결과 데이터
        tab: 탭 구분

    Returns:
        bool: 업데이트 성공 여부
    """
    print(f"\n📊 Stage 2 상태 업데이트 중...")

    status_file = f"kkday_status_{city_name}_{tab}.json"

    try:
        # 기존 상태 파일 읽기
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
        else:
            print(f"⚠️ 상태 파일이 없어 새로 생성: {status_file}")
            status_data = {
                "city": city_name,
                "tab": tab,
                "platform": "kkday",
                "stage1": {"status": "unknown"},
                "stage2": {"status": "pending"}
            }

        # Stage 2 상태 업데이트
        status_data["stage2"] = {
            "status": stage2_data.get("status", "success"),
            "timestamp": datetime.now().isoformat(),
            "data": stage2_data.get("data", {})
        }
        status_data["last_updated"] = datetime.now().isoformat()

        # 파일 저장
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Stage 2 상태 업데이트 완료!")
        print(f"   📊 파일: {status_file}")
        print(f"   📈 상태: {stage2_data.get('status', 'success')}")

        return True

    except Exception as e:
        print(f"❌ 상태 업데이트 실패: {e}")
        return False


def get_klook_style_status(city_name: str, tab: str = "전체") -> Optional[Dict]:
    """
    현재 진행 상태 확인

    Args:
        city_name: 도시명
        tab: 탭 구분

    Returns:
        Dict: 상태 데이터 또는 None
    """
    status_file = f"kkday_status_{city_name}_{tab}.json"

    if not os.path.exists(status_file):
        return None

    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 상태 파일 읽기 실패: {e}")
        return None


# 모듈 로드 확인
print("✅ KLOOK 변환 유틸리티 로드 완료")
print("   📦 함수:")
print("   - create_klook_style_files(): KLOOK 스타일 JSON 파일 생성")
print("   - load_urls_for_stage2(): Stage 2용 URL 로드")
print("   - update_stage2_status(): Stage 2 상태 업데이트")
print("   - get_klook_style_status(): 현재 상태 확인")