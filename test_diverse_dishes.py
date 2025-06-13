#!/usr/bin/env python3
"""
Test Diverse Vietnamese Dish Generation System
"""

import sys
import os
import json
import time
from datetime import datetime
from collections import Counter

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groq_integration import GroqService

def test_dish_diversity():
    """Test the diversity of generated dishes"""
    print("🍽️ TESTING DIVERSE VIETNAMESE DISH GENERATION")
    print("="*60)
    
    groq_service = GroqService()
    
    # Test multiple generations to check for diversity
    all_dishes = []
    test_rounds = 10  # Generate 10 rounds of meals
    
    for round_num in range(1, test_rounds + 1):
        print(f"\n--- Round {round_num}: Generating meals ---")
        
        try:
            # Alternate between different meal types
            meal_types = ["bữa sáng", "bữa trưa", "bữa tối"]
            meal_type = meal_types[(round_num - 1) % len(meal_types)]
            
            meals = groq_service.generate_meal_suggestions(
                meal_type=meal_type,
                calories_target=400,
                protein_target=25,
                fat_target=15,
                carbs_target=45,
                preferences=["healthy"],
                allergies=[],
                cuisine_style="Vietnamese"
            )
            
            if meals and len(meals) > 0:
                print(f"✅ Generated {len(meals)} meals for {meal_type}")
                
                for i, meal in enumerate(meals, 1):
                    dish_name = meal.get('name', 'Unknown')
                    print(f"   🍽️ Meal {i}: {dish_name}")
                    all_dishes.append(dish_name)
            else:
                print(f"❌ No meals generated for {meal_type}")
                
        except Exception as e:
            print(f"💥 Error in round {round_num}: {str(e)}")
        
        # Small delay between requests
        time.sleep(1)
    
    # Analyze diversity
    print(f"\n📊 DIVERSITY ANALYSIS:")
    print(f"Total dishes generated: {len(all_dishes)}")
    
    # Count unique dishes
    dish_counter = Counter(all_dishes)
    unique_dishes = len(dish_counter)
    duplicate_count = len(all_dishes) - unique_dishes
    
    print(f"Unique dishes: {unique_dishes}")
    print(f"Duplicate dishes: {duplicate_count}")
    print(f"Diversity rate: {(unique_dishes / len(all_dishes) * 100):.1f}%")
    
    # Show most common dishes
    print(f"\n🔄 Most common dishes:")
    for dish, count in dish_counter.most_common(5):
        print(f"   {dish}: {count} times")
    
    # Show all unique dishes
    print(f"\n🍽️ All unique dishes generated:")
    for dish in sorted(dish_counter.keys()):
        print(f"   - {dish}")
    
    # Diversity score
    diversity_score = (unique_dishes / len(all_dishes)) * 100 if all_dishes else 0
    
    if diversity_score >= 80:
        print(f"\n🎉 EXCELLENT DIVERSITY: {diversity_score:.1f}%")
    elif diversity_score >= 60:
        print(f"\n✅ GOOD DIVERSITY: {diversity_score:.1f}%")
    elif diversity_score >= 40:
        print(f"\n⚠️ MODERATE DIVERSITY: {diversity_score:.1f}%")
    else:
        print(f"\n❌ LOW DIVERSITY: {diversity_score:.1f}%")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"diversity_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_dishes": len(all_dishes),
            "unique_dishes": unique_dishes,
            "duplicate_count": duplicate_count,
            "diversity_rate": diversity_score,
            "dish_frequency": dict(dish_counter),
            "all_dishes": all_dishes
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")
    
    return diversity_score >= 60

def test_meal_type_diversity():
    """Test diversity within specific meal types"""
    print(f"\n🍽️ TESTING MEAL TYPE SPECIFIC DIVERSITY")
    print("-"*50)
    
    groq_service = GroqService()
    
    meal_types = ["bữa sáng", "bữa trưa", "bữa tối"]
    
    for meal_type in meal_types:
        print(f"\n--- Testing {meal_type} diversity ---")
        
        dishes_for_meal_type = []
        
        # Generate 5 rounds for each meal type
        for round_num in range(1, 6):
            try:
                meals = groq_service.generate_meal_suggestions(
                    meal_type=meal_type,
                    calories_target=350 + round_num * 50,  # Vary calories
                    protein_target=20 + round_num * 5,     # Vary protein
                    fat_target=12 + round_num * 2,         # Vary fat
                    carbs_target=40 + round_num * 5,       # Vary carbs
                    preferences=["healthy"],
                    allergies=[],
                    cuisine_style="Vietnamese"
                )
                
                if meals:
                    for meal in meals:
                        dish_name = meal.get('name', 'Unknown')
                        dishes_for_meal_type.append(dish_name)
                        print(f"   Round {round_num}: {dish_name}")
                
                time.sleep(0.5)  # Small delay
                
            except Exception as e:
                print(f"   Error in round {round_num}: {str(e)}")
        
        # Analyze diversity for this meal type
        if dishes_for_meal_type:
            counter = Counter(dishes_for_meal_type)
            unique = len(counter)
            total = len(dishes_for_meal_type)
            diversity = (unique / total) * 100
            
            print(f"   📊 {meal_type} diversity: {unique}/{total} = {diversity:.1f}%")
            print(f"   🍽️ Unique dishes: {', '.join(counter.keys())}")
        else:
            print(f"   ❌ No dishes generated for {meal_type}")

def test_preference_filtering():
    """Test how preferences affect dish diversity"""
    print(f"\n🎯 TESTING PREFERENCE-BASED FILTERING")
    print("-"*50)
    
    groq_service = GroqService()
    
    preference_tests = [
        {"preferences": ["healthy"], "name": "Healthy"},
        {"preferences": ["high-protein"], "name": "High Protein"},
        {"preferences": ["vegetarian"], "name": "Vegetarian"},
        {"preferences": ["low-carb"], "name": "Low Carb"}
    ]
    
    for test in preference_tests:
        print(f"\n--- Testing {test['name']} preferences ---")
        
        dishes = []
        for i in range(3):  # 3 rounds per preference
            try:
                meals = groq_service.generate_meal_suggestions(
                    meal_type="bữa trưa",
                    calories_target=400,
                    protein_target=25,
                    fat_target=15,
                    carbs_target=45,
                    preferences=test["preferences"],
                    allergies=[],
                    cuisine_style="Vietnamese"
                )
                
                if meals:
                    for meal in meals:
                        dish_name = meal.get('name', 'Unknown')
                        dishes.append(dish_name)
                        print(f"   Round {i+1}: {dish_name}")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   Error in round {i+1}: {str(e)}")
        
        if dishes:
            unique_dishes = len(set(dishes))
            print(f"   📊 Generated {unique_dishes} unique dishes: {', '.join(set(dishes))}")
        else:
            print(f"   ❌ No dishes generated for {test['name']} preferences")

def main():
    """Main function"""
    print("🚀 Starting Diverse Vietnamese Dish Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Overall diversity
        diversity_success = test_dish_diversity()
        
        # Test 2: Meal type specific diversity
        test_meal_type_diversity()
        
        # Test 3: Preference filtering
        test_preference_filtering()
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if diversity_success:
            print(f"✅ Diverse dish generation is working excellently!")
            print(f"🍽️ System successfully avoids duplication and provides variety!")
        else:
            print(f"⚠️ Diversity system needs improvements")
            print(f"🔧 Consider expanding dish database or improving anti-duplication logic")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
