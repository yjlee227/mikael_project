1. 검색창박스
<input id="search_experience_value" placeholder="가고 싶은 곳, 하고 싶은 것을 검색해보세요." type="text" aria-autocomplete="both" aria-haspopup="false" autocapitalize="off" autocomplete="off" autocorrect="off" spellcheck="false" maxlength="50" class="form-control">
#search_experience_value


2. 검색창박스 옆 검색 버튼(첫번째 누르고 2초 후에 한번 더 클릭해야 이동)
<svg viewBox="0 0 24 24" class="kk-icon kk-icon--md"><use href="#ic_search_line_semiblod"></use></svg>
#headerApp > div.container > div > div.header-search > div > div.kksearch-exp > div > div.input-group > span.input-group-btn > button > svg
<button class="btn btn-primary"><svg viewBox="0 0 24 24" class="kk-icon kk-icon--md"><use href="#ic_search_line_semiblod"></use></svg></button>
#headerApp > div.container > div > div.header-search > div > div.kksearch-exp > div > div.input-group > span.input-group-btn > button


3. 검색 결과 페이지 URL 패턴
https://www.kkday.com/ko/product/productlist/%EC%84%9C%EC%9A%B8
https://www.kkday.com/ko/product/productlist/%EC%98%A4%EC%82%AC%EC%B9%B4
https://www.kkday.com/ko/product/productlist/%EC%B9%98%EC%95%99%EB%A7%88%EC%9D%B4
https://www.kkday.com/ko/product/productlist/%ED%8C%8C%EB%A6%AC
https://www.kkday.com/ko/product/productlist/%EB%8F%84%EC%BF%84
https://www.kkday.com/ko/product/productlist/%EB%B0%A9%EC%BD%95


4. 상품 카드 컨테이너
 | 요소         | CSS 셀렉터                             | 설명         |
  |------------|-------------------------------------|------------|
  | 상품 카드 컨테이너 | .product-card.gtm-prod-card-element | 개별 상품 전체   |
  | 상품 제목      | .product-card__title                | 상품명        |
  | 상품 링크      | .product-card a                     | 상품 페이지 URL |
  | 현재 가격      | .kk-price-local__normal             | 판매 가격      |
  | 원가         | .kk-price-local__sale               | 할인 전 가격    |
  | 평점         | .product-card__info-score           | 평점 점수      |
  | 리뷰 수       | .product-card__info-number          | 리뷰 개수      |
  | 예약 수       | .product-card__info-order-number    | 예약 건수      |
  | 할인율        | .product-rank                       | 할인 퍼센트     |

#productListApp > div > div > main > div.product-list-main__product-card-2.layout-columns.layout-columns--gap-x-6.layout-columns--gap-y-8.layout-columns--horizontal-align-default.layout-columns--vertical-align-default.layout-columns--flow-direction-row.layout-u-pb-8

  KKday 완전한 CSS 셀렉터 계층 구조

  4-1. 전체 앱 컨테이너

  #productListApp

  4-2 메인 페이지 컨테이너

  #productListApp > div > div > main

  4-3. 상품 리스트 그리드 컨테이너 ⭐

  #productListApp > div > div > main > div.product-list-main__product-card-2.layout-columns.layout
  -columns--gap-x-6.layout-columns--gap-y-8.layout-columns--horizontal-align-default.layout-column
  s--vertical-align-default.layout-columns--flow-direction-row.layout-u-pb-8

  간단한 버전:
  .product-list-main__product-card-2

  4-4. 개별 상품 카드 (이 컨테이너의 직계 자식들)

  .product-list-main__product-card-2 > .product-card.gtm-prod-card-element

  웹 스크래핑에 최적화된 셀렉터

  # 방법 1: 전체 경로 사용
  container = driver.find_element(By.CSS_SELECTOR, "#productListApp > div > div > main >
  div.product-list-main__product-card-2")
  product_cards = container.find_elements(By.CSS_SELECTOR, ".product-card.gtm-prod-card-element")

  # 방법 2: 클래스명 사용 (더 간단하고 안정적)
  product_cards = driver.find_elements(By.CSS_SELECTOR, ".product-list-main__product-card-2
  .product-card.gtm-prod-card-element")

  # 방법 3: 가장 단순한 방법
  product_cards = driver.find_elements(By.CSS_SELECTOR, ".product-card.gtm-prod-card-element")

  레이아웃 정보

  - 그리드 컬럼: 3열 (--layout-columns-column-count: 3)
  - 간격: X축 6, Y축 8 (gap-x-6, gap-y-8)
  - 정렬: 기본 정렬 (horizontal-align-default, vertical-align-default)
  - 방향: 행 방향 (flow-direction-row)  

        ● KKday 상품 목록 페이지 - 수집된 CSS 셀렉터

        1. 전체 상품 컨테이너

        .product-list-main__product-card-2.layout-columns

        2. 개별 상품 카드 (상품 카드 컨테이너)

        .product-card.gtm-prod-card-element

        3. 상품 링크

        .product-card a[href*="/ko/product/"]

        4. 상품명

        .product-card h3

        5. 상품 이미지

        .product-card .splide__slide img

        6. 평점 수 (리뷰 개수)

        .product-card__info-number
        - 추출 예시: (200) → 200개 리뷰

        7. 가격

        .product-card .price-text
        .product-card .price

        실제 HTML 구조 예시

        <div class="product-list-main__product-card-2 layout-columns">
            <div class="product-card gtm-prod-card-element">
            <a href="/ko/product/3328-la-vallee-village-outlet...">
                <img src="https://image.kkday.com/.../jpg">
                <h3>파리 라 발레 빌리지 아울렛 왕복 교통편</h3>
                <span class="product-card__info-number">(200)</span>
                <span class="price">₩ 31,164</span>
            </a>
            </div>
        </div>


 5. 상품명 추출




  11. 페이지네이션 (다음 페이지)
<ul data-v-3754f6ef="" data-v-73aabd94="" class="pagination"><!----> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">1</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">2</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">3</a></li><li data-v-3754f6ef="" class="a-page active"><a data-v-3754f6ef="">4</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">5</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">6</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">7</a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-right"></i></a></li></ul>
#productListApp > div > div > main > ul

<ul data-v-3754f6ef="" data-v-73aabd94="" class="pagination"><!----> <li data-v-3754f6ef="" class="a-page active"><a data-v-3754f6ef="">1</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">2</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">3</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">4</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">5</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">6</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">7</a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-right"></i></a></li></ul>
#productListApp > div > div > main > ul

<ul data-v-3754f6ef="" data-v-73aabd94="" class="pagination"><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-left"></i></a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">4</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">5</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">6</a></li><li data-v-3754f6ef="" class="a-page active"><a data-v-3754f6ef="">7</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">8</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">9</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">10</a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-right"></i></a></li></ul>
#productListApp > div > div > main > ul

<ul data-v-3754f6ef="" data-v-73aabd94="" class="pagination"><!----> <li data-v-3754f6ef="" class="a-page active"><a data-v-3754f6ef="">1</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">2</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">3</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">4</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">5</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">6</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">7</a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-right"></i></a></li></ul>
#productListApp > div > div > main > ul

<ul data-v-3754f6ef="" data-v-73aabd94="" class="pagination"><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-left"></i></a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">4</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">5</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">6</a></li><li data-v-3754f6ef="" class="a-page active"><a data-v-3754f6ef="">7</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">8</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">9</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">10</a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-right"></i></a></li></ul>
#productListApp > div > div > main > ul

<ul data-v-3754f6ef="" data-v-73aabd94="" class="pagination"><!----> <li data-v-3754f6ef="" class="a-page active"><a data-v-3754f6ef="">1</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">2</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">3</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">4</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">5</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">6</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">7</a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-right"></i></a></li></ul>
#productListApp > div > div > main > ul

<ul data-v-3754f6ef="" data-v-73aabd94="" class="pagination"><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-left"></i></a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">4</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">5</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">6</a></li><li data-v-3754f6ef="" class="a-page active"><a data-v-3754f6ef="">7</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">8</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">9</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">10</a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-right"></i></a></li></ul>
#productListApp > div > div > main > ul

<ul data-v-3754f6ef="" data-v-73aabd94="" class="pagination"><!----> <li data-v-3754f6ef="" class="a-page active"><a data-v-3754f6ef="">1</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">2</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">3</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">4</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">5</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">6</a></li><li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef="">7</a></li> <li data-v-3754f6ef="" class="a-page"><a data-v-3754f6ef=""><i data-v-3754f6ef="" class="fa fa-angle-right"></i></a></li></ul>
#productListApp > div > div > main > ul