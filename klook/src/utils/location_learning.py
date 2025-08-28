import json
import os
import re
from collections import defaultdict

class LocationLearningSystem:
    def __init__(self, db_path=None, city_name=None):
        self.current_city = city_name
        
        if db_path is None:
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
            
            if city_name:
                # 새로운 구조: 대륙/국가/도시코드_keywords.json
                db_path = self._get_city_file_path(project_root, city_name)
            else:
                # 기본 파일
                db_path = os.path.join(project_root, "location_data", "location_keywords.json")
        
        self.db_path = db_path
        self.keyword_db = self._load_db()
        self.confidence_threshold = 7  # 확정 키워드가 되기 위한 빈도수 임계값
    
    def _get_city_file_path(self, project_root, city_name):
        """도시명으로부터 새로운 구조의 파일 경로 생성"""
        try:
            # config.py에서 도시 정보 가져오기
            from ..config import get_city_info, get_city_code
            
            continent, country = get_city_info(city_name)
            city_code = get_city_code(city_name)
            
            # 대륙/국가/도시코드_keywords.json
            db_filename = f"{city_code}_keywords.json"
            db_path = os.path.join(project_root, "location_data", continent, country, db_filename)
            
            return db_path
            
        except Exception as e:
            print(f"⚠️ 도시 정보 조회 실패 ({city_name}): {e}")
            # 폴백: 기존 방식
            city_safe = city_name.lower().replace(" ", "_")
            db_filename = f"{city_safe}_keywords.json"
            return os.path.join(project_root, "location_data", db_filename)

    def _load_db(self):
        """JSON 데이터베이스 파일을 로드합니다."""
        if not os.path.exists(self.db_path):
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            return defaultdict(lambda: {"confirmed": [], "candidates": defaultdict(lambda: {"freq": 0})})

        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                db = defaultdict(lambda: {"confirmed": [], "candidates": defaultdict(lambda: {"freq": 0})})
                for city, values in data.items():
                    db[city]["confirmed"] = values.get("confirmed", [])
                    db[city]["candidates"] = defaultdict(lambda: {"freq": 0}, values.get("candidates", {}))
                return db
        except (json.JSONDecodeError, IOError):
            return defaultdict(lambda: {"confirmed": [], "candidates": defaultdict(lambda: {"freq": 0})})

    def _save_db(self):
        """JSON 데이터베이스 파일에 저장합니다."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                output_db = {city: {
                    "confirmed": values["confirmed"],
                    "candidates": dict(values["candidates"])
                } for city, values in self.keyword_db.items()}
                json.dump(output_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"    ❌ 위치 학습 데이터 저장 실패: {e}")

    def _extract_potential_keywords(self, text):
        """텍스트에서 명사 기반의 잠재적 키워드를 추출합니다."""
        if not text:
            return []

        # 영어 패턴: 대문자로 시작하는 단어들 (Louvre, Orsay, Museum 등)
        english_pattern = r'\b[A-Z][a-zA-Z]+\b'
        english_keywords = re.findall(english_pattern, text)
        
        # 한글 패턴: 2글자 이상 한글
        korean_pattern = r'[가-힣]{2,}'
        korean_keywords = re.findall(korean_pattern, text)
        
        all_keywords = english_keywords + korean_keywords
        
        stop_words = [
            # 기본 서비스 관련
            "Klook", "클룩", "바우처", "티켓", "입장권", "투어", "액티비티", "싱가포르", "한국어",
            "Museum", "Gallery", "Tour", "Ticket", "Experience", "Activity", "Private", "Skip",
            
            # 일반 동사/형용사 (의미없는 키워드)
            "시간", "동안", "제공", "포함", "가능", "안전", "무료", "위한", "모든", "아름다운", "멋진",
            "경험을", "경험하세요", "즐겨보세요", "감상하세요", "탐험하세요", "여행해보세요", "방문하고",
            "즐기세요", "탐험해보세요", "현지인처럼", "일시적인", "흔들리는", "분리된", "따뜻한",
            
            # 일반 명사/도구 (위치와 무관)
            "키트", "사용", "생수", "경험", "선크림", "마법을", "아름다움을", "구명조끼", "마스크",
            "음료", "간식", "뷔페", "식사", "과일", "칵테일", "음악", "시스템", "옵션", "요금",
            
            # 일반적인 형태소/조사
            "동안", "위해", "함께", "가까이서", "사이에서", "근처에서", "따라", "여러", "번의",
            "있는", "모든", "최고의", "숙련된", "놀라운", "상징적인"
        ]
        
        # 길이가 적절하고 스탑워드가 아닌 키워드만 반환
        cleaned_keywords = [kw.strip() for kw in all_keywords if kw.strip() not in stop_words and 1 < len(kw.strip()) < 20]
        
        return list(set(cleaned_keywords))  # 중복 제거

    def learn_from_text(self, city_name, text):
        """주어진 텍스트에서 키워드를 학습하고 DB를 업데이트합니다."""
        if not city_name or not text:
            return

        potential_keywords = self._extract_potential_keywords(text)
        if not potential_keywords:
            return

        for keyword in potential_keywords:
            if keyword in self.keyword_db[city_name]["confirmed"]:
                continue
            self.keyword_db[city_name]["candidates"][keyword]["freq"] += 1

            if self.keyword_db[city_name]["candidates"][keyword]["freq"] >= self.confidence_threshold:
                self.keyword_db[city_name]["confirmed"].append(keyword)
                del self.keyword_db[city_name]["candidates"][keyword]

        self._save_db()

    def get_location_tags(self, city_name, text):
        """텍스트를 분석하여 확정된 위치 태그 목록을 반환하고, 학습을 트리거합니다."""
        if not city_name or not text:
            return []

        confirmed_keywords = self.keyword_db[city_name]["confirmed"]
        found_tags = [kw for kw in confirmed_keywords if kw in text]

        self.learn_from_text(city_name, text)

        return found_tags