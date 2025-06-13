#!/usr/bin/env python3
"""
Simple Comprehensive Test
Test toàn diện đơn giản không cần dependencies phức tạp
"""

import json
import time
import requests
import threading
import concurrent.futures
from typing import Dict, List, Any
from datetime import datetime

class SimpleComprehensiveTest:
    """Test suite đơn giản và toàn diện"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
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
                try:
                    data = response.json()
                    if "message" in data:
                        self.log_result("Server Health", True, "Server is running", duration)
                        return True
                    else:
                        self.log_result("Server Health", False, "Invalid response format", duration)
                        return False
                except:
                    self.log_result("Server Health", False, "Invalid JSON response", duration)
                    return False
            else:
                self.log_result("Server Health", False, f"HTTP {response.status_code}", duration)
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_result("Server Health", False, "Cannot connect to server")
            return False
        except Exception as e:
            self.log_result("Server Health", False, f"Error: {str(e)}")
            return False
    
    def test_groq_integration(self):
        """Test Groq integration"""
        print("\n🤖 TESTING GROQ INTEGRATION")
        print("=" * 40)
        
        try:
            from groq_integration import GroqService
            
            start_time = time.time()
            groq_service = GroqService()
            
            if not groq_service.available:
                self.log_result("Groq Service", False, "Groq service not available")
                return False
            
            # Test meal generation
            meals = groq_service.generate_meal_suggestions(
                calories_target=400,
                protein_target=25,
                fat_target=15,
                carbs_target=50,
                meal_type="bữa sáng",
                use_ai=True
            )
            duration = time.time() - start_time
            
            if meals and len(meals) > 0:
                # Validate meal structure
                meal = meals[0]
                required_fields = ["name", "description", "ingredients", "nutrition"]
                missing_fields = [field for field in required_fields if field not in meal]
                
                if not missing_fields:
                    self.log_result("Groq Integration", True, f"Generated {len(meals)} valid meals", duration)
                    return True
                else:
                    self.log_result("Groq Integration", False, f"Missing fields: {missing_fields}", duration)
                    return False
            else:
                self.log_result("Groq Integration", False, "No meals generated", duration)
                return False
                
        except ImportError:
            self.log_result("Groq Integration", False, "Groq integration not available")
            return False
        except Exception as e:
            self.log_result("Groq Integration", False, f"Error: {str(e)}")
            return False
    
    def test_meal_plan_generation(self):
        """Test meal plan generation endpoint"""
        print("\n🍽️ TESTING MEAL PLAN GENERATION")
        print("=" * 45)
        
        test_cases = [
            {
                "name": "Basic meal plan",
                "data": {
                    "user_id": "test_user_basic",
                    "calories_target": 2000,
                    "protein_target": 150,
                    "fat_target": 65,
                    "carbs_target": 250,
                    "use_ai": False  # Use fallback for reliability
                }
            },
            {
                "name": "Low calorie plan",
                "data": {
                    "user_id": "test_user_low_cal",
                    "calories_target": 1200,
                    "protein_target": 80,
                    "fat_target": 40,
                    "carbs_target": 120,
                    "use_ai": False
                }
            },
            {
                "name": "High protein plan",
                "data": {
                    "user_id": "test_user_high_protein",
                    "calories_target": 2500,
                    "protein_target": 200,
                    "fat_target": 80,
                    "carbs_target": 200,
                    "use_ai": False,
                    "preferences": ["high-protein"],
                    "diet_preference": "healthy"
                }
            }
        ]
        
        success_count = 0
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/api/meal-plan/generate",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"}
                )
                duration = time.time() - start_time
                
                if response.status_code in [200, 201]:
                    try:
                        data = response.json()
                        if "weekly_plan" in data and "user_id" in data:
                            self.log_result(
                                f"Generate: {test_case['name']}", 
                                True, 
                                "Valid meal plan generated", 
                                duration
                            )
                            success_count += 1
                        else:
                            self.log_result(
                                f"Generate: {test_case['name']}", 
                                False, 
                                "Invalid response structure", 
                                duration
                            )
                    except json.JSONDecodeError:
                        self.log_result(
                            f"Generate: {test_case['name']}", 
                            False, 
                            "Invalid JSON response", 
                            duration
                        )
                else:
                    self.log_result(
                        f"Generate: {test_case['name']}", 
                        False, 
                        f"HTTP {response.status_code}", 
                        duration
                    )
                    
            except Exception as e:
                self.log_result(f"Generate: {test_case['name']}", False, f"Error: {str(e)}")
        
        return success_count == len(test_cases)
    
    def test_meal_replacement(self):
        """Test meal replacement endpoint"""
        print("\n🔄 TESTING MEAL REPLACEMENT")
        print("=" * 40)
        
        test_data = {
            "user_id": "test_user_replace",
            "day_of_week": "Monday",
            "meal_type": "Bữa sáng",
            "calories_target": 400,
            "protein_target": 25,
            "fat_target": 15,
            "carbs_target": 50,
            "use_ai": False
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
                    if "message" in data or "success" in data:
                        self.log_result("Meal Replacement", True, "Replacement successful", duration)
                        return True
                    else:
                        self.log_result("Meal Replacement", False, "Invalid response format", duration)
                        return False
                except json.JSONDecodeError:
                    self.log_result("Meal Replacement", False, "Invalid JSON response", duration)
                    return False
            else:
                self.log_result("Meal Replacement", False, f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            self.log_result("Meal Replacement", False, f"Error: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling"""
        print("\n⚠️ TESTING ERROR HANDLING")
        print("=" * 35)
        
        error_tests = [
            {
                "name": "Missing user_id",
                "data": {
                    "calories_target": 2000,
                    "protein_target": 150,
                    "fat_target": 65,
                    "carbs_target": 250
                },
                "expected_status": [400, 422]
            },
            {
                "name": "Invalid nutrition values",
                "data": {
                    "user_id": "test_user",
                    "calories_target": -100,
                    "protein_target": "invalid",
                    "fat_target": 65,
                    "carbs_target": 250
                },
                "expected_status": [400, 422]
            }
        ]
        
        success_count = 0
        for test in error_tests:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/api/meal-plan/generate",
                    json=test["data"],
                    headers={"Content-Type": "application/json"}
                )
                duration = time.time() - start_time
                
                if response.status_code in test["expected_status"]:
                    self.log_result(
                        f"Error: {test['name']}", 
                        True, 
                        f"Correctly returned {response.status_code}", 
                        duration
                    )
                    success_count += 1
                else:
                    self.log_result(
                        f"Error: {test['name']}", 
                        False, 
                        f"Expected {test['expected_status']}, got {response.status_code}", 
                        duration
                    )
                    
            except Exception as e:
                self.log_result(f"Error: {test['name']}", False, f"Exception: {str(e)}")
        
        return success_count == len(error_tests)
    
    def test_concurrent_requests(self):
        """Test concurrent requests"""
        print("\n⚡ TESTING CONCURRENT REQUESTS")
        print("=" * 40)
        
        def make_request(thread_id):
            try:
                data = {
                    "user_id": f"concurrent_test_{thread_id}",
                    "calories_target": 2000,
                    "protein_target": 150,
                    "fat_target": 65,
                    "carbs_target": 250,
                    "use_ai": False
                }
                
                response = requests.post(
                    f"{self.base_url}/api/meal-plan/generate",
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                return response.status_code == 200
            except:
                return False
        
        num_threads = 5
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_threads)]
            results = [future.result() for future in futures]
        
        duration = time.time() - start_time
        successful = sum(results)
        
        if successful >= num_threads * 0.8:  # 80% success rate
            self.log_result(
                "Concurrent Requests", 
                True, 
                f"{successful}/{num_threads} successful", 
                duration
            )
            return True
        else:
            self.log_result(
                "Concurrent Requests", 
                False, 
                f"Only {successful}/{num_threads} successful", 
                duration
            )
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 SIMPLE COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"Target URL: {self.base_url}")
        print("=" * 60)
        
        test_functions = [
            ("Server Health", self.test_server_health),
            ("Groq Integration", self.test_groq_integration),
            ("Meal Plan Generation", self.test_meal_plan_generation),
            ("Meal Replacement", self.test_meal_replacement),
            ("Error Handling", self.test_error_handling),
            ("Concurrent Requests", self.test_concurrent_requests)
        ]
        
        results = {}
        start_time = time.time()
        
        for test_name, test_func in test_functions:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        total_time = time.time() - start_time
        
        # Print summary
        self.print_summary(results, total_time)
        
        return results
    
    def print_summary(self, results: Dict[str, bool], total_time: float):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        
        print("\nTest Results:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        # Show failed individual tests
        failed_tests = [test for test in self.test_results if not test["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests[:5]:  # Show first 5 failures
                print(f"  - {test['test']}: {test['details']}")
            if len(failed_tests) > 5:
                print(f"  ... and {len(failed_tests) - 5} more")
        
        print("\n" + "="*60)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT - Ready for deployment!")
        elif success_rate >= 70:
            print("✅ GOOD - Minor issues, mostly ready")
        elif success_rate >= 50:
            print("⚠️ MODERATE - Some issues need attention")
        else:
            print("❌ POOR - Major issues, fix before deployment")
        
        print("="*60)


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Comprehensive Test")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    tester = SimpleComprehensiveTest(args.url)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
