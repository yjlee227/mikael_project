"""
🗄️ 통합 여행상품 데이터베이스 시스템
- 문서 기반 통합 스키마 SQLite 구현
- KLOOK → 통합 스키마 변환 함수
- 다중 플랫폼 확장 준비

작성일: 2024-08-24
기반: 여행상품 비교·추천 시스템 문서
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import re

class UnifiedTravelDatabase:
    """통합 여행상품 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = "unified_travel_products.db"):
        """
        통합 데이터베이스 초기화
        
        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """데이터베이스 및 테이블 초기화"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # dict-like access
            
            # 메인 products 테이블 생성 (문서 기반)
            self._create_products_table()
            
            # 감사 로그 테이블 생성
            self._create_audit_table()
            
            # 인덱스 생성
            self._create_indexes()
            
            print(f"✅ 통합 데이터베이스 초기화 완료: {self.db_path}")
            
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 실패: {e}")
            raise
    
    def _create_products_table(self):
        """메인 상품 테이블 생성 (문서 스키마 기반)"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS products (
            -- ⭐ 필수 식별 정보
            provider TEXT NOT NULL,
            provider_product_id TEXT NOT NULL,
            fetch_ts TEXT NOT NULL,        -- ISO8601 UTC
            fx_rate NUMERIC,               -- 환율 스냅샷
            
            -- ⭐ 필수 목적지/분류
            destination_city TEXT NOT NULL,
            country TEXT NOT NULL,
            theme_tags TEXT,               -- JSON array
            
            -- ⭐ 필수 상품 정보
            title TEXT NOT NULL,
            subtitle TEXT,
            supplier_name TEXT,
            duration_hours REAL,
            pickup INTEGER DEFAULT 0,     -- boolean (0/1)
            language TEXT,                -- JSON array
            
            -- 포함/불포함
            included TEXT,                -- JSON array
            excluded TEXT,                -- JSON array  
            meeting_point TEXT,
            
            -- ⭐ 필수 가격 정보
            price_value NUMERIC NOT NULL,
            price_currency TEXT NOT NULL,
            option_list TEXT,             -- JSON array of options
            price_basis TEXT DEFAULT 'adult',  -- adult|child|group|option_min
            
            -- 평점/리뷰
            rating_value REAL,            -- 0~5 정규화
            rating_count INTEGER DEFAULT 0,
            
            -- 취소/환불 정책
            cancel_policy TEXT,           -- JSON object
            
            -- 가용성
            availability_calendar TEXT,   -- JSON array
            
            -- 노출/순위
            rank_position INTEGER,
            
            -- ⭐ 필수 링크/이미지
            landing_url TEXT NOT NULL,
            affiliate_url TEXT,
            images TEXT,                  -- JSON array
            
            -- 메타데이터
            product_hash TEXT,            -- SHA1 hash for deduplication
            data_source_meta TEXT,        -- JSON metadata
            
            -- 생성/수정 시간 (자동)
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            PRIMARY KEY (provider, provider_product_id)
        );
        """
        
        self.conn.execute(create_table_sql)
        self.conn.commit()
        print("✅ products 테이블 생성 완료")
    
    def _create_audit_table(self):
        """수집 감사 로그 테이블 생성"""
        create_audit_sql = """
        CREATE TABLE IF NOT EXISTS collection_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetch_session_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            search_query TEXT,
            sort_option TEXT,
            destination_norm TEXT,
            date_scope TEXT,
            user_agent TEXT,
            region TEXT,
            fetch_ts TEXT NOT NULL,
            products_count INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 1.0,
            error_log TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        self.conn.execute(create_audit_sql)
        self.conn.commit()
        print("✅ collection_audit 테이블 생성 완료")
    
    def _create_indexes(self):
        """성능 최적화 인덱스 생성"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_provider_city ON products(provider, destination_city);",
            "CREATE INDEX IF NOT EXISTS idx_fetch_ts ON products(fetch_ts);",
            "CREATE INDEX IF NOT EXISTS idx_price_currency ON products(price_currency, price_value);",
            "CREATE INDEX IF NOT EXISTS idx_rating ON products(rating_value, rating_count);",
            "CREATE INDEX IF NOT EXISTS idx_rank_position ON products(rank_position);",
            "CREATE INDEX IF NOT EXISTS idx_product_hash ON products(product_hash);"
        ]
        
        for index_sql in indexes:
            self.conn.execute(index_sql)
        
        self.conn.commit()
        print("✅ 성능 인덱스 생성 완료")


class KlookToUnifiedConverter:
    """KLOOK 32컬럼 데이터를 통합 스키마로 변환하는 클래스"""
    
    @staticmethod
    def extract_product_id_from_url(url: str) -> str:
        """KLOOK URL에서 상품 ID 추출"""
        try:
            # KLOOK URL 패턴: https://www.klook.com/activity/3880363-xxx
            match = re.search(r'/activity/(\d+)', url)
            if match:
                return match.group(1)
            
            # 다른 패턴이 있다면 추가
            match = re.search(r'id=(\d+)', url)
            if match:
                return match.group(1)
                
            # URL 자체를 ID로 사용
            return hashlib.md5(url.encode()).hexdigest()[:12]
            
        except Exception:
            return hashlib.md5(str(url).encode()).hexdigest()[:12]
    
    @staticmethod
    def normalize_rating(rating_str: str) -> Optional[float]:
        """평점을 0~5 스케일로 정규화"""
        if not rating_str:
            return None
        
        try:
            rating = float(str(rating_str).replace(',', ''))
            
            # 이미 0~5 스케일인 경우
            if 0 <= rating <= 5:
                return round(rating, 2)
            
            # 10점 스케일인 경우
            if 5 < rating <= 10:
                return round(rating / 2, 2)
            
            # 100점 스케일인 경우  
            if 10 < rating <= 100:
                return round(rating / 20, 2)
            
            return None
            
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def convert_to_iso4217(currency_str: str) -> str:
        """통화를 ISO4217 코드로 변환"""
        currency_map = {
            "원": "KRW",
            "달러": "USD", 
            "$": "USD",
            "엔": "JPY",
            "¥": "JPY",
            "유로": "EUR",
            "€": "EUR",
            "파운드": "GBP",
            "£": "GBP"
        }
        
        currency_str = str(currency_str).strip()
        return currency_map.get(currency_str, currency_str.upper())
    
    @staticmethod
    def extract_themes_from_title(title: str) -> List[str]:
        """상품명에서 테마 태그 추출"""
        if not title:
            return []
        
        theme_keywords = {
            "디즈니": ["disney", "theme_park"],
            "유니버설": ["universal", "theme_park"],
            "템플": ["temple", "culture"],
            "궁전": ["palace", "culture"],
            "투어": ["tour"],
            "크루즈": ["cruise"],
            "맛집": ["food", "dining"],
            "쇼핑": ["shopping"],
            "스파": ["spa", "wellness"],
            "골프": ["golf", "sports"],
            "다이빙": ["diving", "water_sports"],
            "서핑": ["surfing", "water_sports"],
            "트레킹": ["trekking", "adventure"],
            "하이킹": ["hiking", "adventure"]
        }
        
        themes = set()
        title_lower = title.lower()
        
        for keyword, tags in theme_keywords.items():
            if keyword in title:
                themes.update(tags)
        
        return list(themes)
    
    @classmethod
    def convert_klook_data(cls, klook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        KLOOK 32컬럼 데이터를 통합 스키마로 변환
        
        Args:
            klook_data: KLOOK CSV 행 데이터 (dict)
            
        Returns:
            통합 스키마 형식의 데이터 (dict)
        """
        
        # 상품 해시 생성 (중복 방지용)
        core_fields = [
            str(klook_data.get('상품명', '')),
            str(klook_data.get('URL', '')),
            str(klook_data.get('가격_정제', ''))
        ]
        product_hash = hashlib.sha1(''.join(core_fields).encode()).hexdigest()
        
        return {
            # ⭐ 필수 식별 정보
            "provider": "Klook",
            "provider_product_id": cls.extract_product_id_from_url(klook_data.get('URL', '')),
            "fetch_ts": datetime.utcnow().isoformat() + "Z",
            "fx_rate": None,  # TODO: 환율 API 연동
            
            # ⭐ 필수 목적지/분류
            "destination_city": klook_data.get('도시명', ''),
            "country": klook_data.get('국가', ''),  # TODO: 영문명 변환
            "theme_tags": json.dumps(cls.extract_themes_from_title(klook_data.get('상품명', '')), ensure_ascii=False),
            
            # ⭐ 필수 상품 정보
            "title": klook_data.get('상품명', ''),
            "subtitle": klook_data.get('부제목', ''),
            "supplier_name": klook_data.get('공급사', ''),
            "duration_hours": cls._parse_duration(klook_data.get('소요시간', '')),
            "pickup": 1 if klook_data.get('픽업포함') else 0,
            "language": json.dumps(["ko"], ensure_ascii=False),  # TODO: 실제 언어 크롤링
            
            # 포함/불포함 (TODO: 실제 크롤링)
            "included": json.dumps([], ensure_ascii=False),
            "excluded": json.dumps([], ensure_ascii=False),
            "meeting_point": klook_data.get('미팅포인트', ''),
            
            # ⭐ 필수 가격 정보
            "price_value": cls._parse_price(klook_data.get('가격_정제', '')),
            "price_currency": cls.convert_to_iso4217(klook_data.get('통화', 'KRW')),
            "option_list": json.dumps([], ensure_ascii=False),  # TODO: 옵션 크롤링
            "price_basis": "adult",
            
            # 평점/리뷰
            "rating_value": cls.normalize_rating(klook_data.get('평점_정제', '')),
            "rating_count": cls._parse_int(klook_data.get('리뷰수', 0)),
            
            # 취소/환불 정책 (TODO: 크롤링)
            "cancel_policy": json.dumps({"free_until_hours": None}, ensure_ascii=False),
            
            # 가용성 (TODO: 크롤링)
            "availability_calendar": json.dumps([], ensure_ascii=False),
            
            # 노출/순위
            "rank_position": klook_data.get('탭내_랭킹', 999),
            
            # ⭐ 필수 링크/이미지
            "landing_url": klook_data.get('URL', ''),
            "affiliate_url": None,  # TODO: 제휴 링크 생성
            "images": json.dumps([
                klook_data.get('메인이미지URL', ''),
                klook_data.get('썸네일URL', '')
            ], ensure_ascii=False),
            
            # 메타데이터
            "product_hash": product_hash,
            "data_source_meta": json.dumps({
                "original_columns": list(klook_data.keys()),
                "conversion_version": "1.0.0",
                "klook_city_id": klook_data.get('도시ID', ''),
                "klook_number": klook_data.get('번호', '')
            }, ensure_ascii=False)
        }
    
    @staticmethod
    def _parse_duration(duration_str: str) -> Optional[float]:
        """소요시간을 시간 단위로 변환"""
        if not duration_str:
            return None
        
        try:
            # "2시간", "3-4시간", "반일", "종일" 등 파싱
            duration_str = str(duration_str).replace(' ', '')
            
            if '시간' in duration_str:
                match = re.search(r'(\d+)', duration_str)
                if match:
                    return float(match.group(1))
            
            if '반일' in duration_str:
                return 4.0
            
            if '종일' in duration_str:
                return 8.0
                
            return None
            
        except Exception:
            return None
    
    @staticmethod
    def _parse_price(price_str: str) -> float:
        """가격 문자열을 숫자로 변환"""
        if not price_str:
            return 0.0
        
        try:
            # 콤마, 공백 제거 후 숫자만 추출
            price_clean = re.sub(r'[^\d.]', '', str(price_str))
            return float(price_clean) if price_clean else 0.0
        except Exception:
            return 0.0
    
    @staticmethod  
    def _parse_int(value: Any) -> int:
        """정수 변환"""
        try:
            return int(float(str(value).replace(',', '')))
        except Exception:
            return 0


def create_unified_database(db_path: str = "unified_travel_products.db") -> UnifiedTravelDatabase:
    """통합 데이터베이스 생성 편의 함수"""
    return UnifiedTravelDatabase(db_path)


def convert_klook_csv_to_unified(klook_data_list: List[Dict]) -> List[Dict]:
    """KLOOK CSV 데이터 리스트를 통합 스키마로 일괄 변환"""
    converter = KlookToUnifiedConverter()
    return [converter.convert_klook_data(data) for data in klook_data_list]


if __name__ == "__main__":
    print("🗄️ 통합 여행상품 데이터베이스 시스템")
    print("   ✅ SQLite 기반 통합 스키마")
    print("   ✅ KLOOK → 통합 스키마 변환")
    print("   ✅ 다중 플랫폼 확장 준비")
    print("   ✅ 감사 로그 및 중복 방지")
    
    # 테스트용 데이터베이스 생성
    db = create_unified_database("test_unified.db")
    print("✅ 테스트 데이터베이스 생성 완료")