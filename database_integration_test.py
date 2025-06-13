#!/usr/bin/env python3
"""
Database Integration Testing
Kiểm tra tích hợp với Firebase và các database operations
"""

import os
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

class DatabaseIntegrationTest:
    """Test tích hợp database"""
    
    def __init__(self):
        self.test_results = []
        self.test_user_id = f"test_user_{int(time.time())}"
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Log kết quả test"""
        result = {
            "test_name": test_name,
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
    
    def test_firebase_connection(self):
        """Test kết nối Firebase"""
        print("\n🔥 TESTING FIREBASE CONNECTION")
        print("=" * 40)
        
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            start_time = time.time()
            
            # Kiểm tra xem Firebase đã được khởi tạo chưa
            try:
                app = firebase_admin.get_app()
                self.log_test_result(
                    "Firebase App Check", 
                    True, 
                    "Firebase app already initialized", 
                    time.time() - start_time
                )
            except ValueError:
                # Chưa khởi tạo, thử khởi tạo
                try:
                    firebase_admin.initialize_app()
                    self.log_test_result(
                        "Firebase Initialization", 
                        True, 
                        "Firebase initialized successfully", 
                        time.time() - start_time
                    )
                except Exception as e:
                    self.log_test_result(
                        "Firebase Initialization", 
                        False, 
                        f"Failed to initialize: {str(e)}", 
                        time.time() - start_time
                    )
                    return False
            
            # Test Firestore connection
            start_time = time.time()
            db = firestore.client()
            
            # Thử đọc một collection
            test_collection = db.collection('test_connection')
            docs = test_collection.limit(1).get()
            
            self.log_test_result(
                "Firestore Connection", 
                True, 
                "Successfully connected to Firestore", 
                time.time() - start_time
            )
            return True
            
        except ImportError:
            self.log_test_result(
                "Firebase Import", 
                False, 
                "Firebase Admin SDK not installed"
            )
            return False
        except Exception as e:
            self.log_test_result(
                "Firebase Connection", 
                False, 
                f"Connection failed: {str(e)}"
            )
            return False
    
    def test_firestore_operations(self):
        """Test các operations cơ bản với Firestore"""
        print("\n📊 TESTING FIRESTORE OPERATIONS")
        print("=" * 40)
        
        try:
            from firebase_admin import firestore
            
            db = firestore.client()
            test_collection = db.collection('test_meal_plans')
            test_doc_id = f"test_doc_{int(time.time())}"
            
            # Test data
            test_data = {
                "user_id": self.test_user_id,
                "created_at": datetime.now(),
                "weekly_plan": {
                    "Monday": {
                        "meals": {
                            "Bữa sáng": [{
                                "name": "Test Meal",
                                "calories": 400,
                                "ingredients": ["Test ingredient"]
                            }]
                        }
                    }
                },
                "test_field": "test_value"
            }
            
            # Test CREATE
            start_time = time.time()
            doc_ref = test_collection.document(test_doc_id)
            doc_ref.set(test_data)
            
            self.log_test_result(
                "Firestore CREATE", 
                True, 
                f"Document created: {test_doc_id}", 
                time.time() - start_time
            )
            
            # Test READ
            start_time = time.time()
            doc = doc_ref.get()
            
            if doc.exists:
                retrieved_data = doc.to_dict()
                self.log_test_result(
                    "Firestore READ", 
                    True, 
                    f"Document retrieved with {len(retrieved_data)} fields", 
                    time.time() - start_time
                )
            else:
                self.log_test_result(
                    "Firestore READ", 
                    False, 
                    "Document not found after creation", 
                    time.time() - start_time
                )
                return False
            
            # Test UPDATE
            start_time = time.time()
            update_data = {
                "updated_at": datetime.now(),
                "test_field": "updated_value"
            }
            doc_ref.update(update_data)
            
            self.log_test_result(
                "Firestore UPDATE", 
                True, 
                "Document updated successfully", 
                time.time() - start_time
            )
            
            # Test QUERY
            start_time = time.time()
            query_results = test_collection.where("user_id", "==", self.test_user_id).get()
            
            self.log_test_result(
                "Firestore QUERY", 
                True, 
                f"Query returned {len(query_results)} documents", 
                time.time() - start_time
            )
            
            # Test DELETE (cleanup)
            start_time = time.time()
            doc_ref.delete()
            
            self.log_test_result(
                "Firestore DELETE", 
                True, 
                "Test document deleted", 
                time.time() - start_time
            )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Firestore Operations", 
                False, 
                f"Operations failed: {str(e)}"
            )
            return False
    
    def test_meal_plan_storage(self):
        """Test lưu trữ meal plan thực tế"""
        print("\n🍽️ TESTING MEAL PLAN STORAGE")
        print("=" * 40)
        
        try:
            from firebase_admin import firestore
            
            db = firestore.client()
            
            # Test với meal plan data thực tế
            meal_plan_data = {
                "user_id": self.test_user_id,
                "created_at": datetime.now(),
                "weekly_plan": {
                    "Monday": {
                        "meals": {
                            "Bữa sáng": [{
                                "name": "Bánh Mì Chay",
                                "description": "Bánh mì chay với đậu hũ",
                                "ingredients": [
                                    {"name": "Bánh mì", "amount": "1 ổ"},
                                    {"name": "Đậu hũ", "amount": "100g"}
                                ],
                                "nutrition": {
                                    "calories": 350,
                                    "protein": 18,
                                    "fat": 12,
                                    "carbs": 45
                                },
                                "preparation": ["Nướng bánh mì", "Chiên đậu hũ"],
                                "preparation_time": "15 phút"
                            }]
                        },
                        "nutrition_summary": {
                            "calories": 350,
                            "protein": 18,
                            "fat": 12,
                            "carbs": 45
                        }
                    }
                }
            }
            
            # Test lưu vào meal_plans collection
            start_time = time.time()
            meal_plans_ref = db.collection('meal_plans').document(self.test_user_id)
            meal_plans_ref.set(meal_plan_data)
            
            self.log_test_result(
                "Meal Plan Storage", 
                True, 
                "Meal plan saved to meal_plans collection", 
                time.time() - start_time
            )
            
            # Test lưu vào latest_meal_plans collection
            start_time = time.time()
            latest_ref = db.collection('latest_meal_plans').document(self.test_user_id)
            latest_ref.set(meal_plan_data)
            
            self.log_test_result(
                "Latest Meal Plan Storage", 
                True, 
                "Meal plan saved to latest_meal_plans collection", 
                time.time() - start_time
            )
            
            # Test đọc lại data
            start_time = time.time()
            retrieved_doc = meal_plans_ref.get()
            
            if retrieved_doc.exists:
                retrieved_data = retrieved_doc.to_dict()
                
                # Validate structure
                required_fields = ["user_id", "created_at", "weekly_plan"]
                missing_fields = [field for field in required_fields if field not in retrieved_data]
                
                if not missing_fields:
                    self.log_test_result(
                        "Meal Plan Retrieval", 
                        True, 
                        "Meal plan retrieved and validated", 
                        time.time() - start_time
                    )
                else:
                    self.log_test_result(
                        "Meal Plan Retrieval", 
                        False, 
                        f"Missing fields: {missing_fields}", 
                        time.time() - start_time
                    )
            else:
                self.log_test_result(
                    "Meal Plan Retrieval", 
                    False, 
                    "Meal plan not found after storage", 
                    time.time() - start_time
                )
            
            # Cleanup
            meal_plans_ref.delete()
            latest_ref.delete()
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "Meal Plan Storage", 
                False, 
                f"Storage test failed: {str(e)}"
            )
            return False
    
    def test_concurrent_database_access(self):
        """Test truy cập database đồng thời"""
        print("\n⚡ TESTING CONCURRENT DATABASE ACCESS")
        print("=" * 45)
        
        try:
            import concurrent.futures
            import threading
            from firebase_admin import firestore
            
            db = firestore.client()
            
            def concurrent_write(thread_id: int):
                """Ghi data đồng thời"""
                try:
                    doc_ref = db.collection('concurrent_test').document(f"thread_{thread_id}")
                    data = {
                        "thread_id": thread_id,
                        "timestamp": datetime.now(),
                        "data": f"Test data from thread {thread_id}"
                    }
                    doc_ref.set(data)
                    return True
                except Exception as e:
                    print(f"Thread {thread_id} failed: {e}")
                    return False
            
            # Test với 5 threads đồng thời
            num_threads = 5
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(concurrent_write, i) for i in range(num_threads)]
                results = [future.result() for future in futures]
            
            duration = time.time() - start_time
            successful_writes = sum(results)
            
            self.log_test_result(
                "Concurrent Writes", 
                successful_writes == num_threads, 
                f"{successful_writes}/{num_threads} writes successful", 
                duration
            )
            
            # Cleanup
            for i in range(num_threads):
                try:
                    db.collection('concurrent_test').document(f"thread_{i}").delete()
                except:
                    pass
            
            return successful_writes == num_threads
            
        except Exception as e:
            self.log_test_result(
                "Concurrent Database Access", 
                False, 
                f"Concurrent test failed: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Chạy tất cả database tests"""
        print("🚀 STARTING DATABASE INTEGRATION TESTS")
        print("=" * 60)
        print(f"Test User ID: {self.test_user_id}")
        print("=" * 60)
        
        test_functions = [
            ("Firebase Connection", self.test_firebase_connection),
            ("Firestore Operations", self.test_firestore_operations),
            ("Meal Plan Storage", self.test_meal_plan_storage),
            ("Concurrent Access", self.test_concurrent_database_access)
        ]
        
        results = {}
        total_start_time = time.time()
        
        for test_name, test_func in test_functions:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        total_time = time.time() - total_start_time
        
        # Print summary
        self.print_summary(results, total_time)
        
        return results
    
    def print_summary(self, results: Dict[str, bool], total_time: float):
        """In tóm tắt kết quả"""
        print("\n" + "="*60)
        print("📊 DATABASE TEST SUMMARY")
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
            print(f"\n❌ Failed Individual Tests:")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test['details']}")
        
        print("\n" + "="*60)
        
        if success_rate >= 80:
            print("🎉 DATABASE READY FOR PRODUCTION!")
        else:
            print("⚠️ DATABASE ISSUES FOUND - INVESTIGATE BEFORE DEPLOYMENT")
        
        print("="*60)


def main():
    """Main test runner"""
    db_tester = DatabaseIntegrationTest()
    results = db_tester.run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
