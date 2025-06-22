# -*- coding: utf-8 -*-
"""
Database 200+ món ăn truyền thống Việt Nam
Dựa trên danh sách chi tiết từ người dùng
"""

# === 1. DẠNG SỢI (BÚN/MÌ CÁC LOẠI) ===
NOODLE_DISHES = {
    "bánh canh": {
        "description": "Được làm từ bột gạo, bột mì, hoặc bột sắn, cán thành sợi to và ngắn",
        "region": "Toàn quốc",
        "main_ingredients": ["bánh canh", "tôm", "cá", "giò heo"],
        "meal_type": ["lunch", "dinner"]
    },
    "bánh đa cua": {
        "description": "Đặc sản Hải Phòng, là bánh đa với nước dùng riêu cua",
        "region": "Miền Bắc",
        "main_ingredients": ["bánh đa", "cua đồng", "cà chua"],
        "meal_type": ["lunch", "dinner"]
    },
    "bánh tằm cà ri": {
        "description": "Đặc sản Cà Mau, loại bún gạo đặc biệt dùng với cà ri gà cay",
        "region": "Miền Nam",
        "main_ingredients": ["bánh tằm", "gà", "cà ri"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún bò huế": {
        "description": "Đặc sản xứ Huế, nước dùng có một ít mắm ruốc tạo nên hương vị đặc trưng",
        "region": "Miền Trung",
        "main_ingredients": ["bún", "thịt bò", "chả", "mắm ruốc"],
        "meal_type": ["breakfast", "lunch"]
    },
    "bún bung": {
        "description": "Đặc sản Hà Nội, bún nấu với sườn lợn và dọc mùng",
        "region": "Miền Bắc",
        "main_ingredients": ["bún", "sườn lợn", "dọc mùng"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún cá": {
        "description": "Đặc sản Hà Nội, bún và chả cá nướng trộn nước mắm, rau sống",
        "region": "Miền Bắc",
        "main_ingredients": ["bún", "chả cá", "rau thơm"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún chả": {
        "description": "Đặc sản Hà Nội, bún ăn kèm chả viên và chả miếng với nước chấm",
        "region": "Miền Bắc",
        "main_ingredients": ["bún", "chả", "thịt nướng"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún măng vịt": {
        "description": "Bún măng dùng với nước hầm xương vịt",
        "region": "Miền Bắc",
        "main_ingredients": ["bún", "măng", "thịt vịt"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún chả cá": {
        "description": "Đặc sản Đà Nẵng, bún với chả cá chan nước dùng nóng",
        "region": "Miền Trung",
        "main_ingredients": ["bún", "chả cá", "nước dùng"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún chạo tôm": {
        "description": "Đặc sản Huế, tôm xiên vào que mía nướng ăn kèm bún, rau sống",
        "region": "Miền Trung",
        "main_ingredients": ["bún", "tôm nướng", "rau sống"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún đậu mắm tôm": {
        "description": "Đặc sản Miền Bắc, bún ăn với đậu rán và mắm tôm",
        "region": "Miền Bắc",
        "main_ingredients": ["bún", "đậu phụ", "mắm tôm"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún mắm": {
        "description": "Đặc sản Trà Vinh, Sóc Trăng, bún chan nước dùng làm từ mắm cá linh hay cá sặc",
        "region": "Miền Nam",
        "main_ingredients": ["bún", "mắm cá", "thịt heo"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún mọc": {
        "description": "Đặc sản Hà Nội, bún với mọc chan nước dùng",
        "region": "Miền Bắc",
        "main_ingredients": ["bún", "mọc", "nước dùng"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún ốc": {
        "description": "Đặc sản Miền Bắc, bún, ốc với nước dùng có vị chua",
        "region": "Miền Bắc",
        "main_ingredients": ["bún", "ốc", "cà chua"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún riêu cua": {
        "description": "Phổ biến khắp cả nước, bún và riêu cua được nấu từ gạch cua",
        "region": "Toàn quốc",
        "main_ingredients": ["bún", "cua đồng", "cà chua", "đậu phụ"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún thịt nướng": {
        "description": "Đặc sản Huế, bún ăn với thịt nướng cùng nước mắm và rau sống kiểu Huế",
        "region": "Miền Trung",
        "main_ingredients": ["bún", "thịt nướng", "rau thơm"],
        "meal_type": ["lunch", "dinner"]
    },
    "bún thang": {
        "description": "Đặc sản Hà Nội, bún ăn với nước dùng và cần đến khoảng 20 nguyên liệu",
        "region": "Miền Bắc",
        "main_ingredients": ["bún", "trứng", "giò lụa", "tôm", "lạp xưởng"],
        "meal_type": ["breakfast", "lunch"]
    },
    "cao lầu": {
        "description": "Đặc sản Quảng Nam (Hội An), sợi mì được chế biến công phu ăn cùng giá đỗ và thịt xá xíu",
        "region": "Miền Trung",
        "main_ingredients": ["mì cao lầu", "thịt xá xíu", "giá đỗ"],
        "meal_type": ["lunch", "dinner"]
    },
    "hủ tiếu": {
        "description": "Đặc sản Miền Nam, bánh hủ tiếu chan nước dùng với thịt băm nhỏ, lòng heo",
        "region": "Miền Nam",
        "main_ingredients": ["hủ tiếu", "thịt heo", "tôm", "lòng heo"],
        "meal_type": ["breakfast", "lunch"]
    },
    "mì quảng": {
        "description": "Đặc sản Quảng Nam, được làm từ sợi mì bằng bột gạo xay mịn",
        "region": "Miền Trung",
        "main_ingredients": ["mì quảng", "thịt heo", "tôm", "trứng cút"],
        "meal_type": ["lunch", "dinner"]
    },
    "mì xào": {
        "description": "Phổ biến khắp cả nước, mì xào chín giòn với trứng, thịt, rau, hải sản",
        "region": "Toàn quốc",
        "main_ingredients": ["mì", "thịt", "rau", "trứng"],
        "meal_type": ["lunch", "dinner"]
    },
    "mì xào giòn": {
        "description": "Phổ biến khắp cả nước, mì trứng chiên giòn, phủ hải sản, rau và nước sốt",
        "region": "Toàn quốc",
        "main_ingredients": ["mì", "hải sản", "rau", "nước sốt"],
        "meal_type": ["lunch", "dinner"]
    },
    "miến lươn": {
        "description": "Đặc sản Nghệ An, được nấu từ miến với thịt lươn",
        "region": "Miền Trung",
        "main_ingredients": ["miến", "lươn", "nước dùng"],
        "meal_type": ["lunch", "dinner"]
    },
    "miến trộn": {
        "description": "Phổ biến khắp cả nước, miến được xào hoặc chần qua, trộn với tôm hoặc cua",
        "region": "Toàn quốc",
        "main_ingredients": ["miến", "tôm", "cua"],
        "meal_type": ["lunch", "dinner"]
    },
    "phở": {
        "description": "Một trong những món ăn đặc trưng nhất của ẩm thực Việt Nam",
        "region": "Miền Bắc",
        "main_ingredients": ["bánh phở", "thịt bò", "nước dùng"],
        "meal_type": ["breakfast", "lunch", "dinner"]
    }
}

# === 2. CƠM ===
RICE_DISHES = {
    "cơm bụi": {
        "description": "Phổ biến khắp cả nước, cơm bình dân với nhiều món ăn đa dạng",
        "region": "Toàn quốc",
        "main_ingredients": ["cơm", "thịt", "rau"],
        "meal_type": ["lunch", "dinner"]
    },
    "cơm cháy ninh bình": {
        "description": "Đặc sản Ninh Bình, Hải Phòng, là phần cơm dưới đáy nồi khi nấu chín vàng giòn",
        "region": "Miền Bắc",
        "main_ingredients": ["cơm cháy", "hải sản"],
        "meal_type": ["lunch", "dinner"]
    },
    "cơm hến": {
        "description": "Đặc sản Huế, cơm nguội trộn với hến luộc, nước hến, mắm ruốc",
        "region": "Miền Trung",
        "main_ingredients": ["cơm", "hến", "mắm ruốc", "rau"],
        "meal_type": ["lunch", "dinner"]
    },
    "cơm gà quảng nam": {
        "description": "Đặc sản Quảng Nam, cơm tẻ chín tới ăn với gà luộc rưới nước dùng gà",
        "region": "Miền Trung",
        "main_ingredients": ["cơm", "thịt gà", "nước dùng"],
        "meal_type": ["lunch", "dinner"]
    },
    "cơm lam": {
        "description": "Đặc sản Trung du và miền núi phía Bắc, Tây Nguyên, được làm từ gạo nếp",
        "region": "Tây Nguyên",
        "main_ingredients": ["gạo nếp", "ống tre"],
        "meal_type": ["lunch", "dinner"]
    },
    "cơm nắm": {
        "description": "Đặc sản Miền Bắc, cơm trắng nóng hổi đem nén chặt thành tấm",
        "region": "Miền Bắc",
        "main_ingredients": ["cơm", "muối vừng"],
        "meal_type": ["breakfast", "lunch"]
    },
    "cơm nếp": {
        "description": "Phổ biến khắp cả nước, được nấu bằng gạo nếp trực tiếp trong nước",
        "region": "Toàn quốc",
        "main_ingredients": ["gạo nếp"],
        "meal_type": ["breakfast", "lunch"]
    },
    "cơm rang": {
        "description": "Phổ biến khắp cả nước, cơm cùng với dầu ăn hoặc mỡ được chiên",
        "region": "Toàn quốc",
        "main_ingredients": ["cơm", "thịt", "trứng"],
        "meal_type": ["lunch", "dinner"]
    },
    "cơm tấm": {
        "description": "Đặc sản Miền Nam, cơm tấm (gạo tẻ vụn) có thể gồm sườn, bì, chả, trứng",
        "region": "Miền Nam",
        "main_ingredients": ["cơm tấm", "sườn nướng", "bì", "chả"],
        "meal_type": ["breakfast", "lunch", "dinner"]
    },
    "cơm trắng": {
        "description": "Phổ biến khắp cả nước, được làm ra từ gạo bằng cách đem nấu với một lượng vừa đủ nước",
        "region": "Toàn quốc",
        "main_ingredients": ["gạo"],
        "meal_type": ["lunch", "dinner"]
    }
}

# === 3. XÔI ===
STICKY_RICE_DISHES = {
    "xôi gà": {"region": "Toàn quốc", "main_ingredients": ["gạo nếp", "thịt gà"], "meal_type": ["breakfast"]},
    "xôi gấc": {"region": "Toàn quốc", "main_ingredients": ["gạo nếp", "quả gấc"], "meal_type": ["breakfast"]},
    "xôi đỗ xanh": {"region": "Miền Bắc", "main_ingredients": ["gạo nếp", "đỗ xanh"], "meal_type": ["breakfast"]},
    "xôi lạc": {"region": "Toàn quốc", "main_ingredients": ["gạo nếp", "đậu phộng"], "meal_type": ["breakfast"]},
    "xôi xéo": {"region": "Miền Bắc", "main_ingredients": ["gạo nếp", "đậu xanh"], "meal_type": ["breakfast"]},
    "xôi ngũ sắc": {"region": "Tây Bắc", "main_ingredients": ["gạo nếp", "lá cơm"], "meal_type": ["breakfast"]},
    "xôi trắng": {"region": "Toàn quốc", "main_ingredients": ["gạo nếp"], "meal_type": ["breakfast"]}
}

# === 4. BÁNH MẶN ===
SAVORY_CAKES = {
    "bánh mì": {"region": "Toàn quốc", "main_ingredients": ["bánh mì", "thịt", "pate"], "meal_type": ["breakfast"]},
    "bánh cuốn": {"region": "Toàn quốc", "main_ingredients": ["bột gạo", "thịt heo"], "meal_type": ["breakfast"]},
    "bánh xèo": {"region": "Toàn quốc", "main_ingredients": ["bột gạo", "tôm", "thịt"], "meal_type": ["lunch", "dinner"]},
    "bánh bao": {"region": "Toàn quốc", "main_ingredients": ["bột mì", "thịt heo"], "meal_type": ["breakfast"]},
    "bánh chưng": {"region": "Miền Bắc", "main_ingredients": ["gạo nếp", "thịt heo"], "meal_type": ["breakfast"]},
    "bánh tét": {"region": "Miền Nam", "main_ingredients": ["gạo nếp", "thịt heo"], "meal_type": ["breakfast"]},
    "bánh bèo": {"region": "Miền Trung", "main_ingredients": ["bột gạo", "tôm"], "meal_type": ["breakfast"]},
    "bánh căn": {"region": "Miền Trung", "main_ingredients": ["bột gạo", "tôm"], "meal_type": ["breakfast"]},
    "bánh khọt": {"region": "Miền Nam", "main_ingredients": ["bột gạo", "tôm"], "meal_type": ["breakfast"]},
    "bánh ít": {"region": "Toàn quốc", "main_ingredients": ["bột nếp", "tôm"], "meal_type": ["breakfast"]}
}

# === 5. CHÁO/CANH/LẨU ===
SOUP_DISHES = {
    "cháo lòng": {"region": "Toàn quốc", "main_ingredients": ["gạo", "lòng heo"], "meal_type": ["breakfast", "dinner"]},
    "cháo gà": {"region": "Toàn quốc", "main_ingredients": ["gạo", "thịt gà"], "meal_type": ["breakfast", "dinner"]},
    "cháo cá": {"region": "Toàn quốc", "main_ingredients": ["gạo", "cá"], "meal_type": ["breakfast", "dinner"]},
    "lẩu thái": {"region": "Toàn quốc", "main_ingredients": ["tôm", "cá", "rau"], "meal_type": ["dinner"]},
    "lẩu mắm": {"region": "Miền Nam", "main_ingredients": ["cá", "mắm", "rau"], "meal_type": ["dinner"]},
    "canh chua": {"region": "Miền Nam", "main_ingredients": ["cá", "cà chua", "dứa"], "meal_type": ["lunch", "dinner"]},
    "canh bí": {"region": "Toàn quốc", "main_ingredients": ["bí đao", "tôm"], "meal_type": ["lunch", "dinner"]},
    "súp cua": {"region": "Toàn quốc", "main_ingredients": ["cua", "trứng"], "meal_type": ["lunch", "dinner"]}
}

# === 6. MÓN CUỐN ===
ROLL_DISHES = {
    "nem cuốn": {"region": "Toàn quốc", "main_ingredients": ["bánh tráng", "tôm", "thịt"], "meal_type": ["lunch", "dinner"]},
    "gỏi cuốn": {"region": "Miền Nam", "main_ingredients": ["bánh tráng", "tôm", "rau"], "meal_type": ["lunch", "dinner"]},
    "nem rán": {"region": "Toàn quốc", "main_ingredients": ["bánh đa nem", "thịt", "rau"], "meal_type": ["lunch", "dinner"]},
    "bò bía": {"region": "Toàn quốc", "main_ingredients": ["bánh tráng", "thịt bò"], "meal_type": ["lunch", "dinner"]},
    "nem chua": {"region": "Toàn quốc", "main_ingredients": ["thịt heo", "lá chuối"], "meal_type": ["lunch", "dinner"]}
}

# === 7. MÓN NƯỚNG/RANG/XÀO ===
GRILLED_DISHES = {
    "thịt nướng": {"region": "Toàn quốc", "main_ingredients": ["thịt heo", "gia vị"], "meal_type": ["lunch", "dinner"]},
    "gà nướng": {"region": "Toàn quốc", "main_ingredients": ["thịt gà", "gia vị"], "meal_type": ["lunch", "dinner"]},
    "cá nướng": {"region": "Toàn quốc", "main_ingredients": ["cá", "gia vị"], "meal_type": ["lunch", "dinner"]},
    "tôm nướng": {"region": "Toàn quốc", "main_ingredients": ["tôm", "gia vị"], "meal_type": ["lunch", "dinner"]},
    "rau muống xào": {"region": "Toàn quốc", "main_ingredients": ["rau muống", "tỏi"], "meal_type": ["lunch", "dinner"]},
    "thịt kho": {"region": "Toàn quốc", "main_ingredients": ["thịt heo", "nước mắm"], "meal_type": ["lunch", "dinner"]},
    "cá kho": {"region": "Toàn quốc", "main_ingredients": ["cá", "nước mắm"], "meal_type": ["lunch", "dinner"]},
    "tôm rang": {"region": "Miền Nam", "main_ingredients": ["tôm", "gia vị"], "meal_type": ["lunch", "dinner"]}
}

# === 8. BÁNH NGỌT ===
SWEET_CAKES = {
    "bánh flan": {"region": "Toàn quốc", "main_ingredients": ["trứng", "sữa"], "meal_type": ["dessert"]},
    "bánh bò": {"region": "Miền Nam", "main_ingredients": ["bột gạo", "đường"], "meal_type": ["dessert"]},
    "bánh da lợn": {"region": "Miền Nam", "main_ingredients": ["bột năng", "đậu xanh"], "meal_type": ["dessert"]},
    "bánh trôi": {"region": "Miền Bắc", "main_ingredients": ["bột nếp", "đường"], "meal_type": ["dessert"]},
    "bánh rán": {"region": "Miền Bắc", "main_ingredients": ["bột nếp", "đậu xanh"], "meal_type": ["dessert"]},
    "bánh pía": {"region": "Miền Nam", "main_ingredients": ["bột mì", "sầu riêng"], "meal_type": ["dessert"]}
}

# === TỔNG HỢP TẤT CẢ MÓN ĂN ===
ALL_TRADITIONAL_DISHES = {
    **NOODLE_DISHES,
    **RICE_DISHES,
    **STICKY_RICE_DISHES,
    **SAVORY_CAKES,
    **SOUP_DISHES,
    **ROLL_DISHES,
    **GRILLED_DISHES,
    **SWEET_CAKES
}
