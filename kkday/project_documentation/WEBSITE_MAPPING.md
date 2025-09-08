# KKday 크롤링 시스템 - 웹사이트 구조 매핑 및 셀렉터 가이드

## 🌐 개요

이 문서는 Klook에서 KKday로 시스템 전환을 위한 웹사이트 구조 분석 및 CSS 셀렉터 매핑 가이드입니다. 실제 KKday 웹사이트 구조를 분석하여 정확한 셀렉터를 제공합니다.

## 🎯 핵심 목표

### 웹사이트 전환 요구사항
- **플랫폼**: Klook (www.klook.com) → KKday (www.kkday.com)
- **언어**: 한국어 기준 페이지 분석
- **타겟 데이터**: 상품명, 가격, 평점, 리뷰수, 이미지, URL
- **페이지 유형**: 검색 결과, 상품 상세, 카테고리 페이지

## 🗺️ 사이트 구조 비교 분석

### Klook vs KKday 기본 구조

#### URL 패턴 비교
```yaml
# Klook URL 구조
메인: https://www.klook.com/
검색: https://www.klook.com/city/{city_id}-activity/?q={keyword}
상품: https://www.klook.com/activity/{product_id}-{product_name}/
카테고리: https://www.klook.com/city/{city_id}-{category}/

# KKday URL 구조  
메인: https://www.kkday.com/
검색: https://www.kkday.com/ko/search?keyword={keyword}&city={city_name}
상품: https://www.kkday.com/ko/product/{product_id}
카테고리: https://www.kkday.com/ko/{country}/{city}/{category}
```

#### 페이지 레이아웃 구조
```html
<!-- Klook 페이지 구조 -->
<div class="search-results">
  <div class="activity-card">
    <img class="activity-image"/>
    <div class="activity-info">
      <h3 class="activity-title"/>
      <div class="activity-price"/>
      <div class="activity-rating"/>
    </div>
  </div>
</div>

<!-- KKday 페이지 구조 (예상) -->
<div class="product-list">
  <div class="product-card">
    <img class="product-image"/>
    <div class="product-details">
      <h4 class="product-name"/>
      <div class="price-info"/>
      <div class="rating-section"/>
    </div>
  </div>
</div>
```

## 🎯 CSS 셀렉터 매핑표

### 1. 기본 네비게이션 셀렉터

#### 검색창 및 버튼
```css
/* Klook 셀렉터 (기존) */
.search-input: "#search-input"
.search-button: "button[type='submit']"

/* KKday 셀렉터 (수집 필요) ⚠️ */
.search-input: "[data-testid='search-input']"
.search-button: "[data-testid='search-submit']"
.search-container: ".search-form-container"
```

#### 페이지네이션
```css
/* Klook 셀렉터 (기존) */
.pagination-next: ".pagination-next"
.pagination-prev: ".pagination-prev"

/* KKday 셀렉터 (수집 필요) ⚠️ */
.pagination-container: ".pagination-wrapper"
.next-page: "[aria-label='다음 페이지']"
.prev-page: "[aria-label='이전 페이지']"
```

### 2. 상품 목록 페이지 셀렉터

#### 상품 카드 컨테이너
```css
/* Klook 셀렉터 (기존) */
.product-container: ".activity-card"
.product-list: ".search-results .activity-list"

/* KKday 셀렉터 (수집 필요) ⚠️ */
.product-container: ".product-card, .tour-card"
.product-list: ".product-list-container .grid-container"
.product-item: "[data-product-id]"
```

#### 상품 링크 추출
```css
/* Klook 셀렉터 (기존) */
.product-link: ".activity-card a[href*='/activity/']"

/* KKday 셀렉터 (수집 필요) ⚠️ */
.product-link: "a[href*='/product/'], a[href*='/tour/']"
.product-url: ".product-card-link"
```

### 3. 상품 데이터 추출 셀렉터

#### 상품명 (최우선순위)
```css
/* Klook 셀렉터 (기존) */
.product-title: ".activity-title, .activity-name h3"

/* KKday 셀렉터 (수집 필요) ⚠️ */
.product-name: ".product-title, .tour-name, h1.product-header"
.product-subtitle: ".product-subtitle, .tour-subtitle"

# 백업 셀렉터 (다중 선택 전략)
.title-selectors: [
    "h1[class*='product']",
    "h2[class*='product']", 
    "[data-testid*='title']",
    ".product-card-title"
]
```

#### 가격 정보 (최우선순위)
```css
/* Klook 셀렉터 (기존) */  
.price: ".activity-price, .price-display"
.original-price: ".price-original"
.discount-price: ".price-discount"

/* KKday 셀렉터 (수집 필요) ⚠️ */
.price-container: ".price-section, .pricing-info"
.current-price: ".current-price, .sale-price"
.original-price: ".original-price, .regular-price"

# 백업 셀렉터 (통화 기호 기반)
.price-selectors: [
    "[class*='price']:contains('₩')",
    "[class*='cost']:contains('원')",
    ".pricing [class*='amount']"
]
```

#### 평점 및 리뷰 (우선순위 2)
```css
/* Klook 셀렉터 (기존) */
.rating: ".activity-rating, .rating-score"
.review-count: ".review-count, .reviews-total"

/* KKday 셀렉터 (수집 필요) ⚠️ */
.rating-container: ".rating-section, .review-summary"
.rating-score: ".rating-value, .score-display"
.rating-stars: ".star-rating, .rating-stars"
.review-count: ".review-count, .reviews-number"

# 별점 이미지 기반 셀렉터
.star-selectors: [
    ".star-rating [class*='star']",
    "[data-rating]",
    ".rating-display .score"
]
```

### 4. 이미지 추출 셀렉터

#### 메인 상품 이미지
```css
/* Klook 셀렉터 (기존) */
.main-image: "#banner_atlas .activity-banner-image-container_left img"
.backup-image: ".activity-banner-image-container_left img"

/* KKday 셀렉터 (수집 필요) ⚠️ */
.hero-image: ".product-hero-image img, .main-gallery img:first-child"
.banner-image: ".product-banner img, .hero-banner img"
.thumbnail-image: ".product-thumbnail img"

# 이미지 소스 추출 전략
.image-selectors: [
    "img[class*='product'][class*='main']",
    "img[class*='hero']",
    ".gallery-main img",
    ".product-image-container img:first-child"
]
```

#### 썸네일 이미지
```css
/* Klook 셀렉터 (기존) */
.card-image: ".activity-card img"
.list-thumbnail: ".activity-image-container img"

/* KKday 셀렉터 (수집 필요) ⚠️ */
.card-thumbnail: ".product-card img, .tour-card img"
.list-image: ".product-list-item img"

# 카드 이미지 백업 전략  
.thumbnail-selectors: [
    ".product-card .image-container img",
    ".card-media img",
    "[class*='thumbnail'] img"
]
```

### 5. 카테고리 및 태그 셀렉터

#### 상품 카테고리
```css
/* Klook 셀렉터 (기존) */
.category: ".activity-category, .category-tag"
.tags: ".activity-tags .tag"

/* KKday 셀렉터 (수집 필요) ⚠️ */
.product-category: ".category-label, .product-type"
.category-tags: ".tag-list .tag-item"
.breadcrumb: ".breadcrumb-container .breadcrumb-item"
```

## 🔍 실제 셀렉터 수집 가이드

### 우선순위 1: 필수 기능 셀렉터 (즉시 필요)

#### Chrome DevTools 활용법
```javascript
// 브라우저 콘솔에서 실행할 셀렉터 테스트 코드
console.log("=== KKday 셀렉터 수집 시작 ===");

// 1. 검색창 찾기
document.querySelectorAll('input[type="text"]').forEach((el, i) => {
  console.log(`검색창 ${i}:`, el.className, el.id, el.getAttribute('data-testid'));
});

// 2. 상품 카드 찾기  
document.querySelectorAll('[class*="product"], [class*="tour"], [class*="card"]').forEach((el, i) => {
  if (el.innerHTML.includes('₩') || el.innerHTML.includes('원')) {
    console.log(`상품카드 ${i}:`, el.className);
  }
});

// 3. 가격 정보 찾기
document.querySelectorAll('[class*="price"], [class*="cost"]').forEach((el, i) => {
  console.log(`가격 ${i}:`, el.className, el.textContent.trim());
});

// 4. 상품명 찾기  
document.querySelectorAll('h1, h2, h3, h4').forEach((el, i) => {
  if (el.closest('[class*="product"]') || el.closest('[class*="tour"]')) {
    console.log(`제목 ${i}:`, el.tagName, el.className, el.textContent.slice(0, 30));
  }
});
```

### 셀렉터 검증 체크리스트

#### 기본 검증 항목
```python
def validate_kkday_selectors():
    """KKday 셀렉터 검증 함수"""
    
    validation_checklist = {
        "search_functionality": [
            "검색창 셀렉터가 정확한가?",
            "검색 버튼이 클릭 가능한가?",
            "검색 결과가 올바르게 로드되는가?"
        ],
        
        "product_extraction": [
            "상품 카드를 모두 찾을 수 있는가?",
            "상품명이 정확히 추출되는가?",
            "가격 정보가 완전히 수집되는가?",
            "이미지 URL이 유효한가?"
        ],
        
        "navigation": [
            "다음 페이지로 이동이 가능한가?",
            "페이지네이션이 정상 작동하는가?",
            "URL 수집이 완전한가?"
        ]
    }
    
    return validation_checklist
```

## 🛡️ 안티봇 대응 전략

### KKday 웹사이트 특성 분석

#### 봇 탐지 메커니즘
```yaml
예상_봇_탐지_방법:
  - CloudFlare 보안 검사
  - reCAPTCHA 인증
  - 요청 빈도 제한
  - User-Agent 검증
  - JavaScript 실행 확인

대응_전략:
  - undetected-chromedriver 사용
  - 랜덤 대기 시간 (2-5초)
  - User-Agent 로테이션
  - 세션 유지 및 쿠키 관리
  - 프록시 사용 (필요시)
```

#### 자연스러운 크롤링 패턴
```python
# 인간 친화적 크롤링 설정
CRAWLING_BEHAVIOR = {
    "page_load_wait": (3, 7),      # 3-7초 대기
    "scroll_behavior": True,        # 스크롤 시뮬레이션
    "mouse_movement": True,         # 마우스 움직임 추가
    "random_clicks": 0.1,          # 10% 확률로 랜덤 클릭
    "session_duration": (30, 60),  # 30-60분 세션
}
```

## 🔄 동적 셀렉터 관리

### 셀렉터 변경 대응 시스템

#### 다중 백업 셀렉터 전략
```python
class KKdaySelectors:
    """KKday 동적 셀렉터 관리 클래스"""
    
    def __init__(self):
        self.selectors = {
            "product_name": [
                ".product-title",           # 주요 셀렉터
                "h1[class*='product']",     # 백업 1
                "[data-testid*='title']",   # 백업 2
                "h2.title, h3.title"       # 백업 3
            ],
            
            "product_price": [
                ".current-price",
                "[class*='price']:contains('₩')",
                ".pricing .amount",
                "[data-testid*='price']"
            ],
            
            "product_image": [
                ".product-hero-image img",
                ".main-gallery img:first-child",
                "img[class*='hero']",
                ".image-container img:first-child"
            ]
        }
    
    def get_element_with_fallback(self, driver, selector_key):
        """백업 셀렉터를 활용한 안전한 요소 찾기"""
        selectors = self.selectors.get(selector_key, [])
        
        for selector in selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.is_displayed():
                    print(f"✅ 성공: {selector_key} - {selector}")
                    return element
            except NoSuchElementException:
                continue
                
        print(f"❌ 실패: {selector_key} - 모든 셀렉터 실패")
        return None
```

### 셀렉터 자동 업데이트 시스템

#### 기계학습 기반 셀렉터 추천
```python
def analyze_page_structure(driver):
    """페이지 구조 분석 및 셀렉터 추천"""
    
    # JavaScript로 페이지 요소 분석
    analysis_script = """
    const elements = document.querySelectorAll('*');
    const classNames = [];
    
    elements.forEach(el => {
        if (el.className && typeof el.className === 'string') {
            classNames.push(el.className);
        }
    });
    
    // 상품 관련 클래스명 필터링
    const productClasses = classNames.filter(cls => 
        cls.includes('product') || 
        cls.includes('tour') ||
        cls.includes('card') ||
        cls.includes('item')
    );
    
    return [...new Set(productClasses)].slice(0, 20);
    """
    
    potential_selectors = driver.execute_script(analysis_script)
    return potential_selectors
```

## 📊 성능 최적화 전략

### 셀렉터 성능 최적화

#### 효율적인 셀렉터 설계 원칙
```css
/* 권장: ID 기반 (가장 빠름) */
#product-12345

/* 권장: 클래스 + 속성 조합 */  
.product-card[data-product-id]

/* 주의: 너무 구체적인 경로 (느림) */
html > body > div > section > div > div > .product-card

/* 주의: 와일드카드 과용 (매우 느림) */
*[class*="product"] *[class*="title"] *
```

#### 셀렉터 성능 측정
```python
import time

def measure_selector_performance(driver, selectors):
    """셀렉터 성능 벤치마크"""
    
    results = {}
    
    for name, selector in selectors.items():
        start_time = time.time()
        
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            end_time = time.time()
            
            results[name] = {
                'selector': selector,
                'time': round(end_time - start_time, 4),
                'count': len(elements),
                'status': 'success'
            }
        except Exception as e:
            results[name] = {
                'selector': selector,
                'time': 0,
                'count': 0,
                'status': f'error: {e}'
            }
    
    return results
```

## 🎯 실제 구현을 위한 액션 아이템

### 즉시 수행할 작업 (Phase 1)

#### 1. KKday 웹사이트 수동 분석
```markdown
📋 할일 목록:
- [ ] KKday 메인 페이지 접속 및 구조 파악
- [ ] 서울 여행상품 검색 결과 페이지 분석  
- [ ] 상품 상세 페이지 1-2개 심층 분석
- [ ] Chrome DevTools로 핵심 셀렉터 5개 수집
- [ ] 실제 셀렉터 동작 테스트 (console에서)
```

#### 2. 셀렉터 코드 적용
```python  
# file_handler.py에서 업데이트할 셀렉터들
PRIORITY_UPDATES = {
    'main_selectors': [
        # 🚨 실제 KKday 사이트 분석 후 교체 필요
        ".product-hero-image img",
        ".main-gallery img:first-child", 
        "img[class*='hero']"
    ],
    
    'thumbnail_selectors': [
        # 🚨 실제 KKday 사이트 분석 후 교체 필요
        ".product-card img",
        ".tour-card img",
        ".card-media img"
    ]
}
```

### 중기 구현 계획 (Phase 2)

#### 셀렉터 관리 시스템 구축
- [ ] 동적 셀렉터 관리 클래스 개발
- [ ] 백업 셀렉터 시스템 구현
- [ ] 셀렉터 성능 모니터링 도구
- [ ] 자동 업데이트 메커니즘

## ⚠️ 주의사항 및 제한사항

### 기술적 제약사항
- **웹사이트 의존성**: KKday 사이트 구조 변경 시 즉시 영향
- **동적 콘텐츠**: JavaScript 렌더링 필수 (Selenium 필요)
- **지역화**: 한국어 페이지 기준, 다른 언어 지원 시 추가 분석 필요

### 윤리적/법적 고려사항
- **이용약관 준수**: KKday ToS 및 robots.txt 확인
- **요청 빈도**: 서버 부하 최소화 (2-5초 간격)
- **데이터 사용**: 개인 연구/분석 목적만 허용

---

**⚠️ 중요 알림**: 이 문서의 KKday 셀렉터는 **예상값**입니다. 실제 구현 전에 반드시 KKday 웹사이트를 직접 분석하여 정확한 셀렉터를 수집해야 합니다.

**다음 단계**: 실제 KKday 웹사이트 분석 및 셀렉터 수집 작업 수행

---

**문서 버전**: v1.0  
**최종 업데이트**: 2024-12-07  
**담당자**: 개발팀  
**상태**: 셀렉터 수집 대기중