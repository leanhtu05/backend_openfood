from groq_integration_direct import groq_service
import json

def test_groq_direct():
    """Test Groq API directly"""
    
    print("Checking Groq service...")
    print(f"Groq service available: {groq_service.available}")
    print(f"Groq service model: {groq_service.model}")
    
    # Test generating meal suggestions
    print("\nGenerating meal suggestions...")
    try:
        meal_suggestions = groq_service.generate_meal_suggestions(
            calories_target=500,
            protein_target=30,
            fat_target=20,
            carbs_target=50,
            meal_type="breakfast",
            day_of_week="Thứ 2",
            use_ai=True
        )
        
        print(f"Successfully generated {len(meal_suggestions)} meal suggestions")
        
        for i, meal in enumerate(meal_suggestions):
            print(f"\nMeal {i+1}: {meal.get('name', 'N/A')}")
            print(f"Ingredients: {len(meal.get('ingredients', []))} items")
            print(f"Preparation: {meal.get('preparation', 'N/A')[:50]}...")
            print(f"Nutrition: {meal.get('nutrition', {})}") 
    except Exception as e:
        print(f"Error generating meal suggestions: {str(e)}")

if __name__ == "__main__":
    test_groq_direct() 