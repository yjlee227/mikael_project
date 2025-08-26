"""
CSV 번호 연속성 관리 시스템
- 기존 CSV에서 마지막 번호 확인
- 다음 번호 자동 생성
- 번호 일관성 유지
"""

import os
import csv
import re

def get_last_product_number(city_name):
    """기존 CSV에서 마지막 상품 번호 확인"""
    try:
        # 가능한 CSV 파일 경로들
        possible_paths = [
            f"data/아시아/일본/{city_name}/klook_{city_name}_products.csv",  # 구마모토 경로
            f"data/{city_name}/klook_{city_name}_products.csv",             # 일반 경로
            f"data/아시아/{city_name}/klook_{city_name}_products.csv",       # 도시국가 경로
            f"klook_{city_name}_products.csv"                               # 현재 디렉토리
        ]
        
        max_number = 0
        
        for csv_path in possible_paths:
            if os.path.exists(csv_path):
                print(f"📁 CSV 파일 발견: {csv_path}")
                
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        # 다양한 번호 컬럼 확인
                        number_value = None
                        
                        # 1. '번호' 컬럼에서 숫자 추출
                        if '번호' in row and row['번호']:
                            # "page1_1" → 1, "KMJ_0001" → 1 등에서 숫자 추출
                            numbers = re.findall(r'(\d+)', str(row['번호']))
                            if numbers:
                                # 가장 뒤의 숫자를 상품 번호로 사용
                                number_value = int(numbers[-1])
                        
                        # 2. 다른 번호 관련 컬럼 확인
                        for col in ['product_number', '상품번호', 'number', 'seq']:
                            if col in row and row[col]:
                                try:
                                    number_value = int(row[col])
                                    break
                                except:
                                    continue
                        
                        # 3. 메인 이미지 파일명에서 번호 추출 (KMJ_0001.jpg → 1)
                        if not number_value and '메인이미지_파일명' in row and row['메인이미지_파일명']:
                            img_numbers = re.findall(r'_(\d+)\.', row['메인이미지_파일명'])
                            if img_numbers:
                                number_value = int(img_numbers[0])
                        
                        if number_value:
                            max_number = max(max_number, number_value)
                
                print(f"   📊 발견된 최대 번호: {max_number}")
                break
        
        if max_number == 0:
            print(f"ℹ️ '{city_name}': 기존 번호 없음, 1번부터 시작")
        else:
            print(f"✅ '{city_name}': 마지막 번호 {max_number}, 다음 번호: {max_number + 1}")
        
        return max_number
        
    except Exception as e:
        print(f"⚠️ 번호 확인 실패: {e}")
        return 0

def get_next_product_number(city_name):
    """다음 상품 번호 반환"""
    last_number = get_last_product_number(city_name)
    return last_number + 1

def update_csv_with_proper_numbers(city_name):
    """기존 CSV의 번호를 순차적으로 업데이트"""
    try:
        csv_path = f"data/아시아/일본/{city_name}/klook_{city_name}_products.csv"
        
        if not os.path.exists(csv_path):
            print(f"❌ CSV 파일 없음: {csv_path}")
            return False
        
        print(f"🔧 CSV 번호 정리 중: {csv_path}")
        
        # 기존 데이터 읽기
        rows = []
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            print("ℹ️ 빈 CSV 파일")
            return True
        
        # 번호 순차적으로 업데이트
        for i, row in enumerate(rows, 1):
            row['번호'] = str(i)
            
            # 이미지 파일명도 업데이트 (도시코드 기반)
            from klook.src.config import get_city_code
            city_code = get_city_code(city_name)
            
            if city_code:
                row['메인이미지_파일명'] = f"{city_code}_{i:04d}.jpg"
                row['썸네일이미지_파일명'] = f"{city_code}_{i:04d}_thumb.jpg"
        
        # 업데이트된 데이터 저장
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"✅ CSV 번호 정리 완료: {len(rows)}개 행")
        return True
        
    except Exception as e:
        print(f"❌ CSV 번호 정리 실패: {e}")
        return False

def validate_csv_numbering(city_name):
    """CSV 번호 일관성 검증"""
    try:
        csv_path = f"data/아시아/일본/{city_name}/klook_{city_name}_products.csv"
        
        if not os.path.exists(csv_path):
            return True  # 파일 없으면 문제 없음
        
        print(f"🔍 CSV 번호 일관성 검증: {city_name}")
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            return True
        
        # 번호 일관성 체크
        issues = []
        expected_number = 1
        
        for row in rows:
            current_number = row.get('번호', '')
            
            # 숫자가 아닌 경우
            if not current_number.isdigit():
                issues.append(f"행 {expected_number}: 번호가 숫자가 아님 ('{current_number}')")
            else:
                actual_number = int(current_number)
                if actual_number != expected_number:
                    issues.append(f"행 {expected_number}: 번호 불일치 (기대: {expected_number}, 실제: {actual_number})")
            
            expected_number += 1
        
        if issues:
            print("⚠️ 번호 일관성 문제 발견:")
            for issue in issues[:5]:  # 최대 5개만 표시
                print(f"   {issue}")
            if len(issues) > 5:
                print(f"   ... 외 {len(issues)-5}개 문제")
            return False
        else:
            print(f"✅ 번호 일관성 정상: {len(rows)}개 행")
            return True
        
    except Exception as e:
        print(f"❌ 번호 검증 실패: {e}")
        return False

# 테스트
if __name__ == "__main__":
    city_name = "구마모토"
    
    print("🔍 CSV 번호 연속성 시스템 테스트")
    print("=" * 50)
    
    # 1. 현재 상태 확인
    last_num = get_last_product_number(city_name)
    next_num = get_next_product_number(city_name)
    
    print(f"📊 현재 상태:")
    print(f"   마지막 번호: {last_num}")
    print(f"   다음 번호: {next_num}")
    
    # 2. 일관성 검증
    print(f"\n🔍 일관성 검증:")
    is_valid = validate_csv_numbering(city_name)
    
    # 3. 정리 제안
    if not is_valid:
        print(f"\n🔧 정리 필요:")
        print(f"   update_csv_with_proper_numbers('{city_name}')를 실행하세요")