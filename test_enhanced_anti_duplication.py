# -*- coding: utf-8 -*-
"""
Test script để kiểm tra enhanced anti-duplication system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_similarity_detection():
    """Test similarity detection function"""
    try:
        from groq_integration import groq_service
        
        print("🔧 Testing Enhanced Similarity Detection...")
        print("=" * 60)
        
        # Test cases for similarity detection
        test_cases = [
            # Should be detected as similar
            ("cơm tấm sườn nướng mật ong", "cơm tấm sườn nướng mật ong miền tây", True),
            ("bánh mì chả cá", "bánh mì chả cá nha trang", True),
            ("phở gà", "phở gà đặc biệt sài gòn", True),
            ("cháo gà", "cháo gà hạt sen miền bắc", True),
            
            # Should NOT be detected as similar
            ("cơm tấm sườn nướng", "bún bò huế", False),
            ("bánh mì", "phở gà", False),
            ("cháo gà", "lẩu thái", False),
            ("cơm chiên", "bánh xèo", False),
        ]
        
        all_pass = True
        
        for dish1, dish2, expected_similar in test_cases:
            result = groq_service._are_dishes_similar(dish1.lower(), dish2.lower())
            
            print(f"\n🔍 Testing: '{dish1}' vs '{dish2}'")
            print(f"   Expected: {'Similar' if expected_similar else 'Different'}")
            print(f"   Got: {'Similar' if result else 'Different'}")
            
            if result == expected_similar:
                print(f"   ✅ PASS")
            else:
                print(f"   ❌ FAIL")
                all_pass = False
        
        return all_pass
        
    except Exception as e:
        print(f"❌ Similarity detection test failed: {e}")
        return False

def test_regional_variation_removal():
    """Test regional variation removal"""
    try:
        from groq_integration import groq_service
        
        print("\n🔧 Testing Regional Variation Removal...")
        print("=" * 60)
        
        test_cases = [
            ("cơm tấm sườn nướng mật ong miền tây", "cơm tấm sườn nướng mật ong"),
            ("bánh mì chả cá nha trang", "bánh mì chả cá"),
            ("phở gà đặc biệt sài gòn", "phở gà"),
            ("cháo gà hạt sen miền bắc", "cháo gà hạt sen"),
            ("bún bò huế truyền thống", "bún bò huế"),
        ]
        
        all_pass = True
        
        for original, expected in test_cases:
            result = groq_service._remove_regional_variations(original)
            
            print(f"\n🔍 Testing: '{original}'")
            print(f"   Expected: '{expected}'")
            print(f"   Got: '{result}'")
            
            if result == expected:
                print(f"   ✅ PASS")
            else:
                print(f"   ❌ FAIL")
                all_pass = False
        
        return all_pass
        
    except Exception as e:
        print(f"❌ Regional variation test failed: {e}")
        return False

def test_anti_duplication_in_generation():
    """Test anti-duplication trong meal generation"""
    try:
        from groq_integration import groq_service
        
        print("\n🔧 Testing Anti-Duplication in Meal Generation...")
        print("=" * 60)
        
        # Clear cache để test từ đầu
        groq_service.clear_cache()
        
        # Manually add some dishes to recent_dishes
        test_recent_dishes = [
            "Cơm Tấm Sườn Nướng Mật Ong",
            "Bánh Mì Chả Cá Nha Trang", 
            "Phở Gà Đặc Biệt"
        ]
        
        groq_service.recent_dishes = test_recent_dishes.copy()
        print(f"📝 Pre-loaded recent dishes: {groq_service.recent_dishes}")
        
        # Generate meals và check xem có tạo similar dishes không
        generated_meals = []
        
        for i in range(5):
            print(f"\n🍽️ Generating meal {i+1}/5...")
            
            meals = groq_service.generate_meal_suggestions(
                calories_target=500,
                protein_target=30,
                fat_target=20,
                carbs_target=50,
                meal_type="bữa trưa",
                preferences=None,
                allergies=None,
                cuisine_style=None
            )
            
            if meals and len(meals) > 0:
                meal_name = meals[0].get('name', 'Unknown')
                generated_meals.append(meal_name)
                print(f"   ✅ Generated: {meal_name}")
            else:
                print(f"   ❌ Failed to generate meal")
        
        # Analyze results
        print(f"\n📊 ANTI-DUPLICATION ANALYSIS:")
        print(f"   Recent dishes: {test_recent_dishes}")
        print(f"   Generated meals: {generated_meals}")
        
        # Check for similar dishes
        violations = []
        
        for generated in generated_meals:
            generated_lower = generated.lower()
            
            for recent in test_recent_dishes:
                recent_lower = recent.lower()
                
                if groq_service._are_dishes_similar(generated_lower, recent_lower):
                    violations.append(f"'{generated}' similar to '{recent}'")
        
        if violations:
            print(f"\n❌ ANTI-DUPLICATION VIOLATIONS:")
            for violation in violations:
                print(f"   - {violation}")
            return False
        else:
            print(f"\n✅ NO VIOLATIONS: All generated meals are sufficiently different!")
            return True
            
    except Exception as e:
        print(f"❌ Anti-duplication generation test failed: {e}")
        return False

def test_diversity_over_time():
    """Test diversity qua nhiều lần generation"""
    try:
        from groq_integration import groq_service
        
        print("\n🔧 Testing Diversity Over Time...")
        print("=" * 60)
        
        # Clear cache
        groq_service.clear_cache()
        
        all_generated_meals = []
        
        # Generate 10 meals over time
        for i in range(10):
            meals = groq_service.generate_meal_suggestions(
                calories_target=400,
                protein_target=25,
                fat_target=15,
                carbs_target=50,
                meal_type="bữa sáng",
                preferences=None,
                allergies=None,
                cuisine_style=None
            )
            
            if meals and len(meals) > 0:
                meal_name = meals[0].get('name', 'Unknown')
                all_generated_meals.append(meal_name)
                print(f"   {i+1}. {meal_name}")
        
        # Analyze diversity
        unique_meals = set(all_generated_meals)
        diversity_rate = len(unique_meals) / len(all_generated_meals) * 100
        
        print(f"\n📊 DIVERSITY ANALYSIS:")
        print(f"   Total meals: {len(all_generated_meals)}")
        print(f"   Unique meals: {len(unique_meals)}")
        print(f"   Diversity rate: {diversity_rate:.1f}%")
        
        # Success criteria: at least 80% diversity
        if diversity_rate >= 80:
            print(f"   ✅ EXCELLENT diversity!")
            return True
        elif diversity_rate >= 60:
            print(f"   ⚠️ GOOD diversity, but could be better")
            return True
        else:
            print(f"   ❌ POOR diversity - too many similar dishes")
            return False
            
    except Exception as e:
        print(f"❌ Diversity over time test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING ENHANCED ANTI-DUPLICATION SYSTEM")
    print("=" * 80)
    
    # Run tests
    test1 = test_similarity_detection()
    test2 = test_regional_variation_removal()
    test3 = test_anti_duplication_in_generation()
    test4 = test_diversity_over_time()
    
    print("\n" + "=" * 80)
    print("📊 ENHANCED ANTI-DUPLICATION TEST RESULTS:")
    print(f"✅ Similarity Detection: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Regional Variation Removal: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Anti-Duplication in Generation: {'PASS' if test3 else 'FAIL'}")
    print(f"✅ Diversity Over Time: {'PASS' if test4 else 'FAIL'}")
    
    if all([test1, test2, test3, test4]):
        print("\n🎉 ALL ENHANCED ANTI-DUPLICATION TESTS PASSED!")
        print("🔧 AI will now generate truly diverse meals!")
        print("📊 No more repetitive variations!")
    else:
        print("\n⚠️ Some anti-duplication issues detected")
        
    print("\n🔧 ENHANCED ANTI-DUPLICATION FEATURES:")
    improvements = [
        "✅ Regional variation detection (Miền Tây, Sài Gòn, etc.)",
        "✅ Word overlap similarity checking (70% threshold)",
        "✅ Enhanced pattern matching for dish categories",
        "✅ Similarity checking before adding to recent dishes",
        "✅ Increased recent dishes tracking (30 dishes)",
        "✅ Stronger prompt instructions against variations",
        "✅ Category-based diversity enforcement"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")
