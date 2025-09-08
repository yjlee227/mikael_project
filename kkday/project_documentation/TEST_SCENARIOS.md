# KKday 크롤링 시스템 - 테스트 시나리오 및 검증 가이드

## 🧪 테스트 개요

이 문서는 Klook에서 KKday로 시스템 전환 과정에서 수행해야 할 모든 테스트 시나리오를 정의합니다. 각 테스트는 구체적인 실행 방법과 성공 기준을 포함합니다.

## 🎯 테스트 목표

### 주요 검증 항목
- **기능 완정성**: 모든 크롤링 기능이 KKday에서 정상 작동
- **데이터 정확성**: 추출되는 데이터의 품질 및 일관성 
- **성능 유지**: 기존 Klook 시스템 대비 성능 저하 없음
- **안정성 확보**: 다양한 환경에서 안정적인 동작

## 📋 테스트 분류 체계

### Level 1: 단위 테스트 (Unit Tests)
각 모듈별 개별 기능 검증

### Level 2: 통합 테스트 (Integration Tests)  
모듈 간 연동 및 전체 워크플로우 검증

### Level 3: 시나리오 테스트 (End-to-End Tests)
실제 사용 시나리오 기반 종합 검증

### Level 4: 성능 테스트 (Performance Tests)
대용량 데이터 및 장시간 실행 안정성 검증

## 🔬 Level 1: 단위 테스트 시나리오

### 1.1 config.py 모듈 테스트

#### 테스트 시나리오: 도시 정보 조회
```python
def test_config_city_lookup():
    """도시 코드 및 정보 조회 기능 테스트"""
    
    # Given: 테스트 도시명들
    test_cities = ["서울", "도쿄", "방콕", "파리"]
    
    # When & Then: 각 도시별 검증
    for city in test_cities:
        city_info = get_city_info(city)
        
        assert city_info is not None, f"{city} 정보를 찾을 수 없음"
        assert 'city_code' in city_info, f"{city} 도시 코드 누락"
        assert 'country' in city_info, f"{city} 국가 정보 누락"
        assert len(city_info['city_code']) == 3, f"{city} 도시 코드 형식 오류"
        
        print(f"✅ {city}: {city_info['city_code']} ({city_info['country']})")

# 예상 결과:
# ✅ 서울: SEL (대한민국)
# ✅ 도쿄: TYO (일본)
# ✅ 방콕: BKK (태국)
# ✅ 파리: PAR (프랑스)
```

#### 테스트 시나리오: KKday 설정 검증
```python
def test_kkday_configuration():
    """KKday 전용 설정값 검증"""
    
    from src.config import CONFIG
    
    # 플랫폼 정보 검증
    assert CONFIG['platform'] == 'KKday'
    assert CONFIG['base_url'] == 'https://www.kkday.com'
    assert CONFIG['data_source'] == 'KKday'
    
    # Klook 관련 설정 제거 확인
    config_str = str(CONFIG)
    assert 'klook' not in config_str.lower(), "Klook 관련 설정 잔존"
    assert 'KLOOK' not in config_str, "KLOOK 대문자 잔존"
    
    print("✅ KKday 설정 검증 완료")
```

### 1.2 utils/ 모듈 테스트

#### 테스트 시나리오: city_manager 별칭 처리
```python
def test_city_alias_mapping():
    """도시명 별칭 매핑 테스트"""
    
    from src.utils.city_manager import normalize_city_name
    
    # 별칭 매핑 테스트 케이스
    test_cases = [
        ("토쿄", "도쿄"),
        ("북경", "베이징"),  
        ("청도", "칭따오"),
        ("KL", "쿠알라룸푸르"),
        ("서울", "서울")  # 자기 자신
    ]
    
    for input_city, expected in test_cases:
        result = normalize_city_name(input_city)
        assert result == expected, f"{input_city} → {result} (예상: {expected})"
        print(f"✅ {input_city} → {result}")
```

#### 테스트 시나리오: file_handler KKday 전용 함수
```python
def test_file_handler_kkday_functions():
    """file_handler의 KKday 전용 함수 테스트"""
    
    from src.utils.file_handler import save_to_csv_kkday, get_csv_path_kkday
    
    # CSV 경로 생성 테스트
    test_city = "서울"
    csv_path = get_csv_path_kkday(test_city)
    
    assert 'kkday' in csv_path.lower(), "파일명에 kkday 누락"
    assert 'klook' not in csv_path.lower(), "파일명에 klook 잔존"
    assert test_city in csv_path, "도시명 누락"
    
    # 테스트 데이터로 CSV 저장
    test_data = {
        "번호": "1",
        "상품명": "테스트 상품",
        "가격": "₩50,000",
        "URL": "https://www.kkday.com/ko/product/12345",
        "데이터소스": "KKday"
    }
    
    result = save_to_csv_kkday(test_data, test_city)
    assert result == True, "CSV 저장 실패"
    
    print(f"✅ CSV 저장: {csv_path}")
```

### 1.3 scraper/ 모듈 테스트

#### 테스트 시나리오: KKdayCrawler 초기화
```python
def test_kkday_crawler_initialization():
    """KKdayCrawler 클래스 초기화 테스트"""
    
    from src.scraper.crawler import KKdayCrawler
    
    # 크롤러 인스턴스 생성
    crawler = KKdayCrawler("서울")
    
    assert crawler.city_name == "서울"
    assert crawler.platform == "KKday"
    assert hasattr(crawler, 'collect_urls_kkday')
    assert hasattr(crawler, 'crawl_product_kkday')
    
    # Klook 관련 속성/메서드 제거 확인
    class_methods = dir(crawler)
    klook_methods = [m for m in class_methods if 'klook' in m.lower()]
    assert len(klook_methods) == 0, f"Klook 메서드 잔존: {klook_methods}"
    
    print("✅ KKdayCrawler 초기화 완료")
```

## 🔗 Level 2: 통합 테스트 시나리오

### 2.1 모듈 간 연동 테스트

#### 테스트 시나리오: config ↔ crawler 연동
```python
def test_config_crawler_integration():
    """config 모듈과 crawler 모듈 연동 테스트"""
    
    from src.config import get_city_info
    from src.scraper.crawler import KKdayCrawler
    
    test_city = "서울"
    
    # Step 1: config에서 도시 정보 조회
    city_info = get_city_info(test_city)
    assert city_info is not None
    
    # Step 2: crawler에 도시 정보 전달
    crawler = KKdayCrawler(test_city)
    assert crawler.city_code == city_info['city_code']
    
    # Step 3: 통합 동작 확인
    initialization_result = crawler.initialize()
    assert initialization_result == True
    
    print(f"✅ config ↔ crawler 연동: {test_city} ({city_info['city_code']})")
```

#### 테스트 시나리오: crawler ↔ file_handler 연동
```python
def test_crawler_filehandler_integration():
    """crawler와 file_handler 연동 테스트"""
    
    from src.scraper.crawler import KKdayCrawler
    from src.utils.file_handler import get_csv_path_kkday
    import os
    
    test_city = "서울"
    crawler = KKdayCrawler(test_city)
    
    # Step 1: 크롤러에서 데이터 생성 (시뮬레이션)
    mock_product_data = {
        "번호": "TEST001",
        "상품명": "서울 시티투어",
        "가격": "₩75,000",
        "URL": "https://www.kkday.com/ko/product/test001",
        "데이터소스": "KKday"
    }
    
    # Step 2: file_handler로 저장
    save_result = crawler.save_product_data(mock_product_data)
    assert save_result == True
    
    # Step 3: 파일 생성 확인
    csv_path = get_csv_path_kkday(test_city)
    assert os.path.exists(csv_path), f"CSV 파일 미생성: {csv_path}"
    
    print(f"✅ crawler ↔ file_handler 연동 완료")
```

### 2.2 전체 워크플로우 테스트

#### 테스트 시나리오: 단일 상품 크롤링 전체 과정
```python
def test_single_product_crawling_workflow():
    """단일 상품 크롤링 전체 워크플로우 테스트"""
    
    from src.scraper.crawler import KKdayCrawler
    import time
    
    # Given: 테스트 설정
    test_city = "서울"
    max_products = 1
    
    # When: 전체 크롤링 과정 실행
    start_time = time.time()
    
    try:
        # Step 1: 크롤러 초기화
        crawler = KKdayCrawler(test_city)
        init_result = crawler.initialize()
        assert init_result == True, "크롤러 초기화 실패"
        
        # Step 2: URL 수집
        urls = crawler.collect_urls_kkday(max_pages=1)
        assert len(urls) > 0, "URL 수집 실패"
        print(f"📊 수집된 URL: {len(urls)}개")
        
        # Step 3: 첫 번째 상품 크롤링
        first_url = urls[0]
        crawl_result = crawler.crawl_product_kkday(first_url, rank=1)
        assert crawl_result == True, "상품 크롤링 실패"
        
        # Step 4: 데이터 검증
        assert crawler.last_product_data is not None
        assert '상품명' in crawler.last_product_data
        assert '가격' in crawler.last_product_data
        assert 'URL' in crawler.last_product_data
        
        end_time = time.time()
        elapsed = round(end_time - start_time, 2)
        
        print(f"✅ 단일 상품 크롤링 완료 ({elapsed}초)")
        print(f"📋 상품명: {crawler.last_product_data.get('상품명', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 크롤링 실패: {e}")
        assert False, f"워크플로우 실패: {e}"
```

## 🚀 Level 3: 시나리오 테스트 (E2E)

### 3.1 실제 사용 시나리오 테스트

#### 시나리오: 서울 여행상품 10개 수집
```python
def test_seoul_10_products_scenario():
    """실제 사용 시나리오: 서울 상품 10개 수집"""
    
    from src.scraper.crawler import KKdayCrawler
    from src.utils.file_handler import get_csv_path_kkday
    import pandas as pd
    import os
    
    # 테스트 파라미터
    TARGET_CITY = "서울"
    TARGET_COUNT = 10
    MAX_PAGES = 3
    
    print(f"🚀 시나리오 시작: {TARGET_CITY} 상품 {TARGET_COUNT}개 수집")
    
    try:
        # Step 1: 환경 준비
        crawler = KKdayCrawler(TARGET_CITY)
        assert crawler.initialize() == True
        
        # Step 2: URL 대량 수집
        start_time = time.time()
        all_urls = crawler.collect_urls_kkday(max_pages=MAX_PAGES)
        collect_time = time.time() - start_time
        
        assert len(all_urls) >= TARGET_COUNT, f"URL 수집 부족: {len(all_urls)}/{TARGET_COUNT}"
        print(f"📊 URL 수집 완료: {len(all_urls)}개 ({collect_time:.1f}초)")
        
        # Step 3: 상품별 크롤링
        successful_products = 0
        failed_products = 0
        
        for i, url in enumerate(all_urls[:TARGET_COUNT]):
            print(f"🔄 진행중 ({i+1}/{TARGET_COUNT}): {url[:50]}...")
            
            crawl_start = time.time()
            result = crawler.crawl_product_kkday(url, rank=i+1)
            crawl_time = time.time() - crawl_start
            
            if result:
                successful_products += 1
                print(f"✅ 성공 ({crawl_time:.1f}초)")
            else:
                failed_products += 1
                print(f"❌ 실패 ({crawl_time:.1f}초)")
            
            # 자연스러운 대기 (2-4초)
            time.sleep(random.uniform(2, 4))
        
        # Step 4: 결과 검증
        total_time = time.time() - start_time
        success_rate = (successful_products / TARGET_COUNT) * 100
        
        assert success_rate >= 80, f"성공률 부족: {success_rate}% (최소 80% 필요)"
        
        # Step 5: CSV 파일 검증
        csv_path = get_csv_path_kkday(TARGET_CITY)
        assert os.path.exists(csv_path), "CSV 파일 미생성"
        
        df = pd.read_csv(csv_path)
        assert len(df) >= successful_products, "CSV 데이터 누락"
        
        print(f"🎉 시나리오 완료!")
        print(f"📊 성공률: {success_rate}% ({successful_products}/{TARGET_COUNT})")
        print(f"⏱️ 총 시간: {total_time/60:.1f}분")
        print(f"📁 저장 위치: {csv_path}")
        
    except AssertionError as e:
        print(f"❌ 시나리오 실패: {e}")
        raise
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        raise
```

#### 시나리오: 다중 도시 크롤링
```python
def test_multi_city_scenario():
    """다중 도시 크롤링 시나리오"""
    
    # 테스트 도시 목록 (난이도 순)
    TEST_CITIES = [
        ("서울", 3),      # 한국어, 쉬움
        ("도쿄", 3),      # 일본, 중간  
        ("방콕", 5),      # 태국, 중간
        ("파리", 3)       # 유럽, 어려움
    ]
    
    results = {}
    
    for city, target_count in TEST_CITIES:
        print(f"\n🌏 {city} 크롤링 시작 (목표: {target_count}개)")
        
        try:
            crawler = KKdayCrawler(city)
            
            # 각 도시별 크롤링
            success_count = crawler.run_crawling(
                max_products=target_count,
                max_pages=2
            )
            
            results[city] = {
                'target': target_count,
                'success': success_count,
                'rate': round((success_count/target_count)*100, 1)
            }
            
            print(f"✅ {city} 완료: {success_count}/{target_count} ({results[city]['rate']}%)")
            
        except Exception as e:
            results[city] = {
                'target': target_count, 
                'success': 0,
                'rate': 0,
                'error': str(e)
            }
            print(f"❌ {city} 실패: {e}")
    
    # 전체 결과 검증
    total_success = sum(r['success'] for r in results.values())
    total_target = sum(r['target'] for r in results.values())
    overall_rate = (total_success / total_target) * 100
    
    print(f"\n📊 전체 결과:")
    for city, result in results.items():
        status = "✅" if result['rate'] >= 70 else "❌" 
        print(f"{status} {city}: {result['rate']}%")
    
    print(f"🎯 전체 성공률: {overall_rate:.1f}%")
    
    assert overall_rate >= 75, f"전체 성공률 부족: {overall_rate}% (최소 75% 필요)"
```

### 3.2 예외 상황 시나리오

#### 시나리오: 네트워크 오류 대응
```python
def test_network_error_scenario():
    """네트워크 오류 상황 대응 테스트"""
    
    from src.scraper.crawler import KKdayCrawler
    from unittest.mock import patch
    import requests
    
    crawler = KKdayCrawler("서울")
    
    # 네트워크 오류 시뮬레이션
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.ConnectionError("네트워크 연결 실패")
        
        # 자동 재시도 메커니즘 테스트
        result = crawler.crawl_with_retry("https://www.kkday.com/test")
        
        # 최대 재시도 후에도 실패하면 False 반환
        assert result == False
        print("✅ 네트워크 오류 대응 확인")
```

#### 시나리오: 잘못된 URL 처리
```python
def test_invalid_url_scenario():
    """잘못된 URL 입력 시 처리 테스트"""
    
    from src.scraper.crawler import KKdayCrawler
    
    crawler = KKdayCrawler("서울")
    
    invalid_urls = [
        "https://www.kkday.com/nonexistent",
        "https://invalid-domain.com/product/123", 
        "",
        None,
        "not-a-url"
    ]
    
    for url in invalid_urls:
        result = crawler.crawl_product_kkday(url, rank=1)
        assert result == False, f"잘못된 URL에서 성공 반환: {url}"
        print(f"✅ 잘못된 URL 처리: {url}")
```

## ⚡ Level 4: 성능 테스트 시나리오

### 4.1 부하 테스트

#### 시나리오: 대용량 URL 처리 (100개)
```python
def test_large_scale_crawling():
    """대용량 크롤링 성능 테스트 (100개 상품)"""
    
    import psutil
    import time
    from src.scraper.crawler import KKdayCrawler
    
    # 성능 측정 시작
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    start_time = time.time()
    
    TARGET_COUNT = 100
    crawler = KKdayCrawler("서울")
    
    print(f"🚀 대용량 테스트 시작: {TARGET_COUNT}개 상품")
    print(f"📊 시작 메모리: {start_memory:.1f}MB")
    
    try:
        # URL 대량 수집
        urls = crawler.collect_urls_kkday(max_pages=10)
        assert len(urls) >= TARGET_COUNT, f"URL 수집 부족: {len(urls)}"
        
        # 배치 크롤링 (10개씩 처리)
        batch_size = 10
        total_processed = 0
        
        for i in range(0, min(TARGET_COUNT, len(urls)), batch_size):
            batch_urls = urls[i:i+batch_size]
            batch_start = time.time()
            
            # 배치 처리
            for j, url in enumerate(batch_urls):
                result = crawler.crawl_product_kkday(url, rank=i+j+1)
                if result:
                    total_processed += 1
                
                # 메모리 사용량 모니터링
                if (i+j+1) % 20 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    print(f"📊 진행률: {i+j+1}/{TARGET_COUNT}, 메모리: {current_memory:.1f}MB")
            
            batch_time = time.time() - batch_start
            print(f"✅ 배치 {i//batch_size + 1} 완료 ({batch_time:.1f}초, {len(batch_urls)}개)")
            
            # 메모리 정리
            if i % 50 == 0:
                import gc
                gc.collect()
        
        # 성능 측정 완료
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024
        
        total_time = end_time - start_time
        memory_increase = end_memory - start_memory
        success_rate = (total_processed / TARGET_COUNT) * 100
        
        # 성능 기준 검증
        assert success_rate >= 85, f"성공률 기준 미달: {success_rate}%"
        assert memory_increase <= 2000, f"메모리 사용량 초과: {memory_increase}MB"  # 2GB 제한
        assert total_time <= 3600, f"시간 초과: {total_time}초 (1시간 제한)"
        
        print(f"🎉 대용량 테스트 완료!")
        print(f"📊 성공률: {success_rate}%")
        print(f"⏱️ 소요시간: {total_time/60:.1f}분") 
        print(f"💾 메모리 증가: {memory_increase:.1f}MB")
        print(f"🚀 평균 속도: {total_processed/(total_time/60):.1f}개/분")
        
    except Exception as e:
        print(f"❌ 대용량 테스트 실패: {e}")
        raise
```

### 4.2 장시간 안정성 테스트

#### 시나리오: 6시간 연속 실행
```python
def test_long_running_stability():
    """장시간 연속 실행 안정성 테스트"""
    
    from src.scraper.crawler import KKdayCrawler
    import time
    import datetime
    
    # 6시간 = 21600초
    TEST_DURATION = 6 * 60 * 60  
    CHECK_INTERVAL = 30 * 60     # 30분마다 체크
    
    start_time = time.time()
    crawler = KKdayCrawler("서울")
    
    print(f"🕐 장시간 안정성 테스트 시작 (6시간)")
    print(f"⏰ 시작 시간: {datetime.datetime.now()}")
    
    error_count = 0
    success_count = 0
    check_points = []
    
    while time.time() - start_time < TEST_DURATION:
        try:
            # 주기적으로 크롤링 실행 (매 5분)
            urls = crawler.collect_urls_kkday(max_pages=1)
            
            if urls:
                result = crawler.crawl_product_kkday(urls[0], rank=1)
                if result:
                    success_count += 1
                else:
                    error_count += 1
            
            # 30분마다 상태 체크
            current_time = time.time()
            if len(check_points) == 0 or current_time - check_points[-1] >= CHECK_INTERVAL:
                check_points.append(current_time)
                elapsed_hours = (current_time - start_time) / 3600
                
                print(f"📊 {elapsed_hours:.1f}시간 경과 - 성공: {success_count}, 실패: {error_count}")
                
                # 오류율 체크
                if success_count + error_count > 0:
                    error_rate = (error_count / (success_count + error_count)) * 100
                    assert error_rate <= 10, f"오류율 초과: {error_rate}%"
            
            # 5분 대기
            time.sleep(5 * 60)
            
        except KeyboardInterrupt:
            print("🛑 사용자 중단")
            break
        except Exception as e:
            error_count += 1
            print(f"⚠️ 오류 발생: {e}")
            
            # 연속 오류 체크
            assert error_count <= 20, f"연속 오류 한계 초과: {error_count}"
    
    total_time = time.time() - start_time
    final_error_rate = (error_count / max(success_count + error_count, 1)) * 100
    
    print(f"🏁 장시간 테스트 완료")
    print(f"⏱️ 실행 시간: {total_time/3600:.1f}시간")
    print(f"📊 성공: {success_count}, 실패: {error_count}")
    print(f"📈 최종 성공률: {100-final_error_rate:.1f}%")
    
    assert final_error_rate <= 5, f"최종 오류율 초과: {final_error_rate}%"
```

## 📊 테스트 실행 및 결과 관리

### 테스트 실행 스케줄

#### 개발 중 테스트 (매일)
```bash
# 빠른 테스트 (5분 이내)
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -k "not slow" -v
```

#### 주간 테스트 (주말)
```bash
# 전체 테스트 스위트 (2-3시간)
python -m pytest tests/ -v --html=report.html
python test_scenarios.py --scenario=multi_city
```

#### 배포 전 테스트 (수동)
```bash
# 성능 및 안정성 테스트 (6-8시간) 
python test_scenarios.py --scenario=large_scale
python test_scenarios.py --scenario=long_running
```

### 테스트 결과 리포팅

#### 자동 리포트 생성
```python
def generate_test_report(test_results):
    """테스트 결과 리포트 자동 생성"""
    
    report = f"""
# KKday 크롤링 시스템 테스트 리포트

**실행 시간**: {datetime.datetime.now()}
**총 테스트**: {test_results['total']}
**성공**: {test_results['passed']} 
**실패**: {test_results['failed']}
**성공률**: {(test_results['passed']/test_results['total'])*100:.1f}%

## 상세 결과

### ✅ 통과한 테스트
{chr(10).join(test_results['passed_tests'])}

### ❌ 실패한 테스트  
{chr(10).join(test_results['failed_tests'])}

### 📊 성능 지표
- 평균 응답시간: {test_results['avg_response_time']:.2f}초
- 메모리 사용량: {test_results['memory_usage']:.1f}MB
- 처리율: {test_results['throughput']:.1f}개/분

## 권장사항
{chr(10).join(test_results['recommendations'])}
"""
    
    # 리포트 파일 저장
    with open('test_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report
```

## ⚠️ 테스트 시 주의사항

### 윤리적 고려사항
- **요청 빈도**: 5초 이상 간격 유지
- **동시 연결**: 최대 1개 세션만 사용
- **테스트 데이터**: 실제 상용 서비스에 영향 없도록 제한

### 기술적 제약사항  
- **브라우저 버전**: Chrome 120+ 필수
- **네트워크**: 안정적인 인터넷 연결 필요
- **시스템 리소스**: 최소 4GB RAM, 권장 8GB

### 테스트 데이터 관리
- **임시 파일**: 테스트 후 자동 정리
- **CSV 백업**: 기존 데이터 덮어쓰기 방지  
- **이미지 폴더**: 테스트용 별도 디렉터리 사용

---

**문서 버전**: v1.0  
**최종 업데이트**: 2024-12-07  
**담당자**: QA팀  
**다음 리뷰**: 2024-12-14