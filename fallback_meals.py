"""
Module chứa dữ liệu món ăn dự phòng khi không có kết nối tới AI.
Mô-đun này cung cấp các món ăn mẫu theo loại bữa ăn (sáng, trưa, tối).
"""

# Dữ liệu món ăn dự phòng cho từng bữa
FALLBACK_MEALS = {
    # Các món ăn sáng
    "bữa sáng": [
        {
            "name": "Bánh mì trứng và rau",
            "ingredients": [
                {"name": "Bánh mì", "amount": "2 lát"},
                {"name": "Trứng gà", "amount": "2 quả"},
                {"name": "Dầu oliu", "amount": "1 muỗng canh"},
                {"name": "Rau xà lách", "amount": "20g"},
                {"name": "Cà chua", "amount": "1/2 quả"},
                {"name": "Muối", "amount": "1/4 muỗng cà phê"},
                {"name": "Tiêu", "amount": "1 nhúm"}
            ],
            "preparation": "Đập trứng vào tô, đánh đều. Cho dầu vào chảo, đổ trứng vào và chiên đến khi chín. Cắt cà chua thành lát mỏng. Xếp trứng, rau xà lách và cà chua vào bánh mì. Rắc muối và tiêu lên trên.",
            "nutrition": {
                "calories": 350,
                "protein": 18,
                "fat": 20,
                "carbs": 28
            }
        },
        {
            "name": "Cháo yến mạch với trái cây",
            "ingredients": [
                {"name": "Yến mạch", "amount": "50g"},
                {"name": "Sữa ít béo", "amount": "200ml"},
                {"name": "Chuối", "amount": "1 quả"},
                {"name": "Dâu tây", "amount": "50g"},
                {"name": "Mật ong", "amount": "1 muỗng canh"},
                {"name": "Hạt chia", "amount": "1 muỗng canh"}
            ],
            "preparation": "Nấu yến mạch với sữa trong 3-5 phút. Cắt chuối thành lát và dâu tây thành miếng nhỏ. Đổ cháo vào bát, thêm trái cây, mật ong và hạt chia lên trên.",
            "nutrition": {
                "calories": 320,
                "protein": 12,
                "fat": 8,
                "carbs": 55
            }
        },
        {
            "name": "Sinh tố năng lượng",
            "ingredients": [
                {"name": "Chuối", "amount": "1 quả"},
                {"name": "Sữa chua Hy Lạp", "amount": "100g"},
                {"name": "Sữa hạnh nhân", "amount": "150ml"},
                {"name": "Bột protein", "amount": "1 muỗng"},
                {"name": "Dâu tây", "amount": "50g"},
                {"name": "Mật ong", "amount": "1 muỗng canh"}
            ],
            "preparation": "Cho tất cả nguyên liệu vào máy xay sinh tố và xay đều cho đến khi mịn. Đổ ra ly và thưởng thức ngay.",
            "nutrition": {
                "calories": 300,
                "protein": 20,
                "fat": 7,
                "carbs": 42
            }
        }
    ],
    
    # Các món ăn trưa
    "bữa trưa": [
        {
            "name": "Salad gà nướng",
            "ingredients": [
                {"name": "Ức gà", "amount": "150g"},
                {"name": "Rau xà lách", "amount": "100g"},
                {"name": "Cà chua bi", "amount": "50g"},
                {"name": "Dưa chuột", "amount": "1/2 quả"},
                {"name": "Ớt chuông", "amount": "1/2 quả"},
                {"name": "Dầu oliu", "amount": "1 muỗng canh"},
                {"name": "Giấm balsamic", "amount": "1 muỗng canh"},
                {"name": "Muối", "amount": "1/4 muỗng cà phê"},
                {"name": "Tiêu", "amount": "1 nhúm"}
            ],
            "preparation": "Ướp ức gà với muối, tiêu và nướng chín. Thái gà thành miếng vừa ăn. Trộn rau xà lách, cà chua bi, dưa chuột và ớt chuông. Thêm gà vào. Trộn dầu oliu và giấm balsamic làm nước sốt, rưới lên salad.",
            "nutrition": {
                "calories": 380,
                "protein": 40,
                "fat": 18,
                "carbs": 12
            }
        },
        {
            "name": "Cơm gạo lứt với đậu hũ",
            "ingredients": [
                {"name": "Gạo lứt", "amount": "80g"},
                {"name": "Đậu hũ", "amount": "150g"},
                {"name": "Bông cải xanh", "amount": "100g"},
                {"name": "Cà rốt", "amount": "1 củ nhỏ"},
                {"name": "Nấm", "amount": "50g"},
                {"name": "Dầu mè", "amount": "1 muỗng cà phê"},
                {"name": "Nước tương", "amount": "1 muỗng canh"},
                {"name": "Tỏi", "amount": "2 tép"}
            ],
            "preparation": "Nấu gạo lứt theo hướng dẫn. Cắt đậu hũ thành khối vuông và chiên vàng. Cắt rau củ thành miếng vừa ăn. Phi tỏi với dầu mè, xào rau củ và đậu hũ, thêm nước tương. Trộn đều với cơm.",
            "nutrition": {
                "calories": 450,
                "protein": 25,
                "fat": 12,
                "carbs": 65
            }
        },
        {
            "name": "Mì Ý sốt cà chua chay",
            "ingredients": [
                {"name": "Mì Ý nguyên cám", "amount": "80g"},
                {"name": "Cà chua", "amount": "200g"},
                {"name": "Nấm", "amount": "100g"},
                {"name": "Hành tây", "amount": "1/2 củ"},
                {"name": "Tỏi", "amount": "2 tép"},
                {"name": "Dầu oliu", "amount": "1 muỗng canh"},
                {"name": "Oregano", "amount": "1/2 muỗng cà phê"},
                {"name": "Muối", "amount": "1/4 muỗng cà phê"},
                {"name": "Tiêu", "amount": "1 nhúm"}
            ],
            "preparation": "Nấu mì theo hướng dẫn. Phi tỏi và hành tây với dầu oliu. Thêm cà chua đã cắt nhỏ và nấm. Nêm gia vị và oregano. Nấu nhỏ lửa 15 phút. Trộn sốt với mì.",
            "nutrition": {
                "calories": 400,
                "protein": 15,
                "fat": 10,
                "carbs": 70
            }
        }
    ],
    
    # Các món ăn tối
    "bữa tối": [
        {
            "name": "Thịt gà nướng với khoai lang và rau",
            "ingredients": [
                {"name": "Đùi gà", "amount": "150g"},
                {"name": "Khoai lang", "amount": "1 củ nhỏ"},
                {"name": "Bông cải xanh", "amount": "100g"},
                {"name": "Ớt chuông", "amount": "1/2 quả"},
                {"name": "Dầu oliu", "amount": "1 muỗng canh"},
                {"name": "Tỏi", "amount": "2 tép"},
                {"name": "Rosemary", "amount": "1 nhánh"},
                {"name": "Muối", "amount": "1/4 muỗng cà phê"},
                {"name": "Tiêu", "amount": "1 nhúm"}
            ],
            "preparation": "Ướp gà với tỏi băm, rosemary, muối, tiêu và dầu oliu. Nướng trong lò 25-30 phút. Cắt khoai lang thành miếng, tẩm dầu oliu và nướng cùng. Hấp rau củ và phục vụ cùng gà và khoai lang.",
            "nutrition": {
                "calories": 480,
                "protein": 35,
                "fat": 25,
                "carbs": 30
            }
        },
        {
            "name": "Cá hồi với quinoa và rau xanh",
            "ingredients": [
                {"name": "Cá hồi", "amount": "150g"},
                {"name": "Quinoa", "amount": "60g"},
                {"name": "Cải bó xôi", "amount": "100g"},
                {"name": "Chanh", "amount": "1/2 quả"},
                {"name": "Dầu oliu", "amount": "1 muỗng canh"},
                {"name": "Tỏi", "amount": "2 tép"},
                {"name": "Muối", "amount": "1/4 muỗng cà phê"},
                {"name": "Tiêu", "amount": "1 nhúm"},
                {"name": "Thì là", "amount": "1 nhánh"}
            ],
            "preparation": "Nấu quinoa theo hướng dẫn. Ướp cá hồi với nước cốt chanh, muối, tiêu. Nướng cá 12-15 phút. Xào cải bó xôi với tỏi và dầu oliu. Phục vụ cá với quinoa và rau xanh, rắc thì là lên trên.",
            "nutrition": {
                "calories": 500,
                "protein": 40,
                "fat": 25,
                "carbs": 30
            }
        },
        {
            "name": "Soup đậu lăng",
            "ingredients": [
                {"name": "Đậu lăng", "amount": "100g"},
                {"name": "Cà rốt", "amount": "1 củ"},
                {"name": "Hành tây", "amount": "1 củ nhỏ"},
                {"name": "Cần tây", "amount": "2 cây"},
                {"name": "Tỏi", "amount": "2 tép"},
                {"name": "Cà chua", "amount": "2 quả"},
                {"name": "Nước dùng rau củ", "amount": "500ml"},
                {"name": "Dầu oliu", "amount": "1 muỗng canh"},
                {"name": "Lá thơm", "amount": "1 nhánh"},
                {"name": "Muối", "amount": "1/4 muỗng cà phê"},
                {"name": "Tiêu", "amount": "1 nhúm"}
            ],
            "preparation": "Phi tỏi và hành tây với dầu oliu. Thêm cà rốt và cần tây thái nhỏ, xào 5 phút. Thêm đậu lăng, cà chua, lá thơm và nước dùng. Nấu khoảng 30 phút cho đến khi đậu lăng mềm. Nêm gia vị và phục vụ nóng.",
            "nutrition": {
                "calories": 350,
                "protein": 20,
                "fat": 8,
                "carbs": 55
            }
        }
    ]
}

# Thêm dữ liệu mẫu cho các bữa ăn để đảm bảo luôn có fallback

# Đảm bảo có đủ 3 loại bữa ăn
if "breakfast" not in FALLBACK_MEALS or not FALLBACK_MEALS["breakfast"]:
    FALLBACK_MEALS["breakfast"] = [
        {
            "name": "Bánh mì trứng ốp la",
            "description": "Bữa sáng giàu protein với trứng và bánh mì",
            "ingredients": [
                {"name": "Bánh mì", "amount": "2 lát"},
                {"name": "Trứng gà", "amount": "2 quả"},
                {"name": "Dầu ăn", "amount": "1 muỗng canh"}
            ],
            "preparation": "Đập trứng vào chảo nóng có dầu. Chiên chín vàng một mặt rồi lật, rắc chút muối tiêu. Ăn kèm với bánh mì nướng.",
            "total_nutrition": {
                "calories": 350,
                "protein": 20,
                "fat": 15,
                "carbs": 35
            }
        }
    ]

if "lunch" not in FALLBACK_MEALS or not FALLBACK_MEALS["lunch"]:
    FALLBACK_MEALS["lunch"] = [
        {
            "name": "Cơm gà xối mỡ",
            "description": "Món cơm với thịt gà thơm ngon",
            "ingredients": [
                {"name": "Gạo", "amount": "150g"},
                {"name": "Thịt gà", "amount": "200g"},
                {"name": "Hành lá", "amount": "20g"},
                {"name": "Gia vị", "amount": "vừa đủ"}
            ],
            "preparation": "Nấu cơm với gạo. Luộc gà chín, xé nhỏ. Phi hành lá với dầu ăn, xối lên gà. Trình bày cơm và gà ra đĩa.",
            "total_nutrition": {
                "calories": 450,
                "protein": 30,
                "fat": 15,
                "carbs": 45
            }
        }
    ]

if "dinner" not in FALLBACK_MEALS or not FALLBACK_MEALS["dinner"]:
    FALLBACK_MEALS["dinner"] = [
        {
            "name": "Canh rau cải thịt bò",
            "description": "Canh rau cải nấu với thịt bò bổ dưỡng",
            "ingredients": [
                {"name": "Rau cải", "amount": "200g"},
                {"name": "Thịt bò", "amount": "100g"},
                {"name": "Nước dùng", "amount": "500ml"},
                {"name": "Gia vị", "amount": "vừa đủ"}
            ],
            "preparation": "Thịt bò thái mỏng, ướp gia vị. Rau cải rửa sạch, cắt khúc. Đun sôi nước dùng, cho thịt bò vào nấu, sau đó cho rau cải vào, nêm nếm vừa ăn.",
            "total_nutrition": {
                "calories": 300,
                "protein": 25,
                "fat": 10,
                "carbs": 20
            }
        }
    ] 