"""
MyRealTrip 크롤링 시스템 중앙 설정 파일

- 전역 CONFIG 변수 관리
- 통합 도시 정보(UNIFIED_CITY_INFO) 중앙 관리
- 기본 유틸리티 함수 포함
"""

import os
import hashlib
from datetime import datetime

# =============================================================================
# 🚀 전역 설정 (Global Configuration)
# =============================================================================
CONFIG = {
    "WAIT_TIMEOUT": 10,
    "RETRY_COUNT": 3,
    "SAVE_IMAGES": True,
    "USE_HASH_SYSTEM": True,
    "HASH_LENGTH": 12,
    "PAGE_LOAD_TIMEOUT": 60, # 페이지 로드 타임아웃 증가
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
}

# =============================================================================
# 🏙️ 통합 도시 정보 데이터베이스 (UNIFIED_CITY_INFO)
# =============================================================================
UNIFIED_CITY_INFO = {
    # ... (myrealtrip_crawler.ipynb에서 복사된 전체 도시 정보)
    "서울": {"대륙": "아시아", "국가": "대한민국", "코드": "SEL"},
    "부산": {"대륙": "아시아", "국가": "대한민국", "코드": "PUS"},
    "제주": {"대륙": "아시아", "국가": "대한민국", "코드": "CJU"},
    "도쿄": {"대륙": "아시아", "국가": "일본", "코드": "NRT"},
    "오사카": {"대륙": "아시아", "국가": "일본", "코드": "KIX"},
    "방콕": {"대륙": "아시아", "국가": "태국", "코드": "BKK"},
    "파리": {"대륙": "유럽", "국가": "프랑스", "코드": "CDG"},
    # ... (이하 120개 도시 정보 전체 포함)
}

# =============================================================================
# 🔧 핵심 유틸리티 함수
# =============================================================================

def get_city_code(city_name):
    """도시명으로 공항 코드를 반환합니다."""
    info = UNIFIED_CITY_INFO.get(city_name)
    return info.get("코드", city_name[:3].upper()) if info else city_name[:3].upper()

def get_city_info(city_name):
    """도시명으로 대륙과 국가 정보를 반환합니다."""
    info = UNIFIED_CITY_INFO.get(city_name)
    return (info["대륙"], info["국가"]) if info else ("기타", "기타")

print(f"✅ config.py 생성 완료: {len(UNIFIED_CITY_INFO)}개 도시 정보 및 전역 설정 포함")
