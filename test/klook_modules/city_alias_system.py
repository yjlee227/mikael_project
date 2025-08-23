#!/usr/bin/env python3
"""
🌍 도시명 별칭(동의어) 처리 시스템
- 구마모토/쿠마모토, 도쿄/토쿄 등 혼용되는 도시명 처리
- 검색 시 자동으로 올바른 도시명으로 변환
"""

# 도시명 별칭 매핑 테이블
CITY_ALIASES = {
    # 일본 도시들
    "쿠마모토": "구마모토",        # 쿠마모토 → 구마모토
    "토쿄": "도쿄",              # 토쿄 → 도쿄  
    "오사카": "오사카",           # 이미 표준
    "교토": "교토",             # 이미 표준
    "후쿠오카": "후쿠오카",        # 이미 표준
    "나고야": "나고야",          # 이미 표준
    "삿포로": "삿포로",          # 이미 표준
    "요코하마": "요코하마",        # 이미 표준
    "고베": "고베",             # 이미 표준
    "히로시마": "히로시마",        # 이미 표준
    "나하": "나하",             # 이미 표준
    
    # 중국 도시들  
    "베이징": "베이징",          # 이미 표준
    "북경": "베이징",           # 북경 → 베이징
    "상하이": "상하이",          # 이미 표준
    "상해": "상하이",           # 상해 → 상하이
    "광저우": "광저우",          # 이미 표준
    "광주": "광저우",           # 광주(중국) → 광저우
    "선전": "선전",             # 이미 표준
    "심천": "선전",             # 심천 → 선전
    "청두": "청두",             # 이미 표준
    "성도": "청두",             # 성도 → 청두
    
    # 한국 도시들
    "서울": "서울",             # 이미 표준
    "seoul": "서울",            # 영문 → 한글
    "부산": "부산",             # 이미 표준
    "busan": "부산",            # 영문 → 한글
    "제주": "제주",             # 이미 표준
    "제주도": "제주",           # 제주도 → 제주
    "jeju": "제주",             # 영문 → 한글
    "인천": "인천",             # 이미 표준
    "대구": "대구",             # 이미 표준
    "대전": "대전",             # 이미 표준
    "광주": "광주",             # 한국 광주 (중국 광저우와 구별)
    "울산": "울산",             # 이미 표준
    
    # 기타 아시아 도시들
    "타이페이": "타이페이",        # 이미 표준
    "대만": "타이페이",          # 대만 → 타이페이 (대표 도시)
    "타이완": "타이페이",        # 타이완 → 타이페이
    "방콕": "방콕",             # 이미 표준
    "bangkok": "방콕",          # 영문 → 한글
    "싱가포르": "싱가포르",        # 이미 표준
    "singapore": "싱가포르",     # 영문 → 한글
    "싱가폴": "싱가포르",        # 싱가폴 → 싱가포르
    "쿠알라룸푸르": "쿠알라룸푸르", # 이미 표준
    "kl": "쿠알라룸푸르",        # KL → 쿠알라룸푸르
    "마닐라": "마닐라",          # 이미 표준
    "manila": "마닐라",         # 영문 → 한글
    "세부": "세부",             # 이미 표준
    "cebu": "세부",             # 영문 → 한글
    
    # 유럽 도시들
    "파리": "파리",             # 이미 표준
    "paris": "파리",            # 영문 → 한글
    "런던": "런던",             # 이미 표준
    "london": "런던",           # 영문 → 한글
    "로마": "로마",             # 이미 표준
    "rome": "로마",             # 영문 → 한글
    "로마": "로마",             # 이미 표준
    "바르셀로나": "바르셀로나",    # 이미 표준
    "barcelona": "바르셀로나",   # 영문 → 한글
    "마드리드": "마드리드",       # 이미 표준
    "madrid": "마드리드",       # 영문 → 한글
    "베를린": "베를린",          # 이미 표준
    "berlin": "베를린",         # 영문 → 한글
    "뮌헨": "뮌헨",             # 이미 표준
    "munich": "뮌헨",           # 영문 → 한글
    "뮈헨": "뮌헨",             # 뮈헨 → 뮌헨
    "프라하": "프라하",          # 이미 표준
    "prague": "프라하",         # 영문 → 한글
    "비엔나": "비엔나",          # 이미 표준
    "vienna": "비엔나",         # 영문 → 한글
    "부다페스트": "부다페스트",    # 이미 표준
    "budapest": "부다페스트",   # 영문 → 한글
    "암스테르담": "암스테르담",    # 이미 표준
    "amsterdam": "암스테르담",  # 영문 → 한글
    
    # 미국 도시들
    "뉴욕": "뉴욕",             # 이미 표준
    "new york": "뉴욕",         # 영문 → 한글
    "nyc": "뉴욕",              # NYC → 뉴욕
    "로스앤젤레스": "로스앤젤레스", # 이미 표준
    "la": "로스앤젤레스",        # LA → 로스앤젤레스
    "los angeles": "로스앤젤레스", # 영문 → 한글
    "라스베이거스": "라스베이거스", # 이미 표준
    "las vegas": "라스베이거스",  # 영문 → 한글
    "샌프란시스코": "샌프란시스코", # 이미 표준
    "san francisco": "샌프란시스코", # 영문 → 한글
    "sf": "샌프란시스코",        # SF → 샌프란시스코
    "시애틀": "시애틀",          # 이미 표준
    "seattle": "시애틀",        # 영문 → 한글
    "마이애미": "마이애미",       # 이미 표준
    "miami": "마이애미",        # 영문 → 한글
    
    # 호주/뉴질랜드
    "시드니": "시드니",          # 이미 표준
    "sydney": "시드니",         # 영문 → 한글
    "멜버른": "멜버른",          # 이미 표준
    "melbourne": "멜버른",      # 영문 → 한글
    "멜본": "멜버른",           # 멜본 → 멜버른
    "골드코스트": "골드코스트",    # 이미 표준
    "gold coast": "골드코스트",  # 영문 → 한글
    "오클랜드": "오클랜드",       # 이미 표준
    "auckland": "오클랜드",     # 영문 → 한글
}

# 역방향 검색을 위한 표준 도시명 목록 (config.py의 UNIFIED_CITY_INFO와 연동)
STANDARD_CITIES = set(CITY_ALIASES.values())

def normalize_city_name(input_city):
    """
    입력된 도시명을 표준 도시명으로 변환
    
    Args:
        input_city (str): 사용자가 입력한 도시명
        
    Returns:
        str: 표준화된 도시명
    """
    if not input_city:
        return input_city
    
    # 공백 제거 및 소문자 변환
    normalized_input = input_city.strip()
    
    # 1. 직접 매칭 (대소문자 구분 없이)
    for alias, standard in CITY_ALIASES.items():
        if normalized_input.lower() == alias.lower():
            print(f"🔄 도시명 변환: '{input_city}' → '{standard}'")
            return standard
    
    # 2. 이미 표준 도시명인 경우
    if normalized_input in STANDARD_CITIES:
        print(f"✅ 표준 도시명: '{input_city}'")
        return normalized_input
    
    # 3. 부분 매칭 (비슷한 이름 찾기)
    similar_cities = []
    for alias in CITY_ALIASES.keys():
        if normalized_input.lower() in alias.lower() or alias.lower() in normalized_input.lower():
            similar_cities.append((alias, CITY_ALIASES[alias]))
    
    if similar_cities:
        # 가장 유사한 도시명 선택 (길이가 가장 비슷한 것)
        best_match = min(similar_cities, key=lambda x: abs(len(x[0]) - len(normalized_input)))
        print(f"🔍 유사 매칭: '{input_city}' → '{best_match[1]}' ('{best_match[0]}'와 유사)")
        return best_match[1]
    
    # 4. 매칭되지 않은 경우 원본 반환
    print(f"⚠️ 도시명 매칭 실패: '{input_city}' (원본 그대로 사용)")
    return normalized_input

def get_city_aliases(standard_city):
    """
    표준 도시명에 대한 모든 별칭 조회
    
    Args:
        standard_city (str): 표준 도시명
        
    Returns:
        list: 해당 도시의 모든 별칭 목록
    """
    aliases = []
    for alias, standard in CITY_ALIASES.items():
        if standard == standard_city:
            aliases.append(alias)
    
    return aliases

def search_city_suggestions(partial_name):
    """
    부분 도시명으로 관련 도시 제안
    
    Args:
        partial_name (str): 부분 도시명
        
    Returns:
        list: 관련 도시 목록 (표준명, 별칭) 튜플
    """
    suggestions = []
    partial_lower = partial_name.lower()
    
    for alias, standard in CITY_ALIASES.items():
        if partial_lower in alias.lower() or partial_lower in standard.lower():
            suggestions.append((standard, alias))
    
    # 중복 제거 및 정렬
    unique_suggestions = list(set(suggestions))
    unique_suggestions.sort(key=lambda x: x[0])
    
    return unique_suggestions

def validate_city_with_config(city_name):
    """
    config.py의 UNIFIED_CITY_INFO와 연동하여 도시명 검증
    
    Args:
        city_name (str): 검증할 도시명
        
    Returns:
        tuple: (is_valid, standard_name, city_info)
    """
    try:
        from .config import UNIFIED_CITY_INFO
        
        # 1. 별칭 시스템으로 표준화
        standard_name = normalize_city_name(city_name)
        
        # 2. UNIFIED_CITY_INFO에서 확인
        if standard_name in UNIFIED_CITY_INFO:
            city_info = UNIFIED_CITY_INFO[standard_name]
            print(f"✅ 도시 검증 성공: '{city_name}' → '{standard_name}' ({city_info['국가']})")
            return True, standard_name, city_info
        else:
            print(f"❌ 도시 검증 실패: '{standard_name}'가 UNIFIED_CITY_INFO에 없음")
            
            # 유사한 도시 제안
            suggestions = search_city_suggestions(standard_name)
            if suggestions:
                print(f"💡 유사한 도시들: {[s[0] for s in suggestions[:3]]}")
            
            return False, standard_name, None
            
    except ImportError:
        print("⚠️ config.py를 import할 수 없습니다.")
        return False, city_name, None

# 사용하기 쉬운 래퍼 함수들
def smart_city_search(user_input):
    """스마트 도시 검색 - 사용자 입력을 받아서 최적의 도시명 반환"""
    is_valid, standard_name, city_info = validate_city_with_config(user_input)
    
    if is_valid:
        return {
            'success': True,
            'original': user_input,
            'standard': standard_name,
            'info': city_info,
            'aliases': get_city_aliases(standard_name)
        }
    else:
        suggestions = search_city_suggestions(user_input)
        return {
            'success': False,
            'original': user_input,
            'standard': standard_name,
            'info': None,
            'suggestions': suggestions
        }

def get_search_variations(city_name):
    """크롤링 시 시도할 수 있는 모든 도시명 변형 반환"""
    standard_name = normalize_city_name(city_name)
    variations = [standard_name]
    
    # 별칭들 추가
    aliases = get_city_aliases(standard_name)
    variations.extend(aliases)
    
    # 영문명 추가 (config에서 가져오기)
    try:
        from .config import UNIFIED_CITY_INFO
        if standard_name in UNIFIED_CITY_INFO:
            english_name = UNIFIED_CITY_INFO[standard_name].get('영문명', '')
            if english_name and english_name not in variations:
                variations.append(english_name)
    except:
        pass
    
    # 중복 제거
    return list(set(variations))

# 테스트 함수
def test_city_aliases():
    """도시명 별칭 시스템 테스트"""
    test_cases = [
        "쿠마모토",     # → 구마모토
        "구마모토",     # → 구마모토 (그대로)
        "토쿄",        # → 도쿄
        "도쿄",        # → 도쿄 (그대로)
        "북경",        # → 베이징
        "상해",        # → 상하이
        "심천",        # → 선전
        "제주도",       # → 제주
        "대만",        # → 타이페이
        "KL",          # → 쿠알라룸푸르
        "NYC",         # → 뉴욕
        "LA",          # → 로스앤젤레스
        "paris",       # → 파리
        "tokyo",       # → 도쿄 (실패 예상)
        "존재하지않는도시", # → 원본 그대로
    ]
    
    print("🧪 도시명 별칭 시스템 테스트")
    print("=" * 40)
    
    for test_city in test_cases:
        print(f"\n🔍 테스트: '{test_city}'")
        result = smart_city_search(test_city)
        
        if result['success']:
            print(f"   ✅ 성공: {result['standard']} ({result['info']['국가']})")
            if result['aliases']:
                print(f"   🔄 별칭: {result['aliases']}")
        else:
            print(f"   ❌ 실패: {result['standard']}")
            if result['suggestions']:
                print(f"   💡 제안: {[s[0] for s in result['suggestions'][:3]]}")

if __name__ == "__main__":
    test_city_aliases()

print("✅ 도시명 별칭 시스템 로드 완료!")
print("🚀 사용법: smart_city_search('쿠마모토') 또는 normalize_city_name('쿠마모토')")