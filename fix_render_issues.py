#!/usr/bin/env python3
"""
Fix common Render deployment issues for Groq integration
Tự động sửa các vấn đề phổ biến khiến Groq fail trên Render
"""

import os
import json
import re

def check_and_fix_requirements():
    """Kiểm tra và sửa requirements.txt"""
    print("🔍 CHECKING REQUIREMENTS.TXT")
    print("=" * 40)
    
    required_packages = {
        "groq": ">=0.4.0",
        "requests": ">=2.25.0",
        "fastapi": ">=0.68.0",
        "uvicorn": ">=0.15.0",
        "python-multipart": ">=0.0.5",
        "firebase-admin": ">=6.0.0",
        "python-dotenv": ">=0.19.0"
    }
    
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print("❌ requirements.txt not found, creating...")
        with open(requirements_file, "w") as f:
            for package, version in required_packages.items():
                f.write(f"{package}{version}\n")
        print("✅ Created requirements.txt")
        return
    
    # Read existing requirements
    with open(requirements_file, "r") as f:
        existing_reqs = f.read()
    
    print(f"📋 Current requirements.txt:")
    print(existing_reqs)
    
    # Check for missing packages
    missing_packages = []
    for package in required_packages:
        if package not in existing_reqs:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️ Missing packages: {missing_packages}")
        
        # Add missing packages
        with open(requirements_file, "a") as f:
            f.write("\n# Added for Groq integration\n")
            for package in missing_packages:
                f.write(f"{package}{required_packages[package]}\n")
        
        print("✅ Added missing packages to requirements.txt")
    else:
        print("✅ All required packages present")

def check_and_fix_environment_handling():
    """Kiểm tra và sửa environment variable handling"""
    print("\n🔧 CHECKING ENVIRONMENT HANDLING")
    print("=" * 45)
    
    # Check if .env file exists (shouldn't be in production)
    if os.path.exists(".env"):
        print("⚠️ .env file found - this should not be deployed to Render")
        print("💡 Make sure .env is in .gitignore")
    
    # Check groq_integration.py for proper env handling
    groq_file = "groq_integration.py"
    if os.path.exists(groq_file):
        with open(groq_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for proper environment variable handling
        if "os.getenv" in content:
            print("✅ Using os.getenv for environment variables")
        else:
            print("⚠️ May not be using os.getenv properly")
        
        # Check for hardcoded API keys
        if re.search(r'api_key\s*=\s*["\'][^"\']+["\']', content):
            print("❌ Possible hardcoded API key found")
        else:
            print("✅ No hardcoded API keys detected")
    
    # Create environment check function
    env_check_code = '''
def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ["GROQ_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ All required environment variables are set")
    return True
'''
    
    print("💡 Add this function to your main.py:")
    print(env_check_code)

def create_render_yaml():
    """Tạo render.yaml cho deployment"""
    print("\n📄 CREATING RENDER.YAML")
    print("=" * 30)
    
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "backend-openfood",
                "env": "python",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
                "envVars": [
                    {
                        "key": "GROQ_API_KEY",
                        "sync": False
                    },
                    {
                        "key": "PYTHON_VERSION",
                        "value": "3.9"
                    }
                ]
            }
        ]
    }
    
    with open("render.yaml", "w") as f:
        import yaml
        yaml.dump(render_config, f, default_flow_style=False)
    
    print("✅ Created render.yaml")
    print("💡 Don't forget to set GROQ_API_KEY in Render dashboard")

def fix_groq_integration_for_render():
    """Sửa groq_integration.py để hoạt động tốt trên Render"""
    print("\n🔧 FIXING GROQ INTEGRATION FOR RENDER")
    print("=" * 50)
    
    groq_file = "groq_integration.py"
    if not os.path.exists(groq_file):
        print("❌ groq_integration.py not found")
        return
    
    with open(groq_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    fixes_applied = []
    
    # Fix 1: Add better error handling for API key
    if "GROQ_API_KEY" in content and "raise" not in content:
        api_key_fix = '''
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY environment variable not set")
            self.available = False
            return
        
        if len(api_key) < 10:
            print("❌ GROQ_API_KEY appears to be invalid")
            self.available = False
            return
'''
        fixes_applied.append("Added API key validation")
    
    # Fix 2: Add timeout handling
    if "timeout" not in content:
        timeout_fix = '''
        # Add timeout to Groq client
        self.client = groq.Groq(
            api_key=api_key,
            timeout=60.0  # 60 second timeout for Render
        )
'''
        fixes_applied.append("Added timeout handling")
    
    # Fix 3: Add retry mechanism
    if "retry" not in content.lower():
        retry_fix = '''
def make_groq_request_with_retry(self, messages, max_retries=3):
    """Make Groq request with retry mechanism for Render"""
    for attempt in range(max_retries):
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0,
                max_tokens=2000,
                timeout=60
            )
            return completion
        except Exception as e:
            print(f"Groq request attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
'''
        fixes_applied.append("Added retry mechanism")
    
    if fixes_applied:
        print(f"✅ Applied fixes: {', '.join(fixes_applied)}")
        print("💡 Manual fixes needed:")
        print("1. Add timeout to Groq client initialization")
        print("2. Add retry mechanism for API calls")
        print("3. Add better error logging")
    else:
        print("✅ No obvious fixes needed")

def create_render_startup_script():
    """Tạo startup script cho Render"""
    print("\n🚀 CREATING RENDER STARTUP SCRIPT")
    print("=" * 40)
    
    startup_script = '''#!/bin/bash
# Render startup script

echo "🚀 Starting backend deployment on Render..."

# Check Python version
python --version

# Check environment variables
echo "Checking environment variables..."
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY not set"
    exit 1
else
    echo "✅ GROQ_API_KEY is set"
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run any pre-startup checks
echo "Running pre-startup checks..."
python -c "
import os
import sys
try:
    import groq
    print('✅ Groq package available')
    
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        client = groq.Groq(api_key=api_key)
        print('✅ Groq client created')
    else:
        print('❌ GROQ_API_KEY not available')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ Groq setup failed: {e}')
    sys.exit(1)
"

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
'''
    
    with open("start.sh", "w", encoding="utf-8") as f:
        f.write(startup_script)
    
    # Make executable
    os.chmod("start.sh", 0o755)
    
    print("✅ Created start.sh")
    print("💡 Update Render start command to: ./start.sh")

def create_render_debug_endpoint():
    """Tạo debug endpoint cho Render"""
    print("\n🔍 CREATING DEBUG ENDPOINT")
    print("=" * 35)
    
    debug_endpoint = '''
@app.get("/debug/groq")
async def debug_groq():
    """Debug endpoint to check Groq integration on Render"""
    import os
    
    debug_info = {
        "groq_api_key_set": bool(os.getenv("GROQ_API_KEY")),
        "groq_api_key_length": len(os.getenv("GROQ_API_KEY", "")),
        "python_version": sys.version,
        "environment": "render" if os.getenv("RENDER") else "local"
    }
    
    # Test Groq import
    try:
        import groq
        debug_info["groq_import"] = "success"
        
        # Test Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                client = groq.Groq(api_key=api_key)
                debug_info["groq_client"] = "success"
                
                # Test simple API call
                completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10,
                    temperature=0.0
                )
                debug_info["groq_api_call"] = "success"
                debug_info["groq_response"] = completion.choices[0].message.content
                
            except Exception as e:
                debug_info["groq_client"] = f"failed: {str(e)}"
        else:
            debug_info["groq_client"] = "no_api_key"
            
    except ImportError as e:
        debug_info["groq_import"] = f"failed: {str(e)}"
    
    return debug_info
'''
    
    print("💡 Add this endpoint to your main.py:")
    print(debug_endpoint)
    print("\n💡 Then test with: GET /debug/groq")

def main():
    """Main fix runner"""
    print("🔧 RENDER GROQ INTEGRATION FIXER")
    print("=" * 50)
    
    # Run all fixes
    check_and_fix_requirements()
    check_and_fix_environment_handling()
    fix_groq_integration_for_render()
    create_render_startup_script()
    create_render_debug_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ RENDER FIXES COMPLETED")
    print("=" * 50)
    
    print("\n📋 DEPLOYMENT CHECKLIST:")
    print("1. ✅ Check requirements.txt")
    print("2. ✅ Add startup script")
    print("3. ✅ Add debug endpoint")
    print("4. 🔲 Set GROQ_API_KEY in Render dashboard")
    print("5. 🔲 Update start command to: ./start.sh")
    print("6. 🔲 Deploy and test /debug/groq endpoint")
    print("7. 🔲 Check Render logs for errors")
    
    print("\n💡 NEXT STEPS:")
    print("1. Commit and push changes")
    print("2. Deploy to Render")
    print("3. Set environment variables in Render dashboard")
    print("4. Test with: python test_production_groq.py <your-render-url>")

if __name__ == "__main__":
    main()
