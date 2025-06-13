#!/usr/bin/env python3
"""
Test Improved Diversity System with Anti-Duplication
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

def test_improved_diversity():
    """Test the improved diversity system"""
    print("🚀 TESTING IMPROVED DIVERSITY SYSTEM")
    print("="*60)
    
    groq_service = GroqService()
    
    # Clear cache to start fresh
    groq_service.cache = {}
    groq_service.recent_dishes = []
    
    all_dishes = []
    test_rounds = 15  # More rounds to test diversity
    
    for round_num in range(1, test_rounds + 1):
        print(f"\n--- Round {round_num}: Generating diverse meals ---")
        
        try:
            # Vary parameters to avoid cache hits
            meal_types = ["bữa sáng", "bữa trưa", "bữa tối"]
            meal_type = meal_types[(round_num - 1) % len(meal_types)]
            
            # Vary nutrition targets slightly
            calories = 350 + (round_num % 5) * 50  # 350-550
            protein = 20 + (round_num % 4) * 5     # 20-35
            fat = 12 + (round_num % 3) * 3         # 12-18
            carbs = 40 + (round_num % 6) * 5       # 40-65
            
            # Vary preferences
            all_preferences = [["healthy"], ["high-protein"], ["vegetarian"], ["low-carb"], []]
            preferences = all_preferences[round_num % len(all_preferences)]
            
            print(f"   🎯 {meal_type} - {calories}kcal, {protein}g protein")
            print(f"   🏷️ Preferences: {preferences}")
            print(f"   📝 Recent dishes: {groq_service.recent_dishes[-3:]}")
            
            meals = groq_service.generate_meal_suggestions(
                meal_type=meal_type,
                calories_target=calories,
                protein_target=protein,
                fat_target=fat,
                carbs_target=carbs,
                preferences=preferences,
                allergies=[],
                cuisine_style="Vietnamese"
            )
            
            if meals and len(meals) > 0:
                print(f"   ✅ Generated {len(meals)} meals")
                
                for i, meal in enumerate(meals, 1):
                    dish_name = meal.get('name', 'Unknown')
                    print(f"      🍽️ Meal {i}: {dish_name}")
                    all_dishes.append(dish_name)
            else:
                print(f"   ❌ No meals generated")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
        
        # Small delay between requests
        time.sleep(0.5)
    
    # Analyze improved diversity
    print(f"\n📊 IMPROVED DIVERSITY ANALYSIS:")
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
        status = "EXCELLENT"
    elif diversity_score >= 60:
        print(f"\n✅ GOOD DIVERSITY: {diversity_score:.1f}%")
        status = "GOOD"
    elif diversity_score >= 40:
        print(f"\n⚠️ MODERATE DIVERSITY: {diversity_score:.1f}%")
        status = "MODERATE"
    else:
        print(f"\n❌ LOW DIVERSITY: {diversity_score:.1f}%")
        status = "LOW"
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"improved_diversity_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_dishes": len(all_dishes),
            "unique_dishes": unique_dishes,
            "duplicate_count": duplicate_count,
            "diversity_rate": diversity_score,
            "status": status,
            "dish_frequency": dict(dish_counter),
            "all_dishes": all_dishes,
            "recent_dishes_tracking": groq_service.recent_dishes
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")
    
    return diversity_score >= 70

def test_cache_effectiveness():
    """Test cache system with diversity"""
    print(f"\n🔄 TESTING CACHE WITH DIVERSITY")
    print("-"*50)
    
    groq_service = GroqService()
    
    # Clear cache
    groq_service.cache = {}
    groq_service.recent_dishes = []
    
    # Test same parameters multiple times
    test_params = {
        "meal_type": "bữa trưa",
        "calories_target": 400,
        "protein_target": 25,
        "fat_target": 15,
        "carbs_target": 45,
        "preferences": ["healthy"],
        "allergies": [],
        "cuisine_style": "Vietnamese"
    }
    
    all_results = []
    
    for i in range(5):
        print(f"\n--- Test {i+1}: Same parameters ---")
        
        meals = groq_service.generate_meal_suggestions(**test_params)
        
        if meals:
            dish_names = [meal.get('name', 'Unknown') for meal in meals]
            all_results.extend(dish_names)
            print(f"   Generated: {', '.join(dish_names)}")
            print(f"   Recent dishes: {groq_service.recent_dishes[-3:]}")
        else:
            print(f"   No meals generated")
        
        time.sleep(0.5)
    
    # Analyze cache effectiveness
    unique_results = len(set(all_results))
    total_results = len(all_results)
    cache_diversity = (unique_results / total_results) * 100 if total_results > 0 else 0
    
    print(f"\n📊 Cache Diversity Analysis:")
    print(f"Total results: {total_results}")
    print(f"Unique results: {unique_results}")
    print(f"Cache diversity: {cache_diversity:.1f}%")
    
    if cache_diversity >= 60:
        print(f"✅ Cache system maintains good diversity")
    else:
        print(f"⚠️ Cache system needs improvement")

def test_anti_duplication_mechanism():
    """Test anti-duplication mechanism specifically"""
    print(f"\n🛡️ TESTING ANTI-DUPLICATION MECHANISM")
    print("-"*50)
    
    groq_service = GroqService()
    
    # Manually set some recent dishes
    groq_service.recent_dishes = ["Phở Bò", "Bún Chả", "Cơm Tấm", "Bánh Mì"]
    print(f"Pre-set recent dishes: {groq_service.recent_dishes}")
    
    # Generate meals and check if they avoid recent dishes
    for i in range(3):
        print(f"\n--- Anti-duplication test {i+1} ---")
        
        meals = groq_service.generate_meal_suggestions(
            meal_type="bữa trưa",
            calories_target=400 + i*50,  # Vary to avoid cache
            protein_target=25,
            fat_target=15,
            carbs_target=45,
            preferences=["healthy"],
            allergies=[],
            cuisine_style="Vietnamese"
        )
        
        if meals:
            for meal in meals:
                dish_name = meal.get('name', 'Unknown')
                if dish_name in groq_service.recent_dishes[:-len(meals)]:  # Exclude just-added dishes
                    print(f"   ⚠️ DUPLICATE DETECTED: {dish_name}")
                else:
                    print(f"   ✅ NEW DISH: {dish_name}")
        
        time.sleep(0.5)

def main():
    """Main function"""
    print("🚀 Starting Improved Diversity Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Improved diversity system
        diversity_success = test_improved_diversity()
        
        # Test 2: Cache effectiveness
        test_cache_effectiveness()
        
        # Test 3: Anti-duplication mechanism
        test_anti_duplication_mechanism()
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if diversity_success:
            print(f"✅ Improved diversity system is working excellently!")
            print(f"🍽️ System successfully provides variety and avoids duplication!")
        else:
            print(f"⚠️ Diversity system still needs further improvements")
            print(f"🔧 Consider additional optimization strategies")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
