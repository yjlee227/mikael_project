# myrealtrip_main.py
# 마이리얼트립 크롤링 - 메인 실행 파일

# 함수 파일에서 모든 함수와 설정 import
from myrealtrip_functions import *
import selenium

# 실행 시작
print("🔄 마이리얼트립 크롤링 시작!")
print(f"🔧 Selenium 버전: {selenium.__version__}")

# 결과를 저장할 리스트 (매번 명확히 초기화!)
all_results = []
print("🔄 결과 저장소 초기화 완료")

# 크롬 드라이버 실행
try:
    driver = setup_driver()
except Exception as e:
    print(f"❌ 드라이버 설정 실패: {e}")
    exit(1)

# 썸네일 폴더 생성 (한 번만)
if CONFIG["SAVE_IMAGES"]:
    img_folder_path = os.path.abspath("") + "/myrealtripthumb_img"
    try:
        shutil.rmtree(img_folder_path)
    except:
        pass
    os.makedirs(img_folder_path, exist_ok=True)
    print("📁 이미지 폴더 생성 완료")

# 🎉 여러 도시 크롤링 시작
print("="*60)
print(f"🌏 총 {len(CITIES_TO_SEARCH)}개 도시 검색 시작!")
print(f"검색할 도시들: {', '.join(CITIES_TO_SEARCH)}")
print(f"📊 현재 저장된 결과 수: {len(all_results)}개")
print(f"⚙️  설정: 재시도 {CONFIG['RETRY_COUNT']}회, 타임아웃 {CONFIG['WAIT_TIMEOUT']}초")
print(f"🆕 새 기능: 도시당 {CONFIG['MAX_PRODUCTS_PER_CITY']}개 상품 크롤링")
print("="*60)

# 각 도시별로 반복 검색
for city_index, city_name in enumerate(CITIES_TO_SEARCH):
    # 진행률 표시
    print_progress(city_index, len(CITIES_TO_SEARCH), city_name, "진행중")
    
    # 도시 정보 가져오기
    continent, country = get_city_info(city_name)
    print(f"  🌍 대륙: {continent} | 국가: {country}")
    
    try:
        # 1. 메인 페이지로 이동 (매번 새로 시작)
        retry_operation(
            lambda: go_to_main_page(driver), 
            "메인 페이지 이동"
        )
        print(f"  📱 마이리얼트립 페이지 열기 완료")
        
        # 2. 검색창 찾기 및 입력
        retry_operation(
            lambda: find_and_fill_search(driver, city_name), 
            "검색창 입력"
        )

        # 3. 검색 버튼 클릭
        retry_operation(
            lambda: click_search_button(driver), 
            "검색 버튼 클릭"
        )

        # 4. 팝업 처리 (선택사항)
        try:
            handle_popup(driver)
        except Exception as e:
            print(f"  ℹ️ 팝업 처리 중 오류 (무시됨): {type(e).__name__}")

        # 5. 전체 상품 보기 클릭 (선택사항)
        try:
            click_view_all(driver)
        except Exception as e:
            print(f"  ℹ️ 전체 상품 보기 처리 중 오류 (무시됨): {type(e).__name__}")

        # 6. 🆕 1페이지의 모든 상품 크롤링 (새로운 기능!)
        try:
            city_results = crawl_all_products_in_page(driver, city_name, continent, country)
            
            if city_results:
                # 결과를 전체 리스트에 추가
                all_results.extend(city_results)
                
                # 중간 저장
                save_intermediate_results(all_results, f"{city_name}_전체상품")
                
                print(f"  ✅ {city_name} 전체 크롤링 완료!")
                print(f"     수집된 상품 수: {len(city_results)}개")
                print(f"     대륙: {continent} | 국가: {country}")
                
                # 상품별 간단 요약 출력
                print(f"  📋 {city_name} 상품 목록:")
                for i, result in enumerate(city_results[:5], 1):  # 처음 5개만 출력
                    safe_name = str(result['상품명'])[:30] + "..." if len(str(result['상품명'])) > 30 else str(result['상품명'])
                    print(f"     {i}. {safe_name} - {result['가격']}")
                if len(city_results) > 5:
                    print(f"     ... 외 {len(city_results)-5}개 상품")
            else:
                print(f"  ⚠️ {city_name}: 상품 정보를 수집하지 못했습니다.")
                
        except Exception as e:
            print(f"  ❌ {city_name} 상품 크롤링 실패: {type(e).__name__}: {e}")

        # 진행률 표시 (완료)
        print_progress(city_index + 1, len(CITIES_TO_SEARCH), city_name, "완료")

        # 다음 검색을 위한 휴식 (마지막 도시가 아닌 경우)
        if city_index < len(CITIES_TO_SEARCH) - 1:
            wait_time = random.uniform(5, 10)
            print(f"  ⏰ 다음 검색까지 {wait_time:.1f}초 대기...")
            time.sleep(wait_time)

    # 구체적인 에러 타입별 처리
    except TimeoutException as e:
        print(f"  ⏰ {city_name}: 페이지 로딩 시간 초과")
        print(f"  📍 위치: {continent} > {country} > {city_name}")
        print(f"  ➡️ 다음 도시로 계속 진행합니다...")
        print_progress(city_index + 1, len(CITIES_TO_SEARCH), city_name, "시간초과")
        continue
        
    except NoSuchElementException as e:
        print(f"  🔍 {city_name}: 필요한 웹 요소를 찾을 수 없음")
        print(f"  📍 위치: {continent} > {country} > {city_name}")
        print(f"  ➡️ 다음 도시로 계속 진행합니다...")
        print_progress(city_index + 1, len(CITIES_TO_SEARCH), city_name, "요소없음")
        continue
        
    except WebDriverException as e:
        print(f"  🌐 {city_name}: 웹드라이버 오류 발생")
        print(f"  📍 위치: {continent} > {country} > {city_name}")
        print(f"  ➡️ 다음 도시로 계속 진행합니다...")
        print_progress(city_index + 1, len(CITIES_TO_SEARCH), city_name, "드라이버오류")
        continue
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 사용자가 크롤링을 중단했습니다.")
        print(f"📊 중단 시점까지 {len(all_results)}개 상품 정보를 수집했습니다.")
        break
        
    except Exception as e:
        print(f"  ❌ {city_name}: 예상치 못한 오류 - {type(e).__name__}: {e}")
        print(f"  📍 위치: {continent} > {country} > {city_name}")
        print(f"  ➡️ 다음 도시로 계속 진행합니다...")
        print_progress(city_index + 1, len(CITIES_TO_SEARCH), city_name, "예상치못한오류")
        continue

# 최종 결과 출력 및 CSV 저장
print("\n" + "="*60)
print("🎉 모든 도시 검색 완료!")
print("="*60)

if all_results:
    print(f"\n📊 총 {len(all_results)}개 상품의 정보를 수집했습니다:")
    print("-" * 80)
    
    # 도시별 상품 수 통계
    city_stats = {}
    for result in all_results:
        city = result['도시']
        if city not in city_stats:
            city_stats[city] = 0
        city_stats[city] += 1
    
    print("📈 도시별 수집 현황:")
    for city, count in city_stats.items():
        continent, country = get_city_info(city)
        print(f"   🌍 {continent} > {country} > {city}: {count}개 상품")
    print("-" * 80)

    # 처음 5개 결과 미리보기
    print("📋 수집된 상품 미리보기 (처음 5개):")
    for i, result in enumerate(all_results[:5], 1):
        print(f"{i}. {result['대륙']} > {result['국가']} > {result['도시']}")
        print(f"   상품명: {result['상품명']}")
        print(f"   가격: {result['가격']}")
        print(f"   평점: {result['평점']}")
        print(f"   리뷰수: {result['리뷰수'] if result['리뷰수'] else '정보 없음'}")
        print(f"   언어: {result['언어'] if result['언어'] else '정보 없음'}")
        print(f"   URL: {result['URL']}")
        print("-" * 40)
    
    if len(all_results) > 5:
        print(f"... 외 {len(all_results)-5}개 상품")

    # CSV 파일로 저장
    try:
        df = pd.DataFrame(all_results)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"myrealtrip_전체상품_최종결과_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 최종 결과가 '{filename}' 파일로 저장되었습니다!")
        print(f"📁 파일 위치: {os.path.abspath(filename)}")
        print("💡 엑셀에서 바로 열어볼 수 있습니다!")
        
        # CSV 파일 내용 미리보기 (컬럼명만)
        print(f"\n📋 CSV 파일 컬럼 구조:")
        print(f"   컬럼: {', '.join(df.columns.tolist())}")
        
        # 통계 정보 추가
        print(f"\n📈 수집 통계:")
        print(f"   🌏 대륙별 분포: {df['대륙'].value_counts().to_dict()}")
        print(f"   🏙️ 국가별 분포: {df['국가'].value_counts().to_dict()}")
        print(f"   🎯 도시별 분포: {df['도시'].value_counts().to_dict()}")
        print(f"   ⭐ 평점 정보 수집률: {len(df[df['평점'] != '정보 없음'])} / {len(df)} ({len(df[df['평점'] != '정보 없음'])/len(df)*100:.1f}%)")
        print(f"   💬 리뷰수 정보 수집률: {len(df[df['리뷰수'] != ''])} / {len(df)} ({len(df[df['리뷰수'] != ''])/len(df)*100:.1f}%)")
        print(f"   🌐 언어 정보 수집률: {len(df[df['언어'] != ''])} / {len(df)} ({len(df[df['언어'] != ''])/len(df)*100:.1f}%)")
        print(f"   🖼️ 이미지 다운로드 성공률: {len(df[df['이미지_경로'].str.contains('.png', na=False)])} / {len(df)} ({len(df[df['이미지_경로'].str.contains('.png', na=False)])/len(df)*100:.1f}%)")
        
    except Exception as e:
        print(f"\n❌ CSV 파일 저장 중 오류: {type(e).__name__}: {e}")
        print("수집된 데이터:")
        for result in all_results:
            print(result)

else:
    print("\n❌ 수집된 결과가 없습니다.")
    print("💡 도시명이나 인터넷 연결을 확인해보세요.")
    print("💡 웹페이지 구조가 변경되었을 수도 있습니다.")

# 최종 마무리 정보
print(f"\n🏁 크롤링 완료!")
print(f"✅ 성공: {len(all_results)}개 상품")

# 도시별 실패 계산
total_expected = 0
for city in CITIES_TO_SEARCH:
    city_count = len([r for r in all_results if r['도시'] == city])
    if city_count == 0:
        total_expected += 1  # 실패한 도시

print(f"❌ 실패: {total_expected}개 도시")
success_rate = len(CITIES_TO_SEARCH) - total_expected
print(f"📊 도시 성공률: {success_rate}/{len(CITIES_TO_SEARCH)} ({success_rate/len(CITIES_TO_SEARCH)*100:.1f}%)")

if all_results:
    avg_products_per_city = len(all_results) / success_rate if success_rate > 0 else 0
    print(f"📈 도시당 평균 상품 수: {avg_products_per_city:.1f}개")

print("="*60)

# 드라이버 안전 종료
try:
    driver.quit()
    print("🚪 웹드라이버 정상 종료")
except:
    print("⚠️ 웹드라이버 종료 중 오류 (무시됨)")

print("🎯 모든 작업이 완료되었습니다!")
print("\n💡 다음 단계:")
print("   1. CSV 파일을 확인하여 데이터 품질 검토")
print("   2. 문제없이 작동한다면 다음 페이지 크롤링 기능 추가 가능")
print("   3. 더 많은 도시를 CITIES_TO_SEARCH에 추가하여 확장 가능")
print("\n🎉 1페이지 24개 상품 크롤링 완료!")