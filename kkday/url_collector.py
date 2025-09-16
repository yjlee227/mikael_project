import sys
import os
import time
import random
import inspect

# ======================================================================
# 🕵️ 스크립트 자체 진단 시작 🕵️
# ======================================================================
print("="*70)
print("🕵️  스크립트 자체 진단 시작 🕵️")
try:
    # Get the full path of the currently running script
    my_path = inspect.getframeinfo(inspect.currentframe()).filename
    print(f"   - 실행 중인 파일 경로: {my_path}")
    with open(my_path, 'r', encoding='utf-8') as f:
        for line in f:
            if 'TARGET_PRODUCTS' in line and not line.strip().startswith('#'):
                print(f"   - 파일에서 읽은 설정: {line.strip()}")
                break
except Exception as e:
    print(f"   - 진단 중 오류: {e}")
print("="*70)
# ======================================================================

# Add src to path to find the crawler modules
sys.path.append('./src')
sys.path.append('.')

try:
    from src.scraper.crawler import KKdayCrawler
    print("✅ KKday 모듈 로드 성공")
except ImportError as e:
    print(f"❌ KKday 모듈 로드 실패: {e}")
    raise

# ===== 🎯 사용자 설정 영역 =====
CITY_NAME = "치앙마이"
TARGET_PRODUCTS = 2  # 수집할 상품 URL 수
MAX_PAGES = 5       # URL을 충분히 수집하기 위해 페이지 수를 넉넉하게 설정
OUTPUT_FILE = "kkday_urls.txt"

print("="*70)
print("🚀 KKday URL 수집기 시작")
print("="*70)
print(f"   🏙️ 도시: {CITY_NAME}")
print(f"   🎯 목표 URL: {TARGET_PRODUCTS}개")
print(f"   📄 최대 페이지: {MAX_PAGES}개")
print(f"   💾 출력 파일: {OUTPUT_FILE}")

crawler = None
collected_urls = []

try:
    # 1. 크롤러 초기화
    print("\n🏗️ KKday 크롤러 초기화...")
    crawler = KKdayCrawler(city_name=CITY_NAME)
    if not crawler.initialize():
        raise Exception("크롤러 초기화 실패")

    # 2. 효율적인 URL 수집 (목표 수량 도달 시 중단)
    print("\n🔗 URL 수집 중...")
    collected_urls = crawler.collect_urls(
        max_pages=MAX_PAGES,
        max_products=TARGET_PRODUCTS
    )

    if not collected_urls:
        print("⚠️ 수집된 URL이 없습니다.")
    else:
        # 3. 파일에 저장
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            for url in collected_urls:
                f.write(url + '\n')
        
        print(f"✅ URL {len(collected_urls)}개를 '{OUTPUT_FILE}'에 성공적으로 저장했습니다.")

except Exception as e:
    print(f"❌ URL 수집 중 오류 발생: {e}")
finally:
    if crawler and crawler.driver:
        print("\n🌐 드라이버를 종료합니다.")
        crawler.driver.quit()
    print("🏁 URL 수집기 종료")