#!/usr/bin/env python3
"""
Test với User ID thực
Test các endpoint với user ID thực của người dùng
"""

import json
import time
import requests
import concurrent.futures
from typing import Dict, List, Any
from datetime import datetime

class RealUserTest:
    """Test với user ID thực"""
    
    def __init__(self, base_url: str = "http://localhost:8001", user_id: str = "49DhdmJHFAY40eEgaPNEJqGdDQK2"):
        self.base_url = base_url.rstrip('/')
        self.user_id = user_id
        self.session = requests.Session()
        self.session.timeout = 60  # Tăng timeout cho AI requests
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.2f}s)")
        if details:
            print(f"   {details}")
    
    def test_server_health(self):
        """Test server health"""
        print("\n🏥 TESTING SERVER HEALTH")
        print("=" * 35)
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_result("Server Health", True, f"Server running: {data['message']}", duration)
                    return True
            
            self.log_result("Server Health", False, f"HTTP {response.status_code}", duration)
            return False
                
        except Exception as e:
            self.log_result("Server Health", False, f"Error: {str(e)}")
            return False
    
    def test_ai_availability(self):
        """Test AI availability"""
        print("\n🤖 TESTING AI AVAILABILITY")
        print("=" * 40)
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/check-ai-availability")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                ai_available = data.get("ai_available", False)
                
                if ai_available:
                    self.log_result("AI Availability", True, "AI service is available", duration)
                    return True
                else:
                    self.log_result("AI Availability", False, f"AI not available: {data.get('message', 'Unknown')}", duration)
                    return False
            else:
                self.log_result("AI Availability", False, f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            self.log_result("AI Availability", False, f"Error: {str(e)}")
            return False
    
    def test_meal_plan_generation_fallback(self):
        """Test meal plan generation với fallback data"""
        print("\n🍽️ TESTING MEAL PLAN GENERATION (FALLBACK)")
        print("=" * 55)
        
        test_data = {
            "user_id": self.user_id,
            "calories_target": 2000,
            "protein_target": 150,
            "fat_target": 65,
            "carbs_target": 250,
            "use_ai": False  # Sử dụng fallback data
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/meal-plan/generate",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            duration = time.time() - start_time
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    
                    # Validate response structure
                    if "weekly_plan" in data and "user_id" in data:
                        weekly_plan = data["weekly_plan"]
                        days_count = len(weekly_plan)
                        
                        # Count total meals
                        total_meals = 0
                        for day_data in weekly_plan.values():
                            if "meals" in day_data:
                                for meal_type, meals in day_data["meals"].items():
                                    total_meals += len(meals)
                        
                        self.log_result(
                            "Meal Plan Generation (Fallback)", 
                            True, 
                            f"Generated {days_count} days, {total_meals} total meals", 
                            duration
                        )
                        return True
                    else:
                        self.log_result(
                            "Meal Plan Generation (Fallback)", 
                            False, 
                            "Invalid response structure", 
                            duration
                        )
                        return False
                        
                except json.JSONDecodeError:
                    self.log_result(
                        "Meal Plan Generation (Fallback)", 
                        False, 
                        "Invalid JSON response", 
                        duration
                    )
                    return False
            else:
                self.log_result(
                    "Meal Plan Generation (Fallback)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:100]}", 
                    duration
                )
                return False
                
        except Exception as e:
            self.log_result("Meal Plan Generation (Fallback)", False, f"Error: {str(e)}")
            return False
    
    def test_meal_plan_generation_ai(self):
        """Test meal plan generation với AI"""
        print("\n🤖 TESTING MEAL PLAN GENERATION (AI)")
        print("=" * 50)
        
        test_data = {
            "user_id": self.user_id,
            "calories_target": 1800,
            "protein_target": 120,
            "fat_target": 60,
            "carbs_target": 180,
            "use_ai": True,  # Sử dụng AI
            "preferences": ["healthy", "vietnamese"],
            "diet_preference": "balanced"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/meal-plan/generate",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            duration = time.time() - start_time
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    
                    if "weekly_plan" in data and "user_id" in data:
                        weekly_plan = data["weekly_plan"]
                        
                        # Check if AI was actually used
                        ai_used = False
                        for day_data in weekly_plan.values():
                            if "meals" in day_data:
                                for meal_type, meals in day_data["meals"].items():
                                    for meal in meals:
                                        # Check for AI-generated content indicators
                                        if "preparation" in meal and len(meal["preparation"]) > 0:
                                            ai_used = True
                                            break
                        
                        self.log_result(
                            "Meal Plan Generation (AI)", 
                            True, 
                            f"AI used: {ai_used}, Generated {len(weekly_plan)} days", 
                            duration
                        )
                        return True
                    else:
                        self.log_result(
                            "Meal Plan Generation (AI)", 
                            False, 
                            "Invalid response structure", 
                            duration
                        )
                        return False
                        
                except json.JSONDecodeError:
                    self.log_result(
                        "Meal Plan Generation (AI)", 
                        False, 
                        "Invalid JSON response", 
                        duration
                    )
                    return False
            else:
                self.log_result(
                    "Meal Plan Generation (AI)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:100]}", 
                    duration
                )
                return False
                
        except Exception as e:
            self.log_result("Meal Plan Generation (AI)", False, f"Error: {str(e)}")
            return False
    
    def test_meal_replacement(self):
        """Test meal replacement"""
        print("\n🔄 TESTING MEAL REPLACEMENT")
        print("=" * 40)
        
        test_data = {
            "user_id": self.user_id,
            "day_of_week": "Monday",
            "meal_type": "Bữa sáng",
            "calories_target": 400,
            "protein_target": 25,
            "fat_target": 15,
            "carbs_target": 50,
            "use_ai": True
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/meal-plan/replace-meal",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            duration = time.time() - start_time
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    
                    if "message" in data or "success" in data or "weekly_plan" in data:
                        self.log_result("Meal Replacement", True, "Replacement successful", duration)
                        return True
                    else:
                        self.log_result("Meal Replacement", False, "Invalid response format", duration)
                        return False
                        
                except json.JSONDecodeError:
                    self.log_result("Meal Replacement", False, "Invalid JSON response", duration)
                    return False
            else:
                self.log_result("Meal Replacement", False, f"HTTP {response.status_code}: {response.text[:100]}", duration)
                return False
                
        except Exception as e:
            self.log_result("Meal Replacement", False, f"Error: {str(e)}")
            return False
    
    def test_day_replacement(self):
        """Test day replacement"""
        print("\n📅 TESTING DAY REPLACEMENT")
        print("=" * 40)
        
        test_data = {
            "user_id": self.user_id,
            "calories_target": 2200,
            "protein_target": 160,
            "fat_target": 70,
            "carbs_target": 260,
            "use_ai": True,
            "day_of_week": "Tuesday"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/replace-day",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            duration = time.time() - start_time
            
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    
                    if "message" in data or "success" in data or "weekly_plan" in data:
                        self.log_result("Day Replacement", True, "Day replacement successful", duration)
                        return True
                    else:
                        self.log_result("Day Replacement", False, "Invalid response format", duration)
                        return False
                        
                except json.JSONDecodeError:
                    self.log_result("Day Replacement", False, "Invalid JSON response", duration)
                    return False
            else:
                self.log_result("Day Replacement", False, f"HTTP {response.status_code}: {response.text[:100]}", duration)
                return False
                
        except Exception as e:
            self.log_result("Day Replacement", False, f"Error: {str(e)}")
            return False
    
    def test_usda_search(self):
        """Test USDA food search"""
        print("\n🔍 TESTING USDA FOOD SEARCH")
        print("=" * 40)
        
        try:
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}/usda/search",
                params={
                    "query": "gạo",
                    "vietnamese": True,
                    "max_results": 5
                }
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if "results" in data:
                        results_count = len(data["results"])
                        self.log_result("USDA Search", True, f"Found {results_count} results", duration)
                        return True
                    else:
                        self.log_result("USDA Search", False, "No results field in response", duration)
                        return False
                        
                except json.JSONDecodeError:
                    self.log_result("USDA Search", False, "Invalid JSON response", duration)
                    return False
            else:
                self.log_result("USDA Search", False, f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            self.log_result("USDA Search", False, f"Error: {str(e)}")
            return False
    
    def test_concurrent_requests(self):
        """Test concurrent requests với user ID thực"""
        print("\n⚡ TESTING CONCURRENT REQUESTS")
        print("=" * 40)
        
        def make_request(request_id):
            try:
                data = {
                    "user_id": self.user_id,
                    "calories_target": 1500 + (request_id * 100),
                    "protein_target": 100 + (request_id * 10),
                    "fat_target": 50 + (request_id * 5),
                    "carbs_target": 150 + (request_id * 15),
                    "use_ai": False  # Use fallback for speed
                }
                
                response = requests.post(
                    f"{self.base_url}/api/meal-plan/generate",
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
                
                return response.status_code in [200, 201]
            except:
                return False
        
        num_requests = 3  # Giảm số request để tránh overload
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [future.result() for future in futures]
        
        duration = time.time() - start_time
        successful = sum(results)
        
        if successful >= num_requests * 0.8:  # 80% success rate
            self.log_result(
                "Concurrent Requests", 
                True, 
                f"{successful}/{num_requests} successful", 
                duration
            )
            return True
        else:
            self.log_result(
                "Concurrent Requests", 
                False, 
                f"Only {successful}/{num_requests} successful", 
                duration
            )
            return False
    
    def run_all_tests(self):
        """Run all tests với user ID thực"""
        print("🚀 REAL USER TESTING SUITE")
        print("=" * 60)
        print(f"Target URL: {self.base_url}")
        print(f"User ID: {self.user_id}")
        print("=" * 60)
        
        test_functions = [
            ("Server Health", self.test_server_health),
            ("AI Availability", self.test_ai_availability),
            ("Meal Plan Generation (Fallback)", self.test_meal_plan_generation_fallback),
            ("Meal Plan Generation (AI)", self.test_meal_plan_generation_ai),
            ("Meal Replacement", self.test_meal_replacement),
            ("Day Replacement", self.test_day_replacement),
            ("USDA Search", self.test_usda_search),
            ("Concurrent Requests", self.test_concurrent_requests)
        ]
        
        results = {}
        start_time = time.time()
        
        for test_name, test_func in test_functions:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                results[test_name] = test_func()
                
                # Thêm delay giữa các test để tránh rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        total_time = time.time() - start_time
        
        # Print summary
        self.print_summary(results, total_time)
        
        return results
    
    def print_summary(self, results: Dict[str, bool], total_time: float):
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 REAL USER TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"User ID: {self.user_id}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        
        print("\nTest Results:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests[:5]:
                print(f"  - {test['test']}: {test['details']}")
            if len(failed_tests) > 5:
                print(f"  ... and {len(failed_tests) - 5} more")
        
        print("\n" + "="*70)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT - Backend ready for production!")
        elif success_rate >= 75:
            print("✅ GOOD - Minor issues, mostly ready")
        elif success_rate >= 50:
            print("⚠️ MODERATE - Some issues need attention")
        else:
            print("❌ POOR - Major issues, fix before deployment")
        
        print("="*70)


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real User Test")
    parser.add_argument("--url", default="http://localhost:8001", help="API base URL")
    parser.add_argument("--user-id", default="49DhdmJHFAY40eEgaPNEJqGdDQK2", help="User ID")
    
    args = parser.parse_args()
    
    tester = RealUserTest(args.url, args.user_id)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
