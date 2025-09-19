# MyRealTrip 크롤러 리팩토링: TODO 리스트

### **핵심 목표 (Core Objectives)**

1.  **모듈식 아키텍처 전환**: `kkday` 프로젝트처럼 `src` 폴더 기반의 체계적인 모듈 구조로 전환한다.
2.  **안정적인 실행 환경**: 위젯(GUI) 없이, 코드에서 직접 실행하는 안정적인 스크립트 기반 실행 환경을 구축한다.
3.  **데이터 규격 통일**: 최종적으로 생성되는 CSV 데이터의 컬럼(이름, 순서, 형식)을 `kkday` 프로젝트와 100% 동일하게 표준화한다.

---

### Phase 1: 프로젝트 구조 설정 (Foundation)

- [ ] `myrealtrip` 폴더 내에 `src` 디렉토리 생성
- [ ] `src` 폴더 내에 `utils` 디렉토리 생성
- [ ] `src` 폴더 내에 `scraper` 디렉토리 생성
- [ ] 각 생성된 폴더 내에 `__init__.py` 빈 파일 생성하여 Python 패키지로 인식시키기

---

### Phase 2: 핵심 기능 모듈화 및 코드 이관

**`src/utils` (공용 기능 모듈)**

- [ ] **`city_manager.py` 생성**: `UNIFIED_CITY_INFO` 및 도시 정보 관련 함수 이관
- [ ] **`file_handler.py` 생성**
    - [ ] 파일 저장/처리 함수 (`save_batch_data`, `download_image` 등) 이관
    - [ ] **(중요)** `create_product_data_structure` 함수를 `kkday`의 컬럼 스키마와 동일하게 수정

**`src/scraper` (크롤링 로직 모듈)**

- [ ] **`driver_manager.py` 생성**: Selenium 드라이버 설정 및 제어 함수 이관
- [ ] **`url_manager.py` 생성**: URL 수집, 관리, `hashlib` 중복 체크 함수 이관
- [ ] **`parsers.py` 생성**
    - [ ] 데이터 추출/정제 함수 (`get_product_name`, `get_price` 등) 이관
    - [ ] **(중요)** `kkday` 컬럼 규격에 필요한 모든 데이터를 추출하도록 함수 보강

---

### Phase 3: 설정 중앙화 및 크롤러 클래스 통합

- [ ] **`src/config.py` 생성**: 모든 설정을 중앙에서 관리하도록 `CONFIG` 변수 및 관련 설정 이관
- [ ] **`src/scraper/crawler.py` 생성**
    - [ ] `MyRealTripCrawler` 클래스 정의
    - [ ] 노트북의 메인 실행 로직을 클래스의 메서드(`run_full_crawling` 등)로 재구성
    - [ ] **(중요)** 최종 데이터 생성 시 `kkday` 컬럼 순서와 규격에 맞춰 `product_data`를 조합하도록 로직 수정

---

### Phase 4: 기능 고도화 (kkday 장점 이식)

- [ ] **지능형 봇 탐지 회피 전략 도입**
    - [ ] `kkday`의 `human_scroll_patterns.py` 파일을 `myrealtrip/src/scraper/`로 복사
    - [ ] `driver_manager.py`의 스크롤 함수를 50가지 패턴을 사용하도록 업그레이드

---

### Phase 5: 실행 환경 재구성 및 최종 정리

- [ ] **`myrealtrip_runner.ipynb` 생성**
    - [ ] 새로운 실행 전용 노트북 생성
    - [ ] `from src.scraper.crawler import MyRealTripCrawler` 구문을 사용하여 크롤러 클래스 import
    - [ ] **(중요)** 위젯(GUI) 없이, `crawler = MyRealTripCrawler(city="서울")` 과 같은 간단한 코드로 크롤링을 직접 실행하도록 구현
- [ ] **기존 노트북 아카이브**
    - [ ] 작업 완료 후, 구형 노트북들을 `_archive` 폴더로 이동하여 정리
- [ ] **최종 통합 테스트**
    - [ ] `myrealtrip_runner.ipynb`에서 주요 도시 크롤링을 실행하여 모든 기능 및 **데이터 컬럼 규격**이 `kkday`와 동일한지 최종 검증
- [ ] **메인 `README.md` 업데이트**
    - [ ] 새로운 프로젝트 구조와 간소화된 실행 방법을 반영하여 `myrealtrip` 폴더의 메인 `README.md` 파일 업데이트
