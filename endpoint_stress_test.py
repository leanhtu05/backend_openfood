#!/usr/bin/env python3
"""
Endpoint Stress Testing
Kiểm tra khả năng chịu tải và hiệu suất của các endpoint
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import threading

class EndpointStressTest:
    """Stress test cho các endpoint"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    async def make_async_request(self, session: aiohttp.ClientSession, endpoint: str, data: Dict) -> Dict:
        """Thực hiện request bất đồng bộ"""
        start_time = time.time()
        try:
            async with session.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_time = time.time() - start_time
                response_data = await response.json()
                
                return {
                    "success": response.status in [200, 201],
                    "status_code": response.status,
                    "response_time": response_time,
                    "response_size": len(str(response_data)),
                    "error": None
                }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "status_code": 0,
                "response_time": response_time,
                "response_size": 0,
                "error": str(e)
            }
    
    async def stress_test_meal_generation(self, concurrent_users: int = 10, requests_per_user: int = 5):
        """Stress test cho meal generation endpoint"""
        print(f"\n🔥 STRESS TEST: Meal Generation")
        print(f"Concurrent Users: {concurrent_users}")
        print(f"Requests per User: {requests_per_user}")
        print(f"Total Requests: {concurrent_users * requests_per_user}")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for user_id in range(concurrent_users):
                for request_id in range(requests_per_user):
                    data = {
                        "user_id": f"stress_test_user_{user_id}",
                        "calories_target": 2000 + (user_id * 100),  # Vary targets
                        "protein_target": 150 + (user_id * 10),
                        "fat_target": 65 + (user_id * 5),
                        "carbs_target": 250 + (user_id * 15),
                        "use_ai": request_id % 2 == 0  # Mix AI and fallback
                    }
                    
                    task = self.make_async_request(session, "/api/meal-plan/generate", data)
                    tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # Analyze results
            self.analyze_stress_test_results(results, total_time, "Meal Generation")
    
    async def stress_test_meal_replacement(self, concurrent_users: int = 8, requests_per_user: int = 3):
        """Stress test cho meal replacement endpoint"""
        print(f"\n🔄 STRESS TEST: Meal Replacement")
        print(f"Concurrent Users: {concurrent_users}")
        print(f"Requests per User: {requests_per_user}")
        print(f"Total Requests: {concurrent_users * requests_per_user}")
        print("=" * 50)
        
        meal_types = ["Bữa sáng", "Bữa trưa", "Bữa tối"]
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for user_id in range(concurrent_users):
                for request_id in range(requests_per_user):
                    data = {
                        "user_id": f"stress_test_user_{user_id}",
                        "day_of_week": days[request_id % len(days)],
                        "meal_type": meal_types[request_id % len(meal_types)],
                        "calories_target": 400 + (request_id * 50),
                        "protein_target": 25 + (request_id * 5),
                        "fat_target": 15 + (request_id * 2),
                        "carbs_target": 50 + (request_id * 10),
                        "use_ai": request_id % 3 == 0  # Mix AI and fallback
                    }
                    
                    task = self.make_async_request(session, "/api/meal-plan/replace-meal", data)
                    tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # Analyze results
            self.analyze_stress_test_results(results, total_time, "Meal Replacement")
    
    def analyze_stress_test_results(self, results: List[Dict], total_time: float, test_name: str):
        """Phân tích kết quả stress test"""
        valid_results = [r for r in results if isinstance(r, dict)]
        
        if not valid_results:
            print("❌ No valid results to analyze")
            return
        
        # Basic metrics
        total_requests = len(valid_results)
        successful_requests = sum(1 for r in valid_results if r["success"])
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests) * 100
        
        # Response time metrics
        response_times = [r["response_time"] for r in valid_results if r["response_time"] > 0]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        else:
            avg_response_time = median_response_time = min_response_time = max_response_time = p95_response_time = 0
        
        # Throughput
        requests_per_second = total_requests / total_time if total_time > 0 else 0
        
        # Error analysis
        error_types = {}
        status_codes = {}
        
        for result in valid_results:
            if not result["success"]:
                error = result.get("error", "Unknown")
                error_types[error] = error_types.get(error, 0) + 1
            
            status_code = result.get("status_code", 0)
            status_codes[status_code] = status_codes.get(status_code, 0) + 1
        
        # Print results
        print(f"\n📊 STRESS TEST RESULTS: {test_name}")
        print("=" * 60)
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {successful_requests}")
        print(f"Failed: {failed_requests}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Requests/Second: {requests_per_second:.2f}")
        
        print(f"\n⏱️ Response Time Metrics:")
        print(f"Average: {avg_response_time:.3f}s")
        print(f"Median: {median_response_time:.3f}s")
        print(f"Min: {min_response_time:.3f}s")
        print(f"Max: {max_response_time:.3f}s")
        print(f"95th Percentile: {p95_response_time:.3f}s")
        
        print(f"\n📈 Status Code Distribution:")
        for status_code, count in sorted(status_codes.items()):
            percentage = (count / total_requests) * 100
            print(f"  {status_code}: {count} ({percentage:.1f}%)")
        
        if error_types:
            print(f"\n❌ Error Types:")
            for error, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / failed_requests) * 100 if failed_requests > 0 else 0
                print(f"  {error}: {count} ({percentage:.1f}%)")
        
        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        if success_rate >= 95:
            print("✅ Excellent success rate")
        elif success_rate >= 90:
            print("⚠️ Good success rate")
        else:
            print("❌ Poor success rate - needs investigation")
        
        if avg_response_time <= 2.0:
            print("✅ Excellent response time")
        elif avg_response_time <= 5.0:
            print("⚠️ Acceptable response time")
        else:
            print("❌ Poor response time - optimization needed")
        
        if requests_per_second >= 10:
            print("✅ Good throughput")
        elif requests_per_second >= 5:
            print("⚠️ Moderate throughput")
        else:
            print("❌ Low throughput - scaling needed")
        
        print("=" * 60)
    
    async def run_all_stress_tests(self):
        """Chạy tất cả stress tests"""
        print("🚀 STARTING ENDPOINT STRESS TESTS")
        print("=" * 60)
        
        # Test meal generation with different loads
        await self.stress_test_meal_generation(concurrent_users=5, requests_per_user=3)
        await asyncio.sleep(2)  # Cool down
        
        await self.stress_test_meal_generation(concurrent_users=10, requests_per_user=2)
        await asyncio.sleep(2)  # Cool down
        
        # Test meal replacement
        await self.stress_test_meal_replacement(concurrent_users=8, requests_per_user=3)
        await asyncio.sleep(2)  # Cool down
        
        print("\n🏁 ALL STRESS TESTS COMPLETED")

def test_groq_service_under_load():
    """Test Groq service under concurrent load"""
    print("\n🤖 TESTING GROQ SERVICE UNDER LOAD")
    print("=" * 50)
    
    try:
        from groq_integration import GroqService
        
        def test_groq_request(thread_id: int):
            """Single Groq request for threading test"""
            try:
                groq_service = GroqService()
                start_time = time.time()
                
                meals = groq_service.generate_meal_suggestions(
                    calories_target=400 + (thread_id * 50),
                    protein_target=25 + (thread_id * 5),
                    fat_target=15 + (thread_id * 2),
                    carbs_target=50 + (thread_id * 10),
                    meal_type="bữa sáng",
                    use_ai=True
                )
                
                response_time = time.time() - start_time
                success = meals is not None and len(meals) > 0
                
                return {
                    "thread_id": thread_id,
                    "success": success,
                    "response_time": response_time,
                    "meal_count": len(meals) if meals else 0
                }
                
            except Exception as e:
                return {
                    "thread_id": thread_id,
                    "success": False,
                    "response_time": 0,
                    "meal_count": 0,
                    "error": str(e)
                }
        
        # Test with 5 concurrent threads
        num_threads = 5
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(test_groq_request, i) for i in range(num_threads)]
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful = sum(1 for r in results if r["success"])
        response_times = [r["response_time"] for r in results if r["response_time"] > 0]
        
        print(f"Concurrent Groq Requests: {num_threads}")
        print(f"Successful: {successful}/{num_threads}")
        print(f"Success Rate: {(successful/num_threads)*100:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        
        if response_times:
            print(f"Avg Response Time: {statistics.mean(response_times):.2f}s")
            print(f"Max Response Time: {max(response_times):.2f}s")
        
        # Show any errors
        errors = [r.get("error") for r in results if not r["success"] and "error" in r]
        if errors:
            print("Errors:")
            for error in errors:
                print(f"  - {error}")
        
    except ImportError:
        print("❌ Groq integration not available for testing")
    except Exception as e:
        print(f"❌ Error testing Groq service: {e}")

async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Endpoint Stress Test")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--requests", type=int, default=5, help="Requests per user")
    
    args = parser.parse_args()
    
    # Run async stress tests
    stress_tester = EndpointStressTest(args.url)
    await stress_tester.run_all_stress_tests()
    
    # Run Groq service test
    test_groq_service_under_load()

if __name__ == "__main__":
    asyncio.run(main())
