# KKday 크롤링 시스템 - 오류 처리 매뉴얼

## 🚨 오류 분류 체계

### 오류 심각도 레벨
```yaml
LEVEL_1_CRITICAL:    # 시스템 중단 필요
  - Python 인터프리터 오류
  - 메모리 부족 (OutOfMemoryError)
  - 하드웨어 장애
  - 라이센스 만료

LEVEL_2_ERROR:       # 기능 실패, 재시도 가능
  - 웹드라이버 초기화 실패
  - 네트워크 연결 오류
  - 파일 시스템 오류
  - 데이터베이스 연결 실패

LEVEL_3_WARNING:     # 부분 실패, 계속 진행 가능
  - CSS 셀렉터 변경으로 인한 데이터 누락
  - 이미지 다운로드 실패
  - 일부 상품 파싱 오류
  - 속도 제한 경고

LEVEL_4_INFO:        # 예상 가능한 상황
  - 중복 상품 스킵
  - 빈 페이지 감지
  - 캐시 히트
  - 정상 재시도

LEVEL_5_DEBUG:       # 개발자 디버깅 정보
  - 셀렉터 매칭 과정
  - 데이터 변환 과정
  - 성능 측정 정보
  - 내부 상태 변화
```

## 🌐 웹드라이버 관련 오류

### Chrome 드라이버 오류
```python
def handle_chrome_driver_errors():
    """Chrome 드라이버 관련 오류 처리 가이드"""
    
    error_scenarios = {
        "ChromeDriverException": {
            "원인": "Chrome 버전과 ChromeDriver 버전 불일치",
            "증상": "'chromedriver' executable needs to be in PATH",
            "해결방법": [
                "chromedriver_autoinstaller.install() 재실행",
                "Chrome 브라우저 최신버전 업데이트",
                "수동으로 ChromeDriver 다운로드 및 설치"
            ],
            "코드예시": """
try:
    driver = uc.Chrome(options=options)
except Exception as e:
    if "chromedriver" in str(e).lower():
        print("🔧 ChromeDriver 재설치 중...")
        chromedriver_autoinstaller.install()
        driver = uc.Chrome(options=options)
    else:
        raise e
            """,
            "예방책": "정기적인 Chrome 업데이트 체크"
        },
        
        "SessionNotCreatedException": {
            "원인": "Chrome 브라우저가 설치되지 않음",
            "증상": "session not created: This version of ChromeDriver only supports Chrome version XX",
            "해결방법": [
                "Chrome 브라우저 설치 확인",
                "Chrome 경로 환경변수 확인",
                "Chromium 사용 고려"
            ],
            "코드예시": """
def check_chrome_installation():
    import subprocess
    import platform
    
    system = platform.system()
    try:
        if system == "Windows":
            result = subprocess.run(['reg', 'query', r'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split()[-1]
                print(f"✅ Chrome 설치됨: {version}")
                return True
        elif system == "Darwin":  # macOS
            result = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Chrome 설치됨: {result.stdout.strip()}")
                return True
        elif system == "Linux":
            result = subprocess.run(['google-chrome', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Chrome 설치됨: {result.stdout.strip()}")
                return True
                
        print("❌ Chrome이 설치되지 않았습니다.")
        return False
    except Exception as e:
        print(f"⚠️ Chrome 설치 확인 실패: {e}")
        return False
            """,
            "예방책": "시스템 요구사항 체크리스트 작성"
        },
        
        "WebDriverException": {
            "원인": "Chrome 프로세스 종료 또는 통신 오류",
            "증상": "chrome not reachable", "target frame detached",
            "해결방법": [
                "Chrome 프로세스 강제 종료 후 재시작",
                "새로운 웹드라이버 인스턴스 생성",
                "시스템 메모리 확인"
            ],
            "코드예시": """
def restart_chrome_driver(current_driver):
    try:
        if current_driver:
            current_driver.quit()
    except:
        pass  # 이미 종료된 경우 무시
    
    # Chrome 프로세스 강제 종료 (Windows)
    if platform.system() == "Windows":
        subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], 
                      capture_output=True)
    
    time.sleep(5)  # 프로세스 완전 종료 대기
    return setup_driver()  # 새 드라이버 생성
            """,
            "예방책": "정기적인 드라이버 재시작 (500개 상품마다)"
        }
    }
    
    return error_scenarios
```

### Selenium 타임아웃 오류
```python
def handle_selenium_timeouts():
    """Selenium 타임아웃 관련 오류 처리"""
    
    timeout_scenarios = {
        "TimeoutException": {
            "원인": "페이지 로딩 시간 초과 또는 요소 대기 시간 초과",
            "증상": "Message: timeout: Timed out receiving message from renderer",
            "해결방법": [
                "페이지 로드 타임아웃 증가 (30→60초)",
                "요소 대기 시간 증가 (10→20초)",
                "네트워크 상태 확인",
                "페이지 새로고침 후 재시도"
            ],
            "코드예시": """
def robust_page_load(driver, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            driver.set_page_load_timeout(60)  # 60초로 증가
            driver.get(url)
            
            # 페이지 로드 완료 확인
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
            
        except TimeoutException:
            print(f"⏰ 타임아웃 발생 (시도 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(10)  # 10초 대기 후 재시도
                continue
            else:
                print(f"❌ 최대 재시도 초과: {url}")
                return False
            """,
            "예방책": "네트워크 품질 모니터링, 적절한 타임아웃 설정"
        },
        
        "NoSuchElementException": {
            "원인": "CSS 셀렉터가 변경되었거나 요소가 동적으로 로드됨",
            "증상": "Unable to locate element",
            "해결방법": [
                "백업 셀렉터 사용",
                "동적 대기 구현",
                "페이지 소스 분석",
                "셀렉터 업데이트"
            ],
            "코드예시": """
def find_element_with_fallbacks(driver, selectors_list):
    \"\"\"다중 셀렉터로 요소 찾기\"\"\"
    
    for i, selector in enumerate(selectors_list):
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            if i > 0:  # 백업 셀렉터로 찾은 경우
                print(f"⚠️ 백업 셀렉터 {i+1} 사용: {selector}")
            return element
            
        except (TimeoutException, NoSuchElementException):
            print(f"🔍 셀렉터 {i+1} 실패: {selector}")
            continue
    
    # 모든 셀렉터 실패 시 페이지 소스 분석
    print("🔬 페이지 소스 분석 중...")
    analyze_page_structure(driver)
    return None

def analyze_page_structure(driver):
    \"\"\"페이지 구조 분석 및 가능한 셀렉터 제안\"\"\"
    try:
        # 주요 컨테이너 확인
        containers = driver.find_elements(By.CSS_SELECTOR, 
                                        "div[class*='product'], div[class*='item'], div[class*='card']")
        print(f"📊 상품 컨테이너 후보: {len(containers)}개")
        
        for i, container in enumerate(containers[:3]):  # 상위 3개만 분석
            class_name = container.get_attribute("class")
            print(f"   {i+1}. 클래스: {class_name}")
            
    except Exception as e:
        print(f"⚠️ 페이지 분석 실패: {e}")
            """,
            "예방책": "정기적인 웹사이트 구조 변화 모니터링"
        }
    }
    
    return timeout_scenarios
```

## 💾 데이터 처리 오류

### CSV 파일 처리 오류
```python
def handle_csv_errors():
    """CSV 파일 관련 오류 처리"""
    
    csv_error_scenarios = {
        "PermissionError": {
            "원인": "CSV 파일이 다른 프로그램(Excel 등)에서 열려있음",
            "증상": "[Errno 13] Permission denied",
            "해결방법": [
                "파일 사용 중인 프로그램 종료",
                "임시 파일명으로 저장 후 이동",
                "파일 락 확인 및 대기"
            ],
            "코드예시": """
def safe_csv_write(file_path, data, max_retries=5):
    import tempfile
    import shutil
    
    for attempt in range(max_retries):
        try:
            # 직접 저장 시도
            with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                writer.writerow(data)
            return True
            
        except PermissionError:
            if attempt < max_retries - 1:
                print(f"📄 CSV 파일 사용 중, 재시도 {attempt + 1}/{max_retries}")
                time.sleep(2)  # 2초 대기
                continue
            else:
                # 임시 파일로 저장
                print("💾 임시 파일로 저장 중...")
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
                temp_path = temp_file.name
                
                with open(temp_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=data.keys())
                    writer.writerow(data)
                
                print(f"⚠️ 임시 파일 저장됨: {temp_path}")
                print("💡 Excel 등에서 원본 파일을 닫은 후 수동으로 병합하세요.")
                return temp_path
            """,
            "예방책": "CSV 파일 전용 뷰어 사용, Excel 사용 금지"
        },
        
        "UnicodeDecodeError": {
            "원인": "CSV 파일 인코딩 문제 (한글 깨짐)",
            "증상": "'utf-8' codec can't decode byte",
            "해결방법": [
                "UTF-8 BOM 사용",
                "인코딩 자동 감지",
                "강제 UTF-8 변환"
            ],
            "코드예시": """
def read_csv_with_encoding_detection(file_path):
    import chardet
    
    # 인코딩 자동 감지
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        encoding_result = chardet.detect(raw_data)
        detected_encoding = encoding_result['encoding']
        confidence = encoding_result['confidence']
    
    print(f"🔍 감지된 인코딩: {detected_encoding} (신뢰도: {confidence:.2f})")
    
    # 인코딩별 시도 순서
    encodings_to_try = [
        'utf-8-sig',    # UTF-8 BOM
        detected_encoding,
        'cp949',        # Windows 한국어
        'euc-kr',       # 리눅스 한국어
        'utf-8',        # UTF-8 (BOM 없음)
        'latin1'        # 최후의 수단
    ]
    
    for encoding in encodings_to_try:
        if encoding is None:
            continue
            
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                print(f"✅ 성공 인코딩: {encoding}")
                return content
        except UnicodeDecodeError:
            print(f"❌ 실패 인코딩: {encoding}")
            continue
    
    print("🚨 모든 인코딩 시도 실패")
    return None
            """,
            "예방책": "항상 UTF-8 BOM으로 저장"
        },
        
        "DictWriter_FieldError": {
            "원인": "CSV 헤더와 데이터 필드 불일치",
            "증상": "ValueError: dict contains fields not in fieldnames",
            "해결방법": [
                "동적 필드명 생성",
                "데이터 필드 검증",
                "누락 필드 기본값 추가"
            ],
            "코드예시": """
def dynamic_csv_write(file_path, product_data):
    # 파일 존재 여부 확인
    file_exists = os.path.exists(file_path)
    
    if file_exists:
        # 기존 헤더 읽기
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            existing_fieldnames = reader.fieldnames or []
    else:
        existing_fieldnames = []
    
    # 새로운 필드명 병합
    new_fieldnames = list(product_data.keys())
    all_fieldnames = list(dict.fromkeys(existing_fieldnames + new_fieldnames))  # 중복 제거
    
    # 누락된 필드 기본값 추가
    complete_data = {}
    for field in all_fieldnames:
        complete_data[field] = product_data.get(field, "")  # 누락 시 빈 문자열
    
    # 헤더가 변경된 경우 전체 파일 다시 쓰기
    if set(existing_fieldnames) != set(all_fieldnames) and file_exists:
        print("📋 CSV 헤더 업데이트 중...")
        
        # 기존 데이터 읽기
        existing_data = []
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 누락 필드 추가
                complete_row = {}
                for field in all_fieldnames:
                    complete_row[field] = row.get(field, "")
                existing_data.append(complete_row)
        
        # 전체 파일 다시 쓰기
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=all_fieldnames)
            writer.writeheader()
            writer.writerows(existing_data)
            writer.writerow(complete_data)
    else:
        # 일반적인 추가 모드
        with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=all_fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(complete_data)
            """,
            "예방책": "표준 데이터 스키마 정의 및 검증"
        }
    }
    
    return csv_error_scenarios
```

### 이미지 다운로드 오류
```python
def handle_image_errors():
    """이미지 다운로드 관련 오류 처리"""
    
    image_error_scenarios = {
        "ConnectionError": {
            "원인": "이미지 서버 연결 실패 또는 네트워크 오류",
            "증상": "HTTPSConnectionPool: Max retries exceeded",
            "해결방법": [
                "재시도 메커니즘 구현",
                "타임아웃 증가",
                "다른 이미지 URL 시도"
            ],
            "코드예시": """
def download_image_with_retry(image_url, save_path, max_retries=3):
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    # 재시도 설정
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=2,  # 지수적 백오프
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.kkday.com/',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
    }
    
    try:
        response = session.get(image_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # 파일 크기 체크
        content_length = response.headers.get('content-length')
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            if size_mb > 10:  # 10MB 초과
                print(f"⚠️ 이미지 크기 초과: {size_mb:.1f}MB")
                return False
        
        # 파일 저장
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ 이미지 다운로드 완료: {os.path.basename(save_path)}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 이미지 다운로드 실패: {e}")
        return False
    finally:
        session.close()
            """,
            "예방책": "이미지 URL 유효성 사전 체크"
        },
        
        "PIL_Error": {
            "원인": "이미지 파일 손상 또는 지원하지 않는 포맷",
            "증상": "cannot identify image file", "Image file is truncated",
            "해결방법": [
                "이미지 무결성 검사",
                "포맷 변환",
                "원본 이미지 재다운로드"
            ],
            "코드예시": """
def validate_and_process_image(image_path, target_width=400):
    from PIL import Image, ImageFile
    
    # 손상된 이미지 처리 허용
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    
    try:
        with Image.open(image_path) as img:
            # 기본 정보 확인
            print(f"📊 이미지 정보: {img.size}, {img.format}, {img.mode}")
            
            # 이미지 무결성 검사
            img.verify()
            
            # 파일 다시 열기 (verify 후에는 재사용 불가)
            with Image.open(image_path) as img:
                # RGB 변환
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # 크기 조정
                if img.width > target_width:
                    ratio = target_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)
                
                # 최적화된 JPEG로 저장
                quality = 85
                img.save(image_path, 'JPEG', quality=quality, optimize=True)
                
                file_size = os.path.getsize(image_path) / 1024  # KB
                print(f"✅ 이미지 처리 완료: {file_size:.1f}KB")
                return True
                
    except Exception as e:
        print(f"❌ 이미지 처리 실패: {e}")
        
        # 손상된 파일 삭제
        try:
            os.remove(image_path)
            print("🗑️ 손상된 이미지 파일 삭제")
        except:
            pass
        
        return False
            """,
            "예방책": "이미지 다운로드 후 즉시 검증"
        }
    }
    
    return image_error_scenarios
```

## 🌐 웹사이트 관련 오류

### KKday 웹사이트 변경 대응
```python
def handle_website_changes():
    """웹사이트 구조 변경 대응"""
    
    website_change_scenarios = {
        "Layout_Change": {
            "감지방법": "기존 셀렉터로 요소를 찾을 수 없음",
            "대응전략": [
                "백업 셀렉터 순차 시도",
                "페이지 구조 자동 분석",
                "관리자에게 알림 발송"
            ],
            "코드예시": """
def detect_layout_changes(driver, expected_selectors):
    \"\"\"레이아웃 변경 감지 및 대응\"\"\"
    
    change_detected = False
    failed_selectors = []
    
    for selector_name, selector_value in expected_selectors.items():
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector_value)
            if not element.is_displayed():
                failed_selectors.append(selector_name)
                change_detected = True
        except NoSuchElementException:
            failed_selectors.append(selector_name)
            change_detected = True
    
    if change_detected:
        print(f"🚨 웹사이트 레이아웃 변경 감지!")
        print(f"   실패한 셀렉터: {', '.join(failed_selectors)}")
        
        # 자동 복구 시도
        recovery_success = attempt_automatic_recovery(driver, failed_selectors)
        
        if not recovery_success:
            # 관리자 알림
            send_layout_change_alert(failed_selectors, driver.current_url)
    
    return not change_detected

def attempt_automatic_recovery(driver, failed_selectors):
    \"\"\"자동 복구 시도\"\"\"
    
    recovery_patterns = {
        'product_title': [
            'h1[class*="title"]',
            '[data-testid*="title"]',
            '.product-name',
            '.item-title'
        ],
        'product_price': [
            '[class*="price"]',
            '[data-testid*="price"]', 
            '.cost',
            '.amount'
        ]
    }
    
    recovered_count = 0
    
    for selector_name in failed_selectors:
        if selector_name in recovery_patterns:
            for backup_selector in recovery_patterns[selector_name]:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, backup_selector)
                    if element.is_displayed():
                        print(f"🔧 {selector_name} 복구 성공: {backup_selector}")
                        recovered_count += 1
                        break
                except NoSuchElementException:
                    continue
    
    return recovered_count == len(failed_selectors)
            """,
            "예방책": "정기적인 웹사이트 모니터링 봇 운영"
        },
        
        "Anti_Bot_Measures": {
            "감지방법": "캡차, 차단 페이지, 비정상적인 응답",
            "대응전략": [
                "User-Agent 변경",
                "요청 간격 증가", 
                "세션 초기화"
            ],
            "코드예시": """
def detect_anti_bot_measures(driver):
    \"\"\"봇 차단 감지\"\"\"
    
    page_source = driver.page_source.lower()
    current_url = driver.current_url.lower()
    page_title = driver.title.lower()
    
    # 차단 패턴 감지
    blocking_indicators = [
        'captcha', 'recaptcha', 'hcaptcha',
        'blocked', 'forbidden', '403',
        'rate limit', 'too many requests',
        'access denied', 'security check',
        'human verification', 'robot'
    ]
    
    for indicator in blocking_indicators:
        if (indicator in page_source or 
            indicator in current_url or 
            indicator in page_title):
            
            print(f"🚫 봇 차단 감지: {indicator}")
            return handle_blocking_response(driver, indicator)
    
    return False

def handle_blocking_response(driver, block_type):
    \"\"\"차단 대응 처리\"\"\"
    
    if 'captcha' in block_type:
        print("🧩 캡차 감지 - 수동 개입 필요")
        input("캡차를 수동으로 해결한 후 Enter를 누르세요...")
        return True
    
    elif 'rate limit' in block_type or 'too many' in block_type:
        print("⏱️ 속도 제한 감지 - 긴 대기 모드")
        time.sleep(random.uniform(300, 600))  # 5-10분 대기
        return True
    
    elif 'blocked' in block_type or 'forbidden' in block_type:
        print("🛑 완전 차단 감지 - 24시간 대기 권장")
        return False
    
    else:
        print(f"❓ 알 수 없는 차단 유형: {block_type}")
        time.sleep(60)  # 1분 대기
        return True
            """,
            "예방책": "자연스러운 브라우징 패턴 유지"
        }
    }
    
    return website_change_scenarios
```

## 📊 시스템 리소스 오류

### 메모리 부족 오류
```python
def handle_memory_issues():
    """메모리 관련 오류 처리"""
    
    memory_scenarios = {
        "OutOfMemoryError": {
            "감지방법": "시스템 메모리 사용률 90% 초과",
            "대응방법": [
                "브라우저 재시작",
                "가비지 컬렉션 강제 실행",
                "이미지 처리 최적화"
            ],
            "코드예시": """
import psutil
import gc

def monitor_memory_usage():
    \"\"\"메모리 사용량 모니터링\"\"\"
    
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    available_mb = memory.available / (1024 * 1024)
    
    print(f"💾 메모리 사용률: {memory_percent:.1f}%")
    print(f"💾 사용 가능: {available_mb:.0f}MB")
    
    # 경고 수준 체크
    if memory_percent > 90:
        print("🚨 메모리 부족 위험!")
        return emergency_memory_cleanup()
    elif memory_percent > 80:
        print("⚠️ 메모리 사용량 높음")
        return proactive_memory_cleanup()
    
    return True

def emergency_memory_cleanup():
    \"\"\"긴급 메모리 정리\"\"\"
    
    print("🧹 긴급 메모리 정리 실행...")
    
    # 1. 가비지 컬렉션 강제 실행
    collected = gc.collect()
    print(f"   🗑️ 가비지 컬렉션: {collected}개 객체 정리")
    
    # 2. 브라우저 재시작 필요 신호
    return False  # 브라우저 재시작 필요

def proactive_memory_cleanup():
    \"\"\"예방적 메모리 정리\"\"\"
    
    print("🧽 예방적 메모리 정리...")
    
    # 가비지 컬렉션
    gc.collect()
    
    # 임시 파일 정리
    import tempfile
    import shutil
    temp_dir = tempfile.gettempdir()
    
    try:
        for file in os.listdir(temp_dir):
            if file.startswith('tmp') and file.endswith('.jpg'):
                file_path = os.path.join(temp_dir, file)
                if os.path.getmtime(file_path) < time.time() - 3600:  # 1시간 이상 된 파일
                    os.remove(file_path)
    except:
        pass
    
    return True
            """,
            "예방책": "정기적인 메모리 모니터링 (100개 상품마다)"
        }
    }
    
    return memory_scenarios
```

## 🔧 자동 복구 메커니즘

### 종합 오류 처리 시스템
```python
class ComprehensiveErrorHandler:
    \"\"\"종합 오류 처리 클래스\"\"\"
    
    def __init__(self):
        self.error_counts = {}
        self.recovery_attempts = {}
        self.max_retries = 3
        
    def handle_error(self, error_type, error_details, context):
        \"\"\"통합 오류 처리\"\"\"
        
        # 오류 빈도 추적
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        print(f"🚨 오류 발생 [{error_type}]: {error_details}")
        print(f"📊 발생 빈도: {self.error_counts[error_type]}회")
        
        # 오류 유형별 처리
        if error_type.startswith("Chrome"):
            return self._handle_chrome_error(error_details, context)
        elif error_type.startswith("Timeout"):
            return self._handle_timeout_error(error_details, context)
        elif error_type.startswith("Network"):
            return self._handle_network_error(error_details, context)
        elif error_type.startswith("Memory"):
            return self._handle_memory_error(error_details, context)
        else:
            return self._handle_unknown_error(error_details, context)
    
    def _handle_chrome_error(self, error_details, context):
        \"\"\"Chrome 관련 오류 처리\"\"\"
        
        if self.recovery_attempts.get("chrome", 0) < self.max_retries:
            self.recovery_attempts["chrome"] = self.recovery_attempts.get("chrome", 0) + 1
            
            print(f"🔧 Chrome 복구 시도 {self.recovery_attempts['chrome']}/{self.max_retries}")
            
            # 복구 시도
            success = restart_chrome_driver(context.get("driver"))
            
            if success:
                print("✅ Chrome 복구 성공")
                self.recovery_attempts["chrome"] = 0  # 성공 시 카운터 리셋
                return True
            else:
                print("❌ Chrome 복구 실패")
                
        return False
    
    def should_abort_crawling(self):
        \"\"\"크롤링 중단 여부 결정\"\"\"
        
        # 치명적 오류가 반복되면 중단
        critical_errors = ["Chrome", "Memory", "Permission"]
        
        for error_type in critical_errors:
            if self.error_counts.get(error_type, 0) > 5:
                print(f"🛑 치명적 오류 반복 ({error_type}): 크롤링 중단")
                return True
        
        return False

# 사용 예시
error_handler = ComprehensiveErrorHandler()

def safe_crawling_execution(crawling_function, *args, **kwargs):
    \"\"\"안전한 크롤링 실행 래퍼\"\"\"
    
    try:
        return crawling_function(*args, **kwargs)
        
    except Exception as e:
        error_type = type(e).__name__
        context = {
            "function": crawling_function.__name__,
            "args": args,
            "kwargs": kwargs,
            "driver": kwargs.get("driver")
        }
        
        recovery_success = error_handler.handle_error(error_type, str(e), context)
        
        if recovery_success and not error_handler.should_abort_crawling():
            print("🔄 복구 후 재시도...")
            return safe_crawling_execution(crawling_function, *args, **kwargs)
        else:
            print("💥 복구 실패 또는 중단 결정")
            return None
```

---

**문서 버전**: v1.0  
**최종 업데이트**: 2024-12-07  
**다음 문서**: WEBSITE_MAPPING.md