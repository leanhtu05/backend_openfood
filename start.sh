#!/bin/bash
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
