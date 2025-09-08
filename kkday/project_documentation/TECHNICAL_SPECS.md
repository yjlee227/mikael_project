# KKday 크롤링 시스템 - 기술적 상세 명세서

## 🖥️ 환경 요구사항

### 시스템 요구사항
```yaml
운영체제:
  Windows: Windows 10 1903+ (권장: Windows 11)
  macOS: macOS 10.14+ (권장: macOS 12+)
  Linux: Ubuntu 20.04+ / CentOS 8+ (권장)

하드웨어:
  CPU: Intel i5 4세대+ / AMD Ryzen 5 2세대+ (권장: 8코어+)
  RAM: 최소 4GB, 권장 8GB, 최적 16GB
  저장공간: 
    - 시스템: 최소 2GB (프로그램 + 라이브러리)
    - 데이터: 최소 5GB (이미지 + CSV 파일)
    - 임시: 최소 1GB (브라우저 캐시)
  
네트워크:
  대역폭: 최소 10Mbps (권장: 100Mbps)
  안정성: 99% 이상 (장시간 크롤링용)
```

### 소프트웨어 의존성
```yaml
Python:
  버전: 3.8.10+ (권장: 3.11.7)
  설치경로: 환경변수 PATH 등록 필수
  가상환경: venv 또는 conda 사용 권장

Chrome Browser:
  버전: 120.0.0.0+ (최신 안정화 버전)
  설치위치: 기본 경로 (/Program Files/Google/Chrome/)
  옵션: --no-sandbox 플래그 지원 필요

라이브러리 정확한 버전:
  selenium==4.15.2                    # 웹드라이버 (필수)
  undetected-chromedriver==3.5.4      # Chrome 차단 회피 (필수)
  requests==2.31.0                    # HTTP 요청 (필수)
  pillow==10.0.1                      # 이미지 처리 (필수)
  beautifulsoup4==4.12.2              # HTML 파싱 (필수)
  lxml==4.9.3                         # XML 파서 (필수)
  user-agents==2.2.0                  # User-Agent 생성 (필수)
  konlpy==0.6.0                       # 한국어 처리 (선택)
  chromedriver-autoinstaller==0.6.2   # 드라이버 자동설치 (필수)
```

### 권한 및 보안 설정
```yaml
실행 권한:
  Windows: 관리자 권한 불필요 (일반 사용자)
  macOS: sudo 권한 불필요
  Linux: chrome 실행 권한 필요

방화벽 설정:
  아웃바운드: HTTPS(443), HTTP(80) 허용
  인바운드: 특별한 설정 불필요
  
보안 소프트웨어:
  백신: Chrome 자동 업데이트 허용
  방화벽: chromedriver 실행 허용
```

## 📊 데이터 구조 상세 명세

### CSV 데이터 스키마
```python
PRODUCT_DATA_SCHEMA = {
    # 그룹 1: 핵심 식별 정보
    "번호": {
        "type": "string",
        "format": "numeric",
        "max_length": 10,
        "required": True,
        "validation": r"^\d+$",
        "example": "1234"
    },
    "상품명": {
        "type": "string", 
        "max_length": 200,
        "required": True,
        "encoding": "utf-8",
        "sanitization": "HTML 태그 제거, 특수문자 <> 제거",
        "example": "도쿄 디즈니랜드 입장권"
    },
    "가격": {
        "type": "string",
        "format": "numeric_only", 
        "validation": r"^\d+$",
        "preprocessing": "쉼표 제거, 통화기호 제거",
        "null_handling": "0으로 처리",
        "example": "65000"
    },
    "평점": {
        "type": "string",
        "format": "decimal",
        "range": "0.0-5.0",
        "validation": r"^\d+\.\d{1,2}$",
        "null_handling": "0.0으로 처리", 
        "example": "4.8"
    },
    "리뷰수": {
        "type": "string",
        "format": "numeric_only",
        "validation": r"^\d+$", 
        "preprocessing": "괄호, 쉼표 제거",
        "null_handling": "0으로 처리",
        "example": "1234"
    },
    "URL": {
        "type": "string",
        "max_length": 500,
        "required": True,
        "validation": r"^https://www\.kkday\.com/",
        "example": "https://www.kkday.com/ko/product/12345"
    },
    
    # 그룹 2: 위치/지역 정보  
    "도시ID": {
        "type": "string",
        "length": 3,
        "format": "uppercase",
        "validation": r"^[A-Z]{3}$",
        "auto_generated": True,
        "example": "TYO"
    },
    "도시명": {
        "type": "string",
        "max_length": 50, 
        "encoding": "utf-8",
        "normalization": "별칭 → 표준명 자동 변환",
        "example": "도쿄"
    },
    "대륙": {
        "type": "string",
        "enum": ["아시아", "유럽", "북미", "오세아니아", "중동", "아프리카", "남미"],
        "auto_generated": True,
        "example": "아시아" 
    },
    "국가": {
        "type": "string",
        "max_length": 50,
        "auto_generated": True,
        "example": "일본"
    },
    "위치태그": {
        "type": "string",
        "max_length": 200,
        "format": "comma_separated",
        "ai_generated": True,
        "example": "디즈니랜드,테마파크,도쿄"
    },
    
    # 그룹 3: 상품 속성 정보
    "카테고리": {
        "type": "string",
        "max_length": 100, 
        "example": "테마파크"
    },
    "언어": {
        "type": "string",
        "max_length": 100,
        "format": "comma_separated", 
        "example": "한국어,영어,일본어"
    },
    "투어형태": {
        "type": "string", 
        "enum": ["개별", "그룹", "프라이빗", "조인", "자유"],
        "example": "개별"
    },
    "미팅방식": {
        "type": "string",
        "enum": ["픽업", "집합지", "직접방문", "온라인"],
        "example": "집합지"
    },
    "소요시간": {
        "type": "string",
        "max_length": 50,
        "format": "duration",
        "example": "1일"
    },
    "하이라이트": {
        "type": "string",
        "max_length": 500,
        "sanitization": "HTML 태그 제거",
        "example": "세계적인 테마파크 디즈니랜드"
    },
    "순위": {
        "type": "string",
        "format": "numeric",
        "validation": r"^\d+$",
        "example": "1"
    },
    
    # 그룹 4: 메타 정보
    "통화": {
        "type": "string",
        "fixed_value": "KRW",
        "example": "KRW"
    },
    "수집일시": {
        "type": "string", 
        "format": "datetime",
        "pattern": "%Y-%m-%d %H:%M:%S",
        "auto_generated": True,
        "example": "2024-12-07 15:30:00"
    },
    "데이터소스": {
        "type": "string",
        "fixed_value": "KKday",
        "example": "KKday"
    },
    "해시값": {
        "type": "string",
        "length": 12,
        "format": "hex",
        "auto_generated": True,
        "algorithm": "MD5 앞 12자리",
        "example": "abc123def456"
    },
    
    # 그룹 5: 이미지 정보
    "메인이미지": {
        "type": "string",
        "max_length": 200,
        "format": "filename",
        "pattern": r"^[A-Z]{3}_\d{4}\.jpg$",
        "example": "TYO_0001.jpg"
    },
    "썸네일이미지": {
        "type": "string", 
        "max_length": 200,
        "format": "filename", 
        "pattern": r"^[A-Z]{3}_\d{4}_thumb\.jpg$",
        "example": "TYO_0001_thumb.jpg"
    }
}
```

### 파일 저장 구조
```yaml
디렉토리 구조:
  data/                           # CSV 데이터 저장소
    ├── 아시아/                   # 대륙별 분류
    │   ├── 일본/                 # 국가별 분류  
    │   │   ├── 도쿄/             # 도시별 분류
    │   │   │   └── kkday_도쿄_products.csv
    │   │   └── 오사카/
    │   │       └── kkday_오사카_products.csv
    │   └── 싱가포르_통합_kkday_products.csv  # 도시국가
    └── 유럽/
        └── 프랑스/
            └── 파리/
                └── kkday_파리_products.csv

  kkday_img/                      # 이미지 저장소
    ├── 아시아/                   # CSV와 동일한 구조
    │   ├── 일본/
    │   │   ├── 도쿄/
    │   │   │   ├── TYO_0001.jpg
    │   │   │   ├── TYO_0001_thumb.jpg
    │   │   │   └── TYO_0002.jpg
    │   │   └── 오사카/
    │   └── 싱가포르/              # 도시국가는 국가명으로
  
  location_data/                  # AI 학습 데이터
    ├── 아시아/
    │   ├── 일본/
    │   │   └── TYO_keywords.json
    │   └── 싱가포르/
    └── location_keywords.json    # 전역 키워드

파일명 규칙:
  CSV: kkday_{도시명}_products.csv
  통합CSV: {국가명}_통합_kkday_products.csv  
  메인이미지: {도시코드}_{번호:04d}.jpg
  썸네일: {도시코드}_{번호:04d}_thumb.jpg
  키워드: {도시코드}_keywords.json
```

## ⚡ 성능 사양 및 최적화

### 처리 성능 목표
```yaml
속도 지표:
  페이지_로딩: 30초 이내 (timeout)
  요소_대기: 10초 이내 (element wait)
  데이터_추출: 5초 이내 (per product)
  이미지_다운로드: 10초 이내 (per image)
  CSV_저장: 1초 이내 (per record)

처리량 지표:
  시간당_상품수: 720개 (12개/분)
  일일_최대처리: 10,000개
  동시_브라우저: 1개 (메모리 절약)
  분당_요청수: 20개 이하 (서버 부하 고려)

리소스 사용량:
  메모리_사용량: 2GB 이하 (경고: 1.5GB)
  CPU_사용률: 80% 이하 (평균: 30%)
  디스크_IO: 100MB/s 이하
  네트워크: 10Mbps 평균 사용
```

### 메모리 최적화 전략
```python
MEMORY_OPTIMIZATION = {
    "browser_options": [
        "--memory-pressure-off",          # 메모리 압박 모드 해제
        "--max_old_space_size=2048",      # V8 힙 크기 제한
        "--disable-dev-shm-usage",        # 공유 메모리 사용 안함
        "--disable-extensions",           # 확장프로그램 비활성화
        "--disable-plugins",              # 플러그인 비활성화
    ],
    
    "data_processing": {
        "chunk_size": 1000,               # 대용량 데이터 청크 단위
        "image_resize": True,             # 이미지 자동 리사이징
        "memory_cleanup_interval": 100,   # 100개마다 메모리 정리
        "gc_collection": True,            # 가비지 컬렉션 활성화
    },
    
    "limits": {
        "max_images_in_memory": 10,       # 메모리상 최대 이미지 수
        "max_csv_rows_buffer": 1000,      # CSV 버퍼 최대 행수
        "browser_restart_after": 500,     # 500개 후 브라우저 재시작
    }
}
```

## 🔒 보안 및 차단 회피

### User-Agent 관리
```python
USER_AGENT_POOL = {
    "rotation_policy": "random_every_50_requests",  # 50회마다 랜덤 변경
    "pool_size": 20,                                # 20개 User-Agent 풀
    
    "desktop_agents": [
        # Windows Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # macOS Chrome  
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Linux Chrome
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Windows Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        # 추가 16개...
    ],
    
    "mobile_agents": [
        # iPhone
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        # Android
        "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        # 추가 8개...
    ]
}
```

### IP 차단 감지 및 대응
```python
BLOCKING_DETECTION = {
    "detection_patterns": [
        "Access Denied",
        "Blocked",
        "Rate Limited", 
        "403 Forbidden",
        "Too Many Requests",
        "Captcha",
        "Human Verification"
    ],
    
    "response_strategies": {
        "soft_block": {
            "detection": "속도 제한 경고",
            "action": "30-60초 대기 후 재시도", 
            "max_retries": 3
        },
        "hard_block": {
            "detection": "완전 차단", 
            "action": "24시간 대기 또는 중단",
            "notification": "관리자에게 알림"
        },
        "captcha": {
            "detection": "캡차 요구",
            "action": "수동 개입 요청",
            "pause_crawling": True
        }
    }
}
```

### 요청 패턴 자연화
```python
NATURAL_BEHAVIOR = {
    "delays": {
        "page_load": {"min": 2, "max": 5, "distribution": "normal"},
        "scroll": {"min": 0.5, "max": 2, "distribution": "exponential"}, 
        "click": {"min": 0.3, "max": 1, "distribution": "uniform"},
        "typing": {"min": 0.1, "max": 0.3, "distribution": "uniform"}
    },
    
    "patterns": {
        "scroll_behavior": [
            "smooth_reading",      # 부드러운 읽기 패턴
            "comparison_scroll",   # 비교 스크롤 패턴  
            "quick_scan",         # 빠른 스캔 패턴
            "hesitant_browsing"   # 망설이는 브라우징 패턴
        ],
        "click_patterns": [
            "precise_click",       # 정확한 클릭
            "slightly_off_click",  # 약간 빗나간 클릭
            "double_check_click"   # 재확인 클릭
        ]
    },
    
    "session_management": {
        "max_session_duration": 3600,    # 1시간 최대 세션
        "break_intervals": [600, 1800],  # 10분, 30분마다 휴식
        "break_duration": {"min": 30, "max": 300}  # 30초-5분 휴식
    }
}
```

## 🌐 네트워크 및 연결 관리

### 연결 설정
```python
NETWORK_CONFIG = {
    "timeouts": {
        "connection": 30,      # 연결 타임아웃 30초
        "page_load": 60,       # 페이지 로드 60초  
        "script": 30,          # 스크립트 실행 30초
        "element_wait": 10,    # 요소 대기 10초
        "download": 120        # 이미지 다운로드 2분
    },
    
    "retry_config": {
        "max_retries": 3,
        "backoff_factor": 2,      # 지수적 백오프
        "retry_statuses": [429, 502, 503, 504],
        "retry_exceptions": [
            "ConnectionError", 
            "TimeoutException",
            "ChunkedEncodingError"
        ]
    },
    
    "headers": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8", 
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
}
```

## 📊 모니터링 및 로깅

### 로그 레벨 및 형식
```python
LOGGING_CONFIG = {
    "levels": {
        "DEBUG": "상세한 디버그 정보 (개발용)",
        "INFO": "일반적인 진행 정보", 
        "WARNING": "경고 (계속 실행 가능)",
        "ERROR": "오류 (기능 실패)",
        "CRITICAL": "심각한 오류 (시스템 중단)"
    },
    
    "formatters": {
        "console": "%(asctime)s [%(levelname)s] %(message)s",
        "file": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
        "json": {
            "timestamp": "%(asctime)s",
            "level": "%(levelname)s", 
            "module": "%(name)s",
            "line": "%(lineno)d",
            "message": "%(message)s"
        }
    },
    
    "handlers": {
        "console": {"level": "INFO", "formatter": "console"},
        "file": {"level": "DEBUG", "formatter": "file", "max_size": "10MB"},
        "error_file": {"level": "ERROR", "formatter": "json"}
    }
}
```

### 성능 메트릭 수집
```python
METRICS_COLLECTION = {
    "system_metrics": [
        "cpu_percent",         # CPU 사용률
        "memory_percent",      # 메모리 사용률  
        "disk_io",            # 디스크 I/O
        "network_io"          # 네트워크 I/O
    ],
    
    "application_metrics": [
        "pages_processed",     # 처리된 페이지 수
        "products_extracted",  # 추출된 상품 수
        "images_downloaded",   # 다운로드된 이미지 수
        "errors_occurred",     # 발생한 오류 수
        "success_rate"        # 성공률
    ],
    
    "timing_metrics": [
        "page_load_time",      # 페이지 로딩 시간
        "extraction_time",     # 데이터 추출 시간
        "save_time",          # 저장 시간
        "total_session_time"   # 전체 세션 시간
    ]
}
```

---

**문서 버전**: v1.0  
**최종 업데이트**: 2024-12-07  
**다음 문서**: ERROR_HANDLING.md