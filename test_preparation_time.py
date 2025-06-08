"""
Test script to verify handling of preparation_time and health_benefits fields
"""
import json
from models import Dish, NutritionInfo, Ingredient
from services.firestore_service import firestore_service

def test_dish_serialization():
    """Test that a Dish with preparation_time and health_benefits serializes correctly"""
    # Create a test dish
    dish = Dish(
        name="Test Dish",
        ingredients=[
            Ingredient(name="Ingredient 1", amount="100g"),
            Ingredient(name="Ingredient 2", amount="50g")
        ],
        preparation=["Step 1", "Step 2", "Step 3"],
        nutrition=NutritionInfo(calories=300, protein=20, fat=10, carbs=30),
        preparation_time="30 phút",
        health_benefits=["Giàu protein", "Tốt cho tim mạch", "Hỗ trợ tiêu hóa"]
    )
    
    # Convert to dict and print
    dish_dict = dish.dict()
    print("Dish dict:", json.dumps(dish_dict, indent=2, ensure_ascii=False))
    
    # Verify health_benefits is a string
    assert isinstance(dish_dict["health_benefits"], str)
    assert "Giàu protein" in dish_dict["health_benefits"]
    assert "preparation_time" in dish_dict
    assert dish_dict["preparation_time"] == "30 phút"
    
    print("Dish serialization test passed!")

def test_meal_plan_transformation():
    """Test transformation of meal plan data"""
    # Create a sample meal plan data
    meal_plan_data = {
        "days": [
            {
                "day_of_week": "Thứ 2",
                "breakfast": {
                    "dishes": [
                        {
                            "name": "Test Dish 1",
                            "ingredients": [{"name": "Ingredient 1", "amount": "100g"}],
                            "preparation": "Step 1. Step 2. Step 3.",
                            "nutrition": {"calories": 300, "protein": 20, "fat": 10, "carbs": 30},
                            "preparation_time": "30 phút",
                            "health_benefits": "Giàu protein. Tốt cho tim mạch. Hỗ trợ tiêu hóa."
                        }
                    ],
                    "nutrition": {"calories": 300, "protein": 20, "fat": 10, "carbs": 30}
                },
                "lunch": {
                    "dishes": [
                        {
                            "name": "Test Dish 2",
                            "ingredients": [{"name": "Ingredient 2", "amount": "150g"}],
                            "preparation": "Step 1. Step 2.",
                            "nutrition": {"calories": 400, "protein": 25, "fat": 15, "carbs": 35}
                            # Missing preparation_time and health_benefits
                        }
                    ],
                    "nutrition": {"calories": 400, "protein": 25, "fat": 15, "carbs": 35}
                },
                "dinner": {
                    "dishes": [],
                    "nutrition": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
                },
                "nutrition": {"calories": 700, "protein": 45, "fat": 25, "carbs": 65}
            }
        ]
    }
    
    # Transform the data
    transformed_data = firestore_service._transform_meal_plan_data(meal_plan_data)
    
    # Verify the transformation
    breakfast_dish = transformed_data["days"][0]["breakfast"]["dishes"][0]
    lunch_dish = transformed_data["days"][0]["lunch"]["dishes"][0]
    
    # Check that preparation was converted to a list
    assert isinstance(breakfast_dish["preparation"], list)
    assert len(breakfast_dish["preparation"]) == 3
    
    # Check that health_benefits was converted to a list
    assert isinstance(breakfast_dish["health_benefits"], list)
    assert len(breakfast_dish["health_benefits"]) == 3
    
    # Check that preparation_time was preserved
    assert breakfast_dish["preparation_time"] == "30 phút"
    
    # Check that missing fields were added
    assert "preparation_time" in lunch_dish
    assert lunch_dish["preparation_time"] is None
    assert "health_benefits" in lunch_dish
    assert lunch_dish["health_benefits"] is None
    
    print("Meal plan transformation test passed!")

if __name__ == "__main__":
    print("=== Testing Dish Serialization ===")
    test_dish_serialization()
    print("\n=== Testing Meal Plan Transformation ===")
    test_meal_plan_transformation()
    print("\nAll tests passed!") 