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
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse

# 내부 모듈 import
from .city_manager import get_city_info, get_city_code

# Selenium은 이미지 URL 추출에만 필요하므로 조건부로 import
try:
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# CONFIG는 crawler에서 주입받거나, 나중에 config 모듈에서 직접 import
# 여기서는 예시로 기본값을 사용합니다.
DEFAULT_CONFIG = {
    "SAVE_IMAGES": True,
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# =============================================================================
# 데이터 구조 및 연속성 관리
# =============================================================================

def create_product_data_structure(city_name, product_number, rank=None):
    """(리팩토링 목표) kkday와 동일한 표준 데이터 구조 생성"""
    continent, country = get_city_info(city_name)
    city_code = get_city_code(city_name)
    
    # TODO: 이 구조를 kkday의 최종 컬럼 스키마와 100% 일치시키기
    return {
        "번호": product_number,
        "상품명": "",
        "가격": "",
        "평점": "",
        "리뷰수": "",
        "URL": "",
        "도시ID": f"{city_code}_{product_number:04d}",
        "도시명": city_name,
        "대륙": continent,
        "국가": country,
        "데이터소스": "MyRealTrip",
        "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "해시값": "",
        "메인이미지": "",
        "썸네일이미지": ""
    }

def get_last_product_number(city_name):
    """기존 CSV에서 마지막 상품 번호 확인"""
    try:
        continent, country = get_city_info(city_name)
        csv_path = os.path.join("data", continent, country, city_name, f"myrealtrip_{city_name}_products.csv")
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            if not df.empty and '번호' in df.columns:
                return df['번호'].max()
        return 0
    except Exception:
        return 0

# =============================================================================
# 디렉토리 및 파일 경로 관리
# =============================================================================

def ensure_directory_structure(city_name):
    """크롤링에 필요한 모든 디렉토리 구조를 생성"""
    try:
        continent, country = get_city_info(city_name)
        base_dirs = ["data", "myrealtripthumb_img", "hash_index"]
        
        for base_dir in base_dirs:
            if base_dir == "hash_index":
                path = os.path.join(base_dir, city_name)
            else:
                path = os.path.join(base_dir, continent, country, city_name)
            os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"⚠️ 디렉토리 생성 실패: {e}")
        return False

# =============================================================================
# CSV 파일 처리
# =============================================================================

def safe_csv_write(file_path, df, mode='w', header=True):
    """CSV 파일을 안전하게 작성 (Permission denied 오류 해결)"""
    # ... (기존 노트북의 safe_csv_write 함수 내용과 동일)
    max_retries = 5
    for attempt in range(max_retries):
        try:
            df.to_csv(file_path, mode=mode, header=header, index=False, encoding='utf-8-sig')
            return True
        except PermissionError as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return False
    return False

def save_batch_data(batch_results, city_name):
    """배치 데이터를 도시별/국가별 CSV에 저장"""
    # ... (기존 노트북의 save_batch_data 함수 내용과 동일)
    if not batch_results:
        return None
    try:
        df = pd.DataFrame(batch_results)
        continent, country = get_city_info(city_name)
        city_code = get_city_code(city_name)

        # 도시별 CSV 저장
        city_dir = os.path.join("data", continent, country, city_name)
        city_csv_path = os.path.join(city_dir, f"myrealtrip_{city_name}_products.csv")
        file_exists = os.path.exists(city_csv_path)
        safe_csv_write(city_csv_path, df, mode='a', header=not file_exists)

        # 국가별 통합 CSV 저장
        country_dir = os.path.join("data", continent, country)
        country_csv_path = os.path.join(country_dir, f"{country}_myrealtrip_products_all.csv")
        country_df = df.copy()
        country_file_exists = os.path.exists(country_csv_path)

        if country_file_exists:
            existing_df = pd.read_csv(country_csv_path, encoding='utf-8-sig')
            last_number = existing_df['번호'].max() if not existing_df.empty else 0
            country_df['번호'] = range(int(last_number) + 1, int(last_number) + 1 + len(country_df))
        else:
            country_df['번호'] = range(1, len(country_df) + 1)
        
        safe_csv_write(country_csv_path, country_df, mode='a', header=not country_file_exists)
        return city_csv_path
    except Exception as e:
        print(f"❌ 배치 데이터 저장 실패: {e}")
        return None

# =============================================================================
# 이미지 처리
# =============================================================================

def download_image(driver, city_name, product_number):
    """대표 이미지를 다운로드하고 저장"""
    # ... (기존 노트북의 download_image 함수 내용과 동일)
    if not DEFAULT_CONFIG["SAVE_IMAGES"] or not SELENIUM_AVAILABLE:
        return {'status': '비활성화'}

    # 이미지 URL 찾기 로직 (간소화)
    img_url = None
    try:
        img_element = driver.find_element(By.CSS_SELECTOR, ".main-image img, .hero-image img, .product-image img")
        img_url = img_element.get_attribute('src')
    except NoSuchElementException:
        return {'status': '이미지 URL 없음'}

    if not img_url:
        return {'status': '이미지 URL 없음'}

    # 파일명 및 경로 설정
    city_code = get_city_code(city_name)
    continent, country = get_city_info(city_name)
    img_filename = f"{city_code}_{product_number:04d}.jpg"
    img_dir = os.path.join("myrealtripthumb_img", continent, country, city_name)
    os.makedirs(img_dir, exist_ok=True)
    img_path = os.path.join(img_dir, img_filename)

    # 다운로드
    try:
        headers = {'User-Agent': DEFAULT_CONFIG['USER_AGENT']}
        response = requests.get(img_url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        with open(img_path, 'wb') as f:
            f.write(response.content)
        return {'status': '다운로드 완료', 'filename': img_filename, 'path': img_path}
    except Exception as e:
        return {'status': f'다운로드 실패: {e}'}

print("✅ file_handler.py 생성 완료: 파일 및 데이터 처리 시스템 준비 완료!")
