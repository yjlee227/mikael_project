#!/usr/bin/env python3
"""
🎯 최종 미사용 함수 분석 (실제 호출 패턴 매칭)
- 함수명이 아닌 실제 호출 패턴 (function_name() 형태)으로 정확히 분석
- 정의는 되어 있지만 실제로는 호출되지 않는 함수들 식별
"""

import os
import subprocess

def get_all_defined_functions():
    """모든 정의된 함수 추출 (def 키워드 기반)"""
    defined_functions = {}
    modules_dir = 'klook_modules'
    
    for filename in os.listdir(modules_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            file_path = os.path.join(modules_dir, filename)
            module_name = filename[:-3]
            
            try:
                result = subprocess.run(['grep', '-n', r'^def ', file_path], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    functions = []
                    for line in lines:
                        # def function_name( 패턴 추출
                        import re
                        match = re.search(r'def\s+([a-zA-Z_]\w*)\s*\(', line)
                        if match:
                            functions.append(match.group(1))
                    defined_functions[module_name] = functions
                else:
                    defined_functions[module_name] = []
            except:
                defined_functions[module_name] = []
    
    return defined_functions

def check_function_actually_called(function_name):
    """특정 함수가 실제로 호출되는지 확인"""
    # 호출 패턴: function_name( 
    call_pattern = f"{function_name}("
    
    # 모든 Python 파일에서 검색
    search_locations = ['klook_modules/', 'KLOOK_Main_Crawler.ipynb']
    
    for location in search_locations:
        try:
            if location.endswith('.ipynb'):
                # 노트북 파일 특별 처리
                if os.path.exists(location):
                    with open(location, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if call_pattern in content:
                        return True, f"노트북에서 호출됨"
            else:
                # 디렉토리에서 grep 검색
                result = subprocess.run(['grep', '-r', call_pattern, location], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    # 함수 정의 라인은 제외 (def function_name(는 호출이 아님)
                    lines = result.stdout.strip().split('\n')
                    actual_calls = []
                    for line in lines:
                        if not line.strip().startswith('def '):
                            actual_calls.append(line.split(':')[0])  # 파일명만
                    
                    if actual_calls:
                        return True, f"호출됨: {actual_calls[0]}"
        except:
            continue
    
    return False, "호출 없음"

def final_unused_analysis():
    """최종 미사용 함수 분석"""
    print("🎯 최종 미사용 함수 분석 (실제 호출 확인)")
    print("=" * 65)
    
    # 모든 정의된 함수 수집
    defined_by_module = get_all_defined_functions()
    
    total_functions = sum(len(funcs) for funcs in defined_by_module.values())
    print(f"📊 총 정의된 함수: {total_functions}개")
    
    # 각 함수별 실제 호출 여부 확인
    truly_unused = []
    used_functions = []
    
    print(f"\n🔍 함수별 호출 확인:")
    
    for module_name, functions in defined_by_module.items():
        print(f"\n🔧 {module_name}.py ({len(functions)}개 함수):")
        
        module_unused = []
        for func in functions:
            is_called, call_info = check_function_actually_called(func)
            
            if is_called:
                used_functions.append(f"{module_name}.{func}")
                print(f"   ✅ {func}: {call_info}")
            else:
                module_unused.append(func)
                truly_unused.append(f"{module_name}.{func}")
                print(f"   🚫 {func}: {call_info}")
        
        if not module_unused:
            print(f"   🎉 모든 함수 사용 중!")
    
    # 통계 계산
    usage_rate = (len(used_functions) / total_functions) * 100 if total_functions > 0 else 0
    
    print(f"\n📊 최종 통계:")
    print(f"   📈 총 정의: {total_functions}개")
    print(f"   ✅ 실제 사용: {len(used_functions)}개")
    print(f"   🚫 실제 미사용: {len(truly_unused)}개")
    print(f"   📊 실제 사용률: {usage_rate:.1f}%")
    
    # 미사용 함수 목록
    if truly_unused:
        print(f"\n📝 미사용 함수 목록:")
        for i, func in enumerate(truly_unused, 1):
            print(f"   {i}. {func}")
    
    return {
        'total_functions': total_functions,
        'used_functions': len(used_functions),
        'unused_functions': len(truly_unused),
        'usage_rate': usage_rate,
        'unused_list': truly_unused
    }

if __name__ == "__main__":
    results = final_unused_analysis()
    
    print(f"\n🎯 최종 결론:")
    print(f"   📊 실제 사용률: {results['usage_rate']:.1f}%")
    print(f"   🚫 정리 대상: {results['unused_functions']}개 함수")