# -*- coding: utf-8 -*-
"""
Service tạo 300+ món ăn Việt Nam với dữ liệu dinh dưỡng chính xác
Sử dụng dữ liệu chuẩn từ Viện Dinh dưỡng Quốc gia
"""

import random
from typing import List, Dict, Optional, Tuple
from vietnamese_nutrition_extended import (
    VEGETABLES_NUTRITION, FRUITS_NUTRITION, MEAT_NUTRITION,
    SEAFOOD_NUTRITION, EGGS_NUTRITION, DAIRY_NUTRITION
)
from vietnamese_traditional_dishes import ALL_TRADITIONAL_DISHES

class VietnameseDishGenerator:
    """
    Generator tạo món ăn Việt Nam đa dạng với dữ liệu dinh dưỡng chính xác
    """
    
    def __init__(self):
        # Patterns món ăn Việt Nam theo miền
        self.dish_patterns = {
            "miền_bắc": {
                "breakfast": [
                    {"base": "phở", "protein": ["bò", "gà"], "garnish": ["hành lá", "giá đỗ xanh"]},
                    {"base": "bún", "protein": ["chả cá", "thịt nướng"], "garnish": ["rau thơm", "dưa chuột"]},
                    {"base": "xôi", "protein": ["thịt gà", "ruốc"], "garnish": ["hành phi", "đậu xanh"]},
                    {"base": "bánh cuốn", "protein": ["thịt heo", "tôm"], "garnish": ["nấm mèo", "hành lá"]},
                    {"base": "cháo", "protein": ["gà", "tôm", "cá"], "garnish": ["gừng", "hành lá"]}
                ],
                "lunch": [
                    {"base": "bún chả", "protein": ["thịt heo nướng"], "garnish": ["rau thơm", "dưa chuột"]},
                    {"base": "cơm", "protein": ["thịt kho", "cá kho"], "side": ["canh rau", "rau luộc"]},
                    {"base": "miến", "protein": ["gà", "lươn"], "garnish": ["nấm", "hành lá"]},
                    {"base": "bánh đa", "protein": ["cua đồng"], "garnish": ["rau muống", "giá đỗ"]},
                    {"base": "nem", "protein": ["thịt heo"], "garnish": ["rau sống", "bánh tráng"]}
                ],
                "dinner": [
                    {"base": "canh", "protein": ["cá", "tôm", "thịt"], "vegetables": ["bí đao", "cải thìa"]},
                    {"base": "lẩu", "protein": ["cá", "thịt bò"], "vegetables": ["rau muống", "cải bắp"]},
                    {"base": "cơm", "protein": ["gà luộc", "thịt luộc"], "side": ["dưa chua", "canh"]},
                    {"base": "chả cá", "protein": ["cá"], "garnish": ["thì là", "bánh đa"]},
                    {"base": "bún riêu", "protein": ["cua đồng"], "garnish": ["rau thơm", "cà chua"]}
                ]
            },
            "miền_trung": {
                "breakfast": [
                    {"base": "bún bò Huế", "protein": ["thịt bò", "chả"], "garnish": ["hành lá", "rau thơm"]},
                    {"base": "mì Quảng", "protein": ["tôm", "thịt heo"], "garnish": ["bánh tráng", "rau sống"]},
                    {"base": "bánh bèo", "protein": ["tôm"], "garnish": ["hành phi", "mắm nêm"]},
                    {"base": "bánh khoái", "protein": ["tôm", "thịt"], "garnish": ["rau sống", "nước chấm"]},
                    {"base": "cháo hến", "protein": ["hến"], "garnish": ["rau thơm", "bánh phồng"]}
                ],
                "lunch": [
                    {"base": "cao lầu", "protein": ["thịt heo"], "garnish": ["giá đỗ", "rau thơm"]},
                    {"base": "cơm hến", "protein": ["hến"], "garnish": ["rau thơm", "bánh tráng"]},
                    {"base": "bánh căn", "protein": ["tôm", "mực"], "garnish": ["rau sống", "nước chấm"]},
                    {"base": "nem lụi", "protein": ["thịt heo"], "garnish": ["bánh tráng", "rau sống"]},
                    {"base": "bún thịt nướng", "protein": ["thịt heo"], "garnish": ["rau thơm", "đậu phộng"]}
                ],
                "dinner": [
                    {"base": "cơm âm phủ", "protein": ["thịt heo", "tôm"], "garnish": ["rau sống"]},
                    {"base": "bánh xèo", "protein": ["tôm", "thịt"], "garnish": ["rau sống", "nước chấm"]},
                    {"base": "chả cá", "protein": ["cá thu"], "garnish": ["bánh tráng", "rau thơm"]},
                    {"base": "cơm gà", "protein": ["thịt gà"], "side": ["canh", "rau luộc"]},
                    {"base": "bánh ít", "protein": ["tôm"], "garnish": ["hành phi", "nước mắm"]}
                ]
            },
            "miền_nam": {
                "breakfast": [
                    {"base": "hủ tiếu", "protein": ["tôm", "thịt heo"], "garnish": ["hành lá", "giá đỗ"]},
                    {"base": "bánh mì", "protein": ["thịt nướng", "chả"], "garnish": ["rau thơm", "dưa chua"]},
                    {"base": "cháo sườn", "protein": ["sườn heo"], "garnish": ["hành lá", "tiêu"]},
                    {"base": "bánh cuốn", "protein": ["tôm", "thịt"], "garnish": ["rau sống", "nước chấm"]},
                    {"base": "cơm tấm", "protein": ["sườn nướng"], "garnish": ["trứng ốp la", "dưa chua"]}
                ],
                "lunch": [
                    {"base": "cơm chiên", "protein": ["tôm", "thịt"], "garnish": ["dưa chua", "nước mắm"]},
                    {"base": "bánh xèo", "protein": ["tôm", "thịt heo"], "garnish": ["rau sống", "nước chấm"]},
                    {"base": "gỏi cuốn", "protein": ["tôm", "thịt"], "garnish": ["rau thơm", "nước chấm"]},
                    {"base": "cà ri", "protein": ["gà", "bò"], "side": ["bánh mì", "rau sống"]},
                    {"base": "lẩu", "protein": ["cá", "tôm"], "vegetables": ["rau muống", "bắp chuối"]}
                ],
                "dinner": [
                    {"base": "canh chua", "protein": ["cá", "tôm"], "vegetables": ["bầu", "đậu bắp"]},
                    {"base": "thịt kho", "protein": ["thịt heo"], "side": ["trứng", "cơm"]},
                    {"base": "cá kho", "protein": ["cá"], "side": ["cơm", "canh"]},
                    {"base": "gà nướng", "protein": ["thịt gà"], "side": ["cơm", "rau sống"]},
                    {"base": "tôm rang", "protein": ["tôm"], "side": ["cơm", "canh rau"]}
                ]
            }
        }
        
        # Cooking methods
        self.cooking_methods = [
            "luộc", "nướng", "xào", "kho", "chiên", "hấp", "nấu", "rang", "om", "quay"
        ]
        
        # Seasonings và gia vị
        self.seasonings = [
            "nước mắm", "muối", "đường", "tiêu", "tỏi", "hành", "gừng", "sả", "ớt"
        ]
    
    def generate_dish_name(self, pattern: Dict, region: str) -> str:
        """Tạo tên món ăn từ pattern"""
        base = pattern["base"]
        protein = random.choice(pattern["protein"])
        
        # Tạo tên món theo pattern
        if base in ["phở", "bún", "hủ tiếu", "mì"]:
            return f"{base.title()} {protein}"
        elif base == "cơm":
            cooking_method = random.choice(self.cooking_methods)
            return f"Cơm {protein} {cooking_method}"
        elif base == "canh":
            vegetable = random.choice(list(VEGETABLES_NUTRITION.keys())[:10])
            return f"Canh {vegetable} {protein}"
        elif base == "bánh":
            return f"Bánh {protein}"
        else:
            return f"{base.title()} {protein}"
    
    def calculate_dish_nutrition(self, ingredients: List[Dict]) -> Dict:
        """Tính toán dinh dưỡng món ăn từ nguyên liệu"""
        total_nutrition = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        
        for ingredient in ingredients:
            name = ingredient["name"]
            amount = ingredient["amount"]  # in grams
            
            # 🔧 FIX: Enhanced nutrition lookup với fallback
            nutrition_data = None

            # Tìm trong các database
            for nutrition_db in [VEGETABLES_NUTRITION, FRUITS_NUTRITION, MEAT_NUTRITION,
                               SEAFOOD_NUTRITION, EGGS_NUTRITION, DAIRY_NUTRITION]:
                if name in nutrition_db:
                    nutrition_data = nutrition_db[name]
                    break

            # 🔧 FIX: Fallback cho các ingredient không tìm thấy
            if not nutrition_data:
                # Estimate nutrition based on ingredient type
                if any(keyword in name.lower() for keyword in ['thịt', 'bò', 'heo', 'gà']):
                    nutrition_data = {"calories": 150, "protein": 20, "fat": 8, "carbs": 0}
                elif any(keyword in name.lower() for keyword in ['cá', 'tôm', 'mực']):
                    nutrition_data = {"calories": 100, "protein": 18, "fat": 2, "carbs": 0}
                elif any(keyword in name.lower() for keyword in ['cơm', 'bánh', 'bún', 'phở']):
                    nutrition_data = {"calories": 130, "protein": 3, "fat": 0.3, "carbs": 28}
                elif any(keyword in name.lower() for keyword in ['rau', 'cải', 'cà']):
                    nutrition_data = {"calories": 25, "protein": 2, "fat": 0.2, "carbs": 4}
                else:
                    # Default fallback
                    nutrition_data = {"calories": 50, "protein": 2, "fat": 1, "carbs": 8}

                print(f"⚠️ Using fallback nutrition for '{name}': {nutrition_data}")

            if nutrition_data:
                # Scale theo amount (nutrition data là per 100g)
                scale = amount / 100.0
                total_nutrition["calories"] += nutrition_data["calories"] * scale
                total_nutrition["protein"] += nutrition_data["protein"] * scale
                total_nutrition["fat"] += nutrition_data["fat"] * scale
                total_nutrition["carbs"] += nutrition_data["carbs"] * scale
        
        return total_nutrition
    
    def generate_ingredients(self, pattern: Dict, serving_size: int = 1) -> List[Dict]:
        """Tạo danh sách nguyên liệu cho món ăn"""
        ingredients = []
        
        # 🔧 FIX: Base ingredient (carbs) - đảm bảo có carbs cho mọi món
        base = pattern["base"]
        if base in ["phở", "bún", "hủ tiếu"]:
            # Thêm bánh phở/bún với lượng hợp lý
            carb_name = "bánh phở" if base == "phở" else "bún tươi"
            # Tạo nutrition data cho bánh phở/bún (estimate based on rice noodles)
            ingredients.append({"name": carb_name, "amount": 200 * serving_size})
            # Add to nutrition database if not exists
            if carb_name not in VEGETABLES_NUTRITION:
                # Rice noodles nutrition estimate
                VEGETABLES_NUTRITION[carb_name] = {"calories": 109, "fat": 0.2, "carbs": 25.0, "protein": 2.2}
        elif base == "cơm":
            # Cooked rice
            ingredients.append({"name": "cơm trắng", "amount": 200 * serving_size})
            if "cơm trắng" not in VEGETABLES_NUTRITION:
                VEGETABLES_NUTRITION["cơm trắng"] = {"calories": 130, "fat": 0.3, "carbs": 28.0, "protein": 2.7}
        elif base == "xôi":
            ingredients.append({"name": "xôi nếp", "amount": 150 * serving_size})
            if "xôi nếp" not in VEGETABLES_NUTRITION:
                VEGETABLES_NUTRITION["xôi nếp"] = {"calories": 116, "fat": 0.2, "carbs": 26.0, "protein": 2.4}
        elif base in ["bánh", "bánh cuốn", "bánh xèo"]:
            ingredients.append({"name": "bánh tráng", "amount": 100 * serving_size})
            if "bánh tráng" not in VEGETABLES_NUTRITION:
                VEGETABLES_NUTRITION["bánh tráng"] = {"calories": 334, "fat": 0.6, "carbs": 83.0, "protein": 3.0}
        elif base == "canh":
            # Canh thường ăn với cơm
            ingredients.append({"name": "cơm trắng", "amount": 150 * serving_size})
        else:
            # Default carb base
            ingredients.append({"name": "cơm trắng", "amount": 150 * serving_size})
        
        # Protein
        protein = random.choice(pattern["protein"])
        protein_amount = 100 * serving_size
        
        # Map protein names to nutrition database keys
        protein_mapping = {
            "bò": "thịt bò loại I",
            "gà": "thịt gà ta", 
            "heo": "thịt lợn nạc",
            "tôm": "tôm biển",
            "cá": "cá rô phi",
            "chả": "chả lợn"
        }
        
        mapped_protein = protein_mapping.get(protein, protein)
        ingredients.append({"name": mapped_protein, "amount": protein_amount})
        
        # Vegetables/garnish
        if "garnish" in pattern:
            for garnish in pattern["garnish"][:2]:  # Limit to 2 garnishes
                if garnish in VEGETABLES_NUTRITION:
                    ingredients.append({"name": garnish, "amount": 30 * serving_size})
        
        # Seasonings
        ingredients.append({"name": "nước mắm", "amount": 10 * serving_size})
        ingredients.append({"name": "tỏi ta", "amount": 5 * serving_size})
        
        return ingredients
    
    def generate_cooking_instructions(self, dish_name: str, ingredients: List[Dict]) -> List[str]:
        """Tạo hướng dẫn nấu ăn thực tế"""
        instructions = []
        
        # Preparation
        instructions.append("Sơ chế nguyên liệu: rửa sạch rau củ, thái nhỏ gia vị")
        
        # Protein preparation
        protein_ingredients = [ing for ing in ingredients if ing["name"] in 
                             [item for sublist in [MEAT_NUTRITION.keys(), SEAFOOD_NUTRITION.keys()] 
                              for item in sublist]]
        
        if protein_ingredients:
            protein_name = protein_ingredients[0]["name"]
            if "thịt" in protein_name:
                instructions.append(f"Ướp {protein_name} với gia vị trong 15 phút")
            elif "cá" in protein_name:
                instructions.append(f"Làm sạch {protein_name}, ướp muối và tiêu")
            elif "tôm" in protein_name:
                instructions.append(f"Tôm bóc vỏ, khử tanh với muối")
        
        # Cooking process
        if "phở" in dish_name.lower():
            instructions.extend([
                "Nấu nước dùng từ xương bò với gia vị thơm",
                "Trụng bánh phở trong nước sôi",
                "Thái thịt mỏng, cho vào tô",
                "Chan nước dùng nóng, rắc hành lá"
            ])
        elif "cơm" in dish_name.lower():
            instructions.extend([
                "Nấu cơm với tỷ lệ nước phù hợp",
                "Xào thịt với gia vị cho thơm",
                "Trình bày cơm và thịt ra đĩa"
            ])
        elif "canh" in dish_name.lower():
            instructions.extend([
                "Đun sôi nước, cho thịt/cá vào nấu",
                "Thêm rau củ, nêm gia vị vừa ăn",
                "Nấu đến khi rau chín mềm"
            ])
        else:
            instructions.extend([
                "Chế biến nguyên liệu theo phương pháp truyền thống",
                "Nêm nướng vừa ăn",
                "Trình bày đẹp mắt khi phục vụ"
            ])
        
        return instructions
    
    def get_traditional_dish(self, meal_type: str, region: str = None) -> Dict:
        """
        🔧 FIX: Lấy món ăn từ database truyền thống 200+ món
        """
        # Filter dishes by meal type
        suitable_dishes = {}
        for dish_name, dish_info in ALL_TRADITIONAL_DISHES.items():
            if meal_type in dish_info.get("meal_type", []):
                # Filter by region if specified
                if region:
                    dish_region = dish_info.get("region", "")
                    if region in dish_region.lower() or "toàn quốc" in dish_region.lower():
                        suitable_dishes[dish_name] = dish_info
                else:
                    suitable_dishes[dish_name] = dish_info

        if not suitable_dishes:
            return None

        # Random select a dish
        dish_name = random.choice(list(suitable_dishes.keys()))
        dish_info = suitable_dishes[dish_name]

        # Generate ingredients based on main_ingredients
        ingredients = []
        for ingredient_name in dish_info["main_ingredients"]:
            # Estimate amount based on ingredient type
            if any(keyword in ingredient_name.lower() for keyword in ['cơm', 'bún', 'phở', 'mì']):
                amount = 200  # Carbs base
            elif any(keyword in ingredient_name.lower() for keyword in ['thịt', 'gà', 'bò', 'heo']):
                amount = 150  # Protein
            elif any(keyword in ingredient_name.lower() for keyword in ['tôm', 'cá', 'cua']):
                amount = 120  # Seafood
            elif any(keyword in ingredient_name.lower() for keyword in ['rau', 'cà', 'bí']):
                amount = 80   # Vegetables
            else:
                amount = 50   # Others

            ingredients.append({"name": ingredient_name, "amount": amount})

        # Add basic seasonings
        ingredients.extend([
            {"name": "nước mắm", "amount": 10},
            {"name": "tỏi ta", "amount": 5}
        ])

        # Calculate nutrition
        nutrition = self.calculate_dish_nutrition(ingredients)

        # Generate cooking instructions
        instructions = self.generate_cooking_instructions_traditional(dish_name, dish_info)

        return {
            "name": dish_name.title(),
            "region": dish_info.get("region", "Việt Nam"),
            "meal_type": meal_type,
            "ingredients": ingredients,
            "nutrition": {
                "calories": round(nutrition["calories"], 1),
                "protein": round(nutrition["protein"], 1),
                "fat": round(nutrition["fat"], 1),
                "carbs": round(nutrition["carbs"], 1)
            },
            "preparation": instructions,
            "cooking_time": f"{random.randint(20, 60)} phút",
            "difficulty": random.choice(["Dễ", "Trung bình", "Khó"]),
            "serving_size": "1 người",
            "source": "Traditional Vietnamese Cuisine Database",
            "description": dish_info.get("description", "Món ăn truyền thống Việt Nam")
        }

    def generate_cooking_instructions_traditional(self, dish_name: str, dish_info: Dict) -> List[str]:
        """Tạo hướng dẫn nấu ăn cho món truyền thống"""
        instructions = []

        # Basic preparation
        instructions.append("Sơ chế nguyên liệu: rửa sạch, thái nhỏ")

        # Specific instructions based on dish type
        if "bún" in dish_name or "phở" in dish_name:
            instructions.extend([
                "Nấu nước dùng từ xương với gia vị thơm",
                "Trụng bánh trong nước sôi",
                "Bày nguyên liệu vào tô, chan nước dùng nóng"
            ])
        elif "cơm" in dish_name:
            instructions.extend([
                "Nấu cơm chín tới",
                "Chế biến món phụ theo truyền thống",
                "Trình bày đẹp mắt"
            ])
        elif "xôi" in dish_name:
            instructions.extend([
                "Ngâm gạo nếp qua đêm",
                "Đồ xôi trong chõ hoặc nồi hấp",
                "Trộn đều với nguyên liệu phụ"
            ])
        elif "bánh" in dish_name:
            instructions.extend([
                "Pha bột với tỷ lệ phù hợp",
                "Chế biến nhân theo công thức truyền thống",
                "Gói/đúc bánh và nấu chín"
            ])
        else:
            instructions.extend([
                "Chế biến theo phương pháp truyền thống",
                "Nêm nướng vừa ăn",
                "Trình bày theo phong cách Việt Nam"
            ])

        return instructions

    def generate_single_dish(self, meal_type: str, region: str = None) -> Dict:
        """
        🔧 FIX: Tạo một món ăn hoàn chỉnh - ưu tiên traditional dishes
        """
        # 🔧 FIX: Try traditional dishes first (70% chance)
        if random.random() < 0.7:
            traditional_dish = self.get_traditional_dish(meal_type, region)
            if traditional_dish:
                return traditional_dish

        # Fallback to generated dishes
        if region is None:
            region = random.choice(["miền_bắc", "miền_trung", "miền_nam"])

        # Get pattern for this meal type and region
        patterns = self.dish_patterns[region][meal_type]
        pattern = random.choice(patterns)

        # Generate dish
        dish_name = self.generate_dish_name(pattern, region)
        ingredients = self.generate_ingredients(pattern)
        nutrition = self.calculate_dish_nutrition(ingredients)
        instructions = self.generate_cooking_instructions(dish_name, ingredients)

        return {
            "name": dish_name,
            "region": region.replace("_", " ").title(),
            "meal_type": meal_type,
            "ingredients": ingredients,
            "nutrition": {
                "calories": round(nutrition["calories"], 1),
                "protein": round(nutrition["protein"], 1),
                "fat": round(nutrition["fat"], 1),
                "carbs": round(nutrition["carbs"], 1)
            },
            "preparation": instructions,
            "cooking_time": f"{random.randint(15, 60)} phút",
            "difficulty": random.choice(["Dễ", "Trung bình", "Khó"]),
            "serving_size": "1 người",
            "source": "Generated from Viện Dinh dưỡng Quốc gia data"
        }
    
    def generate_multiple_dishes(self, count: int = 300) -> List[Dict]:
        """Tạo nhiều món ăn đa dạng"""
        dishes = []
        meal_types = ["breakfast", "lunch", "dinner"]
        regions = ["miền_bắc", "miền_trung", "miền_nam"]
        
        dishes_per_combination = count // (len(meal_types) * len(regions))
        
        for region in regions:
            for meal_type in meal_types:
                for i in range(dishes_per_combination):
                    try:
                        dish = self.generate_single_dish(meal_type, region)
                        dishes.append(dish)
                    except Exception as e:
                        print(f"Error generating dish: {e}")
                        continue
        
        # Fill remaining slots
        while len(dishes) < count:
            try:
                region = random.choice(regions)
                meal_type = random.choice(meal_types)
                dish = self.generate_single_dish(meal_type, region)
                dishes.append(dish)
            except Exception as e:
                print(f"Error generating additional dish: {e}")
                break
        
        return dishes[:count]

# Global instance
vietnamese_dish_generator = VietnameseDishGenerator()
