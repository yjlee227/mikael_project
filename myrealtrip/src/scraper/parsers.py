"""
데이터 추출 및 정제 시스템
- 웹 요소에서 데이터 추출
- 가격, 평점, 텍스트 정제
"""

import re
import time
import random

# Selenium 및 관련 라이브러리 import
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# 임시 CONFIG (나중에 src.config에서 가져오도록 수정)
CONFIG = {
    "WAIT_TIMEOUT": 10,
}

# =============================================================================
# 데이터 추출 함수
# =============================================================================

def get_product_name(driver):
    """상품명을 추출합니다."""
    if not SELENIUM_AVAILABLE: return "상품명 추출 불가"
    # ... (기존 노트북의 get_product_name 함수 로직)
    try:
        return driver.find_element(By.CSS_SELECTOR, "h1").text
    except NoSuchElementException:
        return "상품명 없음"

def get_price(driver):
    """가격을 추출합니다."""
    if not SELENIUM_AVAILABLE: return "가격 정보 없음"
    # ... (기존 노트북의 get_price 함수 로직)
    try:
        return driver.find_element(By.CSS_SELECTOR, ".price, [class*='price']").text
    except NoSuchElementException:
        return "가격 정보 없음"

def get_rating(driver):
    """평점을 추출합니다."""
    if not SELENIUM_AVAILABLE: return "평점 정보 없음"
    # ... (기존 노트북의 get_rating 함수 로직)
    try:
        return driver.find_element(By.CSS_SELECTOR, ".rating, [class*='rating']").text
    except NoSuchElementException:
        return "평점 정보 없음"

def get_review_count(driver):
    """리뷰 수를 추출합니다."""
    if not SELENIUM_AVAILABLE: return "0"
    # ... (기존 노트북의 get_review_count 함수 로직)
    try:
        review_text = driver.find_element(By.XPATH, "//span[contains(text(), '리뷰') or contains(text(), '후기')]").text
        numbers = re.findall(r'\d+', review_text)
        return numbers[0] if numbers else "0"
    except NoSuchElementException:
        return "0"

# =============================================================================
# 데이터 정제 함수
# =============================================================================

def clean_price(price_text):
    """가격 텍스트를 정제하여 숫자만 남깁니다."""
    if not price_text or price_text == "정보 없음":
        return "정보 없음"
    numbers = re.findall(r'\d+', price_text.replace(",", ""))
    return numbers[0] if numbers else "정보 없음"

def clean_rating(rating_text):
    """평점 텍스트를 정제하여 숫자만 남깁니다."""
    if not rating_text or rating_text == "정보 없음":
        return "정보 없음"
    numbers = re.findall(r'\d+\.?\d*', rating_text)
    return numbers[0] if numbers else "정보 없음"

print("✅ parsers.py 생성 완료: 데이터 추출 및 정제 시스템 준비 완료!")
