#!/usr/bin/env python
"""
Complete Authentication Disabler
Creates a clean views.py without any authentication dependencies
"""

def create_clean_views():
    """Create a completely clean views.py without authentication"""
    
    print("🔧 CREATING CLEAN VIEWS: Complete authentication removal")
    
    # Read the problematic views file
    with open("studio/views.py", 'r') as f:
        lines = f.readlines()
    
    clean_lines = []
    skip_block = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip problematic authentication blocks
        if any(phrase in line for phrase in [
            "if False:  # Authentication disabled",
            "user=None  # No authentication",
            "user_id=-1",
            "UserProfile.objects.get_or_create",
            "UserActivity.objects.create", 
            "UserAchievement.objects.filter",
            "get_or_create(user",
            "filter(user=None"
        ]):
            # Start skipping this block
            if line.strip().endswith(':'):
                skip_block = True
                indent_level = len(line) - len(line.lstrip())
                clean_lines.append(f"{' ' * indent_level}# Authentication block disabled\\n")
                continue
            else:
                # Single line to comment out
                clean_lines.append(f"    # {line.strip()}  # Authentication disabled\\n")
                continue
        
        # Check if we should stop skipping
        if skip_block:
            current_indent = len(line) - len(line.lstrip())
            if line.strip() and current_indent <= indent_level:
                skip_block = False
            else:
                continue  # Skip this line
        
        # Keep the line
        clean_lines.append(line)
    
    # Write clean views
    with open("studio/views.py", 'w') as f:
        f.writelines(clean_lines)
    
    print("✅ Created clean views.py")
    print("🎯 Complete authentication removal finished!")

if __name__ == '__main__':
    create_clean_views()
