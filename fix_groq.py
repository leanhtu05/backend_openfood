"""
Fix groq_integration.py to remove proxies parameter
"""
import re
import os
import sys
import time

def fix_groq_file():
    """Fix the groq_integration.py file to work with groq 0.4.0"""
    
    file_path = 'groq_integration.py'
    backup_path = f'groq_integration.py.bak.{int(time.time())}'
    
    print(f"Creating backup of {file_path} to {backup_path}")
    # Create a backup of the original file
    with open(file_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    
    print(f"Reading file: {file_path}")
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the client initialization pattern
    updated_content = re.sub(
        r'(\s+)self\.client\s*=\s*groq\.Client\s*\(.*?\)',
        r'\1self.client = groq.Groq(api_key=self.api_key)',
        content
    )
    
    # If content was changed, write it back
    if updated_content != content:
        print("Updating client initialization...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("File updated successfully!")
    else:
        print("No changes were needed in the file.")

if __name__ == "__main__":
    print("Fixing groq_integration.py file...")
    fix_groq_file()
    print("Done!") 