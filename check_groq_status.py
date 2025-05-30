import os
from dotenv import load_dotenv
from groq_integration_direct import groq_service

# Load environment variables
load_dotenv()

print(f"GROQ_API_KEY exists: {os.getenv('GROQ_API_KEY') is not None}")
print(f"API key (masked): {'*' * 10 + os.getenv('GROQ_API_KEY')[-5:] if os.getenv('GROQ_API_KEY') else 'None'}")
print(f"Groq service available: {groq_service.available}")
print(f"Groq service model: {groq_service.model}")

# Kiểm tra xem có thể gọi API không
if groq_service.available:
    try:
        print("\nTesting API call...")
        result = groq_service.generate_meal_suggestions(
            calories_target=500,
            protein_target=30,
            fat_target=20,
            carbs_target=50,
            meal_type="breakfast",
            use_ai=True
        )
        
        print(f"API call successful: {result is not None}")
        print(f"Number of meals returned: {len(result) if result else 0}")
        
        if result:
            print("\nFirst meal sample:")
            first_meal = result[0]
            print(f"Name: {first_meal.get('name', 'N/A')}")
            print(f"Ingredients: {len(first_meal.get('ingredients', []))} items")
    except Exception as e:
        print(f"API call failed: {str(e)}")
else:
    print("Groq service is not available, cannot test API call") 