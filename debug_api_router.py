import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add debug code to api_router.py
with open("routers/api_router.py", "r", encoding="utf-8") as f:
    content = f.read()

# Check if debug code already exists
if "DEBUG_USE_AI" not in content:
    # Find the replace_meal function
    replace_meal_start = content.find("async def replace_meal(")
    if replace_meal_start > 0:
        # Find the line where use_ai is processed
        use_ai_line = content.find("replace_request.use_ai", replace_meal_start)
        if use_ai_line > 0:
            # Add debug code after this line
            line_end = content.find("\n", use_ai_line)
            if line_end > 0:
                debug_code = '''
            # DEBUG: Print use_ai information
            print(f"DEBUG_USE_AI: {replace_request.use_ai}")
            with open("debug_use_ai.log", "a", encoding="utf-8") as f:
                f.write(f"DEBUG_USE_AI: {replace_request.use_ai}\\n")
                f.write(f"Request data: {replace_request}\\n\\n")
                '''
                content = content[:line_end+1] + debug_code + content[line_end+1:]
                
                # Write the modified content back
                with open("routers/api_router.py", "w", encoding="utf-8") as f:
                    f.write(content)
                print("Added debug code to api_router.py")
            else:
                print("Could not find line end")
        else:
            print("Could not find use_ai line")
    else:
        print("Could not find replace_meal function")
else:
    print("Debug code already exists")

# Add debug code to services.py
with open("services/meal_services.py", "r", encoding="utf-8") as f:
    content = f.read()

# Check if debug code already exists
if "DEBUG_GENERATE_MEAL" not in content:
    # Find the generate_meal function
    generate_meal_start = content.find("def generate_meal(")
    if generate_meal_start > 0:
        # Find where use_ai is first used
        use_ai_line = content.find("if use_ai and AI_SERVICE and AI_AVAILABLE", generate_meal_start)
        if use_ai_line > 0:
            # Add debug code before this line
            line_start = content.rfind("\n", 0, use_ai_line)
            if line_start > 0:
                debug_code = '''
    # DEBUG: Print use_ai information
    print(f"DEBUG_GENERATE_MEAL: use_ai={use_ai}, AI_SERVICE={AI_SERVICE is not None}, AI_AVAILABLE={AI_AVAILABLE}")
    with open("debug_generate_meal.log", "a", encoding="utf-8") as f:
        f.write(f"DEBUG_GENERATE_MEAL: use_ai={use_ai}, AI_SERVICE={AI_SERVICE is not None}, AI_AVAILABLE={AI_AVAILABLE}\\n")
        f.write(f"meal_type={meal_type}, day_of_week={day_of_week}\\n\\n")
                '''
                content = content[:line_start+1] + debug_code + content[line_start+1:]
                
                # Write the modified content back
                with open("services/meal_services.py", "w", encoding="utf-8") as f:
                    f.write(content)
                print("Added debug code to services/meal_services.py")
            else:
                print("Could not find line start")
        else:
            print("Could not find use_ai line in generate_meal")
    else:
        print("Could not find generate_meal function")
else:
    print("Debug code already exists in services/meal_services.py")

print("\nDebug code added. Please restart the server and try the Flutter app again.") 