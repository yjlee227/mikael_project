#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 KLOOK 크롤링 시스템 검증 테스트
- 32컬럼 구조 검증
- 듀얼 이미지 시스템 검증
- 랭킹 매니저 검증
- 디버그 로그 확인
"""

import sys
import os
import time
from datetime import datetime

# 모듈 경로 추가
sys.path.append('./klook_modules')

def test_imports():
    """필수 모듈 import 테스트"""
    print("🔧 === 모듈 Import 테스트 ===")
    
    try:
        from klook_modules.config import CONFIG, get_city_code
        print("   ✅ config 모듈: OK")
    except Exception as e:
        print(f"   ❌ config 모듈: {e}")
        return False
        
    try:
        from klook_modules.data_handler import create_product_data_structure, get_dual_image_urls_klook
        print("   ✅ data_handler 모듈: OK")
    except Exception as e:
        print(f"   ❌ data_handler 모듈: {e}")
        return False
        
    try:
        from klook_modules.ranking_manager import ranking_manager
        print("   ✅ ranking_manager 모듈: OK")
    except Exception as e:
        print(f"   ❌ ranking_manager 모듈: {e}")
        return False
        
    try:
        from klook_modules.crawler_engine import KlookCrawlerEngine, quick_crawl_test
        print("   ✅ crawler_engine 모듈: OK")
    except Exception as e:
        print(f"   ❌ crawler_engine 모듈: {e}")
        return False
    
    return True

def test_33_column_structure():
    """33컬럼 구조 테스트"""
    print("\n📊 === 33컬럼 구조 테스트 ===")
    
    try:
        from klook_modules.data_handler import create_product_data_structure
        
        # 테스트 데이터로 33컬럼 구조 생성
        test_data = create_product_data_structure(
            product_number=1,
            product_name="테스트 상품",
            price="29,600원",
            image_filename="test.jpg",
            url="https://test.com",
            city_name="테스트시티",
            additional_data={
                "위치": "테스트 위치",
                "하이라이트": "테스트 하이라이트"
            },
            dual_images={"main": "main.jpg", "thumb": "thumb.jpg"},
            tab_info={"tab_name": "전체", "ranking": 1}
        )
        
        columns = list(test_data.keys())
        print(f"   📋 생성된 컬럼 수: {len(columns)}")
        
        if len(columns) == 33:
            print("   ✅ 33컬럼 구조: 정상")
            print(f"   📋 컬럼 목록:")
            for i, col in enumerate(columns, 1):
                print(f"      {i:2d}. {col}")
        else:
            print(f"   ❌ 33컬럼 구조: 실패 (현재 {len(columns)}개)")
            
        return len(columns) == 33
        
    except Exception as e:
        print(f"   ❌ 33컬럼 구조 테스트 실패: {e}")
        return False

def test_ranking_manager():
    """랭킹 매니저 테스트"""
    print("\n🏆 === 랭킹 매니저 테스트 ===")
    
    try:
        from klook_modules.ranking_manager import ranking_manager
        
        test_city = "테스트시티"
        test_url = "https://test-url.com"
        test_tab = "테스트탭"
        
        # 랭킹 저장 테스트
        ranking_manager.save_tab_ranking(test_tab, test_url, 5, test_city)
        print("   ✅ 랭킹 저장: 성공")
        
        # 크롤링 여부 확인 테스트
        should_crawl = ranking_manager.should_crawl_url(test_url, test_city)
        print(f"   ✅ 크롤링 여부 확인: {should_crawl}")
        
        # URL 랭킹 조회 테스트
        url_rankings = ranking_manager.get_url_rankings(test_url, test_city)
        print(f"   ✅ URL 랭킹 조회: {bool(url_rankings)}")
        
        # 크롤링 완료 표시 테스트
        ranking_manager.mark_url_crawled(test_url, test_city)
        print("   ✅ 크롤링 완료 표시: 성공")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 랭킹 매니저 테스트 실패: {e}")
        return False

def test_selenium_availability():
    """Selenium 가용성 테스트"""
    print("\n🌐 === Selenium 가용성 테스트 ===")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("   ✅ Selenium import: 성공")
        
        # Chrome 옵션 설정 테스트
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        print("   ✅ Chrome 옵션 설정: 성공")
        
        # 실제 드라이버는 생성하지 않음 (환경에 따라 실패할 수 있음)
        print("   ℹ️ WebDriver 생성은 실제 크롤링에서 테스트됩니다")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Selenium 테스트 실패: {e}")
        return False

def test_file_structure():
    """파일 구조 테스트"""
    print("\n📁 === 파일 구조 테스트 ===")
    
    required_dirs = [
        "data",
        "ranking_data", 
        "klook_thumb_img",
        "url_collected",
        "hash_index"
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}: 존재함")
        else:
            print(f"   ❌ {dir_name}: 없음")
            all_exist = False
    
    return all_exist

def main():
    """메인 테스트 실행"""
    print("🧪 ================================")
    print("🧪 KLOOK 크롤링 시스템 검증 테스트")
    print("🧪 ================================")
    print(f"🕐 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 1. 모듈 Import 테스트
    results["imports"] = test_imports()
    
    # 2. 33컬럼 구조 테스트
    results["33_columns"] = test_33_column_structure()
    
    # 3. 랭킹 매니저 테스트
    results["ranking_manager"] = test_ranking_manager()
    
    # 4. Selenium 가용성 테스트
    results["selenium"] = test_selenium_availability()
    
    # 5. 파일 구조 테스트
    results["file_structure"] = test_file_structure()
    
    # 결과 요약
    print("\n🎯 === 테스트 결과 요약 ===")
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 전체 결과: {passed_tests}/{total_tests} 테스트 통과")
    success_rate = (passed_tests / total_tests) * 100
    print(f"📈 성공률: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 시스템 검증 성공! 크롤링 준비 완료")
    else:
        print("⚠️ 일부 테스트 실패. 문제 해결 필요")
    
    print(f"🕐 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()