import os
import re

def update_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the addon name in preferences access
    content = content.replace(
        "context.preferences.addons['blender_project_manager']",
        "context.preferences.addons['blender_project_manager']"
    )
    content = content.replace(
        "ctx.preferences.addons['blender_project_manager']",
        "ctx.preferences.addons['blender_project_manager']"
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                update_file(file_path)

# Update all Python files in the current directory and subdirectories
process_directory('.') 