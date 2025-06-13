#!/usr/bin/env python3
"""
Master Test Runner
Chạy tất cả các test suites để đảm bảo hệ thống sẵn sàng deploy
"""

import asyncio
import subprocess
import sys
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Any

class MasterTestRunner:
    """Chạy tất cả test suites và tổng hợp kết quả"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        self.start_time = time.time()
        
    def run_test_suite(self, test_name: str, test_command: List[str]) -> Dict[str, Any]:
        """Chạy một test suite và trả về kết quả"""
        print(f"\n🚀 RUNNING: {test_name}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Chạy test command
            result = subprocess.run(
                test_command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            return {
                "name": test_name,
                "success": success,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return {
                "name": test_name,
                "success": False,
                "duration": duration,
                "stdout": "",
                "stderr": "Test timed out after 5 minutes",
                "return_code": -1
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "name": test_name,
                "success": False,
                "duration": duration,
                "stdout": "",
                "stderr": f"Error running test: {str(e)}",
                "return_code": -1
            }
    
    async def run_async_test_suite(self, test_name: str, test_module: str) -> Dict[str, Any]:
        """Chạy async test suite"""
        print(f"\n🚀 RUNNING: {test_name}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Import và chạy async test
            if test_module == "endpoint_stress_test":
                from endpoint_stress_test import EndpointStressTest, test_groq_service_under_load
                
                stress_tester = EndpointStressTest(self.base_url)
                await stress_tester.run_all_stress_tests()
                test_groq_service_under_load()
                
                duration = time.time() - start_time
                return {
                    "name": test_name,
                    "success": True,
                    "duration": duration,
                    "stdout": "Stress tests completed successfully",
                    "stderr": "",
                    "return_code": 0
                }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                "name": test_name,
                "success": False,
                "duration": duration,
                "stdout": "",
                "stderr": f"Error running async test: {str(e)}",
                "return_code": -1
            }
    
    def check_prerequisites(self) -> bool:
        """Kiểm tra các điều kiện tiên quyết"""
        print("🔍 CHECKING PREREQUISITES")
        print("=" * 40)
        
        checks = []
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            print("✅ Python version OK")
            checks.append(True)
        else:
            print(f"❌ Python version {python_version} < 3.8")
            checks.append(False)
        
        # Check required modules
        required_modules = [
            "requests", "aiohttp", "firebase_admin", 
            "groq", "fastapi", "uvicorn"
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module} available")
                checks.append(True)
            except ImportError:
                print(f"⚠️ {module} not available (may be optional)")
                # Don't fail for optional modules
        
        # Check environment variables
        env_vars = ["GROQ_API_KEY"]
        for var in env_vars:
            if os.getenv(var):
                print(f"✅ {var} set")
                checks.append(True)
            else:
                print(f"⚠️ {var} not set")
                # Don't fail for missing env vars
        
        # Check if server is running
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Server running at {self.base_url}")
                checks.append(True)
            else:
                print(f"⚠️ Server at {self.base_url} returned {response.status_code}")
                checks.append(False)
        except Exception as e:
            print(f"⚠️ Cannot reach server at {self.base_url}: {e}")
            checks.append(False)
        
        return True  # Continue even if some checks fail
    
    async def run_all_tests(self):
        """Chạy tất cả test suites"""
        print("🎯 COMPREHENSIVE BACKEND TESTING SUITE")
        print("=" * 70)
        print(f"Target URL: {self.base_url}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites check failed")
            return False
        
        # Define test suites
        test_suites = [
            {
                "name": "Enhanced Groq Integration",
                "type": "sync",
                "command": [sys.executable, "test_enhanced_groq.py"]
            },
            {
                "name": "Comprehensive API Tests",
                "type": "sync", 
                "command": [sys.executable, "comprehensive_test_suite.py", "--url", self.base_url]
            },
            {
                "name": "Database Integration",
                "type": "sync",
                "command": [sys.executable, "database_integration_test.py"]
            },
            {
                "name": "Endpoint Stress Tests",
                "type": "async",
                "module": "endpoint_stress_test"
            }
        ]
        
        # Run each test suite
        for test_suite in test_suites:
            try:
                if test_suite["type"] == "sync":
                    result = self.run_test_suite(test_suite["name"], test_suite["command"])
                else:
                    result = await self.run_async_test_suite(test_suite["name"], test_suite["module"])
                
                self.test_results[test_suite["name"]] = result
                
                # Print immediate result
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                print(f"\n{status} {test_suite['name']} ({result['duration']:.2f}s)")
                
                if not result["success"]:
                    print(f"Error: {result['stderr']}")
                
            except Exception as e:
                print(f"❌ Failed to run {test_suite['name']}: {e}")
                self.test_results[test_suite["name"]] = {
                    "name": test_suite["name"],
                    "success": False,
                    "duration": 0,
                    "stdout": "",
                    "stderr": str(e),
                    "return_code": -1
                }
        
        # Generate comprehensive report
        self.generate_final_report()
        
        # Return overall success
        return all(result["success"] for result in self.test_results.values())
    
    def generate_final_report(self):
        """Tạo báo cáo tổng hợp cuối cùng"""
        total_time = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("📋 FINAL COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Overall statistics
        total_suites = len(self.test_results)
        passed_suites = sum(1 for result in self.test_results.values() if result["success"])
        failed_suites = total_suites - passed_suites
        success_rate = (passed_suites / total_suites) * 100 if total_suites > 0 else 0
        
        print(f"📊 OVERALL STATISTICS:")
        print(f"  Total Test Suites: {total_suites}")
        print(f"  Passed: {passed_suites}")
        print(f"  Failed: {failed_suites}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Total Duration: {total_time:.2f}s")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        for suite_name, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"  {status} {suite_name} ({result['duration']:.2f}s)")
            
            if not result["success"]:
                print(f"    Error: {result['stderr'][:100]}...")
        
        # Performance summary
        durations = [result["duration"] for result in self.test_results.values()]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            print(f"\n⚡ PERFORMANCE SUMMARY:")
            print(f"  Average Suite Duration: {avg_duration:.2f}s")
            print(f"  Longest Suite Duration: {max_duration:.2f}s")
        
        # Deployment readiness assessment
        print(f"\n🎯 DEPLOYMENT READINESS ASSESSMENT:")
        
        if success_rate == 100:
            print("  🎉 EXCELLENT - All tests passed! Ready for production deployment.")
        elif success_rate >= 90:
            print("  ✅ GOOD - Most tests passed. Minor issues may need attention.")
        elif success_rate >= 70:
            print("  ⚠️ MODERATE - Some significant issues found. Review before deployment.")
        else:
            print("  ❌ POOR - Major issues found. DO NOT DEPLOY until fixed.")
        
        # Specific recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        failed_tests = [name for name, result in self.test_results.items() if not result["success"]]
        if failed_tests:
            print(f"  🔧 Fix failing test suites: {', '.join(failed_tests)}")
        
        if total_time > 300:  # 5 minutes
            print(f"  ⚡ Consider optimizing test performance (current: {total_time:.1f}s)")
        
        if success_rate < 100:
            print(f"  📝 Review error logs and fix issues before deployment")
        
        print(f"  🔄 Re-run tests after fixes to ensure stability")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_time": total_time,
            "success_rate": success_rate,
            "test_results": self.test_results
        }
        
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_filename}")
        print("="*80)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Master Test Runner")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--skip-prereq", action="store_true", help="Skip prerequisite checks")
    
    args = parser.parse_args()
    
    # Run all tests
    runner = MasterTestRunner(args.url)
    success = await runner.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
