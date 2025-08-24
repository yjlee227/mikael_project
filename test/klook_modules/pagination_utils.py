"""
🔄 KLOOK 페이지네이션 유틸리티 모듈
- 테스트 검증된 고급 페이지네이션 로직
- 중복 코드 제거 및 통합 관리
- KLOOK 전용 셀렉터 및 최적화된 로직 포함

작성일: 2024-08-24
기반: 테스트 셀에서 검증된 성공 로직
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class KlookPageTool:
    """
    KLOOK 페이지 도구
    - 테스트에서 검증된 KLOOK 전용 페이지네이션 로직
    - 중복 코드 통합 및 재사용성 확보
    - 부드러운 스크롤, 화살표 클릭, 페이지 정보 수집 통합
    """
    
    def __init__(self, driver, wait_timeout=10):
        """
        초기화
        
        Args:
            driver: Selenium WebDriver 인스턴스
            wait_timeout: 대기 시간 (초, 기본값: 10)
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        
        # KLOOK 전용 페이지네이션 셀렉터들 (테스트 검증됨)
        self.arrow_selectors = [
            # KLOOK 전용 셀렉터 (가장 우선)
            ".klk-pagination-next-btn:not(.klk-pagination-next-btn-disabled)",
            "button:not(.klk-pagination-next-btn-disabled)[class*='pagination-next']",
            
            # 원본 코드의 XPath 패턴들
            "//button[contains(@aria-label, '다음')]",
            "//button[contains(text(), '다음')]", 
            "//a[contains(@aria-label, '다음')]",
            "//a[contains(text(), '다음')]",
            "//button[contains(@class, 'next')]",
            "//a[contains(@class, 'next')]",
            
            # CSS 셀렉터 버전
            "button[aria-label*='다음']:not([disabled])",
            "button[class*='next']:not([disabled])",
            "a[aria-label*='다음']",
            "a[class*='next']",
            ".pagination .next",
            ".pager .next",
            
            # 페이지 번호 기반
            ".pagination button:not([disabled]):last-child",
            ".pager a:not([disabled]):last-child",
            
            # 기타 패턴
            "button[title*='다음']:not([disabled])",
            "button[data-testid*='next']:not([disabled])",
            "nav[role='navigation'] button:last-child:not([disabled])"
        ]
    
    def smooth_scroll_to_pagination(self):
        """
        페이지네이션을 찾기 위해 부드럽게 아래로 스크롤
        테스트에서 검증된 300px씩 부드러운 스크롤 로직
        
        Returns:
            bool: 페이지네이션 요소 발견 여부
        """
        print("🔽 페이지네이션 영역 찾기 위한 부드러운 스크롤...")
        
        try:
            current_position = self.driver.execute_script("return window.pageYOffset")
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # 300px씩 부드럽게 스크롤
            for scroll_to in range(int(current_position), int(page_height), 300):
                self.driver.execute_script(f"window.scrollTo({{top: {scroll_to}, behavior: 'smooth'}});")
                time.sleep(0.5)
                
                # 페이지네이션 요소가 보이는지 확인
                try:
                    pagination = self.driver.find_element(By.CSS_SELECTOR, 
                                                       "button[aria-label*='next'], .pagination, [class*='page']")
                    if pagination.is_displayed():
                        print("    ✅ 페이지네이션 영역 발견!")
                        return True
                except:
                    continue
            
            print("    ✅ 부드러운 스크롤 완료")
            return False
            
        except Exception as e:
            print(f"    ⚠️ 스크롤 중 오류: {e}")
            return False
    
    def is_last_page(self):
        """
        마지막 페이지 여부 확인 (KLOOK 전용 로직)
        
        Returns:
            bool: True if 마지막 페이지, False if 다음 페이지 존재
        """
        try:
            # KLOOK 전용 disabled 버튼 체크
            disabled_button = self.driver.find_element(By.CSS_SELECTOR, 
                                                     ".klk-pagination-next-btn-disabled")
            print("    🏁 마지막 페이지입니다 (KLOOK disabled 버튼 발견)")
            return True
        except:
            print("    ✅ KLOOK disabled 버튼 없음 - 다음 페이지 가능")
            return False
    
    def click_next_page(self, current_url):
        """
        고급 다음 페이지 클릭 (테스트에서 검증된 로직)
        
        Args:
            current_url: 현재 페이지 URL (페이지 변화 확인용)
            
        Returns:
            dict: {
                'success': bool,
                'method': str ('click' or 'url_change'),
                'new_url': str,
                'selector_used': str
            }
        """
        print("➡️ 다음 페이지로 이동 시도...")
        
        # 1단계: 마지막 페이지 체크
        if self.is_last_page():
            return {
                'success': False,
                'method': 'last_page',
                'new_url': current_url,
                'selector_used': '.klk-pagination-next-btn-disabled'
            }
        
        # 2단계: 화살표 버튼 찾기 및 클릭 시도
        for selector in self.arrow_selectors:
            try:
                # XPath와 CSS 셀렉터 구분 처리
                if selector.startswith('//'):
                    arrow_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    arrow_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))

                print(f"✅ 화살표 버튼 발견: {selector}")

                # 스크롤하여 버튼이 보이도록 함
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", arrow_button)
                time.sleep(1)

                # 화살표 클릭
                self.driver.execute_script("arguments[0].click();", arrow_button)
                print("🖱️ 화살표 클릭 실행!")

                # 3단계: 클릭 후 페이지 변화 확인
                time.sleep(2)
                new_url = self.driver.current_url
                if 'page=' in new_url or new_url != current_url:
                    print("✅ 페이지 이동 확인됨!")
                    return {
                        'success': True,
                        'method': 'click',
                        'new_url': new_url,
                        'selector_used': selector
                    }
                else:
                    print("⚠️ 클릭했으나 페이지 변화 없음, 다음 셀렉터 시도...")

            except Exception as e:
                print(f"   선택자 {selector} 실패: {e}")
                continue
        
        # 4단계: 모든 클릭 시도 실패시 URL 직접 변경
        print("❌ 화살표 클릭 실패. URL 직접 변경으로 다음 페이지 이동")
        
        try:
            if '?' in current_url:
                next_page_url = current_url + "&page=2" if 'page=' not in current_url else current_url.replace('page=1', 'page=2')
            else:
                next_page_url = current_url + "?page=2"

            self.driver.get(next_page_url)
            print(f"🔄 대안 URL로 이동: {next_page_url}")
            
            return {
                'success': True,
                'method': 'url_change',
                'new_url': next_page_url,
                'selector_used': 'direct_url'
            }
            
        except Exception as e:
            print(f"❌ URL 직접 변경도 실패: {e}")
            return {
                'success': False,
                'method': 'failed',
                'new_url': current_url,
                'selector_used': 'none'
            }
    
    def verify_page_change(self, old_url, expected_change=None):
        """
        페이지 이동 확인
        
        Args:
            old_url: 이전 페이지 URL
            expected_change: 예상되는 변화 (예: 'page=2')
            
        Returns:
            dict: {
                'changed': bool,
                'old_url': str,
                'new_url': str,
                'change_detected': str
            }
        """
        current_url = self.driver.current_url
        changed = current_url != old_url
        
        change_type = 'none'
        if changed:
            if 'page=' in current_url:
                change_type = 'page_parameter'
            elif current_url != old_url:
                change_type = 'url_different'
        
        return {
            'changed': changed,
            'old_url': old_url,
            'new_url': current_url,
            'change_detected': change_type
        }
    
    def get_pagination_info(self):
        """
        현재 페이지의 페이지네이션 정보 수집
        
        Returns:
            dict: 페이지네이션 관련 정보
        """
        try:
            # 현재 페이지 번호 찾기
            current_page = 1
            try:
                current_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".pagination .active, .pagination .current, [aria-current='page']")
                if current_elements:
                    current_text = current_elements[0].text.strip()
                    if current_text.isdigit():
                        current_page = int(current_text)
            except:
                pass
            
            # 전체 페이지 수 추정
            total_pages = current_page
            try:
                page_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".pagination button, .pagination a")
                for element in page_elements:
                    text = element.text.strip()
                    if text.isdigit():
                        page_num = int(text)
                        total_pages = max(total_pages, page_num)
            except:
                pass
            
            # 다음 페이지 존재 여부
            has_next = not self.is_last_page()
            
            return {
                'current_page': current_page,
                'total_pages': total_pages,
                'has_next_page': has_next,
                'is_last_page': not has_next
            }
            
        except Exception as e:
            print(f"⚠️ 페이지네이션 정보 수집 중 오류: {e}")
            return {
                'current_page': 1,
                'total_pages': 1,
                'has_next_page': False,
                'is_last_page': True
            }


# 편의 함수들 (기존 코드와의 호환성)
def create_klook_page_tool(driver, wait_timeout=10):
    """
    KlookPageTool 인스턴스 생성 편의 함수
    
    Args:
        driver: Selenium WebDriver
        wait_timeout: 대기 시간 (초)
    
    Returns:
        KlookPageTool: KLOOK 페이지 도구 인스턴스
    """
    return KlookPageTool(driver, wait_timeout)


def quick_next_page_click(driver, current_url):
    """
    빠른 다음 페이지 클릭 (기존 코드 호환용)
    
    Args:
        driver: Selenium WebDriver
        current_url: 현재 URL
        
    Returns:
        bool: 성공 여부
    """
    tool = KlookPageTool(driver)
    tool.smooth_scroll_to_pagination()
    result = tool.click_next_page(current_url)
    return result['success']


if __name__ == "__main__":
    print("🔄 KLOOK 페이지네이션 유틸리티 모듈")
    print("   ✅ KlookPageTool 클래스")
    print("   ✅ 테스트 검증된 KLOOK 전용 페이지네이션 로직")
    print("   ✅ 부드러운 스크롤 + 화살표 클릭 + 정보 수집")
    print("   ✅ 중복 코드 통합 관리")