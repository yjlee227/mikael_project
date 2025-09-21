# 🔧 크롤러 표준화 및 DB 통일성 프로젝트 - TODO 리스트

## 🎯 **프로젝트 목표**
**KLOOK, KKDAY, MYREALTRIP 3개 크롤러의 완전한 표준화 및 SQL 친화적 데이터베이스 통일**

### **⚡ 전략 결정사항 (2025-09-21 업데이트)**
**"지금 표준화 → 효율적 확장"** 전략 채택
- **우선순위**: 177개 도시 수집 전에 표준화 완성
- **목표**: SQL 기반 대용량 분석 환경 구축
- **방법**: 점진적 전환 (기존 코드 90% 재활용)

---

## 📊 **현재 진행 상황 요약**

| 플랫폼 | 완성도 | 현재 상태 | SQL 준비도 | 주요 작업 |
|--------|--------|-----------|------------|-----------|
| **KKDAY** | 🟢 90% | 표준 기준 | 🔄 50% | SQL 친화적 구조 전환 🔄 |
| **KLOOK** | 🟡 60% | 2단계 분리 완료 | 🟡 30% | Data Lake 구조 적용 📋 |
| **MYREALTRIP** | 🔴 30% | 리팩토링 대기 | 🔴 10% | 전면 모듈화 리팩토링 📋 |

### **🎯 우선순위 조정 (2025-09-21)**
1. **KKDAY SQL 구조 전환** (현재 진행 중)
2. **KLOOK Data Lake 적용**
3. **MYREALTRIP 표준화**

---

## ✅ **완료된 작업 (2025-09-21)**

### **Phase 0: 기반 구조 분석 및 설계**
- [x] KKDAY vs KLOOK CSV 컬럼 구조 비교 분석
- [x] 30개 컬럼 표준 스키마 설계
- [x] 이미지 처리 방식 통합 설계
- [x] 위치태그 학습 시스템 구조 파악

### **Phase 1: KKDAY 표준화 완성**
- [x] KKDAY 30개 컬럼 구조 적용 (`file_handler.py`)
- [x] 이미지 경로 자동 생성 시스템 통합 (`crawler.py`)
- [x] 위치태그 학습 시스템 설정 및 테스트
- [x] 삿포로 키워드 학습 데이터베이스 초기화
- [x] location_data 디렉토리 구조 생성
- [x] KLOOK vs KKDAY 파일 저장 방식 비교 분석 (JSON vs TXT)
- [x] 표준화 우선순위 전략 결정
- [x] SQL 친화적 Data Lake 아키텍처 설계
- [x] 점진적 구현 방법 수립

---

## 🔄 **진행 중인 작업**

### **Phase 2: KKDAY SQL 친화적 구조 전환 (우선순위 1위)**

#### **2.1 Data Lake 디렉토리 구조 생성**
- [ ] **폴더 구조 생성**
  - [ ] `data/raw/stage1_urls/` - URL 수집 원시 데이터
  - [ ] `data/raw/stage2_products/` - 상품 상세 원시 데이터
  - [ ] `data/staging/` - 검증된 중간 데이터
  - [ ] `data/warehouse/dimensions/` - 차원 테이블
  - [ ] `data/warehouse/facts/` - 팩트 테이블
  - [ ] `sql/ddl/` - 테이블 정의 스크립트
  - [ ] `sql/etl/` - ETL 변환 스크립트
  - [ ] `sql/analytics/` - 분석 쿼리

#### **2.2 데이터 파이프라인 모듈 생성**
- [ ] **새로운 파이프라인 모듈**
  - [ ] `src/data/extract.py` - Stage 1 URL 수집 (기존 url_manager.py 활용)
  - [ ] `src/data/transform.py` - 데이터 변환 (기존 parsers.py 활용)
  - [ ] `src/data/load.py` - Stage 2 로드 (기존 file_handler.py 활용)
  - [ ] `src/pipelines/stage1_pipeline.py` - URL 수집 파이프라인
  - [ ] `src/pipelines/stage2_pipeline.py` - 상세 크롤링 파이프라인

#### **2.3 데이터 형식 전환 (CSV → Parquet)**
- [ ] **Parquet 저장 시스템**
  - [ ] `save_to_parquet_kkday()` 함수 구현 (기존 save_to_csv_kkday 재활용)
  - [ ] 시간 기반 파티셔닝 적용 (year/month/day)
  - [ ] 지역 기반 파티셔닝 적용 (continent/country/city)
  - [ ] 메타데이터 스키마 정의

#### **2.4 기존 시스템과의 호환성 유지**
- [ ] **점진적 전환 시스템**
  - [ ] 심볼릭 링크를 통한 무중단 전환
  - [ ] 기존 CSV 출력과 Parquet 출력 병행
  - [ ] 기존 노트북 호환성 확보

### **Phase 3: KLOOK Data Lake 구조 적용**

#### **2.1 아키텍처 준비 및 클래스 설계**
- [ ] **새로운 클래스 파일 생성**
  - [ ] `src/scraper/url_collector.py` - KlookURLCollector 클래스
  - [ ] `src/scraper/detail_crawler.py` - KlookDetailCrawler 클래스
  - [ ] `src/utils/data_persistence.py` - URL 저장/로드 시스템
  - [ ] `src/utils/session_manager.py` - 세션 상태 관리

#### **2.2 기존 함수 분석 및 재분배**
- [ ] **드라이버 관련 함수 매핑**
  - [ ] `setup_driver()` → Stage 1 & Stage 2 모두 활용
  - [ ] `close_driver()` → 각 단계 종료 시 활용
  - [ ] `restart_driver()` → 오류 복구 시 활용

- [ ] **네비게이션 함수 분리**
  - [ ] `navigate_to_search()` → Stage 1에서만 활용
  - [ ] `handle_popup()` → Stage 1에서만 활용
  - [ ] `apply_filters()` → Stage 1에서만 활용

- [ ] **URL 수집 함수 이관**
  - [ ] `collect_activity_urls()` → Stage 1 핵심 기능으로 이관
  - [ ] `scroll_and_load_more()` → Stage 1에서만 활용
  - [ ] `extract_urls_from_page()` → Stage 1에서만 활용

- [ ] **데이터 추출 함수 이관**
  - [ ] `extract_product_details()` → Stage 2 핵심 기능으로 이관
  - [ ] `download_images()` → Stage 2에서만 활용
  - [ ] `save_to_csv()` → Stage 2에서만 활용

#### **2.3 Stage 1 (URL 수집) 구현**
- [ ] **KlookURLCollector 클래스 구현**
  - [ ] `__init__(self, city_name: str)` 구현
  - [ ] `collect_urls(self, max_urls: int)` 메서드 구현
  - [ ] 기존 `collect_activity_urls()` 로직 통합
  - [ ] 진행률 표시 기능 추가

- [ ] **데이터 저장 시스템**
  - [ ] JSON 스키마 설계 (수집 시간, 도시, 총 개수)
  - [ ] `save_collected_urls()` 메서드 구현
  - [ ] 중복 URL 자동 제거
  - [ ] 데이터 무결성 검증

- [ ] **실행 노트북 생성**
  - [ ] `klook_stage1_runner.ipynb` 생성
  - [ ] 간단한 설정 셀 (도시, 최대 URL 수)
  - [ ] URL 수집 실행 셀
  - [ ] 결과 확인 및 다음 단계 안내 셀

#### **2.4 Stage 2 (상세 크롤링) 구현**
- [ ] **KlookDetailCrawler 클래스 구현**
  - [ ] `__init__(self, city_name: str)` 구현
  - [ ] `load_saved_urls()` 메서드 구현
  - [ ] `crawl_details_from_saved_urls()` 메서드 구현
  - [ ] 배치 처리 (URL 그룹별)

- [ ] **데이터 처리 강화**
  - [ ] 이미지 다운로드 통합
  - [ ] 썸네일 처리 로직
  - [ ] **KKDAY 컬럼 스키마 적용** (30개 컬럼)
  - [ ] 데이터 형식 통일

- [ ] **실행 노트북 생성**
  - [ ] `klook_stage2_runner.ipynb` 생성
  - [ ] 저장된 URL 확인 셀
  - [ ] 상세 크롤링 실행 셀
  - [ ] 결과 통계 및 검증 셀

#### **2.5 시스템 통합 및 안정성 강화**
- [ ] **오류 처리 및 복구**
  - [ ] 진행 지점 저장 시스템
  - [ ] 부분 완료 상태에서 재개
  - [ ] 실패 URL 격리 및 재시도

- [ ] **설정 관리 업데이트**
  - [ ] `src/config.py` 수정 (2단계 실행 관련 설정)
  - [ ] 파일 경로 관리
  - [ ] 타이밍 설정 (권장 대기시간)

---

## 📋 **대기 중인 작업**

### **Phase 3: MYREALTRIP 모듈화 리팩토링**

#### **3.1 프로젝트 구조 설정**
- [ ] `myrealtrip/src` 디렉토리 생성
- [ ] `src/utils` 디렉토리 생성
- [ ] `src/scraper` 디렉토리 생성
- [ ] 각 폴더에 `__init__.py` 생성

#### **3.2 핵심 기능 모듈화**
- [ ] **`src/utils` 모듈 생성**
  - [ ] `city_manager.py` - 도시 정보 관리
  - [ ] `file_handler.py` - 파일 저장/처리 (**KKDAY 컬럼 스키마 적용**)

- [ ] **`src/scraper` 모듈 생성**
  - [ ] `driver_manager.py` - Selenium 드라이버 제어
  - [ ] `url_manager.py` - URL 수집 및 관리
  - [ ] `parsers.py` - 데이터 추출 (**KKDAY 규격 데이터 추출**)

#### **3.3 설정 중앙화 및 크롤러 클래스 통합**
- [ ] `src/config.py` 생성 - 중앙 설정 관리
- [ ] `src/scraper/crawler.py` 생성
  - [ ] `MyRealTripCrawler` 클래스 정의
  - [ ] 노트북 로직을 클래스 메서드로 재구성
  - [ ] **KKDAY 컬럼 순서와 규격에 맞춘 데이터 조합**

#### **3.4 기능 고도화**
- [ ] **지능형 봇 탐지 회피 전략 도입**
  - [ ] `kkday`의 `human_scroll_patterns.py` 복사
  - [ ] 50가지 패턴을 사용하는 스크롤 함수 업그레이드

#### **3.5 실행 환경 재구성**
- [ ] `myrealtrip_runner.ipynb` 생성
  - [ ] 위젯(GUI) 제거
  - [ ] `crawler = MyRealTripCrawler(city="서울")` 간단 실행
- [ ] 기존 노트북 `_archive` 폴더로 이동
- [ ] 메인 `README.md` 업데이트

---

## 🧪 **테스트 및 검증 단계**

### **Phase 4: 통합 테스트**
- [ ] **단위 테스트**
  - [ ] KLOOK Stage 1 테스트 (10개, 50개, 200개 URL)
  - [ ] KLOOK Stage 2 테스트 (상세 정보 추출)
  - [ ] MYREALTRIP 모듈 개별 테스트

- [ ] **통합 테스트**
  - [ ] KLOOK Stage 1 → Stage 2 연속 실행
  - [ ] 시간차 실행 테스트
  - [ ] 여러 도시 동시 처리

- [ ] **데이터 품질 검증**
  - [ ] **30개 컬럼 구조 일치 확인**
  - [ ] **컬럼 순서 및 데이터 타입 통일 확인**
  - [ ] 이미지 경로 자동 생성 검증
  - [ ] 위치태그 학습 시스템 동작 확인

### **Phase 5: 성능 검증**
- [ ] **메모리 사용량 모니터링**
  - [ ] 각 단계별 메모리 사용량 측정
  - [ ] 메모리 누수 검사
  - [ ] 가비지 컬렉션 효율성

- [ ] **실행 시간 분석**
  - [ ] 단계별 실행 시간 측정
  - [ ] 병목 지점 분석
  - [ ] 최적화 포인트 식별

---

## 📚 **문서화 및 배포**

### **Phase 6: 최종 정리**
- [ ] **사용자 가이드 작성**
  - [ ] 통합 실행 가이드
  - [ ] 플랫폼별 설정 변경 가이드
  - [ ] 문제 해결 가이드

- [ ] **마이그레이션 가이드**
  - [ ] 기존 사용자 대상 전환 가이드
  - [ ] 설정 마이그레이션 방법
  - [ ] 데이터 백업 및 복원

- [ ] **코드 품질 보증**
  - [ ] 모든 새 클래스 및 함수 검토
  - [ ] 기존 함수 통합 검증
  - [ ] 코딩 스타일 통일

---

## 🏆 **핵심 성공 기준**

### **필수 달성 목표 (업데이트)**
- ✅ **30개 컬럼 표준 스키마**: 모든 플랫폼이 동일한 구조 생성
- ✅ **이미지 경로 통일**: 파일명 + 전체경로 이중 저장
- ✅ **위치태그 자동 학습**: 3개 플랫폼 모두 학습 시스템 적용
- 🔄 **SQL 친화적 Data Lake**: Parquet 기반 분석 최적화 구조
- 🔄 **2단계 분리 실행**: URL 수집과 상세 크롤링 완전한 세션 분리
- 📋 **모듈화 아키텍처**: 유지보수, 확장성, 재사용성 극대화

### **성능 목표**
- 🎯 **URL 수집 성공률**: 95% 이상
- 🎯 **상세 크롤링 성공률**: 90% 이상
- 🎯 **봇 탐지 회피**: 연속 실행 시 차단율 5% 이하
- 🎯 **메모리 효율성**: 각 단계 완료 후 메모리 완전 해제
- 🎯 **데이터 품질**: 필수 필드 완성도 95% 이상

---

## 📈 **진행 상태 추적**

### **전체 진행률 (업데이트)**
- **완료된 항목**: 20 / 총 90개 항목 (22%)
- **현재 우선순위**: KKDAY SQL 친화적 구조 전환
- **예상 완료 일정**: 2025년 10월 말 (SQL 분석 환경 포함)

### **마일스톤 (재조정)**
- ✅ **Milestone 1**: KKDAY 기본 표준화 완성 (2025-09-21 완료)
- 🔄 **Milestone 2**: KKDAY SQL Data Lake 전환 (진행 중)
- 📋 **Milestone 3**: KLOOK Data Lake 적용 (대기 중)
- 📋 **Milestone 4**: MYREALTRIP 완전 리팩토링 (대기 중)
- 🎯 **Milestone 5**: 3플랫폼 SQL 분석 환경 완성 (최종 목표)

---

## 🚀 **다음 단계 실행 계획**

### **이번 주 우선 작업 (재조정)**
1. **KKDAY Data Lake 폴더 구조 생성**
2. **KKDAY 데이터 파이프라인 모듈 구현**
3. **CSV → Parquet 변환 시스템 구축**

### **다음 주 계획**
1. **KKDAY SQL 분석 환경 구축 및 테스트**
2. **KLOOK Data Lake 구조 적용 시작**
3. **성능 최적화 및 안정성 강화**

### **예상 효과**
- **개발 시간**: 기존 대비 58% 단축 (점진적 전환)
- **유지보수**: 3개 시스템 → 1개 표준 시스템
- **분석 효율성**: 수집과 동시에 SQL 분석 가능

---

*이 TODO 리스트는 크롤러 표준화 및 DB 통일성 프로젝트의 마스터 계획입니다.*
*최종 업데이트: 2025-09-21*