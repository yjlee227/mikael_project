"""
🚀 그룹 1: 통일된 함수명 - (hashlib 리팩토링 완료)
- 도시 정보를 UNIFIED_CITY_INFO로 통합하여 단일 소스로 관리
- hashlib 기반 초고속 중복 방지 시스템 추가
"""

# 조건부 import - 라이브러리가 없어도 기본 기능 동작
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    print("⚠️ pandas가 설치되지 않았습니다. CSV 기능이 제한됩니다.")
    PANDAS_AVAILABLE = False

import warnings, os, time, shutil, urllib, random
import threading 
_csv_loading_lock = threading.Lock() ## 🔒 자물쇠 걸기
warnings.filterwarnings(action='ignore')
import platform
import re                        # 가격/평점 정제용 정규식
import json                      # 메타데이터 JSON 저장용
import hashlib                   # 🆕 초고속 URL 중복 방지 시스템용
from datetime import datetime    # 타임스탬프용
# PIL import moved to conditional section below
from typing import List, Dict, Tuple, Optional

# 호환성을 위한 조건부 import
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    print("⚠️ PIL이 설치되지 않았습니다. 이미지 처리 기능이 제한됩니다.")
    PIL_AVAILABLE = False

try:
    import chromedriver_autoinstaller
    import undetected_chromedriver as uc
    from user_agents import parse
    WEBDRIVER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 웹드라이버 라이브러리 import 실패: {e}")
    print("💡 다음 명령어로 해결하세요: pip install setuptools undetected-chromedriver")
    WEBDRIVER_AVAILABLE = False
    # 대체 import (최소 실행을 위해)
    uc = None
    parse = None

try:
    import selenium
    SELENIUM_AVAILABLE = True
    print(f"🔧 Selenium 버전: {selenium.__version__}")
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ⭐⭐⭐ 중요 설정: 여기서 수정하세요! ⭐⭐⭐
CONFIG = {
    "WAIT_TIMEOUT": 10,
    "RETRY_COUNT": 3,
    "POPUP_WAIT": 5,
    "SAVE_IMAGES": True,
    
    # 🆕 hashlib 시스템 설정
    "USE_HASH_SYSTEM": True,       # hashlib 시스템 사용 여부
    "HASH_LENGTH": 12,             # 해시 길이 (기본 12자리)
    "KEEP_CSV_SYSTEM": True,       # 기존 CSV 시스템 병행 유지

    # 🆕 V2 3-tier URL 시스템 설정
    "USE_V2_URL_SYSTEM": True,     # V2 3-tier URL 시스템 사용
    "V2_URL_COLLECTED": "url_collected",    # 수집 대기 URL 폴더
    "V2_URL_DONE": "url_done",             # 완료된 URL 폴더
    "V2_URL_PROGRESS": "url_progress",     # 진행 상황 폴더

    # 🆕 페이지 최적화 설정 추가
    "SMART_WAIT_MAX": 8,          # smart_wait_for_page_load 최대 대기
    "NEW_TAB_ENABLED": False,      # 새 탭 크롤링 활성화
    "PAGE_LOAD_TIMEOUT": 6,       # 페이지 로드 타임아웃

    "SHORT_MIN_DELAY": 0.2,    # 타이핑 간격 (0.2초 ~ 0.5초)
    "SHORT_MAX_DELAY": 0.5,

    "MEDIUM_MIN_DELAY": 7,     # 페이지 로드 등 일반 대기 (7초 ~ 15초)
    "MEDIUM_MAX_DELAY": 15,

    "LONG_MIN_DELAY": 20,      # 가끔씩 쉬는 시간 (20초 ~ 40초)
    "LONG_MAX_DELAY": 40,
    
    "MAX_PRODUCTS_PER_CITY": 1,     #⭐⭐⭐⭐⭐⭐⭐⭐⭐#
    
    # 🆕 Gemini 지적사항 해결: USER_AGENT 추가
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
}

# 🏙️ 검색할 도시들 (여기서 변경!)
CITIES_TO_SEARCH = ["서울"]

# =============================================================================
# 📍 [최종 수정본] 단일 정보 소스 및 리팩토링된 함수
# =============================================================================

UNIFIED_CITY_INFO = {
    # -------------------------------
    # 한국
    # -------------------------------
    "서울": {"대륙": "아시아", "국가": "대한민국", "코드": "SEL", "영문명": "seoul"},
    "부산": {"대륙": "아시아", "국가": "대한민국", "코드": "PUS", "영문명": "busan"},
    "제주": {"대륙": "아시아", "국가": "대한민국", "코드": "CJU", "영문명": "jeju"},
    "대구": {"대륙": "아시아", "국가": "대한민국", "코드": "TAE", "영문명": "daegu"},
    "광주": {"대륙": "아시아", "국가": "대한민국", "코드": "KWJ", "영문명": "gwangju"},
    "여수": {"대륙": "아시아", "국가": "대한민국", "코드": "RSU", "영문명": "yeosu"},
    "인천": {"대륙": "아시아", "국가": "대한민국", "코드": "ICN", "영문명": "incheon"},
    "속초": {"대륙": "아시아", "국가": "대한민국", "코드": "SOK", "영문명": "sokcho"},
    "강릉": {"대륙": "아시아", "국가": "대한민국", "코드": "GAN", "영문명": "gangneung"},
    "김포": {"대륙": "아시아", "국가": "대한민국", "코드": "GMP", "영문명": "gimpo"},

    # -------------------------------
    # 동남아시아
    # -------------------------------
    # 태국
    "방콕": {"대륙": "아시아", "국가": "태국", "코드": "BKK", "영문명": "bangkok"},
    "파타야": {"대륙": "아시아", "국가": "태국", "코드": "BKK", "영문명": "pattaya"},
    "아유타야": {"대륙": "아시아", "국가": "태국", "코드": "BKK", "영문명": "ayutthaya"},
    "치앙마이": {"대륙": "아시아", "국가": "태국", "코드": "CNX", "영문명": "chiang mai"},
    "빠이": {"대륙": "아시아", "국가": "태국", "코드": "CNX", "영문명": "pai"},
    "치앙라이": {"대륙": "아시아", "국가": "태국", "코드": "CEI", "영문명": "chiang rai"},
    "푸켓": {"대륙": "아시아", "국가": "태국", "코드": "HKT", "영문명": "phuket"},
    "피피": {"대륙": "아시아", "국가": "태국", "코드": "KBV", "영문명": "phi phi"},
    "크라비": {"대륙": "아시아", "국가": "태국", "코드": "KBV", "영문명": "krabi"},
    "후아힌": {"대륙": "아시아", "국가": "태국", "코드": "HHQ", "영문명": "hua hin"},
    "코사무이": {"대륙": "아시아", "국가": "태국", "코드": "USM", "영문명": "koh samui"},
    "코팡안": {"대륙": "아시아", "국가": "태국", "코드": "USM", "영문명": "koh phangan"},  # 코사무이 경유

    # 싱가포르
    "싱가포르": {"대륙": "아시아", "국가": "싱가포르", "코드": "SIN", "영문명": "singapore"},

    # 말레이시아
    "쿠알라룸푸르": {"대륙": "아시아", "국가": "말레이시아", "코드": "KUL", "영문명": "kuala lumpur"},
    "코타키나발루": {"대륙": "아시아", "국가": "말레이시아", "코드": "BKI", "영문명": "kota kinabalu"},
    "페낭": {"대륙": "아시아", "국가": "말레이시아", "코드": "PEN", "영문명": "penang"},
    "랑카위": {"대륙": "아시아", "국가": "말레이시아", "코드": "LGK", "영문명": "langkawi"},
    "조호르바루": {"대륙": "아시아", "국가": "말레이시아", "코드": "JHB", "영문명": "johor bahru"},

    # 필리핀
    "세부": {"대륙": "아시아", "국가": "필리핀", "코드": "CEB", "영문명": "cebu"},
    "보홀": {"대륙": "아시아", "국가": "필리핀", "코드": "TAG", "영문명": "bohol"},
    "마닐라": {"대륙": "아시아", "국가": "필리핀", "코드": "MNL", "영문명": "manila"},
    "보라카이": {"대륙": "아시아", "국가": "필리핀", "코드": "MPH", "영문명": "boracay"},
    "팔라완": {"대륙": "아시아", "국가": "필리핀", "코드": "PPS", "영문명": "palawan"},
    "다바오": {"대륙": "아시아", "국가": "필리핀", "코드": "DVO", "영문명": "davao"},

    # 베트남
    "다낭": {"대륙": "아시아", "국가": "베트남", "코드": "DAD", "영문명": "da nang"},
    "호이안": {"대륙": "아시아", "국가": "베트남", "코드": "DAD", "영문명": "hoi an"},
    "후에": {"대륙": "아시아", "국가": "베트남", "코드": "HUI", "영문명": "hue"},
    "호치민": {"대륙": "아시아", "국가": "베트남", "코드": "SGN", "영문명": "ho chi minh city"},
    "무이네": {"대륙": "아시아", "국가": "베트남", "코드": "SGN", "영문명": "mui ne"},
    "푸꾸옥": {"대륙": "아시아", "국가": "베트남", "코드": "PQC", "영문명": "phu quoc"},
    "나트랑": {"대륙": "아시아", "국가": "베트남", "코드": "CXR", "영문명": "nha trang"},
    "하노이": {"대륙": "아시아", "국가": "베트남", "코드": "HAN", "영문명": "hanoi"},
    "달랏": {"대륙": "아시아", "국가": "베트남", "코드": "DLI", "영문명": "da lat"},
    "사파": {"대륙": "아시아", "국가": "베트남", "코드": "HAN", "영문명": "sapa"},  # 하노이 경유
    "껀터": {"대륙": "아시아", "국가": "베트남", "코드": "VCA", "영문명": "can tho"},

    # 캄보디아
    "프놈펜": {"대륙": "아시아", "국가": "캄보디아", "코드": "PNH", "영문명": "phnom penh"},
    "시엠립": {"대륙": "아시아", "국가": "캄보디아", "코드": "REP", "영문명": "siem reap"},
    "씨엠립": {"대륙": "아시아", "국가": "캄보디아", "코드": "REP", "영문명": "siem reap"},

    # 라오스
    "비엔티안": {"대륙": "아시아", "국가": "라오스", "코드": "VTE", "영문명": "vientiane"},
    "방비엥": {"대륙": "아시아", "국가": "라오스", "코드": "VTE", "영문명": "vang vieng"},
    "루앙프라방": {"대륙": "아시아", "국가": "라오스", "코드": "LPQ", "영문명": "luang prabang"},

    # 인도네시아
    "발리": {"대륙": "아시아", "국가": "인도네시아", "코드": "DPS", "영문명": "bali"},

    # 몰디브
    "말레": {"대륙": "아시아", "국가": "몰디브", "코드": "MLE", "영문명": "male"},

    # 스리랑카
    "콜롬보": {"대륙": "아시아", "국가": "스리랑카", "코드": "CMB", "영문명": "colombo"},

    # 우즈베키스탄
    "타슈켄트": {"대륙": "아시아", "국가": "우즈베키스탄", "코드": "TAS", "영문명": "tashkent"},
    "사마르칸트": {"대륙": "아시아", "국가": "우즈베키스탄", "코드": "SKD", "영문명": "samarkand"},
    "부하라": {"대륙": "아시아", "국가": "우즈베키스탄", "코드": "BHK", "영문명": "bukhara"},
}

# -------------------------------
# 일본 + 중국/대만
# -------------------------------
UNIFIED_CITY_INFO.update({
    # 일본 (기존 + 추가)
    "도쿄": {"대륙": "아시아", "국가": "일본", "코드": "NRT", "영문명": "tokyo"},
    "오사카": {"대륙": "아시아", "국가": "일본", "코드": "KIX", "영문명": "osaka"},
    "교토": {"대륙": "아시아", "국가": "일본", "코드": "KIX", "영문명": "kyoto"},  # KIX 이용
    "나고야": {"대륙": "아시아", "국가": "일본", "코드": "NGO", "영문명": "nagoya"},
    "후쿠오카": {"대륙": "아시아", "국가": "일본", "코드": "FUK", "영문명": "fukuoka"},
    "벳푸": {"대륙": "아시아", "국가": "일본", "코드": "OIT", "영문명": "beppu"},  # OIT 이용
    "오이타": {"대륙": "아시아", "국가": "일본", "코드": "OIT", "영문명": "oita"},
    "구마모토": {"대륙": "아시아", "국가": "일본", "코드": "KMJ", "영문명": "kumamoto"},
    "오키나와": {"대륙": "아시아", "국가": "일본", "코드": "OKA", "영문명": "okinawa"},
    "미야코지마": {"대륙": "아시아", "국가": "일본", "코드": "MMY", "영문명": "miyakojima"},
    "삿포로": {"대륙": "아시아", "국가": "일본", "코드": "CTS", "영문명": "sapporo"},
    # 일본 추가
    "나가사키": {"대륙": "아시아", "국가": "일본", "코드": "NGS", "영문명": "nagasaki"},
    "사가": {"대륙": "아시아", "국가": "일본", "코드": "HSG", "영문명": "saga"},
    "미야자키": {"대륙": "아시아", "국가": "일본", "코드": "KMI", "영문명": "miyazaki"},
    "가고시마": {"대륙": "아시아", "국가": "일본", "코드": "KOJ", "영문명": "kagoshima"},
    "요코하마": {"대륙": "아시아", "국가": "일본", "코드": "HND", "영문명": "yokohama"},  # 도쿄 하네다 이용
    "나라": {"대륙": "아시아", "국가": "일본", "코드": "KIX", "영문명": "nara"},      # 간사이 이용
    "히로시마": {"대륙": "아시아", "국가": "일본", "코드": "HIJ", "영문명": "hiroshima"},
    "하코다테": {"대륙": "아시아", "국가": "일본", "코드": "HKD", "영문명": "hakodate"},

    # 중국/대만
    "타이베이": {"대륙": "아시아", "국가": "대만", "코드": "TPE", "영문명": "taipei"},
    "가오슝": {"대륙": "아시아", "국가": "대만", "코드": "KHH", "영문명": "kaohsiung"},
    "타이중": {"대륙": "아시아", "국가": "대만", "코드": "RMQ", "영문명": "taichung"},
    "상하이": {"대륙": "아시아", "국가": "중국", "코드": "PVG", "영문명": "shanghai"},
    "베이징": {"대륙": "아시아", "국가": "중국", "코드": "PEK", "영문명": "beijing"},
    "싼야": {"대륙": "아시아", "국가": "중국", "코드": "SYX", "영문명": "sanya"},
    "홍콩": {"대륙": "아시아", "국가": "홍콩", "코드": "HKG", "영문명": "hong kong"},
    "마카오": {"대륙": "아시아", "국가": "마카오", "코드": "MFM", "영문명": "macau"},
})

# -------------------------------
# 유럽 (이탈리아 확장 + 추천지 포함)
# -------------------------------
UNIFIED_CITY_INFO.update({
    # 프랑스
    "파리": {"대륙": "유럽", "국가": "프랑스", "코드": "CDG", "영문명": "paris"},
    "니스": {"대륙": "유럽", "국가": "프랑스", "코드": "NCE", "영문명": "nice"},
    "리옹": {"대륙": "유럽", "국가": "프랑스", "코드": "LYS", "영문명": "lyon"},

    # 영국·아일랜드
    "런던": {"대륙": "유럽", "국가": "영국", "코드": "LHR", "영문명": "london"},
    "더블린": {"대륙": "유럽", "국가": "아일랜드", "코드": "DUB", "영문명": "dublin"},

    # 이탈리아 (기존 + 아말피 해안)
    "로마": {"대륙": "유럽", "국가": "이탈리아", "코드": "FCO", "영문명": "rome"},
    "피렌체": {"대륙": "유럽", "국가": "이탈리아", "코드": "FLR", "영문명": "florence"},
    "베네치아": {"대륙": "유럽", "국가": "이탈리아", "코드": "VCE", "영문명": "venice"},
    "밀라노": {"대륙": "유럽", "국가": "이탈리아", "코드": "MXP", "영문명": "milan"},
    "나폴리": {"대륙": "유럽", "국가": "이탈리아", "코드": "NAP", "영문명": "naples"},
    "아말피": {"대륙": "유럽", "국가": "이탈리아", "코드": "NAP", "영문명": "amalfi"},
    "포시타노": {"대륙": "유럽", "국가": "이탈리아", "코드": "NAP", "영문명": "positano"},
    "라벨로": {"대륙": "유럽", "국가": "이탈리아", "코드": "NAP", "영문명": "ravello"},
    "소렌토": {"대륙": "유럽", "국가": "이탈리아", "코드": "NAP", "영문명": "sorrento"},
    "카프리": {"대륙": "유럽", "국가": "이탈리아", "코드": "NAP", "영문명": "capri"},
    "팔레르모": {"대륙": "유럽", "국가": "이탈리아", "코드": "PMO", "영문명": "palermo"},
    "카타니아": {"대륙": "유럽", "국가": "이탈리아", "코드": "CTA", "영문명": "catania"},
    "토리노": {"대륙": "유럽", "국가": "이탈리아", "코드": "TRN", "영문명": "turin"},
    "제노바": {"대륙": "유럽", "국가": "이탈리아", "코드": "GOA", "영문명": "genoa"},
    "베로나": {"대륙": "유럽", "국가": "이탈리아", "코드": "VRN", "영문명": "verona"},
    "피사": {"대륙": "유럽", "국가": "이탈리아", "코드": "PSA", "영문명": "pisa"},
    "시에나": {"대륙": "유럽", "국가": "이탈리아", "코드": "FLR", "영문명": "siena"},  # FLR 이용

    # 스페인
    "바르셀로나": {"대륙": "유럽", "국가": "스페인", "코드": "BCN", "영문명": "barcelona"},
    "마드리드": {"대륙": "유럽", "국가": "스페인", "코드": "MAD", "영문명": "madrid"},
    "세비야": {"대륙": "유럽", "국가": "스페인", "코드": "SVQ", "영문명": "seville"},
    "그라나다": {"대륙": "유럽", "국가": "스페인", "코드": "GRX", "영문명": "granada"},
    "이비자": {"대륙": "유럽", "국가": "스페인", "코드": "IBZ", "영문명": "ibiza"},
    "발렌시아": {"대륙": "유럽", "국가": "스페인", "코드": "VLC", "영문명": "valencia"},
    "말라가": {"대륙": "유럽", "국가": "스페인", "코드": "AGP", "영문명": "malaga"},

    # 포르투갈
    "리스본": {"대륙": "유럽", "국가": "포르투갈", "코드": "LIS", "영문명": "lisbon"},
    "포르투": {"대륙": "유럽", "국가": "포르투갈", "코드": "OPO", "영문명": "porto"},

    # 중부·동유럽
    "프라하": {"대륙": "유럽", "국가": "체코", "코드": "PRG", "영문명": "prague"},
    "비엔나": {"대륙": "유럽", "국가": "오스트리아", "코드": "VIE", "영문명": "vienna"},
    "부다페스트": {"대륙": "유럽", "국가": "헝가리", "코드": "BUD", "영문명": "budapest"},
    "바르샤바": {"대륙": "유럽", "국가": "폴란드", "코드": "WAW", "영문명": "warsaw"},
    "크라쿠프": {"대륙": "유럽", "국가": "폴란드", "코드": "KRK", "영문명": "krakow"},

    # 스위스
    "취리히": {"대륙": "유럽", "국가": "스위스", "코드": "ZRH", "영문명": "zurich"},
    "인터라켄": {"대륙": "유럽", "국가": "스위스", "코드": "ZRH", "영문명": "interlaken"},  # ZRH 이용
    "제네바": {"대륙": "유럽", "국가": "스위스", "코드": "GVA", "영문명": "geneva"},

    # 베네룩스·북유럽·발칸
    "암스테르담": {"대륙": "유럽", "국가": "네덜란드", "코드": "AMS", "영문명": "amsterdam"},
    "브뤼셀": {"대륙": "유럽", "국가": "벨기에", "코드": "BRU", "영문명": "brussels"},
    "브뤼헤": {"대륙": "유럽", "국가": "벨기에", "코드": "BRU", "영문명": "bruges"},  # 브뤼셀 경유
    "코펜하겐": {"대륙": "유럽", "국가": "덴마크", "코드": "CPH", "영문명": "copenhagen"},
    "스톡홀름": {"대륙": "유럽", "국가": "스웨덴", "코드": "ARN", "영문명": "stockholm"},
    "오슬로": {"대륙": "유럽", "국가": "노르웨이", "코드": "OSL", "영문명": "oslo"},
    "헬싱키": {"대륙": "유럽", "국가": "핀란드", "코드": "HEL", "영문명": "helsinki"},
    "자그레브": {"대륙": "유럽", "국가": "크로아티아", "코드": "ZAG", "영문명": "zagreb"},
    "두브로브니크": {"대륙": "유럽", "국가": "크로아티아", "코드": "DBV", "영문명": "dubrovnik"},
    "스플리트": {"대륙": "유럽", "국가": "크로아티아", "코드": "SPU", "영문명": "split"},

    # 독일
    "뮌헨": {"대륙": "유럽", "국가": "독일", "코드": "MUC", "영문명": "munich"},
    "베를린": {"대륙": "유럽", "국가": "독일", "코드": "BER", "영문명": "berlin"},
    "프랑크푸르트": {"대륙": "유럽", "국가": "독일", "코드": "FRA", "영문명": "frankfurt"},

    # 그리스·터키
    "아테네": {"대륙": "유럽", "국가": "그리스", "코드": "ATH", "영문명": "athens"},
    "산토리니": {"대륙": "유럽", "국가": "그리스", "코드": "JTR", "영문명": "santorini"},
    "이스탄불": {"대륙": "유럽", "국가": "터키", "코드": "IST", "영문명": "istanbul"},
})

# -------------------------------
# 북미, 오세아니아
# -------------------------------
UNIFIED_CITY_INFO.update({
    "뉴욕": {"대륙": "북미", "국가": "미국", "코드": "JFK", "영문명": "new york city"},
    "로스앤젤레스": {"대륙": "북미", "국가": "미국", "코드": "LAX", "영문명": "los angeles"},
    "시카고": {"대륙": "북미", "국가": "미국", "코드": "ORD", "영문명": "chicago"},
    "하와이": {"대륙": "북미", "국가": "미국", "코드": "HNL", "영문명": "hawaii"},
    "샌프란시스코": {"대륙": "북미", "국가": "미국", "코드": "SFO", "영문명": "san francisco"},
    "라스베이거스": {"대륙": "북미", "국가": "미국", "코드": "LAS", "영문명": "las vegas"},
    "워싱턴 D.C.": {"대륙": "북미", "국가": "미국", "코드": "IAD", "영문명": "washington, d.c."},
    "보스턴": {"대륙": "북미", "국가": "미국", "코드": "BOS", "영문명": "boston"},
    "시애틀": {"대륙": "북미", "국가": "미국", "코드": "SEA", "영문명": "seattle"},

    # 미국 추가
    "마이애미": {"대륙": "북미", "국가": "미국", "코드": "MIA", "영문명": "miami"},
    "올랜도": {"대륙": "북미", "국가": "미국", "코드": "MCO", "영문명": "orlando"},
    "뉴올리언스": {"대륙": "북미", "국가": "미국", "코드": "MSY", "영문명": "new orleans"},

    # 캐나다
    "밴쿠버": {"대륙": "북미", "국가": "캐나다", "코드": "YVR", "영문명": "vancouver"},
    "토론토": {"대륙": "북미", "국가": "캐나다", "코드": "YYZ", "영문명": "toronto"},
    "몬트리올": {"대륙": "북미", "국가": "캐나다", "코드": "YUL", "영문명": "montreal"},
    "캘거리": {"대륙": "북미", "국가": "캐나다", "코드": "YYC", "영문명": "calgary"},

    # 멕시코
    "칸쿤": {"대륙": "북미", "국가": "멕시코", "코드": "CUN", "영문명": "cancun"},
    "멕시코시티": {"대륙": "북미", "국가": "멕시코", "코드": "MEX", "영문명": "mexico city"},
    "시드니": {"대륙": "오세아니아", "국가": "호주", "코드": "SYD", "영문명": "sydney"},

    # 오세아니아
    "멜버른": {"대륙": "오세아니아", "국가": "호주", "코드": "MEL", "영문명": "melbourne"},
    "브리즈번": {"대륙": "오세아니아", "국가": "호주", "코드": "BNE", "영문명": "brisbane"},
    "퍼스": {"대륙": "오세아니아", "국가": "호주", "코드": "PER", "영문명": "perth"},
    "케언즈": {"대륙": "오세아니아", "국가": "호주", "코드": "CNS", "영문명": "cairns"},

    "오클랜드": {"대륙": "오세아니아", "국가": "뉴질랜드", "코드": "AKL", "영문명": "auckland"},
    "퀸스타운": {"대륙": "오세아니아", "국가": "뉴질랜드", "코드": "ZQN", "영문명": "queenstown"},

    # 미크로네시아 (한국 인기 휴양지)
    "괌": {"대륙": "오세아니아", "국가": "괌", "코드": "GUM", "영문명": "guam"},
    "사이판": {"대륙": "오세아니아", "국가": "북마리아나 제도", "코드": "SPN", "영문명": "saipan"},
})


# -------------------------------
# 중동, 아프리카
# -------------------------------
UNIFIED_CITY_INFO.update({
    "두바이": {"대륙": "중동", "국가": "아랍에미리트", "코드": "DXB", "영문명": "dubai"},
    "아부다비": {"대륙": "중동", "국가": "아랍에미리트", "코드": "AUH", "영문명": "abu dhabi"},
    "도하": {"대륙": "중동", "국가": "카타르", "코드": "DOH", "영문명": "doha"},
    "텔아비브": {"대륙": "중동", "국가": "이스라엘", "코드": "TLV", "영문명": "tel aviv"},
    "예루살렘": {"대륙": "중동", "국가": "이스라엘", "코드": "TLV", "영문명": "jerusalem"},  
    "카이로": {"대륙": "아프리카", "국가": "이집트", "코드": "CAI", "영문명": "cairo"},
    "마라케시": {"대륙": "아프리카", "국가": "모로코", "코드": "RAK", "영문명": "marrakech"},
    "카사블랑카": {"대륙": "아프리카", "국가": "모로코", "코드": "CMN", "영문명": "casablanca"},
    "케이프타운": {"대륙": "아프리카", "국가": "남아프리카공화국", "코드": "CPT", "영문명": "cape town"},
    "요하네스버그": {"대륙": "아프리카", "국가": "남아프리카공화국", "코드": "JNB", "영문명": "johannesburg"},
    "나이로비": {"대륙": "아프리카", "국가": "케냐", "코드": "NBO", "영문명": "nairobi"},
})


print(f"✅ UNIFIED_CITY_INFO 최종 업데이트 완료! 총 {len(UNIFIED_CITY_INFO)}개 도시")

# =============================================================================
# 🔧 핵심 함수들
# =============================================================================

def get_city_code(city_name):
    """도시명으로 공항 코드 반환 (UNIFIED_CITY_INFO 사용)"""
    info = UNIFIED_CITY_INFO.get(city_name)
    if info:
        code = info.get("코드", city_name[:3].upper())
        return code
    return city_name[:3].upper()

def get_city_info(city_name):
    """통합된 도시 정보 가져오기 (사전 정의된 값만 사용)"""
    info = UNIFIED_CITY_INFO.get(city_name)
    if info:
        return info["대륙"], info["국가"]
    else:
        # 정의되지 않은 도시에 대한 기본값
        return "기타", "기타"

# =============================================================================
# 🆕 hashlib 기반 초고속 중복 방지 시스템
# =============================================================================

def get_url_hash(url):
    """URL을 고유한 짧은 해시로 변환 (0.0001초)"""
    hash_length = CONFIG.get("HASH_LENGTH", 12)
    return hashlib.md5(url.encode('utf-8')).hexdigest()[:hash_length]

def is_url_processed_fast(url, city_name):
    """해시 파일 존재 여부로 초고속 중복 체크 (0.001초)"""
    if not CONFIG.get("USE_HASH_SYSTEM", True):
        return False
        
    url_hash = get_url_hash(url)
    hash_file = os.path.join("hash_index", city_name, f"{url_hash}.done")
    return os.path.exists(hash_file)

def mark_url_processed_fast(url, city_name, product_number=None, rank=None):
    """해시 파일 생성으로 완료 표시 (0.002초) - 순위 정보 추가"""
    if not CONFIG.get("USE_HASH_SYSTEM", True):
        return False
        
    url_hash = get_url_hash(url)
    hash_dir = os.path.join("hash_index", city_name)
    os.makedirs(hash_dir, exist_ok=True)
    
    hash_file = os.path.join(hash_dir, f"{url_hash}.done")
    with open(hash_file, 'w', encoding='utf-8') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"URL: {url}\n")
        f.write(f"Product: {product_number}\n")
        if rank is not None:
            f.write(f"Rank: {rank}\n")  # 🆕 순위 정보 추가
        f.write(f"City: {city_name}\n")  # 🆕 도시 정보 추가
        f.write(f"Completed: {timestamp}\n")
    
    return True

def get_last_collected_rank(city_name):
    """마지막 수집된 순위 조회 (개수 기반 시스템용)"""
    hash_dir = os.path.join("hash_index", city_name)
    if not os.path.exists(hash_dir):
        return 0
    
    max_rank = 0
    try:
        for filename in os.listdir(hash_dir):
            if filename.endswith('.done'):
                filepath = os.path.join(hash_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('Rank: '):
                                rank = int(line.split('Rank: ')[1].strip())
                                max_rank = max(max_rank, rank)
                except (ValueError, IndexError, FileNotFoundError):
                    continue
    except Exception as e:
        print(f"⚠️ 순위 조회 실패: {e}")
    
    return max_rank

def get_next_collection_range(city_name, count=3):
    """다음 수집할 순위 범위 자동 계산 (개수 기반 시스템)"""
    last_rank = get_last_collected_rank(city_name)
    start_rank = last_rank + 1
    end_rank = start_rank + count - 1
    
    print(f"🎯 '{city_name}' 다음 수집 범위: {start_rank}~{end_rank}위 ({count}개)")
    return start_rank, end_rank

def find_missing_ranks(city_name, max_rank=50):
    """누락된 순위 구간 찾기"""
    hash_dir = os.path.join("hash_index", city_name)
    if not os.path.exists(hash_dir):
        return []
    
    collected_ranks = set()
    try:
        for filename in os.listdir(hash_dir):
            if filename.endswith('.done'):
                filepath = os.path.join(hash_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('Rank: '):
                                rank = int(line.split('Rank: ')[1].strip())
                                if 1 <= rank <= max_rank:
                                    collected_ranks.add(rank)
                except (ValueError, IndexError, FileNotFoundError):
                    continue
    except Exception as e:
        print(f"⚠️ 누락 순위 조회 실패: {e}")
        return []
    
    # 연속된 누락 구간 찾기
    missing_ranges = []
    if not collected_ranks:
        return [(1, max_rank)]
    
    sorted_ranks = sorted(collected_ranks)
    current_start = 1
    
    for rank in sorted_ranks:
        if rank > current_start:
            missing_ranges.append((current_start, rank - 1))
        current_start = max(current_start, rank + 1)
    
    # 마지막 구간 체크
    if current_start <= max_rank:
        missing_ranges.append((current_start, max_rank))
    
    return missing_ranges

def smart_next_collection_range(city_name, count=3, fill_gaps=True):
    """🆕 지능형 다음 수집 범위 계산 (랭킹 매니저 통합 - 범용)"""
    # 랭킹 매니저를 우선 사용 (더 정확함)
    try:
        from .ranking_manager import ranking_manager
        
        print(f"🏆 랭킹 매니저로 다음 범위 계산 중...")
        start_rank, end_rank = ranking_manager.get_next_available_range(
            city_name, count, tab_name=None, fill_gaps=fill_gaps
        )
        
        if fill_gaps:
            print(f"🔧 갭 채우기 모드: {start_rank}~{end_rank}위")
        else:
            print(f"🔧 연속 모드: {start_rank}~{end_rank}위")
        
        return start_rank, end_rank
        
    except Exception as e:
        print(f"⚠️ 랭킹 매니저 사용 실패: {e}")
        print(f"🔄 기존 방식으로 폴백...")
    
    # 폴백: 기존 방식
    if fill_gaps:
        missing_ranges = find_missing_ranks(city_name)
        if missing_ranges:
            # 가장 작은 갭부터 채우기
            start_missing, end_missing = missing_ranges[0]
            gap_size = end_missing - start_missing + 1
            
            if gap_size >= count:
                # 갭이 충분히 크면 갭에서 수집
                end_rank = start_missing + count - 1
                print(f"🔧 폴백 갭 채우기 모드: {start_missing}~{end_rank}위")
                return start_missing, end_rank
            else:
                # 갭이 작으면 갭 전체 + 연속 순위
                remaining = count - gap_size
                last_rank = get_last_collected_rank(city_name)
                next_start = max(end_missing + 1, last_rank + 1)
                next_end = next_start + remaining - 1
                
                print(f"🔧 폴백 하이브리드 모드: {start_missing}~{end_missing}위(갭) + {next_start}~{next_end}위(연속)")
                # 편의상 연속 범위만 반환 (갭은 별도 처리 필요)
                return start_missing, start_missing + count - 1
    
    # 기본: 연속된 다음 순위들 (폴백)
    print(f"🔧 폴백 연속 모드")
    return get_next_collection_range(city_name, count)

def ensure_config_directory():
    """config 디렉토리 안정성 확보"""
    config_dir = os.path.join(os.getcwd(), "config")
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_completed_urls_from_csv(city_name):
    """CSV 파일에서 완료된 URL 목록 가져오기 (호환성용)"""
    try:
        continent, country = get_city_info(city_name)
        
        # 도시국가 특별 처리
        if city_name in ["마카오", "홍콩", "싱가포르"]:
            csv_path = os.path.join("data", continent, f"klook_{city_name}_products.csv")
        else:
            csv_path = os.path.join("data", continent, country, city_name, f"klook_{city_name}_products.csv")
        
        if not os.path.exists(csv_path):
            return set()
        
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        if 'URL' in df.columns:
            return set(df['URL'].dropna().tolist())
        return set()
        
    except Exception as e:
        print(f"⚠️ CSV URL 로드 실패: {e}")
        return set()

def save_url_to_log(city_name, url):
    """V2 3-tier 시스템에 URL 로그 저장 (호환성용)"""
    try:
        log_dir = CONFIG.get("V2_URL_LOG", "url_collected")
        os.makedirs(log_dir, exist_ok=True)
        
        city_code = get_city_code(city_name)
        log_file = os.path.join(log_dir, f"{city_code}_url_log.txt")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} | {url}\n")
        
        return True
    except Exception as e:
        print(f"⚠️ URL 로그 저장 실패: {e}")
        return False

print("✅ 그룹 1 완료: 기본 설정 및 hashlib 통합 시스템 정의 완료!")
print(f"🚀 hashlib 시스템 상태: {'활성화' if CONFIG.get('USE_HASH_SYSTEM', True) else '비활성화'}")
print(f"🔄 CSV 호환성: {'유지' if CONFIG.get('KEEP_CSV_SYSTEM', True) else '비활성화'}")
print(f"📊 해시 길이: {CONFIG.get('HASH_LENGTH', 12)}자리")