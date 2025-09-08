# KKday 크롤링 시스템 - 배포 및 운영 가이드

## 🚀 배포 개요

이 문서는 KKday 크롤링 시스템의 완전한 배포, 운영, 유지보수 가이드를 제공합니다. 개발 환경부터 프로덕션 배포까지 모든 단계를 다룹니다.

## 🎯 배포 전략 및 환경

### 배포 환경 분류

#### 환경별 특성 정의
```yaml
개발환경(Development):
  목적: "개발자 개별 테스트"
  특징: "빠른 수정/테스트, 외부 접근 없음"
  리소스: "최소 요구사양"
  데이터: "샘플 데이터 사용"

스테이징환경(Staging):
  목적: "통합 테스트 및 QA"
  특징: "프로덕션과 동일 구성, 안전한 테스트"
  리소스: "프로덕션의 70% 수준"
  데이터: "익명화된 실제 데이터"

프로덕션환경(Production):
  목적: "실제 서비스 운영"
  특징: "안정성 최우선, 모니터링 필수"
  리소스: "최대 성능 구성"
  데이터: "실제 운영 데이터"
```

### 시스템 요구사항

#### 하드웨어 요구사항
```yaml
최소_사양:
  CPU: "4코어 이상"
  RAM: "8GB 이상"
  스토리지: "100GB SSD"
  네트워크: "100Mbps 이상"

권장_사양:
  CPU: "8코어 이상 (Intel i7/AMD Ryzen 7)"
  RAM: "16GB 이상"
  스토리지: "500GB NVMe SSD"
  네트워크: "1Gbps 이상"

프로덕션_사양:
  CPU: "16코어 이상 (서버급 Xeon/EPYC)"
  RAM: "32GB 이상"
  스토리지: "1TB NVMe SSD RAID 1"
  네트워크: "10Gbps 이상"
  백업: "별도 스토리지 시스템"
```

#### 소프트웨어 요구사항
```yaml
운영체제:
  권장: "Ubuntu 22.04 LTS, CentOS 8, Windows Server 2022"
  지원: "macOS 13+, Windows 11"

Python환경:
  버전: "Python 3.9-3.11 (권장: 3.11.7)"
  패키지관리자: "pip 23.0+, conda (선택)"
  가상환경: "venv, virtualenv, conda"

브라우저:
  Chrome: "120.0+ (필수)"
  ChromeDriver: "자동 관리됨 (undetected-chromedriver)"

의존성:
  - selenium==4.15.0
  - undetected-chromedriver==3.5.4
  - beautifulsoup4==4.12.2
  - requests==2.31.0
  - pillow==10.1.0
  - pandas==2.1.4
  - psutil==5.9.6
```

## 📦 설치 및 구성

### 자동 설치 스크립트

#### Linux/macOS 설치 스크립트
```bash
#!/bin/bash
# install_kkday_crawler.sh - KKday 크롤링 시스템 자동 설치

set -e  # 오류 시 스크립트 중단

echo "🚀 KKday 크롤링 시스템 설치 시작"

# 시스템 정보 확인
echo "📊 시스템 정보 확인 중..."
echo "OS: $(uname -s) $(uname -r)"
echo "Architecture: $(uname -m)"
echo "Available Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Available Disk: $(df -h / | awk 'NR==2 {print $4}')"

# Python 설치 확인
echo "🐍 Python 설치 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되지 않았습니다."
    echo "Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python 버전: $PYTHON_VERSION"

# Python 버전 검증
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "✅ Python 버전 요구사항 충족"
else
    echo "❌ Python 3.9 이상이 필요합니다"
    exit 1
fi

# 작업 디렉터리 생성
INSTALL_DIR="$HOME/kkday-crawler"
echo "📁 설치 디렉터리: $INSTALL_DIR"

if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️ 기존 설치 발견. 백업 생성 중..."
    mv "$INSTALL_DIR" "${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 가상환경 생성
echo "🔧 Python 가상환경 생성 중..."
python3 -m venv venv
source venv/bin/activate

# pip 업그레이드
echo "📦 pip 업그레이드 중..."
pip install --upgrade pip

# 의존성 설치
echo "📦 의존성 패키지 설치 중..."
cat > requirements.txt << EOF
selenium==4.15.0
undetected-chromedriver==3.5.4
beautifulsoup4==4.12.2
requests==2.31.0
pillow==10.1.0
pandas==2.1.4
psutil==5.9.6
jupyter==1.0.0
ipykernel==6.26.0
konlpy==0.6.0
lxml==4.9.3
fake-useragent==1.4.0
EOF

pip install -r requirements.txt

# Chrome 설치 확인
echo "🌐 Chrome 브라우저 확인 중..."
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
    echo "✅ Chrome 브라우저 발견"
else
    echo "⚠️ Chrome 브라우저가 설치되지 않았습니다."
    echo "Ubuntu/Debian: wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - && sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list' && sudo apt update && sudo apt install google-chrome-stable"
    echo "CentOS/RHEL: sudo yum install https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm"
    echo "macOS: brew install --cask google-chrome"
fi

# 프로젝트 구조 생성
echo "📁 프로젝트 구조 생성 중..."
mkdir -p {src/{scraper,utils},data,kkday_img,logs,config,tests}

# 설정 파일 생성
echo "⚙️ 기본 설정 파일 생성 중..."
cat > config/settings.ini << EOF
[DEFAULT]
platform = KKday
base_url = https://www.kkday.com
data_source = KKday
log_level = INFO

[crawling]
default_delay = 3
max_retries = 3
timeout = 30
batch_size = 20

[storage]
data_dir = ./data
image_dir = ./kkday_img
log_dir = ./logs

[performance]
max_memory_mb = 2048
max_cpu_percent = 70
monitoring_interval = 5
EOF

# 시작 스크립트 생성
cat > start.sh << EOF
#!/bin/bash
# KKday 크롤링 시스템 시작 스크립트

cd "\$(dirname "\$0")"
source venv/bin/activate

echo "🚀 KKday 크롤링 시스템 시작"
echo "📊 시스템 상태:"
echo "  - Python: \$(python --version)"
echo "  - 작업 디렉터리: \$(pwd)"
echo "  - 메모리: \$(free -h | awk '/^Mem:/ {print \$3 "/" \$2}')"

# Jupyter 노트북 서버 시작 (선택사항)
if [ "\$1" = "notebook" ]; then
    echo "📓 Jupyter 노트북 서버 시작 중..."
    jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser
else
    echo "💡 사용법:"
    echo "  크롤링 실행: python -m src.scraper.crawler"
    echo "  노트북 실행: ./start.sh notebook"
    echo "  테스트 실행: python -m pytest tests/"
fi
EOF

chmod +x start.sh

# 중지 스크립트 생성
cat > stop.sh << EOF
#!/bin/bash
# KKday 크롤링 시스템 중지 스크립트

echo "🛑 KKday 크롤링 시스템 종료 중..."

# Jupyter 노트북 서버 종료
pkill -f "jupyter-notebook" 2>/dev/null || true

# Chrome 프로세스 정리
pkill -f "chrome" 2>/dev/null || true
pkill -f "chromedriver" 2>/dev/null || true

echo "✅ 시스템 종료 완료"
EOF

chmod +x stop.sh

# 상태 확인 스크립트 생성
cat > status.sh << EOF
#!/bin/bash
# KKday 크롤링 시스템 상태 확인

echo "📊 KKday 크롤링 시스템 상태"
echo "========================================"

# 가상환경 상태
if [ -f "venv/bin/activate" ]; then
    echo "✅ Python 가상환경: 정상"
    source venv/bin/activate
    echo "   Python 버전: \$(python --version)"
    echo "   pip 버전: \$(pip --version | cut -d' ' -f2)"
else
    echo "❌ Python 가상환경: 오류"
fi

# 의존성 확인
echo -n "📦 의존성 패키지: "
if pip list | grep -q selenium; then
    echo "정상"
else
    echo "오류 - requirements.txt 설치 필요"
fi

# 디스크 사용량
echo "💾 디스크 사용량: \$(df -h . | awk 'NR==2 {print \$5}')"

# 메모리 사용량
echo "🧠 메모리 사용량: \$(free -h | awk '/^Mem:/ {print \$3 "/" \$2}')"

# 실행 중인 프로세스
CHROME_PROCESSES=\$(pgrep -c chrome || echo 0)
JUPYTER_PROCESSES=\$(pgrep -c jupyter || echo 0)

echo "🔄 실행 중인 프로세스:"
echo "   Chrome: \$CHROME_PROCESSES개"
echo "   Jupyter: \$JUPYTER_PROCESSES개"

# 로그 파일 확인
if [ -d "logs" ]; then
    LOG_COUNT=\$(ls logs/*.log 2>/dev/null | wc -l)
    echo "📋 로그 파일: \${LOG_COUNT}개"
else
    echo "📋 로그 파일: 없음"
fi

echo "========================================"
EOF

chmod +x status.sh

# 설치 완료 메시지
echo ""
echo "🎉 KKday 크롤링 시스템 설치 완료!"
echo "========================================"
echo "📁 설치 위치: $INSTALL_DIR"
echo "🚀 시작 방법: ./start.sh"
echo "🛑 종료 방법: ./stop.sh"
echo "📊 상태 확인: ./status.sh"
echo "📓 노트북 실행: ./start.sh notebook"
echo ""
echo "💡 다음 단계:"
echo "1. cd $INSTALL_DIR"
echo "2. source venv/bin/activate"
echo "3. 설정 파일 확인 (config/settings.ini)"
echo "4. 첫 테스트 실행"
echo ""
echo "📚 문서: README.md, TECHNICAL_SPECS.md 참조"
echo "🐛 이슈 리포트: GitHub Issues"
```

#### Windows PowerShell 설치 스크립트
```powershell
# install_kkday_crawler.ps1 - Windows용 설치 스크립트

param(
    [string]$InstallPath = "$env:USERPROFILE\kkday-crawler"
)

Write-Host "🚀 KKday 크롤링 시스템 설치 시작" -ForegroundColor Green

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "⚠️ 일부 기능을 위해 관리자 권한을 권장합니다"
}

# 시스템 정보
Write-Host "📊 시스템 정보 확인 중..." -ForegroundColor Yellow
$os = Get-CimInstance -ClassName Win32_OperatingSystem
$cpu = Get-CimInstance -ClassName Win32_Processor
$memory = Get-CimInstance -ClassName Win32_ComputerSystem

Write-Host "OS: $($os.Caption) $($os.Version)"
Write-Host "CPU: $($cpu.Name)"
Write-Host "RAM: $([math]::Round($memory.TotalPhysicalMemory / 1GB, 2)) GB"

# Python 설치 확인
Write-Host "🐍 Python 설치 확인 중..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "✅ $pythonVersion"
    } else {
        throw "Python not found"
    }
} catch {
    Write-Error "❌ Python이 설치되지 않았습니다"
    Write-Host "https://www.python.org/downloads/ 에서 Python 3.9+ 설치"
    exit 1
}

# 설치 디렉터리 생성
Write-Host "📁 설치 디렉터리 생성: $InstallPath" -ForegroundColor Yellow
if (Test-Path $InstallPath) {
    $backupPath = "${InstallPath}_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Move-Item $InstallPath $backupPath
    Write-Host "⚠️ 기존 설치를 $backupPath 로 백업"
}

New-Item -ItemType Directory -Path $InstallPath -Force
Set-Location $InstallPath

# 가상환경 생성
Write-Host "🔧 Python 가상환경 생성 중..." -ForegroundColor Yellow
python -m venv venv
& .\venv\Scripts\Activate.ps1

# 의존성 설치
Write-Host "📦 의존성 패키지 설치 중..." -ForegroundColor Yellow
pip install --upgrade pip

@"
selenium==4.15.0
undetected-chromedriver==3.5.4
beautifulsoup4==4.12.2
requests==2.31.0
pillow==10.1.0
pandas==2.1.4
psutil==5.9.6
jupyter==1.0.0
ipykernel==6.26.0
lxml==4.9.3
fake-useragent==1.4.0
"@ | Out-File -FilePath requirements.txt -Encoding UTF8

pip install -r requirements.txt

# 프로젝트 구조 생성
Write-Host "📁 프로젝트 구조 생성 중..." -ForegroundColor Yellow
$folders = @("src\scraper", "src\utils", "data", "kkday_img", "logs", "config", "tests")
foreach ($folder in $folders) {
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
}

# 설정 파일 생성
Write-Host "⚙️ 기본 설정 파일 생성 중..." -ForegroundColor Yellow
@"
[DEFAULT]
platform = KKday
base_url = https://www.kkday.com
data_source = KKday
log_level = INFO

[crawling]
default_delay = 3
max_retries = 3
timeout = 30
batch_size = 20

[storage]
data_dir = ./data
image_dir = ./kkday_img
log_dir = ./logs

[performance]
max_memory_mb = 2048
max_cpu_percent = 70
monitoring_interval = 5
"@ | Out-File -FilePath config\settings.ini -Encoding UTF8

# 시작 스크립트 생성
@"
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat

echo 🚀 KKday 크롤링 시스템 시작
echo 📊 시스템 상태:
python --version
echo   작업 디렉터리: %cd%

if "%1"=="notebook" (
    echo 📓 Jupyter 노트북 서버 시작 중...
    jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser
) else (
    echo 💡 사용법:
    echo   크롤링 실행: python -m src.scraper.crawler
    echo   노트북 실행: start.bat notebook
    echo   테스트 실행: python -m pytest tests/
    pause
)
"@ | Out-File -FilePath start.bat -Encoding ASCII

# 중지 스크립트 생성
@"
@echo off
echo 🛑 KKday 크롤링 시스템 종료 중...

taskkill /f /im jupyter.exe 2>nul
taskkill /f /im chrome.exe 2>nul
taskkill /f /im chromedriver.exe 2>nul

echo ✅ 시스템 종료 완료
pause
"@ | Out-File -FilePath stop.bat -Encoding ASCII

Write-Host ""
Write-Host "🎉 KKday 크롤링 시스템 설치 완료!" -ForegroundColor Green
Write-Host "========================================"
Write-Host "📁 설치 위치: $InstallPath"
Write-Host "🚀 시작 방법: start.bat"
Write-Host "🛑 종료 방법: stop.bat"
Write-Host "📓 노트북 실행: start.bat notebook"
Write-Host ""
Write-Host "💡 다음 단계:" -ForegroundColor Yellow
Write-Host "1. cd $InstallPath"
Write-Host "2. venv\Scripts\activate"
Write-Host "3. 설정 파일 확인 (config\settings.ini)"
Write-Host "4. 첫 테스트 실행"
```

### 수동 설치 가이드

#### 단계별 수동 설치
```bash
# 1. 기본 환경 준비
# Python 3.9+ 설치 확인
python3 --version  # 3.9.0 이상 확인

# 2. 프로젝트 디렉터리 생성
mkdir kkday-crawler
cd kkday-crawler

# 3. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate.bat  # Windows

# 4. 필수 패키지 설치
pip install --upgrade pip
pip install selenium undetected-chromedriver beautifulsoup4 requests pillow pandas psutil

# 5. 선택적 패키지 설치 (노트북 사용 시)
pip install jupyter ipykernel

# 6. Chrome 브라우저 설치 확인
google-chrome --version  # Linux
# Chrome 브라우저가 없으면 설치 필요

# 7. 프로젝트 구조 생성
mkdir -p {src/{scraper,utils},data,kkday_img,logs,config,tests}

# 8. 기본 설정 파일 생성
cat > config/settings.ini << 'EOF'
[DEFAULT]
platform = KKday
base_url = https://www.kkday.com
data_source = KKday

[crawling]
default_delay = 3
max_retries = 3
timeout = 30
EOF

# 9. 설치 검증
python -c "import selenium, undetected_chromedriver; print('설치 성공')"
```

## ⚙️ 환경 설정 및 구성

### 설정 파일 관리

#### 계층적 설정 시스템
```python
# config/config_manager.py - 설정 관리 시스템
import os
import configparser
import json
from pathlib import Path

class ConfigManager:
    """계층적 설정 관리 시스템"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config = configparser.ConfigParser()
        self.load_configurations()
    
    def load_configurations(self):
        """설정 파일들을 우선순위에 따라 로드"""
        
        config_files = [
            'default.ini',      # 기본 설정
            'environment.ini',  # 환경별 설정
            'local.ini'        # 로컬 오버라이드
        ]
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                self.config.read(config_path, encoding='utf-8')
                print(f"✅ 설정 로드: {config_file}")
            else:
                print(f"⚠️ 설정 파일 없음: {config_file}")
    
    def get(self, section, key, fallback=None):
        """설정 값 조회"""
        # 환경 변수 우선 확인
        env_key = f"KKDAY_{section.upper()}_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value:
            return env_value
        
        # 설정 파일에서 조회
        return self.config.get(section, key, fallback=fallback)
    
    def get_section(self, section_name):
        """섹션 전체 조회"""
        if section_name in self.config:
            return dict(self.config[section_name])
        return {}
    
    def validate_configuration(self):
        """설정 유효성 검증"""
        required_settings = [
            ('DEFAULT', 'platform'),
            ('DEFAULT', 'base_url'),
            ('crawling', 'default_delay'),
            ('storage', 'data_dir')
        ]
        
        missing = []
        for section, key in required_settings:
            if not self.get(section, key):
                missing.append(f"{section}.{key}")
        
        if missing:
            raise ValueError(f"필수 설정 누락: {missing}")
        
        print("✅ 설정 검증 완료")
        return True


# 사용 예시
config = ConfigManager()

# 기본 설정 파일들 생성
def create_default_configs():
    """기본 설정 파일들 생성"""
    
    # default.ini - 기본 설정
    default_config = """
[DEFAULT]
platform = KKday
base_url = https://www.kkday.com
data_source = KKday
log_level = INFO

[crawling]
default_delay = 3
max_retries = 3
timeout = 30
batch_size = 20
max_pages = 10
user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

[storage]
data_dir = ./data
image_dir = ./kkday_img
log_dir = ./logs
csv_encoding = utf-8
image_quality = 85

[performance]
max_memory_mb = 2048
max_cpu_percent = 70
monitoring_interval = 5
gc_threshold = 100

[network]
connection_timeout = 10
read_timeout = 30
max_connections = 10
retry_backoff_factor = 1.0
"""
    
    # environment.ini - 환경별 설정
    env_config = """
[development]
debug = true
log_level = DEBUG
batch_size = 5
default_delay = 5

[staging]
debug = false
log_level = INFO
batch_size = 15
default_delay = 3

[production]
debug = false
log_level = WARNING
batch_size = 20
default_delay = 2
max_memory_mb = 4096
"""
    
    # 설정 디렉터리 생성
    os.makedirs('config', exist_ok=True)
    
    with open('config/default.ini', 'w', encoding='utf-8') as f:
        f.write(default_config.strip())
    
    with open('config/environment.ini', 'w', encoding='utf-8') as f:
        f.write(env_config.strip())
    
    print("✅ 기본 설정 파일 생성 완료")
```

### 환경 변수 관리

#### 환경별 변수 설정
```bash
# .env.development - 개발환경 변수
export KKDAY_ENV=development
export KKDAY_DEFAULT_LOG_LEVEL=DEBUG
export KKDAY_CRAWLING_BATCH_SIZE=5
export KKDAY_CRAWLING_DEFAULT_DELAY=5
export KKDAY_STORAGE_DATA_DIR=./dev_data

# .env.staging - 스테이징환경 변수  
export KKDAY_ENV=staging
export KKDAY_DEFAULT_LOG_LEVEL=INFO
export KKDAY_CRAWLING_BATCH_SIZE=15
export KKDAY_NETWORK_MAX_CONNECTIONS=5

# .env.production - 프로덕션환경 변수
export KKDAY_ENV=production
export KKDAY_DEFAULT_LOG_LEVEL=WARNING
export KKDAY_CRAWLING_BATCH_SIZE=20
export KKDAY_PERFORMANCE_MAX_MEMORY_MB=4096
export KKDAY_NETWORK_MAX_CONNECTIONS=20

# 환경 변수 로드 스크립트
load_environment() {
    local env_file=".env.${KKDAY_ENV:-development}"
    if [ -f "$env_file" ]; then
        source "$env_file"
        echo "✅ 환경 변수 로드: $env_file"
    else
        echo "⚠️ 환경 파일 없음: $env_file"
    fi
}
```

## 🔄 CI/CD 파이프라인

### GitHub Actions 워크플로우

#### 자동화된 테스트 및 배포
```yaml
# .github/workflows/ci-cd.yml
name: KKday Crawler CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

env:
  PYTHON_VERSION: '3.11'
  
jobs:
  test:
    name: 테스트 실행
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
    - name: 코드 체크아웃
      uses: actions/checkout@v4
      
    - name: Python ${{ matrix.python-version }} 설정
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Chrome 설치
      uses: browser-actions/setup-chrome@latest
      
    - name: 의존성 캐시
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        
    - name: 의존성 설치
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-html
        
    - name: 린트 검사
      run: |
        pip install flake8 black
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check src/
        
    - name: 단위 테스트
      run: |
        pytest tests/unit/ -v --cov=src --cov-report=xml
        
    - name: 통합 테스트
      run: |
        pytest tests/integration/ -v --html=reports/integration_test.html
        
    - name: 테스트 결과 업로드
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{ matrix.python-version }}
        path: reports/
        
    - name: 코드 커버리지 업로드
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security-scan:
    name: 보안 스캔
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - name: 코드 체크아웃
      uses: actions/checkout@v4
      
    - name: Python 보안 스캔
      uses: pypa/gh-action-pip-audit@v1.0.8
      with:
        inputs: requirements.txt
        
    - name: 의존성 취약점 검사
      run: |
        pip install safety
        safety check --json --output safety-report.json
        
    - name: 코드 품질 분석
      uses: github/super-linter@v4
      env:
        DEFAULT_BRANCH: main
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  build:
    name: 빌드 및 패키징
    runs-on: ubuntu-latest
    needs: [test, security-scan]
    
    steps:
    - name: 코드 체크아웃
      uses: actions/checkout@v4
      
    - name: Python 설정
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: 빌드 도구 설치
      run: |
        python -m pip install --upgrade pip
        pip install build wheel setuptools
        
    - name: 패키지 빌드
      run: |
        python -m build
        
    - name: 아티팩트 업로드
      uses: actions/upload-artifact@v3
      with:
        name: distributions
        path: dist/

  deploy-staging:
    name: 스테이징 배포
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - name: 아티팩트 다운로드
      uses: actions/download-artifact@v3
      with:
        name: distributions
        path: dist/
        
    - name: 스테이징 서버 배포
      run: |
        echo "🚀 스테이징 서버 배포 중..."
        # 실제 배포 스크립트 실행
        # ssh-keyscan -H ${{ secrets.STAGING_HOST }} >> ~/.ssh/known_hosts
        # scp -r dist/ ${{ secrets.STAGING_USER }}@${{ secrets.STAGING_HOST }}:~/kkday-crawler/
        # ssh ${{ secrets.STAGING_USER }}@${{ secrets.STAGING_HOST }} 'cd ~/kkday-crawler && ./deploy.sh staging'
        
    - name: 스모크 테스트
      run: |
        echo "🧪 스테이징 환경 스모크 테스트 실행"
        # curl -f http://staging.kkday-crawler.internal/health
        
  deploy-production:
    name: 프로덕션 배포
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'release'
    environment: production
    
    steps:
    - name: 배포 승인 대기
      uses: trstringer/manual-approval@v1
      with:
        secret: ${{ github.TOKEN }}
        approvers: team-leads,devops-team
        
    - name: 아티팩트 다운로드
      uses: actions/download-artifact@v3
      with:
        name: distributions
        path: dist/
        
    - name: 프로덕션 배포
      run: |
        echo "🚀 프로덕션 배포 중..."
        # 블루-그린 배포 스크립트 실행
        
    - name: 배포 검증
      run: |
        echo "✅ 배포 검증 중..."
        # 헬스 체크 및 기본 기능 테스트
```

### Docker 컨테이너화

#### 운영용 Dockerfile
```dockerfile
# Dockerfile - 프로덕션용 컨테이너
FROM python:3.11-slim

# 메타데이터
LABEL maintainer="kkday-crawler-team"
LABEL version="1.0"
LABEL description="KKday Crawler System"

# 환경 변수
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# 시스템 패키지 업데이트 및 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Chrome 및 ChromeDriver 설치
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉터리 설정
WORKDIR /app

# Python 의존성 먼저 복사 및 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 권한 설정
RUN useradd -m -u 1000 crawler \
    && chown -R crawler:crawler /app
USER crawler

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import selenium; print('Health OK')" || exit 1

# 포트 노출 (Jupyter 노트북용)
EXPOSE 8888

# 볼륨 마운트 포인트
VOLUME ["/app/data", "/app/kkday_img", "/app/logs"]

# 기본 명령
CMD ["python", "-m", "src.scraper.crawler"]
```

#### Docker Compose 구성
```yaml
# docker-compose.yml - 전체 서비스 구성
version: '3.8'

services:
  kkday-crawler:
    build: .
    image: kkday-crawler:latest
    container_name: kkday-crawler-app
    restart: unless-stopped
    
    environment:
      - KKDAY_ENV=production
      - KKDAY_DEFAULT_LOG_LEVEL=INFO
      - DISPLAY=:99
      
    volumes:
      - ./data:/app/data
      - ./kkday_img:/app/kkday_img
      - ./logs:/app/logs
      - ./config:/app/config
      
    networks:
      - kkday-network
      
    depends_on:
      - redis
      - prometheus
    
    # 리소스 제한
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '2'
          memory: 2G
    
    # 헬스 체크
    healthcheck:
      test: ["CMD", "python", "-c", "import psutil; exit(0 if psutil.cpu_percent() < 90 else 1)"]
      interval: 30s
      timeout: 10s
      retries: 3

  jupyter-notebook:
    build: .
    image: kkday-crawler:latest
    container_name: kkday-jupyter
    restart: unless-stopped
    
    command: ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
    
    ports:
      - "8888:8888"
      
    volumes:
      - ./:/app
      
    environment:
      - JUPYTER_ENABLE_LAB=yes
      
    networks:
      - kkday-network

  redis:
    image: redis:7-alpine
    container_name: kkday-redis
    restart: unless-stopped
    
    ports:
      - "6379:6379"
      
    volumes:
      - redis-data:/data
      
    networks:
      - kkday-network
      
    command: ["redis-server", "--appendonly", "yes"]

  prometheus:
    image: prom/prometheus:latest
    container_name: kkday-prometheus
    restart: unless-stopped
    
    ports:
      - "9090:9090"
      
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
      
    networks:
      - kkday-network

  grafana:
    image: grafana/grafana:latest
    container_name: kkday-grafana
    restart: unless-stopped
    
    ports:
      - "3000:3000"
      
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
      
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      
    networks:
      - kkday-network

volumes:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  kkday-network:
    driver: bridge
```

## 🔍 모니터링 및 로깅

### 통합 로깅 시스템

#### 구조화된 로깅 구현
```python
# src/utils/logger.py - 통합 로깅 시스템
import logging
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

class KKdayLogger:
    """KKday 크롤링 시스템 전용 로거"""
    
    def __init__(self, name="kkday-crawler", log_dir="logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 핸들러 중복 방지
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """로그 핸들러 설정"""
        
        # 포맷터 설정
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        
        json_formatter = JsonFormatter()
        
        # 1. 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # 2. 파일 핸들러 (일반 로그)
        file_handler = RotatingFileHandler(
            filename=self.log_dir / f"{self.name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)
        
        # 3. 오류 전용 핸들러
        error_handler = TimedRotatingFileHandler(
            filename=self.log_dir / f"{self.name}-error.log",
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)
        
        # 4. JSON 구조화 로그 (모니터링용)
        json_handler = TimedRotatingFileHandler(
            filename=self.log_dir / f"{self.name}-structured.jsonl",
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(json_formatter)
        self.logger.addHandler(json_handler)
    
    def debug(self, message, **kwargs):
        """디버그 로그"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message, **kwargs):
        """정보 로그"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message, **kwargs):
        """경고 로그"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message, exception=None, **kwargs):
        """오류 로그"""
        if exception:
            kwargs['exception_type'] = type(exception).__name__
            kwargs['exception_message'] = str(exception)
        self.logger.error(message, extra=kwargs, exc_info=exception)
    
    def critical(self, message, **kwargs):
        """치명적 오류 로그"""
        self.logger.critical(message, extra=kwargs)
    
    # 특수 용도 로깅 메소드들
    def crawl_start(self, city, url_count):
        """크롤링 시작 로그"""
        self.info("크롤링 시작", 
                 event_type="crawl_start",
                 city=city, 
                 url_count=url_count)
    
    def crawl_success(self, url, duration):
        """크롤링 성공 로그"""
        self.info("크롤링 성공",
                 event_type="crawl_success", 
                 url=url, 
                 duration=duration)
    
    def crawl_error(self, url, error, duration):
        """크롤링 오류 로그"""
        self.error("크롤링 실패",
                  event_type="crawl_error",
                  url=url, 
                  error=str(error),
                  duration=duration)
    
    def performance_metric(self, metric_name, value, unit=""):
        """성능 메트릭 로그"""
        self.info("성능 메트릭",
                 event_type="performance_metric",
                 metric=metric_name,
                 value=value,
                 unit=unit)


class JsonFormatter(logging.Formatter):
    """JSON 형태 로그 포맷터"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # extra 필드 추가
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 
                          'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process',
                          'message', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


# 로거 인스턴스 생성 및 사용
logger = KKdayLogger()

# 사용 예시
def example_usage():
    """로거 사용 예시"""
    
    logger.info("시스템 시작", version="1.0", environment="production")
    
    try:
        # 크롤링 작업
        logger.crawl_start("서울", 100)
        # ... 작업 수행
        logger.crawl_success("https://example.com", 3.2)
        
    except Exception as e:
        logger.crawl_error("https://example.com", e, 5.1)
    
    logger.performance_metric("memory_usage", 1024, "MB")
```

### 시스템 모니터링 대시보드

#### Prometheus 메트릭 수집
```python
# src/monitoring/metrics.py - Prometheus 메트릭
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil
import threading
import time

class KKdayMetrics:
    """KKday 크롤링 시스템 메트릭 수집기"""
    
    def __init__(self, port=8000):
        self.port = port
        
        # 카운터 메트릭
        self.crawl_requests_total = Counter(
            'kkday_crawl_requests_total',
            'Total number of crawl requests',
            ['city', 'status']
        )
        
        self.data_extracted_total = Counter(
            'kkday_data_extracted_total', 
            'Total number of data points extracted',
            ['data_type']
        )
        
        # 히스토그램 메트릭
        self.crawl_duration_seconds = Histogram(
            'kkday_crawl_duration_seconds',
            'Time spent on crawling requests',
            ['city'],
            buckets=[1, 2, 5, 10, 30, 60, 120, 300]
        )
        
        self.response_time_seconds = Histogram(
            'kkday_response_time_seconds',
            'HTTP response time',
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
        )
        
        # 게이지 메트릭
        self.memory_usage_bytes = Gauge(
            'kkday_memory_usage_bytes',
            'Current memory usage in bytes'
        )
        
        self.cpu_usage_percent = Gauge(
            'kkday_cpu_usage_percent',
            'Current CPU usage percentage'
        )
        
        self.active_crawlers = Gauge(
            'kkday_active_crawlers',
            'Number of active crawler instances'
        )
        
        self.queue_size = Gauge(
            'kkday_queue_size',
            'Current size of crawling queue',
            ['queue_type']
        )
    
    def start_metrics_server(self):
        """메트릭 서버 시작"""
        start_http_server(self.port)
        print(f"📊 메트릭 서버 시작: http://localhost:{self.port}/metrics")
        
        # 시스템 메트릭 주기적 업데이트
        self._start_system_metrics_updater()
    
    def _start_system_metrics_updater(self):
        """시스템 메트릭 자동 업데이트"""
        def update_system_metrics():
            while True:
                try:
                    # 메모리 사용량
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    self.memory_usage_bytes.set(memory_info.rss)
                    
                    # CPU 사용률
                    cpu_percent = psutil.cpu_percent()
                    self.cpu_usage_percent.set(cpu_percent)
                    
                    time.sleep(5)  # 5초마다 업데이트
                    
                except Exception as e:
                    print(f"⚠️ 시스템 메트릭 업데이트 오류: {e}")
                    time.sleep(10)
        
        metrics_thread = threading.Thread(target=update_system_metrics)
        metrics_thread.daemon = True
        metrics_thread.start()
    
    # 메트릭 기록 메소드들
    def record_crawl_request(self, city, status='success'):
        """크롤링 요청 기록"""
        self.crawl_requests_total.labels(city=city, status=status).inc()
    
    def record_crawl_duration(self, city, duration):
        """크롤링 소요시간 기록"""
        self.crawl_duration_seconds.labels(city=city).observe(duration)
    
    def record_response_time(self, duration):
        """응답시간 기록"""
        self.response_time_seconds.observe(duration)
    
    def record_data_extraction(self, data_type='product'):
        """데이터 추출 기록"""
        self.data_extracted_total.labels(data_type=data_type).inc()
    
    def set_active_crawlers(self, count):
        """활성 크롤러 수 설정"""
        self.active_crawlers.set(count)
    
    def set_queue_size(self, queue_type, size):
        """큐 크기 설정"""
        self.queue_size.labels(queue_type=queue_type).set(size)


# 메트릭 데코레이터
metrics = KKdayMetrics()

def track_crawl_performance(city):
    """크롤링 성능 추적 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                metrics.record_crawl_request(city, 'success')
                metrics.record_crawl_duration(city, duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                metrics.record_crawl_request(city, 'error')
                metrics.record_crawl_duration(city, duration)
                
                raise e
        return wrapper
    return decorator


# Grafana 대시보드 설정
grafana_dashboard_config = """
{
  "dashboard": {
    "title": "KKday 크롤링 시스템 모니터링",
    "panels": [
      {
        "title": "크롤링 요청 수",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(kkday_crawl_requests_total[5m])",
            "legendFormat": "{{city}} - {{status}}"
          }
        ]
      },
      {
        "title": "평균 응답시간",
        "type": "graph", 
        "targets": [
          {
            "expr": "kkday_crawl_duration_seconds_bucket",
            "legendFormat": "{{city}}"
          }
        ]
      },
      {
        "title": "시스템 리소스",
        "type": "graph",
        "targets": [
          {
            "expr": "kkday_memory_usage_bytes / 1024 / 1024",
            "legendFormat": "메모리 사용량 (MB)"
          },
          {
            "expr": "kkday_cpu_usage_percent", 
            "legendFormat": "CPU 사용률 (%)"
          }
        ]
      }
    ]
  }
}
"""
```

## 🔧 운영 및 유지보수

### 자동화된 백업 시스템

#### 데이터 백업 스크립트
```bash
#!/bin/bash
# backup.sh - 자동화된 백업 시스템

set -e

# 설정값
BACKUP_DIR="/backup/kkday-crawler"
RETENTION_DAYS=30
DATE=$(date +%Y%m%d_%H%M%S)

echo "🔄 KKday 크롤링 시스템 백업 시작: $DATE"

# 백업 디렉터리 생성
mkdir -p "$BACKUP_DIR/$DATE"

# 1. 데이터 백업
echo "📁 데이터 백업 중..."
if [ -d "./data" ]; then
    tar -czf "$BACKUP_DIR/$DATE/data_backup.tar.gz" -C . data/
    echo "✅ 데이터 백업 완료: $(du -h $BACKUP_DIR/$DATE/data_backup.tar.gz | cut -f1)"
fi

# 2. 이미지 백업 (선택적)
echo "🖼️ 이미지 백업 중..."
if [ -d "./kkday_img" ] && [ "$(du -s ./kkday_img | cut -f1)" -gt 1000 ]; then
    tar -czf "$BACKUP_DIR/$DATE/images_backup.tar.gz" -C . kkday_img/
    echo "✅ 이미지 백업 완료: $(du -h $BACKUP_DIR/$DATE/images_backup.tar.gz | cut -f1)"
else
    echo "⚠️ 이미지 백업 스킵 (용량 부족 또는 디렉터리 없음)"
fi

# 3. 로그 백업
echo "📋 로그 백업 중..."
if [ -d "./logs" ]; then
    tar -czf "$BACKUP_DIR/$DATE/logs_backup.tar.gz" -C . logs/
    echo "✅ 로그 백업 완료: $(du -h $BACKUP_DIR/$DATE/logs_backup.tar.gz | cut -f1)"
fi

# 4. 설정 백업
echo "⚙️ 설정 백업 중..."
if [ -d "./config" ]; then
    tar -czf "$BACKUP_DIR/$DATE/config_backup.tar.gz" -C . config/
    echo "✅ 설정 백업 완료"
fi

# 5. 데이터베이스 백업 (있는 경우)
if command -v sqlite3 &> /dev/null && [ -f "./database.db" ]; then
    echo "🗄️ 데이터베이스 백업 중..."
    sqlite3 ./database.db ".backup $BACKUP_DIR/$DATE/database_backup.db"
    echo "✅ 데이터베이스 백업 완료"
fi

# 6. 백업 메타정보 생성
cat > "$BACKUP_DIR/$DATE/backup_info.txt" << EOF
백업 정보
===============================
백업 시간: $DATE
호스트명: $(hostname)
시스템: $(uname -a)
Python 버전: $(python3 --version 2>/dev/null || echo "N/A")
백업 유형: 전체 백업

백업된 항목:
$(ls -la "$BACKUP_DIR/$DATE/")

총 백업 크기: $(du -sh "$BACKUP_DIR/$DATE" | cut -f1)
EOF

# 7. 오래된 백업 정리
echo "🧹 오래된 백업 정리 중..."
find "$BACKUP_DIR" -type d -name "20*" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true

BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | grep "^20" | wc -l)
echo "📊 현재 백업 개수: $BACKUP_COUNT개 (보존 기간: ${RETENTION_DAYS}일)"

# 8. 백업 검증
echo "✅ 백업 검증 중..."
BACKUP_SIZE=$(du -sb "$BACKUP_DIR/$DATE" | cut -f1)
if [ $BACKUP_SIZE -gt 1000000 ]; then  # 1MB 이상
    echo "✅ 백업 완료: $(du -sh "$BACKUP_DIR/$DATE" | cut -f1)"
    
    # 백업 성공 알림 (선택사항)
    if command -v mail &> /dev/null; then
        echo "KKday 크롤링 시스템 백업이 성공적으로 완료되었습니다." | \
            mail -s "백업 완료 알림 - $DATE" admin@company.com
    fi
else
    echo "❌ 백업 실패: 백업 크기가 너무 작음"
    exit 1
fi

echo "🎉 백업 프로세스 완료"

# crontab 설정 예시 (주석)
# 매일 새벽 2시에 백업 실행
# 0 2 * * * /path/to/backup.sh >> /var/log/kkday-backup.log 2>&1
```

### 시스템 상태 체크

#### 헬스 체크 스크립트
```bash
#!/bin/bash
# health_check.sh - 시스템 헬스 체크

echo "🔍 KKday 크롤링 시스템 헬스 체크"
echo "========================================"

HEALTH_STATUS=0

# 1. Python 환경 체크
echo "🐍 Python 환경 체크..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION"
else
    echo "❌ Python3가 설치되지 않음"
    HEALTH_STATUS=1
fi

# 2. 가상환경 체크
echo "🔧 가상환경 체크..."
if [ -f "venv/bin/activate" ]; then
    echo "✅ 가상환경 존재"
    source venv/bin/activate
    
    # 핵심 패키지 체크
    if python -c "import selenium, undetected_chromedriver" 2>/dev/null; then
        echo "✅ 핵심 패키지 설치됨"
    else
        echo "❌ 핵심 패키지 누락"
        HEALTH_STATUS=1
    fi
else
    echo "❌ 가상환경 없음"
    HEALTH_STATUS=1
fi

# 3. Chrome 브라우저 체크
echo "🌐 Chrome 브라우저 체크..."
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version)
    echo "✅ $CHROME_VERSION"
elif command -v chromium-browser &> /dev/null; then
    CHROME_VERSION=$(chromium-browser --version)
    echo "✅ $CHROME_VERSION"
else
    echo "❌ Chrome 브라우저 없음"
    HEALTH_STATUS=1
fi

# 4. 디스크 공간 체크
echo "💾 디스크 공간 체크..."
DISK_USAGE=$(df . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 90 ]; then
    echo "✅ 디스크 사용률: ${DISK_USAGE}%"
else
    echo "⚠️ 디스크 사용률 높음: ${DISK_USAGE}%"
    HEALTH_STATUS=1
fi

# 5. 메모리 체크
echo "🧠 메모리 체크..."
if command -v free &> /dev/null; then
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')
    echo "✅ 메모리 사용률: $MEMORY_USAGE"
fi

# 6. 필수 디렉터리 체크
echo "📁 디렉터리 구조 체크..."
REQUIRED_DIRS=("src" "data" "kkday_img" "logs" "config")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir 디렉터리 존재"
    else
        echo "❌ $dir 디렉터리 없음"
        mkdir -p "$dir"
        echo "🔧 $dir 디렉터리 생성"
    fi
done

# 7. 설정 파일 체크
echo "⚙️ 설정 파일 체크..."
if [ -f "config/settings.ini" ]; then
    echo "✅ 설정 파일 존재"
else
    echo "❌ 설정 파일 없음"
    HEALTH_STATUS=1
fi

# 8. 로그 파일 크기 체크
echo "📋 로그 파일 체크..."
if [ -d "logs" ]; then
    LOG_SIZE=$(du -sm logs/ 2>/dev/null | cut -f1)
    if [ $LOG_SIZE -gt 1000 ]; then  # 1GB 초과
        echo "⚠️ 로그 파일 크기 큼: ${LOG_SIZE}MB"
        echo "💡 로그 정리 권장: find logs/ -name '*.log' -mtime +30 -delete"
    else
        echo "✅ 로그 파일 크기 정상: ${LOG_SIZE}MB"
    fi
fi

# 9. 네트워크 연결 체크
echo "🌐 네트워크 연결 체크..."
if ping -c 1 www.kkday.com &> /dev/null; then
    echo "✅ KKday 웹사이트 접근 가능"
else
    echo "❌ KKday 웹사이트 접근 불가"
    HEALTH_STATUS=1
fi

# 10. 프로세스 체크
echo "🔄 실행 중인 프로세스 체크..."
CHROME_PROCESSES=$(pgrep -c chrome || echo 0)
PYTHON_PROCESSES=$(pgrep -c python || echo 0)

echo "   Chrome 프로세스: $CHROME_PROCESSES개"
echo "   Python 프로세스: $PYTHON_PROCESSES개"

if [ $CHROME_PROCESSES -gt 10 ]; then
    echo "⚠️ Chrome 프로세스가 많음 (정리 권장)"
fi

echo "========================================"

# 최종 상태 출력
if [ $HEALTH_STATUS -eq 0 ]; then
    echo "🎉 시스템 상태 양호"
    exit 0
else
    echo "⚠️ 시스템에 문제가 있습니다"
    exit 1
fi
```

### 자동 업데이트 시스템

#### 업데이트 스크립트
```bash
#!/bin/bash
# update_system.sh - 자동 업데이트

set -e

echo "🔄 KKday 크롤링 시스템 업데이트 시작"

# 1. 백업 생성
echo "💾 현재 상태 백업 중..."
./backup.sh

# 2. Git 업데이트 (있는 경우)
if [ -d ".git" ]; then
    echo "📥 소스코드 업데이트 중..."
    git fetch origin
    git pull origin main
fi

# 3. 의존성 업데이트
echo "📦 의존성 업데이트 중..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# 4. 설정 검증
echo "⚙️ 설정 검증 중..."
python -c "
import sys
sys.path.append('src')
from utils.config_manager import ConfigManager
config = ConfigManager()
config.validate_configuration()
print('설정 검증 완료')
"

# 5. 데이터 마이그레이션 (필요시)
if [ -f "scripts/migrate.py" ]; then
    echo "🔄 데이터 마이그레이션 실행 중..."
    python scripts/migrate.py
fi

# 6. 테스트 실행
echo "🧪 기본 테스트 실행 중..."
python -c "
import selenium
import undetected_chromedriver
print('핵심 모듈 임포트 성공')
"

# 7. 서비스 재시작 (프로덕션 환경)
if [ "$KKDAY_ENV" = "production" ]; then
    echo "🔄 서비스 재시작 중..."
    ./stop.sh
    sleep 5
    ./start.sh
fi

echo "✅ 업데이트 완료"

# 업데이트 로그 기록
echo "$(date): 시스템 업데이트 완료" >> logs/update.log
```

---

**문서 버전**: v1.0  
**최종 업데이트**: 2024-12-07  
**담당자**: DevOps팀  
**검토 주기**: 월간  
**다음 업데이트**: 2025-01-07