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

### 위치 학습 시스템 (품사 분석 적용)
```python
# 가상환경 활성화 필요
source venv/bin/activate

from src.utils.location_learning import LocationLearningSystem

# 크라비 키워드 학습 (KoNLPy 품사 분석 적용)
learner = LocationLearningSystem(city_name="크라비")
learner.learn_from_text("크라비", "텍스트 내용")

# 확정된 위치 태그만 추출 (임계값 7 이상)
tags = learner.get_location_tags("크라비", "상품 설명 텍스트")
```

## 최근 업데이트

### v2.2 (2025-09-01) - 품사 분석 시스템 구축
- 🎯 **KoNLPy + Java 환경 구축**: WSL2 가상환경에서 품사 분석 시스템 완성
- 🔧 **스마트 키워드 필터링**: 사용자 검색 관점 기반 자동 필터링
  - 기능어 자동 제거: "타고", "출발", "또는" 등
  - 위치/활동 키워드만 학습: "크라비", "카약", "맑은" 등
  - 임계값(7) 도달 시 확정 키워드로 자동 승격
- 📋 **프론트엔드 서비스 설계**: `프론트엔드아이디어.md` 문서 작성
  - 인천공항 이용자 지원 서비스 (편명 → 자동 알람)
  - 글로벌 공항 → 숙소 이동 가이드
  - 제휴 마케팅 통합 수익화 전략
- 🔄 **다음 작업 준비**: 컬럼 구조 최적화 (21개 → 15개) 설계 완료

### v2.1 (2025-08-28)
- 페이지네이션 무한루프 버그 수정 (1→2→1→2 반복 → 1→2→3→4 순차진행)
- 위치 학습 시스템 리팩토링
- 파일 구조 변경: `크라비_keywords.json` → `아시아/태국/KBV_keywords.json`
- 대륙/국가/도시코드 기반 계층 구조 적용
- 마이그레이션 스크립트 구현 및 실행 완료
- 자동 백업 시스템 구현 (`backup_YYYYMMDD_HHMMSS` 폴더)
- README.md 문서화 완료
- 크롤링 데이터 컬럼 분석 및 설계 문서 작성 (`../컬럼정리.txt`)

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
### ✅ 완료된 작업
- [x] 새로운 구조로 크라비 크롤링 테스트 실행
- [x] 기존 코드와의 호환성 확인
- [x] 테스트 성공 후 마이그레이션 스크립트 및 백업 파일 정리
- [x] 다른 도시 (파리 등) 마이그레이션 추가
- [x] 품사 분석 기반 키워드 필터링 시스템 구축

### 🚀 다음 작업 (내일 진행)
- [ ] **file_handler.py 컬럼 구조 최적화**
  - 현재 21개 → 15개 컬럼으로 축소
  - `create_product_data_structure` 함수 수정
- [ ] **새 컬럼 추가**
  - 메인이미지경로, 썸네일이미지경로
  - 소요시간, 제휴URL
- [ ] **중복 컬럼 제거**
  - 언어 필드 중복 수정
  - 불필요한 메타데이터 제거

## 기술 스택
- Python 3.x
- Selenium WebDriver
- Jupyter Notebook
- JSON 데이터 저장
- KoNLPy + Java (품사 분석)
- WSL2 + 가상환경

## 마이그레이션 도구
- `migrate_location_files.py`: 위치 학습 파일 구조 변경 스크립트
- 자동 백업 및 롤백 기능 포함