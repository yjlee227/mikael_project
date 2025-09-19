# MyRealTrip 크롤링 시스템 (v2.0 - Refactored)

## 1. 프로젝트 개요

이 프로젝트는 `myrealtrip` 웹사이트의 여행 상품 정보를 수집하는 크롤링 시스템입니다. 

초기 버전의 복잡성을 개선하고 `kkday` 크롤러 개발을 통해 얻은 최신 기술과 안정적인 아키텍처를 적용하여 **전면 리팩토링된 v2.0 시스템**입니다.


## 2. 핵심 특징

- **모듈식 아키텍처**: 모든 코드가 `src` 폴더 내에 기능별(`scraper`, `utils`)로 분리되어 있어 유지보수와 확장이 매우 용이합니다.
- **중앙화된 설정**: `src/config.py` 파일에서 모든 주요 설정을 관리하여 일관성을 유지합니다.
- **지능형 봇 탐지 회피**: `kkday` 프로젝트에서 검증된 50가지의 인간 행동 기반 스크롤 패턴을 탑재하여 탐지 가능성을 최소화합니다.
- **안정적인 데이터 관리**: `hashlib`를 이용한 초고속 중복 URL 체크 및 안전한 CSV 저장 로직을 통해 데이터의 무결성을 보장합니다.
- **간소화된 실행**: 복잡한 노트북 셀 실행 과정 없이, 단일 실행 파일(`myrealtrip_runner.ipynb`)에서 간단한 코드로 크롤러를 실행할 수 있습니다.


## 3. 프로젝트 구조

```
myrealtrip/
├── src/                          # 모든 핵심 로직이 모듈화되어 위치
│   ├── config.py               # 전역 설정 및 도시 정보
│   ├── scraper/                # 크롤링 기능 모듈
│   │   ├── crawler.py          # 메인 크롤러 클래스
│   │   ├── driver_manager.py   # 드라이버 및 브라우저 제어
│   │   ├── parsers.py          # 데이터 추출 및 정제
│   │   ├── url_manager.py      # URL 수집 및 관리
│   │   └── human_scroll_patterns.py # 50가지 인간 행동 스크롤 패턴
│   └── utils/                  # 공용 유틸리티 모듈
│       ├── city_manager.py     # 도시명 별칭 처리 등
│       └── file_handler.py     # CSV, 이미지 등 파일 처리
├── myrealtrip_runner.ipynb     # 🚀 크롤러를 실행하는 유일한 파일
├── data/                         # 수집된 CSV 데이터 저장
├── myrealtripthumb_img/          # 수집된 이미지 저장
├── hash_index/                   # 수집 완료된 URL 해시 인덱스
└── _archive/                     # 구버전 노트북 보관소
```

## 4. 실행 방법

1.  **`myrealtrip_runner.ipynb` 파일을 엽니다.**
2.  아래와 같이 코드 셀에서 **원하는 도시와 수집할 상품 개수를 수정**합니다.
3.  해당 셀을 실행하면 크롤링이 시작됩니다.

```python
# 1. 필요한 모듈 import
from src.scraper.crawler import MyRealTripCrawler

# 2. 크롤링 설정
TARGET_CITY = "도쿄"       # 원하는 도시 이름으로 변경하세요
MAX_PRODUCTS = 10            # 수집할 최대 상품 수

# 3. 크롤러 생성 및 실행
if __name__ == '__main__':
    try:
        crawler = MyRealTripCrawler(city_name=TARGET_CITY)
        crawler.run_crawling(max_products=MAX_PRODUCTS)
    except Exception as e:
        print(f'크롤링 중 예상치 못한 오류가 발생했습니다: {e}')
```

---
*이 문서는 리팩토링 프로젝트의 일환으로 업데이트되었습니다. (최종 업데이트: 2025-09-19)*
