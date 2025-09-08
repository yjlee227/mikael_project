# KKday 크롤링 시스템 - 성능 모니터링 및 최적화 가이드

## 📊 성능 모니터링 개요

이 문서는 KKday 크롤링 시스템의 성능을 측정, 모니터링, 최적화하기 위한 완전한 가이드를 제공합니다. 실시간 성능 추적부터 병목 지점 해결까지 체계적인 접근 방법을 다룹니다.

## 🎯 성능 목표 및 KPI

### 핵심 성능 지표 (KPI)

#### 처리 성능 목표
```yaml
크롤링 속도:
  페이지_로딩: "3-5초/페이지"
  데이터_추출: "1-2초/상품"
  이미지_다운로드: "2-3초/이미지"
  전체_처리율: "10-15개 상품/분"

리소스 사용량:
  CPU_사용률: "<50% (평균)"  
  메모리_사용량: "<2GB (최대)"
  네트워크_대역폭: "<10MB/분"
  디스크_I/O: "<100MB/분"

안정성 지표:
  가동시간: ">99% (24시간 기준)"
  오류율: "<5% (전체 작업 대비)"
  재시도_성공률: ">90%"
  메모리_누수: "0MB/시간"
```

#### 품질 성능 목표
```yaml
데이터_정확성:
  필수_필드_추출률: ">95%"
  가격_정보_정확도: ">98%"
  이미지_다운로드_성공률: ">90%"
  중복_제거_정확도: ">99%"

사용성 지표:
  초기_설정시간: "<10분"
  평균_응답시간: "<3초"
  UI_반응속도: "<1초"
  로그_가독성: "상/중/하 평가"
```

## 📈 실시간 성능 모니터링 시스템

### 성능 메트릭 수집 클래스

#### 종합 성능 모니터 구현
```python
import time
import psutil
import threading
import logging
from collections import deque
from datetime import datetime, timedelta

class KKdayPerformanceMonitor:
    """KKday 크롤링 시스템 성능 모니터링 클래스"""
    
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.metrics = {
            'response_times': deque(maxlen=window_size),
            'memory_usage': deque(maxlen=window_size), 
            'cpu_usage': deque(maxlen=window_size),
            'success_count': 0,
            'error_count': 0,
            'start_time': time.time()
        }
        
        self.process = psutil.Process()
        self.monitoring = False
        self.monitor_thread = None
        
        # 성능 로거 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - 성능 - %(message)s',
            handlers=[
                logging.FileHandler('performance.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('performance')
    
    def start_monitoring(self, interval=5):
        """실시간 모니터링 시작"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_system_metrics,
            args=(interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.logger.info("🚀 성능 모니터링 시작")
    
    def stop_monitoring(self):
        """모니터링 중단"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("🛑 성능 모니터링 중단")
    
    def _monitor_system_metrics(self, interval):
        """시스템 메트릭 주기적 수집"""
        while self.monitoring:
            try:
                # CPU 사용률
                cpu_percent = psutil.cpu_percent()
                self.metrics['cpu_usage'].append(cpu_percent)
                
                # 메모리 사용량
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self.metrics['memory_usage'].append(memory_mb)
                
                # 임계값 체크
                if cpu_percent > 80:
                    self.logger.warning(f"⚠️ CPU 사용률 높음: {cpu_percent}%")
                
                if memory_mb > 1500:  # 1.5GB
                    self.logger.warning(f"⚠️ 메모리 사용량 높음: {memory_mb:.1f}MB")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"❌ 모니터링 오류: {e}")
                time.sleep(interval)
    
    def record_operation(self, operation_name, duration, success=True):
        """개별 작업 성능 기록"""
        self.metrics['response_times'].append({
            'operation': operation_name,
            'duration': duration,
            'timestamp': time.time(),
            'success': success
        })
        
        if success:
            self.metrics['success_count'] += 1
        else:
            self.metrics['error_count'] += 1
        
        # 성능 로깅
        status = "✅" if success else "❌"
        self.logger.info(f"{status} {operation_name}: {duration:.2f}초")
    
    def get_performance_summary(self):
        """성능 요약 리포트 생성"""
        current_time = time.time()
        uptime = current_time - self.metrics['start_time']
        
        # 응답시간 통계
        if self.metrics['response_times']:
            response_times = [r['duration'] for r in self.metrics['response_times']]
            avg_response = sum(response_times) / len(response_times)
            max_response = max(response_times)
            min_response = min(response_times)
        else:
            avg_response = max_response = min_response = 0
        
        # 메모리/CPU 통계
        if self.metrics['memory_usage']:
            avg_memory = sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage'])
            max_memory = max(self.metrics['memory_usage'])
        else:
            avg_memory = max_memory = 0
            
        if self.metrics['cpu_usage']:
            avg_cpu = sum(self.metrics['cpu_usage']) / len(self.metrics['cpu_usage'])
            max_cpu = max(self.metrics['cpu_usage'])
        else:
            avg_cpu = max_cpu = 0
        
        # 성공률 계산
        total_operations = self.metrics['success_count'] + self.metrics['error_count']
        success_rate = (self.metrics['success_count'] / max(total_operations, 1)) * 100
        
        summary = {
            'uptime_hours': uptime / 3600,
            'total_operations': total_operations,
            'success_rate': success_rate,
            'performance': {
                'avg_response_time': avg_response,
                'max_response_time': max_response,
                'min_response_time': min_response
            },
            'resources': {
                'avg_memory_mb': avg_memory,
                'max_memory_mb': max_memory,
                'avg_cpu_percent': avg_cpu,
                'max_cpu_percent': max_cpu
            }
        }
        
        return summary
    
    def generate_performance_report(self):
        """상세 성능 리포트 생성"""
        summary = self.get_performance_summary()
        
        report = f"""
# KKday 크롤링 시스템 성능 리포트

**생성 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**가동 시간**: {summary['uptime_hours']:.1f}시간
**총 작업 수**: {summary['total_operations']}개
**성공률**: {summary['success_rate']:.1f}%

## 📊 성능 지표

### 응답 시간
- **평균**: {summary['performance']['avg_response_time']:.2f}초
- **최대**: {summary['performance']['max_response_time']:.2f}초  
- **최소**: {summary['performance']['min_response_time']:.2f}초

### 리소스 사용량
- **평균 메모리**: {summary['resources']['avg_memory_mb']:.1f}MB
- **최대 메모리**: {summary['resources']['max_memory_mb']:.1f}MB
- **평균 CPU**: {summary['resources']['avg_cpu_percent']:.1f}%
- **최대 CPU**: {summary['resources']['max_cpu_percent']:.1f}%

## 📈 성능 평가

### 목표 달성도
"""
        
        # 목표 달성도 평가
        evaluations = self._evaluate_performance(summary)
        for category, result in evaluations.items():
            status = "✅" if result['passed'] else "❌"
            report += f"- **{category}**: {status} {result['message']}\n"
        
        report += f"""

## 🔍 권장사항
{self._generate_recommendations(summary)}
        """
        
        # 리포트 파일 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'performance_report_{timestamp}.md'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"📋 성능 리포트 생성: {filename}")
        return report
    
    def _evaluate_performance(self, summary):
        """성능 목표 달성도 평가"""
        evaluations = {}
        
        # 응답 시간 평가 (목표: 5초 이내)
        avg_response = summary['performance']['avg_response_time']
        if avg_response <= 5:
            evaluations['응답시간'] = {'passed': True, 'message': f'{avg_response:.2f}초 (목표: 5초)'}
        else:
            evaluations['응답시간'] = {'passed': False, 'message': f'{avg_response:.2f}초 초과 (목표: 5초)'}
        
        # 메모리 사용량 평가 (목표: 2GB 이내)
        max_memory = summary['resources']['max_memory_mb']
        if max_memory <= 2048:  # 2GB
            evaluations['메모리사용량'] = {'passed': True, 'message': f'{max_memory:.1f}MB (목표: 2GB)'}
        else:
            evaluations['메모리사용량'] = {'passed': False, 'message': f'{max_memory:.1f}MB 초과 (목표: 2GB)'}
        
        # 성공률 평가 (목표: 95% 이상)
        success_rate = summary['success_rate']
        if success_rate >= 95:
            evaluations['성공률'] = {'passed': True, 'message': f'{success_rate:.1f}% (목표: 95%)'}
        else:
            evaluations['성공률'] = {'passed': False, 'message': f'{success_rate:.1f}% 미달 (목표: 95%)'}
        
        return evaluations
    
    def _generate_recommendations(self, summary):
        """성능 개선 권장사항 생성"""
        recommendations = []
        
        # 응답 시간 개선
        if summary['performance']['avg_response_time'] > 5:
            recommendations.append("🚀 **응답 시간 개선**: 셀렉터 최적화 또는 대기시간 단축 검토")
        
        # 메모리 사용량 개선
        if summary['resources']['max_memory_mb'] > 1500:
            recommendations.append("💾 **메모리 최적화**: 가비지 컬렉션 주기 조정 또는 배치 크기 축소")
        
        # CPU 사용량 개선
        if summary['resources']['avg_cpu_percent'] > 50:
            recommendations.append("⚡ **CPU 최적화**: 병렬 처리 최적화 또는 대기시간 증가")
        
        # 성공률 개선
        if summary['success_rate'] < 95:
            recommendations.append("🎯 **안정성 개선**: 재시도 로직 강화 또는 오류 처리 개선")
        
        if not recommendations:
            recommendations.append("✨ **현재 성능 양호**: 모든 지표가 목표를 달성하고 있습니다")
        
        return '\n'.join(f"- {rec}" for rec in recommendations)


# 성능 모니터링 데코레이터
monitor = KKdayPerformanceMonitor()

def performance_track(operation_name):
    """성능 추적 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_operation(operation_name, duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_operation(operation_name, duration, success=False)
                raise e
        return wrapper
    return decorator
```

### 실시간 성능 대시보드

#### 콘솔 기반 실시간 모니터링
```python
import os
import time
from datetime import datetime

class KKdayPerformanceDashboard:
    """실시간 성능 대시보드"""
    
    def __init__(self, monitor):
        self.monitor = monitor
        self.running = False
    
    def start_dashboard(self, refresh_interval=5):
        """대시보드 시작"""
        self.running = True
        
        while self.running:
            try:
                self.clear_screen()
                self.display_dashboard()
                time.sleep(refresh_interval)
            except KeyboardInterrupt:
                self.running = False
                print("\n🛑 대시보드 종료")
    
    def clear_screen(self):
        """화면 지우기"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_dashboard(self):
        """대시보드 화면 출력"""
        summary = self.monitor.get_performance_summary()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        dashboard = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         KKday 크롤링 성능 모니터 v1.0                         ║
║                              {current_time}                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ 🚀 시스템 상태                                                                 ║
║   가동시간: {summary['uptime_hours']:.1f}시간                                  ║
║   총 작업: {summary['total_operations']}개                                     ║
║   성공률: {summary['success_rate']:.1f}%                                       ║
║                                                                              ║
║ ⚡ 성능 지표                                                                   ║
║   평균 응답시간: {summary['performance']['avg_response_time']:.2f}초             ║
║   최대 응답시간: {summary['performance']['max_response_time']:.2f}초             ║
║                                                                              ║
║ 💾 리소스 사용량                                                               ║
║   현재 메모리: {self.get_current_memory():.1f}MB                              ║
║   최대 메모리: {summary['resources']['max_memory_mb']:.1f}MB                   ║
║   현재 CPU: {self.get_current_cpu():.1f}%                                     ║
║   최대 CPU: {summary['resources']['max_cpu_percent']:.1f}%                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 최근 작업 기록:
{self.get_recent_operations()}

⚠️ 알림:
{self.get_alerts(summary)}

💡 Ctrl+C로 종료
        """
        
        print(dashboard)
    
    def get_current_memory(self):
        """현재 메모리 사용량 조회"""
        return self.monitor.process.memory_info().rss / 1024 / 1024
    
    def get_current_cpu(self):
        """현재 CPU 사용률 조회"""
        return psutil.cpu_percent()
    
    def get_recent_operations(self):
        """최근 작업 기록 조회"""
        recent_ops = list(self.monitor.metrics['response_times'])[-5:]  # 최근 5개
        if not recent_ops:
            return "  아직 작업 기록이 없습니다."
        
        operations = []
        for op in recent_ops:
            status = "✅" if op['success'] else "❌"
            timestamp = datetime.fromtimestamp(op['timestamp']).strftime('%H:%M:%S')
            operations.append(f"  {status} {timestamp} | {op['operation']} | {op['duration']:.2f}초")
        
        return '\n'.join(operations)
    
    def get_alerts(self, summary):
        """경고 알림 생성"""
        alerts = []
        
        if summary['resources']['avg_memory_mb'] > 1500:
            alerts.append("🔥 메모리 사용량이 높습니다")
        
        if summary['resources']['avg_cpu_percent'] > 70:
            alerts.append("🔥 CPU 사용률이 높습니다")
        
        if summary['performance']['avg_response_time'] > 10:
            alerts.append("🐌 응답 시간이 느립니다")
        
        if summary['success_rate'] < 90:
            alerts.append("⚠️ 성공률이 낮습니다")
        
        if not alerts:
            alerts.append("✨ 모든 지표가 정상 범위입니다")
        
        return '\n'.join(f"  {alert}" for alert in alerts)


# 사용 예시
def run_performance_monitoring():
    """성능 모니터링 실행"""
    
    # 모니터 시작
    monitor.start_monitoring(interval=5)
    
    # 대시보드 시작 (별도 스레드)
    dashboard = KKdayPerformanceDashboard(monitor)
    dashboard_thread = threading.Thread(target=dashboard.start_dashboard)
    dashboard_thread.daemon = True
    dashboard_thread.start()
    
    return monitor
```

## 🔧 성능 최적화 전략

### 메모리 최적화

#### 가비지 컬렉션 최적화
```python
import gc
import weakref
from collections import deque

class MemoryOptimizer:
    """메모리 사용량 최적화 도구"""
    
    def __init__(self):
        self.object_pool = deque(maxlen=1000)
        self.weak_refs = weakref.WeakSet()
        
    def optimize_memory_usage(self):
        """메모리 사용량 최적화 실행"""
        
        # 명시적 가비지 컬렉션
        collected = gc.collect()
        
        # 순환 참조 해제
        self._break_circular_references()
        
        # 객체 풀 정리
        self.object_pool.clear()
        
        return {
            'collected_objects': collected,
            'active_objects': len(gc.get_objects()),
            'memory_freed_mb': self._calculate_memory_freed()
        }
    
    def _break_circular_references(self):
        """순환 참조 해제"""
        # 약한 참조를 사용하여 순환 참조 방지
        for obj in list(self.weak_refs):
            if hasattr(obj, 'clear_references'):
                obj.clear_references()
    
    def _calculate_memory_freed(self):
        """해제된 메모리 계산"""
        # 실제 구현 시 psutil 사용
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        return max(0, self.last_memory - current_memory)
    
    @staticmethod
    def memory_efficient_batch_processing(data_list, batch_size=50):
        """메모리 효율적인 배치 처리"""
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            
            # 배치 처리
            yield batch
            
            # 배치 완료 후 메모리 정리
            del batch
            if i % (batch_size * 5) == 0:  # 5배치마다 GC
                gc.collect()


# 메모리 효율적인 크롤링 예시
def memory_efficient_crawling(urls, batch_size=20):
    """메모리 효율적인 대량 크롤링"""
    
    optimizer = MemoryOptimizer()
    
    for i, batch in enumerate(optimizer.memory_efficient_batch_processing(urls, batch_size)):
        print(f"🔄 배치 {i+1} 처리 중 ({len(batch)}개 URL)")
        
        # 배치별 크롤링 처리
        for url in batch:
            process_single_url(url)
        
        # 주기적 메모리 최적화
        if i % 5 == 0:  # 5배치마다
            result = optimizer.optimize_memory_usage()
            print(f"🧹 메모리 최적화: {result['collected_objects']}개 객체 해제")
```

### CPU 최적화

#### 비동기 처리 및 멀티프로세싱
```python
import asyncio
import aiohttp
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class CPUOptimizer:
    """CPU 사용량 최적화 도구"""
    
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.session = None
    
    async def async_crawl_urls(self, urls, max_concurrent=10):
        """비동기 URL 크롤링"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            tasks = [
                self.crawl_single_url_async(semaphore, url) 
                for url in urls
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
    
    async def crawl_single_url_async(self, semaphore, url):
        """단일 URL 비동기 크롤링"""
        
        async with semaphore:
            try:
                async with self.session.get(url) as response:
                    content = await response.text()
                    # 데이터 파싱 로직
                    return self.parse_content(content)
                    
            except Exception as e:
                return {'error': str(e), 'url': url}
    
    def multiprocess_crawling(self, urls, chunk_size=None):
        """멀티프로세싱 크롤링"""
        
        chunk_size = chunk_size or max(1, len(urls) // self.max_workers)
        url_chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.process_url_chunk, chunk) 
                for chunk in url_chunks
            ]
            
            results = []
            for future in futures:
                try:
                    chunk_results = future.result()
                    results.extend(chunk_results)
                except Exception as e:
                    print(f"❌ 청크 처리 실패: {e}")
            
            return results
    
    @staticmethod
    def process_url_chunk(url_chunk):
        """URL 청크 처리 (별도 프로세스)"""
        results = []
        
        for url in url_chunk:
            try:
                # 실제 크롤링 로직
                result = crawl_single_url_sync(url)
                results.append(result)
                
                # CPU 부하 조절
                time.sleep(0.1)
                
            except Exception as e:
                results.append({'error': str(e), 'url': url})
        
        return results


# 성능 최적화된 크롤링 실행
def optimized_crawling_execution(urls):
    """최적화된 크롤링 실행"""
    
    optimizer = CPUOptimizer()
    
    # URL 개수에 따른 최적 전략 선택
    if len(urls) < 50:
        # 소량: 일반 동기 처리
        results = [crawl_single_url_sync(url) for url in urls]
        
    elif len(urls) < 200:
        # 중량: 비동기 처리
        results = asyncio.run(optimizer.async_crawl_urls(urls))
        
    else:
        # 대량: 멀티프로세싱
        results = optimizer.multiprocess_crawling(urls)
    
    return results
```

### 네트워크 최적화

#### 연결 풀링 및 재시도 메커니즘
```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

class NetworkOptimizer:
    """네트워크 성능 최적화 도구"""
    
    def __init__(self):
        self.session = self._create_optimized_session()
    
    def _create_optimized_session(self):
        """최적화된 HTTP 세션 생성"""
        
        session = requests.Session()
        
        # 재시도 정책 설정
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1  # 1초, 2초, 4초 간격으로 재시도
        )
        
        # HTTP 어댑터 설정
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,  # 연결 풀 크기
            pool_maxsize=20       # 최대 연결 수
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 기본 헤더 설정
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def smart_request(self, url, **kwargs):
        """지능적 HTTP 요청"""
        
        start_time = time.time()
        
        try:
            response = self.session.get(url, timeout=(10, 30), **kwargs)
            response.raise_for_status()
            
            duration = time.time() - start_time
            
            # 성능 기록
            monitor.record_operation('http_request', duration, success=True)
            
            return response
            
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            monitor.record_operation('http_request', duration, success=False)
            
            # 오류 유형별 처리
            if isinstance(e, requests.exceptions.Timeout):
                print(f"⏰ 타임아웃: {url}")
            elif isinstance(e, requests.exceptions.ConnectionError):
                print(f"🔗 연결 오류: {url}")
            else:
                print(f"❌ HTTP 오류: {e}")
            
            raise e
    
    def adaptive_delay(self, response_time, error_count=0):
        """응답시간 기반 적응적 지연"""
        
        base_delay = 2.0  # 기본 2초
        
        # 응답시간에 따른 조정
        if response_time > 10:
            delay_factor = 2.0
        elif response_time > 5:
            delay_factor = 1.5
        else:
            delay_factor = 1.0
        
        # 오류 횟수에 따른 조정
        error_penalty = error_count * 0.5
        
        total_delay = base_delay * delay_factor + error_penalty
        
        # 최대 10초 제한
        final_delay = min(total_delay, 10.0)
        
        time.sleep(final_delay)
        return final_delay


# 최적화된 네트워크 크롤러
class OptimizedKKdayCrawler:
    """네트워크 최적화된 KKday 크롤러"""
    
    def __init__(self, city_name):
        self.city_name = city_name
        self.network_optimizer = NetworkOptimizer()
        self.error_count = 0
        self.last_request_time = 0
    
    def crawl_with_optimization(self, url):
        """최적화된 크롤링 수행"""
        
        # 적응적 지연 적용
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < 2:  # 최소 2초 간격
            time.sleep(2 - time_since_last)
        
        try:
            response = self.network_optimizer.smart_request(url)
            
            # 성공 시 오류 카운트 리셋
            self.error_count = 0
            self.last_request_time = time.time()
            
            return self.parse_response(response)
            
        except Exception as e:
            self.error_count += 1
            
            # 적응적 지연 적용
            delay = self.network_optimizer.adaptive_delay(
                response_time=5.0,  # 오류 시 가정값
                error_count=self.error_count
            )
            
            print(f"🔄 오류 후 {delay:.1f}초 대기")
            return None
```

## 📊 성능 벤치마킹

### 성능 테스트 스위트

#### 종합 성능 벤치마크
```python
import statistics
from datetime import datetime

class KKdayPerformanceBenchmark:
    """KKday 크롤링 시스템 성능 벤치마크"""
    
    def __init__(self):
        self.results = {}
    
    def run_comprehensive_benchmark(self):
        """종합 성능 벤치마크 실행"""
        
        print("🚀 KKday 크롤링 시스템 성능 벤치마크 시작")
        
        # 1. 단일 URL 성능 테스트
        self.results['single_url'] = self.benchmark_single_url()
        
        # 2. 배치 처리 성능 테스트  
        self.results['batch_processing'] = self.benchmark_batch_processing()
        
        # 3. 메모리 사용량 테스트
        self.results['memory_usage'] = self.benchmark_memory_usage()
        
        # 4. 동시 처리 성능 테스트
        self.results['concurrent_processing'] = self.benchmark_concurrent_processing()
        
        # 종합 리포트 생성
        return self.generate_benchmark_report()
    
    def benchmark_single_url(self, iterations=10):
        """단일 URL 처리 성능 테스트"""
        
        test_url = "https://www.kkday.com/ko/product/test"
        times = []
        
        print(f"📊 단일 URL 성능 테스트 ({iterations}회)")
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                # 실제 크롤링 시뮬레이션
                result = simulate_single_crawl(test_url)
                duration = time.time() - start_time
                times.append(duration)
                
                print(f"  테스트 {i+1}: {duration:.2f}초")
                
            except Exception as e:
                print(f"  테스트 {i+1}: 실패 - {e}")
        
        if times:
            return {
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
                'success_rate': len(times) / iterations * 100
            }
        else:
            return {'error': 'All tests failed'}
    
    def benchmark_batch_processing(self, batch_sizes=[10, 20, 50]):
        """배치 처리 성능 테스트"""
        
        results = {}
        
        for batch_size in batch_sizes:
            print(f"📊 배치 처리 테스트 (크기: {batch_size})")
            
            # 테스트 URL 생성
            test_urls = [f"https://www.kkday.com/ko/product/test{i}" 
                        for i in range(batch_size)]
            
            start_time = time.time()
            
            try:
                # 배치 크롤링 시뮬레이션
                batch_results = simulate_batch_crawl(test_urls)
                
                total_time = time.time() - start_time
                throughput = batch_size / total_time  # 개/초
                
                results[f'batch_{batch_size}'] = {
                    'total_time': total_time,
                    'throughput': throughput,
                    'avg_time_per_item': total_time / batch_size,
                    'success_count': len([r for r in batch_results if r])
                }
                
                print(f"  완료: {total_time:.2f}초 ({throughput:.2f}개/초)")
                
            except Exception as e:
                results[f'batch_{batch_size}'] = {'error': str(e)}
                print(f"  실패: {e}")
        
        return results
    
    def benchmark_memory_usage(self, duration=60):
        """메모리 사용량 벤치마크"""
        
        print(f"📊 메모리 사용량 테스트 ({duration}초)")
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        memory_samples = []
        start_time = time.time()
        
        # 지속적인 크롤링 시뮬레이션
        while time.time() - start_time < duration:
            # 크롤링 작업 시뮬레이션
            simulate_crawling_work()
            
            # 메모리 사용량 기록
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)
            
            time.sleep(1)  # 1초마다 측정
        
        final_memory = process.memory_info().rss / 1024 / 1024
        
        return {
            'initial_memory_mb': initial_memory,
            'final_memory_mb': final_memory,
            'max_memory_mb': max(memory_samples),
            'avg_memory_mb': statistics.mean(memory_samples),
            'memory_growth_mb': final_memory - initial_memory,
            'memory_samples': len(memory_samples)
        }
    
    def benchmark_concurrent_processing(self, concurrent_levels=[1, 5, 10]):
        """동시 처리 성능 벤치마크"""
        
        results = {}
        
        for level in concurrent_levels:
            print(f"📊 동시 처리 테스트 (동시성: {level})")
            
            start_time = time.time()
            
            try:
                # 동시 처리 시뮬레이션
                concurrent_results = simulate_concurrent_crawling(level)
                
                total_time = time.time() - start_time
                
                results[f'concurrent_{level}'] = {
                    'total_time': total_time,
                    'requests_per_second': level / total_time * len(concurrent_results),
                    'success_rate': sum(1 for r in concurrent_results if r) / len(concurrent_results) * 100
                }
                
                print(f"  완료: {total_time:.2f}초")
                
            except Exception as e:
                results[f'concurrent_{level}'] = {'error': str(e)}
                print(f"  실패: {e}")
        
        return results
    
    def generate_benchmark_report(self):
        """벤치마크 결과 리포트 생성"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# KKday 크롤링 시스템 성능 벤치마크 리포트

**실행 시간**: {timestamp}
**시스템 사양**: {psutil.cpu_count()}코어, {psutil.virtual_memory().total / 1024**3:.1f}GB RAM

## 📊 성능 테스트 결과

### 1. 단일 URL 처리 성능
"""
        
        if 'single_url' in self.results and 'avg_time' in self.results['single_url']:
            single = self.results['single_url']
            report += f"""
- **평균 처리시간**: {single['avg_time']:.2f}초
- **최소 처리시간**: {single['min_time']:.2f}초  
- **최대 처리시간**: {single['max_time']:.2f}초
- **표준편차**: {single['std_dev']:.2f}초
- **성공률**: {single['success_rate']:.1f}%
"""
        
        report += "\n### 2. 배치 처리 성능\n"
        
        if 'batch_processing' in self.results:
            for batch_name, batch_data in self.results['batch_processing'].items():
                if 'throughput' in batch_data:
                    report += f"""
- **{batch_name}**: {batch_data['throughput']:.2f}개/초 (총 {batch_data['total_time']:.2f}초)
"""
        
        report += "\n### 3. 메모리 사용량\n"
        
        if 'memory_usage' in self.results:
            memory = self.results['memory_usage']
            if 'avg_memory_mb' in memory:
                report += f"""
- **초기 메모리**: {memory['initial_memory_mb']:.1f}MB
- **최종 메모리**: {memory['final_memory_mb']:.1f}MB
- **최대 메모리**: {memory['max_memory_mb']:.1f}MB
- **평균 메모리**: {memory['avg_memory_mb']:.1f}MB
- **메모리 증가량**: {memory['memory_growth_mb']:.1f}MB
"""
        
        # 성능 점수 계산
        score = self.calculate_performance_score()
        report += f"\n## 🏆 종합 성능 점수: {score}/100\n"
        
        # 리포트 파일 저장
        filename = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📋 벤치마크 리포트 생성: {filename}")
        return report
    
    def calculate_performance_score(self):
        """종합 성능 점수 계산"""
        score = 100
        
        # 응답시간 점수 (40점)
        if 'single_url' in self.results and 'avg_time' in self.results['single_url']:
            avg_time = self.results['single_url']['avg_time']
            if avg_time <= 3:
                time_score = 40
            elif avg_time <= 5:
                time_score = 30
            elif avg_time <= 10:
                time_score = 20
            else:
                time_score = 10
        else:
            time_score = 0
        
        # 메모리 점수 (30점)
        if 'memory_usage' in self.results and 'max_memory_mb' in self.results['memory_usage']:
            max_memory = self.results['memory_usage']['max_memory_mb']
            if max_memory <= 1000:  # 1GB 이하
                memory_score = 30
            elif max_memory <= 2000:  # 2GB 이하
                memory_score = 20
            else:
                memory_score = 10
        else:
            memory_score = 0
        
        # 처리량 점수 (30점)
        throughput_score = 30  # 기본값
        if 'batch_processing' in self.results:
            # 배치 처리 결과에서 최고 처리량 확인
            max_throughput = 0
            for batch_data in self.results['batch_processing'].values():
                if isinstance(batch_data, dict) and 'throughput' in batch_data:
                    max_throughput = max(max_throughput, batch_data['throughput'])
            
            if max_throughput >= 1.0:  # 1개/초 이상
                throughput_score = 30
            elif max_throughput >= 0.5:  # 0.5개/초 이상
                throughput_score = 20
            else:
                throughput_score = 10
        
        final_score = min(100, time_score + memory_score + throughput_score)
        return final_score


# 벤치마크 실행 함수들 (시뮬레이션)
def simulate_single_crawl(url):
    """단일 크롤링 시뮬레이션"""
    time.sleep(random.uniform(2, 5))  # 2-5초 시뮬레이션
    return {"url": url, "data": "mock_data"}

def simulate_batch_crawl(urls):
    """배치 크롤링 시뮬레이션"""  
    results = []
    for url in urls:
        time.sleep(random.uniform(1, 3))  # 개별 처리 시간
        results.append(simulate_single_crawl(url))
    return results

def simulate_crawling_work():
    """크롤링 작업 시뮬레이션"""
    # 메모리 사용 시뮬레이션
    data = [i for i in range(1000)]  # 임시 데이터 생성
    time.sleep(0.5)
    del data

def simulate_concurrent_crawling(concurrent_level):
    """동시 처리 시뮬레이션"""
    results = []
    for i in range(concurrent_level * 2):  # 각 레벨당 2개씩 처리
        time.sleep(random.uniform(0.5, 2))
        results.append(True if random.random() > 0.1 else False)  # 90% 성공률
    return results
```

## 🎛️ 성능 튜닝 가이드

### 자동 성능 튜닝

#### 적응형 성능 조정기
```python
class AdaptivePerformanceTuner:
    """적응형 성능 조정 시스템"""
    
    def __init__(self):
        self.settings = {
            'batch_size': 20,
            'delay_time': 3.0,
            'max_workers': 4,
            'memory_threshold': 1500,  # MB
            'cpu_threshold': 70        # %
        }
        
        self.performance_history = deque(maxlen=50)
        self.adjustment_history = []
    
    def auto_tune_performance(self, current_metrics):
        """현재 메트릭을 기반으로 성능 자동 조정"""
        
        adjustments = []
        
        # 메모리 사용량 기반 조정
        if current_metrics['memory_mb'] > self.settings['memory_threshold']:
            # 배치 크기 축소
            old_batch = self.settings['batch_size']
            self.settings['batch_size'] = max(5, old_batch - 5)
            adjustments.append(f"배치크기 {old_batch} → {self.settings['batch_size']}")
        
        # CPU 사용률 기반 조정
        if current_metrics['cpu_percent'] > self.settings['cpu_threshold']:
            # 대기시간 증가
            old_delay = self.settings['delay_time']
            self.settings['delay_time'] = min(10.0, old_delay + 0.5)
            adjustments.append(f"대기시간 {old_delay} → {self.settings['delay_time']}초")
        
        # 응답시간 기반 조정
        if current_metrics['response_time'] > 10:
            # 워커 수 감소
            old_workers = self.settings['max_workers']
            self.settings['max_workers'] = max(1, old_workers - 1)
            adjustments.append(f"워커수 {old_workers} → {self.settings['max_workers']}")
        
        # 성능이 좋을 때 점진적 최적화
        if (current_metrics['memory_mb'] < self.settings['memory_threshold'] * 0.7 and 
            current_metrics['cpu_percent'] < self.settings['cpu_threshold'] * 0.7 and
            current_metrics['response_time'] < 5):
            
            # 배치 크기 증가 (조심스럽게)
            if self.settings['batch_size'] < 50:
                old_batch = self.settings['batch_size']
                self.settings['batch_size'] += 2
                adjustments.append(f"배치크기 증가 {old_batch} → {self.settings['batch_size']}")
        
        # 조정 내역 기록
        if adjustments:
            self.adjustment_history.append({
                'timestamp': time.time(),
                'adjustments': adjustments,
                'metrics': current_metrics.copy()
            })
            
            print(f"🔧 성능 자동 조정: {', '.join(adjustments)}")
        
        return self.settings
    
    def get_optimization_recommendations(self):
        """성능 최적화 권장사항 생성"""
        
        if len(self.performance_history) < 10:
            return ["데이터 수집 중... 더 많은 성능 데이터가 필요합니다."]
        
        recommendations = []
        
        # 메모리 사용 패턴 분석
        memory_values = [p['memory_mb'] for p in self.performance_history]
        avg_memory = statistics.mean(memory_values)
        max_memory = max(memory_values)
        
        if max_memory > 2000:
            recommendations.append("💾 메모리 사용량 최적화: 배치 크기 축소 또는 가비지 컬렉션 강화")
        
        # 응답시간 패턴 분석
        response_times = [p['response_time'] for p in self.performance_history]
        avg_response = statistics.mean(response_times)
        
        if avg_response > 8:
            recommendations.append("🐌 응답시간 개선: 셀렉터 최적화 또는 네트워크 설정 점검")
        
        # CPU 사용 패턴 분석
        cpu_values = [p['cpu_percent'] for p in self.performance_history]
        avg_cpu = statistics.mean(cpu_values)
        
        if avg_cpu > 80:
            recommendations.append("⚡ CPU 부하 감소: 대기시간 증가 또는 동시성 축소")
        
        # 성공률 분석
        success_rates = [p.get('success_rate', 100) for p in self.performance_history]
        avg_success = statistics.mean(success_rates)
        
        if avg_success < 90:
            recommendations.append("🎯 안정성 개선: 재시도 로직 강화 또는 오류 처리 개선")
        
        if not recommendations:
            recommendations.append("✨ 현재 성능이 우수합니다. 현 상태를 유지하세요.")
        
        return recommendations


# 자동 튜닝 통합 크롤러
class AutoTuningKKdayCrawler:
    """자동 성능 튜닝이 포함된 KKday 크롤러"""
    
    def __init__(self, city_name):
        self.city_name = city_name
        self.tuner = AdaptivePerformanceTuner()
        self.monitor = KKdayPerformanceMonitor()
        
    def crawl_with_auto_tuning(self, urls):
        """자동 튜닝이 적용된 크롤링"""
        
        self.monitor.start_monitoring()
        
        try:
            results = []
            
            for i, batch_start in enumerate(range(0, len(urls), self.tuner.settings['batch_size'])):
                batch_end = min(batch_start + self.tuner.settings['batch_size'], len(urls))
                batch_urls = urls[batch_start:batch_end]
                
                print(f"🔄 배치 {i+1} 처리 중 ({len(batch_urls)}개)")
                
                # 배치 크롤링
                batch_results = self.process_batch(batch_urls)
                results.extend(batch_results)
                
                # 현재 성능 메트릭 수집
                current_metrics = {
                    'memory_mb': psutil.Process().memory_info().rss / 1024 / 1024,
                    'cpu_percent': psutil.cpu_percent(),
                    'response_time': self.calculate_avg_response_time(),
                    'success_rate': self.calculate_success_rate(batch_results)
                }
                
                # 자동 튜닝 수행
                if i % 5 == 0:  # 5배치마다 튜닝
                    self.tuner.auto_tune_performance(current_metrics)
                
                # 조정된 대기시간 적용
                time.sleep(self.tuner.settings['delay_time'])
            
            return results
            
        finally:
            self.monitor.stop_monitoring()
            
            # 최종 성능 리포트
            final_report = self.monitor.generate_performance_report()
            print("📋 자동 튜닝 크롤링 완료")
```

---

**문서 버전**: v1.0  
**최종 업데이트**: 2024-12-07  
**담당자**: DevOps팀  
**다음 리뷰**: 2024-12-21