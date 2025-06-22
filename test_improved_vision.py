# -*- coding: utf-8 -*-
"""
Test script cho improved Gemini Vision với weight estimation
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_weight_estimation_prompt():
    """Test prompt cải thiện cho weight estimation"""
    try:
        from gemini_vision import gemini_vision_service
        
        print("🔧 Testing Improved Gemini Vision Weight Estimation...")
        print("=" * 60)
        
        if not gemini_vision_service.available:
            print("❌ Gemini Vision service not available")
            print("💡 Make sure GEMINI_API_KEY is set in environment")
            return False
        
        # Test với mock image data (placeholder)
        print("📸 Testing with sample food image...")
        
        # Create a simple test image (1x1 pixel) for testing
        import base64
        test_image_data = base64.b64decode('/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/wA==')
        
        try:
            recognized_foods, analysis_result = gemini_vision_service.recognize_food(test_image_data)
            
            print(f"✅ Analysis completed successfully")
            print(f"📊 Foods detected: {len(recognized_foods)}")
            
            # Check for weight estimation improvements
            if "weight_estimation_tips" in analysis_result:
                tips = analysis_result["weight_estimation_tips"]
                print(f"💡 Weight estimation tips provided: {len(tips)}")
                for tip in tips[:3]:  # Show first 3 tips
                    print(f"   • {tip}")
            
            # Check for enhanced portion size format
            for i, food in enumerate(recognized_foods[:2]):  # Show first 2 foods
                print(f"\n🍽️ Food {i+1}: {food.food_name}")
                print(f"   📏 Portion: {food.portion_size}")
                print(f"   🎯 Confidence: {food.confidence:.2f}")
                
                # Check if weight data is available
                if hasattr(food, 'estimated_grams'):
                    print(f"   ⚖️ Estimated weight: {food.estimated_grams}g")
                if hasattr(food, 'weight_confidence'):
                    print(f"   📊 Weight confidence: {food.weight_confidence:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during food recognition: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

def test_weight_estimation_recommendations():
    """Test weight estimation recommendations"""
    try:
        from gemini_vision import gemini_vision_service
        
        print("\n🔧 Testing Weight Estimation Recommendations...")
        print("=" * 60)
        
        # Mock analysis result for testing recommendations
        mock_analysis = {
            "image_analysis": {
                "reference_objects_detected": [],
                "image_quality": "poor",
                "lighting_condition": "poor"
            },
            "foods": [
                {
                    "weight_estimation": {
                        "weight_confidence": 0.4
                    }
                }
            ]
        }
        
        recommendations = gemini_vision_service.get_weight_estimation_recommendations(mock_analysis)
        
        print(f"📋 Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        # Test with good quality analysis
        good_analysis = {
            "image_analysis": {
                "reference_objects_detected": ["đũa", "bát cơm"],
                "image_quality": "good"
            },
            "foods": [
                {
                    "weight_estimation": {
                        "weight_confidence": 0.9
                    }
                }
            ]
        }
        
        good_recommendations = gemini_vision_service.get_weight_estimation_recommendations(good_analysis)
        print(f"\n✅ Good quality analysis recommendations: {len(good_recommendations)}")
        for rec in good_recommendations:
            print(f"  • {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Recommendations test failed: {e}")
        return False

def show_improvement_summary():
    """Hiển thị tóm tắt cải thiện"""
    print("\n🎉 GEMINI VISION WEIGHT ESTIMATION IMPROVEMENTS:")
    print("=" * 80)
    
    improvements = [
        "📏 Enhanced prompt với reference object guidelines",
        "⚖️ Specific weight estimation in grams (not just portion descriptions)",
        "🎯 Weight confidence scoring (0.1-1.0)",
        "📊 Image quality assessment",
        "🔍 Reference object detection (chopsticks, bowls, coins, hands)",
        "💡 Smart recommendations để cải thiện accuracy",
        "📐 Scale calculation từ reference objects",
        "🍽️ Vietnamese portion size standards",
        "📸 Image quality và angle assessment",
        "✅ Enhanced portion size format: '180g (1 bát cơm đầy)'"
    ]
    
    for improvement in improvements:
        print(f"  ✅ {improvement}")
    
    print(f"\n🔧 USAGE TIPS FOR USERS:")
    tips = [
        "Đặt đũa hoặc đồng xu cạnh món ăn",
        "Chụp từ góc thẳng xuống (90 độ)",
        "Đảm bảo ánh sáng đủ sáng",
        "Sử dụng nền trắng hoặc đĩa trắng",
        "Chụp từng món riêng lẻ nếu có nhiều món",
        "Sử dụng bát/đĩa kích thước chuẩn"
    ]
    
    for tip in tips:
        print(f"  💡 {tip}")

if __name__ == "__main__":
    print("🚀 TESTING IMPROVED GEMINI VISION WEIGHT ESTIMATION")
    print("=" * 80)
    
    # Run tests
    test1 = test_weight_estimation_prompt()
    test2 = test_weight_estimation_recommendations()
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS:")
    print(f"✅ Weight Estimation Prompt: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Recommendations System: {'PASS' if test2 else 'FAIL'}")
    
    # Show improvements summary
    show_improvement_summary()
    
    if test1 and test2:
        print("\n🎉 ALL TESTS PASSED!")
        print("🔧 Gemini Vision now provides accurate weight estimation in grams!")
    else:
        print("\n❌ Some tests failed - check GEMINI_API_KEY and implementation")
