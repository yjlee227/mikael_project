"""
🚀 그룹 2: 이미지 처리 및 데이터 저장 함수들
- 이미지 다운로드, 리사이즈, 저장 시스템
- CSV 데이터 저장 및 관리
- 파일 시스템 관리 및 최적화
"""

import os
import time
import random
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# config 모듈에서 모든 설정과 라이브러리 상태 import
from .config import CONFIG, get_city_info, get_city_code, PANDAS_AVAILABLE, PIL_AVAILABLE

# 조건부 import - config에서 확인된 상태에 따라
if PANDAS_AVAILABLE:
    import pandas as pd

# requests는 이 모듈에서만 필요하므로 로컬 체크
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("⚠️ requests가 설치되지 않았습니다. 이미지 다운로드 기능이 제한됩니다.")
    REQUESTS_AVAILABLE = False

if PIL_AVAILABLE:
    from PIL import Image

# =============================================================================
# 📸 이미지 처리 시스템
# =============================================================================

def get_image_src_klook(driver, url_type="Product"):
    """✅ 이미지 URL 수집 (KLOOK 최적화)"""
    print(f"  📸 {url_type} 이미지 수집 중...")

    image_selectors = [
        ("css", ".ActivityCardImage--image"),           # KLOOK 최우선 (100% 확인됨)
        ("css", ".card-pic img"),                       # KLOOK 백업
        ("css", ".activity-card-image img"),            # KLOOK 백업2  
        ("css", "img[alt*='activity']"),                # KLOOK 백업3
        ("css", "img[src*='klook']"),                   # KLOOK 도메인 이미지
        ("css", "img"),                                 # 범용 백업
    ]

    for selector_type, selector_value in image_selectors:
        try:
            if selector_type == "css":
                image_elements = driver.find_elements("css selector", selector_value)
            
            for img_element in image_elements:
                try:
                    img_src = img_element.get_attribute("src")
                    if img_src and ("klook" in img_src.lower() or "activity" in img_src.lower() or len(img_src) > 50):
                        return img_src
                except:
                    continue
                    
        except Exception:
            continue
    
    raise Exception("이미지를 찾을 수 없습니다")

def get_dual_image_urls_klook(driver, url_type="Product"):
    """✅ 메인 + 썸네일 이미지 URL 수집 (KLOOK 최적화)"""
    print(f"  📸 {url_type} 듀얼 이미지 수집 중...")
    
    # 메인 이미지와 썸네일 이미지 선택자들 (실제 작동하는 셀렉터로 업데이트)
    main_selectors = [
        ("css", "#banner_atlas .activity-banner-image-container_left img"),   # KLOOK 메인 이미지 (실제 작동)
        ("css", ".activity-banner-image-container_left img"),                 # 백업 1
        ("css", ".main-image img"),                                           # 일반 백업
        ("css", ".hero-image img"),                                           # 일반 백업
        ("css", ".product-image img"),                                        # 일반 백업
        ("css", ".ActivityCardImage--image"),                                 # 기존 셀렉터 (백업)
        ("css", ".product-hero-image img"),                                   # 상세 페이지 메인 (백업)
    ]
    
    thumb_selectors = [
        # 원본 노트북과 동일한 썸네일 셀렉터 (작동 확인됨)
        ("css", "#banner_atlas .activity-banner-image-container_right img"),  # KLOOK 썸네일 이미지
        ("css", ".activity-banner-image-container_right img"),                # 백업 1
        ("css", ".product-gallery img:nth-child(2)"),                        # 일반 백업
        ("css", ".gallery img:nth-child(2)"),                                # 일반 백업
        ("css", ".slider img:nth-child(2)"),                                 # 일반 백업
        # 추가 백업 셀렉터들
        ("css", ".Gallery-module--thumbnails img"),     # 갤러리 썸네일 (새 구조)
        ("css", ".gallery-thumbnails img"),             # 갤러리 썸네일
        ("css", "[data-testid='gallery-thumbnail'] img"), # 테스트ID 기반
        ("css", ".thumbnail img"),                      # 일반 썸네일
        ("css", ".swiper-slide img"),                   # 스와이퍼 슬라이드 내 이미지
        ("css", ".image-gallery-thumbnails img"),       # 이미지 갤러리 썸네일
        ("css", ".product-gallery-thumb img"),          # 상품 갤러리 썸네일
        ("css", ".slider-thumb img"),                   # 슬라이더 썸네일
    ]
    
    images = {"main": None, "thumb": None}
    
    # 메인 이미지 찾기 (디버그 정보 추가)
    print(f"    🔍 메인 이미지 검색 시작...")
    for i, (selector_type, selector_value) in enumerate(main_selectors):
        try:
            if selector_type == "css":
                image_elements = driver.find_elements("css selector", selector_value)
                print(f"      📍 메인 셀렉터 {i+1}: '{selector_value}' → {len(image_elements)}개 요소")
            
            if image_elements:
                for j, img_element in enumerate(image_elements):
                    try:
                        img_src = img_element.get_attribute("src")
                        print(f"        - 요소 {j+1}: {img_src[:80]}..." if img_src else f"        - 요소 {j+1}: src 없음")
                        if img_src and ("klook" in img_src.lower() or "activity" in img_src.lower() or len(img_src) > 50):
                            images["main"] = img_src
                            print(f"      ✅ 메인 이미지 발견: {img_src[:80]}...")
                            break
                    except Exception as e:
                        print(f"        - 요소 {j+1}: 오류 - {e}")
                        continue
            
            if images["main"]:
                break
                    
        except Exception as e:
            print(f"      ❌ 메인 셀렉터 '{selector_value}' 처리 실패: {e}")
            continue
    
    if not images["main"]:
        print(f"      ⚠️ 메인 이미지를 찾지 못했습니다")
    
    # 썸네일 이미지 찾기 (디버그 정보 추가)
    print(f"    🔍 썸네일 이미지 검색 시작...")
    for i, (selector_type, selector_value) in enumerate(thumb_selectors):
        try:
            if selector_type == "css":
                image_elements = driver.find_elements("css selector", selector_value)
                print(f"      📍 썸네일 셀렉터 {i+1}: '{selector_value}' → {len(image_elements)}개 요소")
            
            if image_elements:
                for j, img_element in enumerate(image_elements):
                    try:
                        img_src = img_element.get_attribute("src")
                        print(f"        - 요소 {j+1}: {img_src[:60] if img_src else 'None'}...")
                        if img_src and img_src != images["main"] and ("klook" in img_src.lower() or "thumb" in img_src.lower() or len(img_src) > 30):
                            images["thumb"] = img_src
                            print(f"      ✅ 썸네일 발견: {img_src[:60]}...")
                            break
                    except Exception as e:
                        print(f"        ❌ 요소 {j+1} 처리 실패: {e}")
                        continue
            
            if images["thumb"]:
                break
                    
        except Exception as e:
            print(f"      ❌ 셀렉터 '{selector_value}' 실패: {e}")
            continue
    
    if not images["thumb"]:
        print(f"      ⚠️ 썸네일 이미지를 찾을 수 없습니다")
    
    return images

def download_and_save_image_klook(img_src, product_number, city_name, max_size_kb=300):
    """✅ 이미지 다운로드 및 저장 (KLOOK 최적화)"""
    if not CONFIG["SAVE_IMAGES"]:
        return None
    
    if not REQUESTS_AVAILABLE:
        print("  ⚠️ requests가 설치되지 않아 이미지 다운로드를 건너뜁니다.")
        return None
    
    if not PIL_AVAILABLE:
        print("  ⚠️ PIL이 설치되지 않아 이미지 처리를 건너뜁니다.")
        return None
        
    print(f"  📥 이미지 다운로드 및 리사이즈 시작...")
    
    try:
        # 파일명 생성 (간단한 형식)
        city_code = get_city_code(city_name)
        img_filename = f"{city_code}_{product_number:04d}.jpg"  # HAN_0001.jpg 형식
        
        # 이미지 폴더 경로 (계층적 구조)
        continent, country = get_city_info(city_name)
        img_base_folder = os.path.join(os.getcwd(), "klook_thumb_img")
        
        # 기존 시스템과 호환되는 폴더 구조
        if city_name in ["마카오", "홍콩", "싱가포르"]:
            img_folder = os.path.join(img_base_folder, continent)
        else:
            img_folder = os.path.join(img_base_folder, continent, country, city_name)
        
        os.makedirs(img_folder, exist_ok=True)
        img_path = os.path.join(img_folder, img_filename)
        
        # 이미지 다운로드
        headers = {
            'User-Agent': CONFIG["USER_AGENT"],
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
            
            # 적절한 크기로 리사이즈 (가로 400px 기준)
            width, height = img.size
            if width > 400:
                ratio = 400 / width
                new_height = int(height * ratio)
                img = img.resize((400, new_height), Image.Resampling.LANCZOS)
            
            # 품질 조정하여 저장 (300KB 이하 목표)
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
        print(f"  ✅ 이미지 저장 완료: {img_filename} ({file_size_kb:.1f}KB)")
        return img_filename
        
    except Exception as e:
        print(f"  ❌ 이미지 저장 실패: {type(e).__name__}: {e}")
        # 임시 파일 정리
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return None

def download_dual_images_klook(image_urls, product_number, city_name, max_size_kb=300):
    """✅ 듀얼 이미지 다운로드 및 저장 (메인 + 썸네일, 메인만 fallback)"""
    if not CONFIG["SAVE_IMAGES"]:
        return {"main": None, "thumb": None}
    
    if not REQUESTS_AVAILABLE or not PIL_AVAILABLE:
        print("  ⚠️ 필요한 라이브러리가 설치되지 않아 이미지 다운로드를 건너뜁니다.")
        return {"main": None, "thumb": None}
    
    results = {"main": None, "thumb": None}
    
    # 메인 이미지 다운로드
    if image_urls.get("main"):
        print(f"  📥 메인 이미지 다운로드 중...")
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
        print(f"  📥 썸네일 이미지 다운로드 중...")
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
        print(f"  ✅ 듀얼 이미지 저장 완료: 메인 + 썸네일")
    elif results["main"]:
        print(f"  ✅ 메인 이미지만 저장 완료 (썸네일 없음)")
    else:
        print(f"  ❌ 이미지 저장 실패")
    
    return results

def download_single_image_klook(img_src, product_number, city_name, image_type="main", max_size_kb=300):
    """✅ 단일 이미지 다운로드 (메인/썸네일 구분)"""
    try:
        # 파일명 생성 (간단하고 명확한 형식)
        city_code = get_city_code(city_name)
        if image_type == "main":
            img_filename = f"{city_code}_{product_number:04d}.jpg"  # HAN_0001.jpg
        else:
            img_filename = f"{city_code}_{product_number:04d}_thumb.jpg"  # HAN_0001_thumb.jpg
        
        # 이미지 폴더 경로 (계층적 구조)
        continent, country = get_city_info(city_name)
        img_base_folder = os.path.join(os.getcwd(), "klook_thumb_img")
        
        # 기존 시스템과 호환되는 폴더 구조
        if city_name in ["마카오", "홍콩", "싱가포르"]:
            img_folder = os.path.join(img_base_folder, continent)
        else:
            img_folder = os.path.join(img_base_folder, continent, country, city_name)
        
        os.makedirs(img_folder, exist_ok=True)
        img_path = os.path.join(img_folder, img_filename)
        
        # 이미지 다운로드
        headers = {
            'User-Agent': CONFIG["USER_AGENT"],
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
        print(f"    ✅ {image_type} 이미지 저장: {img_filename} ({file_size_kb:.1f}KB)")
        return img_filename
        
    except Exception as e:
        print(f"    ❌ {image_type} 이미지 저장 실패: {type(e).__name__}: {e}")
        # 임시 파일 정리
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return None

# =============================================================================
# 💾 CSV 데이터 저장 시스템
# =============================================================================

def safe_csv_write(file_path, df, mode='w', header=True):
    """CSV 파일을 안전하게 작성 (Permission denied 오류 해결)"""
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            # 기존 파일이 있고 쓰기 모드인 경우 백업 생성
            if mode == 'a' and os.path.exists(file_path):
                # 파일이 잠겨있는지 확인
                try:
                    with open(file_path, 'a', encoding='utf-8-sig') as test_file:
                        test_file.write('')  # 빈 문자열 쓰기 테스트
                except PermissionError:
                    print(f"    ⚠️ 파일이 잠겨있음, {attempt+1}번째 재시도...")
                    time.sleep(2)  # 2초 대기
                    continue
            
            # CSV 파일 작성
            df.to_csv(file_path, mode=mode, header=header, index=False, encoding='utf-8-sig')
            return True
            
        except PermissionError as e:
            print(f"    ⚠️ 권한 오류 ({attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                # 잠깐 대기 후 재시도
                wait_time = (attempt + 1) * 2  # 2, 4, 6, 8초
                print(f"    ⏰ {wait_time}초 대기 후 재시도...")
                time.sleep(wait_time)
            else:
                # 최종 시도 - 백업 파일로 저장
                backup_path = file_path.replace('.csv', f'_backup_{datetime.now().strftime("%H%M%S")}.csv')
                try:
                    df.to_csv(backup_path, mode='w', header=True, index=False, encoding='utf-8-sig')
                    print(f"    💾 백업 파일로 저장: {backup_path}")
                    return True
                except Exception as backup_error:
                    print(f"    ❌ 백업 저장도 실패: {backup_error}")
                    return False
                    
        except Exception as e:
            print(f"    ❌ 예상치 못한 오류: {e}")
            return False
    
    return False

def save_to_csv_klook(product_data, city_name):
    """✅ KLOOK 상품 데이터를 CSV 파일로 저장 (원본 노트북과 동일하게 국가별 CSV 자동 생성)"""
    if not product_data:
        print("  ⚠️ 저장할 데이터가 없습니다.")
        return False
    
    if not PANDAS_AVAILABLE:
        print("  ⚠️ pandas가 설치되지 않아 CSV 저장을 건너뜁니다.")
        return False

    try:
        continent, country = get_city_info(city_name)
        city_code = get_city_code(city_name)
        
        # DataFrame 생성
        df = pd.DataFrame([product_data])
        
        # 도시ID가 없으면 추가
        if '도시ID' not in df.columns or df['도시ID'].empty:
            df['도시ID'] = f"{city_code}_1"
            print(f"  ✅ 도시ID 컬럼 추가: {city_code}_1")
        
        # 번호가 없으면 추가
        if '번호' not in df.columns:
            df['번호'] = 1
            print(f"  ✅ 번호 컬럼 추가: 1")
        
        # 도시국가 처리 (원본과 동일)
        if city_name in ["마카오", "홍콩", "싱가포르"]:
            data_dir = os.path.join("data", continent)
            os.makedirs(data_dir, exist_ok=True)
            city_csv = os.path.join(data_dir, f"klook_{city_name}_products.csv")
            
            if os.path.exists(city_csv):
                city_success = safe_csv_write(city_csv, df, mode='a', header=False)
            else:
                city_success = safe_csv_write(city_csv, df, mode='w', header=True)
            
            if city_success:
                print(f"  💾 도시국가 데이터 저장 완료: {city_csv}")
                return True
            else:
                print(f"  ❌ 도시국가 데이터 저장 실패")
                return False

        # 일반 도시 처리 - 원본 노트북과 동일하게 도시별 + 국가별 CSV 동시 생성
        data_dir = os.path.join("data", continent, country, city_name)
        os.makedirs(data_dir, exist_ok=True)

        city_csv = os.path.join(data_dir, f"klook_{city_name}_products.csv")
        
        # 도시별 CSV 저장
        if os.path.exists(city_csv):
            city_success = safe_csv_write(city_csv, df, mode='a', header=False)
        else:
            city_success = safe_csv_write(city_csv, df, mode='w', header=True)

        # 국가별 CSV 자동 생성 (원본 노트북과 동일)
        country_dir = os.path.join("data", continent, country)
        os.makedirs(country_dir, exist_ok=True)
        country_csv = os.path.join(country_dir, f"{country}_klook_products_all.csv")
        
        country_df = df.copy()
        
        if os.path.exists(country_csv):
            existing_df = pd.read_csv(country_csv, encoding='utf-8-sig')
            if not existing_df.empty and '번호' in existing_df.columns:
                last_number = existing_df['번호'].max()
                country_df['번호'] = int(last_number) + 1
                print(f"  🔗 국가별 연속번호: {last_number + 1}")
            country_success = safe_csv_write(country_csv, country_df, mode='a', header=False)
        else:
            country_df['번호'] = 1
            print(f"  🆕 국가별 신규파일: 1")
            country_success = safe_csv_write(country_csv, country_df, mode='w', header=True)

        if city_success and country_success:
            print(f"  💾 데이터 저장 완료:")
            print(f"     📁 도시별: {city_csv}")
            print(f"     📁 국가별: {country_csv}")
            print(f"     🆔 도시ID: {city_code}_X")
            return True
        else:
            print(f"  ⚠️ 일부 파일 저장 실패 (도시:{city_success}, 국가:{country_success})")
            return False
        
    except Exception as e:
        print(f"  ❌ CSV 저장 실패: {type(e).__name__}: {e}")
        return False

def create_product_data_structure(product_number, product_name, price, image_filename, url, city_name, additional_data=None, tab_info=None, dual_images=None):
    """✅ 상품 데이터 구조 생성 (기존 32개 컬럼 구조 적용)"""
    continent, country = get_city_info(city_name)
    city_code = get_city_code(city_name)
    
    # 기존 32개 컬럼 구조에 맞는 데이터 생성
    base_data = {
        # 기본 정보
        "번호": product_number,
        "도시ID": f"{city_code}_{product_number}",
        "페이지": tab_info.get("page", 1) if tab_info else 1,
        "대륙": continent,
        "국가": country,
        "도시": city_name,
        "공항코드": city_code,
        "상품타입": "Activity",
        "상품명": product_name,
        
        # 가격 정보
        "가격_원본": additional_data.get("가격_원본", price) if additional_data else price,
        "가격_정제": price,
        
        # 평점 및 리뷰
        "평점_원본": additional_data.get("평점_원본", "정보 없음") if additional_data else "정보 없음",
        "평점_정제": additional_data.get("평점", "정보 없음") if additional_data else "정보 없음",
        "리뷰수": additional_data.get("리뷰수", "정보 없음") if additional_data else "정보 없음",
        
        # 기타 정보
        "언어": additional_data.get("언어", "정보 없음") if additional_data else "정보 없음",
        "카테고리": additional_data.get("카테고리", "정보 없음") if additional_data else "정보 없음",
        "하이라이트": additional_data.get("하이라이트", "정보 없음") if additional_data else "정보 없음",
        "위치": additional_data.get("위치", "정보 없음") if additional_data else "정보 없음",
        
        # 메인 이미지 정보 (듀얼 이미지 시스템 적용)
        "메인이미지_파일명": dual_images.get("main") if dual_images and dual_images.get("main") else (image_filename if image_filename else "정보 없음"),
        "메인이미지_상대경로": f"{continent}\\{country}\\{city_name}\\{dual_images.get('main')}" if dual_images and dual_images.get("main") else (f"{continent}\\{country}\\{city_name}\\{image_filename}" if image_filename else "정보 없음"),
        "메인이미지_전체경로": f"klook_thumb_img\\{continent}\\{country}\\{city_name}\\{dual_images.get('main')}" if dual_images and dual_images.get("main") else (f"klook_thumb_img\\{continent}\\{country}\\{city_name}\\{image_filename}" if image_filename else "정보 없음"),
        "메인이미지_상태": "메인 다운로드 완료" if (dual_images and dual_images.get("main")) or image_filename else "다운로드 실패",
        
        # 썸네일 이미지 정보 (듀얼 이미지 시스템)
        "썸네일이미지_파일명": dual_images.get("thumb") if dual_images and dual_images.get("thumb") else "정보 없음",
        "썸네일이미지_상대경로": f"{continent}\\{country}\\{city_name}\\{dual_images.get('thumb')}" if dual_images and dual_images.get("thumb") else "정보 없음",
        "썸네일이미지_전체경로": f"klook_thumb_img\\{continent}\\{country}\\{city_name}\\{dual_images.get('thumb')}" if dual_images and dual_images.get("thumb") else "정보 없음",
        "썸네일이미지_상태": "썸네일 다운로드 완료" if dual_images and dual_images.get("thumb") else "정보 없음",
        
        # URL 및 메타데이터
        "URL": url,
        "수집_시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "상태": "완전수집",
        
        # 탭 및 랭킹 정보 (실제 순위 사용)
        "탭명": tab_info.get("tab_name", "전체") if tab_info else "전체",
        "탭순서": tab_info.get("tab_order", 1) if tab_info else 1,
        "탭내_랭킹": tab_info.get("actual_ranking", product_number) if tab_info else product_number,
        "URL_해시": additional_data.get("URL_해시", "") if additional_data else ""
    }
    
    # 추가 데이터가 있으면 기존 32개 컬럼 내에서만 업데이트 (추가 컬럼 생성 방지)
    if additional_data:
        print(f"    📝 추가 데이터 확인: {list(additional_data.keys())}")
        allowed_updates = ["가격_원본", "평점_원본", "평점", "리뷰수", "언어", "카테고리", "하이라이트", "위치", "URL_해시"]
        for key, value in additional_data.items():
            if key in allowed_updates and key in base_data:
                base_data[key] = value
                print(f"      ✅ 업데이트: {key} = {value}")
            elif key not in allowed_updates:
                print(f"      ⏭️ 스킵됨: {key} (32컬럼 구조 유지)")
    else:
        print(f"    ⚠️ 추가 데이터 없음 - additional_data가 비어있거나 None")
    
    return base_data

# =============================================================================
# 📊 데이터 관리 및 통계
# =============================================================================

def get_csv_stats(city_name):
    """CSV 파일 통계 정보 조회"""
    if not PANDAS_AVAILABLE:
        print("⚠️ pandas가 설치되지 않아 CSV 통계를 확인할 수 없습니다.")
        return {"exists": False, "error": "pandas not available"}
    
    try:
        continent, country = get_city_info(city_name)
        
        # 도시국가 특별 처리
        if city_name in ["마카오", "홍콩", "싱가포르"]:
            csv_path = os.path.join("data", continent, f"klook_{city_name}_products.csv")
        else:
            csv_path = os.path.join("data", continent, country, city_name, f"klook_{city_name}_products.csv")
        
        if not os.path.exists(csv_path):
            return {"exists": False, "count": 0, "last_updated": None}
        
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        file_mtime = os.path.getmtime(csv_path)
        last_updated = datetime.fromtimestamp(file_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "exists": True,
            "count": len(df),
            "last_updated": last_updated,
            "file_size": os.path.getsize(csv_path),
            "columns": list(df.columns)
        }
        
    except Exception as e:
        print(f"⚠️ CSV 통계 조회 실패: {e}")
        return {"exists": False, "error": str(e)}

def backup_csv_data(city_name, backup_suffix=None):
    """CSV 데이터 백업"""
    try:
        continent, country = get_city_info(city_name)
        
        # 도시국가 특별 처리 (기존 구조 호환)
        if city_name in ["마카오", "홍콩", "싱가포르"]:
            csv_dir = os.path.join("data", continent)
            csv_filename = f"{city_name}_klook_products_all.csv"  # 기존 파일명 형식
        else:
            csv_dir = os.path.join("data", continent, country, city_name)
            csv_filename = f"{city_name}_klook_products_all.csv"  # 기존 파일명 형식
        
        csv_path = os.path.join(csv_dir, csv_filename)
        
        if not os.path.exists(csv_path):
            print(f"⚠️ 백업할 CSV 파일이 없습니다: {csv_path}")
            return False
        
        # 백업 파일명 생성
        if not backup_suffix:
            backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        backup_filename = f"klook_{city_name}_products_backup_{backup_suffix}.csv"
        backup_path = os.path.join(csv_dir, backup_filename)
        
        # 파일 복사
        import shutil
        shutil.copy2(csv_path, backup_path)
        
        print(f"✅ CSV 백업 완료: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ CSV 백업 실패: {e}")
        return False

# =============================================================================
# 🧹 파일 시스템 정리
# =============================================================================

def cleanup_temp_files():
    """임시 파일 정리"""
    temp_patterns = [
        "*.temp",
        "*.tmp",
        "cookies/*/Default/Cookies",
        "cookies/*/Default/Cookies-journal"
    ]
    
    cleaned_count = 0
    for pattern in temp_patterns:
        try:
            import glob
            temp_files = glob.glob(pattern, recursive=True)
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                    cleaned_count += 1
                except:
                    pass
        except:
            pass
    
    if cleaned_count > 0:
        print(f"🧹 임시 파일 {cleaned_count}개 정리 완료")
    
    return cleaned_count


def create_country_consolidated_csv(country_name, force_recreate=False):
    """✅ 국가별 통합 CSV 파일 생성"""
    print(f"\n🌏 '{country_name}' 국가별 통합 CSV 생성 중...")
    
    try:
        # 국가별 데이터 폴더 찾기
        data_base = os.path.join(os.getcwd(), "data")
        country_cities = []
        
        # 아시아 대륙에서 해당 국가 찾기
        asia_path = os.path.join(data_base, "아시아", country_name)
        if os.path.exists(asia_path):
            for city in os.listdir(asia_path):
                city_path = os.path.join(asia_path, city)
                if os.path.isdir(city_path):
                    # 도시별 CSV 찾기
                    csv_file = os.path.join(city_path, f"{city}_klook_products_all.csv")
                    if os.path.exists(csv_file):
                        country_cities.append((city, csv_file))
        
        # 도시국가 특별 처리 (홍콩, 싱가포르, 마카오)
        special_cities = ["홍콩", "싱가포르", "마카오"]
        for city in special_cities:
            if city == country_name:  # 국가명과 도시명이 같은 경우
                city_csv = os.path.join(data_base, "아시아", f"{city}_klook_products_all.csv")
                if os.path.exists(city_csv):
                    country_cities.append((city, city_csv))
        
        if not country_cities:
            print(f"   ❌ '{country_name}'에서 CSV 파일을 찾을 수 없습니다.")
            return False
        
        print(f"   📊 발견된 도시: {len(country_cities)}개")
        for city, _ in country_cities:
            print(f"      - {city}")
        
        # 통합 CSV 경로
        if country_name in special_cities:
            consolidated_path = os.path.join(data_base, "아시아", f"{country_name}_통합_klook_products.csv")
        else:
            country_dir = os.path.join(data_base, "아시아", country_name)
            os.makedirs(country_dir, exist_ok=True)
            consolidated_path = os.path.join(country_dir, f"{country_name}_통합_klook_products.csv")
        
        # 기존 파일 확인
        if os.path.exists(consolidated_path) and not force_recreate:
            print(f"   ✅ 통합 파일이 이미 존재합니다: {consolidated_path}")
            return True
        
        # 모든 도시 CSV 병합 (pandas 없이 구현)
        try:
            import pandas as pd
            # pandas가 있는 경우 기존 방식 사용
            all_dataframes = []
            total_products = 0
            
            for city, csv_file in country_cities:
                try:
                    df = pd.read_csv(csv_file, encoding='utf-8-sig')
                    print(f"      📄 {city}: {len(df)}개 상품")
                    all_dataframes.append(df)
                    total_products += len(df)
                except Exception as e:
                    print(f"      ❌ {city} CSV 읽기 실패: {e}")
            
            if not all_dataframes:
                print(f"   ❌ 읽을 수 있는 CSV 파일이 없습니다.")
                return False
            
            # 데이터프레임 병합
            consolidated_df = pd.concat(all_dataframes, ignore_index=True)
            
            # 번호 재정렬
            consolidated_df['번호'] = range(1, len(consolidated_df) + 1)
            
            # 통합 CSV 저장
            consolidated_df.to_csv(consolidated_path, index=False, encoding='utf-8-sig')
            
        except ImportError:
            # pandas가 없는 경우 수동으로 CSV 병합
            print(f"   📊 pandas 없이 CSV 병합 중...")
            import csv
            
            all_rows = []
            header = None
            total_products = 0
            
            for city, csv_file in country_cities:
                try:
                    with open(csv_file, 'r', encoding='utf-8-sig') as f:
                        reader = csv.reader(f)
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
                writer = csv.writer(f)
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
    """✅ 크롤링 완료 후 자동으로 국가별 통합 CSV 생성"""
    try:
        from .config import get_city_info
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

print("✅ 그룹 2 완료: 이미지 처리 및 데이터 저장 함수들 정의 완료!")
print("   📸 이미지 시스템:")
print("   - get_image_src_klook(): KLOOK 이미지 URL 수집")
print("   - download_and_save_image_klook(): 이미지 다운로드 및 최적화")
print("   - get_dual_image_urls_klook(): 듀얼 이미지 URL 수집 (업그레이드)")
print("   - download_dual_images_klook(): 메인+썸네일 다운로드 (업그레이드)")
print("   💾 데이터 저장:")
print("   - save_to_csv_klook(): CSV 저장 (도시국가 특별 처리)")
print("   - create_product_data_structure(): 상품 데이터 구조 생성")
print("   - create_country_consolidated_csv(): 국가별 통합 CSV 생성 (신규)")
print("   - auto_create_country_csv_after_crawling(): 자동 통합 생성 (신규)")
print("   📊 데이터 관리:")
print("   - get_csv_stats(): CSV 통계 조회")
print("   - backup_csv_data(): 데이터 백업")
print("   🧹 시스템 관리:")
print("   - cleanup_temp_files(): 임시 파일 정리")