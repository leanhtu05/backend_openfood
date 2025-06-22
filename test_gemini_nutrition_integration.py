# -*- coding: utf-8 -*-
"""
Test script cho Gemini Vision integration với Vietnamese nutrition databases
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_official_nutrition_lookup():
    """Test lookup dữ liệu dinh dưỡng chính thức"""
    try:
        from gemini_vision import gemini_vision_service
        
        print("🔧 Testing Official Nutrition Data Lookup...")
        print("=" * 60)
        
        # Test cases với các món ăn từ Gemini Vision
        test_foods = [
            {"name": "Cơm chiên gà", "grams": 300},
            {"name": "Gà", "grams": 150},
            {"name": "Rau củ", "grams": 100},
            {"name": "phở bò", "grams": 500},
            {"name": "cơm tấm", "grams": 300},
            {"name": "thịt bò", "grams": 100},
            {"name": "rau muống", "grams": 80},
            {"name": "trứng gà", "grams": 60},
            {"name": "tôm", "grams": 120},
            {"name": "cà rốt", "grams": 100}
        ]
        
        official_count = 0
        extended_count = 0
        not_found_count = 0
        
        for food in test_foods:
            nutrition_data = gemini_vision_service.get_official_nutrition_data(
                food["name"], food["grams"]
            )
            
            print(f"\n🍽️ {food['name']} ({food['grams']}g):")
            
            if nutrition_data:
                data_quality = nutrition_data.get("data_quality", "unknown")
                if data_quality == "official_dish":
                    official_count += 1
                    print(f"   ✅ Official dish data: {nutrition_data['calories']} kcal")
                elif data_quality == "official_ingredient":
                    official_count += 1
                    print(f"   ✅ Official ingredient data: {nutrition_data['calories']} kcal")
                elif data_quality == "extended_database":
                    extended_count += 1
                    print(f"   📊 Extended database: {nutrition_data['calories']} kcal")
                
                print(f"   📋 Source: {nutrition_data['source']}")
                print(f"   🔢 Nutrition: {nutrition_data['protein']}g protein, {nutrition_data['fat']}g fat, {nutrition_data['carbs']}g carbs")
            else:
                not_found_count += 1
                print(f"   ❌ No nutrition data found")
        
        total_foods = len(test_foods)
        coverage = ((official_count + extended_count) / total_foods) * 100
        
        print(f"\n📊 COVERAGE RESULTS:")
        print(f"✅ Official database: {official_count}/{total_foods}")
        print(f"📊 Extended database: {extended_count}/{total_foods}")
        print(f"❌ Not found: {not_found_count}/{total_foods}")
        print(f"📈 Total coverage: {coverage:.1f}%")
        
        return coverage >= 75  # Expect at least 75% coverage
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_nutrition_accuracy():
    """Test độ chính xác của nutrition data"""
    try:
        from gemini_vision import gemini_vision_service
        
        print("\n🔧 Testing Nutrition Data Accuracy...")
        print("=" * 60)
        
        # Test với phở bò - món có data chính thức
        pho_nutrition = gemini_vision_service.get_official_nutrition_data("phở bò", 500)
        
        if pho_nutrition:
            print(f"🍜 Phở bò (500g):")
            print(f"   📊 {pho_nutrition['calories']} kcal")
            print(f"   🥩 {pho_nutrition['protein']}g protein")
            print(f"   🧈 {pho_nutrition['fat']}g fat")
            print(f"   🍞 {pho_nutrition['carbs']}g carbs")
            print(f"   📋 Source: {pho_nutrition['source']}")
            
            # Kiểm tra tính hợp lý
            calories = pho_nutrition['calories']
            protein = pho_nutrition['protein']
            fat = pho_nutrition['fat']
            carbs = pho_nutrition['carbs']
            
            # Tính calories từ macros
            calculated_calories = (protein * 4) + (fat * 9) + (carbs * 4)
            calorie_diff = abs(calculated_calories - calories) / calories
            
            print(f"   🧮 Calculated calories: {calculated_calories:.1f}")
            print(f"   📏 Difference: {calorie_diff:.1%}")
            
            if calorie_diff < 0.2:  # Less than 20% difference
                print(f"   ✅ Nutrition data is consistent")
                return True
            else:
                print(f"   ⚠️ Large discrepancy in nutrition data")
                return False
        else:
            print(f"❌ No data found for phở bò")
            return False
            
    except Exception as e:
        print(f"❌ Accuracy test failed: {e}")
        return False

def test_extended_database_integration():
    """Test tích hợp với extended database"""
    try:
        from gemini_vision import gemini_vision_service
        
        print("\n🔧 Testing Extended Database Integration...")
        print("=" * 60)
        
        # Test với các nguyên liệu từ extended database
        extended_foods = [
            {"name": "bầu", "grams": 100},
            {"name": "cà tím", "grams": 100},
            {"name": "cải bắp", "grams": 100},
            {"name": "thịt heo", "grams": 100}
        ]
        
        found_count = 0
        
        for food in extended_foods:
            nutrition_data = gemini_vision_service.get_extended_nutrition_data(
                food["name"], food["grams"]
            )
            
            print(f"\n🥬 {food['name']} ({food['grams']}g):")
            
            if nutrition_data:
                found_count += 1
                print(f"   ✅ Found: {nutrition_data['calories']} kcal")
                print(f"   📊 {nutrition_data['protein']}g protein, {nutrition_data['fat']}g fat")
                print(f"   📋 Source: {nutrition_data['source']}")
            else:
                print(f"   ❌ Not found in extended database")
        
        coverage = (found_count / len(extended_foods)) * 100
        print(f"\n📈 Extended database coverage: {coverage:.1f}%")
        
        return coverage >= 50  # Expect at least 50% coverage
        
    except Exception as e:
        print(f"❌ Extended database test failed: {e}")
        return False

def show_integration_summary():
    """Hiển thị tóm tắt tích hợp"""
    print("\n🎉 GEMINI VISION + VIETNAMESE NUTRITION INTEGRATION:")
    print("=" * 80)
    
    features = [
        "🏛️ Official Vietnamese nutrition database integration",
        "📊 Extended nutrition database fallback",
        "🔍 Smart food name normalization",
        "⚖️ Accurate weight-based nutrition calculation",
        "📋 Data source tracking và quality indicators",
        "🎯 Priority system: Official > Extended > Gemini estimates",
        "✅ Consistent nutrition data validation",
        "🇻🇳 Vietnamese food-specific portion standards",
        "📈 High coverage for common Vietnamese foods",
        "🔧 Fallback system for unknown foods"
    ]
    
    for feature in features:
        print(f"  ✅ {feature}")
    
    print(f"\n🔧 DATA SOURCES PRIORITY:")
    sources = [
        "1. Viện Dinh dưỡng Quốc gia (Official dishes)",
        "2. Bảng thành phần dinh dưỡng thực phẩm VN (Official ingredients)",
        "3. Vietnamese Extended Nutrition Database",
        "4. Gemini AI estimates (fallback)"
    ]
    
    for source in sources:
        print(f"  📊 {source}")

if __name__ == "__main__":
    print("🚀 TESTING GEMINI VISION + VIETNAMESE NUTRITION INTEGRATION")
    print("=" * 80)
    
    # Run tests
    test1 = test_official_nutrition_lookup()
    test2 = test_nutrition_accuracy()
    test3 = test_extended_database_integration()
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS:")
    print(f"✅ Official Nutrition Lookup: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Nutrition Data Accuracy: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Extended Database Integration: {'PASS' if test3 else 'FAIL'}")
    
    # Show integration summary
    show_integration_summary()
    
    if all([test1, test2, test3]):
        print("\n🎉 ALL TESTS PASSED!")
        print("🔧 Gemini Vision now uses official Vietnamese nutrition data!")
        print("📊 Accurate weight estimation + official nutrition = precise food tracking!")
    else:
        print("\n❌ Some tests failed - check database integration")
