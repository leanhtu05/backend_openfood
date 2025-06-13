#!/usr/bin/env python3
"""
Deploy Groq Regex Fix to Render
Commit và push các thay đổi để fix lỗi 'cannot access local variable re'
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description=""):
    """Run a shell command and return result"""
    print(f"🔧 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✅ Success")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Command timeout")
        return False
    except Exception as e:
        print(f"❌ Command error: {e}")
        return False

def check_git_status():
    """Check git status and show changes"""
    print("\n📋 CHECKING GIT STATUS")
    print("=" * 40)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository")
        return False
    
    # Show git status
    run_command("git status --porcelain", "Checking for changes")
    
    # Show specific changes to groq_integration.py
    if os.path.exists('groq_integration.py'):
        print("\n🔍 Changes to groq_integration.py:")
        run_command("git diff groq_integration.py", "Showing groq_integration.py changes")
    
    return True

def commit_and_push_changes():
    """Commit and push the regex fix changes"""
    print("\n📤 COMMITTING AND PUSHING CHANGES")
    print("=" * 50)
    
    # Add changes
    success = run_command("git add .", "Adding all changes")
    if not success:
        return False
    
    # Create commit message
    commit_message = f"Fix Groq regex 're' variable access error - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    commit_command = f'git commit -m "{commit_message}"'
    
    success = run_command(commit_command, "Committing changes")
    if not success:
        print("⚠️ Commit failed - might be no changes to commit")
        return False
    
    # Push to remote
    success = run_command("git push", "Pushing to remote repository")
    if not success:
        print("❌ Push failed - check remote repository access")
        return False
    
    print("✅ Successfully committed and pushed changes!")
    return True

def verify_files_exist():
    """Verify that the fixed files exist"""
    print("\n📁 VERIFYING FILES")
    print("=" * 30)
    
    required_files = [
        "groq_integration.py",
        "test_render_groq_fix.py",
        "main.py"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist

def show_deployment_instructions():
    """Show instructions for Render deployment"""
    print("\n🚀 RENDER DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)
    
    print("1. ✅ Code changes have been pushed to repository")
    print("2. 🔄 Render will automatically detect the changes and redeploy")
    print("3. ⏱️ Wait for deployment to complete (usually 2-5 minutes)")
    print("4. 🧪 Test the fix using:")
    print("   python test_render_groq_fix.py <your-render-url>")
    print("5. 🔍 Check Render logs for any remaining errors")
    print("6. 📊 Monitor the /debug/groq endpoint for status")
    
    print("\n💡 DEBUGGING TIPS:")
    print("- Check Render build logs for import errors")
    print("- Verify GROQ_API_KEY environment variable is set")
    print("- Look for 'cannot access local variable re' in logs")
    print("- Test with simple meal generation requests first")

def main():
    """Main deployment script"""
    print("🔧 GROQ REGEX FIX DEPLOYMENT")
    print("=" * 60)
    print("This script will commit and push the regex fix to resolve:")
    print("'Error generating meal suggestions: cannot access local variable 're'")
    print("=" * 60)
    
    # Verify we have the necessary files
    if not verify_files_exist():
        print("❌ Missing required files. Please ensure all fixes are in place.")
        sys.exit(1)
    
    # Check git status
    if not check_git_status():
        print("❌ Git repository issues. Please resolve before deploying.")
        sys.exit(1)
    
    # Ask for confirmation
    print("\n❓ CONFIRMATION")
    print("=" * 20)
    print("The following changes will be deployed:")
    print("- Fixed regex operations in groq_integration.py")
    print("- Added safe_regex_* helper functions")
    print("- Enhanced error handling for 're' module access")
    print("- Added debug endpoint for troubleshooting")
    
    response = input("\nProceed with deployment? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Deployment cancelled by user")
        sys.exit(0)
    
    # Commit and push changes
    if commit_and_push_changes():
        show_deployment_instructions()
        print("\n✅ DEPLOYMENT INITIATED SUCCESSFULLY!")
        print("🔄 Render will now automatically redeploy your application")
    else:
        print("\n❌ DEPLOYMENT FAILED!")
        print("Please check the errors above and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
