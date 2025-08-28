# KLOOK 크롤러

## 개요
KLOOK 여행 상품 데이터를 수집하는 크롤러 시스템

## 주요 기능
- 도시별 여행 상품 크롤링
- 위치 기반 키워드 학습 시스템
- 페이지네이션 자동 처리

## 파일 구조

### 크롤러
- `KLOOK_Crawler_v2.ipynb`: 메인 크롤링 노트북

### 위치 학습 시스템
```
location_data/
├── location_keywords.json          # 통합 키워드 파일
├── 아시아/
│   └── 태국/
│       └── KBV_keywords.json       # 크라비 키워드 학습 데이터
└── 유럽/
    └── 프랑스/
        └── PAR_keywords.json       # 파리 키워드 학습 데이터 (예정)
```

### 소스 코드
- `src/utils/location_learning.py`: 위치 학습 시스템 클래스
- `src/config.py`: 도시 코드 및 매핑 정보

## 사용법

### 크롤링 실행
1. `KLOOK_Crawler_v2.ipynb` 노트북 열기
2. 타겟 도시 설정
3. 셀 순차 실행

### 위치 학습 시스템
```python
from src.utils.location_learning import LocationLearningSystem

# 크라비 키워드 학습
learner = LocationLearningSystem(city_name="크라비")
learner.learn_from_text("크라비", "텍스트 내용")
```

## 최근 업데이트

### v2.1 (2025-08-28)
- 페이지네이션 무한루프 버그 수정 (1→2→1→2 반복 → 1→2→3→4 순차진행)
- 위치 학습 시스템 리팩토링
- 파일 구조 변경: `크라비_keywords.json` → `아시아/태국/KBV_keywords.json`
- 대륙/국가/도시코드 기반 계층 구조 적용
- 마이그레이션 스크립트 구현 및 실행 완료
- 자동 백업 시스템 구현 (`backup_YYYYMMDD_HHMMSS` 폴더)

## 크롤링 데이터 컬럼
- `title`: 상품명
- `price`: 가격 정보
- `rating`: 평점
- `review_count`: 리뷰 개수
- `url`: 상품 페이지 URL
- `image_url`: 상품 이미지 URL
- `location_tags`: 위치 학습 시스템 추출 태그
- `description`: 상품 설명
- `category`: 카테고리 정보

## TODO (다음 작업)
- [ ] 새로운 구조로 크라비 크롤링 테스트 실행
- [ ] 기존 코드와의 호환성 확인
- [ ] 테스트 성공 후 마이그레이션 스크립트 및 백업 파일 정리
- [ ] 다른 도시 (파리 등) 마이그레이션 추가

## 기술 스택
- Python 3.x
- Selenium WebDriver
- Jupyter Notebook
- JSON 데이터 저장

## 마이그레이션 도구
- `migrate_location_files.py`: 위치 학습 파일 구조 변경 스크립트
- 자동 백업 및 롤백 기능 포함