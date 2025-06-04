"""
Services package for the application.
"""

# Import services for easy use
from .firestore_service import firestore_service

# Import from meal_services with explicit relative import
from .meal_services import (
    generate_weekly_meal_plan,
    generate_day_meal_plan,
    replace_day_meal_plan,
    create_fallback_meal,
    generate_meal,
    used_dishes_tracker
)

# Define function to process preparation steps from string to list
def _process_preparation_steps(preparation):
    """
    Process preparation steps to ensure they are in list format.
    
    Args:
        preparation: Preparation steps as string or list
        
    Returns:
        List[str]: Preparation steps as a list of strings
    """
    # If already a list, return as is
    if isinstance(preparation, list):
        return preparation
    
    # If none or empty, return empty list
    if not preparation:
        return []
    
    # Convert string to list
    preparation_str = str(preparation)
    
    # Try to split by common step separators
    if "Step " in preparation_str or "Bước " in preparation_str:
        # Split by step indicators
        import re
        steps = re.split(r'Step \d+:|Bước \d+:|Bước thứ \d+:', preparation_str)
        # Remove empty steps and strip whitespace
        steps = [step.strip() for step in steps if step.strip()]
        if steps:
            return steps
    
    # Try to split by periods followed by space
    steps = preparation_str.split('. ')
    if len(steps) > 1:
        # Make sure each step ends with a period
        steps = [step + ('.' if not step.endswith('.') else '') for step in steps]
        return steps
    
    # Try to split by newlines
    steps = preparation_str.split('\n')
    if len(steps) > 1:
        return [step.strip() for step in steps if step.strip()]
    
    # If all else fails, return the whole string as a single step
    return [preparation_str]

# Define the functions we need to expose
__all__ = [
    'firestore_service', 
    'generate_weekly_meal_plan', 
    'replace_day_meal_plan', 
    'generate_day_meal_plan', 
    'create_fallback_meal', 
    'generate_meal',
    'used_dishes_tracker',
    '_process_preparation_steps'  # Add the new function to __all__
]

# Print debug info to verify the correct function is being used
print(f"[DEBUG] Imported generate_weekly_meal_plan from {generate_weekly_meal_plan.__module__}")