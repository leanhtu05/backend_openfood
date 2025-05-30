"""
Update imports in relevant files to use the fixed Groq integration
"""
import os
import re
import glob

def update_imports():
    """Update all relevant files to use the fixed Groq integration"""
    
    # Pattern to match import statements for groq_integration
    pattern = r'from\s+groq_integration\s+import\s+groq_service'
    replacement = 'from groq_integration_direct import groq_service  # Fixed version'
    
    # Get all Python files
    python_files = glob.glob('*.py') + glob.glob('**/*.py')
    
    updated_files = []
    
    for file_path in python_files:
        # Skip the fixed implementation files themselves
        if file_path in ['groq_integration_direct.py', 'direct_groq_client.py', 'update_imports.py']:
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the file imports groq_service
        if re.search(pattern, content):
            print(f"Found import in {file_path}")
            
            # Create backup
            backup_path = f"{file_path}.bak.import"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update the import
            updated_content = re.sub(pattern, replacement, content)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            updated_files.append(file_path)
    
    print(f"\nUpdated {len(updated_files)} files:")
    for file_path in updated_files:
        print(f"- {file_path}")

if __name__ == "__main__":
    print("Updating imports to use the fixed Groq integration...")
    update_imports()
    print("Done!") 