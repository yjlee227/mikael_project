"""
인간 행동 기반 스크롤 패턴 라이브러리
- 실제 사람의 스크롤 행동을 분석하여 구현
- 각 패턴은 실제 인간의 다양한 읽기/탐색 스타일을 모방
"""

import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# =============================================================================
# 인간 행동 기반 스크롤 패턴 50개
# =============================================================================

HUMAN_SCROLL_PATTERNS = {
    # 1-10: 천천히 읽는 사용자 패턴
    "느린_탐색": [
        {
            "name": "꼼꼼한_독서형",
            "description": "천천히 읽으며 중간중간 멈춤",
            "actions": [
                {"action": "scroll", "pixels": 200, "duration": 1.2},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll", "pixels": 150, "duration": 1.0},
                {"action": "pause", "duration": 3.2},
                {"action": "scroll", "pixels": 300, "duration": 1.5},
                {"action": "pause", "duration": 2.8}
            ]
        },
        {
            "name": "신중한_검토형",
            "description": "조금씩 스크롤하며 내용 확인",
            "actions": [
                {"action": "scroll", "pixels": 100, "duration": 0.8},
                {"action": "pause", "duration": 2.0},
                {"action": "scroll", "pixels": 120, "duration": 0.9},
                {"action": "pause", "duration": 2.7},
                {"action": "scroll", "pixels": 80, "duration": 0.7},
                {"action": "pause", "duration": 1.8},
                {"action": "scroll", "pixels": 200, "duration": 1.1}
            ]
        },
        {
            "name": "상세_분석형",
            "description": "내용을 자세히 보며 천천히 진행",
            "actions": [
                {"action": "scroll", "pixels": 180, "duration": 1.1},
                {"action": "pause", "duration": 3.5},
                {"action": "scroll", "pixels": 90, "duration": 0.8},
                {"action": "pause", "duration": 2.2},
                {"action": "scroll_up", "pixels": 50, "duration": 0.6},
                {"action": "pause", "duration": 1.5},
                {"action": "scroll", "pixels": 250, "duration": 1.4}
            ]
        },
        {
            "name": "집중_읽기형",
            "description": "한 부분씩 집중해서 읽기",
            "actions": [
                {"action": "scroll", "pixels": 160, "duration": 1.0},
                {"action": "pause", "duration": 4.0},
                {"action": "scroll", "pixels": 140, "duration": 0.9},
                {"action": "pause", "duration": 3.2},
                {"action": "scroll", "pixels": 110, "duration": 0.8},
                {"action": "pause", "duration": 2.8}
            ]
        },
        {
            "name": "비교_검토형",
            "description": "위로 돌아가서 비교해보며 읽기",
            "actions": [
                {"action": "scroll", "pixels": 200, "duration": 1.2},
                {"action": "pause", "duration": 2.0},
                {"action": "scroll_up", "pixels": 100, "duration": 0.8},
                {"action": "pause", "duration": 1.8},
                {"action": "scroll", "pixels": 300, "duration": 1.5},
                {"action": "pause", "duration": 2.5}
            ]
        },
        {
            "name": "점진적_독서형",
            "description": "점점 스크롤 양을 늘려가며 읽기",
            "actions": [
                {"action": "scroll", "pixels": 80, "duration": 0.7},
                {"action": "pause", "duration": 2.2},
                {"action": "scroll", "pixels": 120, "duration": 0.9},
                {"action": "pause", "duration": 2.0},
                {"action": "scroll", "pixels": 180, "duration": 1.1},
                {"action": "pause", "duration": 1.8},
                {"action": "scroll", "pixels": 240, "duration": 1.3}
            ]
        },
        {
            "name": "중간_휴식형",
            "description": "중간에 긴 휴식을 취하며 읽기",
            "actions": [
                {"action": "scroll", "pixels": 150, "duration": 1.0},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll", "pixels": 200, "duration": 1.2},
                {"action": "pause", "duration": 5.0},
                {"action": "scroll", "pixels": 180, "duration": 1.1},
                {"action": "pause", "duration": 2.0}
            ]
        },
        {
            "name": "반복_확인형",
            "description": "같은 부분을 여러 번 확인",
            "actions": [
                {"action": "scroll", "pixels": 120, "duration": 0.9},
                {"action": "pause", "duration": 2.0},
                {"action": "scroll_up", "pixels": 60, "duration": 0.6},
                {"action": "pause", "duration": 1.5},
                {"action": "scroll", "pixels": 180, "duration": 1.1},
                {"action": "pause", "duration": 2.8}
            ]
        },
        {
            "name": "세밀_체크형",
            "description": "매우 작은 단위로 스크롤하며 확인",
            "actions": [
                {"action": "scroll", "pixels": 60, "duration": 0.6},
                {"action": "pause", "duration": 1.8},
                {"action": "scroll", "pixels": 70, "duration": 0.7},
                {"action": "pause", "duration": 2.1},
                {"action": "scroll", "pixels": 80, "duration": 0.7},
                {"action": "pause", "duration": 1.9},
                {"action": "scroll", "pixels": 90, "duration": 0.8}
            ]
        },
        {
            "name": "신중한_판단형",
            "description": "각 섹션을 신중하게 판단하며 진행",
            "actions": [
                {"action": "scroll", "pixels": 140, "duration": 1.0},
                {"action": "pause", "duration": 3.8},
                {"action": "scroll", "pixels": 160, "duration": 1.1},
                {"action": "pause", "duration": 4.2},
                {"action": "scroll", "pixels": 100, "duration": 0.8},
                {"action": "pause", "duration": 2.5}
            ]
        }
    ],

    # 11-20: 빠른 스캔 사용자 패턴
    "빠른_스캔": [
        {
            "name": "급한_훑어보기형",
            "description": "빠르게 전체 내용을 훑어봄",
            "actions": [
                {"action": "scroll", "pixels": 400, "duration": 0.8},
                {"action": "pause", "duration": 0.8},
                {"action": "scroll", "pixels": 500, "duration": 0.9},
                {"action": "pause", "duration": 0.6},
                {"action": "scroll", "pixels": 450, "duration": 0.8},
                {"action": "pause", "duration": 0.7}
            ]
        },
        {
            "name": "키워드_탐색형",
            "description": "특정 키워드를 찾기 위한 빠른 스크롤",
            "actions": [
                {"action": "scroll", "pixels": 300, "duration": 0.6},
                {"action": "pause", "duration": 0.5},
                {"action": "scroll", "pixels": 350, "duration": 0.7},
                {"action": "pause", "duration": 0.4},
                {"action": "scroll_up", "pixels": 100, "duration": 0.4},
                {"action": "pause", "duration": 0.6},
                {"action": "scroll", "pixels": 400, "duration": 0.8}
            ]
        },
        {
            "name": "개요_파악형",
            "description": "전체적인 구조를 빠르게 파악",
            "actions": [
                {"action": "scroll", "pixels": 600, "duration": 1.0},
                {"action": "pause", "duration": 0.8},
                {"action": "scroll", "pixels": 500, "duration": 0.9},
                {"action": "pause", "duration": 0.5},
                {"action": "scroll_up", "pixels": 200, "duration": 0.6},
                {"action": "pause", "duration": 0.7}
            ]
        },
        {
            "name": "속독_스캔형",
            "description": "빠른 속도로 읽으며 스크롤",
            "actions": [
                {"action": "scroll", "pixels": 280, "duration": 0.5},
                {"action": "pause", "duration": 0.8},
                {"action": "scroll", "pixels": 320, "duration": 0.6},
                {"action": "pause", "duration": 0.7},
                {"action": "scroll", "pixels": 380, "duration": 0.7},
                {"action": "pause", "duration": 0.6}
            ]
        },
        {
            "name": "점프_읽기형",
            "description": "중요한 부분만 골라서 보기",
            "actions": [
                {"action": "scroll", "pixels": 250, "duration": 0.5},
                {"action": "pause", "duration": 0.9},
                {"action": "scroll", "pixels": 400, "duration": 0.7},
                {"action": "pause", "duration": 0.5},
                {"action": "scroll", "pixels": 300, "duration": 0.6},
                {"action": "pause", "duration": 0.8}
            ]
        },
        {
            "name": "시간절약형",
            "description": "시간을 아끼기 위한 효율적 스크롤",
            "actions": [
                {"action": "scroll", "pixels": 420, "duration": 0.7},
                {"action": "pause", "duration": 0.6},
                {"action": "scroll", "pixels": 380, "duration": 0.6},
                {"action": "pause", "duration": 0.5},
                {"action": "scroll", "pixels": 460, "duration": 0.8},
                {"action": "pause", "duration": 0.7}
            ]
        },
        {
            "name": "빠른_검색형",
            "description": "원하는 정보를 빠르게 찾기",
            "actions": [
                {"action": "scroll", "pixels": 350, "duration": 0.6},
                {"action": "pause", "duration": 0.4},
                {"action": "scroll", "pixels": 400, "duration": 0.7},
                {"action": "pause", "duration": 0.3},
                {"action": "scroll_up", "pixels": 150, "duration": 0.4},
                {"action": "scroll", "pixels": 500, "duration": 0.8}
            ]
        },
        {
            "name": "효율_우선형",
            "description": "최소 시간으로 최대 정보 획득",
            "actions": [
                {"action": "scroll", "pixels": 480, "duration": 0.8},
                {"action": "pause", "duration": 0.7},
                {"action": "scroll", "pixels": 520, "duration": 0.9},
                {"action": "pause", "duration": 0.5},
                {"action": "scroll", "pixels": 360, "duration": 0.6}
            ]
        },
        {
            "name": "대략_파악형",
            "description": "대략적인 내용만 파악하고 넘어감",
            "actions": [
                {"action": "scroll", "pixels": 300, "duration": 0.5},
                {"action": "pause", "duration": 0.6},
                {"action": "scroll", "pixels": 450, "duration": 0.7},
                {"action": "pause", "duration": 0.4},
                {"action": "scroll", "pixels": 400, "duration": 0.7},
                {"action": "pause", "duration": 0.5}
            ]
        },
        {
            "name": "빠른_결정형",
            "description": "빠르게 보고 결정을 내림",
            "actions": [
                {"action": "scroll", "pixels": 380, "duration": 0.6},
                {"action": "pause", "duration": 0.8},
                {"action": "scroll", "pixels": 420, "duration": 0.7},
                {"action": "pause", "duration": 0.6},
                {"action": "scroll", "pixels": 350, "duration": 0.6},
                {"action": "pause", "duration": 0.9}
            ]
        }
    ],

    # 21-30: 상세 읽기 사용자 패턴
    "상세_읽기": [
        {
            "name": "완벽주의형",
            "description": "모든 내용을 빠짐없이 읽기",
            "actions": [
                {"action": "scroll", "pixels": 120, "duration": 1.0},
                {"action": "pause", "duration": 3.0},
                {"action": "scroll", "pixels": 100, "duration": 0.9},
                {"action": "pause", "duration": 3.5},
                {"action": "scroll", "pixels": 130, "duration": 1.1},
                {"action": "pause", "duration": 4.0},
                {"action": "scroll_up", "pixels": 50, "duration": 0.7},
                {"action": "scroll", "pixels": 180, "duration": 1.2}
            ]
        },
        {
            "name": "학습목적형",
            "description": "공부하듯이 자세히 읽기",
            "actions": [
                {"action": "scroll", "pixels": 90, "duration": 0.8},
                {"action": "pause", "duration": 4.2},
                {"action": "scroll", "pixels": 110, "duration": 0.9},
                {"action": "pause", "duration": 3.8},
                {"action": "scroll_up", "pixels": 60, "duration": 0.6},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll", "pixels": 170, "duration": 1.1}
            ]
        },
        {
            "name": "전문가형",
            "description": "전문적 관점에서 꼼꼼히 분석",
            "actions": [
                {"action": "scroll", "pixels": 150, "duration": 1.1},
                {"action": "pause", "duration": 3.5},
                {"action": "scroll_up", "pixels": 70, "duration": 0.7},
                {"action": "pause", "duration": 2.2},
                {"action": "scroll", "pixels": 200, "duration": 1.3},
                {"action": "pause", "duration": 4.0},
                {"action": "scroll", "pixels": 120, "duration": 1.0}
            ]
        },
        {
            "name": "비판적_읽기형",
            "description": "비판적으로 분석하며 읽기",
            "actions": [
                {"action": "scroll", "pixels": 140, "duration": 1.0},
                {"action": "pause", "duration": 3.8},
                {"action": "scroll_up", "pixels": 80, "duration": 0.7},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll", "pixels": 160, "duration": 1.1},
                {"action": "pause", "duration": 3.2},
                {"action": "scroll", "pixels": 180, "duration": 1.2}
            ]
        },
        {
            "name": "연구자형",
            "description": "연구 목적으로 세밀하게 검토",
            "actions": [
                {"action": "scroll", "pixels": 80, "duration": 0.8},
                {"action": "pause", "duration": 4.5},
                {"action": "scroll", "pixels": 100, "duration": 0.9},
                {"action": "pause", "duration": 4.0},
                {"action": "scroll_up", "pixels": 50, "duration": 0.6},
                {"action": "pause", "duration": 2.8},
                {"action": "scroll", "pixels": 150, "duration": 1.1}
            ]
        },
        {
            "name": "메모형",
            "description": "중요한 부분에서 멈춰서 메모",
            "actions": [
                {"action": "scroll", "pixels": 120, "duration": 1.0},
                {"action": "pause", "duration": 5.0},
                {"action": "scroll", "pixels": 140, "duration": 1.1},
                {"action": "pause", "duration": 4.5},
                {"action": "scroll", "pixels": 100, "duration": 0.9},
                {"action": "pause", "duration": 6.0}
            ]
        },
        {
            "name": "질문형",
            "description": "궁금한 부분에서 멈춰서 생각",
            "actions": [
                {"action": "scroll", "pixels": 110, "duration": 0.9},
                {"action": "pause", "duration": 3.5},
                {"action": "scroll_up", "pixels": 40, "duration": 0.5},
                {"action": "pause", "duration": 2.8},
                {"action": "scroll", "pixels": 180, "duration": 1.2},
                {"action": "pause", "duration": 4.2}
            ]
        },
        {
            "name": "이해확인형",
            "description": "이해할 때까지 반복해서 읽기",
            "actions": [
                {"action": "scroll", "pixels": 130, "duration": 1.0},
                {"action": "pause", "duration": 3.0},
                {"action": "scroll_up", "pixels": 90, "duration": 0.8},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll", "pixels": 200, "duration": 1.3},
                {"action": "pause", "duration": 3.8}
            ]
        },
        {
            "name": "분석형",
            "description": "내용을 분석하며 천천히 읽기",
            "actions": [
                {"action": "scroll", "pixels": 100, "duration": 0.9},
                {"action": "pause", "duration": 4.0},
                {"action": "scroll", "pixels": 120, "duration": 1.0},
                {"action": "pause", "duration": 3.8},
                {"action": "scroll_up", "pixels": 60, "duration": 0.6},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll", "pixels": 180, "duration": 1.2}
            ]
        },
        {
            "name": "심층이해형",
            "description": "깊이 있는 이해를 위한 정독",
            "actions": [
                {"action": "scroll", "pixels": 90, "duration": 0.8},
                {"action": "pause", "duration": 4.8},
                {"action": "scroll", "pixels": 110, "duration": 0.9},
                {"action": "pause", "duration": 4.2},
                {"action": "scroll", "pixels": 130, "duration": 1.0},
                {"action": "pause", "duration": 3.5}
            ]
        }
    ],

    # 31-40: 되돌아보기 사용자 패턴
    "되돌아_보기": [
        {
            "name": "확인중독형",
            "description": "계속해서 위로 돌아가서 확인",
            "actions": [
                {"action": "scroll", "pixels": 200, "duration": 1.2},
                {"action": "pause", "duration": 1.8},
                {"action": "scroll_up", "pixels": 150, "duration": 1.0},
                {"action": "pause", "duration": 2.0},
                {"action": "scroll", "pixels": 300, "duration": 1.5},
                {"action": "scroll_up", "pixels": 100, "duration": 0.8},
                {"action": "scroll", "pixels": 250, "duration": 1.3}
            ]
        },
        {
            "name": "비교검토형",
            "description": "앞 내용과 비교하며 읽기",
            "actions": [
                {"action": "scroll", "pixels": 180, "duration": 1.1},
                {"action": "pause", "duration": 2.2},
                {"action": "scroll_up", "pixels": 200, "duration": 1.2},
                {"action": "pause", "duration": 1.8},
                {"action": "scroll", "pixels": 320, "duration": 1.6},
                {"action": "pause", "duration": 2.5}
            ]
        },
        {
            "name": "망설이는형",
            "description": "결정을 못 내리고 계속 왔다갔다",
            "actions": [
                {"action": "scroll", "pixels": 150, "duration": 1.0},
                {"action": "pause", "duration": 2.0},
                {"action": "scroll_up", "pixels": 80, "duration": 0.7},
                {"action": "pause", "duration": 1.5},
                {"action": "scroll", "pixels": 120, "duration": 0.9},
                {"action": "scroll_up", "pixels": 60, "duration": 0.6},
                {"action": "scroll", "pixels": 200, "duration": 1.2}
            ]
        },
        {
            "name": "재확인형",
            "description": "중요한 부분을 다시 확인",
            "actions": [
                {"action": "scroll", "pixels": 220, "duration": 1.3},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll_up", "pixels": 180, "duration": 1.1},
                {"action": "pause", "duration": 2.8},
                {"action": "scroll", "pixels": 280, "duration": 1.4},
                {"action": "pause", "duration": 2.0}
            ]
        },
        {
            "name": "연결점_찾기형",
            "description": "앞뒤 연결점을 찾으며 읽기",
            "actions": [
                {"action": "scroll", "pixels": 160, "duration": 1.0},
                {"action": "pause", "duration": 1.8},
                {"action": "scroll_up", "pixels": 120, "duration": 0.9},
                {"action": "pause", "duration": 2.2},
                {"action": "scroll", "pixels": 240, "duration": 1.3},
                {"action": "scroll_up", "pixels": 80, "duration": 0.7},
                {"action": "scroll", "pixels": 200, "duration": 1.2}
            ]
        },
        {
            "name": "맥락파악형",
            "description": "전체적인 맥락을 파악하기 위해 이동",
            "actions": [
                {"action": "scroll", "pixels": 190, "duration": 1.1},
                {"action": "pause", "duration": 2.0},
                {"action": "scroll_up", "pixels": 140, "duration": 1.0},
                {"action": "pause", "duration": 1.8},
                {"action": "scroll", "pixels": 260, "duration": 1.4},
                {"action": "pause", "duration": 2.3}
            ]
        },
        {
            "name": "의심많은형",
            "description": "의심스러운 부분을 계속 재검토",
            "actions": [
                {"action": "scroll", "pixels": 140, "duration": 0.9},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll_up", "pixels": 100, "duration": 0.8},
                {"action": "pause", "duration": 3.0},
                {"action": "scroll", "pixels": 180, "duration": 1.1},
                {"action": "scroll_up", "pixels": 90, "duration": 0.7},
                {"action": "scroll", "pixels": 220, "duration": 1.3}
            ]
        },
        {
            "name": "정보통합형",
            "description": "여러 정보를 통합하기 위해 이동",
            "actions": [
                {"action": "scroll", "pixels": 200, "duration": 1.2},
                {"action": "pause", "duration": 2.0},
                {"action": "scroll_up", "pixels": 160, "duration": 1.0},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll", "pixels": 300, "duration": 1.5},
                {"action": "pause", "duration": 2.2}
            ]
        },
        {
            "name": "체크리스트형",
            "description": "체크리스트처럼 확인하며 이동",
            "actions": [
                {"action": "scroll", "pixels": 170, "duration": 1.1},
                {"action": "pause", "duration": 1.5},
                {"action": "scroll_up", "pixels": 110, "duration": 0.8},
                {"action": "pause", "duration": 1.8},
                {"action": "scroll", "pixels": 190, "duration": 1.2},
                {"action": "scroll_up", "pixels": 70, "duration": 0.6},
                {"action": "scroll", "pixels": 240, "duration": 1.3}
            ]
        },
        {
            "name": "완벽추구형",
            "description": "완벽하게 이해하기 위해 반복 확인",
            "actions": [
                {"action": "scroll", "pixels": 150, "duration": 1.0},
                {"action": "pause", "duration": 2.8},
                {"action": "scroll_up", "pixels": 130, "duration": 0.9},
                {"action": "pause", "duration": 3.2},
                {"action": "scroll", "pixels": 250, "duration": 1.4},
                {"action": "pause", "duration": 2.5}
            ]
        }
    ],

    # 41-50: 특이 행동 패턴
    "특이_행동": [
        {
            "name": "불규칙형",
            "description": "완전히 불규칙한 스크롤 패턴",
            "actions": [
                {"action": "scroll", "pixels": 350, "duration": 0.7},
                {"action": "pause", "duration": 0.5},
                {"action": "scroll_up", "pixels": 200, "duration": 0.8},
                {"action": "pause", "duration": 3.0},
                {"action": "scroll", "pixels": 100, "duration": 0.4},
                {"action": "pause", "duration": 1.2},
                {"action": "scroll", "pixels": 400, "duration": 1.1}
            ]
        },
        {
            "name": "충동형",
            "description": "충동적으로 스크롤하는 패턴",
            "actions": [
                {"action": "scroll", "pixels": 500, "duration": 0.6},
                {"action": "pause", "duration": 0.3},
                {"action": "scroll_up", "pixels": 300, "duration": 0.9},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll", "pixels": 250, "duration": 0.8},
                {"action": "pause", "duration": 1.8}
            ]
        },
        {
            "name": "탐험형",
            "description": "페이지를 탐험하듯 이동",
            "actions": [
                {"action": "scroll", "pixels": 600, "duration": 1.2},
                {"action": "pause", "duration": 1.0},
                {"action": "scroll_up", "pixels": 400, "duration": 1.5},
                {"action": "pause", "duration": 2.0},
                {"action": "scroll", "pixels": 300, "duration": 0.8},
                {"action": "scroll", "pixels": 450, "duration": 1.0}
            ]
        },
        {
            "name": "휠_남용형",
            "description": "마우스 휠을 과도하게 사용",
            "actions": [
                {"action": "scroll", "pixels": 50, "duration": 0.2},
                {"action": "scroll", "pixels": 60, "duration": 0.2},
                {"action": "scroll", "pixels": 70, "duration": 0.3},
                {"action": "pause", "duration": 1.5},
                {"action": "scroll", "pixels": 80, "duration": 0.3},
                {"action": "scroll", "pixels": 90, "duration": 0.3},
                {"action": "pause", "duration": 2.0}
            ]
        },
        {
            "name": "페이지점프형",
            "description": "페이지를 크게 점프하며 이동",
            "actions": [
                {"action": "scroll", "pixels": 800, "duration": 1.0},
                {"action": "pause", "duration": 1.5},
                {"action": "scroll_up", "pixels": 600, "duration": 1.2},
                {"action": "pause", "duration": 2.5},
                {"action": "scroll", "pixels": 400, "duration": 0.8}
            ]
        },
        {
            "name": "지루함형",
            "description": "지루해서 빠르게 스크롤만 함",
            "actions": [
                {"action": "scroll", "pixels": 400, "duration": 0.5},
                {"action": "scroll", "pixels": 450, "duration": 0.6},
                {"action": "scroll", "pixels": 500, "duration": 0.7},
                {"action": "pause", "duration": 0.8},
                {"action": "scroll_up", "pixels": 200, "duration": 0.6}
            ]
        },
        {
            "name": "실수연발형",
            "description": "실수로 잘못 스크롤하고 다시 돌아가기",
            "actions": [
                {"action": "scroll", "pixels": 300, "duration": 0.6},
                {"action": "scroll_up", "pixels": 350, "duration": 0.8},
                {"action": "pause", "duration": 1.0},
                {"action": "scroll", "pixels": 200, "duration": 0.7},
                {"action": "pause", "duration": 1.8},
                {"action": "scroll", "pixels": 180, "duration": 0.9}
            ]
        },
        {
            "name": "주의산만형",
            "description": "주의가 산만해서 이곳저곳 보기",
            "actions": [
                {"action": "scroll", "pixels": 150, "duration": 0.8},
                {"action": "pause", "duration": 0.5},
                {"action": "scroll", "pixels": 300, "duration": 0.6},
                {"action": "scroll_up", "pixels": 100, "duration": 0.4},
                {"action": "pause", "duration": 2.2},
                {"action": "scroll", "pixels": 250, "duration": 0.9}
            ]
        },
        {
            "name": "테스트형",
            "description": "스크롤이 제대로 되는지 테스트",
            "actions": [
                {"action": "scroll", "pixels": 100, "duration": 0.5},
                {"action": "scroll_up", "pixels": 100, "duration": 0.5},
                {"action": "scroll", "pixels": 200, "duration": 0.7},
                {"action": "scroll_up", "pixels": 50, "duration": 0.4},
                {"action": "scroll", "pixels": 300, "duration": 1.0},
                {"action": "pause", "duration": 2.0}
            ]
        },
        {
            "name": "즉흥형",
            "description": "즉흥적이고 예측 불가능한 패턴",
            "actions": [
                {"action": "scroll", "pixels": 280, "duration": 0.9},
                {"action": "pause", "duration": 0.3},
                {"action": "scroll_up", "pixels": 150, "duration": 1.2},
                {"action": "pause", "duration": 4.0},
                {"action": "scroll", "pixels": 420, "duration": 0.6},
                {"action": "pause", "duration": 1.1}
            ]
        }
    ]
}

# =============================================================================
# 스크롤 패턴 실행 함수 (개선된 버전)
# =============================================================================

def execute_scroll_pattern(driver, pattern):
    """선택된 패턴을 실제로 실행 (개선된 스크롤 로직 적용)"""
    print(f"🎭 실행 패턴: {pattern['name']} - {pattern['description']}")

    for action in pattern['actions']:
        try:
            action_type = action.get('action')
            
            if action_type in ['scroll', 'scroll_up']:
                pixels = action.get('pixels', 100)
                duration = action.get('duration', 1.0)
                
                # scroll_up일 경우 pixels를 음수로 변경
                if action_type == 'scroll_up':
                    pixels = -pixels

                # 부드러운 스크롤 애니메이션 구현
                start_time = time.time()
                end_time = start_time + duration
                
                total_scrolled = 0
                
                while time.time() < end_time:
                    elapsed_time = time.time() - start_time
                    # 간단한 ease-out 효과 (처음엔 빠르고 끝에 느려짐)
                    scroll_progress = elapsed_time / duration
                    ease_out_progress = 1 - (1 - scroll_progress) ** 2
                    
                    target_scroll = pixels * ease_out_progress
                    scroll_this_frame = target_scroll - total_scrolled
                    
                    driver.execute_script(f"window.scrollBy(0, {scroll_this_frame});")
                    total_scrolled += scroll_this_frame
                    
                    time.sleep(0.02) # 약 50fps를 위한 짧은 대기

                # 정확한 위치로 보정
                remaining_scroll = pixels - total_scrolled
                if abs(remaining_scroll) > 0:
                    driver.execute_script(f"window.scrollBy(0, {remaining_scroll});")

            elif action_type == 'pause':
                duration = action.get('duration', 1.0)
                print(f"   - ⏸️ {duration:.1f}초 동안 일시정지...")
                time.sleep(duration)

        except Exception as e:
            print(f"⚠️ 스크롤 액션 실행 실패: {e}")
            continue

    print(f"✅ 패턴 '{pattern['name']}' 실행 완료")

def get_random_scroll_pattern():
    """랜덤하게 스크롤 패턴을 선택"""
    category = random.choice(list(HUMAN_SCROLL_PATTERNS.keys()))
    pattern = random.choice(HUMAN_SCROLL_PATTERNS[category])
    return pattern

def get_pattern_by_type(pattern_type):
    """특정 타입의 패턴만 선택"""
    if pattern_type in HUMAN_SCROLL_PATTERNS:
        return random.choice(HUMAN_SCROLL_PATTERNS[pattern_type])
    else:
        return get_random_scroll_pattern()

def simulate_human_scroll(driver, scroll_type="random"):
    """인간의 스크롤 행동을 시뮬레이션"""
    if scroll_type == "random":
        pattern = get_random_scroll_pattern()
    else:
        pattern = get_pattern_by_type(scroll_type)
    
    execute_scroll_pattern(driver, pattern)
    return pattern['name']
