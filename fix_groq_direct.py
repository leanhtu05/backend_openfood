"""
Fix groq_integration.py directly by rewriting the entire file
"""
import os
import re
from pathlib import Path

def fix_groq_file():
    """Fix the groq_integration.py file to work with groq 0.4.0"""
    
    file_path = 'groq_integration.py'
    backup_path = 'groq_integration.py.bak'
    
    print(f"Creating backup of {file_path} to {backup_path}")
    # Create a backup of the original file
    with open(file_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    
    print(f"Reading file: {file_path}")
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the line with the client initialization
    client_init_line = None
    for i, line in enumerate(lines):
        if 'self.client = groq.Client(' in line:
            client_init_line = i
            print(f"Found client initialization at line {i+1}: {line.strip()}")
            break
    
    if client_init_line is not None:
        # Replace the line with the correct client initialization
        lines[client_init_line] = '                    self.client = groq.Client(api_key=self.api_key)\n'
        print(f"Replaced with: {lines[client_init_line].strip()}")
        
        # Write the modified content back to the file
        print("Writing updated content to file...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("File updated successfully!")
    else:
        print("Could not find client initialization line.")

if __name__ == "__main__":
    print("Fixing groq_integration.py file directly...")
    fix_groq_file()
    print("Done!") 