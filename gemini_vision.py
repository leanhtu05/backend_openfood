"""
Service for food recognition using Gemini Vision Pro API
"""
import os
import base64
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import models
from models import RecognizedFood, NutritionInfo

# Import Vietnamese nutrition databases
from vietnamese_nutrition_database import (
    get_ingredient_nutrition,
    get_dish_nutrition,
    calculate_dish_nutrition_from_ingredients,
    VIETNAMESE_NUTRITION_DATABASE,
    VIETNAMESE_DISHES_NUTRITION
)
from vietnamese_nutrition_extended import (
    VEGETABLES_NUTRITION, FRUITS_NUTRITION, MEAT_NUTRITION,
    SEAFOOD_NUTRITION, EGGS_NUTRITION, DAIRY_NUTRITION
)
from vietnamese_traditional_dishes import ALL_TRADITIONAL_DISHES
from groq_integration import GroqService

# Try to import Gemini from Google Generative AI SDK
try:
    import google.generativeai as genai
    from google.generativeai.types.generation_types import GenerationConfig
    GEMINI_AVAILABLE = True
except ImportError:
    print("Google Generative AI SDK not installed. Use 'pip install google-generativeai'")
    GEMINI_AVAILABLE = False

class GeminiVisionService:
    """Service for food recognition using Google's Gemini Vision Pro"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini Vision service with API key
        
        Args:
            api_key: Gemini API key, from environment variable if not provided
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.available = GEMINI_AVAILABLE and self.api_key is not None
        
        # Initialize model
        if self.available:
            try:
                print("\n=== INITIALIZING GEMINI VISION SERVICE ===")
                print(f"API Key exists: {self.api_key is not None}")
                
                # Configure API key
                genai.configure(api_key=self.api_key)
                
                # Get Gemini Vision model
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                print("Gemini Vision service initialized successfully")
                print("=== GEMINI VISION SERVICE INITIALIZED ===\n")
            except Exception as e:
                print(f"ERROR initializing Gemini Vision: {str(e)}")
                import traceback
                traceback.print_exc()
                self.available = False
                self.model = None
        else:
            print("Gemini Vision service not available. Make sure to set GEMINI_API_KEY.")
            self.model = None
            
    def recognize_food(self, image_data: bytes) -> Tuple[List[RecognizedFood], Dict[str, Any]]:
        """
        Recognize food in an image using Gemini Vision Pro
        
        Args:
            image_data: Image bytes
            
        Returns:
            Tuple of recognized foods list and raw analysis
        """
        if not self.available or not self.model:
            raise ValueError("Gemini Vision service is not available.")
            
        try:
            # Encode image to base64 for API
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare prompt for Gemini Vision
            prompt = """
            Analyze this food image and identify EACH INDIVIDUAL FOOD COMPONENT separately with ACCURATE WEIGHT ESTIMATION:

            🔧 WEIGHT ESTIMATION GUIDELINES:
            1. Look for reference objects in the image (chopsticks, spoons, bowls, plates, hands, coins)
            2. Use these reference objects to estimate scale and actual food portions
            3. Consider typical Vietnamese portion sizes:
               - Cơm (rice): 150-200g per serving
               - Phở noodles: 200-250g per bowl
               - Bún: 150-200g per serving
               - Thịt (meat): 80-150g per portion
               - Rau (vegetables): 50-100g per serving
               - Canh (soup): 200-300ml per bowl

            🍽️ REFERENCE OBJECT SIZES (for scale):
            - Đũa (chopsticks): 23cm long
            - Thìa cơm (spoon): 15cm long
            - Bát cơm (rice bowl): 11.5cm diameter
            - Đĩa (plate): 20cm diameter
            - Đồng xu 500 VND: 2.4cm diameter
            - Bàn tay người lớn: ~18cm long

            IMPORTANT: Break down complex dishes into individual components!

            Examples:
            - Bún chả → ["Bún 180g", "Chả cá 100g", "Rau sống 60g", "Nước mắm pha 50ml"]
            - Mâm cơm → ["Cơm trắng 180g", "Thịt kho 120g", "Canh chua 250ml", "Rau muống xào 80g"]
            - Phở bò → ["Bánh phở 220g", "Thịt bò 90g", "Nước dùng 400ml", "Hành lá 10g", "Ngò gai 5g"]

            1. Identify ALL individual food components visible in the image
            2. For each component, provide:
               - Name of the food component (in Vietnamese and English)
               - ACCURATE weight estimate in grams (or ml for liquids)
               - Confidence level for weight estimation (0.1-1.0)
               - Reference objects used for scale estimation
               - FOCUS ON BASIC NUTRITION DATA (calories, protein, fat, carbs, fiber)
               - The system will automatically lookup official Vietnamese nutrition data
               - Only provide estimated nutrition if you're confident about the food type
               - Use realistic Vietnamese portion nutrition values:
                 * Cơm (150g): ~195 kcal, 4g protein, 0.4g fat, 43g carbs
                 * Phở bò (1 tô): ~420 kcal, 25g protein, 12g fat, 58g carbs
                 * Thịt heo (100g): ~242 kcal, 27g protein, 14g fat, 0g carbs
                 * Rau muống (80g): ~15 kcal, 2g protein, 0.2g fat, 2.5g carbs

            Return your analysis in this exact JSON format:
            {
              "image_analysis": {
                "reference_objects_detected": ["đũa", "bát cơm"],
                "image_quality": "good|fair|poor",
                "lighting_condition": "good|fair|poor",
                "angle_assessment": "optimal|acceptable|suboptimal"
              },
              "foods": [
                {
                  "name_vi": "Vietnamese name",
                  "name_en": "English name",
                  "confidence": 0.95,
                  "weight_estimation": {
                    "estimated_grams": 180,
                    "weight_confidence": 0.85,
                    "estimation_method": "reference_object|visual_comparison|standard_portion",
                    "reference_used": "đũa 23cm",
                    "portion_description": "1 bát cơm đầy"
                  },
                  "nutrition": {
                    "calories": 200,
                    "protein": 10,
                    "fat": 5,
                    "carbs": 30,
                    "fiber": 3,
                    "sugar": 8,
                    "saturated_fat": 2,
                    "trans_fat": 0,
                    "cholesterol": 15,
                    "sodium": 300,
                    "potassium": 150,
                    "calcium": 50,
                    "iron": 2,
                    "vitamin_c": 10,
                    "vitamin_a": 100,
                    "caffeine": 0,
                    "alcohol": 0,
                    "glycemic_index": 55,
                    "water_content": 85
                  }
                }
              ]
            }

            🎯 WEIGHT ESTIMATION ACCURACY GUIDELINES:
            - PRIORITY 1: Look for reference objects first (chopsticks, spoons, coins, hands)
            - PRIORITY 2: Compare food size to standard containers (bowls, plates, cups)
            - PRIORITY 3: Use visual estimation based on typical Vietnamese portions
            - Be conservative with estimates - better to underestimate than overestimate
            - Consider food density: rice is denser than noodles, meat is denser than vegetables
            - Account for perspective and camera angle in your estimation
            - If multiple reference objects are visible, use the most reliable one
            - Provide weight_confidence based on available visual cues:
              * 0.9-1.0: Clear reference objects + good angle + good lighting
              * 0.7-0.8: Some reference objects or clear portion indicators
              * 0.5-0.6: Visual estimation only, no clear references
              * 0.3-0.4: Poor image quality or unclear portions

            Important guidelines:
            - ALWAYS break down complex dishes into individual components
            - Each component should be listed separately with its own weight and nutrition
            - For combo dishes (like bún chả), list each part with individual weights
            - For meals with multiple dishes, list each dish separately with weights
            - Provide realistic estimates based on typical nutritional values for each component
            - Use null for nutrients that are not applicable (e.g., caffeine in vegetables)
            - For glycemic index: Low (0-55), Medium (56-69), High (70-100)
            - Water content as percentage (0-100)
            - All mineral/vitamin values should be reasonable for the portion size
            - Do not include explanations or text outside the JSON
            - Focus on ACCURATE WEIGHT ESTIMATION as the primary goal
            """
            
            # Configure generation parameters
            generation_config = GenerationConfig(
                temperature=0.4,
                top_p=1.0,
                top_k=32,
                max_output_tokens=2048,
            )
            
            # Call Gemini Vision API
            response = self.model.generate_content(
                contents=[
                    {"role": "user", "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}}
                    ]}
                ],
                generation_config=generation_config
            )
            
            # Extract response text
            result_text = response.text
            
            # Parse JSON from response
            try:
                # Find JSON in response (handle if there's text around it)
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    result = {"foods": []}
            except json.JSONDecodeError:
                result = {"foods": []}
                print(f"Error parsing JSON from Gemini response: {result_text[:500]}")
                
            # Extract image analysis info
            image_analysis = result.get("image_analysis", {})
            reference_objects = image_analysis.get("reference_objects_detected", [])
            image_quality = image_analysis.get("image_quality", "fair")

            # Convert to RecognizedFood objects
            recognized_foods = []
            for food in result.get("foods", []):
                # Use Vietnamese name if available, fallback to English
                food_name = food.get("name_vi") or food.get("name_en") or "Không xác định"

                # Extract weight estimation data
                weight_data = food.get("weight_estimation", {})
                estimated_grams = weight_data.get("estimated_grams", 100)  # Default 100g
                weight_confidence = weight_data.get("weight_confidence", 0.5)
                estimation_method = weight_data.get("estimation_method", "visual_comparison")
                reference_used = weight_data.get("reference_used", "none")
                portion_description = weight_data.get("portion_description", "Không xác định")

                # Create enhanced portion size string with weight
                enhanced_portion_size = f"{estimated_grams}g ({portion_description})"

                # Create NutritionInfo from response with comprehensive data (optional)
                nutrition_data = food.get("nutrition", {})

                # Helper function to safely convert to float or None
                def safe_float(value):
                    if value is None or value == "":
                        return None
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return None

                # Helper function to safely convert to int or None
                def safe_int(value):
                    if value is None or value == "":
                        return None
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return None

                # 🔧 FIX: Ưu tiên dữ liệu dinh dưỡng chính thức từ database Việt Nam
                official_nutrition = self.get_official_nutrition_data(food_name, estimated_grams)

                if official_nutrition:
                    # Sử dụng dữ liệu chính thức
                    print(f"✅ Using official nutrition data for {food_name}: {official_nutrition['source']}")
                    nutrition = NutritionInfo(
                        # Basic nutrition từ database chính thức
                        calories=float(official_nutrition["calories"]),
                        protein=float(official_nutrition["protein"]),
                        fat=float(official_nutrition["fat"]),
                        carbs=float(official_nutrition["carbs"]),

                        # Detailed nutrition với estimates hợp lý
                        fiber=float(official_nutrition["fiber"]),
                        sugar=float(official_nutrition["carbs"]) * 0.1,  # Estimate 10% of carbs as sugar
                        saturated_fat=float(official_nutrition["fat"]) * 0.3,  # Estimate 30% of fat as saturated
                        trans_fat=0.0,
                        cholesterol=20.0 if "thịt" in food_name.lower() or "trứng" in food_name.lower() else 0.0,
                        sodium=float(official_nutrition["sodium"]),
                        potassium=100.0,  # Default estimate
                        calcium=50.0,     # Default estimate
                        iron=2.0,         # Default estimate
                        vitamin_c=5.0,    # Default estimate
                        vitamin_a=50.0,   # Default estimate
                        caffeine=0.0,
                        alcohol=0.0,
                        glycemic_index=55,  # Medium GI default
                        water_content=70.0  # Default water content
                    )

                    # Update portion size với data quality info
                    enhanced_portion_size = f"{estimated_grams}g ({portion_description}) - {official_nutrition['data_quality']}"

                else:
                    # Fallback to Gemini's nutrition data
                    print(f"⚠️ Using Gemini nutrition data for {food_name} (no official data found)")
                    nutrition_data = food.get("nutrition", {})

                    nutrition = NutritionInfo(
                        # Basic nutrition (required)
                        calories=float(nutrition_data.get("calories", 100)),
                        protein=float(nutrition_data.get("protein", 5)),
                        fat=float(nutrition_data.get("fat", 3)),
                        carbs=float(nutrition_data.get("carbs", 15)),

                        # Detailed nutrition (optional)
                        fiber=safe_float(nutrition_data.get("fiber")) or 2.0,
                        sugar=safe_float(nutrition_data.get("sugar")) or 5.0,
                        saturated_fat=safe_float(nutrition_data.get("saturated_fat")) or 1.0,
                        trans_fat=safe_float(nutrition_data.get("trans_fat")) or 0.0,
                        cholesterol=safe_float(nutrition_data.get("cholesterol")) or 10.0,
                        sodium=safe_float(nutrition_data.get("sodium")) or 100.0,
                        potassium=safe_float(nutrition_data.get("potassium")) or 150.0,
                        calcium=safe_float(nutrition_data.get("calcium")) or 50.0,
                        iron=safe_float(nutrition_data.get("iron")) or 2.0,
                        vitamin_c=safe_float(nutrition_data.get("vitamin_c")) or 5.0,
                        vitamin_a=safe_float(nutrition_data.get("vitamin_a")) or 50.0,
                        caffeine=safe_float(nutrition_data.get("caffeine")) or 0.0,
                        alcohol=safe_float(nutrition_data.get("alcohol")) or 0.0,
                        glycemic_index=safe_int(nutrition_data.get("glycemic_index")) or 55,
                        water_content=safe_float(nutrition_data.get("water_content")) or 70.0
                    )
                
                # Create RecognizedFood object with enhanced weight data
                recognized_food = RecognizedFood(
                    food_name=food_name,
                    confidence=float(food.get("confidence", 0.5)),
                    nutrition=nutrition,
                    portion_size=enhanced_portion_size
                )

                # Add weight estimation metadata to the object (if RecognizedFood supports it)
                if hasattr(recognized_food, 'estimated_grams'):
                    recognized_food.estimated_grams = estimated_grams
                if hasattr(recognized_food, 'weight_confidence'):
                    recognized_food.weight_confidence = weight_confidence
                if hasattr(recognized_food, 'estimation_method'):
                    recognized_food.estimation_method = estimation_method
                if hasattr(recognized_food, 'reference_used'):
                    recognized_food.reference_used = reference_used
                
                recognized_foods.append(recognized_food)
                
            # Add weight estimation recommendations to result
            result["weight_estimation_tips"] = self.get_weight_estimation_recommendations(result)

            return recognized_foods, result

        except Exception as e:
            print(f"Error recognizing food with Gemini: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return empty results on error
            return [], {"error": str(e)}

    def normalize_food_name(self, food_name: str) -> List[str]:
        """
        🔧 FIX: Chuẩn hóa và tạo các biến thể tên món ăn để tìm kiếm
        """
        normalized_name = food_name.lower().strip()

        # Tạo danh sách các biến thể tên để tìm kiếm
        variations = [normalized_name]

        # Mapping các tên thường gặp
        name_mappings = {
            # Món cơm
            "cơm chiên": "cơm rang",
            "cơm chiên gà": "cơm rang",
            "cơm chiên thịt": "cơm rang",

            # Thịt gà
            "gà": "thịt gà ta",
            "thịt gà": "thịt gà ta",
            "gà ta": "thịt gà ta",
            "gà rán": "thịt gà ta",
            "gà nướng": "thịt gà ta",

            # Thịt heo/lợn
            "thịt heo": "thịt lợn nạc",
            "heo": "thịt lợn nạc",
            "lợn": "thịt lợn nạc",
            "thịt ba chỉ": "thịt lợn nửa nạc nửa mỡ",

            # Thịt bò
            "bò": "thịt bò loại I",
            "thịt bò": "thịt bò loại I",
            "thịt bò nạc": "thịt bò loại I",

            # Rau củ chung
            "rau củ": "rau muống",
            "rau xanh": "rau muống",
            "rau": "rau muống",
            "củ": "cà rốt",

            # Cá
            "cá": "cá chép",
            "cá tươi": "cá chép",

            # Tôm
            "tôm": "tôm biển",
            "tôm tươi": "tôm biển",
            "tôm sú": "tôm biển",

            # Trứng
            "trứng": "trứng gà",

            # Phở và món nước
            "phở": "phở bò",
            "phở tái": "phở bò",
            "phở chín": "phở bò",
            "bún bò": "bún bò huế",
            "bún riêu": "bún riêu cua",
            "hủ tiếu": "hủ tiếu",

            # Món xào
            "rau muống xào": "rau muống",
            "cải xào": "cải xanh",
            "thịt xào": "thịt lợn nạc",
        }

        # Thêm mapping nếu có
        if normalized_name in name_mappings:
            variations.append(name_mappings[normalized_name])

        # Thêm các biến thể khác
        for original, mapped in name_mappings.items():
            if original in normalized_name:
                variations.append(mapped)
                variations.append(normalized_name.replace(original, mapped))

        return list(set(variations))  # Remove duplicates

    def get_official_nutrition_data(self, food_name: str, estimated_grams: float) -> Optional[Dict]:
        """
        🔧 FIX: Lấy dữ liệu dinh dưỡng chính thức từ database Việt Nam với smart lookup

        Args:
            food_name: Tên món ăn/nguyên liệu
            estimated_grams: Khối lượng ước tính

        Returns:
            Dict chứa nutrition data chính thức hoặc None
        """
        try:
            # Tạo các biến thể tên để tìm kiếm
            name_variations = self.normalize_food_name(food_name)
            print(f"🔍 Searching for '{food_name}' with variations: {name_variations}")

            # 1. Tìm trong database món ăn hoàn chỉnh trước
            for name_variant in name_variations:
                dish_nutrition = get_dish_nutrition(name_variant)
                if dish_nutrition:
                    print(f"✅ Found dish nutrition for '{name_variant}'")
                    return {
                        "calories": dish_nutrition["calories"],
                        "protein": dish_nutrition["protein"],
                        "fat": dish_nutrition["fat"],
                        "carbs": dish_nutrition["carbs"],
                        "fiber": dish_nutrition.get("fiber", 0),
                        "sodium": dish_nutrition.get("sodium", 0),
                        "source": f"Official Vietnamese Database - {dish_nutrition['source']}",
                        "reference_code": dish_nutrition["reference_code"],
                        "serving_size": dish_nutrition.get("serving_size", f"{estimated_grams}g"),
                        "data_quality": "official_dish"
                    }

            # 2. Tìm trong database nguyên liệu
            for name_variant in name_variations:
                ingredient_nutrition = get_ingredient_nutrition(name_variant, estimated_grams)
                if ingredient_nutrition:
                    print(f"✅ Found ingredient nutrition for '{name_variant}'")
                    return {
                        "calories": round(ingredient_nutrition["calories"], 1),
                        "protein": round(ingredient_nutrition["protein"], 1),
                        "fat": round(ingredient_nutrition["fat"], 1),
                        "carbs": round(ingredient_nutrition["carbs"], 1),
                        "fiber": round(ingredient_nutrition["fiber"], 1),
                        "sodium": 0,  # Default
                        "source": f"Official Vietnamese Database - {ingredient_nutrition['source']}",
                        "reference_code": ingredient_nutrition["reference_code"],
                        "serving_size": f"{estimated_grams}g",
                        "data_quality": "official_ingredient"
                    }

            # 3. Tìm trong extended database
            for name_variant in name_variations:
                extended_nutrition = self.get_extended_nutrition_data(name_variant, estimated_grams)
                if extended_nutrition:
                    print(f"✅ Found extended nutrition for '{name_variant}'")
                    return extended_nutrition

            print(f"❌ No nutrition data found for '{food_name}' and its variations")
            return None

        except Exception as e:
            print(f"❌ Error getting official nutrition for {food_name}: {e}")
            return None

    def get_extended_nutrition_data(self, food_name: str, estimated_grams: float) -> Optional[Dict]:
        """
        🔧 FIX: Lấy dữ liệu từ extended nutrition database với fuzzy matching
        """
        try:
            # Tìm trong các database extended
            all_databases = [
                ("VEGETABLES", VEGETABLES_NUTRITION),
                ("FRUITS", FRUITS_NUTRITION),
                ("MEAT", MEAT_NUTRITION),
                ("SEAFOOD", SEAFOOD_NUTRITION),
                ("EGGS", EGGS_NUTRITION),
                ("DAIRY", DAIRY_NUTRITION)
            ]

            # Tìm exact match trước
            for db_name, db in all_databases:
                if food_name in db:
                    nutrition_per_100g = db[food_name]
                    scale_factor = estimated_grams / 100.0

                    return {
                        "calories": round(nutrition_per_100g["calories"] * scale_factor, 1),
                        "protein": round(nutrition_per_100g["protein"] * scale_factor, 1),
                        "fat": round(nutrition_per_100g["fat"] * scale_factor, 1),
                        "carbs": round(nutrition_per_100g["carbs"] * scale_factor, 1),
                        "fiber": round(nutrition_per_100g.get("fiber", 0) * scale_factor, 1),
                        "sodium": 0,  # Default
                        "source": f"Vietnamese Extended Database - {db_name}",
                        "reference_code": "VN-EXT",
                        "serving_size": f"{estimated_grams}g",
                        "data_quality": "extended_database"
                    }

            # Tìm partial match nếu không có exact match
            for db_name, db in all_databases:
                for key in db.keys():
                    # Kiểm tra nếu food_name chứa trong key hoặc ngược lại
                    if food_name in key or key in food_name:
                        nutrition_per_100g = db[key]
                        scale_factor = estimated_grams / 100.0

                        print(f"🔍 Partial match: '{food_name}' -> '{key}' in {db_name}")

                        return {
                            "calories": round(nutrition_per_100g["calories"] * scale_factor, 1),
                            "protein": round(nutrition_per_100g["protein"] * scale_factor, 1),
                            "fat": round(nutrition_per_100g["fat"] * scale_factor, 1),
                            "carbs": round(nutrition_per_100g["carbs"] * scale_factor, 1),
                            "fiber": round(nutrition_per_100g.get("fiber", 0) * scale_factor, 1),
                            "sodium": 0,  # Default
                            "source": f"Vietnamese Extended Database - {db_name} (partial match: {key})",
                            "reference_code": "VN-EXT",
                            "serving_size": f"{estimated_grams}g",
                            "data_quality": "extended_database"
                        }

            return None

        except Exception as e:
            print(f"❌ Error getting extended nutrition for {food_name}: {e}")
            return None

    def get_weight_estimation_recommendations(self, analysis_result: Dict) -> List[str]:
        """
        Đưa ra khuyến nghị để cải thiện độ chính xác ước tính khối lượng
        """
        recommendations = []

        # Check image analysis
        image_analysis = analysis_result.get("image_analysis", {})
        reference_objects = image_analysis.get("reference_objects_detected", [])
        image_quality = image_analysis.get("image_quality", "fair")

        # Check weight confidence of foods
        foods = analysis_result.get("foods", [])
        avg_weight_confidence = 0.5
        if foods:
            confidences = []
            for food in foods:
                weight_data = food.get("weight_estimation", {})
                confidences.append(weight_data.get("weight_confidence", 0.5))
            avg_weight_confidence = sum(confidences) / len(confidences)

        # Generate recommendations based on analysis
        if not reference_objects:
            recommendations.append("📏 Đặt đũa, thìa, hoặc đồng xu cạnh món ăn để tham chiếu kích thước")
            recommendations.append("🖐️ Đặt bàn tay cạnh món ăn để so sánh kích thước")

        if image_quality == "poor":
            recommendations.append("📸 Chụp ảnh rõ nét hơn, tránh bị mờ")
            recommendations.append("💡 Đảm bảo ánh sáng đủ sáng và đều")

        if avg_weight_confidence < 0.6:
            recommendations.append("📐 Chụp từ góc nhìn thẳng xuống (90 độ) để ước tính chính xác hơn")
            recommendations.append("🍽️ Đặt món ăn trên nền trắng hoặc đĩa trắng để dễ nhận diện")
            recommendations.append("📏 Sử dụng bát/đĩa có kích thước chuẩn (bát cơm 11.5cm, đĩa 20cm)")

        if len(foods) > 3:
            recommendations.append("🔍 Với nhiều món ăn, chụp từng món riêng lẻ để ước tính chính xác hơn")

        if avg_weight_confidence >= 0.8 and reference_objects:
            recommendations.append("✅ Chất lượng ảnh tốt! Ước tính khối lượng đáng tin cậy")

        return recommendations

# Create singleton instance for application
gemini_vision_service = GeminiVisionService() 