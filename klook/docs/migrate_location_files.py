#!/usr/bin/env python3
"""
위치 학습 파일 마이그레이션 스크립트
- 기존: location_data/크라비_keywords.json
- 신규: location_data/아시아/태국/KBV_keywords.json
"""

import os
import json
import shutil
from datetime import datetime

# 프로젝트 루트 경로
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCATION_DATA_DIR = os.path.join(PROJECT_ROOT, "location_data")

# 도시 매핑 정보 (config.py에서 가져온 정보)
CITY_MAPPING = {
    "크라비": {"대륙": "아시아", "국가": "태국", "코드": "KBV"},
    "파리": {"대륙": "유럽", "국가": "프랑스", "코드": "PAR"},
}

def backup_existing_files():
    """기존 파일들을 백업"""
    print("📦 기존 파일 백업 중...")
    
    backup_dir = os.path.join(LOCATION_DATA_DIR, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_files = []
    
    for file in os.listdir(LOCATION_DATA_DIR):
        if file.endswith('_keywords.json') or file == 'location_keywords.json':
            src = os.path.join(LOCATION_DATA_DIR, file)
            dst = os.path.join(backup_dir, file)
            shutil.copy2(src, dst)
            backup_files.append(file)
            print(f"   ✅ 백업: {file}")
    
    print(f"📁 백업 완료: {backup_dir}")
    return backup_dir, backup_files

def create_directory_structure():
    """새로운 디렉토리 구조 생성"""
    print("🏗️ 새 디렉토리 구조 생성 중...")
    
    for city_name, info in CITY_MAPPING.items():
        continent = info["대륙"]
        country = info["국가"]
        
        new_dir = os.path.join(LOCATION_DATA_DIR, continent, country)
        os.makedirs(new_dir, exist_ok=True)
        print(f"   ✅ 생성: {continent}/{country}")

def migrate_files():
    """파일 마이그레이션 실행"""
    print("🚚 파일 마이그레이션 중...")
    
    migrated_files = []
    
    # 1. 도시별 파일들 마이그레이션
    for city_name, info in CITY_MAPPING.items():
        old_filename = f"{city_name}_keywords.json"
        old_path = os.path.join(LOCATION_DATA_DIR, old_filename)
        
        if os.path.exists(old_path):
            continent = info["대륙"]
            country = info["국가"]
            city_code = info["코드"]
            
            new_filename = f"{city_code}_keywords.json"
            new_path = os.path.join(LOCATION_DATA_DIR, continent, country, new_filename)
            
            # 파일 이동
            shutil.move(old_path, new_path)
            migrated_files.append({
                "from": old_filename,
                "to": f"{continent}/{country}/{new_filename}"
            })
            print(f"   ✅ 이동: {old_filename} → {continent}/{country}/{new_filename}")
    
    # 2. location_keywords.json 파일 처리 (통합 파일)
    main_file = os.path.join(LOCATION_DATA_DIR, "location_keywords.json")
    if os.path.exists(main_file):
        print(f"   ℹ️ 통합 파일 유지: location_keywords.json")
    
    return migrated_files

def verify_migration():
    """마이그레이션 결과 검증"""
    print("🔍 마이그레이션 검증 중...")
    
    success = True
    
    for city_name, info in CITY_MAPPING.items():
        continent = info["대륙"]
        country = info["국가"]
        city_code = info["코드"]
        
        new_filename = f"{city_code}_keywords.json"
        new_path = os.path.join(LOCATION_DATA_DIR, continent, country, new_filename)
        
        if os.path.exists(new_path):
            try:
                # JSON 파일 유효성 검사
                with open(new_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"   ✅ 검증 성공: {continent}/{country}/{new_filename}")
            except Exception as e:
                print(f"   ❌ 검증 실패: {new_filename} - {e}")
                success = False
        else:
            print(f"   ⚠️ 파일 없음: {continent}/{country}/{new_filename}")
    
    return success

def main():
    """메인 실행 함수"""
    print("🚀 위치 학습 파일 마이그레이션 시작")
    print("="*50)
    
    try:
        # 1. 백업
        backup_dir, backup_files = backup_existing_files()
        
        # 2. 디렉토리 구조 생성
        create_directory_structure()
        
        # 3. 파일 마이그레이션
        migrated_files = migrate_files()
        
        # 4. 검증
        if verify_migration():
            print("\n🎉 마이그레이션 성공!")
            print(f"📁 백업 위치: {backup_dir}")
            print(f"📊 마이그레이션된 파일: {len(migrated_files)}개")
            
            for migration in migrated_files:
                print(f"   • {migration['from']} → {migration['to']}")
                
        else:
            print("\n❌ 마이그레이션 중 오류 발생")
            print("💡 백업 파일에서 복구하세요")
            
    except Exception as e:
        print(f"\n❌ 마이그레이션 실패: {e}")
        print("💡 백업 파일에서 복구하세요")

if __name__ == "__main__":
    main()