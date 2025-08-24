"""
🎮 KLOOK 크롤링 모듈 패키지
- 모듈화된 KLOOK 크롤링 시스템
- 그룹 1-11.5의 모든 기능을 모듈로 분리
"""

# 버전 정보
__version__ = "1.0.0"
__author__ = "KLOOK Crawler Team"

# 단계별 안전한 import (순환 참조 방지)
try:
    # 기본 설정 및 유틸리티
    from . import config
    from . import system_utils
    from . import city_alias_system
    
    # 데이터 처리
    from . import data_handler
    from . import data_consolidator
    
    # URL 및 순위 관리
    from . import url_manager
    from . import rank_mapper
    from . import ranking_manager
    
    # 드라이버 및 수집
    from . import driver_manager
    from . import tab_selector
    from . import url_collection
    
    # 페이지네이션 시스템 (KlookPageTool 포함)
    from . import pagination_utils
    from . import pagination_ranking_system
    from . import simple_pagination_crawler
    from . import integrated_pagination_crawler
    
    # 크롤링 엔진
    from . import crawler_engine
    from . import category_system
    from . import control_system
    
    print("✅ KLOOK 크롤링 모듈 패키지 로드 완료!")
    print(f"🔧 버전: {__version__}")
    
    # 패키지 정보
    __all__ = [
        # 기본 설정 및 유틸리티
        'config',
        'system_utils',
        'city_alias_system',
        
        # 데이터 처리
        'data_handler',
        'data_consolidator',
        
        # URL 및 순위 관리
        'url_manager',
        'rank_mapper',
        'ranking_manager',
        
        # 드라이버 및 수집
        'driver_manager',
        'tab_selector',
        'url_collection',
        
        # 페이지네이션 시스템 (KlookPageTool 포함)
        'pagination_utils',
        'pagination_ranking_system',
        'simple_pagination_crawler',
        'integrated_pagination_crawler',
        
        # 크롤링 엔진
        'crawler_engine',
        'category_system',
        'control_system'
    ]
    
except Exception as e:
    print(f"⚠️ 일부 모듈 로드 실패: {e}")
    print("💡 개별 모듈을 직접 import 하세요: from klook_modules import driver_manager")