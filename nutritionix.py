import os
import requests
from typing import Dict, List, Optional, Union
from models import NutritionInfo, Ingredient

# Normally, these would be stored securely in environment variables
NUTRITIONIX_APP_ID = "f837778f"
NUTRITIONIX_API_KEY = "90d57371717961de0084daee6fe94f14"

class NutritionixAPI:
    BASE_URL = "https://trackapi.nutritionix.com/v2"
    
    def __init__(self, app_id: str = NUTRITIONIX_APP_ID, api_key: str = NUTRITIONIX_API_KEY):
        self.app_id = app_id
        self.api_key = api_key
        self.headers = {
            "x-app-id": self.app_id,
            "x-app-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def get_nutrition_by_query(self, query: str) -> Optional[NutritionInfo]:
        """
        Get nutrition information from Nutritionix API for a natural language query.
        
        Args:
            query: Natural language description of food (e.g., "100g chicken breast")
            
        Returns:
            NutritionInfo object or None if the API call fails
        """
        endpoint = f"{self.BASE_URL}/natural/nutrients"
        payload = {"query": query}
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if "foods" in data and len(data["foods"]) > 0:
                food = data["foods"][0]
                return NutritionInfo(
                    calories=food.get("nf_calories", 0),
                    protein=food.get("nf_protein", 0),
                    fat=food.get("nf_total_fat", 0),
                    carbs=food.get("nf_total_carbohydrate", 0)
                )
            return None
        except Exception as e:
            print(f"Error getting nutrition data: {e}")
            return None
    
    def get_nutrition_for_ingredients(self, ingredients: List[Ingredient]) -> NutritionInfo:
        """
        Calculate total nutrition for a list of ingredients.
        
        Args:
            ingredients: List of Ingredient objects
            
        Returns:
            NutritionInfo with total nutritional values
        """
        total = NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
        
        for ingredient in ingredients:
            query = f"{ingredient.amount} {ingredient.name}"
            nutrition = self.get_nutrition_by_query(query)
            
            if nutrition:
                total.calories += nutrition.calories
                total.protein += nutrition.protein
                total.fat += nutrition.fat
                total.carbs += nutrition.carbs
        
        return total
    
    def get_dish_suggestions(self, 
                            target_calories: float, 
                            target_protein: float = None,
                            target_fat: float = None,
                            target_carbs: float = None) -> List[Dict]:
        """
        Get dish suggestions based on target nutritional values.
        This is a mock implementation as Nutritionix doesn't provide this functionality directly.
        
        Args:
            target_calories: Target calories for the dish
            target_protein: Target protein in grams (optional)
            target_fat: Target fat in grams (optional)
            target_carbs: Target carbs in grams (optional)
            
        Returns:
            List of dish suggestions with their names and nutritional information
        """
        # This would ideally call an API endpoint to get suggestions
        # For now, we're returning mock suggestions
        
        # For a real implementation, you might use Nutritionix's food database search
        # and filter/sort the results to match the target nutrition values
        
        # Mock response
        suggestions = [
            {
                "name": "Grilled Chicken Salad",
                "nutrition": {
                    "calories": target_calories * 0.9,  # Close to target
                    "protein": target_protein * 1.1 if target_protein else 25,
                    "fat": target_fat * 0.8 if target_fat else 10,
                    "carbs": target_carbs * 0.9 if target_carbs else 15
                }
            },
            {
                "name": "Vegetable Stir Fry with Tofu",
                "nutrition": {
                    "calories": target_calories * 1.1,
                    "protein": target_protein * 0.9 if target_protein else 18,
                    "fat": target_fat * 0.7 if target_fat else 12,
                    "carbs": target_carbs * 1.2 if target_carbs else 25
                }
            }
        ]
        
        return suggestions

# Example of fallback data when API is not available
FALLBACK_NUTRITION_DATA = {
    "chicken breast": NutritionInfo(calories=165, protein=31, fat=3.6, carbs=0),
    "rice": NutritionInfo(calories=130, protein=2.7, fat=0.3, carbs=28),
    "broccoli": NutritionInfo(calories=55, protein=3.7, fat=0.6, carbs=11),
    "salmon": NutritionInfo(calories=208, protein=20, fat=13, carbs=0),
    "egg": NutritionInfo(calories=68, protein=5.5, fat=4.8, carbs=0.6),
    "oatmeal": NutritionInfo(calories=150, protein=5, fat=2.5, carbs=27),
}

def get_nutrition_fallback(ingredient_name: str, amount_str: str = "100g") -> NutritionInfo:
    """
    Get nutrition information from fallback data when API is not available.
    
    Args:
        ingredient_name: Name of the ingredient
        amount_str: Amount string (e.g., "100g")
        
    Returns:
        NutritionInfo object with scaled values based on amount
    """
    # Parse amount (simple implementation, would need to be more robust in production)
    try:
        amount = float(''.join(filter(str.isdigit, amount_str)))
        unit = ''.join(filter(str.isalpha, amount_str))
        
        # Default to 100g if no unit specified
        if not unit:
            unit = 'g'
            
        # Only handle grams for simplicity
        if unit != 'g':
            print(f"Warning: Only gram units supported, treating {amount_str} as {amount}g")
    except:
        amount = 100  # Default to 100g
    
    # Scale factor (relative to 100g)
    scale = amount / 100
    
    # Find the closest matching ingredient in our fallback data
    ingredient_key = next((k for k in FALLBACK_NUTRITION_DATA.keys() 
                          if ingredient_name.lower() in k or k in ingredient_name.lower()), None)
    
    if not ingredient_key:
        # Return default values if no match found
        return NutritionInfo(calories=100 * scale, protein=5 * scale, fat=5 * scale, carbs=10 * scale)
    
    base_nutrition = FALLBACK_NUTRITION_DATA[ingredient_key]
    
    # Scale the nutrition values based on the amount
    return NutritionInfo(
        calories=base_nutrition.calories * scale,
        protein=base_nutrition.protein * scale,
        fat=base_nutrition.fat * scale,
        carbs=base_nutrition.carbs * scale
    )
