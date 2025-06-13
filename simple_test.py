#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Starting test...")

try:
    from groq_integration import GroqService
    print("✅ Import successful")
    
    # Test diverse dish suggestions
    gs = GroqService()
    print("✅ Service created")
    
    # Test diverse dish method
    diverse_dishes = gs._get_diverse_dish_suggestions("bữa sáng", ["healthy"], [])
    print(f"✅ Diverse dishes: {diverse_dishes[:100]}...")
    
    # Test one meal generation
    print("Testing meal generation...")
    meals = gs.generate_meal_suggestions(
        meal_type="bữa sáng",
        calories_target=350,
        protein_target=20,
        fat_target=12,
        carbs_target=40,
        preferences=["healthy"],
        allergies=[],
        cuisine_style="Vietnamese"
    )
    
    if meals:
        print(f"✅ Generated {len(meals)} meals:")
        for meal in meals:
            print(f"   - {meal.get('name', 'Unknown')}")
    else:
        print("❌ No meals generated")
        
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
