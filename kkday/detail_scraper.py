# detail_scraper.py
import sys
import os
import time
import random

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
CITY_NAME = "방콕"
INPUT_FILE = "kkday_urls.txt"

print("="*70)
print("🚀 KKday 상세 정보 스크레이퍼 시작")
print("="*70)
print(f"   🏙️ 도시: {CITY_NAME}")
print(f"   💾 입력 파일: {INPUT_FILE}")

# 1. URL 파일 읽기
if not os.path.exists(INPUT_FILE):
    print(f"❌ URL 파일 '{INPUT_FILE}'을 찾을 수 없습니다.")
    print("💡 먼저 url_collector.py를 실행하여 URL을 수집하세요.")
    sys.exit()

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    urls_to_scrape = [line.strip() for line in f if line.strip()]

if not urls_to_scrape:
    print("⚠️ URL 파일에 수집할 URL이 없습니다.")
    sys.exit()

print(f"✅ '{INPUT_FILE}'에서 {len(urls_to_scrape)}개의 URL을 읽었습니다.")

crawler = None
try:
    # 2. 크롤러 초기화
    print("\n🏗️ KKday 크롤러 초기화...")
    crawler = KKdayCrawler(city_name=CITY_NAME)
    if not crawler.initialize():
        raise Exception("크롤러 초기화 실패")

    # 3. 배치 크롤링 실행
    print("\n📦 상세 정보 스크래핑 시작...")
    success = crawler.crawl_products_batch(urls_to_scrape)

    # 4. [추가] 국가별 통합 CSV 자동 생성
    if success:
        from src.utils.file_handler import auto_create_country_csv_after_crawling
        auto_create_country_csv_after_crawling(CITY_NAME)

except Exception as e:
    print(f"❌ 스크래핑 중 오류 발생: {e}")
finally:
    if crawler and crawler.driver:
        print("\n🌐 드라이버를 종료합니다.")
        crawler.driver.quit()
    print("🏁 상세 정보 스크레이퍼 종료")
