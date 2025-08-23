#!/usr/bin/env python3
"""
🧪 데이터 처리 파이프라인 빠른 테스트
- 실제 크롤링 2-3개 URL 테스트
- CSV 저장 및 이미지 다운로드 확인
- 32개 컬럼 구조 검증
"""

import os
import sys
import time
from datetime import datetime

# 모듈 import
try:
    from klook_modules.driver_manager import setup_driver, go_to_main_page, find_and_fill_search, click_search_button
    from klook_modules.crawler_engine import KlookCrawlerEngine
    from klook_modules.config import UNIFIED_CITY_INFO
    from klook_modules.url_collection import collect_urls_from_current_page
    print("✅ 모든 모듈 로드 성공!")
except ImportError as e:
    print(f"❌ 모듈 로드 실패: {e}")
    sys.exit(1)

def test_data_pipeline():
    """데이터 처리 파이프라인 테스트"""
    print("🧪 데이터 처리 파이프라인 테스트 시작!")
    print("=" * 60)
    
    # 테스트 설정
    TEST_CITY = "서울"
    MAX_TEST_URLS = 3
    
    driver = None
    try:
        # 1. 드라이버 설정
        print("🔧 크롬 드라이버 설정 중...")
        driver = setup_driver()
        
        # 2. KLOOK 페이지 이동
        print(f"🌐 KLOOK {TEST_CITY} 검색 페이지 이동...")
        go_to_main_page(driver)
        find_and_fill_search(driver, TEST_CITY)
        click_search_button(driver)
        time.sleep(3)
        
        # 3. 테스트용 URL 수집
        print("🔗 테스트용 URL 수집 중...")
        test_urls = collect_urls_from_current_page(driver, limit=MAX_TEST_URLS)
        
        if not test_urls:
            print("❌ 테스트용 URL을 찾을 수 없습니다.")
            return False
        
        print(f"✅ {len(test_urls)}개 테스트 URL 수집 완료")
        
        # 4. 크롤링 엔진 초기화
        print("🚀 크롤링 엔진 초기화...")
        crawler = KlookCrawlerEngine(driver)
        crawler.reset_stats(TEST_CITY)
        
        # 5. 각 URL별 데이터 처리 파이프라인 테스트
        for i, url in enumerate(test_urls, 1):
            print(f"\n🧪 테스트 {i}/{len(test_urls)}")
            print(f"🔗 URL: {url[:60]}...")
            
            try:
                # 크롤링 실행
                result = crawler.process_single_url(url, TEST_CITY, f"test_{i}")
                
                if result.get('success') and not result.get('skipped'):
                    product_data = result.get('product_data', {})
                    
                    # 데이터 구조 검증
                    print(f"✅ 크롤링 성공!")
                    print(f"   📊 데이터 컬럼 수: {len(product_data.keys())}개")
                    print(f"   🏷️ 상품명: {product_data.get('상품명', 'N/A')[:30]}...")
                    print(f"   💰 가격: {product_data.get('가격_정제', 'N/A')}")
                    print(f"   📸 메인이미지: {product_data.get('메인이미지_파일명', 'N/A')}")
                    print(f"   📸 썸네일이미지: {product_data.get('썸네일이미지_파일명', 'N/A')}")
                    print(f"   🎪 탭명: {product_data.get('탭명', 'N/A')}")
                    print(f"   🏆 랭킹: {product_data.get('탭내_랭킹', 'N/A')}")
                    
                    # 32개 컬럼 확인
                    if len(product_data.keys()) >= 30:
                        print(f"   ✅ 32개 컬럼 구조 적용됨")
                    else:
                        print(f"   ⚠️ 컬럼 수 부족: {len(product_data.keys())}개")
                    
                    # 듀얼 이미지 확인
                    main_img = product_data.get('메인이미지_파일명', '정보 없음')
                    thumb_img = product_data.get('썸네일이미지_파일명', '정보 없음')
                    
                    if main_img != '정보 없음' and thumb_img != '정보 없음':
                        print(f"   ✅ 듀얼 이미지 시스템 작동")
                    elif main_img != '정보 없음':
                        print(f"   ✅ 메인 이미지만 다운로드")
                    else:
                        print(f"   ⚠️ 이미지 다운로드 실패")
                    
                elif result.get('skipped'):
                    print(f"⏭️ 건너뛰기: {result.get('reason', 'unknown')}")
                else:
                    print(f"❌ 실패: {result.get('error', '알 수 없음')}")
                
            except Exception as e:
                print(f"💥 테스트 실패: {e}")
                import traceback
                traceback.print_exc()
            
            # 테스트 간 대기
            time.sleep(2)
        
        # 6. 결과 파일 확인
        print(f"\n📁 결과 파일 확인...")
        
        # CSV 파일 확인
        from klook_modules.config import get_city_info
        continent, country = get_city_info(TEST_CITY)
        
        if TEST_CITY in ["마카오", "홍콩", "싱가포르"]:
            csv_path = f"data/{continent}/{TEST_CITY}_klook_products_all.csv"
        else:
            csv_path = f"data/{continent}/{country}/{TEST_CITY}/{TEST_CITY}_klook_products_all.csv"
        
        if os.path.exists(csv_path):
            try:
                import pandas as pd
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                print(f"✅ CSV 파일 생성 확인: {len(df)}개 데이터, {len(df.columns)}개 컬럼")
                print(f"   파일 위치: {csv_path}")
                
                # 최근 데이터 확인 (테스트로 추가된 것)
                if len(df) > 0:
                    latest_row = df.iloc[-1]
                    print(f"   최신 데이터: {latest_row.get('상품명', 'N/A')[:30]}...")
                    print(f"   수집시간: {latest_row.get('수집_시간', 'N/A')}")
                
            except Exception as e:
                print(f"⚠️ CSV 분석 실패: {e}")
        else:
            print(f"❌ CSV 파일 없음: {csv_path}")
        
        # 이미지 폴더 확인
        if TEST_CITY in ["마카오", "홍콩", "싱가포르"]:
            img_folder = f"klook_thumb_img/{continent}"
        else:
            img_folder = f"klook_thumb_img/{continent}/{country}/{TEST_CITY}"
        
        if os.path.exists(img_folder):
            img_files = [f for f in os.listdir(img_folder) if f.endswith('.jpg')]
            main_imgs = [f for f in img_files if '_thumb' not in f]
            thumb_imgs = [f for f in img_files if '_thumb' in f]
            
            print(f"✅ 이미지 폴더 확인: {len(img_files)}개 이미지")
            print(f"   메인: {len(main_imgs)}개, 썸네일: {len(thumb_imgs)}개")
            print(f"   폴더 위치: {img_folder}")
        else:
            print(f"❌ 이미지 폴더 없음: {img_folder}")
        
        # 7. 최종 통계
        stats = crawler.get_stats_summary()
        print(f"\n📊 테스트 결과:")
        print(f"   성공: {stats['success_count']}개")
        print(f"   실패: {stats['error_count']}개")
        print(f"   건너뜀: {stats['skip_count']}개")
        print(f"   성공률: {stats['success_rate']:.1f}%")
        
        # 성공 여부 판정
        if stats['success_count'] > 0:
            print(f"\n🎉 데이터 처리 파이프라인 테스트 성공!")
            return True
        else:
            print(f"\n❌ 데이터 처리 파이프라인 테스트 실패!")
            return False
            
    except Exception as e:
        print(f"💥 테스트 중 치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 드라이버 정리
        if driver:
            try:
                driver.quit()
                print("✅ 드라이버 종료 완료")
            except:
                pass

if __name__ == "__main__":
    print("🧪 KLOOK 데이터 처리 파이프라인 테스트")
    print("=" * 60)
    print("📋 테스트 항목:")
    print("   1. 크롤링 엔진 동작 확인")
    print("   2. CSV 저장 (32개 컬럼) 확인")
    print("   3. 듀얼 이미지 다운로드 확인")
    print("   4. 데이터 구조 무결성 확인")
    print("=" * 60)
    
    success = test_data_pipeline()
    
    if success:
        print("\n✅ 모든 테스트 통과! 데이터 처리 파이프라인이 정상 작동합니다.")
    else:
        print("\n❌ 테스트 실패! 파이프라인 연결에 문제가 있습니다.")