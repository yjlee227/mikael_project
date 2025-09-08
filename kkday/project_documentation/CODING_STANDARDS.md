# KKday 크롤링 시스템 - 코딩 표준 및 개발 가이드라인

## 🎯 코딩 워크플로우 (Chain of Thought 기법)

### 📋 작업 전 필수 단계
모든 코딩 작업 시작 전에 다음 단계를 거칩니다:

1. **문제 분석 단계**
   ```
   Q: 이 작업에서 해결해야 할 핵심 문제는 무엇인가?
   A: 현재 상황 + 목표 상황 명확히 정의
   ```

2. **해결 계획 수립**
   ```
   Q: 어떤 순서로 작업을 진행할 것인가?
   A: 1단계 → 2단계 → 3단계 구체적 계획 제시
   ```

3. **가정 사항 명시**
   ```
   Q: 어떤 가정을 하고 있는가?
   A: 기존 코드 동작, 의존성, 제약사항 등
   ```

4. **검증 방법 제시**
   ```
   Q: 작업 완료 후 어떻게 검증할 것인가?
   A: 테스트 방법, 확인 기준 제시
   ```

**예시 템플릿:**
```markdown
## 작업 계획서
**문제**: Klook 셀렉터를 KKday용으로 변경
**목표**: KKday 웹사이트에서 정상적으로 데이터 추출
**단계**: 
1. 기존 셀렉터 분석
2. KKday 웹사이트 구조 파악  
3. 새로운 셀렉터 적용
4. 동작 테스트
**가정**: KKday 웹사이트가 표준 HTML 구조 사용
**검증**: 실제 상품 페이지에서 데이터 추출 성공
```

## 🏗️ 컨텍스트 및 환경 정보 관리

### 📁 파일 및 코드베이스 컨텍스트

#### 프로젝트 구조 이해
```python
# 의존성 관계 맵
src/
├── config.py              # 전역 설정 (모든 모듈이 의존)
├── scraper/
│   ├── crawler.py          # 메인 엔진 (모든 scraper 모듈 사용)
│   ├── driver_manager.py   # 웹드라이버 관리
│   ├── parsers.py          # 데이터 추출 (driver_manager 의존)
│   ├── ranking.py          # 순위 관리
│   └── url_manager.py      # URL 관리
└── utils/
    ├── file_handler.py     # 파일 저장 (config 의존)
    ├── city_manager.py     # 도시 관리 (config 의존)  
    └── location_learning.py # AI 학습 (config 의존)
```

#### 핵심 데이터 구조
```python
# 표준 상품 데이터 구조 (file_handler.py에서 정의)
PRODUCT_DATA_STRUCTURE = {
    "번호": str,           # 상품 고유 번호
    "상품명": str,         # 필수 필드
    "가격": str,           # 필수 필드  
    "평점": str,           # 선택 필드
    "리뷰수": str,         # 선택 필드
    "URL": str,            # 필수 필드
    "도시ID": str,         # config.py에서 자동 생성
    "도시명": str,         # 사용자 입력
    "데이터소스": "KKday", # 고정값
    # ... 총 24개 필드
}
```

#### Import 관계 및 호출 패턴
```python
# crawler.py에서 다른 모듈 호출 패턴
from ..config import CONFIG
from ..utils.file_handler import save_to_csv_kkday
from .parsers import extract_all_product_data
from .driver_manager import setup_driver

# 호출 순서
driver = setup_driver()                           # 1. 드라이버 초기화
data = extract_all_product_data(driver, url)     # 2. 데이터 추출
save_to_csv_kkday(data, city_name)              # 3. 데이터 저장
```

### 🏛️ 아키텍처 및 설계 컨텍스트

#### 설계 패턴
- **모듈 패턴**: 각 기능별로 독립적 모듈 구성
- **팩토리 패턴**: driver_manager에서 드라이버 생성
- **전략 패턴**: parsers에서 다양한 파싱 전략 사용
- **싱글톤 패턴**: config에서 전역 설정 관리

#### 데이터 흐름
```mermaid
사용자 입력 (도시명) 
→ config.py (도시 정보 조회)
→ driver_manager.py (브라우저 초기화)  
→ url_manager.py (URL 수집)
→ parsers.py (데이터 추출)
→ file_handler.py (CSV/이미지 저장)
```

#### 오류 처리 전략
```python
# 표준 오류 처리 패턴
try:
    result = risky_operation()
    if not result:
        print(f"⚠️ 경고: 작업 부분 실패")
        return False
    print(f"✅ 성공: 작업 완료")  
    return True
except Exception as e:
    print(f"❌ 오류: {e}")
    return False
```

## 📝 코딩 스타일 및 제약 조건

### 🐍 Python 코딩 컨벤션

#### 네이밍 규칙
```python
# 함수명: snake_case
def extract_product_data():
    pass

# 클래스명: PascalCase  
class KKdayCrawler:
    pass

# 상수: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# 변수명: snake_case
city_name = "서울"
product_data = {}
```

#### 함수 문서화 표준
```python
def save_to_csv_kkday(product_data, city_name):
    """KKday 상품 데이터를 CSV로 저장
    
    Args:
        product_data (dict): 상품 데이터 딕셔너리
        city_name (str): 도시명
        
    Returns:
        bool: 저장 성공 여부
        
    Raises:
        ValueError: 필수 필드 누락 시
        IOError: 파일 저장 실패 시
    """
```

#### 에러 메시지 표준
```python
# 이모지 기반 상태 표시
print("🚀 시작: 크롤링 초기화")     # 시작
print("✅ 성공: 데이터 저장 완료")   # 성공  
print("⚠️ 경고: 일부 데이터 누락")   # 경고
print("❌ 오류: 네트워크 연결 실패") # 오류
print("ℹ️ 정보: 현재 진행률 50%")    # 정보
```

### ⚡ 성능 및 보안 최적화

#### 성능 요구사항
```python
# 복잡도 제한
- 시간 복잡도: O(n^2) 이하
- 메모리 사용량: 2GB 이하  
- 페이지 처리 시간: 5초 이내

# 효율적인 데이터 처리
def process_large_dataset(data):
    """대용량 데이터 처리 시 메모리 효율적 방법 사용"""
    for chunk in chunked(data, 1000):  # 청크 단위 처리
        process_chunk(chunk)
```

#### 보안 요구사항  
```python
# 사용자 입력 검증
def validate_city_name(city_name):
    """도시명 입력 검증"""
    if not isinstance(city_name, str):
        raise ValueError("도시명은 문자열이어야 합니다")
    
    if len(city_name) > 50:
        raise ValueError("도시명이 너무 깁니다")
    
    # XSS 방지를 위한 특수문자 제거
    safe_name = re.sub(r'[<>"\']', '', city_name)
    return safe_name

# 민감 정보 로깅 금지
def log_safe_data(data):
    """안전한 데이터만 로깅"""
    safe_data = {k: v for k, v in data.items() 
                 if k not in ['password', 'token', 'key']}
    print(f"데이터: {safe_data}")
```

#### 웹 크롤링 윤리 가이드
```python
# 적절한 대기 시간
MIN_DELAY = 2  # 최소 2초 대기
MAX_DELAY = 5  # 최대 5초 대기

# User-Agent 다양화
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    # 최소 3개 이상 순환 사용
]

# 서버 부하 최소화
def respect_robots_txt():
    """robots.txt 확인 및 준수"""
    # robots.txt 파싱 로직
    pass
```

## 🔍 디버깅 및 자가 점검 시스템

### 🛠️ 오류 진단 템플릿

#### 오류 보고 표준 형식
```markdown
## 오류 보고서

**발생 시점**: 2024-12-07 15:30:00
**파일**: ./src/scraper/parsers.py:145
**함수**: extract_product_name()

**오류 메시지**:
```
Traceback (most recent call last):
  File "./src/scraper/parsers.py", line 145, in extract_product_name
    product_name = element.find('.product-title').text
AttributeError: 'NoneType' object has no attribute 'text'
```

**관련 코드**:
```python
def extract_product_name(driver):
    element = driver.find_element(By.CSS_SELECTOR, '.product-container')
    product_name = element.find('.product-title').text  # 145번째 줄
    return product_name
```

**예상 원인**: CSS 셀렉터 '.product-title'을 찾을 수 없음
**재현 방법**: 도쿄 상품 페이지에서 상품명 추출 시도
**브라우저**: Chrome 120.0.0.0
**운영체제**: Windows 11
```

#### 자가 진단 체크리스트
```python
def self_diagnostic_check():
    """코드 수정 전 자가 진단"""
    
    checklist = [
        "✅ 기존 코드의 동작 원리를 이해했는가?",
        "✅ 수정할 코드의 영향 범위를 파악했는가?", 
        "✅ 의존성이 있는 다른 함수들을 확인했는가?",
        "✅ 에러 처리를 적절히 구현했는가?",
        "✅ 성능에 부정적 영향은 없는가?",
        "✅ 보안상 취약점은 없는가?",
        "✅ 코딩 컨벤션을 준수했는가?",
        "✅ 문서화(주석/docstring)를 완료했는가?",
        "✅ 테스트 방법을 계획했는가?",
    ]
    
    return checklist
```

### 🧪 테스트 및 검증 프로토콜

#### 단위 테스트 템플릿
```python
def test_function_name():
    """함수별 단위 테스트"""
    
    # Given (준비)
    test_input = "서울"
    expected_output = "SEL"
    
    # When (실행)  
    actual_output = get_city_code(test_input)
    
    # Then (검증)
    assert actual_output == expected_output
    print(f"✅ 테스트 통과: {test_input} → {actual_output}")
```

#### 통합 테스트 시나리오
```python
def integration_test_scenario():
    """전체 시스템 통합 테스트"""
    
    # 1. 초기화 테스트
    crawler = KKdayCrawler("서울")
    assert crawler.initialize() == True
    
    # 2. URL 수집 테스트  
    urls = crawler.collect_urls(max_pages=1)
    assert len(urls) > 0
    
    # 3. 데이터 추출 테스트
    success = crawler.crawl_product(urls[0], rank=1)
    assert success == True
    
    # 4. 파일 저장 확인
    csv_path = get_csv_path("서울")
    assert os.path.exists(csv_path)
    
    print("✅ 통합 테스트 모두 통과")
```

## 📊 품질 관리 지표

### 🎯 코드 품질 KPI
- **테스트 커버리지**: 80% 이상
- **함수 복잡도**: 순환복잡도 10 이하  
- **문서화율**: 모든 public 함수 100% 문서화
- **에러 처리율**: 모든 외부 의존성 100% 예외처리

### 🔍 코드 리뷰 체크포인트
```markdown
## 코드 리뷰 체크리스트

**기능성**
- [ ] 요구사항을 올바르게 구현했는가?
- [ ] 엣지 케이스를 고려했는가?
- [ ] 에러 처리가 적절한가?

**성능**  
- [ ] 시간/공간 복잡도가 적절한가?
- [ ] 불필요한 연산이나 메모리 사용은 없는가?
- [ ] 대용량 데이터 처리 시 문제없는가?

**보안**
- [ ] 사용자 입력 검증을 했는가?  
- [ ] SQL 인젝션, XSS 등 취약점은 없는가?
- [ ] 민감 정보 노출 위험은 없는가?

**유지보수성**
- [ ] 코드가 읽기 쉽고 이해하기 쉬운가?
- [ ] 적절한 주석과 문서화가 되어있는가?
- [ ] 재사용 가능한 구조인가?
```

## 🔄 지속적 개선 프로세스

### 📈 성능 모니터링
```python
import time
import psutil

def performance_monitor(func):
    """성능 모니터링 데코레이터"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        
        print(f"⏱️ 실행시간: {end_time - start_time:.2f}초")
        print(f"💾 메모리 사용: {(end_memory - start_memory) / 1024**2:.2f}MB")
        
        return result
    return wrapper
```

### 🔧 지속적 리팩토링
```python
def code_smell_detector():
    """코드 냄새 탐지기"""
    
    smells = [
        "함수 길이 50줄 초과",
        "중복 코드 3회 이상",  
        "과도한 주석 (코드 대비 30% 초과)",
        "매직 넘버 사용",
        "과도한 중첩 (depth 4 초과)",
    ]
    
    return smells
```

---

**문서 버전**: v1.0  
**최종 업데이트**: 2024-12-07  
**적용 범위**: 전체 KKday 크롤링 시스템