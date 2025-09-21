# 🚀 크롤러 표준화 및 DB 통일성 프로젝트

## 📖 **프로젝트 개요**

이 프로젝트는 **KLOOK, KKDAY, MYREALTRIP 3개 여행 플랫폼 크롤러를 완전히 표준화하고 데이터베이스를 통일**하는 대규모 아키텍처 리팩토링 프로젝트입니다.

### **🎯 핵심 목표**
- **아키텍처 통일**: 3개 플랫폼이 동일한 모듈 구조 사용
- **데이터 표준화**: 30개 컬럼의 완전히 동일한 스키마 (SQL 최적화)
- **기능 고도화**: 봇 탐지 회피, 자동 학습, 오류 복구 등 고급 기능
- **운영 효율성**: 2단계 분리 실행으로 안정성 극대화
- **SQL 친화적 구조**: 대용량 분석을 위한 Data Lake/Warehouse 아키텍처

---

## 🏗️ **표준 아키텍처**

### **PostgreSQL 중심 하이브리드 아키텍처**
```
platform/                          # klook, kkday, myrealtrip
├── postgresql/                     # 🐘 PostgreSQL 데이터베이스
│   ├── schema/                    # 스키마 정의
│   │   ├── dimensions.sql         # 차원 테이블 (도시, 플랫폼 등)
│   │   ├── facts.sql              # 팩트 테이블 (상품, 랭킹 등)
│   │   ├── partitions.sql         # 파티션 정의
│   │   └── indexes.sql            # 인덱스 최적화
│   ├── functions/                 # 저장 프로시저
│   │   ├── data_transform.sql     # 데이터 변환 함수
│   │   ├── analytics.sql          # 분석 함수
│   │   └── maintenance.sql        # 유지보수 함수
│   ├── views/                     # 분석용 뷰
│   │   ├── product_analytics.sql  # 상품 분석 뷰
│   │   ├── city_summary.sql       # 도시별 요약 뷰
│   │   └── platform_comparison.sql # 플랫폼 비교 뷰
│   └── migrations/                # 스키마 변경 이력
├── data/                          # 📁 보조 데이터 저장
│   ├── archive/                   # 🗄️ Parquet 아카이브 (3개월+)
│   │   └── year=2025/month=09/
│   │       └── fact_products_archive.parquet
│   ├── temp/                      # 🔄 임시 수집 파일
│   └── backup/                    # 💾 백업 파일
├── src/                           # 💻 소스 코드
│   ├── database/                  # 데이터베이스 연결 및 관리
│   │   ├── __init__.py
│   │   ├── connection.py          # PostgreSQL 연결 관리
│   │   ├── models.py              # SQLAlchemy ORM 모델
│   │   └── migrations.py          # 스키마 마이그레이션
│   ├── etl/                       # 실시간 ETL 파이프라인
│   │   ├── __init__.py
│   │   ├── url_ingestion.py       # Stage 1: URL → PostgreSQL
│   │   ├── product_ingestion.py   # Stage 2: Product → PostgreSQL
│   │   └── data_validation.py     # 데이터 품질 검증
│   ├── scraper/                   # 기존 크롤러 모듈 (개선)
│   │   ├── crawler.py             # PostgreSQL 직접 연동
│   │   ├── url_collector.py       # DB 직접 저장
│   │   └── detail_crawler.py      # DB 직접 저장
│   └── analytics/                 # 분석 모듈
│       ├── __init__.py
│       ├── queries.py             # 공통 분석 쿼리
│       └── reports.py             # 리포트 생성
├── notebooks/                     # 📔 분석 노트북
│   ├── exploratory/               # 탐색적 분석
│   ├── production/                # 운영 분석
│   │   ├── postgresql_analysis.ipynb
│   │   └── performance_monitoring.ipynb
│   └── experiments/               # 실험 분석
├── sql/                           # 🔍 SQL 스크립트 모음
│   ├── analytics/                 # 분석 쿼리
│   │   ├── city_performance.sql
│   │   ├── price_trends.sql
│   │   └── platform_comparison.sql
│   ├── maintenance/               # 유지보수 스크립트
│   │   ├── partition_cleanup.sql
│   │   ├── index_rebuild.sql
│   │   └── stats_update.sql
│   └── exports/                   # 데이터 내보내기
│       ├── to_parquet.sql
│       └── to_csv.sql
└── config/                        # ⚙️ 설정 파일
    ├── postgresql.yaml            # PostgreSQL 설정
    ├── etl_pipeline.yaml          # ETL 파이프라인 설정
    └── monitoring.yaml            # 모니터링 설정
```

---

## 📊 **PostgreSQL 최적화 스키마**

### **정규화된 관계형 구조**

#### **차원 테이블 (Dimensions)**
```sql
-- 도시 마스터 테이블
CREATE TABLE dim_cities (
    city_id VARCHAR(10) PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    continent_name VARCHAR(50) NOT NULL,
    coordinates POINT,                    -- PostgreSQL 지리 타입
    timezone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 플랫폼 마스터 테이블
CREATE TABLE dim_platforms (
    platform_id VARCHAR(10) PRIMARY KEY,
    platform_name VARCHAR(50) NOT NULL,
    base_url VARCHAR(255),
    api_config JSONB,                     -- 플랫폼별 설정
    created_at TIMESTAMP DEFAULT NOW()
);

-- 카테고리 마스터 테이블
CREATE TABLE dim_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INTEGER REFERENCES dim_categories(category_id),
    platform_id VARCHAR(10) REFERENCES dim_platforms(platform_id)
);
```

#### **팩트 테이블 (Facts) - 파티셔닝 적용**
```sql
-- 상품 팩트 테이블 (월별 파티셔닝)
CREATE TABLE fact_products (
    product_key BIGSERIAL,
    product_id VARCHAR(50) NOT NULL,
    city_id VARCHAR(10) REFERENCES dim_cities(city_id),
    platform_id VARCHAR(10) REFERENCES dim_platforms(platform_id),

    -- 기본 상품 정보
    product_name TEXT NOT NULL,
    price DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'KRW',
    rating DECIMAL(3,2),
    review_count INTEGER DEFAULT 0,

    -- PostgreSQL 특화 타입 활용
    location_tags TEXT[],                 -- 배열 타입
    product_metadata JSONB,               -- JSON 메타데이터
    images JSONB,                         -- 이미지 정보 JSON

    -- 순위 및 메타 정보
    rank_position INTEGER,
    collected_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (product_key, collected_date)
) PARTITION BY RANGE (collected_date);

-- 월별 파티션 생성
CREATE TABLE fact_products_2025_09 PARTITION OF fact_products
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');
CREATE TABLE fact_products_2025_10 PARTITION OF fact_products
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
```

#### **원시 데이터 테이블 (Raw Data)**
```sql
-- 수집 원시 데이터 (JSON 저장)
CREATE TABLE raw_collection_data (
    collection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id VARCHAR(10) REFERENCES dim_platforms(platform_id),
    city_id VARCHAR(10) REFERENCES dim_cities(city_id),
    stage INTEGER NOT NULL,               -- 1: URL수집, 2: 상품상세

    -- JSON 데이터
    collection_metadata JSONB,            -- 수집 설정 및 통계
    raw_data JSONB,                       -- 원시 크롤링 데이터
    processing_status VARCHAR(20) DEFAULT 'pending',

    collected_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);
```

### **PostgreSQL 특화 기능 활용**

#### **1. JSON 데이터 구조**
```json
-- product_metadata 예시
{
  "tour_type": "group",
  "meeting_method": "pickup",
  "duration": "8 hours",
  "language": ["korean", "english"],
  "highlights": ["전문 가이드", "점심 포함"],
  "original_data": {...}
}

-- images 예시
{
  "main": {
    "filename": "CTS_0001.jpg",
    "url": "https://...",
    "local_path": "/images/asia/japan/sapporo/CTS_0001.jpg"
  },
  "thumbnail": {
    "filename": "CTS_0001_thumb.jpg",
    "url": "https://...",
    "local_path": "/images/asia/japan/sapporo/CTS_0001_thumb.jpg"
  }
}
```

#### **2. 인덱스 최적화**
```sql
-- 지리적 검색 인덱스
CREATE INDEX idx_cities_coordinates ON dim_cities USING GIST (coordinates);

-- 배열 검색 인덱스 (위치태그)
CREATE INDEX idx_products_location_tags ON fact_products USING GIN (location_tags);

-- JSON 검색 인덱스
CREATE INDEX idx_products_metadata ON fact_products USING GIN (product_metadata);

-- 복합 인덱스 (자주 사용하는 조합)
CREATE INDEX idx_products_city_date ON fact_products (city_id, collected_date);
CREATE INDEX idx_products_platform_rank ON fact_products (platform_id, rank_position);
```

### **데이터 구조 비교**

| 구조 | 기존 (30컬럼 평면) | PostgreSQL 최적화 | 장점 |
|------|------------------|------------------|------|
| **저장 효율성** | 중복 데이터 다량 | 정규화로 60% 절약 | 공간 효율 |
| **위치태그** | 쉼표 구분 문자열 | TEXT[] 배열 | 검색 성능 10배↑ |
| **메타데이터** | 개별 컬럼 30개 | JSONB 1개 | 유연성 극대화 |
| **확장성** | 컬럼 추가 복잡 | JSON 필드 추가 | 무제한 확장 |
| **쿼리 성능** | 전체 스캔 | 인덱스 활용 | 100배 향상 |

---

## ⚡ **2단계 분리 실행 시스템**

### **🎯 봇 탐지 회피 전략**
```python
# Stage 1: URL 수집 전용 (별도 세션)
collector = PlatformURLCollector(city="도쿄")
collector.collect_urls(max_urls=200)
# → 시스템 종료, 시간 간격 대기 (30분 ~ 2시간)

# Stage 2: 상세 크롤링 전용 (시간차 실행)
crawler = PlatformDetailCrawler(city="도쿄")
crawler.crawl_details_from_saved_urls()
```

### **⚙️ 실행 흐름**
1. **Stage 1 실행** → URL 수집 → JSON 저장 → 세션 종료
2. **시간 간격 대기** → 자연스러운 인간 행동 패턴 모방
3. **Stage 2 실행** → URL 로드 → 상세 크롤링 → CSV 저장

---

## 🧠 **지능형 기능**

### **1. 위치태그 자동 학습 시스템**
```python
# 상품 수집시마다 자동 학습
learning_system = LocationLearningSystem(city_name='삿포로')
tags = learning_system.get_location_tags('삿포로', product_text)

# 7회 누적 시 confirmed 키워드로 승격
# 다음 수집부터 자동으로 위치태그 추출
```

### **2. 50가지 인간 스크롤 패턴**
```python
# 탐지 회피를 위한 다양한 스크롤 패턴
patterns = [
    "natural_reading_scroll",    # 자연스러운 독서 패턴
    "curious_browser_scroll",    # 호기심 많은 브라우저
    "quick_scanner_scroll",      # 빠른 스캔 패턴
    # ... 47가지 추가 패턴
]
```

### **3. 이미지 경로 자동 생성**
```python
# 파일명과 전체 경로 자동 생성 및 저장
main_img_path = get_smart_image_path(city_name, product_number, "main")
thumb_img_path = get_smart_image_path(city_name, product_number, "thumb")

# CSV에 4개 컬럼 저장: 파일명 + 전체경로
data = {
    "메인이미지": "CTS_0001.jpg",
    "썸네일이미지": "CTS_0001_thumb.jpg",
    "메인이미지_경로": "platform/img/아시아/일본/삿포로/CTS_0001.jpg",
    "썸네일이미지_경로": "platform/img/아시아/일본/삿포로/CTS_0001_thumb.jpg"
}
```

---

## 📈 **현재 진행 상황**

### **✅ 완료된 플랫폼: KKDAY (90%)**
- **아키텍처**: 표준 모듈 구조 완성
- **데이터**: 30개 컬럼 스키마 적용
- **기능**: 위치태그 학습, 이미지 경로 자동 생성
- **테스트**: 삿포로 위치태그 15개 키워드 학습 완료

### **🔄 진행 중: KLOOK (60%)**
- **현재 작업**: 6셀 단일 실행 → 2단계 분리 실행 전환
- **계획**: 60개 세부 TODO 항목으로 체계적 전환
- **목표**: URL 수집과 상세 크롤링 완전 분리

### **📋 대기 중: MYREALTRIP (30%)**
- **현재 상태**: Jupyter Notebook 기반
- **목표**: KKDAY 아키텍처로 완전 리팩토링
- **계획**: 모듈화 + 위젯 제거 + 안정적 실행

---

## 🛠️ **설치 및 실행**

### **1. 환경 설정**
```bash
# 프로젝트 클론
git clone [repository-url]
cd mikael_project

# 의존성 설치
pip install -r requirements.txt

# 위치태그 학습을 위한 KoNLPy 설치 (선택)
pip install konlpy
```

### **2. 기본 실행 (KKDAY 예시)**
```python
# Stage 1: URL 수집
from kkday.src.scraper.url_collector import KKdayURLCollector

collector = KKdayURLCollector(city_name="삿포로")
collector.collect_urls(max_urls=100)

# 30분 ~ 2시간 대기 후...

# Stage 2: 상세 크롤링
from kkday.src.scraper.detail_crawler import KKdayDetailCrawler

crawler = KKdayDetailCrawler(city_name="삿포로")
crawler.crawl_details_from_saved_urls()
```

### **3. 통합 실행 (노트북)**
```python
# kkday_stage1_runner.ipynb 실행
TARGET_CITY = "삿포로"
MAX_URLS = 200

# kkday_stage2_runner.ipynb 실행 (시간차)
# 자동으로 저장된 URL 로드하여 크롤링
```

---

## 📋 **데이터 출력 예시**

### **표준 CSV 출력**
```csv
번호,상품명,가격,평점,리뷰수,URL,도시ID,도시명,대륙,국가,위치태그,카테고리,언어,투어형태,미팅방식,소요시간,하이라이트,순위,통화,수집일시,데이터소스,해시값,메인이미지,썸네일이미지,메인이미지_경로,썸네일이미지_경로,상품번호,분류,특징,제휴링크
1,"홋카이도 스키 투어","₩141,658",4.1/5,67,"https://...",CTS,삿포로,아시아,일본,"홋카이도,테이네,스키장",일본 > 홋카이도 > 삿포로,중국어,KKday 전용투어,현장에서 전자바우처 제시,가장 빠른 예약 가능일: 2025-12-15,"세심한 경험, 잊지 못할 추억...",1,KRW,"2025-09-20 22:02:01",KKday,13f68dd5a97c,CTS_0001.jpg,CTS_0001_thumb.jpg,kkday/img/아시아/일본/삿포로/CTS_0001.jpg,kkday/img/아시아/일본/삿포로/CTS_0001_thumb.jpg,157140,삿포로,"스키 장비 풀세트 포함",""
```

### **위치태그 학습 결과 (JSON)**
```json
{
  "삿포로": {
    "confirmed": [
      "홋카이도", "삿포로", "테이네", "스키장", "스키",
      "모이와산", "조잔케이", "온천", "맥주", "박물관",
      "오타루", "샤코탄", "셔틀", "버스", "일일", "투어"
    ],
    "candidates": {
      "강습": {"freq": 5},
      "장비": {"freq": 4},
      "프리미엄": {"freq": 3}
    }
  }
}
```

---

## 🔧 **고급 설정**

### **config.py 주요 설정**
```python
CONFIG = {
    "MAX_PRODUCTS_PER_CITY": 200,
    "SELENIUM_WAIT_TIMEOUT": 10,
    "HUMAN_DELAY_RANGE": (2, 5),
    "LOCATION_LEARNING_THRESHOLD": 7,
    "STAGE_DELAY_HOURS": 2,
    "IMAGE_DOWNLOAD_ENABLED": True,
    "BOT_DETECTION_AVOIDANCE": True
}
```

### **도시 정보 관리**
```python
UNIFIED_CITY_INFO = {
    "삿포로": {
        "대륙": "아시아",
        "국가": "일본",
        "코드": "CTS",
        "영문명": "sapporo"
    }
    # ... 177개 도시 정보
}
```

---

## 🎯 **성능 지표**

### **목표 성능**
- **URL 수집 성공률**: 95% 이상
- **상세 크롤링 성공률**: 90% 이상
- **봇 탐지 회피율**: 95% 이상 (차단율 5% 이하)
- **메모리 효율성**: 각 단계 완료 후 완전 해제
- **데이터 품질**: 필수 필드 완성도 95% 이상

### **실제 성과 (KKDAY)**
- ✅ 위치태그 학습: 15개 키워드 자동 추출
- ✅ 이미지 경로: 100% 자동 생성
- ✅ CSV 스키마: 30개 컬럼 완벽 적용
- ✅ 데이터 연속성: 번호 중복 없이 순차 저장

---

## 📚 **문서 구조**

```
docs/
├── STANDARDIZATION_README.md      # 📖 이 파일 (프로젝트 개요)
├── STANDARDIZATION_TODO.md        # ✅ 상세 작업 계획
├── klook/
│   ├── README_KKDAY_CONVERSION.md  # KLOOK 전환 가이드
│   ├── TODO_KKDAY_CONVERSION.md    # KLOOK 작업 리스트
│   └── FUNCTION_VERIFICATION_CHECKLIST.md
└── Myrealtrip/
    ├── refactoring_readme.md       # MYREALTRIP 리팩토링 가이드
    └── refactoring_todo.md         # MYREALTRIP 작업 리스트
```

---

## 🤝 **기여 가이드**

### **개발 워크플로우**
1. 이슈 생성 및 브랜치 생성
2. 모듈별 개발 및 테스트
3. 코드 리뷰 및 병합
4. 통합 테스트 실행

### **코딩 스타일**
- **함수명**: snake_case
- **클래스명**: PascalCase
- **상수**: UPPER_CASE
- **주석**: 한국어 + 영어 혼용

---

## 📞 **문의 및 지원**

### **프로젝트 관리**
- **주 담당자**: [사용자명]
- **프로젝트 시작**: 2025-09-21
- **예상 완료**: 2025-10-31

### **기술 스택**
- **언어**: Python 3.8+
- **웹 드라이버**: Selenium ChromeDriver
- **데이터 처리**: Pandas, Parquet, DuckDB
- **SQL 분석**: dbt, BigQuery/Snowflake 호환
- **자연어 처리**: KoNLPy (선택)
- **이미지 처리**: PIL/Pillow

---

## 🚀 **표준화 우선순위 전략**

### **⚡ 핵심 결정사항**
**"지금 표준화 → 효율적 확장"** 전략 채택

### **📋 Phase별 실행 계획**

#### **Phase 1: KKDAY 완전 표준화 (현재 진행)**
- ✅ **30개 컬럼 스키마 적용 완료**
- ✅ **위치태그 학습 시스템 활성화 완료**
- 🔄 **2단계 분리 실행 전환 (진행 중)**
- 🔄 **SQL 친화적 데이터 구조 적용**

#### **Phase 2: KLOOK 표준화 전환**
- 📋 기존 2단계 JSON 시스템 → 표준 Data Lake 구조
- 📋 30개 컬럼 스키마 적용
- 📋 Parquet 형식 전환

#### **Phase 3: MYREALTRIP 완전 리팩토링**
- 📋 Jupyter Notebook → 모듈화 아키텍처
- 📋 표준 30개 컬럼 적용
- 📋 2단계 분리 실행 구현

### **🎯 전략적 우선순위 근거**

#### **✅ 지금 표준화해야 하는 이유**
1. **기술 부채 방지**: 서로 다른 3개 시스템 → 통일된 1개 시스템
2. **확장성 확보**: 177개 도시 대응 가능한 구조
3. **분석 효율성**: 수집과 동시에 SQL 분석 가능
4. **데이터 품질**: 처음부터 일관된 스키마로 수집

#### **📊 예상 효과**
- **개발 시간**: 10개월 → 4.2개월 (58% 단축)
- **유지보수**: 3개 시스템 → 1개 표준 시스템
- **데이터 품질**: 수동 변환 없이 즉시 분석 가능
- **확장성**: 1000개 도시까지 확장 가능한 구조

### **🔧 점진적 구현 방법**

#### **1단계: 폴더 구조 변경 (1일)**
```bash
# 기존 코드 유지하며 구조만 변경
mkdir -p data/{raw,staging,warehouse}
mkdir -p sql/{ddl,etl,analytics}
# 심볼릭 링크로 무중단 전환
```

#### **2단계: 코드 점진적 이동 (2-3일)**
```python
# 기존 함수 90% 재활용
class Stage1Pipeline:
    def collect_urls(self):
        return self.crawler.collect_activity_urls()  # 기존 함수 활용
```

#### **3단계: 데이터 형식 전환 (1-2일)**
```python
# CSV → Parquet (기존 로직 99% 재활용)
df.to_parquet(path, partition_cols=['year', 'month', 'continent'])
```

---

*이 README는 크롤러 표준화 및 DB 통일성 프로젝트의 종합 가이드입니다.*
*최신 정보는 `STANDARDIZATION_TODO.md`에서 확인하세요.*

---

## 🏆 **프로젝트 비전**

**"3개 플랫폼, 하나의 표준"**

이 프로젝트를 통해 KLOOK, KKDAY, MYREALTRIP 크롤러가 완전히 통일된 아키텍처와 데이터 형식을 갖추어, 유지보수가 쉽고 확장 가능하며 안정적인 여행 데이터 수집 시스템을 구축합니다.

**🎯 최종 목표: 여행 데이터 수집의 새로운 표준 확립** 🚀