# 🗺️ 여행상품 비교 시스템 웹 배포 로드맵

## 📋 개요

현재 단계에서 완전한 웹 서비스 배포까지의 세분화된 6주 작업 계획입니다.

**목표**: 3개 플랫폼(MyRealTrip, KLOOK, KKday) 데이터를 활용한 여행상품 비교 웹 서비스 구축

---

## 🔥 Phase 1: 데이터 기반 구축 (2-3주)

### 📊 Week 1: 데이터 수집 & 분석

#### **Day 1-2: 데이터 수집 완료**
```
✅ 현재 진행중: 3개 플랫폼 데이터 수집
├── MyRealTrip: 도쿄 10개 상품
├── KLOOK: 도쿄 10개 상품
└── KKday: 도쿄 10개 상품

수집 데이터 형식:
- CSV 파일 (각 플랫폼별)
- 이미지 파일
- 메타데이터
```

#### **Day 3-4: 데이터 분석 및 시각화**
```python
# 1. 데이터 품질 분석
- 컬럼 완성도 체크
- 누락 데이터 식별
- 데이터 타입 검증

# 2. 시각화 생성
plt.figure(figsize=(12, 8))
# 가격 비교 막대 그래프
# 플랫폼별 평점 분포
# 카테고리별 상품 수
# 누락 데이터 히트맵

# 3. 비교 가능성 분석
- 동일 상품 매칭률 계산
- 가격 분산 분석
- 플랫폼별 강점 분석
```

#### **Day 5-7: 통합 스키마 최적화**
```sql
-- 기존 21컬럼 스키마 개선
CREATE TABLE travel_products_v2 (
    id SERIAL PRIMARY KEY,

    -- 필수 식별 정보 (100% 필수)
    provider VARCHAR(50) NOT NULL,
    provider_product_id VARCHAR(100) NOT NULL,
    destination_city VARCHAR(100) NOT NULL,
    product_title TEXT NOT NULL,

    -- 비교 핵심 정보 (90% 완성도 목표)
    price DECIMAL(10,2),
    currency VARCHAR(10),
    rating DECIMAL(3,2),
    review_count INTEGER,

    -- 매칭 보조 정보 (80% 완성도 목표)
    category VARCHAR(100),
    duration VARCHAR(50),
    main_image_url TEXT,

    -- 부가 정보 (60% 완성도 목표)
    highlights TEXT[],
    languages VARCHAR(50)[],
    tour_type VARCHAR(50),

    -- 시스템 정보
    product_hash VARCHAR(40) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 매칭 결과 테이블
CREATE TABLE product_matches (
    id SERIAL PRIMARY KEY,
    product_1_id INTEGER REFERENCES travel_products_v2(id),
    product_2_id INTEGER REFERENCES travel_products_v2(id),
    similarity_score DECIMAL(5,4),
    match_type VARCHAR(20), -- exact, similar, potential
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 🧪 Week 2: 알고리즘 테스트 & API 설계

#### **Day 8-10: 상품 매칭 알고리즘 실제 테스트**
```python
# 1. 매칭 알고리즘 구현
class ProductMatcher:
    def __init__(self):
        self.bm25_weight = 0.4
        self.embedding_weight = 0.3
        self.structured_weight = 0.3

    def match_products(self, product_a, product_b):
        # BM25 점수 계산
        bm25_score = self.calculate_bm25(
            product_a.title + " " + product_a.category,
            product_b.title + " " + product_b.category
        )

        # 임베딩 유사도 (Sentence-BERT)
        embedding_score = self.calculate_embedding_similarity(
            product_a.title, product_b.title
        )

        # 구조화된 데이터 매칭
        structured_score = self.calculate_structured_match(
            product_a, product_b
        )

        final_score = (
            bm25_score * self.bm25_weight +
            embedding_score * self.embedding_weight +
            structured_score * self.structured_weight
        )

        return final_score

    def calculate_structured_match(self, a, b):
        score = 0.0
        # 가격 유사도 (±20% 이내)
        if abs(a.price - b.price) / max(a.price, b.price) < 0.2:
            score += 0.3
        # 카테고리 일치
        if a.category == b.category:
            score += 0.4
        # 평점 유사도
        if abs(a.rating - b.rating) < 0.5:
            score += 0.3
        return score

# 2. 테스트 데이터로 검증
test_results = []
for mrt_product in myrealtrip_products:
    for klook_product in klook_products:
        score = matcher.match_products(mrt_product, klook_product)
        if score > 0.7:  # 임계값
            test_results.append({
                'mrt': mrt_product.title,
                'klook': klook_product.title,
                'score': score,
                'verified': None  # 수동 검증 필요
            })

# 3. 수동 검증 및 정확도 계산
manually_verify_matches(test_results)
accuracy = calculate_accuracy(test_results)
print(f"매칭 정확도: {accuracy:.2f}%")
```

#### **Day 11-14: FastAPI 백엔드 설계**
```python
# 프로젝트 구조
travel_compare_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱
│   ├── models/              # SQLAlchemy 모델
│   │   ├── __init__.py
│   │   ├── product.py
│   │   └── match.py
│   ├── schemas/             # Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── product.py
│   │   └── response.py
│   ├── api/                 # API 라우터
│   │   ├── __init__.py
│   │   ├── products.py
│   │   ├── compare.py
│   │   └── search.py
│   ├── core/                # 핵심 로직
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── matcher.py
│   └── utils/               # 유틸리티
│       ├── __init__.py
│       └── cache.py
├── requirements.txt
└── docker-compose.yml

# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Travel Product Comparison API",
    description="여행상품 비교 서비스 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(compare.router, prefix="/api/compare", tags=["compare"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

@app.get("/")
async def root():
    return {"message": "Travel Comparison API is running!"}
```

---

## 🎨 Phase 2: 프론트엔드 개발 (2-3주)

### Week 3-4: Next.js 개발

#### **Day 15-18: 프로젝트 설정 & 기본 구조**
```bash
# 프로젝트 생성
npx create-next-app@latest travel-compare-web --typescript --tailwind --eslint

# 프로젝트 구조
travel-compare-web/
├── pages/
│   ├── index.tsx            # 메인 페이지
│   ├── compare/
│   │   └── [city].tsx       # 도시별 비교 페이지
│   ├── product/
│   │   └── [id].tsx         # 상품 상세 페이지
│   └── api/                 # Next.js API 라우트 (프록시)
├── components/              # 재사용 컴포넌트
│   ├── common/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── Layout.tsx
│   ├── product/
│   │   ├── ProductCard.tsx
│   │   ├── ProductList.tsx
│   │   └── ComparisonTable.tsx
│   └── charts/
│       ├── PriceChart.tsx
│       └── RatingChart.tsx
├── hooks/                   # 커스텀 훅
│   ├── useProducts.ts
│   └── useComparison.ts
├── lib/                     # 유틸리티
│   ├── api.ts
│   ├── types.ts
│   └── utils.ts
├── styles/                  # 스타일
└── public/                  # 정적 파일
```

#### **Day 19-21: 핵심 컴포넌트 개발**
```typescript
// types.ts
export interface Product {
  id: number;
  provider: 'MyRealTrip' | 'KLOOK' | 'KKday';
  provider_product_id: string;
  destination_city: string;
  product_title: string;
  price: number;
  currency: string;
  rating: number;
  review_count: number;
  category: string;
  duration: string;
  main_image_url: string;
  product_url: string;
}

export interface ComparisonResult {
  products: Product[];
  comparison: {
    cheapest: Product;
    most_expensive: Product;
    average_rating: number;
    price_difference: number;
  };
}

// ProductCard.tsx
import Image from 'next/image';
import { Product } from '@/lib/types';

interface ProductCardProps {
  product: Product;
  isComparing?: boolean;
  onCompare?: (product: Product) => void;
}

export default function ProductCard({ product, isComparing, onCompare }: ProductCardProps) {
  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: currency === 'KRW' ? 'KRW' : 'USD'
    }).format(price);
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-4">
      <div className="relative h-48 mb-4">
        <Image
          src={product.main_image_url || '/placeholder.jpg'}
          alt={product.product_title}
          fill
          className="object-cover rounded"
        />
        <div className="absolute top-2 left-2 bg-blue-500 text-white px-2 py-1 rounded text-sm">
          {product.provider}
        </div>
      </div>

      <h3 className="font-semibold text-lg mb-2 line-clamp-2">
        {product.product_title}
      </h3>

      <div className="flex justify-between items-center mb-2">
        <span className="text-2xl font-bold text-blue-600">
          {formatPrice(product.price, product.currency)}
        </span>
        <div className="flex items-center">
          <span className="text-yellow-500">★</span>
          <span className="ml-1">{product.rating}</span>
          <span className="text-gray-500 ml-1">({product.review_count})</span>
        </div>
      </div>

      <div className="flex justify-between items-center">
        <span className="text-gray-600 text-sm">{product.category}</span>
        <button
          onClick={() => onCompare?.(product)}
          className={`px-4 py-2 rounded text-sm ${
            isComparing
              ? 'bg-red-500 text-white'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          {isComparing ? '비교 제거' : '비교 추가'}
        </button>
      </div>
    </div>
  );
}
```

#### **Day 22-28: 페이지 구현 & 통합**
```typescript
// pages/index.tsx (메인 페이지)
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/common/Layout';
import ProductCard from '@/components/product/ProductCard';
import { Product } from '@/lib/types';
import { searchProducts } from '@/lib/api';

export default function Home() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCity, setSelectedCity] = useState('도쿄');
  const [compareList, setCompareList] = useState<Product[]>([]);

  useEffect(() => {
    loadProducts();
  }, [selectedCity]);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await searchProducts({ city: selectedCity });
      setProducts(data.products);
    } catch (error) {
      console.error('상품 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = (product: Product) => {
    const isAlreadyComparing = compareList.some(p => p.id === product.id);

    if (isAlreadyComparing) {
      setCompareList(compareList.filter(p => p.id !== product.id));
    } else {
      if (compareList.length < 3) {
        setCompareList([...compareList, product]);
      } else {
        alert('최대 3개까지 비교할 수 있습니다.');
      }
    }
  };

  const goToCompare = () => {
    if (compareList.length >= 2) {
      const productIds = compareList.map(p => p.id).join(',');
      router.push(`/compare?products=${productIds}`);
    }
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* 검색 섹션 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h1 className="text-3xl font-bold text-center mb-6">
            여행상품 가격 비교
          </h1>

          <div className="flex flex-col md:flex-row gap-4">
            <select
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              className="flex-1 p-3 border border-gray-300 rounded-lg"
            >
              <option value="도쿄">도쿄</option>
              <option value="오사카">오사카</option>
              <option value="방콕">방콕</option>
              <option value="싱가포르">싱가포르</option>
            </select>

            <input
              type="text"
              placeholder="상품명으로 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 p-3 border border-gray-300 rounded-lg"
            />

            <button
              onClick={loadProducts}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              검색
            </button>
          </div>
        </div>

        {/* 상품 목록 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {loading ? (
            // 로딩 스켈레톤
            Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="bg-gray-200 animate-pulse rounded-lg h-80"></div>
            ))
          ) : (
            products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                isComparing={compareList.some(p => p.id === product.id)}
                onCompare={handleCompare}
              />
            ))
          )}
        </div>
      </div>
    </Layout>
  );
}
```

---

## ⚙️ Phase 3: 자동화 & 배포 (1-2주)

### Week 5: 시스템 통합 & 자동화

#### **Day 29-32: 데이터 자동 업데이트 시스템**
```python
# scheduler.py
import schedule
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.product import Product
from crawlers.kkday_crawler import KKdayCrawler
from crawlers.klook_crawler import KlookCrawler
from crawlers.myrealtrip_crawler import MyRealTripCrawler

class DataUpdateScheduler:
    def __init__(self):
        self.db = SessionLocal()
        self.crawlers = {
            'kkday': KKdayCrawler(),
            'klook': KlookCrawler(),
            'myrealtrip': MyRealTripCrawler()
        }

    def update_city_data(self, city: str):
        """특정 도시 데이터 업데이트"""
        print(f"[{datetime.now()}] {city} 데이터 업데이트 시작")

        for platform, crawler in self.crawlers.items():
            try:
                # 새 데이터 크롤링
                new_products = crawler.crawl_city(city, max_products=20)

                # 기존 데이터와 비교 후 업데이트
                updated_count = self.update_products(platform, new_products)

                print(f"[{platform}] {updated_count}개 상품 업데이트 완료")

            except Exception as e:
                print(f"[{platform}] 업데이트 실패: {e}")

        print(f"[{datetime.now()}] {city} 데이터 업데이트 완료")

    def run_scheduler(self):
        """스케줄러 실행"""
        # 매일 오전 6시에 인기 도시 업데이트
        schedule.every().day.at("06:00").do(self.update_city_data, "도쿄")
        schedule.every().day.at("06:30").do(self.update_city_data, "오사카")
        schedule.every().day.at("07:00").do(self.update_city_data, "방콕")

        # 매주 일요일에 전체 데이터 검증
        schedule.every().sunday.at("03:00").do(self.verify_all_data)

        print("스케줄러 시작...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크

# Docker 컨테이너로 실행
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/travel_compare
    depends_on:
      - db
      - redis

  scheduler:
    build: .
    command: python scheduler.py
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/travel_compare
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: travel_compare
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

#### **Day 33-35: 배포 준비**
```bash
# 배포 스크립트
# deploy.sh
#!/bin/bash

echo "🚀 Travel Compare 배포 시작..."

# 1. 백엔드 배포 (Railway)
echo "📦 백엔드 배포 중..."
cd travel_compare_api
railway login
railway up

# 2. 프론트엔드 배포 (Vercel)
echo "🎨 프론트엔드 배포 중..."
cd ../travel-compare-web
vercel --prod

# 3. 데이터베이스 마이그레이션
echo "🗄️ 데이터베이스 설정 중..."
alembic upgrade head

# 4. 초기 데이터 로드
echo "📊 초기 데이터 로드 중..."
python scripts/load_initial_data.py

echo "✅ 배포 완료!"
echo "🌐 웹사이트: https://travel-compare.vercel.app"
echo "📡 API: https://travel-compare-api.railway.app"
```

---

## 🎯 Phase 4: 테스트 & 출시 (1주)

### Week 6: 최종 테스트 & 런칭

#### **Day 36-42: 종합 테스트 & 최적화**
```python
# 성능 테스트
import asyncio
import aiohttp
import time

async def performance_test():
    """API 성능 테스트"""
    base_url = "https://travel-compare-api.railway.app"

    # 동시 요청 테스트
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):  # 100개 동시 요청
            task = session.get(f"{base_url}/api/products?city=도쿄")
            tasks.append(task)

        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        print(f"100개 요청 처리 시간: {end_time - start_time:.2f}초")
        print(f"평균 응답 시간: {(end_time - start_time) / 100:.3f}초")

# 사용자 테스트 스크립트
test_scenarios = [
    {
        "name": "기본 검색",
        "steps": [
            "메인 페이지 접속",
            "도쿄 선택",
            "검색 버튼 클릭",
            "결과 확인"
        ]
    },
    {
        "name": "상품 비교",
        "steps": [
            "상품 3개 선택",
            "비교하기 클릭",
            "비교 결과 확인",
            "최저가 상품 확인"
        ]
    },
    {
        "name": "예약 연결",
        "steps": [
            "상품 선택",
            "예약하기 클릭",
            "원본 사이트 이동 확인"
        ]
    }
]
```

---

## 📈 최종 결과물

### 🎯 완성된 시스템
1. **데이터**: 3개 플랫폼 × 10개 도시 × 평균 50개 상품 = 1,500개 상품
2. **API**: 초당 100+ 요청 처리 가능
3. **웹사이트**: 모바일/데스크톱 최적화
4. **자동화**: 매일 자동 데이터 업데이트

### 💰 운영 비용 (월)
- 데이터베이스: $15 (Railway PostgreSQL)
- API 서버: $5 (Railway Hobby)
- 프론트엔드: $0 (Vercel Free)
- **총합: $20/월**

### 📊 예상 성과
- **사용자**: 월 1,000+ 방문자
- **절약 금액**: 사용자당 평균 15,000원
- **매칭 정확도**: 90%+
- **응답 속도**: 평균 500ms 이하

---

## 🎯 단계별 핵심 마일스톤

| Week | 핵심 목표 | 성공 지표 | 예상 소요시간 |
|------|----------|----------|---------------|
| 1 | 데이터 검증 | 30개 상품 매칭 80% 성공 | 40시간 |
| 2-3 | API 완성 | 응답시간 < 1초 | 60시간 |
| 4-5 | 웹사이트 완성 | 모든 기능 정상 작동 | 80시간 |
| 6 | 자동화 | 24시간 무중단 운영 | 30시간 |
| 7 | MVP 출시 | 실제 사용자 접속 | 20시간 |

**총 예상 작업시간: 230시간 (6주)**

---

## 🚀 시작하기

### 즉시 실행 가능한 다음 단계

1. **데이터 수집 완료** (현재 진행중)
   - 3개 플랫폼에서 도쿄 상품 각 10개 수집

2. **개발 환경 설정**
   ```bash
   # 백엔드 프로젝트 생성
   mkdir travel_compare_api
   cd travel_compare_api
   pip install fastapi uvicorn sqlalchemy psycopg2-binary

   # 프론트엔드 프로젝트 생성
   npx create-next-app@latest travel-compare-web --typescript --tailwind
   ```

3. **데이터 분석 시작**
   - 수집된 CSV 파일 로드
   - 시각화 코드 작성
   - 매칭 알고리즘 테스트

이 로드맵대로 진행하면 **6주 안에 완전한 여행상품 비교 서비스**를 런칭할 수 있습니다! 🎉

---

**문서 버전**: v1.0
**생성일**: 2025-09-17
**최종 업데이트**: 2025-09-17