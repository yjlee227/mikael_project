# KKday 셀렉터 수집 전략 및 진행 상황

## 🎯 **수집 전략**

### **컨테이너 기반 셀렉터 수집 방식 채택**

#### **선택 이유**
- **데이터 정확성**: 올바른 상품 데이터만 추출
- **성능 최적화**: 전체 DOM 검색 대신 범위 제한
- **안정성**: 웹사이트 구조 변경에 상대적으로 안정적
- **확장성**: 새로운 데이터 필드 추가 용이

#### **수집 방식**
```python
# 1. 컨테이너 먼저 찾기
product_cards = driver.find_elements(By.CSS_SELECTOR, ".product-card.gtm-prod-card-element")

# 2. 각 컨테이너 내부에서 데이터 추출
for card in product_cards:
    title = card.find_element(By.CSS_SELECTOR, "h3")
    price = card.find_element(By.CSS_SELECTOR, ".price")
    image = card.find_element(By.CSS_SELECTOR, "img")
```

## 📊 **CSV 데이터 구조**

### **통합형 CSV 파일** (상세페이지 우선 + 백업 셀렉터)
```csv
page_type,element_type,selector_name,css_selector,priority,backup_selector,description,test_status
```

#### **필드 설명**
- **page_type**: `list` (목록페이지) / `detail` (상세페이지)
- **element_type**: `container`, `text`, `image`, `button`, `navigation` 등
- **selector_name**: 셀렉터 식별명
- **css_selector**: 메인 CSS 셀렉터 (상세페이지 우선)
- **priority**: 1(필수), 2(중요), 3(선택)
- **backup_selector**: 백업 셀렉터 (주로 목록페이지)
- **description**: 셀렉터 설명
- **test_status**: `verified`, `pending`, `failed`

## 🔍 **수집 현황**

### ✅ **완료된 수집**

#### **목록페이지 - 상품 카드 컨테이너**
| 요소 | 셀렉터 | 상태 |
|------|--------|------|
| 전체 상품 컨테이너 | `.product-list-main__product-card-2.layout-columns` | ✅ |
| 개별 상품 카드 | `.product-card.gtm-prod-card-element` | ✅ |
| 상품명 | `.product-card h3` | ✅ |
| 상품 이미지 | `.product-card .splide__slide img` | ✅ |
| 평점/리뷰 수 | `.product-card__info-number` | ✅ |
| 가격 | `.product-card .price` | ✅ |
| 상품 링크 | `.product-card a[href*="/ko/product/"]` | ✅ |

### ⏳ **수집 예정**

#### **목록페이지 - 추가 요소들**
- **페이지네이션**: 이전/다음 버튼, 페이지 번호
- **검색 기능**: 검색창, 검색 버튼, 자동완성
- **필터링**: 가격/카테고리/지역/평점 필터
- **정렬 옵션**: 인기순/가격순/평점순 등
- **로딩 요소**: 스피너, 무한스크롤, 더보기 버튼

#### **상세페이지 - 전체 섹션**
- **Hero 섹션**: 메인 갤러리, 전체 제목, 최종 가격
- **예약 섹션**: 날짜 선택, 인원수, 옵션, 예약 버튼
- **상품 정보**: 설명, 포함사항, 주의사항
- **위치 정보**: 지도, 주소
- **리뷰 섹션**: 전체 평점, 개별 리뷰
- **관련 상품**: 추천 상품 목록

## 🛠️ **수집 도구 및 방법**

### **수집 방법**
1. **Chrome DevTools**: 수동 셀렉터 확인
2. **JavaScript Console**: 셀렉터 테스트
3. **Python Selenium**: 자동 검증
4. **스크린샷**: 시각적 확인

### **검증 스크립트**
```javascript
// Chrome 콘솔에서 실행
console.log("=== KKday 컨테이너 셀렉터 테스트 ===");

// 1. 상품 카드 컨테이너 찾기
const cards = document.querySelectorAll('.product-card.gtm-prod-card-element');
console.log(`상품 카드 개수: ${cards.length}`);

// 2. 각 카드 내부 요소 확인
cards.forEach((card, i) => {
    const title = card.querySelector('h3')?.textContent;
    const price = card.querySelector('.price')?.textContent;
    const image = card.querySelector('img')?.src;
    console.log(`카드 ${i}: ${title?.slice(0,20)}... | ${price} | 이미지: ${image ? 'O' : 'X'}`);
});
```

## 📋 **다음 단계**

### **단계 1**: 목록페이지 추가 셀렉터 수집
- 페이지네이션, 검색, 필터 요소들

### **단계 2**: 상세페이지 컨테이너 구조 분석
- Hero, 예약, 정보, 리뷰 섹션별 컨테이너 식별

### **단계 3**: CSV 파일 생성 및 데이터 정리
- 통합 CSV 파일에 모든 셀렉터 정리

### **단계 4**: 코드 적용 및 테스트
- 기존 Klook 코드를 KKday 셀렉터로 전환

---

**문서 버전**: v1.0  
**최종 업데이트**: 2024-12-07  
**수집 방식**: 컨테이너 기반  
**상태**: 목록페이지 기본 셀렉터 수집 완료