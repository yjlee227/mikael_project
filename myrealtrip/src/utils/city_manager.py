"""
도시 정보 관리 시스템
- 도시명 별칭 처리 (동의어 변환)
- 도시 정보 조회 및 검증
"""

# 중앙 설정에서 도시 정보와 기본 함수를 import
from ..config import UNIFIED_CITY_INFO, get_city_code, get_city_info

# 도시명 별칭(동의어) 매핑 테이블
CITY_ALIASES = {
    "쿠마모토": "구마모토",
    "토쿄": "도쿄",
    "북경": "베이징",
    "상해": "상하이",
    "타이페이": "타이베이",
    "KL": "쿠알라룸푸르",
    "LA": "로스앤젤레스",
    # ... (기타 필요한 별칭 추가)
}

def normalize_city_name(city_input):
    """도시명을 표준 이름으로 변환합니다 (예: 토쿄 -> 도쿄)."""
    if not city_input:
        return city_input
    
    city_clean = city_input.strip()
    normalized = CITY_ALIASES.get(city_clean, city_clean)
    
    # 원본과 다를 경우에만 로그 출력
    if city_input != normalized:
        print(f"🌍 도시명 정규화: '{city_input}' → '{normalized}'")
    return normalized

def is_city_supported(city_name):
    """지원되는 도시인지 확인합니다."""
    normalized_city = normalize_city_name(city_name)
    return normalized_city in UNIFIED_CITY_INFO

def get_supported_cities():
    """지원되는 모든 도시 목록을 반환합니다."""
    return list(UNIFIED_CITY_INFO.keys())

print("✅ city_manager.py 리팩토링 완료: 이제 config.py의 중앙 데이터를 사용합니다.")