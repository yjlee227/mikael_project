#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('./klook_modules')

from klook_modules.data_handler import create_product_data_structure

# 테스트 데이터로 컬럼 구조 확인
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

print(f"총 컬럼 수: {len(test_data)}")
print("\n32개 목표 컬럼:")
for i, col in enumerate(test_data.keys(), 1):
    print(f"{i:2d}. {col}")

# 실제 32개 컬럼 확인
expected_32_columns = [
    "번호", "도시ID", "페이지", "대륙", "국가", "도시", "공항코드", "상품타입", "상품명",
    "가격_원본", "가격_정제", "평점_원본", "평점_정제", "리뷰수", "언어", "카테고리", "하이라이트", "위치",
    "메인이미지_파일명", "메인이미지_상대경로", "메인이미지_전체경로", "메인이미지_상태",
    "썸네일이미지_파일명", "썸네일이미지_상대경로", "썸네일이미지_전체경로", "썸네일이미지_상태",
    "URL", "수집_시간", "상태", "탭명", "탭순서", "탭내_랭킹", "URL_해시"
]

print(f"\n목표 32개 컬럼 수: {len(expected_32_columns)}")
print("목표 컬럼:")
for i, col in enumerate(expected_32_columns, 1):
    print(f"{i:2d}. {col}")

print(f"\n현재 컬럼 수: {len(test_data)}")
print(f"목표 컬럼 수: {len(expected_32_columns)}")
print(f"차이: {len(test_data) - len(expected_32_columns)}")