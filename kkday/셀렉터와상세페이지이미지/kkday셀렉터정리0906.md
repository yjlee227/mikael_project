 1. 메인 페이지 검색창

  #search_experience_value
  input.form-control[placeholder*="가고 싶은 곳"]

  2. 검색 버튼

  #headerApp > div.container > div > div.header-search > div > div.kksearch-exp > div >
  div.input-group > span.input-group-btn > button
  button.btn.btn-primary

  3. 검색 결과 페이지 URL 패턴

  https://www.kkday.com/ko/product/productlist/{도시명}
  예시:
  - /ko/product/productlist/%EC%84%9C%EC%9A%B8 (서울)
  - /ko/product/productlist/%EC%98%A4%EC%82%AC%EC%B9%B4 (오사카)
  - /ko/product/productlist/%ED%8C%8C%EB%A6%AC (파리)

  🎯 우선순위 2: 상품 데이터 추출 (목록페이지)

  4. 상품 카드 컨테이너

  .product-list-main__product-card-2
  .product-card.gtm-prod-card-element

  5. 상품명

  .product-card h3
  .product-card__title

  6. 가격 정보

  .kk-price-local__normal
  .product-card .price-text
  .product-card .price

  7. 평점 및 리뷰수

  .product-card__info-score          /* 평점 */
  .product-card__info-number         /* 리뷰수 (200) */
  .product-score__count              /* 리뷰수 대안 */

  8. 상품 링크 (URL)

  .product-card a[href*="/ko/product/"]
  .product-card a

  🎯 우선순위 3: 이미지 수집

  9. 메인 상품 이미지

  .product-card .splide__slide img
  .pb-image-grid__img

  10. 썸네일 이미지

  .product-card img
  .package-image__img

  🎯 우선순위 4: 네비게이션

  11. 페이지네이션 (다음 페이지)

  .pagination .a-page a
  .pagination .fa-angle-right
  #productListApp > div > div > main > ul.pagination

  12. 팝업 닫기 버튼

  .close
  [data-dismiss="modal"]
  button[aria-hidden="true"]

  🎯 우선순위 5: 추가 상품 정보 (목록페이지)

  13. 할인율 / 예약수

  .product-rank                      /* 할인율 */
  .product-card__info-order-number   /* 예약수 */

  🎯 최우선: 상세페이지 데이터 (CSV 컬럼용)

  14. 기본 컨테이너

  #productDetailApp                  /* 최상위 컨테이너 */

  15. 상품명 (상세페이지)

  .product-title__name
  h1.product-title__name

  16. 카테고리/위치태그

  .product-location__text            /* 태국-푸켓, 프랑스-파리 */
  .breadcrumb li a                   /* breadcrumb 내 카테고리 */

  17. 하이라이트 (상품설명)

  #product-info-sec div p            /* 메인 설명문 */
  #product-info-sec ul li            /* 하이라이트 리스트 */
  .info-sec-collapsable div

  18. 특징

  .package-desc ul li                /* 옵션별 특징 */
  .critical-info-text                /* 주요 특징 */
  .kk-icon-with-text__text          /* 아이콘 포함 특징 */

  19. 언어

  .kk-icon-with-text__text           /* "한국어 가이드" */
  #ic_earth_line + .kk-icon-with-text__text  /* 언어 아이콘 다음 텍스트 */

  20. 투어형태

  .info-table td                     /* 정보 테이블의 "투어 유형" 행 */
  table.info-table tr:contains("투어 유형") td:last-child

  21. 미팅방식

  .kk-icon-with-text__text           /* "현장에서 전자바우처 제시" */
  #ic_deviceMobile_line + .kk-icon-with-text__text  /* 모바일 아이콘 다음 */

  22. 소요시간

  .critical-info span                /* "총 소요시간: 1 일" */
  #ic_clock_line + .kk-icon-with-text__text  /* 시계 아이콘 다음 */

  23. 평점 (상세페이지)

  .product-score span:first-child    /* 평점 숫자 */
  .product-score__count              /* 리뷰 개수 */

  24. 위치 안내

  .board-title h4                    /* 장소명 */
  .text-grey.break-word              /* 주소 */
  #map-sec                          /* 지도 섹션 */

  🎯 유연한 다중 셀렉터 전략

  # 각 데이터별 fallback 셀렉터 배열
  KKDAY_SELECTORS = {
      "상품명": [
          "#productDetailApp .product-title__name",
          "#productDetailApp h1.product-title__name",
          ".product-card h3",
          ".product-card__title"
      ],
      "가격": [
          "#productDetailApp .kk-price-local__normal",
          ".product-card .kk-price-local__normal",
          ".product-card .price-text"
      ],
      "소요시간": [
          ".critical-info span",
          "#ic_clock_line + .kk-icon-with-text__text",
          ".kk-icon-with-text__text:contains('시간')"
      ],
      "위치태그": [
          ".product-location__text",
          ".breadcrumb li a"
      ]
  }