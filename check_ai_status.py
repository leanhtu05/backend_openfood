import requests
import json

try:
    # Check AI availability
    response = requests.get('http://localhost:8000/check-ai-availability')
    ai_availability = response.json()
    print("AI Availability:")
    print(json.dumps(ai_availability, indent=2))
    
    # Check API status
    response = requests.get('http://localhost:8000/api-status')
    api_status = response.json()
    print("\nAPI Status:")
    print(json.dumps(api_status, indent=2))
except Exception as e:
    print(f"Error: {e}") 