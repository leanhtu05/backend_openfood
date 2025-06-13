"""
Update imports in relevant files to use the fixed Groq integration
"""
import os
import re
import glob

def update_imports():
    """Update all relevant files to use the fixed Groq integration"""
    
    # Patterns to match import statements - REVERT TO groq_integration.py (more complete)
    patterns = [
        (r'from\s+groq_integration_direct\s+import\s+groq_service', 'from groq_integration import groq_service  # Enhanced version'),
        (r'from\s+groq_integration_direct\s+import\s+GroqService', 'from groq_integration import GroqService  # Enhanced version'),
        (r'from\s+groq_integration_fixed\s+import\s+GroqService', 'from groq_integration import GroqService  # Enhanced version'),
        (r'import\s+groq_integration_direct', 'import groq_integration  # Enhanced version')
    ]
    
    # Get all Python files
    python_files = glob.glob('*.py') + glob.glob('**/*.py')
    
    updated_files = []
    
    for file_path in python_files:
        # Skip the fixed implementation files themselves
        if file_path in ['groq_integration_direct.py', 'direct_groq_client.py', 'update_imports.py']:
            continue
            
        try:
            # Try different encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"Could not decode {file_path} with any encoding")
                continue
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
        
        # Check if the file imports from groq_integration
        found_patterns = []
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                found_patterns.append((pattern, replacement))

        if found_patterns:
            print(f"Found imports in {file_path}")

            # Create backup
            backup_path = f"{file_path}.bak.import"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Update all matching imports
            updated_content = content
            for pattern, replacement in found_patterns:
                updated_content = re.sub(pattern, replacement, updated_content)
                print(f"  - Updated: {pattern}")

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