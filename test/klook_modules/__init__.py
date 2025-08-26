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
    from . import config
    from . import data_handler
    from . import url_manager
    from . import system_utils
    from . import driver_manager
    from . import tab_selector
    from . import url_collection
    from . import crawler_engine
    from . import category_system
    from . import control_system
    
    print("✅ KLOOK 크롤링 모듈 패키지 로드 완료!")
    print(f"🔧 버전: {__version__}")
    
    # 패키지 정보
    __all__ = [
        'config',
        'data_handler', 
        'url_manager',
        'system_utils',
        'driver_manager',
        'tab_selector',
        'url_collection',
        'crawler_engine',
        'category_system',
        'control_system'
    ]
    
except Exception as e:
    print(f"⚠️ 일부 모듈 로드 실패: {e}")
    print("💡 개별 모듈을 직접 import 하세요: from klook_modules import driver_manager")