#!/usr/bin/env python3
# Script để kiểm tra các thuộc tính của config

import config

print("=== Config module inspection ===")
print("Config dir:", dir(config))
print("\n=== Config.Config class ===")
print("Config.Config dir:", dir(config.Config))
print("\nChecking USE_ENHANCED_DISH_INFO:")
print("1. In config module?", hasattr(config, "USE_ENHANCED_DISH_INFO"))
print("2. In Config class?", hasattr(config.Config, "USE_ENHANCED_DISH_INFO"))
print("3. In config.config object?", hasattr(config.config, "USE_ENHANCED_DISH_INFO"))

# Try to access the variable in different ways
try:
    print("\n1. config.USE_ENHANCED_DISH_INFO =", config.USE_ENHANCED_DISH_INFO)
except AttributeError as e:
    print("Error accessing config.USE_ENHANCED_DISH_INFO:", e)

try:
    print("2. config.Config.USE_ENHANCED_DISH_INFO =", config.Config.USE_ENHANCED_DISH_INFO)
except AttributeError as e:
    print("Error accessing config.Config.USE_ENHANCED_DISH_INFO:", e)

try:
    print("3. config.config.USE_ENHANCED_DISH_INFO =", config.config.USE_ENHANCED_DISH_INFO)
except AttributeError as e:
    print("Error accessing config.config.USE_ENHANCED_DISH_INFO:", e) 