"""
파일 처리 및 데이터 저장 시스템
- CSV 파일 생성 및 저장
- 이미지 다운로드 및 저장
- 데이터 구조 관리
"""

import os
import csv
import requests
import hashlib
from datetime import datetime
from urllib.parse import urlparse

from ..config import CONFIG, get_city_info, get_city_code, SELENIUM_AVAILABLE

if SELENIUM_AVAILABLE:
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException

# =============================================================================
# 기본 데이터 구조 생성
# =============================================================================

def create_product_data_structure(city_name, product_number, rank=None):
    """기본 상품 데이터 구조 생성"""
    
    # 도시 정보 가져오기
    continent, country = get_city_info(city_name)
    city_code = get_city_code(city_name)
    
    # 기본 데이터 구조
    base_data = {
        # 기본 정보
        "번호": product_number,
        "도시ID": city_code,
        "도시명": city_name,
        "대륙": continent,
        "국가": country,
        "순위": rank or product_number,
        "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        
        # 상품 정보 (parsers.py에서 채워짐)
        "상품명": "",
        "가격": "",
        "통화": "KRW",
        "평점": "",
        "리뷰수": "",
        "카테고리": "",
        "하이라이트": "",              # 🆕 원본 기능 추가
        "특징": "",
        "언어": "",                  # 🆕 원본 기능 추가
        "태그": "",
        "설명": "",
        "URL": "",
        "상품번호": "",
        
        # 이미지 정보
        "메인이미지": "",
        "썸네일이미지": "",
        
        # 위치 정보
        "주소": "",
        "위도": "",
        "경도": "",
        
        # 추가 정보
        "예약가능여부": "",
        "취소정책": "",
        "언어": "",
        "소요시간": "",
        "포함사항": "",
        "제외사항": "",
        "주의사항": "",
        
        # 메타데이터
        "데이터소스": "KLOOK",
        "크롤링버전": "v2.0",
        "해시값": ""
    }
    
    return base_data

# =============================================================================
# CSV 파일 관리
# =============================================================================

def ensure_directory_structure(city_name):
    """디렉토리 구조 생성"""
    try:
        continent, country = get_city_info(city_name)
        
        # CSV 저장 경로 결정
        if city_name in ["마카오", "홍콩", "싱가포르"]:
            csv_dir = os.path.join("data", continent)
        else:
            csv_dir = os.path.join("data", continent, country, city_name)
        
        # 디렉토리 생성
        os.makedirs(csv_dir, exist_ok=True)
        
        # 이미지 디렉토리 생성
        img_dir = os.path.join("klook_img", city_name)
        os.makedirs(img_dir, exist_ok=True)
        
        return True
        
    except Exception as e:
        print(f"⚠️ 디렉토리 생성 실패: {e}")
        return False

def is_duplicate_hash(city_name, new_hash):
    """기존 CSV에서 해시 중복 체크 (csv 모듈만 사용)"""
    try:
        continent, country = get_city_info(city_name)
        
        # CSV 파일 경로 결정 (범용적으로 수정)
        if city_name == country:
            # 도시국가: 대륙 직하에 저장
            csv_path = os.path.join("data", continent, f"klook_{city_name}_products.csv")
        else:
            # 일반 도시: 대륙/국가/도시 구조
            csv_path = os.path.join("data", continent, country, city_name, f"klook_{city_name}_products.csv")
        
        if not os.path.exists(csv_path):
            return False
        
        # CSV 파일에서 해시값 체크
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('해시값') == new_hash:
                    return True
        return False
        
    except Exception as e:
        print(f"⚠️ 해시 중복 체크 실패: {e}")
        return False

def save_to_csv_klook(product_data, city_name):
    """KLOOK 상품 데이터를 CSV로 저장 (범용 대륙 지원)"""
    try:
        continent, country = get_city_info(city_name)
        
        # CSV 파일 경로 결정 (범용적으로 수정)
        if city_name == country:
            # 도시국가: 대륙 직하에 저장
            csv_path = os.path.join("data", continent, f"klook_{city_name}_products.csv")
        else:
            # 일반 도시: 대륙/국가/도시 구조
            csv_path = os.path.join("data", continent, country, city_name, f"klook_{city_name}_products.csv")
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        # 🚀 해시값 생성 및 중복 체크 (번호 할당 전에 수행)
        hash_string = f"{product_data.get('상품명', '')}{product_data.get('가격', '')}{product_data.get('URL', '')}"
        new_hash = hashlib.md5(hash_string.encode()).hexdigest()[:12]
        
        if is_duplicate_hash(city_name, new_hash):
            print(f"   ⏭️ 중복 상품 스킵 (해시: {new_hash})")
            return False
        
        # 중복이 아닌 경우에만 번호 할당
        if '번호' not in product_data or not product_data.get('번호'):
            next_number = get_next_product_number(city_name)
            product_data['번호'] = str(next_number)
            print(f"  🔢 번호 할당: {next_number}")
        
        product_data['해시값'] = new_hash
        
        # CSV 파일 존재 여부 확인
        file_exists = os.path.exists(csv_path)
        
        # CSV 저장
        with open(csv_path, 'a', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=product_data.keys())
            
            # 헤더 쓰기 (파일이 새로 생성된 경우)
            if not file_exists:
                writer.writeheader()
            
            # 데이터 쓰기
            writer.writerow(product_data)
        
        return True
        
    except Exception as e:
        print(f"⚠️ CSV 저장 실패: {e}")
        return False

def get_csv_stats(city_name):
    """CSV 파일 통계 정보 반환 (범용 대륙 지원)"""
    try:
        continent, country = get_city_info(city_name)
        
        # CSV 파일 경로 결정 (범용적으로 수정)
        if city_name == country:
            # 도시국가: 대륙 직하에 저장
            csv_path = os.path.join("data", continent, f"klook_{city_name}_products.csv")
        else:
            # 일반 도시: 대륙/국가/도시 구조
            csv_path = os.path.join("data", continent, country, city_name, f"klook_{city_name}_products.csv")
        
        if not os.path.exists(csv_path):
            return {"error": "CSV 파일을 찾을 수 없습니다"}
        
        # 파일 통계 수집
        file_size = os.path.getsize(csv_path)
        
        # 행 수 및 해시 통계 세기
        unique_hashes = set()
        row_count = 0
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_count += 1
                hash_value = row.get('해시값')
                if hash_value:
                    unique_hashes.add(hash_value)
        
        return {
            "total_products": row_count,
            "unique_hashes": len(unique_hashes),
            "file_size": file_size,
            "file_path": csv_path
        }
        
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# 이미지 처리 시스템
# =============================================================================

def get_dual_image_urls_klook(driver, url_type="Product"):
    """KLOOK에서 메인 이미지와 썸네일 이미지 URL 추출 (원본 정교한 셀렉터 사용)"""
    if not SELENIUM_AVAILABLE:
        return None, None
    
    main_img_url = None
    thumb_img_url = None
    
    # 원본에서 실제 작동하는 정교한 메인 이미지 셀렉터들
    main_selectors = [
        "#banner_atlas .activity-banner-image-container_left img",   # KLOOK 메인 이미지 (실제 작동)
        ".activity-banner-image-container_left img",                 # 백업 1
        ".main-image img",                                           # 일반 백업
        ".hero-image img",                                           # 일반 백업
        ".product-image img",                                        # 일반 백업
        ".ActivityCardImage--image",                                 # 기존 셀렉터 (백업)
        ".product-hero-image img",                                   # 상세 페이지 메인 (백업)
    ]
    
    # 원본에서 실제 작동하는 정교한 썸네일 이미지 셀렉터들
    thumb_selectors = [
        "#banner_atlas .activity-banner-image-container_right img",  # KLOOK 썸네일 이미지
        ".activity-banner-image-container_right img",                # 백업 1
        ".product-gallery img:nth-child(2)",                        # 일반 백업
        ".gallery img:nth-child(2)",                                # 일반 백업
        ".slider img:nth-child(2)",                                 # 일반 백업
        ".Gallery-module--thumbnails img",                          # 갤러리 썸네일 (새 구조)
        ".gallery-thumbnails img",                                  # 갤러리 썸네일
        "[data-testid='gallery-thumbnail'] img",                   # 테스트ID 기반
        ".thumbnail img",                                           # 일반 썸네일
        ".swiper-slide img",                                        # 스와이퍼 슬라이드 내 이미지
        ".image-gallery-thumbnails img",                            # 이미지 갤러리 썸네일
        ".product-gallery-thumb img",                               # 상품 갤러리 썸네일
        ".slider-thumb img",                                        # 슬라이더 썸네일
    ]
    
    def try_get_image_url(selectors):
        for selector in selectors:
            try:
                img_element = driver.find_element(By.CSS_SELECTOR, selector)
                img_url = img_element.get_attribute("src")
                if img_url and img_url.startswith("http"):
                    return img_url
            except NoSuchElementException:
                continue
        return None
    
    try:
        # 메인 이미지 추출
        main_img_url = try_get_image_url(main_selectors)
        
        # 썸네일 이미지 추출
        thumb_img_url = try_get_image_url(thumb_selectors)
        
        # 썸네일이 없으면 메인 이미지 사용
        if not thumb_img_url and main_img_url:
            thumb_img_url = main_img_url
        
    except Exception as e:
        print(f"      ⚠️ 이미지 URL 추출 실패: {e}")
    
    return main_img_url, thumb_img_url

def download_single_image_klook(img_src, product_number, city_name, image_type="main", max_size_kb=300):
    """단일 이미지 다운로드 (메인/썸네일 구분) - 원본 코드 기반"""
    if not CONFIG["SAVE_IMAGES"]:
        return None
    
    try:
        import requests
        from PIL import Image
    except ImportError:
        print("      ⚠️ 필요한 라이브러리가 설치되지 않아 이미지 다운로드를 건너뜁니다.")
        return None
    
    try:
        # 파일명 생성 - 원본 코드와 동일
        city_code = get_city_code(city_name)
        if image_type == "main":
            img_filename = f"{city_code}_{product_number:04d}.jpg"  # KMJ_0001.jpg
        else:
            img_filename = f"{city_code}_{product_number:04d}_thumb.jpg"  # KMJ_0001_thumb.jpg
        
        # 이미지 폴더 경로 - 원본 코드와 동일
        continent, country = get_city_info(city_name)
        img_base_folder = os.path.join(os.getcwd(), "klook_img")
        
        # 폴더 구조 (범용적으로 수정)
        continent, country = get_city_info(city_name)
        if city_name == country:
            # 도시국가: 대륙 직하에 저장
            img_folder = os.path.join(img_base_folder, continent)
        else:
            # 일반 도시: 대륙/국가/도시 구조
            img_folder = os.path.join(img_base_folder, continent, country, city_name)
        
        os.makedirs(img_folder, exist_ok=True)
        img_path = os.path.join(img_folder, img_filename)
        
        # 이미지 다운로드
        headers = {
            'User-Agent': CONFIG.get("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
            'Referer': 'https://www.klook.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
        }
        
        response = requests.get(img_src, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 임시 파일에 저장
        temp_path = img_path + ".temp"
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        # 이미지 리사이즈 및 최적화
        with Image.open(temp_path) as img:
            # RGB로 변환 (JPEG 호환성)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # 타입별 크기 조정
            width, height = img.size
            if image_type == "main":
                target_width = 400  # 메인 이미지
            else:
                target_width = 200  # 썸네일 이미지
            
            if width > target_width:
                ratio = target_width / width
                new_height = int(height * ratio)
                img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
            
            # 품질 조정하여 저장
            quality = 85
            while quality > 30:
                img.save(img_path, "JPEG", quality=quality, optimize=True)
                
                # 파일 크기 확인
                if os.path.getsize(img_path) <= max_size_kb * 1024:
                    break
                quality -= 10
        
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        file_size_kb = os.path.getsize(img_path) / 1024
        print(f"      ✅ {image_type} 이미지 저장: {img_filename} ({file_size_kb:.1f}KB)")
        return img_filename
        
    except Exception as e:
        print(f"      ❌ {image_type} 이미지 저장 실패: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return None

def download_dual_images_klook(image_urls, product_number, city_name, max_size_kb=300):
    """듀얼 이미지 다운로드 (메인 + 썸네일) - 원본 코드 기반"""
    if not CONFIG["SAVE_IMAGES"]:
        return {"main": None, "thumb": None}
    
    results = {"main": None, "thumb": None}
    
    # 메인 이미지 다운로드
    if image_urls.get("main"):
        print(f"    📥 메인 이미지 다운로드 중...")
        main_filename = download_single_image_klook(
            image_urls["main"], 
            product_number, 
            city_name, 
            image_type="main",
            max_size_kb=max_size_kb
        )
        results["main"] = main_filename
    
    # 썸네일 이미지 다운로드 (선택사항)
    if image_urls.get("thumb"):
        print(f"    📥 썸네일 이미지 다운로드 중...")
        thumb_filename = download_single_image_klook(
            image_urls["thumb"], 
            product_number, 
            city_name, 
            image_type="thumb",
            max_size_kb=max_size_kb//2  # 썸네일은 더 작게
        )
        results["thumb"] = thumb_filename
    
    # 결과 로그
    if results["main"] and results["thumb"]:
        print(f"    ✅ 듀얼 이미지 저장 완료: 메인 + 썸네일")
    elif results["main"]:
        print(f"    ✅ 메인 이미지만 저장 완료 (썸네일 없음)")
    else:
        print(f"    ❌ 이미지 저장 실패")
    
    return results

def download_and_save_image_klook(image_url, product_number, city_name, image_type="main", max_size_kb=300):
    """하위 호환성을 위한 래퍼 함수"""
    return download_single_image_klook(image_url, product_number, city_name, image_type, max_size_kb)

def get_image_stats(city_name):
    """이미지 저장 통계"""
    try:
        img_dir = os.path.join("klook_img", city_name)
        
        if not os.path.exists(img_dir):
            return {"total_images": 0, "total_size": 0}
        
        total_images = 0
        total_size = 0
        
        for filename in os.listdir(img_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                filepath = os.path.join(img_dir, filename)
                total_images += 1
                total_size += os.path.getsize(filepath)
        
        return {
            "total_images": total_images,
            "total_size": total_size,
            "directory": img_dir
        }
        
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# 데이터 검증 시스템
# =============================================================================

def validate_product_data(product_data):
    """상품 데이터 유효성 검증"""
    required_fields = ["상품명", "URL"]
    
    for field in required_fields:
        if not product_data.get(field):
            return False
    
    return True

def clean_text_data(text):
    """텍스트 데이터 정리"""
    if not text:
        return ""
    
    # 공백 정리
    cleaned = " ".join(text.split())
    
    # 특수문자 정리
    cleaned = cleaned.replace('"', '""')  # CSV 호환
    
    return cleaned.strip()

def format_price_data(price_text):
    """가격 데이터 포맷팅"""
    if not price_text:
        return ""
    
    # 숫자만 추출
    import re
    numbers = re.findall(r'\d+', str(price_text).replace(',', ''))
    
    if numbers:
        return numbers[0]
    
    return price_text.strip()

# =============================================================================
# CSV 번호 연속성 관리 시스템
# =============================================================================

def get_last_product_number(city_name):
    """기존 CSV에서 마지막 상품 번호 확인 (범용 대륙 지원)"""
    try:
        continent, country = get_city_info(city_name)
        
        # CSV 파일 경로 결정 (범용적으로 수정)
        if city_name == country:
            # 도시국가: 대륙 직하에 저장
            csv_path = os.path.join("data", continent, f"klook_{city_name}_products.csv")
        else:
            # 일반 도시: 대륙/국가/도시 구조
            csv_path = os.path.join("data", continent, country, city_name, f"klook_{city_name}_products.csv")
        
        if not os.path.exists(csv_path):
            return 0
        
        max_number = 0
        import csv
        import re
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                number_value = None
                
                # 1. '번호' 컬럼에서 숫자 추출
                if '번호' in row and row['번호']:
                    if row['번호'].isdigit():
                        number_value = int(row['번호'])
                    else:
                        # "page1_1", "KMJ_0001" 등에서 숫자 추출
                        numbers = re.findall(r'(\d+)', str(row['번호']))
                        if numbers:
                            number_value = int(numbers[-1])
                
                # 2. 다른 번호 관련 컬럼 확인
                for col in ['product_number', '상품번호', 'number']:
                    if col in row and row[col] and str(row[col]).isdigit():
                        number_value = int(row[col])
                        break
                
                # 3. 이미지 파일명에서 번호 추출 (KMJ_0001.jpg → 1)
                if not number_value:
                    for img_col in ['메인이미지_파일명', '썸네일이미지_파일명']:
                        if img_col in row and row[img_col]:
                            img_numbers = re.findall(r'_(\d+)\.', row[img_col])
                            if img_numbers:
                                number_value = int(img_numbers[0])
                                break
                
                if number_value:
                    max_number = max(max_number, number_value)
        
        return max_number
        
    except Exception as e:
        print(f"⚠️ 번호 확인 실패: {e}")
        return 0

def get_next_product_number(city_name):
    """다음 상품 번호 반환"""
    last_number = get_last_product_number(city_name)
    return last_number + 1

def ensure_csv_number_continuity(city_name):
    """CSV 번호 연속성 보장"""
    try:
        last_num = get_last_product_number(city_name)
        next_num = last_num + 1
        
        print(f"🔢 '{city_name}' 번호 연속성: 마지막 {last_num} → 다음 {next_num}")
        
        return next_num
        
    except Exception as e:
        print(f"⚠️ 번호 연속성 확인 실패: {e}")
        return 1  # 기본값

# =============================================================================
# 국가별 통합 CSV 생성 시스템 - 원본 코드 기반
# =============================================================================

def create_country_consolidated_csv(country_name, force_recreate=False):
    """국가별 통합 CSV 파일 생성 - 전체 대륙 지원 범용 버전"""
    print(f"\n🌏 '{country_name}' 국가별 통합 CSV 생성 중...")
    
    try:
        # 국가별 데이터 폴더 찾기 (전체 대륙 지원)
        data_base = os.path.join(os.getcwd(), "data")
        country_cities = []
        
        # 해당 국가가 속한 대륙 찾기
        from ..config import UNIFIED_CITY_INFO
        country_continent = None
        for city_name, city_info in UNIFIED_CITY_INFO.items():
            if city_info.get("국가") == country_name:
                country_continent = city_info.get("대륙")
                break
        
        # 대륙을 찾지 못한 경우 모든 대륙에서 검색
        if not country_continent:
            print(f"   🔍 '{country_name}'의 대륙 정보를 찾지 못함 - 전체 대륙에서 검색")
            search_continents = ["아시아", "유럽", "북미", "오세아니아", "중동", "아프리카", "남미"]
        else:
            print(f"   🗺️ '{country_name}' 대륙: {country_continent}")
            search_continents = [country_continent]
        
        # 대륙별로 해당 국가 폴더 검색
        for continent in search_continents:
            continent_country_path = os.path.join(data_base, continent, country_name)
            if os.path.exists(continent_country_path):
                print(f"   📂 '{continent}/{country_name}' 경로 발견")
                for city in os.listdir(continent_country_path):
                    city_path = os.path.join(continent_country_path, city)
                    if os.path.isdir(city_path):
                        # 도시별 CSV 찾기
                        csv_file = os.path.join(city_path, f"klook_{city}_products.csv")
                        if os.path.exists(csv_file):
                            country_cities.append((city, csv_file))
        
        # 도시국가 특별 처리 (대륙 직하에 있는 경우)
        city_countries = ["홍콩", "싱가포르", "마카오", "괌"]
        if country_name in city_countries:
            for continent in search_continents:
                city_csv = os.path.join(data_base, continent, f"klook_{country_name}_products.csv")
                if os.path.exists(city_csv):
                    country_cities.append((country_name, city_csv))
                    break
        
        if not country_cities:
            print(f"   ❌ '{country_name}'에서 CSV 파일을 찾을 수 없습니다.")
            return False
        
        print(f"   📊 발견된 도시: {len(country_cities)}개")
        for city, _ in country_cities:
            print(f"      - {city}")
        
        # 통합 CSV 경로 (대륙별로 생성)
        if country_continent:
            # 대륙 정보가 있는 경우
            if country_name in city_countries:
                # 도시국가: 대륙 직하에 저장
                consolidated_path = os.path.join(data_base, country_continent, f"{country_name}_통합_klook_products.csv")
            else:
                # 일반 국가: 대륙/국가/ 경로에 저장
                country_dir = os.path.join(data_base, country_continent, country_name)
                os.makedirs(country_dir, exist_ok=True)
                consolidated_path = os.path.join(country_dir, f"{country_name}_통합_klook_products.csv")
        else:
            # 대륙 정보가 없는 경우: 기타 폴더에 저장
            other_dir = os.path.join(data_base, "기타", country_name)
            os.makedirs(other_dir, exist_ok=True)
            consolidated_path = os.path.join(other_dir, f"{country_name}_통합_klook_products.csv")
        
        # 기존 파일 확인
        if os.path.exists(consolidated_path) and not force_recreate:
            print(f"   ✅ 통합 파일이 이미 존재합니다: {consolidated_path}")
            return True
        
        # CSV 병합 (pandas 없이 구현)
        import csv as csv_module
        
        all_rows = []
        header = None
        total_products = 0
        
        for city, csv_file in country_cities:
            try:
                with open(csv_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv_module.reader(f)
                    city_rows = list(reader)
                    
                    if city_rows:
                        if header is None:
                            header = city_rows[0]  # 첫 번째 파일의 헤더 사용
                        
                        # 데이터 행만 추가 (헤더 제외)
                        data_rows = city_rows[1:] if len(city_rows) > 1 else []
                        all_rows.extend(data_rows)
                        print(f"      📄 {city}: {len(data_rows)}개 상품")
                        total_products += len(data_rows)
                    
            except Exception as e:
                print(f"      ❌ {city} CSV 읽기 실패: {e}")
        
        if not all_rows:
            print(f"   ❌ 읽을 수 있는 CSV 데이터가 없습니다.")
            return False
        
        # 번호 재정렬
        for i, row in enumerate(all_rows, 1):
            if len(row) > 0:
                row[0] = str(i)  # 첫 번째 컬럼이 번호라고 가정
        
        # 통합 CSV 저장
        with open(consolidated_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv_module.writer(f)
            if header:
                writer.writerow(header)
            writer.writerows(all_rows)
        
        print(f"   ✅ 통합 CSV 생성 완료!")
        print(f"      📊 총 상품: {total_products}개")
        print(f"      📁 저장 위치: {consolidated_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 통합 CSV 생성 실패: {e}")
        return False

def auto_create_country_csv_after_crawling(city_name):
    """크롤링 완료 후 자동으로 국가별 통합 CSV 생성"""
    try:
        continent, country = get_city_info(city_name)
        
        if country:
            print(f"\n🌏 '{city_name}' 크롤링 완료 후 '{country}' 국가별 통합 CSV 자동 생성...")
            success = create_country_consolidated_csv(country)
            if success:
                print(f"   ✅ '{country}' 국가별 통합 CSV 자동 생성 완료!")
            else:
                print(f"   ⚠️ '{country}' 국가별 통합 CSV 생성 실패")
        
    except Exception as e:
        print(f"   ⚠️ 국가별 통합 CSV 자동 생성 중 오류: {e}")


print("✅ file_handler.py 로드 완료: 파일 처리 시스템 준비!")
print("   📸 도시코드 기반 이미지 파일명: KMJ_0001.jpg, KMJ_0001_thumb.jpg")
print("   📊 국가별 통합 CSV 자동 생성 기능 포함")