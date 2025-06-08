"""
Utility functions for processing preparation steps
"""

def process_preparation_steps(preparation):
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