"""
🚀 통합 페이지네이션 크롤러
- 페이지네이션 기반 순위별 URL 수집
- 순위 정보와 크롤링 데이터 분리 저장
- CSV, 이미지, 랭킹의 연속성 보장
"""

import os
import time
from datetime import datetime
from .pagination_ranking_system import pagination_ranking_system, ranking_data_matcher, continuity_manager
from .crawler_engine import KlookCrawlerEngine
from .data_handler import save_to_csv_klook, create_product_data_structure

class IntegratedPaginationCrawler:
    """통합 페이지네이션 크롤러"""
    
    def __init__(self, driver):
        self.driver = driver
        self.crawler_engine = KlookCrawlerEngine(driver)
        self.stats = {
            'urls_collected': 0,
            'products_crawled': 0,
            'pages_processed': 0,
            'ranking_continuity_maintained': True
        }
    
    def execute_pagination_crawling(self, city_name, target_count=15, max_pages=5):
        """페이지네이션 기반 전체 크롤링 실행"""
        print(f"🚀 '{city_name}' 페이지네이션 크롤링 시작")
        print("=" * 60)
        print(f"🎯 설정: {target_count}개 상품, 최대 {max_pages}페이지")
        
        start_time = time.time()
        
        try:
            # 1단계: 연속성 검사
            print(f"\n1️⃣ 연속성 검사")
            print("-" * 30)
            continuity_check = continuity_manager.ensure_continuity_consistency(city_name)
            
            if continuity_check and not continuity_check['consistent']:
                print(f"⚠️ 연속성 문제 발견 - 권장 시작 번호: {continuity_check['recommended_next']}")
                start_number = continuity_check['recommended_next']
            else:
                start_number = continuity_check['next_number'] if continuity_check else 1
            
            # 2단계: 페이지네이션 URL 수집
            print(f"\n2️⃣ 페이지네이션 URL 수집")
            print("-" * 30)
            collected_urls = pagination_ranking_system.collect_urls_with_pagination(
                self.driver, city_name, target_count, max_pages
            )
            
            if not collected_urls:
                print("❌ URL 수집 실패")
                return False
            
            self.stats['urls_collected'] = len(collected_urls)
            self.stats['pages_processed'] = max(url_data['page'] for url_data in collected_urls)
            
            # 3단계: 순위별 크롤링 실행
            print(f"\n3️⃣ 순위별 상품 크롤링")
            print("-" * 30)
            success_count = self._crawl_products_by_ranking(collected_urls, city_name, start_number)
            
            self.stats['products_crawled'] = success_count
            
            # 4단계: 랭킹-CSV 매핑 테이블 생성
            print(f"\n4️⃣ 랭킹-CSV 매핑 생성")
            print("-" * 30)
            mapping_file = ranking_data_matcher.create_ranking_csv_mapping(city_name)
            
            # 5단계: 최종 결과
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n✅ 페이지네이션 크롤링 완료!")
            print("=" * 60)
            print(f"📊 최종 결과:")
            print(f"   🔗 수집된 URL: {self.stats['urls_collected']}개")
            print(f"   📄 처리된 페이지: {self.stats['pages_processed']}페이지")
            print(f"   ✅ 크롤링 성공: {self.stats['products_crawled']}개")
            print(f"   🏆 순위 범위: 1위 ~ {len(collected_urls)}위")
            print(f"   ⏱️ 소요 시간: {int(total_time//60)}분 {int(total_time%60)}초")
            print(f"   🔗 매핑 파일: {mapping_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 페이지네이션 크롤링 실패: {e}")
            return False
    
    def _crawl_products_by_ranking(self, collected_urls, city_name, start_number):
        """순위별 상품 크롤링"""
        success_count = 0
        current_csv_number = start_number
        
        print(f"📊 {len(collected_urls)}개 URL 순위별 크롤링 시작 (CSV 번호: {start_number}부터)")
        
        for idx, url_data in enumerate(collected_urls, 1):
            url = url_data['url']
            global_rank = url_data['global_rank']
            page = url_data['page']
            
            print(f"\n📊 진행률: {idx}/{len(collected_urls)} | {global_rank}위 (페이지{page})")
            print(f"🔗 URL: {url[:60]}...")
            
            try:
                # 상품 페이지 이동
                self.driver.get(url)
                time.sleep(3)
                
                # 상품 정보 추출
                result = self.crawler_engine._extract_product_info(url, city_name, current_csv_number)
                
                if result:
                    # 랭킹 정보 추가
                    result['탭명'] = '전체'
                    result['탭내_랭킹'] = global_rank
                    result['페이지'] = page
                    result['CSV_번호'] = current_csv_number
                    
                    # 추가 메타데이터
                    result['페이지네이션_정보'] = {
                        'page': page,
                        'page_position': url_data['page_position'],
                        'collection_method': 'pagination_ranking'
                    }
                    
                    # CSV 저장
                    save_success = save_to_csv_klook(result, city_name)
                    
                    if save_success:
                        print(f"   ✅ 성공: {result.get('상품명', 'N/A')[:30]}... (CSV#{current_csv_number})")
                        success_count += 1
                        current_csv_number += 1
                        
                        # 랭킹 매니저에 크롤링 완료 표시
                        try:
                            from .ranking_manager import ranking_manager
                            ranking_manager.mark_url_crawled(url, city_name)
                        except:
                            pass
                    else:
                        print(f"   ❌ CSV 저장 실패")
                else:
                    print(f"   ❌ 상품 정보 추출 실패")
                
                # 자연스러운 대기
                time.sleep(2)
                
            except Exception as e:
                print(f"   💥 크롤링 오류: {e}")
                continue
        
        print(f"\n📊 순위별 크롤링 완료: {success_count}/{len(collected_urls)}개 성공")
        return success_count

class PaginationCrawlingValidator:
    """페이지네이션 크롤링 검증자"""
    
    def validate_ranking_continuity(self, city_name):
        """순위 연속성 검증"""
        print(f"🔍 '{city_name}' 순위 연속성 검증")
        print("-" * 40)
        
        try:
            from .config import get_city_code
            city_code = get_city_code(city_name)
            
            # 누적 랭킹 데이터 로드
            accumulated_file = f"ranking_data/{city_code}_accumulated_rankings.json"
            if not os.path.exists(accumulated_file):
                print("❌ 랭킹 데이터 파일이 없습니다")
                return False
            
            import json
            with open(accumulated_file, 'r', encoding='utf-8') as f:
                ranking_data = json.load(f)
            
            # 전체 탭 순위 추출
            rankings = []
            for url_hash, url_info in ranking_data["url_rankings"].items():
                tab_rankings = url_info.get("tab_rankings", {})
                if "전체" in tab_rankings:
                    rank = tab_rankings["전체"]["ranking"]
                    rankings.append({
                        'rank': rank,
                        'url': url_info["url"],
                        'page_info': url_info.get("pagination_info", {})
                    })
            
            # 순위별 정렬
            rankings.sort(key=lambda x: x['rank'])
            
            # 연속성 검사
            issues = []
            for i in range(1, len(rankings)):
                current_rank = rankings[i]['rank']
                previous_rank = rankings[i-1]['rank']
                
                if current_rank != previous_rank + 1:
                    issues.append({
                        'position': i,
                        'expected': previous_rank + 1,
                        'actual': current_rank,
                        'gap': current_rank - previous_rank - 1
                    })
            
            if issues:
                print(f"⚠️ 순위 연속성 문제: {len(issues)}개")
                for issue in issues[:3]:  # 상위 3개만 표시
                    print(f"   위치 {issue['position']}: 예상 {issue['expected']}위 → 실제 {issue['actual']}위 (갭: {issue['gap']})")
            else:
                print("✅ 순위 연속성 완벽")
            
            print(f"📊 검증 결과: {len(rankings)}개 순위, {len(issues)}개 불연속")
            return len(issues) == 0
            
        except Exception as e:
            print(f"❌ 순위 연속성 검증 실패: {e}")
            return False
    
    def validate_data_consistency(self, city_name):
        """데이터 일관성 검증"""
        print(f"\n🔍 '{city_name}' 데이터 일관성 검증")
        print("-" * 40)
        
        try:
            from .config import get_city_code, get_city_info
            city_code = get_city_code(city_name)
            continent, country = get_city_info(city_name)
            
            # 랭킹 데이터에서 URL 목록
            ranking_urls = set()
            accumulated_file = f"ranking_data/{city_code}_accumulated_rankings.json"
            
            if os.path.exists(accumulated_file):
                import json
                with open(accumulated_file, 'r', encoding='utf-8') as f:
                    ranking_data = json.load(f)
                
                for url_info in ranking_data["url_rankings"].values():
                    if url_info.get("crawled", False):
                        ranking_urls.add(url_info["url"])
            
            # CSV에서 URL 목록
            csv_urls = set()
            csv_path = f"data/{continent}/{country}/{country}_klook_products_all.csv"
            
            if os.path.exists(csv_path):
                with open(csv_path, 'r', encoding='utf-8-sig') as f:
                    header = f.readline()
                    columns = header.strip().split(',')
                    
                    url_idx = None
                    for i, col in enumerate(columns):
                        if 'URL' in col:
                            url_idx = i
                            break
                    
                    if url_idx is not None:
                        for line in f:
                            parts = line.strip().split(',')
                            if len(parts) > url_idx:
                                url = parts[url_idx].strip('"')
                                csv_urls.add(url)
            
            # 일관성 분석
            common_urls = ranking_urls & csv_urls
            ranking_only = ranking_urls - csv_urls
            csv_only = csv_urls - ranking_urls
            
            print(f"📊 데이터 일관성 결과:")
            print(f"   🏆 랭킹 크롤링 완료: {len(ranking_urls)}개")
            print(f"   📋 CSV 저장됨: {len(csv_urls)}개")
            print(f"   ✅ 일치하는 URL: {len(common_urls)}개")
            
            if ranking_only:
                print(f"   ⚠️ 크롤링했지만 CSV 없음: {len(ranking_only)}개")
            
            if csv_only:
                print(f"   ⚠️ CSV에만 있고 랭킹 없음: {len(csv_only)}개")
            
            consistency_rate = len(common_urls) / max(len(ranking_urls), 1) * 100
            print(f"   📈 일관성 비율: {consistency_rate:.1f}%")
            
            return consistency_rate >= 90
            
        except Exception as e:
            print(f"❌ 데이터 일관성 검증 실패: {e}")
            return False
    
    def generate_pagination_report(self, city_name):
        """페이지네이션 크롤링 리포트 생성"""
        print(f"\n📋 '{city_name}' 페이지네이션 리포트 생성")
        print("-" * 40)
        
        try:
            ranking_continuity = self.validate_ranking_continuity(city_name)
            data_consistency = self.validate_data_consistency(city_name)
            
            report = {
                "city_name": city_name,
                "report_generated": datetime.now().isoformat(),
                "validation_results": {
                    "ranking_continuity": ranking_continuity,
                    "data_consistency": data_consistency,
                    "overall_status": "success" if ranking_continuity and data_consistency else "warning"
                },
                "recommendations": []
            }
            
            # 권장사항 생성
            if not ranking_continuity:
                report["recommendations"].append("순위 연속성 문제 해결 필요")
            
            if not data_consistency:
                report["recommendations"].append("랭킹-CSV 데이터 일관성 개선 필요")
            
            if ranking_continuity and data_consistency:
                report["recommendations"].append("시스템 상태 우수 - 추가 개선사항 없음")
            
            # 리포트 저장
            os.makedirs("reports", exist_ok=True)
            report_file = f"reports/pagination_report_{city_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 리포트 생성 완료: {report_file}")
            print(f"   📊 순위 연속성: {'✅ 양호' if ranking_continuity else '⚠️ 문제'}")
            print(f"   📊 데이터 일관성: {'✅ 양호' if data_consistency else '⚠️ 문제'}")
            
            return report_file
            
        except Exception as e:
            print(f"❌ 리포트 생성 실패: {e}")
            return None

# 전역 인스턴스
pagination_crawler_validator = PaginationCrawlingValidator()

print("✅ 통합 페이지네이션 크롤러 로드 완료!")
print("   🚀 기능:")
print("   - execute_pagination_crawling(): 페이지네이션 전체 크롤링")
print("   - validate_ranking_continuity(): 순위 연속성 검증")
print("   - validate_data_consistency(): 데이터 일관성 검증")
print("   - generate_pagination_report(): 종합 리포트 생성")