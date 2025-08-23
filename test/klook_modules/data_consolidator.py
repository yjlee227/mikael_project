"""
📊 데이터 통합 관리 시스템
ranking_data, ranking_urls, url_collected, CSV를 논리적으로 연결하고 효율적으로 정리
"""

import os
import json
import pandas as pd
import hashlib
from datetime import datetime
from collections import defaultdict
from .config import get_city_code, get_city_info

class DataConsolidator:
    """데이터 통합 관리자"""
    
    def __init__(self):
        self.base_dirs = {
            'ranking_data': 'ranking_data',
            'ranking_urls': 'ranking_urls', 
            'url_collected': 'url_collected',
            'data': 'data'
        }
    
    def create_master_data_view(self, city_name):
        """🎯 핵심: 모든 데이터를 연결한 마스터 뷰 생성"""
        try:
            city_code = get_city_code(city_name)
            
            print(f"📊 '{city_name}' 마스터 데이터 뷰 생성 중...")
            
            # 1. ranking_data에서 핵심 정보 로드
            accumulated_file = f"{self.base_dirs['ranking_data']}/{city_code}_accumulated_rankings.json"
            if not os.path.exists(accumulated_file):
                print(f"❌ 누적 랭킹 데이터 없음: {accumulated_file}")
                return None
            
            with open(accumulated_file, 'r', encoding='utf-8') as f:
                ranking_data = json.load(f)
            
            # 2. CSV 데이터 로드 (있다면)
            csv_data = self._load_csv_data(city_name)
            
            # 3. url_collected 로그 로드
            collected_log = self._load_collected_log(city_code)
            
            # 4. 마스터 뷰 생성
            master_view = []
            
            for url_hash, url_info in ranking_data['url_rankings'].items():
                url = url_info['url']
                
                # 기본 정보
                row = {
                    'URL': url,
                    'URL_해시': url_hash,
                    'first_found': url_info.get('first_found'),
                    'is_duplicate': url_info.get('is_duplicate', False),
                    'crawled': url_info.get('crawled', False),
                    'crawled_at': url_info.get('crawled_at'),
                }
                
                # 탭별 순위 정보
                tab_rankings = url_info.get('tab_rankings', {})
                for tab_name, ranking_info in tab_rankings.items():
                    row[f'{tab_name}_순위'] = ranking_info['ranking']
                    row[f'{tab_name}_발견시간'] = ranking_info['found_at']
                
                # CSV 데이터와 매칭
                if csv_data is not None:
                    csv_match = csv_data[csv_data['URL'] == url]
                    if not csv_match.empty:
                        row['CSV_번호'] = csv_match.iloc[0]['번호']
                        row['상품명'] = csv_match.iloc[0]['상품명']
                        row['가격'] = csv_match.iloc[0]['가격_정제']
                        row['CSV_탭내랭킹'] = csv_match.iloc[0].get('탭내_랭킹')
                        row['has_csv_data'] = True
                    else:
                        row['has_csv_data'] = False
                else:
                    row['has_csv_data'] = False
                
                # 수집 로그와 매칭
                if url in collected_log:
                    row['collection_timestamp'] = collected_log[url]
                    row['was_collected'] = True
                else:
                    row['was_collected'] = False
                
                master_view.append(row)
            
            # DataFrame으로 변환
            df = pd.DataFrame(master_view)
            
            # 정렬 (첫 발견 시간순)
            df = df.sort_values('first_found')
            
            print(f"✅ 마스터 뷰 생성 완료: {len(df)}개 URL")
            return df
            
        except Exception as e:
            print(f"❌ 마스터 뷰 생성 실패: {e}")
            return None
    
    def _load_csv_data(self, city_name):
        """CSV 데이터 로드"""
        try:
            continent, country = get_city_info(city_name)
            
            # 여러 경로 시도
            csv_paths = []
            if city_name in ["마카오", "홍콩", "싱가포르"]:
                csv_paths = [
                    f"data/{continent}/{city_name}_klook_products_all.csv",
                    f"data/{continent}/klook_{city_name}_products.csv"
                ]
            else:
                csv_paths = [
                    f"data/{continent}/{country}/{city_name}/{city_name}_klook_products_all.csv",
                    f"data/{continent}/{country}/{city_name}/klook_{city_name}_products.csv",
                    f"data/{continent}/{country}/{country}_klook_products_all.csv"
                ]
            
            for csv_path in csv_paths:
                if os.path.exists(csv_path):
                    return pd.read_csv(csv_path, encoding='utf-8-sig')
            
            print(f"⚠️ CSV 파일 없음: {city_name}")
            return None
            
        except Exception as e:
            print(f"❌ CSV 로드 실패: {e}")
            return None
    
    def _load_collected_log(self, city_code):
        """수집 로그 로드"""
        try:
            log_file = f"{self.base_dirs['url_collected']}/{city_code}_url_log.txt"
            if not os.path.exists(log_file):
                return {}
            
            collected_log = {}
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '|' in line:
                        parts = line.strip().split(' | ')
                        if len(parts) == 2:
                            timestamp, url = parts
                            collected_log[url] = timestamp
            
            return collected_log
            
        except Exception as e:
            print(f"❌ 수집 로그 로드 실패: {e}")
            return {}
    
    def detect_data_inconsistencies(self, city_name):
        """🔍 데이터 불일치 감지"""
        print(f"🔍 '{city_name}' 데이터 정합성 검사...")
        
        master_df = self.create_master_data_view(city_name)
        if master_df is None:
            return
        
        issues = []
        
        # 1. 크롤링 완료했지만 CSV 데이터 없음
        crawled_no_csv = master_df[(master_df['crawled'] == True) & (master_df['has_csv_data'] == False)]
        if not crawled_no_csv.empty:
            issues.append({
                'type': 'crawled_but_no_csv',
                'count': len(crawled_no_csv),
                'description': '크롤링 완료했지만 CSV에 없는 URL들'
            })
        
        # 2. CSV에 있지만 ranking_data에 없음
        if 'has_csv_data' in master_df.columns:
            csv_no_ranking = master_df[(master_df['has_csv_data'] == True) & (master_df['URL_해시'].isna())]
            if not csv_no_ranking.empty:
                issues.append({
                    'type': 'csv_but_no_ranking',
                    'count': len(csv_no_ranking), 
                    'description': 'CSV에 있지만 랭킹 데이터에 없는 URL들'
                })
        
        # 3. 수집 로그와 크롤링 완료 상태 불일치
        log_crawl_mismatch = master_df[
            (master_df['was_collected'] == True) & (master_df['crawled'] == False)
        ]
        if not log_crawl_mismatch.empty:
            issues.append({
                'type': 'log_crawl_mismatch', 
                'count': len(log_crawl_mismatch),
                'description': '수집 로그에 있지만 크롤링 완료 표시되지 않은 URL들'
            })
        
        # 결과 출력
        if issues:
            print(f"⚠️ {len(issues)}개 데이터 불일치 발견:")
            for issue in issues:
                print(f"   - {issue['description']}: {issue['count']}개")
        else:
            print("✅ 데이터 정합성 양호")
        
        return issues, master_df
    
    def cleanup_redundant_files(self, city_name):
        """🧹 중복 파일 정리"""
        try:
            city_code = get_city_code(city_name)
            
            print(f"🧹 '{city_name}' 중복 파일 정리 중...")
            
            # ranking_urls 폴더의 중복 파일들 정리
            ranking_urls_dir = self.base_dirs['ranking_urls']
            if os.path.exists(ranking_urls_dir):
                files = [f for f in os.listdir(ranking_urls_dir) if f.startswith(city_code)]
                
                # 탭별로 그룹화
                tab_files = defaultdict(list)
                for file in files:
                    if '_' in file:
                        parts = file.split('_')
                        if len(parts) >= 3:
                            tab_name = parts[1]
                            tab_files[tab_name].append((file, os.path.getctime(
                                os.path.join(ranking_urls_dir, file)
                            )))
                
                # 각 탭에서 가장 최신 파일만 유지
                files_to_remove = []
                for tab_name, file_list in tab_files.items():
                    if len(file_list) > 1:
                        # 생성 시간 기준 정렬 (최신이 마지막)
                        file_list.sort(key=lambda x: x[1])
                        # 최신 파일을 제외한 나머지 삭제 대상
                        files_to_remove.extend([f[0] for f in file_list[:-1]])
                
                if files_to_remove:
                    print(f"   📁 ranking_urls: {len(files_to_remove)}개 중복 파일 발견")
                    for file in files_to_remove:
                        file_path = os.path.join(ranking_urls_dir, file)
                        backup_path = file_path + '.backup'
                        os.rename(file_path, backup_path)
                        print(f"      🔄 백업: {file} → {file}.backup")
                else:
                    print("   ✅ ranking_urls: 중복 파일 없음")
            
            # ranking_data 폴더의 개별 파일들 (accumulated가 있으면 불필요)
            ranking_data_dir = self.base_dirs['ranking_data']
            accumulated_file = f"{city_code}_accumulated_rankings.json"
            
            if os.path.exists(os.path.join(ranking_data_dir, accumulated_file)):
                individual_files = [
                    f for f in os.listdir(ranking_data_dir) 
                    if f.startswith(city_code) and f != accumulated_file and f.endswith('.json')
                ]
                
                if individual_files:
                    print(f"   📁 ranking_data: {len(individual_files)}개 개별 파일 발견")
                    for file in individual_files:
                        file_path = os.path.join(ranking_data_dir, file)
                        backup_path = file_path + '.backup'
                        os.rename(file_path, backup_path)
                        print(f"      🔄 백업: {file} → {file}.backup")
                else:
                    print("   ✅ ranking_data: 불필요한 개별 파일 없음")
            
            print("✅ 중복 파일 정리 완료")
            
        except Exception as e:
            print(f"❌ 파일 정리 실패: {e}")
    
    def create_unified_city_report(self, city_name):
        """📋 도시별 통합 리포트 생성"""
        try:
            print(f"📋 '{city_name}' 통합 리포트 생성 중...")
            
            # 마스터 뷰 생성
            master_df = self.create_master_data_view(city_name)
            if master_df is None:
                return
            
            # 데이터 불일치 검사
            issues, _ = self.detect_data_inconsistencies(city_name)
            
            # 리포트 생성
            report = {
                'city_name': city_name,
                'city_code': get_city_code(city_name),
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_urls': len(master_df),
                    'crawled_urls': len(master_df[master_df['crawled'] == True]),
                    'csv_data_urls': len(master_df[master_df['has_csv_data'] == True]),
                    'collected_log_urls': len(master_df[master_df['was_collected'] == True]),
                    'duplicate_urls': len(master_df[master_df['is_duplicate'] == True])
                },
                'tab_rankings': {},
                'data_issues': issues,
                'file_locations': {
                    'ranking_data': f"ranking_data/{get_city_code(city_name)}_accumulated_rankings.json",
                    'url_collected': f"url_collected/{get_city_code(city_name)}_url_log.txt",
                    'csv_data': "data/[continent]/[country]/[city]/"
                }
            }
            
            # 탭별 순위 통계
            tab_columns = [col for col in master_df.columns if col.endswith('_순위')]
            for col in tab_columns:
                tab_name = col.replace('_순위', '')
                valid_rankings = master_df[col].dropna()
                if not valid_rankings.empty:
                    report['tab_rankings'][tab_name] = {
                        'total_urls': len(valid_rankings),
                        'min_rank': int(valid_rankings.min()),
                        'max_rank': int(valid_rankings.max()),
                        'avg_rank': round(valid_rankings.mean(), 1)
                    }
            
            # 리포트 저장
            os.makedirs('reports', exist_ok=True)
            report_file = f"reports/{city_name}_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            # 마스터 뷰 CSV 저장
            master_csv = f"reports/{city_name}_master_view_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            master_df.to_csv(master_csv, index=False, encoding='utf-8-sig')
            
            print(f"✅ 리포트 생성 완료:")
            print(f"   📊 JSON 리포트: {report_file}")
            print(f"   📊 마스터 뷰: {master_csv}")
            
            # 요약 출력
            print(f"\n📈 '{city_name}' 데이터 요약:")
            print(f"   전체 URL: {report['summary']['total_urls']}개")
            print(f"   크롤링 완료: {report['summary']['crawled_urls']}개")
            print(f"   CSV 데이터: {report['summary']['csv_data_urls']}개")
            print(f"   수집 로그: {report['summary']['collected_log_urls']}개")
            print(f"   중복 URL: {report['summary']['duplicate_urls']}개")
            
            if report['tab_rankings']:
                print(f"   탭별 순위:")
                for tab_name, stats in report['tab_rankings'].items():
                    print(f"      {tab_name}: {stats['total_urls']}개 ({stats['min_rank']}-{stats['max_rank']}위)")
            
            return report_file, master_csv
            
        except Exception as e:
            print(f"❌ 리포트 생성 실패: {e}")
            return None, None

# 전역 인스턴스
data_consolidator = DataConsolidator()

print("✅ 데이터 통합 관리 시스템 로드 완료!")
print("   🎯 기능:")
print("   - create_master_data_view(): 모든 데이터 연결한 마스터 뷰")
print("   - detect_data_inconsistencies(): 데이터 불일치 감지")
print("   - cleanup_redundant_files(): 중복 파일 정리")
print("   - create_unified_city_report(): 통합 리포트 생성")