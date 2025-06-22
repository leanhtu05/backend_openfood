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
            "description": "Bánh mì sandwich với trứng chiên và rau tươi, bữa sáng bổ dưỡng và ngon miệng",
            "ingredients": [
                {"name": "Bánh mì", "amount": "2 lát"},
                {"name": "Trứng gà", "amount": "2 quả"},
                {"name": "Dầu oliu", "amount": "1 muỗng canh"},
                {"name": "Rau xà lách", "amount": "20g"},
                {"name": "Cà chua", "amount": "1/2 quả"},
                {"name": "Muối", "amount": "1/4 muỗng cà phê"},
                {"name": "Tiêu", "amount": "1 nhúm"}
            ],
            "preparation": [
                "Đập trứng vào tô, đánh đều với muối và tiêu",
                "Cho dầu oliu vào chảo, đổ trứng vào và chiên đến khi chín vàng",
                "Cắt cà chua thành lát mỏng, rửa sạch rau xà lách",
                "Xếp trứng, rau xà lách và cà chua vào bánh mì",
                "Trình bày đẹp mắt và thưởng thức"
            ],
            "nutrition": {
                "calories": 350,
                "protein": 18,
                "fat": 20,
                "carbs": 28
            },
            "preparation_time": "10 phút",
            "health_benefits": "Giàu protein từ trứng giúp xây dựng cơ bắp. Rau xà lách và cà chua cung cấp vitamin C và chất xơ tốt cho tiêu hóa. Bánh mì cung cấp carbohydrate cho năng lượng buổi sáng."
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
        },
        # 🔧 FIX: Thêm nhiều món ăn sáng đa dạng
        {
            "name": "Phở Gà Truyền Thống",
            "description": "Phở gà nóng hổi với nước dùng thơm ngon",
            "ingredients": [
                {"name": "Bánh phở", "amount": "150g"},
                {"name": "Thịt gà", "amount": "100g"},
                {"name": "Hành lá", "amount": "20g"},
                {"name": "Rau thơm", "amount": "30g"},
                {"name": "Nước dùng gà", "amount": "400ml"}
            ],
            "preparation": [
                "Luộc bánh phở trong nước sôi 2-3 phút",
                "Thái thịt gà thành lát mỏng",
                "Rửa sạch rau thơm và hành lá",
                "Cho bánh phở vào tô, xếp thịt gà lên trên",
                "Đổ nước dùng nóng vào, rắc hành lá và rau thơm"
            ],
            "nutrition": {
                "calories": 380,
                "protein": 25,
                "fat": 8,
                "carbs": 55
            },
            "preparation_time": "15 phút",
            "health_benefits": "Giàu protein từ thịt gà, carbohydrate từ bánh phở cung cấp năng lượng, nước dùng bổ sung nước và khoáng chất"
        },
        {
            "name": "Xôi Xéo Đậu Xanh",
            "description": "Xôi xéo truyền thống với đậu xanh và nước cốt dừa",
            "ingredients": [
                {"name": "Gạo nếp", "amount": "100g"},
                {"name": "Đậu xanh", "amount": "50g"},
                {"name": "Nước cốt dừa", "amount": "100ml"},
                {"name": "Muối", "amount": "1/2 tsp"},
                {"name": "Đường", "amount": "1 tsp"}
            ],
            "preparation": [
                "Ngâm gạo nếp 4-6 tiếng",
                "Đậu xanh luộc chín, nghiền nhuyễn",
                "Nấu xôi với nước cốt dừa và muối",
                "Trộn đậu xanh với xôi",
                "Trang trí và thưởng thức"
            ],
            "nutrition": {
                "calories": 420,
                "protein": 12,
                "fat": 15,
                "carbs": 65
            },
            "preparation_time": "30 phút",
            "health_benefits": "Đậu xanh giàu protein thực vật, gạo nếp cung cấp năng lượng bền vững, nước cốt dừa bổ sung chất béo tốt"
        },
        {
            "name": "Bánh Cuốn Tôm Thịt",
            "description": "Bánh cuốn mỏng với nhân tôm thịt thơm ngon",
            "ingredients": [
                {"name": "Bánh cuốn", "amount": "3 cái"},
                {"name": "Thịt heo", "amount": "80g"},
                {"name": "Tôm", "amount": "60g"},
                {"name": "Nấm mèo", "amount": "30g"},
                {"name": "Hành lá", "amount": "15g"},
                {"name": "Nước mắm", "amount": "2 tsp"}
            ],
            "preparation": [
                "Thịt heo và tôm băm nhỏ",
                "Nấm mèo ngâm mềm, thái nhỏ",
                "Xào nhân với hành lá và nước mắm",
                "Cuốn nhân vào bánh cuốn",
                "Ăn kèm với nước chấm"
            ],
            "nutrition": {
                "calories": 340,
                "protein": 22,
                "fat": 10,
                "carbs": 40
            },
            "preparation_time": "25 phút",
            "health_benefits": "Tôm và thịt cung cấp protein chất lượng cao, bánh cuốn ít dầu mỡ, dễ tiêu hóa"
        },
        {
            "name": "Cháo Gà Hạt Sen",
            "description": "Cháo gà bổ dưỡng với hạt sen thơm ngon",
            "ingredients": [
                {"name": "Gạo tẻ", "amount": "80g"},
                {"name": "Thịt gà", "amount": "100g"},
                {"name": "Hạt sen", "amount": "40g"},
                {"name": "Hành lá", "amount": "15g"},
                {"name": "Gừng", "amount": "10g"}
            ],
            "preparation": [
                "Gạo vo sạch, nấu cháo",
                "Thịt gà luộc chín, xé sợi",
                "Hạt sen luộc mềm",
                "Cho gà và hạt sen vào cháo",
                "Nêm nếm, rắc hành lá"
            ],
            "nutrition": {
                "calories": 360,
                "protein": 28,
                "fat": 6,
                "carbs": 50
            },
            "preparation_time": "40 phút",
            "health_benefits": "Hạt sen giàu vitamin B, thịt gà cung cấp protein, cháo dễ tiêu hóa và bổ dưỡng"
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
        },
        # 🔧 FIX: Thêm nhiều món ăn trưa đa dạng
        {
            "name": "Bún Bò Huế Đặc Biệt",
            "description": "Bún bò Huế cay nồng với thịt bò và chả",
            "ingredients": [
                {"name": "Bún", "amount": "150g"},
                {"name": "Thịt bò", "amount": "120g"},
                {"name": "Chả lụa", "amount": "50g"},
                {"name": "Hành lá", "amount": "20g"},
                {"name": "Rau thơm", "amount": "30g"},
                {"name": "Nước dùng", "amount": "400ml"}
            ],
            "preparation": [
                "Luộc bún trong nước sôi",
                "Thái thịt bò và chả lụa",
                "Chuẩn bị rau thơm và hành lá",
                "Xếp bún vào tô, cho thịt bò và chả lên trên",
                "Đổ nước dùng nóng, rắc rau thơm"
            ],
            "nutrition": {
                "calories": 480,
                "protein": 32,
                "fat": 12,
                "carbs": 58
            },
            "preparation_time": "20 phút",
            "health_benefits": "Thịt bò giàu sắt và protein, bún cung cấp carbohydrate, rau thơm bổ sung vitamin"
        },
        {
            "name": "Cơm Âm Phủ Huế",
            "description": "Cơm âm phủ truyền thống Huế với nhiều loại thịt",
            "ingredients": [
                {"name": "Cơm trắng", "amount": "150g"},
                {"name": "Thịt heo", "amount": "80g"},
                {"name": "Tôm", "amount": "60g"},
                {"name": "Chả cá", "amount": "40g"},
                {"name": "Rau sống", "amount": "50g"},
                {"name": "Nước mắm pha", "amount": "30ml"}
            ],
            "preparation": [
                "Nấu cơm dẻo",
                "Luộc thịt heo và tôm",
                "Chiên chả cá vàng",
                "Chuẩn bị rau sống",
                "Xếp tất cả lên cơm, chấm nước mắm"
            ],
            "nutrition": {
                "calories": 520,
                "protein": 28,
                "fat": 18,
                "carbs": 62
            },
            "preparation_time": "30 phút",
            "health_benefits": "Đa dạng protein từ thịt, tôm, cá; rau sống cung cấp vitamin và chất xơ"
        },
        {
            "name": "Mì Quảng Tôm Cua",
            "description": "Mì Quảng đặc sản miền Trung với tôm cua",
            "ingredients": [
                {"name": "Mì Quảng", "amount": "120g"},
                {"name": "Tôm", "amount": "100g"},
                {"name": "Cua đồng", "amount": "80g"},
                {"name": "Thịt heo", "amount": "60g"},
                {"name": "Trứng cút", "amount": "4 quả"},
                {"name": "Rau thơm", "amount": "40g"}
            ],
            "preparation": [
                "Luộc mì Quảng",
                "Nấu nước dùng từ tôm cua",
                "Luộc thịt heo và trứng cút",
                "Xếp mì vào tô với tôm, cua, thịt",
                "Đổ nước dùng, rắc rau thơm"
            ],
            "nutrition": {
                "calories": 550,
                "protein": 35,
                "fat": 20,
                "carbs": 55
            },
            "preparation_time": "35 phút",
            "health_benefits": "Hải sản giàu omega-3, protein đa dạng, mì Quảng cung cấp năng lượng"
        },
        {
            "name": "Hủ Tiếu Nam Vang",
            "description": "Hủ tiếu Nam Vang với tôm, thịt và gan",
            "ingredients": [
                {"name": "Hủ tiếu", "amount": "130g"},
                {"name": "Tôm", "amount": "80g"},
                {"name": "Thịt heo", "amount": "70g"},
                {"name": "Gan heo", "amount": "50g"},
                {"name": "Giá đỗ", "amount": "40g"},
                {"name": "Hành lá", "amount": "15g"}
            ],
            "preparation": [
                "Luộc hủ tiếu mềm",
                "Luộc tôm, thịt heo và gan",
                "Trần giá đỗ qua nước sôi",
                "Xếp hủ tiếu vào tô với topping",
                "Đổ nước dùng trong, rắc hành lá"
            ],
            "nutrition": {
                "calories": 460,
                "protein": 30,
                "fat": 15,
                "carbs": 50
            },
            "preparation_time": "25 phút",
            "health_benefits": "Gan heo giàu sắt và vitamin A, tôm cung cấp protein chất lượng cao"
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
        },
        # 🔧 FIX: Thêm nhiều món ăn tối đa dạng
        {
            "name": "Lẩu Thái Hải Sản",
            "description": "Lẩu Thái chua cay với hải sản tươi ngon",
            "ingredients": [
                {"name": "Tôm", "amount": "150g"},
                {"name": "Cua", "amount": "100g"},
                {"name": "Cá", "amount": "120g"},
                {"name": "Rau muống", "amount": "100g"},
                {"name": "Nấm", "amount": "80g"},
                {"name": "Nước dùng lẩu Thái", "amount": "500ml"}
            ],
            "preparation": [
                "Chuẩn bị hải sản tươi sạch",
                "Rửa rau muống và nấm",
                "Đun sôi nước dùng lẩu Thái",
                "Cho hải sản vào nấu trước",
                "Thêm rau và nấm, nấu chín"
            ],
            "nutrition": {
                "calories": 420,
                "protein": 45,
                "fat": 12,
                "carbs": 25
            },
            "preparation_time": "30 phút",
            "health_benefits": "Hải sản giàu omega-3 và protein, rau xanh cung cấp vitamin và khoáng chất"
        },
        {
            "name": "Bánh Xèo Miền Tây",
            "description": "Bánh xèo giòn rụm với tôm thịt và giá đỗ",
            "ingredients": [
                {"name": "Bột bánh xèo", "amount": "150g"},
                {"name": "Tôm", "amount": "100g"},
                {"name": "Thịt ba chỉ", "amount": "80g"},
                {"name": "Giá đỗ", "amount": "100g"},
                {"name": "Rau sống", "amount": "80g"},
                {"name": "Nước mắm pha", "amount": "50ml"}
            ],
            "preparation": [
                "Pha bột bánh xèo với nước",
                "Tôm và thịt ướp gia vị",
                "Đổ bột vào chảo nóng",
                "Cho tôm thịt và giá đỗ vào",
                "Gấp đôi bánh, ăn kèm rau sống"
            ],
            "nutrition": {
                "calories": 480,
                "protein": 28,
                "fat": 22,
                "carbs": 45
            },
            "preparation_time": "25 phút",
            "health_benefits": "Protein từ tôm thịt, giá đỗ giàu vitamin C, rau sống cung cấp chất xơ"
        },
        {
            "name": "Cà Ri Gà Khoai Tây",
            "description": "Cà ri gà thơm ngon với khoai tây mềm",
            "ingredients": [
                {"name": "Thịt gà", "amount": "200g"},
                {"name": "Khoai tây", "amount": "150g"},
                {"name": "Cà rốt", "amount": "80g"},
                {"name": "Nước cốt dừa", "amount": "200ml"},
                {"name": "Bột cà ri", "amount": "2 tbsp"},
                {"name": "Hành tây", "amount": "1 củ"}
            ],
            "preparation": [
                "Thịt gà cắt miếng vừa ăn",
                "Khoai tây và cà rốt cắt khối",
                "Phi hành tây với bột cà ri",
                "Cho gà vào xào, thêm nước cốt dừa",
                "Thêm khoai tây, cà rốt và niêu"
            ],
            "nutrition": {
                "calories": 520,
                "protein": 35,
                "fat": 25,
                "carbs": 40
            },
            "preparation_time": "40 phút",
            "health_benefits": "Thịt gà cung cấp protein chất lượng, khoai tây giàu vitamin C, nước cốt dừa bổ sung chất béo tốt"
        },
        {
            "name": "Chả Cá Lã Vọng",
            "description": "Chả cá Hà Nội truyền thống với thì là",
            "ingredients": [
                {"name": "Cá tra", "amount": "200g"},
                {"name": "Thì là", "amount": "50g"},
                {"name": "Hành lá", "amount": "30g"},
                {"name": "Bún", "amount": "100g"},
                {"name": "Đậu phộng rang", "amount": "30g"},
                {"name": "Mắm tôm", "amount": "2 tsp"}
            ],
            "preparation": [
                "Cá tra ướp nghệ và nướng",
                "Thì là và hành lá rửa sạch",
                "Luộc bún mềm",
                "Xào cá với thì là và hành lá",
                "Ăn kèm bún và đậu phộng"
            ],
            "nutrition": {
                "calories": 450,
                "protein": 32,
                "fat": 18,
                "carbs": 35
            },
            "preparation_time": "30 phút",
            "health_benefits": "Cá giàu omega-3 và protein, thì là có tính kháng khuẩn, đậu phộng cung cấp chất béo tốt"
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