"""
Test script to verify the fix for preparation field conversion
"""
import sys
import json
from services.firestore_service import FirestoreService
from models import WeeklyMealPlan

def test_transform_meal_plan():
    """Test transforming meal plan data with string preparation to list preparation"""
    # Sample meal plan data from Firestore
    sample_data = {
        "days": [
            {
                "day_of_week": "Thứ 2",
                "breakfast": {
                    "dishes": [
                        {
                            "name": "Bánh Mì Chay Đậu Xanh",
                            "ingredients": [
                                {"name": "Bánh mì", "amount": "1 ổ"},
                                {"name": "Đậu xanh", "amount": "100g"}
                            ],
                            "preparation": "Đặt bánh mì vào lò nướng 2 phút.\nĐậu xanh luộc chín, trộn với rau thơm.\nĐặt đậu xanh lên bánh mì.",
                            "nutrition": {
                                "calories": 148.0,
                                "protein": 11.0,
                                "fat": 4.8,
                                "carbs": 15.0
                            }
                        }
                    ],
                    "nutrition": {
                        "calories": 148.0,
                        "protein": 11.0,
                        "fat": 4.8,
                        "carbs": 15.0
                    }
                },
                "lunch": {
                    "dishes": [
                        {
                            "name": "Cơm Gà",
                            "ingredients": [
                                {"name": "Gạo", "amount": "100g"},
                                {"name": "Thịt gà", "amount": "150g"}
                            ],
                            "preparation": "Nấu cơm với gạo.\nLuộc gà chín, xé nhỏ.\nTrình bày cơm và gà ra đĩa.",
                            "nutrition": {
                                "calories": 250.0,
                                "protein": 20.0,
                                "fat": 5.0,
                                "carbs": 30.0
                            }
                        }
                    ],
                    "nutrition": {
                        "calories": 250.0,
                        "protein": 20.0,
                        "fat": 5.0,
                        "carbs": 30.0
                    }
                },
                "dinner": {
                    "dishes": [
                        {
                            "name": "Bún Chả",
                            "ingredients": [
                                {"name": "Bún", "amount": "100g"},
                                {"name": "Thịt lợn", "amount": "150g"}
                            ],
                            "preparation": "Ướp thịt lợn với gia vị, nướng chín.\nTrụng bún, phục vụ với rau sống.",
                            "nutrition": {
                                "calories": 300.0,
                                "protein": 25.0,
                                "fat": 10.0,
                                "carbs": 35.0
                            }
                        }
                    ],
                    "nutrition": {
                        "calories": 300.0,
                        "protein": 25.0,
                        "fat": 10.0,
                        "carbs": 35.0
                    }
                },
                "nutrition": {
                    "calories": 698.0,
                    "protein": 56.0,
                    "fat": 19.8,
                    "carbs": 80.0
                }
            }
        ]
    }
    
    # Initialize FirestoreService
    firestore_service = FirestoreService()
    
    # Transform data
    print("Transforming meal plan data...")
    transformed_data = firestore_service._transform_meal_plan_data(sample_data)
    
    # Check transformation results
    print("\nChecking transformation results...")
    
    # Check breakfast dish preparation
    breakfast_dish = transformed_data["days"][0]["breakfast"]["dishes"][0]
    print(f"Breakfast dish preparation type: {type(breakfast_dish['preparation'])}")
    print(f"Breakfast dish preparation: {breakfast_dish['preparation']}")
    assert isinstance(breakfast_dish["preparation"], list), "Breakfast dish preparation should be a list"
    
    # Check lunch dish preparation
    lunch_dish = transformed_data["days"][0]["lunch"]["dishes"][0]
    print(f"Lunch dish preparation type: {type(lunch_dish['preparation'])}")
    print(f"Lunch dish preparation: {lunch_dish['preparation']}")
    assert isinstance(lunch_dish["preparation"], list), "Lunch dish preparation should be a list"
    
    # Check dinner dish preparation
    dinner_dish = transformed_data["days"][0]["dinner"]["dishes"][0]
    print(f"Dinner dish preparation type: {type(dinner_dish['preparation'])}")
    print(f"Dinner dish preparation: {dinner_dish['preparation']}")
    assert isinstance(dinner_dish["preparation"], list), "Dinner dish preparation should be a list"
    
    # Validate with Pydantic model
    print("\nValidating with Pydantic model...")
    try:
        meal_plan = WeeklyMealPlan(**transformed_data)
        print("✅ Pydantic validation successful!")
    except Exception as e:
        print(f"❌ Pydantic validation failed: {str(e)}")
        raise
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    print("Bắt đầu kiểm tra sửa lỗi cho trường preparation trong Dish model...")
    
    # Kiểm tra hàm chuyển đổi meal plan
    test_transform_meal_plan()
    
    print("Kiểm tra hoàn tất, mọi thứ hoạt động tốt!") 