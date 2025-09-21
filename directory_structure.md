# 📂 표준화된 크롤링 데이터 디렉토리 구조

## 제안된 구조

```
mikael_project/
├── crawl_data/                          # 크롤링 원시 데이터
│   ├── klook/
│   │   ├── sessions/                    # 세션별 JSON 파일
│   │   │   ├── 2025-09-20_sapporo_all/
│   │   │   │   ├── urls.json           # URL 수집 데이터
│   │   │   │   ├── status.json         # 크롤링 상태
│   │   │   │   └── products.json       # 상품 상세 데이터
│   │   │   ├── 2025-09-21_tokyo_tour/
│   │   │   └── 2025-09-22_osaka_activity/
│   │   └── images/                      # 이미지 파일
│   │       ├── asia/japan/sapporo/
│   │       ├── asia/japan/tokyo/
│   │       └── asia/japan/osaka/
│   ├── kkday/
│   │   ├── sessions/
│   │   │   ├── 2025-09-20_tokyo_all/
│   │   │   └── 2025-09-21_sapporo_tour/
│   │   └── images/
│   │       └── asia/japan/
│   └── logs/                            # 크롤링 로그
│       ├── klook_crawl.log
│       └── kkday_crawl.log
├── processed_data/                      # 가공된 데이터
│   ├── csv/                            # 표준화된 CSV
│   │   ├── klook/
│   │   │   ├── asia_japan_sapporo_products.csv
│   │   │   ├── asia_japan_tokyo_products.csv
│   │   │   └── asia_japan_osaka_products.csv
│   │   └── kkday/
│   │       ├── asia_japan_tokyo_products.csv
│   │       └── asia_japan_sapporo_products.csv
│   ├── unified/                        # 통합 데이터
│   │   ├── asia_japan_all_products.csv
│   │   └── platform_comparison.csv
│   └── backup/                         # 백업 파일
├── database/                           # 데이터베이스 관련
│   ├── schema.sql                      # PostgreSQL 스키마
│   ├── migrations/                     # 스키마 변경 이력
│   └── dumps/                          # 데이터베이스 덤프
└── scripts/                            # 관리 스크립트
    ├── data_migration.py               # 기존 데이터 이주
    ├── directory_organizer.py          # 디렉토리 정리
    └── json_processor.py               # JSON 데이터 처리
```

## 파일 명명 규칙

### 1. 세션 디렉토리
```
{YYYY-MM-DD}_{city}_{tab}/
예: 2025-09-20_sapporo_all/
```

### 2. JSON 파일
```
urls.json          # URL 수집 데이터
status.json        # 크롤링 상태
products.json      # 상품 상세 데이터 (선택)
```

### 3. CSV 파일
```
{continent}_{country}_{city}_products.csv
예: asia_japan_sapporo_products.csv
```

### 4. 이미지 디렉토리
```
{continent}/{country}/{city}/
예: asia/japan/sapporo/
```

## 장점

1. **확장성**: 새로운 플랫폼/도시 추가 용이
2. **추적성**: 날짜별 세션 관리로 이력 추적 가능
3. **조직성**: 원시데이터와 가공데이터 분리
4. **표준성**: 일관된 명명 규칙
5. **백업**: 자동 백업 및 버전 관리 지원

## PostgreSQL 연동

- `crawl_sessions` 테이블의 `session_id`가 디렉토리명과 매핑
- JSON 파일 경로가 DB에 저장되어 추적 가능
- 이미지 경로가 표준화되어 웹 서비스 연동 용이