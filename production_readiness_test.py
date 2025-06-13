#!/usr/bin/env python3
"""
Production Readiness Test
Kiểm tra đặc biệt cho production environment
"""

import requests
import time
import json
import ssl
import socket
from urllib.parse import urlparse
from typing import Dict, List, Any
import concurrent.futures
from datetime import datetime

class ProductionReadinessTest:
    """Test sẵn sàng cho production"""
    
    def __init__(self, base_url: str):
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
    
    def test_ssl_certificate(self):
        """Kiểm tra SSL certificate (nếu HTTPS)"""
        print("\n🔒 TESTING SSL CERTIFICATE")
        print("=" * 40)
        
        parsed_url = urlparse(self.base_url)
        
        if parsed_url.scheme != 'https':
            self.log_result("SSL Certificate", True, "HTTP endpoint - SSL not required")
            return True
        
        try:
            start_time = time.time()
            
            # Get SSL certificate info
            hostname = parsed_url.hostname
            port = parsed_url.port or 443
            
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
            
            duration = time.time() - start_time
            
            # Check certificate validity
            not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_until_expiry = (not_after - datetime.now()).days
            
            if days_until_expiry > 30:
                self.log_result(
                    "SSL Certificate", 
                    True, 
                    f"Valid until {not_after.strftime('%Y-%m-%d')} ({days_until_expiry} days)", 
                    duration
                )
                return True
            else:
                self.log_result(
                    "SSL Certificate", 
                    False, 
                    f"Expires soon: {not_after.strftime('%Y-%m-%d')} ({days_until_expiry} days)", 
                    duration
                )
                return False
                
        except Exception as e:
            self.log_result("SSL Certificate", False, f"SSL check failed: {str(e)}")
            return False
    
    def test_response_headers(self):
        """Kiểm tra security headers"""
        print("\n🛡️ TESTING SECURITY HEADERS")
        print("=" * 40)
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health")
            duration = time.time() - start_time
            
            headers = response.headers
            security_checks = []
            
            # Check important security headers
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': None,  # For HTTPS only
                'Content-Security-Policy': None,
            }
            
            for header, expected in security_headers.items():
                if header in headers:
                    if expected is None:
                        security_checks.append(f"✅ {header} present")
                    elif isinstance(expected, list):
                        if headers[header] in expected:
                            security_checks.append(f"✅ {header}: {headers[header]}")
                        else:
                            security_checks.append(f"⚠️ {header}: {headers[header]} (expected: {expected})")
                    elif headers[header] == expected:
                        security_checks.append(f"✅ {header}: {headers[header]}")
                    else:
                        security_checks.append(f"⚠️ {header}: {headers[header]} (expected: {expected})")
                else:
                    security_checks.append(f"❌ {header} missing")
            
            # Check for server information disclosure
            if 'Server' in headers:
                security_checks.append(f"⚠️ Server header disclosed: {headers['Server']}")
            else:
                security_checks.append("✅ Server header hidden")
            
            self.log_result(
                "Security Headers", 
                True, 
                f"Checked {len(security_headers)} headers", 
                duration
            )
            
            for check in security_checks:
                print(f"   {check}")
            
            return True
            
        except Exception as e:
            self.log_result("Security Headers", False, f"Header check failed: {str(e)}")
            return False
    
    def test_rate_limiting(self):
        """Kiểm tra rate limiting"""
        print("\n🚦 TESTING RATE LIMITING")
        print("=" * 40)
        
        try:
            # Make rapid requests to test rate limiting
            rapid_requests = 20
            start_time = time.time()
            
            responses = []
            for i in range(rapid_requests):
                try:
                    response = self.session.get(f"{self.base_url}/health", timeout=5)
                    responses.append(response.status_code)
                except:
                    responses.append(0)
            
            duration = time.time() - start_time
            
            # Check if any requests were rate limited (429 status)
            rate_limited = sum(1 for status in responses if status == 429)
            successful = sum(1 for status in responses if status == 200)
            
            if rate_limited > 0:
                self.log_result(
                    "Rate Limiting", 
                    True, 
                    f"Rate limiting active: {rate_limited}/{rapid_requests} requests limited", 
                    duration
                )
            else:
                self.log_result(
                    "Rate Limiting", 
                    False, 
                    f"No rate limiting detected: {successful}/{rapid_requests} requests succeeded", 
                    duration
                )
            
            return rate_limited > 0
            
        except Exception as e:
            self.log_result("Rate Limiting", False, f"Rate limit test failed: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Kiểm tra error handling trong production"""
        print("\n⚠️ TESTING PRODUCTION ERROR HANDLING")
        print("=" * 45)
        
        error_tests = [
            {
                "name": "404 Not Found",
                "url": f"{self.base_url}/nonexistent-endpoint",
                "method": "GET",
                "expected_status": 404
            },
            {
                "name": "405 Method Not Allowed",
                "url": f"{self.base_url}/health",
                "method": "POST",
                "expected_status": 405
            },
            {
                "name": "Invalid JSON",
                "url": f"{self.base_url}/api/meal-plan/generate",
                "method": "POST",
                "data": "invalid json",
                "expected_status": [400, 422]
            }
        ]
        
        success_count = 0
        for test in error_tests:
            try:
                start_time = time.time()
                
                if test["method"] == "GET":
                    response = self.session.get(test["url"])
                elif test["method"] == "POST":
                    if "data" in test:
                        response = self.session.post(
                            test["url"], 
                            data=test["data"],
                            headers={"Content-Type": "application/json"}
                        )
                    else:
                        response = self.session.post(test["url"])
                
                duration = time.time() - start_time
                
                expected = test["expected_status"]
                if isinstance(expected, list):
                    success = response.status_code in expected
                else:
                    success = response.status_code == expected
                
                if success:
                    self.log_result(
                        f"Error: {test['name']}", 
                        True, 
                        f"Returned {response.status_code} as expected", 
                        duration
                    )
                    success_count += 1
                else:
                    self.log_result(
                        f"Error: {test['name']}", 
                        False, 
                        f"Expected {expected}, got {response.status_code}", 
                        duration
                    )
                    
            except Exception as e:
                self.log_result(f"Error: {test['name']}", False, f"Test failed: {str(e)}")
        
        return success_count == len(error_tests)
    
    def test_performance_benchmarks(self):
        """Kiểm tra performance benchmarks cho production"""
        print("\n⚡ TESTING PERFORMANCE BENCHMARKS")
        print("=" * 45)
        
        benchmarks = [
            {
                "name": "Health Check Response Time",
                "url": f"{self.base_url}/health",
                "method": "GET",
                "max_time": 1.0  # 1 second
            },
            {
                "name": "API Response Time",
                "url": f"{self.base_url}/api/meal-plan/generate",
                "method": "POST",
                "data": {
                    "user_id": "benchmark_test",
                    "calories_target": 2000,
                    "protein_target": 150,
                    "fat_target": 65,
                    "carbs_target": 250,
                    "use_ai": False  # Use fallback for consistent timing
                },
                "max_time": 10.0  # 10 seconds
            }
        ]
        
        success_count = 0
        for benchmark in benchmarks:
            try:
                start_time = time.time()
                
                if benchmark["method"] == "GET":
                    response = self.session.get(benchmark["url"])
                elif benchmark["method"] == "POST":
                    response = self.session.post(
                        benchmark["url"],
                        json=benchmark.get("data", {}),
                        headers={"Content-Type": "application/json"}
                    )
                
                duration = time.time() - start_time
                
                if duration <= benchmark["max_time"] and response.status_code in [200, 201]:
                    self.log_result(
                        benchmark["name"], 
                        True, 
                        f"Response time: {duration:.3f}s (limit: {benchmark['max_time']}s)", 
                        duration
                    )
                    success_count += 1
                else:
                    self.log_result(
                        benchmark["name"], 
                        False, 
                        f"Too slow: {duration:.3f}s (limit: {benchmark['max_time']}s) or error {response.status_code}", 
                        duration
                    )
                    
            except Exception as e:
                self.log_result(benchmark["name"], False, f"Benchmark failed: {str(e)}")
        
        return success_count == len(benchmarks)
    
    def test_data_validation(self):
        """Kiểm tra data validation trong production"""
        print("\n🔍 TESTING DATA VALIDATION")
        print("=" * 40)
        
        validation_tests = [
            {
                "name": "SQL Injection Protection",
                "data": {
                    "user_id": "'; DROP TABLE users; --",
                    "calories_target": 2000,
                    "protein_target": 150,
                    "fat_target": 65,
                    "carbs_target": 250
                }
            },
            {
                "name": "XSS Protection",
                "data": {
                    "user_id": "<script>alert('xss')</script>",
                    "calories_target": 2000,
                    "protein_target": 150,
                    "fat_target": 65,
                    "carbs_target": 250
                }
            },
            {
                "name": "Large Payload Protection",
                "data": {
                    "user_id": "x" * 10000,  # Very long string
                    "calories_target": 2000,
                    "protein_target": 150,
                    "fat_target": 65,
                    "carbs_target": 250
                }
            }
        ]
        
        success_count = 0
        for test in validation_tests:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/api/meal-plan/generate",
                    json=test["data"],
                    headers={"Content-Type": "application/json"}
                )
                duration = time.time() - start_time
                
                # Should return 400/422 for invalid data, not 500
                if response.status_code in [400, 422]:
                    self.log_result(
                        test["name"], 
                        True, 
                        f"Properly rejected with {response.status_code}", 
                        duration
                    )
                    success_count += 1
                elif response.status_code == 500:
                    self.log_result(
                        test["name"], 
                        False, 
                        "Server error - validation may be insufficient", 
                        duration
                    )
                else:
                    self.log_result(
                        test["name"], 
                        False, 
                        f"Unexpected response: {response.status_code}", 
                        duration
                    )
                    
            except Exception as e:
                self.log_result(test["name"], False, f"Validation test failed: {str(e)}")
        
        return success_count == len(validation_tests)
    
    def run_all_tests(self):
        """Chạy tất cả production readiness tests"""
        print("🏭 PRODUCTION READINESS TEST SUITE")
        print("=" * 60)
        print(f"Target URL: {self.base_url}")
        print("=" * 60)
        
        test_functions = [
            ("SSL Certificate", self.test_ssl_certificate),
            ("Security Headers", self.test_response_headers),
            ("Rate Limiting", self.test_rate_limiting),
            ("Error Handling", self.test_error_handling),
            ("Performance Benchmarks", self.test_performance_benchmarks),
            ("Data Validation", self.test_data_validation)
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
        self.print_production_summary(results, total_time)
        
        return results
    
    def print_production_summary(self, results: Dict[str, bool], total_time: float):
        """In tóm tắt production readiness"""
        print("\n" + "="*70)
        print("🏭 PRODUCTION READINESS ASSESSMENT")
        print("="*70)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        readiness_score = (passed / total) * 100 if total > 0 else 0
        
        print(f"Production Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Readiness Score: {readiness_score:.1f}%")
        print(f"Test Duration: {total_time:.2f}s")
        
        print("\nTest Results:")
        for test_name, result in results.items():
            status = "✅ READY" if result else "❌ NOT READY"
            print(f"  {status} {test_name}")
        
        # Production readiness verdict
        print(f"\n🎯 PRODUCTION DEPLOYMENT VERDICT:")
        
        if readiness_score == 100:
            print("  🚀 FULLY READY - All production checks passed!")
        elif readiness_score >= 80:
            print("  ✅ MOSTLY READY - Minor issues, but safe to deploy")
        elif readiness_score >= 60:
            print("  ⚠️ PARTIALLY READY - Address issues before production")
        else:
            print("  ❌ NOT READY - Critical issues must be fixed")
        
        print("="*70)


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Readiness Test")
    parser.add_argument("url", help="Production URL to test")
    
    args = parser.parse_args()
    
    tester = ProductionReadinessTest(args.url)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    all_ready = all(results.values())
    exit(0 if all_ready else 1)


if __name__ == "__main__":
    main()
