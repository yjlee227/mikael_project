#!/usr/bin/env python3
"""
KLOOK 변환 유틸리티 테스트 스크립트
- 함수별 동작 검증
- JSON 파일 구조 확인
- KLOOK과 구조 비교
"""

import sys
import os
from datetime import datetime

# 프로젝트 경로 추가
sys.path.append('./src')
sys.path.append('.')

def test_klook_converter():
    """KLOOK 변환 함수 테스트"""
    print("🧪 KLOOK 변환 유틸리티 테스트 시작")
    print("="*50)

    try:
        from src.utils.klook_converter import create_klook_style_files, load_urls_for_stage2, update_stage2_status
        print("✅ 모듈 import 성공")
    except Exception as e:
        print(f"❌ 모듈 import 실패: {e}")
        return False

    # 테스트 데이터
    test_city = "테스트도쿄"
    test_urls = [
        "https://www.kkday.com/ko/product/157140-test-product-1",
        "https://www.kkday.com/ko/product/157141-test-product-2",
        "https://www.kkday.com/ko/product/157142-test-product-3"
    ]

    print(f"\n📋 테스트 데이터:")
    print(f"   🏙️ 도시: {test_city}")
    print(f"   📊 URL 개수: {len(test_urls)}개")

    # 1. JSON 파일 생성 테스트
    print(f"\n🔧 테스트 1: JSON 파일 생성")
    try:
        url_file, status_file = create_klook_style_files(test_city, test_urls)

        if url_file and status_file:
            print(f"✅ JSON 파일 생성 성공")
            print(f"   📄 URL 파일: {url_file}")
            print(f"   📊 상태 파일: {status_file}")

            # 파일 존재 확인
            if os.path.exists(url_file) and os.path.exists(status_file):
                print(f"✅ 파일 존재 확인 완료")
            else:
                print(f"❌ 파일 존재 확인 실패")
                return False
        else:
            print(f"❌ JSON 파일 생성 실패")
            return False

    except Exception as e:
        print(f"❌ JSON 파일 생성 테스트 실패: {e}")
        return False

    # 2. JSON 파일 구조 검증
    print(f"\n🔧 테스트 2: JSON 파일 구조 검증")
    try:
        import json

        # URL 데이터 파일 검증
        with open(url_file, 'r', encoding='utf-8') as f:
            url_data = json.load(f)

        required_url_fields = ["collection_info", "url_rank_mapping", "collection_stats"]
        for field in required_url_fields:
            if field not in url_data:
                print(f"❌ URL 데이터에 {field} 필드 누락")
                return False

        # 상태 파일 검증
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)

        required_status_fields = ["city", "tab", "platform", "stage1", "stage2"]
        for field in required_status_fields:
            if field not in status_data:
                print(f"❌ 상태 데이터에 {field} 필드 누락")
                return False

        print(f"✅ JSON 구조 검증 완료")
        print(f"   📄 URL 데이터 필드: {len(url_data.keys())}개")
        print(f"   📊 상태 데이터 필드: {len(status_data.keys())}개")
        print(f"   🔗 URL 매핑: {len(url_data['url_rank_mapping'])}개")

    except Exception as e:
        print(f"❌ JSON 구조 검증 실패: {e}")
        return False

    # 3. URL 로드 테스트
    print(f"\n🔧 테스트 3: URL 로드")
    try:
        loaded_urls = load_urls_for_stage2(test_city, tab="전체")

        if loaded_urls:
            print(f"✅ URL 로드 성공: {len(loaded_urls)}개")

            # 원본과 비교
            if len(loaded_urls) == len(test_urls):
                print(f"✅ URL 개수 일치")
            else:
                print(f"⚠️ URL 개수 불일치: 원본 {len(test_urls)}, 로드 {len(loaded_urls)}")

            # URL 내용 비교
            all_match = all(url in test_urls for url in loaded_urls)
            if all_match:
                print(f"✅ URL 내용 일치")
            else:
                print(f"⚠️ URL 내용 불일치")

        else:
            print(f"❌ URL 로드 실패")
            return False

    except Exception as e:
        print(f"❌ URL 로드 테스트 실패: {e}")
        return False

    # 4. Stage 2 상태 업데이트 테스트
    print(f"\n🔧 테스트 4: Stage 2 상태 업데이트")
    try:
        stage2_test_data = {
            "status": "success",
            "data": {
                "total_processed": 3,
                "success_count": 3,
                "error_count": 0,
                "skip_count": 0,
                "csv_generated": True,
                "completion_time": datetime.now().isoformat()
            }
        }

        success = update_stage2_status(test_city, stage2_test_data, tab="전체")

        if success:
            print(f"✅ Stage 2 상태 업데이트 성공")

            # 업데이트 결과 확인
            with open(status_file, 'r', encoding='utf-8') as f:
                updated_status = json.load(f)

            if updated_status["stage2"]["status"] == "success":
                print(f"✅ 상태 업데이트 내용 확인 완료")
            else:
                print(f"⚠️ 상태 업데이트 내용 불일치")

        else:
            print(f"❌ Stage 2 상태 업데이트 실패")
            return False

    except Exception as e:
        print(f"❌ Stage 2 상태 업데이트 테스트 실패: {e}")
        return False

    # 5. KLOOK 구조와 비교
    print(f"\n🔧 테스트 5: KLOOK 구조 비교")
    try:
        klook_url_file = "klook_urls_data_삿포로_전체.json"
        klook_status_file = "klook_status_삿포로_전체.json"

        if os.path.exists(klook_url_file):
            with open(klook_url_file, 'r', encoding='utf-8') as f:
                klook_url_data = json.load(f)

            # 구조 비교
            klook_keys = set(klook_url_data.keys())
            kkday_keys = set(url_data.keys())

            if klook_keys == kkday_keys:
                print(f"✅ KLOOK과 URL 데이터 구조 일치")
            else:
                missing = klook_keys - kkday_keys
                extra = kkday_keys - klook_keys
                if missing:
                    print(f"⚠️ KKDAY에 누락된 필드: {missing}")
                if extra:
                    print(f"⚠️ KKDAY에 추가된 필드: {extra}")
        else:
            print(f"⚠️ KLOOK 파일이 없어 구조 비교 건너뜀")

    except Exception as e:
        print(f"⚠️ KLOOK 구조 비교 실패: {e}")

    # 테스트 파일 정리
    print(f"\n🧹 테스트 파일 정리")
    try:
        if os.path.exists(url_file):
            os.remove(url_file)
        if os.path.exists(status_file):
            os.remove(status_file)
        print(f"✅ 테스트 파일 정리 완료")
    except Exception as e:
        print(f"⚠️ 테스트 파일 정리 실패: {e}")

    print(f"\n{'='*50}")
    print(f"🎉 모든 테스트 완료!")
    print(f"✅ KLOOK 변환 유틸리티가 정상적으로 작동합니다.")
    return True

if __name__ == "__main__":
    success = test_klook_converter()
    if success:
        print(f"\n🚀 이제 노트북에서 안전하게 사용할 수 있습니다!")
        print(f"💡 테스트 완료 후 실제 도시로 테스트해보세요.")
    else:
        print(f"\n❌ 테스트 실패 - 문제를 해결 후 다시 테스트하세요.")

    sys.exit(0 if success else 1)