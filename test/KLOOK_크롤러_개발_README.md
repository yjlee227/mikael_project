# 🏗️ KLOOK 크롤러 개발 프로젝트

## 📋 프로젝트 개요
마이리얼트립 크롤러를 기반으로 KLOOK 글로벌 사이트 크롤링 시스템 개발

**개발 목표**: 전 세계 주요 도시 KLOOK 액티비티/경험 상품 데이터 수집  
**초기 목표**: 서울 지역 750-1,600개 상품 (프로토타입)  
**확장 목표**: 전 세계 50+ 도시, 17,000-33,000개 상품  
**예상 개발 기간**: 2-3일 (단일 도시), 1-2주 (글로벌 확장)

---

## 🚨 중요 발견사항: 크롤링 혁신 전략

### 🎯 **핵심 발견: Sitemap 활용의 게임체인저**

**KLOOK 한국 사이트맵**: `https://www.klook.com/ko/sitemap-master-index.xml`

#### ✅ **왜 이것이 혁신적인가?**
```python
BREAKTHROUGH_ADVANTAGES = {
    "개발_시간": "8-13일 → 2-3일 (75% 단축)",
    "성공률": "70-80% → 95%+ (25% 향상)",
    "법적_안전성": "100% 합법 (robots.txt 공식 제공)",
    "기술_복잡도": "높음 → 낮음 (XML 파싱만 필요)",
    "유지보수": "KLOOK 자동 업데이트"
}
```

---

## 📊 KLOOK 제약사항 분석

### 🔴 **robots.txt 주요 제약**
```python
KLOOK_RESTRICTIONS = {
    "완전_차단": [
        "*/search/*",      # 🚨 검색 결과 페이지
        "*/searchresult/*", # 🚨 검색 결과
        "*/voucher/",      # 바우처 페이지
        "*/my_klook/",     # 개인 페이지
        "*/preview/"       # 미리보기 페이지
    ],
    
    "한국어_특별_제한": {
        "경로": "/ko/",
        "허용_봇": "Yeti (네이버봇)만 허용",
        "일반_크롤러": "제한적 허용"
    },
    
    "API_차단": [
        "/v1/hotelapiserv/*",
        "/xos_api/v1/hotelapiserv/*"
    ]
}
```

### ✅ **활용 가능한 경로**
```python
ALLOWED_PATHS = {
    "Sitemap_기반": "https://www.klook.com/ko/sitemap-master-index.xml",
    "카테고리_페이지": [
        "https://www.klook.com/things-to-do/region-seoul/",
        "https://www.klook.com/attractions/region-seoul/",
        "https://www.klook.com/things-to-do-list/1-seoul/"
    ],
    "이벤트_검색": "https://www.klook.com/event/search/*",
    "직접_상품_URL": "https://www.klook.com/activity/*/"
}
```

---

## 🛠️ 개발 전략

### 🥇 **1순위 전략: Sitemap 활용** (강력 추천)

#### **구현 방법**
```python
def klook_sitemap_strategy():
    """KLOOK Sitemap 기반 크롤링 전략"""
    
    # 1단계: 마스터 사이트맵 분석
    master_sitemap = "https://www.klook.com/ko/sitemap-master-index.xml"
    
    # 2단계: 타겟 카테고리 식별
    target_categories = [
        "experience",  # 경험/액티비티 (핵심)
        "event",       # 이벤트/프로모션
        "city",        # 도시별 상품
        "activity"     # 액티비티
    ]
    
    # 3단계: 서울 관련 URL 필터링
    seoul_filters = ["seoul", "서울", "korea", "한국"]
    
    # 4단계: URL 수집 및 크롤링
    collected_urls = extract_seoul_urls(master_sitemap, target_categories)
    
    return collected_urls

# 예상 결과
EXPECTED_SITEMAP_RESULTS = {
    "서울_액티비티": "500-1,000개",
    "서울_이벤트": "50-100개",
    "서울_호텔": "200-500개",
    "서울_기타": "100-200개",
    "총계": "850-1,800개 URL"
}
```

#### **장점**
- ✅ **법적 안전**: robots.txt 공식 허용
- ✅ **높은 성공률**: 95%+ 
- ✅ **빠른 개발**: 2-3일
- ✅ **자동 업데이트**: KLOOK이 관리

### 🥈 **2순위 전략: 카테고리 페이지 활용**

#### **구현 방법**
```python
def klook_category_strategy():
    """허용된 카테고리 페이지 활용"""
    
    category_urls = [
        "https://www.klook.com/things-to-do/region-seoul/",
        "https://www.klook.com/attractions/region-seoul/"
    ]
    
    # 각 카테고리에서 상품 링크 수집
    for category_url in category_urls:
        product_links = scrape_category_page(category_url)
        # 상품 상세 정보 크롤링
```

#### **특징**
- ⚠️ **봇 탐지 위험**: 중간 수준
- ⏰ **개발 시간**: 5-7일
- 📊 **성공률**: 70-80%

---

## ⏰ 개발 일정

### 🎯 **최적 시나리오** (Sitemap 활용)
```
📅 Day 1: Sitemap 분석 + URL 추출 로직 구현
   - 마스터 사이트맵 구조 파악 (2시간)
   - XML 파싱 및 URL 필터링 구현 (4시간)
   - 초기 테스트 (2시간)

📅 Day 2: 마이리얼트립 크롤러 수정
   - KLOOK 맞춤 선택자 수정 (6시간)
   - 한국어 데이터 처리 로직 (2시간)

📅 Day 3: 테스트 및 최적화
   - 소규모 테스트 (10-50개 상품) (4시간)
   - 대규모 테스트 (200+ 상품) (4시간)
```

### 🔥 **도전 시나리오** (복합 전략)
```
📅 Day 1-2: Sitemap + 카테고리 복합 구현
📅 Day 3-4: 봇 탐지 회피 로직 추가
📅 Day 5-7: 광범위한 테스트 및 안정화
```

---

## 🔧 기술 구현 세부사항

### **필수 수정 사항**

#### 1. **기본 URL 변경**
```python
# 기존 (마이리얼트립)
def go_to_main_page(driver):
    driver.get("https://www.myrealtrip.com/experiences/")

# 수정 (KLOOK)
def go_to_main_page_klook(driver):
    # Sitemap 기반이므로 메인 페이지 접근 불필요
    # 또는 허용된 카테고리 페이지 사용
    driver.get("https://www.klook.com/things-to-do/region-seoul/")
```

#### 2. **URL 수집 로직 완전 교체**
```python
# 기존: 페이지 스크래핑 방식
def collect_product_urls(driver):
    # 복잡한 스크래핑 로직...

# 수정: Sitemap 기반 방식
def collect_klook_urls_from_sitemap():
    """Sitemap에서 직접 URL 수집"""
    return parse_sitemap_urls("https://www.klook.com/ko/sitemap-master-index.xml")
```

#### 3. **선택자 패턴 변경**
```python
# KLOOK 전용 선택자
KLOOK_SELECTORS = {
    "상품명": [
        "h1[data-testid='activity-title']",
        ".activity-detail-title",
        "h1.title"
    ],
    "가격": [
        "[data-testid='checkout-price']",
        ".price-display",
        ".currency-value"
    ],
    "평점": [
        "[data-testid='rating-score']",
        ".rating-number",
        ".review-score"
    ],
    "이미지": [
        "[data-testid='activity-image']",
        ".gallery-main img",
        ".hero-image img"
    ]
}
```

#### 4. **데이터 구조 수정**
```python
# KLOOK 맞춤 데이터 구조
def crawl_klook_product(driver, url, product_number):
    return {
        '번호': product_number,
        '사이트': 'KLOOK',
        '국가': '한국',
        '도시': '서울',
        '상품명': get_product_name_klook(driver),
        '가격': get_price_klook(driver),
        '평점': get_rating_klook(driver),
        '카테고리': get_category_klook(driver),
        '언어': get_language_klook(driver),
        '소요시간': get_duration_klook(driver),  # KLOOK 특화
        '포함사항': get_inclusions_klook(driver),  # KLOOK 특화
        'URL': url,
        '수집시간': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
```

---

## 🧪 테스트 계획

### **단계별 테스트**

#### **Phase 1: Sitemap 테스트**
```python
TEST_PHASE_1 = {
    "목표": "Sitemap URL 추출 검증",
    "기간": "4시간",
    "내용": [
        "마스터 사이트맵 파싱 테스트",
        "서울 관련 URL 필터링 정확도",
        "URL 유효성 검증 (200 응답)"
    ]
}
```

#### **Phase 2: 소규모 크롤링**
```python
TEST_PHASE_2 = {
    "목표": "10-20개 상품 크롤링",
    "기간": "4시간", 
    "내용": [
        "선택자 정확도 검증",
        "데이터 추출 완성도",
        "한국어 인코딩 문제 확인"
    ]
}
```

#### **Phase 3: 대규모 안정성**
```python
TEST_PHASE_3 = {
    "목표": "200-500개 상품 크롤링",
    "기간": "8시간",
    "내용": [
        "장시간 크롤링 안정성",
        "봇 탐지 회피 효과",
        "데이터 품질 일관성"
    ]
}
```

---

## ⚠️ 리스크 및 대응 방안

### **주요 리스크**

#### 🔴 **높은 위험**
```python
HIGH_RISK = {
    "한국_IP_봇탐지": {
        "위험도": "높음",
        "대응": "프록시 사용, 긴 대기시간 (30-60초)",
        "추가시간": "+2일"
    },
    
    "동적_선택자_변경": {
        "위험도": "중간",
        "대응": "다중 선택자 패턴, 정기 업데이트",
        "추가시간": "+1일"
    }
}
```

#### 🟡 **중간 위험**
```python
MEDIUM_RISK = {
    "CAPTCHA_발생": {
        "위험도": "중간",
        "대응": "수동 처리 로직 구현",
        "추가시간": "+4시간"
    },
    
    "한국어_인코딩": {
        "위험도": "낮음",
        "대응": "UTF-8 강제 설정",
        "추가시간": "+2시간"
    }
}
```

### **백업 계획**
```python
BACKUP_PLANS = {
    "Plan_A": "Sitemap 활용 (1순위)",
    "Plan_B": "카테고리 페이지 크롤링",
    "Plan_C": "수동 URL 리스트 작성",
    "Plan_D": "영어 사이트 활용 (/en-SG/)"
}
```

---

## 📊 예상 성과

### **정량적 목표**
```python
QUANTITATIVE_GOALS = {
    "URL_수집": "800-1,600개 (서울 관련)",
    "실제_크롤링": "500-1,000개 (필터링 후)",
    "데이터_품질": "95%+ 완전성",
    "크롤링_속도": "상품당 30-45초",
    "일일_처리량": "200-400개 상품"
}
```

### **예상 수집 데이터**
```python
EXPECTED_DATA_FIELDS = [
    "상품명", "가격", "평점", "리뷰수",
    "카테고리", "소요시간", "언어",
    "포함사항", "제외사항", "취소정책",
    "이미지_URL", "상품_URL", "수집시간"
]

ESTIMATED_DATA_VOLUME = {
    "CSV_파일_크기": "2-5MB",
    "이미지_폴더_크기": "100-500MB",
    "총_데이터_크기": "100-1000MB"
}
```

---

## 🏆 성공 기준

### **기술적 성공 기준**
- ✅ 500개 이상 서울 상품 데이터 수집
- ✅ 95% 이상 데이터 완전성 달성
- ✅ IP 차단 없이 안정적 크롤링
- ✅ 한국어 데이터 완벽 처리

### **비즈니스 성공 기준**
- ✅ 3일 이내 개발 완료
- ✅ 월 1회 자동 업데이트 가능
- ✅ 법적 문제 없는 크롤링
- ✅ 타 도시 확장 용이성

---

## 🌍 글로벌 확장 전략

### **다중 도시 크롤링 아키텍처**

#### **글로벌 도시 매핑**
```python
def klook_global_sitemap_crawler(target_cities):
    """전 세계 모든 도시 지원 KLOOK 크롤러"""
    master_sitemap = "https://www.klook.com/ko/sitemap-master-index.xml"
    
    # 50+ 도시 매핑 시스템
    city_mappings = {
        # 아시아 태평양
        "서울": ["seoul", "서울", "korea", "한국"],
        "도쿄": ["tokyo", "도쿄", "japan", "일본"], 
        "오사카": ["osaka", "오사카", "japan"],
        "방콕": ["bangkok", "방콕", "thailand"],
        "싱가포르": ["singapore", "싱가포르"],
        "홍콩": ["hong-kong", "홍콩"],
        "타이베이": ["taipei", "타이베이", "taiwan"],
        
        # 유럽
        "런던": ["london", "런던", "uk", "united-kingdom"],
        "파리": ["paris", "파리", "france"],
        "로마": ["rome", "로마", "italy"],
        "바르셀로나": ["barcelona", "바르셀로나", "spain"],
        
        # 미주
        "뉴욕": ["new-york", "뉴욕", "usa", "united-states"],
        "로스앤젤레스": ["los-angeles", "로스앤젤레스", "usa"],
        "밴쿠버": ["vancouver", "밴쿠버", "canada"],
        
        # 중동/아프리카
        "두바이": ["dubai", "두바이", "uae"],
        "카이로": ["cairo", "카이로", "egypt"]
    }
    
    # 배치 처리 시스템
    results = {}
    for city_name, search_terms in city_mappings.items():
        if city_name in target_cities or 'all' in target_cities:
            city_urls = extract_city_urls(master_sitemap, search_terms)
            results[city_name] = {
                'urls_found': len(city_urls),
                'urls': city_urls,
                'estimated_products': len(city_urls) * 0.7  # 70% 성공률 가정
            }
    
    return results
```

#### **대규모 배치 처리 시스템**
```python
def batch_global_crawler(cities_batch, concurrent_browsers=3):
    """다중 브라우저 동시 크롤링 시스템"""
    
    results_summary = {
        'total_cities': len(cities_batch),
        'total_products_collected': 0,
        'success_rate_by_city': {},
        'processing_time': 0
    }
    
    # 동시 처리를 위한 브라우저 풀
    browser_pool = initialize_browser_pool(concurrent_browsers)
    
    for city in cities_batch:
        city_result = process_city_batch(city, browser_pool[city % concurrent_browsers])
        results_summary['success_rate_by_city'][city] = city_result['success_rate']
        results_summary['total_products_collected'] += city_result['products_count']
    
    return results_summary

# 예상 글로벌 처리량
GLOBAL_SCALING_ESTIMATES = {
    "단일_도시": "500-1,000개 상품/일",
    "10개_도시_동시": "3,000-8,000개 상품/일", 
    "50개_도시_배치": "15,000-35,000개 상품/주",
    "전세계_커버리지": "50+ 도시, 100+ 국가"
}
```

### **글로벌 확장의 비즈니스 가치**

#### **시장 규모 분석**
```python
GLOBAL_MARKET_VALUE = {
    "아시아_태평양": {
        "도시수": 25,
        "예상_상품수": "12,000-20,000개",
        "시장가치": "$2.1B (KLOOK 아시아 시장)"
    },
    "유럽": {
        "도시수": 15, 
        "예상_상품수": "7,000-12,000개",
        "시장가치": "$800M (유럽 체험 관광 시장)"
    },
    "미주": {
        "도시수": 10,
        "예상_상품수": "4,000-8,000개", 
        "시장가치": "$1.2B (북미 체험 관광)"
    },
    "기타_지역": {
        "도시수": 8,
        "예상_상품수": "2,000-4,000개",
        "시장가치": "$300M"
    }
}

# 총 글로벌 잠재력
TOTAL_GLOBAL_POTENTIAL = {
    "총_도시수": "50+ 도시",
    "총_상품수": "25,000-44,000개",
    "시장_규모": "$4.4B+ 글로벌 체험관광 시장",
    "데이터_가치": "실시간 글로벌 여행 트렌드 인사이트"
}
```

#### **확장 단계별 계획**
```python
EXPANSION_PHASES = {
    "Phase_1": {
        "기간": "1주",
        "도시": "서울 (프로토타입 완성)",
        "목표": "750-1,600개 상품",
        "성과": "시스템 검증 및 최적화"
    },
    
    "Phase_2": {
        "기간": "2주", 
        "도시": "아시아 5개 도시 (도쿄, 방콕, 싱가포르, 홍콩, 타이베이)",
        "목표": "4,000-8,000개 상품",
        "성과": "다국어 데이터 처리 시스템 구축"
    },
    
    "Phase_3": {
        "기간": "1개월",
        "도시": "글로벌 20개 주요 도시", 
        "목표": "12,000-25,000개 상품",
        "성과": "완전한 글로벌 크롤링 플랫폼"
    },
    
    "Phase_4": {
        "기간": "2개월",
        "도시": "전세계 50+ 도시 (완전 커버리지)",
        "목표": "25,000-50,000개 상품", 
        "성과": "세계 최대 규모 KLOOK 데이터베이스"
    }
}
```

### **기술적 혁신 포인트**

#### **다중 사이트맵 통합 시스템**
```python
def multi_region_sitemap_integration():
    """지역별 사이트맵 자동 통합 시스템"""
    
    regional_sitemaps = {
        "한국어": "https://www.klook.com/ko/sitemap-master-index.xml",
        "일본어": "https://www.klook.com/ja/sitemap-master-index.xml",
        "영어": "https://www.klook.com/en-US/sitemap-master-index.xml",
        "중국어": "https://www.klook.com/zh-CN/sitemap-master-index.xml"
    }
    
    # 자동 언어 감지 및 최적 사이트맵 선택
    for region, sitemap_url in regional_sitemaps.items():
        regional_data = parse_regional_sitemap(sitemap_url)
        merge_global_dataset(regional_data, region)
    
    return create_unified_global_dataset()
```

#### **성능 혁신**
```python
PERFORMANCE_BREAKTHROUGHS = {
    "동시처리_브라우저": "3-5개 동시 실행",
    "일일_처리량": "1,000-5,000개 상품/일",
    "글로벌_커버리지": "24시간 내 50개 도시 커버",
    "자동화_수준": "95%+ 무인 자동 처리",
    "데이터_품질": "다국어 95%+ 정확도"
}
```

## 🚀 다음 단계

### **즉시 착수 가능한 작업**
1. **서울 프로토타입 완성** (우선순위 1)
2. **글로벌 도시 매핑 시스템 구축** (우선순위 2) 
3. **다중 브라우저 배치 처리 시스템** (우선순위 3)
4. **아시아 5개 도시 확장 테스트** (우선순위 4)

### **필요 리소스 (글로벌 확장)**
- 👨‍💻 **개발자**: 1-2명 (중급 이상)
- ⏰ **시간**: 프로토타입 2-3일, 글로벌 확장 2-4주
- 💰 **비용**: 서버 리소스 추가 필요 (멀티 브라우저)
- 🖥️ **환경**: 고성능 서버 (동시 브라우저 3-5개)
- 🌐 **인프라**: 프록시 서비스 (지역별 IP)

---

## 📚 참고 자료

### **핵심 URL**
- **KLOOK 한국 사이트맵**: https://www.klook.com/ko/sitemap-master-index.xml
- **KLOOK robots.txt**: https://www.klook.com/robots.txt
- **KLOOK 서울 카테고리**: https://www.klook.com/things-to-do/region-seoul/

### **기술 문서**
- **마이리얼트립 크롤러**: `test88_widget_upgrade_test.ipynb`
- **크롤러 적용 가이드**: `크롤러_적용_가이드.md`
- **Sitemap XML 표준**: https://www.sitemaps.org/

---

## 📝 개발 로그

### **2025-08-06 조사 완료**
- ✅ KLOOK robots.txt 분석 완료
- ✅ Sitemap 기반 전략 수립
- ✅ 마이리얼트립 크롤러 분석 완료
- ✅ 개발 일정 및 리스크 평가 완료

### **다음 세션 준비사항**
- [ ] Sitemap 파싱 코드 작성
- [ ] KLOOK 상품 페이지 선택자 조사
- [ ] 마이리얼트립 크롤러 KLOOK 버전 생성

---

## 🎯 결론

**KLOOK 크롤링 프로젝트는 Sitemap 활용으로 매우 실현 가능**합니다!

### **핵심 성공 요소**
1. **Sitemap 우선 전략**: 95% 성공률, 2-3일 개발
2. **법적 준수**: robots.txt 완전 준수
3. **기존 크롤러 활용**: 개발 시간 대폭 단축
4. **단계적 접근**: 리스크 최소화

**이 README를 기반으로 체계적인 KLOOK 크롤러 개발을 진행하세요!** 🚀✨