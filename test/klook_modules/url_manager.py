"""
🚀 그룹 3: KLOOK 전용 URL 패턴 + hashlib 통합 간소화된 상태 관리 시스템
- KLOOK /activity/ 패턴 완전 변경
- hashlib 최적화 활성화
- URL 중복 방지 및 상태 관리
"""

import os
import re
import hashlib
import json
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# config 모듈에서 필요한 함수들 import
from .config import CONFIG, get_city_code, is_url_processed_fast, mark_url_processed_fast

# =============================================================================
# 🔗 KLOOK URL 패턴 및 검증 시스템
# =============================================================================

def is_valid_klook_url(url):
    """✅ KLOOK URL 유효성 검사 (activity 패턴)"""
    if not url or not isinstance(url, str):
        return False
    
    # KLOOK 도메인 체크
    klook_domains = [
        'klook.com',
        'www.klook.com', 
        'm.klook.com'
    ]
    
    parsed = urlparse(url)
    domain_valid = any(domain in parsed.netloc.lower() for domain in klook_domains)
    
    if not domain_valid:
        return False
    
    # /activity/ 패턴 체크 (KLOOK 표준)
    activity_patterns = [
        r'/activity/\d+',           # /activity/123456
        r'/ko/activity/\d+',        # /ko/activity/123456  
        r'/en/activity/\d+',        # /en/activity/123456
        r'/activity/[^/]+',         # /activity/slug-name
    ]
    
    path_valid = any(re.search(pattern, url) for pattern in activity_patterns)
    
    # 제외할 패턴들
    excluded_patterns = [
        r'/search',
        r'/category',
        r'/city',
        r'/user',
        r'/account',
        r'/cart',
        r'/checkout'
    ]
    
    excluded = any(re.search(pattern, url) for pattern in excluded_patterns)
    
    return path_valid and not excluded

def extract_klook_activity_id(url):
    """KLOOK activity ID 추출"""
    if not url:
        return None
    
    # /activity/숫자 패턴에서 ID 추출
    id_patterns = [
        r'/activity/(\d+)',
        r'/ko/activity/(\d+)', 
        r'/en/activity/(\d+)'
    ]
    
    for pattern in id_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def normalize_klook_url(url):
    """✅ KLOOK URL 정규화 (중복 방지용)"""
    if not url:
        return url
    
    try:
        parsed = urlparse(url)
        
        # 기본 정규화
        normalized_url = f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path}"
        
        # 쿼리 파라미터 정리 (필수만 유지)
        if parsed.query:
            query_params = parse_qs(parsed.query)
            essential_params = {}
            
            # KLOOK에서 필수적인 파라미터들만 유지
            essential_keys = ['currency', 'locale', 'aid']  # 필요시 추가
            
            for key in essential_keys:
                if key in query_params:
                    essential_params[key] = query_params[key]
            
            if essential_params:
                query_string = urlencode(essential_params, doseq=True)
                normalized_url += f"?{query_string}"
        
        return normalized_url
        
    except Exception as e:
        print(f"⚠️ URL 정규화 실패: {e}")
        return url

# =============================================================================
# 📊 URL 상태 관리 시스템 (hashlib 통합)
# =============================================================================

def is_url_already_processed(url, city_name):
    """✅ URL 중복 체크 (hashlib 초고속 + CSV 호환성)"""
    if not url:
        return True  # 빈 URL은 처리된 것으로 간주
    
    # 1. URL 정규화
    normalized_url = normalize_klook_url(url)
    
    # 2. hashlib 초고속 체크 (0.001초)
    if CONFIG.get("USE_HASH_SYSTEM", True):
        if is_url_processed_fast(normalized_url, city_name):
            return True
    
    # 3. 기존 CSV 호환성 체크 (필요시에만)
    if CONFIG.get("KEEP_CSV_SYSTEM", True):
        try:
            from .config import get_completed_urls_from_csv
            completed_urls = get_completed_urls_from_csv(city_name)
            if normalized_url in completed_urls:
                # CSV에는 있지만 해시에 없으면 해시에도 추가
                if CONFIG.get("USE_HASH_SYSTEM", True):
                    mark_url_processed_fast(normalized_url, city_name, "csv_sync")
                return True
        except Exception as e:
            print(f"⚠️ CSV 호환성 체크 실패: {e}")
    
    return False

def mark_url_as_processed(url, city_name, product_number=None, rank=None):
    """✅ URL을 처리 완료로 표시 (hashlib + V2 3-tier + 순위 정보)"""
    if not url:
        return False
    
    normalized_url = normalize_klook_url(url)
    
    try:
        # 1. hashlib 시스템에 기록 (초고속) - 순위 정보 포함
        if CONFIG.get("USE_HASH_SYSTEM", True):
            mark_url_processed_fast(normalized_url, city_name, product_number, rank)
        
        # 2. V2 3-tier 시스템에 기록
        if CONFIG.get("USE_V2_URL_SYSTEM", True):
            from .config import save_url_to_log
            save_url_to_log(city_name, normalized_url)
        
        return True
        
    except Exception as e:
        print(f"❌ URL 처리 완료 표시 실패: {e}")
        return False

def get_unprocessed_urls(url_list, city_name):
    """미처리 URL만 필터링"""
    if not url_list:
        return []
    
    unprocessed = []
    total_count = len(url_list)
    processed_count = 0
    
    print(f"🔍 {total_count}개 URL 중복 검사 중...")
    
    for url in url_list:
        if is_valid_klook_url(url):
            if not is_url_already_processed(url, city_name):
                unprocessed.append(url)
            else:
                processed_count += 1
    
    print(f"   📊 결과: 미처리 {len(unprocessed)}개, 중복 제외 {processed_count}개")
    return unprocessed

# =============================================================================
# 📂 URL 수집 및 저장 시스템
# =============================================================================

def save_urls_to_collection(urls, city_name, source="manual"):
    """URL을 수집 폴더에 저장 (V2 3-tier 시스템)"""
    if not urls:
        return False
    
    try:
        # V2 수집 폴더에 저장
        collection_dir = CONFIG.get("V2_URL_COLLECTED", "url_collected")
        os.makedirs(collection_dir, exist_ok=True)
        
        city_code = get_city_code(city_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{city_code}_{source}_{timestamp}.json"
        filepath = os.path.join(collection_dir, filename)
        
        # JSON 형태로 저장 (메타데이터 포함)
        data = {
            "city_name": city_name,
            "city_code": city_code,
            "source": source,
            "collected_at": datetime.now().isoformat(),
            "total_urls": len(urls),
            "urls": urls
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 URL 수집 저장 완료: {filename} ({len(urls)}개)")
        return True
        
    except Exception as e:
        print(f"❌ URL 수집 저장 실패: {e}")
        return False

def load_urls_from_collection(city_name, source_filter=None):
    """수집 폴더에서 URL 로드"""
    try:
        collection_dir = CONFIG.get("V2_URL_COLLECTED", "url_collected")
        if not os.path.exists(collection_dir):
            return []
        
        city_code = get_city_code(city_name)
        all_urls = []
        
        # 해당 도시의 모든 수집 파일 찾기
        for filename in os.listdir(collection_dir):
            if filename.startswith(city_code) and filename.endswith('.json'):
                if source_filter and source_filter not in filename:
                    continue
                
                filepath = os.path.join(collection_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'urls' in data:
                            all_urls.extend(data['urls'])
                except Exception as e:
                    print(f"⚠️ 파일 로드 실패: {filename} - {e}")
        
        # 중복 제거
        unique_urls = list(set(all_urls))
        print(f"📂 수집된 URL 로드: {len(unique_urls)}개 (중복 제거 후)")
        return unique_urls
        
    except Exception as e:
        print(f"❌ URL 수집 로드 실패: {e}")
        return []

# =============================================================================
# 🔗 URL 분석 및 통계
# =============================================================================

def analyze_url_patterns(urls):
    """URL 패턴 분석"""
    if not urls:
        return {}
    
    analysis = {
        "total_urls": len(urls),
        "valid_klook_urls": 0,
        "activity_ids": [],
        "domains": {},
        "languages": {"ko": 0, "en": 0, "other": 0},
        "patterns": {}
    }
    
    for url in urls:
        if is_valid_klook_url(url):
            analysis["valid_klook_urls"] += 1
            
            # Activity ID 추출
            activity_id = extract_klook_activity_id(url)
            if activity_id:
                analysis["activity_ids"].append(activity_id)
            
            # 도메인 분석
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            analysis["domains"][domain] = analysis["domains"].get(domain, 0) + 1
            
            # 언어 분석
            if '/ko/' in url:
                analysis["languages"]["ko"] += 1
            elif '/en/' in url:
                analysis["languages"]["en"] += 1
            else:
                analysis["languages"]["other"] += 1
    
    # 고유 Activity ID 수
    analysis["unique_activities"] = len(set(analysis["activity_ids"]))
    
    return analysis

def get_url_collection_stats(city_name):
    """URL 수집 통계"""
    try:
        collection_dir = CONFIG.get("V2_URL_COLLECTED", "url_collected")
        if not os.path.exists(collection_dir):
            return {"total_files": 0, "total_urls": 0}
        
        city_code = get_city_code(city_name)
        stats = {
            "total_files": 0,
            "total_urls": 0,
            "sources": {},
            "latest_collection": None
        }
        
        latest_time = 0
        
        for filename in os.listdir(collection_dir):
            if filename.startswith(city_code) and filename.endswith('.json'):
                stats["total_files"] += 1
                
                filepath = os.path.join(collection_dir, filename)
                try:
                    # 파일 정보
                    file_time = os.path.getmtime(filepath)
                    if file_time > latest_time:
                        latest_time = file_time
                        stats["latest_collection"] = datetime.fromtimestamp(file_time).strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 내용 분석
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        url_count = data.get('total_urls', 0)
                        source = data.get('source', 'unknown')
                        
                        stats["total_urls"] += url_count
                        stats["sources"][source] = stats["sources"].get(source, 0) + url_count
                        
                except Exception as e:
                    print(f"⚠️ 통계 수집 실패: {filename} - {e}")
        
        return stats
        
    except Exception as e:
        print(f"❌ URL 수집 통계 실패: {e}")
        return {"error": str(e)}

print("✅ 그룹 3 완료: KLOOK 전용 URL 패턴 + hashlib 통합 간소화된 상태 관리 시스템!")
print("🚀 hashlib 최적화: 활성화")
print("🧹 KLOOK /activity/ 패턴으로 완전 변경 완료")
print("   🔗 URL 검증:")
print("   - is_valid_klook_url(): KLOOK activity URL 검증")
print("   - normalize_klook_url(): URL 정규화")
print("   📊 상태 관리:")
print("   - is_url_already_processed(): hashlib 초고속 중복 체크")
print("   - mark_url_as_processed(): 처리 완료 표시")
print("   📂 수집 시스템:")
print("   - save_urls_to_collection(): V2 3-tier 수집 저장")
print("   - load_urls_from_collection(): 수집 URL 로드")
print("   📈 분석 도구:")
print("   - analyze_url_patterns(): URL 패턴 분석")
print("   - get_url_collection_stats(): 수집 통계")