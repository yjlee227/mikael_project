"""
도시 정보 관리 시스템
- 도시명 별칭 처리 (동의어 변환)
- 도시 정보 조회 및 검증
- config.py의 UNIFIED_CITY_INFO와 연동
"""

from ..config import UNIFIED_CITY_INFO, get_city_code, get_city_info

# 도시명 별칭 매핑 테이블
CITY_ALIASES = {
    # 일본 도시들
    "쿠마모토": "구마모토",
    "토쿄": "도쿄",
    "오사카": "오사카",
    "교토": "교토",
    "후쿠오카": "후쿠오카",
    "나고야": "나고야",
    "삿포로": "삿포로",
    "요코하마": "요코하마",
    
    # 중국 도시들  
    "베이징": "베이징",
    "북경": "베이징",
    "상하이": "상하이",
    "상해": "상하이",
    "광저우": "광저우",
    "선전": "선전",
    "심천": "선전",
    "청두": "청두",
    "성도": "청두",
    
    # 한국 도시들
    "서울": "서울",
    "seoul": "서울",
    "부산": "부산",
    "busan": "부산",
    "제주": "제주",
    "제주도": "제주",
    "jeju": "제주",
    
    # 동남아시아
    "타이페이": "타이베이",
    "타이백": "타이베이",
    "방콕": "방콕",
    "bangkok": "방콕",
    "다낭": "다낭",
    "호치민": "호치민",
    "사이공": "호치민",
    
    # 유럽
    "파리": "파리",
    "paris": "파리",
    "런던": "런던",
    "london": "런던",
    "로마": "로마",
    "rome": "로마",
}

def normalize_city_name(city_input):
    """
    도시명 정규화 (별칭 → 표준명 변환)
    
    Args:
        city_input (str): 입력된 도시명
        
    Returns:
        str: 정규화된 표준 도시명
    """
    if not city_input:
        return city_input
    
    # 공백 제거 및 소문자 변환 후 다시 원래 케이스로
    city_clean = city_input.strip()
    
    # 별칭 테이블에서 검색
    normalized = CITY_ALIASES.get(city_clean, city_clean)
    
    print(f"🌍 도시명 정규화: '{city_input}' → '{normalized}'")
    return normalized

def is_city_supported(city_name):
    """
    지원되는 도시인지 확인
    
    Args:
        city_name (str): 도시명
        
    Returns:
        bool: 지원 여부
    """
    normalized_city = normalize_city_name(city_name)
    return normalized_city in UNIFIED_CITY_INFO

def get_supported_cities():
    """
    지원되는 모든 도시 목록 반환
    
    Returns:
        list: 지원되는 도시명 리스트
    """
    return list(UNIFIED_CITY_INFO.keys())

def get_city_full_info(city_name):
    """
    도시의 전체 정보 반환
    
    Args:
        city_name (str): 도시명
        
    Returns:
        dict: 도시 정보 (대륙, 국가, 코드, 영문명)
    """
    normalized_city = normalize_city_name(city_name)
    
    if normalized_city in UNIFIED_CITY_INFO:
        info = UNIFIED_CITY_INFO[normalized_city].copy()
        info['한국명'] = normalized_city
        return info
    else:
        return {
            '한국명': normalized_city,
            '대륙': '기타',
            '국가': '기타',
            '코드': normalized_city[:3].upper(),
            '영문명': normalized_city.lower()
        }

def validate_city_list(city_list):
    """
    도시 목록 검증 및 정규화
    
    Args:
        city_list (list): 도시명 리스트
        
    Returns:
        tuple: (정규화된_도시_리스트, 지원되지_않는_도시_리스트)
    """
    normalized_cities = []
    unsupported_cities = []
    
    for city in city_list:
        normalized = normalize_city_name(city)
        if is_city_supported(normalized):
            normalized_cities.append(normalized)
        else:
            unsupported_cities.append(city)
    
    return normalized_cities, unsupported_cities

def get_cities_by_region(continent=None, country=None):
    """
    지역별 도시 목록 조회
    
    Args:
        continent (str, optional): 대륙명
        country (str, optional): 국가명
        
    Returns:
        list: 해당 지역의 도시 리스트
    """
    result = []
    
    for city, info in UNIFIED_CITY_INFO.items():
        if continent and info['대륙'] != continent:
            continue
        if country and info['국가'] != country:
            continue
        result.append(city)
    
    return result

# 편의 함수들 (기존 코드와의 호환성)
def get_city_airport_code(city_name):
    """도시의 공항 코드 조회"""
    normalized_city = normalize_city_name(city_name)
    return get_city_code(normalized_city)

def get_city_continent_country(city_name):
    """도시의 대륙, 국가 정보 조회"""
    normalized_city = normalize_city_name(city_name)
    return get_city_info(normalized_city)

print("✅ city_manager.py 로드 완료: 도시 정보 관리 시스템 준비!")