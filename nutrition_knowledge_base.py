"""
Enhanced Nutrition Knowledge Base for DietAI Chatbot
Cơ sở kiến thức dinh dưỡng nâng cao cho chatbot DietAI
"""

# Nutrition facts database
NUTRITION_FACTS = {
    "macronutrients": {
        "protein": {
            "calories_per_gram": 4,
            "daily_requirement": "0.8-2.2g per kg body weight",
            "functions": ["muscle building", "enzyme production", "immune function"],
            "vietnamese_sources": ["thịt bò", "cá", "đậu phụ", "trứng", "tôm", "gà"],
            "timing": "distribute throughout day, 20-30g per meal"
        },
        "carbohydrates": {
            "calories_per_gram": 4,
            "daily_requirement": "45-65% of total calories",
            "types": {
                "simple": ["đường", "mật ong", "trái cây"],
                "complex": ["gạo lứt", "yến mạch", "khoai lang", "bánh mì nguyên cám"]
            },
            "glycemic_index": {
                "low": ["yến mạch", "đậu", "rau xanh"],
                "medium": ["gạo lứt", "khoai lang"],
                "high": ["gạo trắng", "bánh mì trắng", "khoai tây"]
            }
        },
        "fats": {
            "calories_per_gram": 9,
            "daily_requirement": "20-35% of total calories",
            "types": {
                "saturated": ["thịt đỏ", "bơ", "dầu dừa"],
                "monounsaturated": ["dầu olive", "bơ", "hạt macadamia"],
                "polyunsaturated": ["cá hồi", "hạt chia", "óc chó"],
                "omega3": ["cá thu", "cá hồi", "hạt lanh", "óc chó"],
                "omega6": ["dầu hướng dương", "hạt bí"]
            }
        }
    },
    
    "micronutrients": {
        "vitamins": {
            "vitamin_d": {
                "functions": ["bone health", "immune function", "mood regulation"],
                "sources": ["cá hồi", "trứng", "nấm", "ánh nắng mặt trời"],
                "deficiency_symptoms": ["mệt mỏi", "đau xương", "trầm cảm"],
                "daily_requirement": "600-800 IU"
            },
            "vitamin_b12": {
                "functions": ["red blood cell formation", "nervous system"],
                "sources": ["thịt", "cá", "trứng", "sữa"],
                "deficiency_symptoms": ["thiếu máu", "mệt mỏi", "tê tay chân"],
                "daily_requirement": "2.4 mcg"
            },
            "vitamin_c": {
                "functions": ["immune system", "collagen synthesis", "antioxidant"],
                "sources": ["cam", "ổi", "ớt chuông", "bông cải xanh"],
                "daily_requirement": "65-90 mg"
            }
        },
        "minerals": {
            "iron": {
                "functions": ["oxygen transport", "energy metabolism"],
                "sources": ["thịt đỏ", "gan", "rau bina", "đậu lăng"],
                "absorption_enhancers": ["vitamin C", "thịt"],
                "absorption_inhibitors": ["trà", "cà phê", "canxi"],
                "daily_requirement": "8-18 mg"
            },
            "calcium": {
                "functions": ["bone health", "muscle function", "nerve transmission"],
                "sources": ["sữa", "phô mai", "rau xanh đậm", "cá có xương"],
                "daily_requirement": "1000-1200 mg"
            }
        }
    },
    
    "vietnamese_nutrition": {
        "traditional_dishes": {
            "pho_bo": {
                "calories_per_bowl": 350,
                "protein": 25,
                "carbs": 45,
                "fat": 8,
                "benefits": ["high protein", "warming", "digestive"],
                "modifications": {
                    "weight_loss": "more vegetables, less noodles",
                    "diabetes": "shirataki noodles, extra protein",
                    "high_protein": "double meat, add egg"
                }
            },
            "com_tam": {
                "calories_per_serving": 450,
                "protein": 30,
                "carbs": 55,
                "fat": 12,
                "benefits": ["complete meal", "balanced macros"],
                "modifications": {
                    "weight_loss": "brown rice, grilled instead of fried",
                    "diabetes": "cauliflower rice, extra vegetables"
                }
            }
        },
        
        "superfoods": {
            "gac_fruit": {
                "nutrients": ["lycopene", "beta-carotene", "vitamin E"],
                "benefits": ["antioxidant", "eye health", "skin health"]
            },
            "dragon_fruit": {
                "nutrients": ["vitamin C", "iron", "magnesium", "fiber"],
                "benefits": ["immune support", "digestive health", "hydration"]
            },
            "bitter_melon": {
                "nutrients": ["vitamin C", "folate", "charantin"],
                "benefits": ["blood sugar control", "immune support"]
            }
        }
    },
    
    "health_conditions": {
        "diabetes": {
            "dietary_principles": [
                "low glycemic index foods",
                "portion control",
                "regular meal timing",
                "fiber-rich foods"
            ],
            "recommended_foods": ["rau xanh", "cá", "đậu", "yến mạch"],
            "foods_to_limit": ["gạo trắng", "đường", "bánh ngọt", "nước ngọt"],
            "meal_planning": "3 main meals + 2 snacks, consistent carb intake"
        },
        
        "hypertension": {
            "dietary_principles": [
                "low sodium",
                "high potassium",
                "DASH diet",
                "limit processed foods"
            ],
            "recommended_foods": ["rau xanh", "trái cây", "ngũ cốc nguyên hạt", "cá"],
            "foods_to_limit": ["muối", "đồ ăn chế biến sẵn", "thịt hun khói"],
            "sodium_limit": "less than 2300mg per day"
        },
        
        "obesity": {
            "dietary_principles": [
                "caloric deficit",
                "high protein",
                "high fiber",
                "portion control"
            ],
            "recommended_foods": ["protein lean", "rau xanh", "trái cây", "ngũ cốc nguyên hạt"],
            "meal_timing": "regular meals, avoid late night eating",
            "weight_loss_rate": "0.5-1kg per week"
        }
    },
    
    "meal_timing": {
        "pre_workout": {
            "timing": "30-60 minutes before",
            "foods": ["chuối", "yến mạch", "bánh mì nguyên cám"],
            "avoid": ["high fat", "high fiber", "large portions"]
        },
        "post_workout": {
            "timing": "within 30 minutes",
            "ratio": "3:1 carbs to protein",
            "foods": ["sữa chocolate", "chuối + protein", "cơm + thịt"]
        },
        "intermittent_fasting": {
            "16_8": "16 hours fast, 8 hours eating window",
            "benefits": ["weight loss", "metabolic health", "cellular repair"],
            "considerations": ["not for everyone", "medical supervision if needed"]
        }
    }
}

def get_nutrition_advice(topic: str, user_condition: str = None) -> str:
    """
    Lấy lời khuyên dinh dưỡng dựa trên chủ đề và tình trạng sức khỏe
    """
    advice = []
    
    if topic in NUTRITION_FACTS.get("health_conditions", {}):
        condition_info = NUTRITION_FACTS["health_conditions"][topic]
        advice.append(f"Nguyên tắc dinh dưỡng cho {topic}:")
        for principle in condition_info["dietary_principles"]:
            advice.append(f"• {principle}")
        
        advice.append(f"\nThực phẩm nên ăn: {', '.join(condition_info['recommended_foods'])}")
        if "foods_to_limit" in condition_info:
            advice.append(f"Thực phẩm nên hạn chế: {', '.join(condition_info['foods_to_limit'])}")
    
    return "\n".join(advice)

def get_vietnamese_dish_nutrition(dish_name: str) -> dict:
    """
    Lấy thông tin dinh dưỡng của món ăn Việt Nam
    """
    dishes = NUTRITION_FACTS.get("vietnamese_nutrition", {}).get("traditional_dishes", {})
    
    # Tìm kiếm gần đúng
    for key, value in dishes.items():
        if dish_name.lower() in key or key in dish_name.lower():
            return value
    
    return None

def get_nutrient_info(nutrient: str) -> dict:
    """
    Lấy thông tin chi tiết về một chất dinh dưỡng
    """
    # Tìm trong macronutrients
    macros = NUTRITION_FACTS.get("macronutrients", {})
    if nutrient in macros:
        return macros[nutrient]
    
    # Tìm trong vitamins
    vitamins = NUTRITION_FACTS.get("micronutrients", {}).get("vitamins", {})
    if nutrient in vitamins:
        return vitamins[nutrient]
    
    # Tìm trong minerals
    minerals = NUTRITION_FACTS.get("micronutrients", {}).get("minerals", {})
    if nutrient in minerals:
        return minerals[nutrient]
    
    return None
