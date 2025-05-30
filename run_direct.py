"""
Direct server script to run the app directly without uvicorn.
"""
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 