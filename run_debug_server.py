"""
Debug server script.
Run this to start the API server in debug mode.
"""
import subprocess
import sys
import os

def main():
    """Run the FastAPI server with uvicorn"""
    # Get the path to the uvicorn executable
    uvicorn_path = os.path.join(os.path.dirname(sys.executable), "Scripts", "uvicorn.exe")
    if not os.path.exists(uvicorn_path):
        # Try user installation
        user_scripts = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python", "Python311", "Scripts")
        uvicorn_path = os.path.join(user_scripts, "uvicorn.exe")
        if not os.path.exists(uvicorn_path):
            print("Could not find uvicorn executable. Please install it with:")
            print("pip install uvicorn")
            return

    # Run uvicorn
    print(f"Starting server with: {uvicorn_path}")
    subprocess.run([uvicorn_path, "main:app", "--reload"])

if __name__ == "__main__":
    main() 