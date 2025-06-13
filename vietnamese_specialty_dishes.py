# -*- coding: utf-8 -*-
"""
Các món ăn Việt Nam đặc sắc và mới lạ
Tập hợp những món ăn truyền thống nhưng ít phổ biến và những biến tướng sáng tạo
"""

SPECIALTY_DISHES = {
    "bữa sáng": {
        # Món nước đặc sắc
        "Cháo Cá Hồi Nấu Dừa": {
            "description": "Cháo cá hồi thơm béo nấu với nước dừa tươi, đậm đà hương vị miền Tây",
            "ingredients": [
                {"name": "Cá hồi", "amount": "200g"},
                {"name": "Gạo tẻ", "amount": "100g"},
                {"name": "Nước dừa tươi", "amount": "300ml"},
                {"name": "Hành lá", "amount": "20g"},
                {"name": "Ngò rí", "amount": "10g"},
                {"name": "Tiêu", "amount": "1 tsp"}
            ],
            "preparation": [
                "Bước 1: Vo gạo sạch, ngâm 30 phút",
                "Bước 2: Cá hồi rửa sạch, cắt miếng vừa ăn, ướp với muối tiêu",
                "Bước 3: Nấu cháo gạo với nước dừa đến khi mềm",
                "Bước 4: Cho cá hồi vào nấu thêm 10 phút",
                "Bước 5: Nêm nướng vừa ăn, rắc hành lá ngò rí"
            ],
            "nutrition": {"calories": 380, "protein": 25, "fat": 18, "carbs": 35},
            "preparation_time": "45 phút",
            "health_benefits": "Giàu omega-3, protein cao, tốt cho tim mạch và não bộ"
        },

        "Bánh Cuốn Thanh Trì": {
            "description": "Bánh cuốn làng Thanh Trì nổi tiếng với lớp bánh mỏng như tơ, nhân thịt thơm ngon",
            "ingredients": [
                {"name": "Bột gạo", "amount": "200g"},
                {"name": "Bột năng", "amount": "50g"},
                {"name": "Thịt heo xay", "amount": "150g"},
                {"name": "Mộc nhĩ", "amount": "30g"},
                {"name": "Hành tím", "amount": "20g"},
                {"name": "Nước mắm", "amount": "2 tbsp"}
            ],
            "preparation": [
                "Bước 1: Pha bột gạo với nước thành hỗn hợp mịn",
                "Bước 2: Xào nhân thịt với mộc nhĩ, hành tím",
                "Bước 3: Tráng bánh mỏng trên chảo chống dính",
                "Bước 4: Cho nhân vào cuốn tròn",
                "Bước 5: Ăn kèm với chả lụa, nước mắm pha"
            ],
            "nutrition": {"calories": 320, "protein": 18, "fat": 12, "carbs": 42},
            "preparation_time": "60 phút",
            "health_benefits": "Dễ tiêu hóa, ít dầu mỡ, phù hợp cho người ăn kiêng"
        },

        "Xôi Chiên Phồng": {
            "description": "Xôi chiên giòn rụm, phồng xốp, món ăn vặt độc đáo của Hà Nội",
            "ingredients": [
                {"name": "Xôi nếp", "amount": "300g"},
                {"name": "Trứng gà", "amount": "2 quả"},
                {"name": "Bột chiên giòn", "amount": "100g"},
                {"name": "Dầu ăn", "amount": "500ml"},
                {"name": "Muối vừng", "amount": "2 tbsp"},
                {"name": "Tôm khô", "amount": "30g"}
            ],
            "preparation": [
                "Bước 1: Nấu xôi nếp chín tới, để nguội",
                "Bước 2: Cắt xôi thành miếng vuông vừa ăn",
                "Bước 3: Tẩm xôi qua trứng đánh tan, lăn bột chiên giòn",
                "Bước 4: Chiên trong dầu nóng đến vàng giòn",
                "Bước 5: Rắc muối vừng và tôm khô rang"
            ],
            "nutrition": {"calories": 420, "protein": 12, "fat": 22, "carbs": 48},
            "preparation_time": "40 phút",
            "health_benefits": "Cung cấp năng lượng nhanh, giàu carbohydrate"
        }
    },

    "bữa trưa": {
        # Cơm đặc sắc
        "Cơm Âm Phủ Huế": {
            "description": "Món cơm cung đình Huế với nhiều loại thịt và rau củ, trình bày đẹp mắt",
            "ingredients": [
                {"name": "Cơm tấm", "amount": "200g"},
                {"name": "Thịt heo quay", "amount": "100g"},
                {"name": "Chả lụa", "amount": "50g"},
                {"name": "Tôm khô", "amount": "30g"},
                {"name": "Trứng cút", "amount": "5 quả"},
                {"name": "Rau muống", "amount": "100g"},
                {"name": "Nước mắm Phú Quốc", "amount": "3 tbsp"}
            ],
            "preparation": [
                "Bước 1: Nấu cơm tấm dẻo, để riêng",
                "Bước 2: Thái thịt heo quay, chả lụa thành lát mỏng",
                "Bước 3: Luộc trứng cút, bóc vỏ",
                "Bước 4: Xào rau muống với tỏi",
                "Bước 5: Trình bày tất cả lên đĩa, ăn kèm nước mắm pha"
            ],
            "nutrition": {"calories": 580, "protein": 32, "fat": 24, "carbs": 65},
            "preparation_time": "50 phút",
            "health_benefits": "Đầy đủ dinh dưỡng, protein đa dạng, vitamin từ rau xanh"
        },

        "Bún Măng Vịt": {
            "description": "Món bún đặc sản miền Bắc với nước dùng trong vắt từ xương vịt và măng tươi",
            "ingredients": [
                {"name": "Bún tươi", "amount": "200g"},
                {"name": "Thịt vịt", "amount": "200g"},
                {"name": "Măng tươi", "amount": "150g"},
                {"name": "Tôm khô", "amount": "30g"},
                {"name": "Hành lá", "amount": "20g"},
                {"name": "Ngò gai", "amount": "15g"},
                {"name": "Nước mắm", "amount": "2 tbsp"}
            ],
            "preparation": [
                "Bước 1: Ninh xương vịt để lấy nước dùng trong",
                "Bước 2: Thịt vịt luộc chín, xé sợi",
                "Bước 3: Măng tươi thái sợi, luộc qua nước sôi",
                "Bước 4: Tôm khô ngâm mềm, rang thơm",
                "Bước 5: Trình bày bún, thịt vịt, măng, chan nước dùng nóng"
            ],
            "nutrition": {"calories": 450, "protein": 28, "fat": 15, "carbs": 55},
            "preparation_time": "90 phút",
            "health_benefits": "Ít cholesterol, giàu protein, chất xơ từ măng tốt cho tiêu hóa"
        },

        "Mì Quảng Tôm Cua": {
            "description": "Mì Quảng đặc biệt với tôm tươi và cua đồng, nước dùng đậm đà",
            "ingredients": [
                {"name": "Mì Quảng", "amount": "200g"},
                {"name": "Tôm sú", "amount": "150g"},
                {"name": "Cua đồng", "amount": "2 con"},
                {"name": "Thịt heo", "amount": "100g"},
                {"name": "Trứng cút", "amount": "4 quả"},
                {"name": "Bánh tráng", "amount": "2 tờ"},
                {"name": "Rau thơm", "amount": "50g"}
            ],
            "preparation": [
                "Bước 1: Nấu nước dùng từ xương heo và cua",
                "Bước 2: Tôm sú bóc vỏ, giữ nguyên đuôi",
                "Bước 3: Thịt heo thái lát mỏng",
                "Bước 4: Luộc mì Quảng vừa chín",
                "Bước 5: Trình bày mì, tôm cua, chan nước dùng, rắc bánh tráng nướng"
            ],
            "nutrition": {"calories": 520, "protein": 35, "fat": 18, "carbs": 58},
            "preparation_time": "75 phút",
            "health_benefits": "Giàu protein từ hải sản, omega-3, khoáng chất"
        }
    },

    "bữa tối": {
        # Lẩu đặc sắc
        "Lẩu Mắm": {
            "description": "Lẩu mắm đặc sản miền Tây với nước dùng từ mắm cá linh, chua cay đậm đà",
            "ingredients": [
                {"name": "Mắm cá linh", "amount": "100ml"},
                {"name": "Cá lóc", "amount": "300g"},
                {"name": "Tôm sú", "amount": "200g"},
                {"name": "Thịt heo", "amount": "150g"},
                {"name": "Dứa", "amount": "200g"},
                {"name": "Đậu bắp", "amount": "100g"},
                {"name": "Rau muống", "amount": "200g"}
            ],
            "preparation": [
                "Bước 1: Pha mắm cá linh với nước, lọc bỏ cặn",
                "Bước 2: Cá lóc thái khoanh, ướp gia vị",
                "Bước 3: Dứa thái múi cau, đậu bắp thái khúc",
                "Bước 4: Nấu nước lẩu với mắm pha, cho dứa vào",
                "Bước 5: Nhúng các loại thịt cá và rau theo thứ tự"
            ],
            "nutrition": {"calories": 380, "protein": 42, "fat": 12, "carbs": 28},
            "preparation_time": "45 phút",
            "health_benefits": "Giàu protein, ít calo, nhiều vitamin từ rau củ"
        },

        "Bánh Xèo Miền Tây": {
            "description": "Bánh xèo miền Tây size lớn, giòn tan với nhân tôm thịt đậm đà",
            "ingredients": [
                {"name": "Bột gạo", "amount": "300g"},
                {"name": "Nước dừa", "amount": "400ml"},
                {"name": "Nghệ tươi", "amount": "20g"},
                {"name": "Tôm sú", "amount": "200g"},
                {"name": "Thịt ba chỉ", "amount": "150g"},
                {"name": "Giá đỗ", "amount": "100g"},
                {"name": "Rau sống", "amount": "200g"}
            ],
            "preparation": [
                "Bước 1: Pha bột gạo với nước dừa và nghệ",
                "Bước 2: Tôm bóc vỏ, thịt thái lát mỏng",
                "Bước 3: Đổ bột vào chảo nóng, tráng mỏng",
                "Bước 4: Cho nhân tôm thịt và giá đỗ vào",
                "Bước 5: Gấp đôi bánh, ăn kèm rau sống và nước mắm"
            ],
            "nutrition": {"calories": 420, "protein": 25, "fat": 16, "carbs": 48},
            "preparation_time": "40 phút",
            "health_benefits": "Giàu protein, vitamin A từ nghệ, chất xơ từ rau"
        },

        "Cháo Ếch Singapore": {
            "description": "Cháo ếch nấu theo phong cách Singapore với gia vị đặc trưng",
            "ingredients": [
                {"name": "Ếch", "amount": "2 con"},
                {"name": "Gạo tẻ", "amount": "150g"},
                {"name": "Gừng", "amount": "30g"},
                {"name": "Hành lá", "amount": "20g"},
                {"name": "Ngò rí", "amount": "15g"},
                {"name": "Tiêu đen", "amount": "1 tsp"},
                {"name": "Dầu mè", "amount": "1 tbsp"}
            ],
            "preparation": [
                "Bước 1: Ếch làm sạch, chặt miếng vừa ăn",
                "Bước 2: Gạo vo sạch, nấu cháo đến khi mềm",
                "Bước 3: Gừng thái sợi, phi thơm",
                "Bước 4: Cho ếch vào cháo nấu 15 phút",
                "Bước 5: Nêm nướng, rắc hành lá ngò rí, chấm dầu mè"
            ],
            "nutrition": {"calories": 350, "protein": 28, "fat": 8, "carbs": 42},
            "preparation_time": "50 phút",
            "health_benefits": "Protein cao, ít mỡ, tốt cho người bệnh và phục hồi sức khỏe"
        }
    }
}

def get_specialty_dish(meal_type: str, dish_name: str):
    """
    Lấy thông tin chi tiết về món ăn đặc sắc
    
    Args:
        meal_type: Loại bữa ăn (bữa sáng, bữa trưa, bữa tối)
        dish_name: Tên món ăn
        
    Returns:
        Dict chứa thông tin chi tiết món ăn hoặc None
    """
    meal_dishes = SPECIALTY_DISHES.get(meal_type, {})
    return meal_dishes.get(dish_name)

def get_all_specialty_dishes(meal_type: str = None):
    """
    Lấy tất cả món ăn đặc sắc theo loại bữa ăn
    
    Args:
        meal_type: Loại bữa ăn (tùy chọn)
        
    Returns:
        Dict hoặc List chứa thông tin món ăn
    """
    if meal_type:
        return SPECIALTY_DISHES.get(meal_type, {})
    return SPECIALTY_DISHES

def get_specialty_dish_names(meal_type: str):
    """
    Lấy danh sách tên các món ăn đặc sắc
    
    Args:
        meal_type: Loại bữa ăn
        
    Returns:
        List tên món ăn
    """
    meal_dishes = SPECIALTY_DISHES.get(meal_type, {})
    return list(meal_dishes.keys())
