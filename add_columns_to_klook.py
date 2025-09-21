#!/usr/bin/env python3
"""
KLOOK CSV에 상품번호, 분류 컬럼 추가 스크립트
- URL에서 상품번호(activity ID) 추출
- 카테고리에서 분류 추출 또는 기본값 설정
"""

import pandas as pd
import re
import os

def extract_product_id_from_url(url):
    """URL에서 KLOOK 상품번호(activity ID) 추출"""
    try:
        # https://www.klook.com/ko/activity/118115-japan-hokkaido-... 형태에서 118115 추출
        match = re.search(r'/activity/(\d+)', url)
        if match:
            return match.group(1)
        return ""
    except Exception:
        return ""

def extract_classification_from_category(category, tab):
    """카테고리에서 분류 추출"""
    try:
        if pd.isna(category) or not category:
            return tab if tab else "일반"

        # "일본 > 투어 > 일일 투어" -> "일일 투어"
        parts = str(category).split(" > ")
        if len(parts) > 1:
            return parts[-1].strip()
        else:
            return category.strip()
    except Exception:
        return tab if tab else "일반"

def add_columns_to_klook_csv(input_file, output_file=None):
    """KLOOK CSV에 상품번호, 분류 컬럼 추가"""

    if output_file is None:
        output_file = input_file  # 원본 파일 덮어쓰기

    print(f"🔧 KLOOK CSV 컬럼 추가 시작: {input_file}")

    try:
        # CSV 읽기
        df = pd.read_csv(input_file, encoding='utf-8')
        print(f"   📊 원본 데이터: {len(df)}행, {len(df.columns)}개 컬럼")

        # 현재 컬럼 확인
        current_columns = df.columns.tolist()
        print(f"   📋 현재 컬럼: {current_columns[-3:]}")  # 마지막 3개 컬럼만 표시

        # 1. 상품번호 컬럼 추가
        if 'URL' in df.columns:
            df['상품번호'] = df['URL'].apply(extract_product_id_from_url)
            print(f"   ✅ '상품번호' 컬럼 추가 완료")
        else:
            df['상품번호'] = ""
            print(f"   ⚠️ URL 컬럼이 없어 상품번호를 빈 값으로 설정")

        # 2. 분류 컬럼 추가
        if '카테고리' in df.columns and '탭' in df.columns:
            df['분류'] = df.apply(lambda row: extract_classification_from_category(
                row['카테고리'], row.get('탭', '')), axis=1)
            print(f"   ✅ '분류' 컬럼 추가 완료")
        elif '탭' in df.columns:
            df['분류'] = df['탭']
            print(f"   ⚠️ 카테고리 컬럼이 없어 탭으로 분류 설정")
        else:
            df['분류'] = "일반"
            print(f"   ⚠️ 카테고리, 탭 컬럼이 없어 분류를 '일반'으로 설정")

        # 3. 컬럼 순서 재정렬 (KKDAY와 동일하게)
        desired_order = [
            '번호', '상품명', '가격', '평점', '리뷰수', 'URL', '도시ID', '도시명', '대륙', '국가',
            '위치태그', '카테고리', '언어', '투어형태', '미팅방식', '소요시간', '하이라이트', '순위',
            '통화', '수집일시', '데이터소스', '해시값', '메인이미지', '썸네일이미지',
            '메인이미지_경로', '썸네일이미지_경로', '상품번호', '분류', '특징', 'klook_ad_link'
        ]

        # 존재하는 컬럼만 선택하여 재정렬
        available_columns = [col for col in desired_order if col in df.columns]
        missing_columns = [col for col in desired_order if col not in df.columns]

        if missing_columns:
            print(f"   ⚠️ 누락된 컬럼: {missing_columns}")
            # 누락된 컬럼을 빈 값으로 추가
            for col in missing_columns:
                df[col] = ""

        # 컬럼 순서 재정렬
        df = df[desired_order]

        # 4. 저장
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"   💾 수정된 파일 저장: {output_file}")
        print(f"   📊 최종 데이터: {len(df)}행, {len(df.columns)}개 컬럼")

        # 5. 샘플 데이터 확인
        print(f"\n📋 상품번호/분류 샘플:")
        for i in range(min(3, len(df))):
            product_id = df.iloc[i]['상품번호']
            classification = df.iloc[i]['분류']
            url = df.iloc[i]['URL']
            print(f"   {i+1}. ID: {product_id}, 분류: {classification}")
            print(f"      URL: {url[:60]}...")

        print(f"\n✅ KLOOK CSV 컬럼 추가 완료!")
        return True

    except Exception as e:
        print(f"❌ 처리 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    # KLOOK CSV 파일 경로
    klook_file = "/mnt/c/Users/redsk/OneDrive/デスク トップ/mikael_project/klook/data/아시아/일본/일본_통합_klook_products.csv"

    if os.path.exists(klook_file):
        success = add_columns_to_klook_csv(klook_file)
        if success:
            print(f"\n🎉 작업 완료! 이제 KLOOK과 KKDAY가 동일한 30개 컬럼을 가집니다.")
        else:
            print(f"\n❌ 작업 실패.")
    else:
        print(f"❌ 파일을 찾을 수 없습니다: {klook_file}")