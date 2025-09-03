import json
import os
import re
from collections import defaultdict

class LocationLearningSystem:
    def __init__(self, db_path=None, city_name=None):
        self.current_city = city_name

        # KoNLPy 초기화 (조건부)
        from klook.src.config import KONLPY_AVAILABLE
        if KONLPY_AVAILABLE:
            from konlpy.tag import Okt
            self.okt = Okt()
            print(f"🔧 {city_name or '기본'} 도시용 품사 분석기 초기화 완료")
        else:
            self.okt = None
            print(f"⚠️ {city_name or '기본'} 도시: 패턴 기반 키워드 추출 사용")

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
            from klook.src.config import get_city_info, get_city_code
            
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
        """[개선] 품사 분석을 통해 사용자 검색 관점의 키워드를 추출합니다."""
        if not text:
            return []

        # KoNLPy 사용 가능 시 품사 분석
        if self.okt:
            try:
                pos_tagged = self.okt.pos(text, norm=True, stem=True)
                # 명사와 알파벳만 추출
                potential_keywords = [word for word, pos in pos_tagged if pos in ['Noun', 'Alpha']]
            except Exception as e:
                print(f"    ⚠️ 품사 분석 실패, 패턴 방식으로 폴백: {e}")
                potential_keywords = self._regex_extract_fallback(text)
        else:
            # 폴백: 기존 정규식 방식
            potential_keywords = self._regex_extract_fallback(text)

        # 사용자 검색 관점 기반 필터링
        functional_words = [
            # 순수 기능어 (사용자가 절대 검색하지 않을 단어)
            "타고", "출발", "또는", "그리고", "함께", "위해", "동안", "하여", "통해",
            "있는", "있습니다", "제공", "포함", "가능", "위한", "모든", "여러",
            "방법을", "하세요", "보세요", "즐기세요", "만끽하고", "탐험하고"
        ]

        # 길이 조건 + 기능어 제거
        cleaned_keywords = [
            kw.strip() for kw in potential_keywords
            if kw.strip() not in functional_words and 1 < len(kw.strip()) < 20
        ]

        return list(set(cleaned_keywords))  # 중복 제거

    def _regex_extract_fallback(self, text):
        """폴백: 기존 정규식 방식"""
        # 영어 패턴
        english_pattern = r'\b[A-Z][a-zA-Z]+\b'
        english_keywords = re.findall(english_pattern, text)

        # 한글 패턴
        korean_pattern = r'[가-힣]{2,}'
        korean_keywords = re.findall(korean_pattern, text)

        return english_keywords + korean_keywords

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