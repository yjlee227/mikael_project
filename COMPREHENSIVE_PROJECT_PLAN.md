# **종합 프로젝트 계획 (Comprehensive Project Plan) v1.0**

## **1. 🗺️ 프로젝트 개요**

- **프로젝트명:** 여행상품 비교 시스템 구축 및 웹 배포
- **최종 목표:** 3개 플랫폼(MyRealTrip, KLOOK, KKday)의 여행상품 데이터를 수집, 비교, 분석하여 사용자에게 제공하는 완전한 웹 서비스 구축
- **예상 기간:** 총 7주 (MVP 출시 기준)

---

## **2. 🔥 Phase 1: 데이터 기반 구축 (2-3주)**

### **2.1. 목표**
3개 플랫폼에서 상품 데이터를 수집하고, 데이터 분석 및 스키마 최적화를 거쳐 상품 매칭 알고리즘의 유효성을 검증합니다. 최종적으로 비교 분석 리포트를 완성하여 데이터 기반을 확립합니다.

### **2.2. 상세 실행 계획**
| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1.1 | 대상 상품 선정 | 비교할 도시, 카테고리 기준 확정 | 웹 브라우저 | 기준 정의서 (Markdown) | 0.5일 |
| 1.2 | URL 수집 | 기준에 맞는 상품 URL 30개 수집 | 웹 브라우저 | `data/target_urls.json` | 0.5일 |
| 1.3 | 크롤러 수정/검증 | 최신 사이트 구조에 맞게 크롤러 코드 점검 | `kkday/`, `klook/`, `Myrealtrip/` 크롤러 | 수정된 크롤러 스크립트 | 3-4일 |
| 1.4 | 데이터 수집 실행 | 크롤러를 실행하여 원시 데이터 수집 | Python, 크롤러 스크립트 | `data/raw/` 내 플랫폼별 JSON | 1일 |
| 1.5 | 데이터 정제/분석 | 수집 데이터 표준화 및 품질 분석. **(→ 2.3.B 기술 명세 참고)** | Python (Pandas, Matplotlib) | `data/processed/cleaned_data.csv` | 1일 |
| 1.6 | 통합 스키마 확정 | DB 테이블 구조 최종 설계. **(→ 2.3.A 기술 명세 참고)** | `travel_comparison_engine/unified_travel_database.py` | 최종 스키마가 반영된 Python 파일 | 2일 |
| 1.7 | 매칭 알고리즘 구현 | BM25, Embedding 등을 결합한 매칭 로직 개발. **(→ 2.3.C 기술 명세 참고)** | Python (`thefuzz`, `sentence-transformers`) | `notebooks/matching_test.ipynb` | 2-3일 |
| 1.8 | 분석 리포트 작성 | 비교 분석표, 시각화 차트를 포함한 리포트 | Python (Matplotlib), Markdown | `reports/comparison_report_v1.md` | 1-2일 |

### **2.3. 기술 명세 (Developer's Reference)**
#### **A. 통합 데이터베이스 스키마 (v2)**
*(관련 작업: 1.6)*
```sql
CREATE TABLE travel_products_v2 (
    id SERIAL PRIMARY KEY, provider VARCHAR(50) NOT NULL, provider_product_id VARCHAR(100) NOT NULL, destination_city VARCHAR(100) NOT NULL, product_title TEXT NOT NULL, price DECIMAL(10,2), currency VARCHAR(10), rating DECIMAL(3,2), review_count INTEGER, category VARCHAR(100), main_image_url TEXT, product_hash VARCHAR(40) UNIQUE, created_at TIMESTAMP DEFAULT NOW(), updated_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE product_matches (
    id SERIAL PRIMARY KEY, product_1_id INTEGER REFERENCES travel_products_v2(id), product_2_id INTEGER REFERENCES travel_products_v2(id), similarity_score DECIMAL(5,4), match_type VARCHAR(20), verified BOOLEAN DEFAULT FALSE
);
```
#### **B. 데이터 분석 및 시각화 코드 예시**
*(관련 작업: 1.5, 1.8)*
```python
import matplotlib.pyplot as plt
import seaborn as sns
# 데이터 품질 분석: 누락 데이터 히트맵, 가격 비교 막대 그래프, 평점 분포 등
plt.figure(figsize=(12, 8))
sns.heatmap(df.isnull(), cbar=False)
plt.title('Missing Data Heatmap')
plt.show()
```
#### **C. 상품 매칭 알고리즘 로직**
*(관련 작업: 1.7)*
```python
class ProductMatcher:
    def __init__(self, bm25_weight=0.4, embedding_weight=0.3, structured_weight=0.3):
        self.bm25_weight = bm25_weight; self.embedding_weight = embedding_weight; self.structured_weight = structured_weight
    def match_products(self, product_a, product_b):
        # BM25 (텍스트 유사도), Sentence-BERT (의미 유사도), 정형 데이터(가격, 카테고리) 점수를 가중 합산
        final_score = (self.calculate_bm25(product_a.title, product_b.title) * self.bm25_weight + self.calculate_embedding_similarity(product_a.title, product_b.title) * self.embedding_weight + self.calculate_structured_match(product_a, product_b) * self.structured_weight)
        return final_score
```

---

## **3. 🚀 Phase 2: 백엔드 개발 (1-2주)**

### **3.1. 목표**
FastAPI를 사용하여 데이터베이스와 연동된 안정적이고 빠른 RESTful API 서버를 구축합니다. 상품 조회, 검색, 비교 API를 개발하고 캐싱을 적용하여 성능을 최적화합니다.

### **3.2. 상세 실행 계획**
| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2.1 | 개발 환경 설정 | FastAPI 프로젝트 구조 설계 및 라이브러리 설치. **(→ 3.3.A 기술 명세 참고)** | `requirements.txt`, `Dockerfile` | `backend_api/` 프로젝트 폴더 | 1일 |
| 2.2 | DB 모델링/연동 | SQLAlchemy 모델 생성 및 DB 연결 설정 | `backend_api/database.py`, `models.py` | DB 테이블 및 연결 설정 | 2일 |
| 2.3 | 데이터 Seeding | 정제된 데이터를 DB에 삽입하는 스크립트 작성 | `scripts/seed_db.py` | DB에 초기 데이터 적재 | 0.5일 |
| 2.4 | CRUD 로직 구현 | 데이터 생성, 조회, 수정, 삭제 로직 추상화 | `backend_api/crud.py` | 핵심 DB 인터페이스 함수 | 2일 |
| 2.5 | API 라우터 구현 | 각 엔드포인트(라우터) 개발. **(→ 3.3.B 기술 명세 참고)** | `backend_api/routers/` | `/products`, `/search` 등 API | 2.5일 |
| 2.6 | 캐싱 적용 | Redis를 이용한 API 응답 캐싱 로직 구현 | `backend_api/utils/cache.py` | 응답 속도가 개선된 API | 1일 |
| 2.7 | 단위/통합 테스트 | `pytest`를 이용한 API 기능 및 성능 테스트 코드 작성 | `backend_api/tests/` | API 테스트 코드 | 2일 |

### **3.3. 기술 명세 (Developer's Reference)**
#### **A. 백엔드 프로젝트 구조**
*(관련 작업: 2.1)*
```
travel_compare_api/
├── app/
│   ├── main.py, models/, schemas/, api/, core/
├── requirements.txt
└── docker-compose.yml
```
#### **B. FastAPI 메인 앱 및 라우터 예시**
*(관련 작업: 2.5)*
```python
# main.py
from fastapi import FastAPI
from .api import products
app = FastAPI(title="Travel Product Comparison API")
app.include_router(products.router, prefix="/api/products", tags=["products"])

# api/products.py
from fastapi import APIRouter, Depends
router = APIRouter()
@router.get("/", response_model=List[schemas.Product])
def read_products(db: Session = Depends(get_db)):
    return crud.get_products(db)
```

---

## **4. 🎨 Phase 3: 프론트엔드 개발 (2-3주)**

### **4.1. 목표**
Next.js를 사용하여 백엔드 API와 통신하는 사용자 친화적인 웹 인터페이스를 개발합니다. 실시간 가격 비교, 필터링, 시각화 차트 등 핵심 기능을 구현하고 모바일 환경에 최적화된 반응형 디자인을 적용합니다.

### **4.2. 상세 실행 계획**
| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 3.1 | 개발 환경 설정 | Next.js, TypeScript, Tailwind CSS 프로젝트 설정. **(→ 4.3.A 기술 명세 참고)** | `package.json` | `frontend_web/` 프로젝트 폴더 | 1일 |
| 3.2 | UI 컴포넌트 개발 | 재사용 가능한 UI 컴포넌트(카드, 버튼 등) 제작. **(→ 4.3.C 기술 명세 참고)** | `frontend_web/components/` | `ProductCard.tsx`, `SearchBar.tsx` | 3일 |
| 3.3 | 페이지 레이아웃/라우팅 | 메인, 검색, 비교 페이지 등 라우팅 및 기본 레이아웃 설정 | `frontend_web/app/` | 기본 페이지 구조 | 2일 |
| 3.4 | API 연동/상태관리 | 백엔드 API 호출 및 `Zustand` 또는 `SWR`로 상태관리 | `frontend_web/lib/api.ts`, `hooks/` | API 호출 함수 및 전역 스토어 | 3일 |
| 3.5 | 페이지 기능 구현 | 각 페이지에 실제 데이터 연동 및 기능 구현. **(→ 4.3.D 기술 명세 참고)** | `frontend_web/app/**/page.tsx` | 기능이 구현된 웹 페이지 | 3일 |
| 3.6 | 반응형 디자인 | 모바일, 태블릿 등 다양한 화면 크기 지원 | Tailwind CSS | 반응형 UI | 2일 |

### **4.3. 기술 명세 (Developer's Reference)**
#### **A. 프론트엔드 프로젝트 구조**
*(관련 작업: 3.1)*
```
travel-compare-web/
├── app/
│   ├── (pages)/, layout.tsx
├── components/
├── hooks/
└── lib/
```
#### **B. 타입 정의 (`types.ts`)**
*(관련 작업: 3.4)*
```typescript
export interface Product { id: number; provider: string; product_title: string; price: number; /* ... */ }
```
#### **C. 핵심 컴포넌트: `ProductCard.tsx`**
*(관련 작업: 3.2)*
```typescript
import Image from 'next/image';
import { Product } from '@/lib/types';
export default function ProductCard({ product }: { product: Product }) { /* ... */ }
```
#### **D. 메인 페이지 데이터 페칭 예시 (Server Component)**
*(관련 작업: 3.5)*
```typescript
// app/(pages)/page.tsx
import { searchProducts } from '@/lib/api';
export default async function Home() {
  const initialProducts = await searchProducts({ city: '도쿄' });
  return ( <ProductList initialProducts={initialProducts} /> );
}
```

---

## **5. ⚙️ Phase 4: 자동화 & 최적화 (1-2주)**

### **5.1. 목표**
수동으로 이루어지던 데이터 수집 및 갱신 프로세스를 자동화하고, API 응답 속도 및 DB 쿼리 효율성을 개선하여 시스템을 안정화시킵니다.

### **5.2. 상세 실행 계획**
| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 4.1 | 크롤러 스크립트화 | `.ipynb` 파일을 `.py` 스크립트로 변환 | `scripts/run_crawler.py` | 자동 실행 가능한 크롤러 스크립트 | 3일 |
| 4.2 | 스케줄링 설정 | GitHub Actions 또는 `APScheduler`로 매일 자동 실행. **(→ 5.3.A 기술 명세 참고)** | `.github/workflows/crawler.yml` | 자동화된 크롤링 파이프라인 | 2일 |
| 4.3 | 데이터 검증/알림 | 크롤링 후 데이터 무결성 검사 및 오류 알림 | `scripts/validate_data.py` | 데이터 검증 시스템 | 2일 |
| 4.4 | 성능 테스트/최적화 | DB 인덱싱, API 쿼리 최적화. **(→ 5.3.B 기술 명세 참고)** | PostgreSQL, `pytest` | 최적화된 쿼리 및 인덱스 | 2일 |

### **5.3. 기술 명세 (Developer's Reference)**
#### **A. 데이터 업데이트 스케줄러**
*(관련 작업: 4.2)*
```python
# scheduler.py
import schedule
import time
def job():
    print("Data crawling job running...")

schedule.every().day.at("06:00").do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
```
#### **B. API 성능 테스트**
*(관련 작업: 4.4)*
```python
# tests/test_performance.py
import asyncio
import aiohttp
import time

async def test_api_performance():
    async with aiohttp.ClientSession() as session:
        tasks = [session.get("http://localhost:8000/api/products") for i in range(100)]
        start_time = time.time()
        await asyncio.gather(*tasks)
        duration = time.time() - start_time
        assert duration < 5 # 100개 요청을 5초 안에 처리
```

---

## **6. 🎯 Phase 5: 배포 & 런칭 (1주)**

### **6.1. 목표**
개발된 백엔드와 프론트엔드 애플리케이션을 클라우드에 배포하고, 도메인을 연결하여 실제 사용자가 접속할 수 있는 MVP(Minimum Viable Product)를 출시합니다.

### **6.2. 상세 실행 계획**
| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 5.1 | 백엔드 배포 | Railway에 FastAPI 앱 배포 (`Dockerfile` 사용) | `Dockerfile`, Railway | 동작 중인 백엔드 서비스 URL | 2일 |
| 5.2 | 프론트엔드 배포 | Vercel에 Next.js 앱 배포 | Vercel | 동작 중인 웹사이트 URL | 1일 |
| 5.3 | 도메인 연결 | 구매한 도메인에 프론트/백엔드 연결 | DNS 설정 | `yourdomain.com`, `api.yourdomain.com` | 1일 |
| 5.4 | 베타 테스트 | 지인 대상 테스트 및 피드백 수집. **(→ 6.3.B 기술 명세 참고)** | Google Forms | 버그 및 개선사항 리스트 | 3일 |

### **6.3. 기술 명세 (Developer's Reference)**
#### **A. 배포 스크립트 예시**
*(관련 작업: 5.1, 5.2)*
```bash
#!/bin/bash
# deploy.sh
echo "🚀 Backend Deploying to Railway..."
cd backend_api && railway up
echo "🎨 Frontend Deploying to Vercel..."
cd ../frontend_web && vercel --prod
```
#### **B. 베타 테스트 시나리오**
*(관련 작업: 5.4)*
- **시나리오 1: 기본 검색** (메인 페이지 접속 → 도시 선택 → 검색 → 결과 확인)
- **시나리오 2: 상품 비교** (상품 3개 선택 → 비교하기 → 비교 결과 확인 → 최저가 확인)
- **시나리오 3: 원본 사이트 이동** (상품 카드 클릭 → 원본 플랫폼 상품 페이지로 이동 확인)

---

## **7. 📈 Phase 6: 개선 & 성장 (지속)**

### **7.1. 목표**
사용자 피드백과 데이터 분석을 기반으로 서비스를 지속적으로 개선하고, 콘텐츠 확장 및 수익 모델 적용을 통해 서비스의 성장을 도모합니다.

### **7.2. 상세 실행 계획**
| 작업 번호 | 작업 내용 | 상세 설명 | 사용 도구 / 파일 | 산출물 | 예상 시간 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 6.1 | 분석 도구 도입 | Google Analytics, Hotjar 등 설치 | Next.js 코드 | 사용자 행동 분석 대시보드 | 2일 |
| 6.2 | 기능 개선 | 피드백 기반 기능 개선 및 우선순위 관리 | Jira, Trello 등 | 업데이트된 기능 | 지속 |
| 6.3 | 콘텐츠 확장 | 신규 도시, 신규 플랫폼 추가 | 크롤러 스크립트 | 확장된 DB 데이터 | 지속 |
| 6.4 | 수익 모델 적용 | 제휴 마케팅 링크 적용 로직 개발 | 백엔드 로직 | 제휴 수익 창출 시스템 | 지속 |

### **7.3. 최종 목표 시스템 및 성과 지표**
- **데이터 규모:** 10개 도시 × 3개 플랫폼 × 50개 상품 ≈ 1,500개
- **API 성능:** 초당 100+ 요청 처리
- **매칭 정확도:** 90% 이상
- **월간 운영 비용:** 약 $20 (Railway + Vercel 기준)
- **핵심 성과 지표(KPI):** 월간 활성 사용자(MAU), 평균 비교 세션 시간, 제휴 링크 클릭률
