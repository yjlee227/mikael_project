### **PROJECT_PLAN.md (초안)**

### **🔥 Phase 1: 데이터 기반 구축 (예상 소요: 2-3주)**

| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1.1 | 대상 상품 선정 | 비교할 도시, 카테고리 기준 확정 | 웹 브라우저 | 기준 정의서 (간단한 Markdown) | 0.5일 |
| 1.2 | URL 수집 | 기준에 맞는 상품 URL 30개 수집 | 웹 브라우저 | `data/target_urls.json` | 0.5일 |
| 1.3 | 크롤러 수정/검증 | 최신 사이트에 맞게 크롤러 코드 점검 | `kkday/`, `klook/`, `Myrealtrip/` 내 크롤러 파일 | 수정된 크롤러 스크립트 | 3-4일 |
| 1.4 | 데이터 수집 실행 | 크롤러를 실행하여 원시 데이터 수집 | Python, 크롤러 스크립트 | `data/raw/` 내 플랫폼별 JSON 파일 | 1일 |
| 1.5 | 데이터 정제 | 수집된 데이터 표준화 및 정제 | Python (Pandas) | `data/processed/cleaned_data.csv` | 1일 |
| 1.6 | 통합 스키마 확정 | DB 테이블 구조 최종 설계 | `travel_comparison_engine/unified_travel_database.py` | 최종 스키마가 반영된 Python 파일 | 2일 |
| 1.7 | 매칭 알고리즘 구현 | 제목 유사도 기반 매칭 로직 개발 | Python (e.g., `thefuzz` 라이브러리) | `notebooks/matching_test.ipynb` | 2-3일 |
| 1.8 | 분석 리포트 작성 | 비교 분석표, 시각화 차트 포함 | Python (Matplotlib), Markdown | `reports/comparison_report_v1.md` | 1-2일 |

### **🚀 Phase 2: 백엔드 개발 (예상 소요: 1-2주)**

| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2.1 | 개발 환경 설정 | FastAPI 프로젝트 구조 및 라이브러리 설치 | `requirements.txt`, `Dockerfile` | `backend_api/` 프로젝트 폴더 | 1일 |
| 2.2 | DB 모델링/연동 | SQLAlchemy 모델 생성 및 DB 연결 | `backend_api/database.py`, `models.py` | DB 테이블 및 연결 설정 | 2일 |
| 2.3 | 데이터 Seeding | 정제된 데이터를 DB에 삽입 | Python 스크립트 | DB에 초기 데이터 적재 | 0.5일 |
| 2.4 | CRUD 로직 구현 | 데이터 생성, 조회, 수정, 삭제 로직 | `backend_api/crud.py` | 핵심 DB 인터페이스 함수 | 2일 |
| 2.5 | API 라우터 구현 | 각 엔드포인트(라우터) 개발 | `backend_api/routers/` | `/products`, `/search` 등 API | 2.5일 |
| 2.6 | 캐싱 적용 | Redis를 이용한 API 응답 캐싱 | `backend_api/main.py` | 응답 속도가 개선된 API | 1일 |
| 2.7 | 단위/통합 테스트 | `pytest`를 이용한 API 테스트 코드 작성 | `backend_api/tests/` | API 테스트 코드 | 2일 |

### **🎨 Phase 3: 프론트엔드 개발 (예상 소요: 2-3주)**

| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 3.1 | 개발 환경 설정 | Next.js, TypeScript, Tailwind CSS 설정 | `package.json` | `frontend_web/` 프로젝트 폴더 | 1일 |
| 3.2 | UI 컴포넌트 개발 | 재사용 가능한 UI 컴포넌트 제작 | `frontend_web/components/` | `ProductCard.tsx`, `SearchBar.tsx` 등 | 3일 |
| 3.3 | 페이지 레이아웃/라우팅 | 메인, 검색, 비교 페이지 등 라우팅 설정 | `frontend_web/app/` | 기본 페이지 구조 | 2일 |
| 3.4 | API 연동/상태관리 | 백엔드 API 호출 및 `Zustand`로 상태관리 | `frontend_web/lib/api.ts`, `store.ts` | API 호출 함수 및 전역 스토어 | 3일 |
| 3.5 | 페이지 기능 구현 | 각 페이지에 실제 데이터 연동 및 기능 구현 | `frontend_web/app/**/page.tsx` | 기능이 구현된 웹 페이지 | 3일 |
| 3.6 | 반응형 디자인 | 모바일, 태블릿 등 다양한 화면 크기 지원 | Tailwind CSS | 반응형 UI | 2일 |

### **⚙️ Phase 4: 자동화 & 최적화 (예상 소요: 1-2주)**

| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4.1 | 크롤러 스크립트화 | `.ipynb` 파일을 `.py` 스크립트로 변환 | `scripts/run_crawler.py` | 자동 실행 가능한 크롤러 스크립트 | 3일 |
| 4.2 | 스케줄링 설정 | GitHub Actions 등으로 매일 자동 실행 | `.github/workflows/crawler.yml` | 자동화된 크롤링 파이프라인 | 2일 |
| 4.3 | 데이터 검증/알림 | 크롤링 후 데이터 무결성 검사 및 오류 알림 | `scripts/validate_data.py` | 데이터 검증 시스템 | 2일 |
| 4.4 | 성능 최적화 | DB 인덱싱, API 쿼리 최적화 | PostgreSQL, FastAPI 코드 | 최적화된 쿼리 및 인덱스 | 2일 |

### **🎯 Phase 5: 배포 & 런칭 (예상 소요: 1주)**

| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 5.1 | 백엔드 배포 | Railway에 FastAPI 앱 배포 | `Dockerfile`, Railway | 동작 중인 백엔드 서비스 URL | 2일 |
| 5.2 | 프론트엔드 배포 | Vercel에 Next.js 앱 배포 | Vercel | 동작 중인 웹사이트 URL | 1일 |
| 5.3 | 도메인 연결 | 구매한 도메인에 프론트/백엔드 연결 | DNS 설정 | `yourdomain.com`, `api.yourdomain.com` | 1일 |
| 5.4 | 베타 테스트 | 지인 대상 테스트 및 피드백 수집 | Google Forms | 버그 및 개선사항 리스트 | 3일 |

### **📈 Phase 6: 개선 & 성장 (예상 소요: 지속)**

| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 6.1 | 분석 도구 도입 | Google Analytics, Hotjar 등 설치 | Next.js 코드 | 사용자 행동 분석 대시보드 | 2일 |
| 6.2 | 기능 개선 | 피드백 기반 기능 개선 및 우선순위 관리 | Jira, Trello 등 | 업데이트된 기능 | 지속 |
| 6.3 | 콘텐츠 확장 | 신규 도시, 신규 플랫폼 추가 | 크롤러 스크립트 | 확장된 DB 데이터 | 지속 |
| 6.4 | 수익 모델 적용 | 제휴 마케팅 링크 적용 | 백엔드 로직 | 제휴 수익 창출 시스템 | 지속 |
