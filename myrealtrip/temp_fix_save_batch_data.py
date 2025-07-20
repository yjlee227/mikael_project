def save_batch_data(batch_results, city_name):
    """✅ 수정된 배치 데이터 저장 (데이터 연속성 확보)"""
    if not batch_results:
        return None
    
    try:
        # 도시 정보 가져오기
        continent, country = get_city_info(city_name)
        
        # 계층 구조 폴더 생성: data/대륙/국가/도시/
        data_dir = os.path.join("data", continent, country, city_name)
        os.makedirs(data_dir, exist_ok=True)
        
        # 파일명 설정
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 🔧 수정: 1. 도시별 CSV (추가 방식으로 변경 - 데이터 연속성 확보)
        city_csv = os.path.join(data_dir, f"myrealtrip_{city_name}_products.csv")
        df = pd.DataFrame(batch_results)
        
        # 기존 파일이 있으면 추가, 없으면 새로 생성 (도시별도 연속성 확보)
        if os.path.exists(city_csv):
            df.to_csv(city_csv, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(city_csv, index=False, encoding='utf-8-sig')
        
        # 🔧 수정: 2. 국가별 통합 CSV (추가 방식) - 같은 데이터 저장으로 연속성 확보
        country_dir = os.path.join("data", continent, country)
        country_csv = os.path.join(country_dir, f"{country}_myrealtrip_products_all.csv")
        
        # 기존 파일이 있으면 추가, 없으면 새로 생성
        if os.path.exists(country_csv):
            df.to_csv(country_csv, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(country_csv, index=False, encoding='utf-8-sig')
        
        print(f"✅ 배치 데이터 저장 완료 (연속성 확보):")
        print(f"   📁 도시별: {city_csv}")
        print(f"   📁 국가별: {country_csv}")
        
        return {
            "city_csv": city_csv,
            "country_csv": country_csv,
            "data_count": len(batch_results)
        }
        
    except Exception as e:
        print(f"❌ 배치 데이터 저장 실패: {e}")
        return None