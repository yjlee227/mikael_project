-- PostgreSQL 통합 크롤링 데이터베이스 스키마
-- 플랫폼별(KLOOK, KKDAY) 도시별 확장 가능한 구조

-- 1. 기본 메타데이터 테이블
CREATE TABLE platforms (
    platform_id SERIAL PRIMARY KEY,
    platform_name VARCHAR(20) UNIQUE NOT NULL, -- 'klook', 'kkday'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE regions (
    region_id SERIAL PRIMARY KEY,
    continent VARCHAR(20) NOT NULL,     -- 아시아
    country VARCHAR(50) NOT NULL,       -- 일본
    city_name VARCHAR(100) NOT NULL,    -- 삿포로, 도쿄
    city_code VARCHAR(10),               -- CTS, NRT
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(continent, country, city_name)
);

-- 2. 크롤링 수집 작업 관리
CREATE TABLE crawl_sessions (
    session_id SERIAL PRIMARY KEY,
    platform_id INTEGER REFERENCES platforms(platform_id),
    region_id INTEGER REFERENCES regions(region_id),
    tab_name VARCHAR(50),               -- 전체, 투어, 액티비티
    target_products INTEGER,
    max_pages INTEGER,
    session_status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. URL 수집 데이터 (JSON의 url_rank_mapping)
CREATE TABLE crawl_urls (
    url_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES crawl_sessions(session_id),
    rank_position INTEGER NOT NULL,
    product_url TEXT NOT NULL,
    page_number INTEGER,
    page_index INTEGER,
    is_duplicate BOOLEAN DEFAULT FALSE,
    collected_at TIMESTAMP,
    INDEX(session_id, rank_position),
    INDEX(product_url)
);

-- 4. 크롤링 단계별 상태 관리
CREATE TABLE crawl_stages (
    stage_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES crawl_sessions(session_id),
    stage_name VARCHAR(20) NOT NULL,    -- stage1, stage2
    stage_status VARCHAR(20) NOT NULL,  -- pending, success, failed
    stage_timestamp TIMESTAMP,
    url_count INTEGER,
    new_count INTEGER,
    file_path TEXT,
    error_message TEXT,
    INDEX(session_id, stage_name)
);

-- 5. 최종 상품 데이터 (CSV 통합 데이터)
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES crawl_sessions(session_id),
    platform_id INTEGER REFERENCES platforms(platform_id),
    region_id INTEGER REFERENCES regions(region_id),

    -- 상품 기본 정보
    platform_product_id VARCHAR(50),    -- 상품번호
    product_name TEXT NOT NULL,
    price VARCHAR(20),
    rating VARCHAR(10),
    review_count INTEGER,
    product_url TEXT,

    -- 위치 정보
    location_tag TEXT,
    category TEXT,
    classification TEXT,                 -- 분류

    -- 서비스 정보
    language_code TEXT,
    tour_type VARCHAR(100),
    meeting_type VARCHAR(100),
    duration TEXT,
    highlights TEXT,
    features TEXT,

    -- 메타데이터
    rank_position INTEGER,
    currency VARCHAR(10),
    collected_at TIMESTAMP,
    data_source VARCHAR(20),
    hash_value VARCHAR(32),

    -- 이미지 정보
    main_image VARCHAR(100),
    thumbnail_image VARCHAR(100),
    main_image_path TEXT,
    thumbnail_image_path TEXT,

    -- 제휴 링크
    affiliate_link TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX(platform_id, region_id),
    INDEX(platform_product_id),
    INDEX(collected_at)
);

-- 6. 기본 데이터 삽입
INSERT INTO platforms (platform_name) VALUES ('klook'), ('kkday');

INSERT INTO regions (continent, country, city_name, city_code) VALUES
('아시아', '일본', '삿포로', 'CTS'),
('아시아', '일본', '도쿄', 'NRT'),
('아시아', '일본', '오사카', 'KIX'),
('아시아', '한국', '서울', 'ICN');

-- 뷰: 크롤링 세션 요약
CREATE VIEW crawl_session_summary AS
SELECT
    cs.session_id,
    p.platform_name,
    CONCAT(r.city_name, '(', r.city_code, ')') as city,
    cs.tab_name,
    cs.target_products,
    cs.session_status,
    COUNT(cu.url_id) as collected_urls,
    COUNT(pr.product_id) as processed_products,
    cs.started_at,
    cs.completed_at
FROM crawl_sessions cs
LEFT JOIN platforms p ON cs.platform_id = p.platform_id
LEFT JOIN regions r ON cs.region_id = r.region_id
LEFT JOIN crawl_urls cu ON cs.session_id = cu.session_id
LEFT JOIN products pr ON cs.session_id = pr.session_id
GROUP BY cs.session_id, p.platform_name, r.city_name, r.city_code, cs.tab_name,
         cs.target_products, cs.session_status, cs.started_at, cs.completed_at;