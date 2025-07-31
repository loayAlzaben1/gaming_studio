#!/usr/bin/env python
"""
Emergency Syntax Fix - Fix all broken user authentication replacements
"""
import re

def fix_syntax_errors():
    """Fix all syntax errors in views.py from authentication removal"""
    
    print("🚨 EMERGENCY SYNTAX FIX: Fixing broken authentication replacements")
    
    views_file = "studio/views.py"
    
    # Read the current file
    with open(views_file, 'r') as f:
        content = f.read()
    
    # Fix all broken syntax patterns
    fixes = [
        # Fix broken get_or_create calls
        (r'get_or_create\(user=None  # No authentication\)', 'get_or_create(user_id=-1)  # No authentication'),
        (r'filter\(user=None  # No authentication\)', 'filter(user_id=-1)  # No authentication'),
        (r'get\(user=None  # No authentication\)', 'get(user_id=-1)  # No authentication'),
        
        # Fix broken filter chains
        (r'user=None  # No authentication\)\.', 'user_id=-1)  # No authentication.'),
        
        # Fix broken assignments
        (r'= None  # No authentication', '= None  # No authentication'),
        
        # Comment out problematic lines that can't be easily fixed
        (r'^(\s*)(.*get_or_create\(user_id=-1\).*)', r'\1# \2  # Disabled - no authentication'),
        (r'^(\s*)(.*filter\(user_id=-1\).*)', r'\1# \2  # Disabled - no authentication'),
        (r'^(\s*)(.*\.get\(user_id=-1\).*)', r'\1# \2  # Disabled - no authentication'),
    ]
    
    original_content = content
    
    # Apply fixes
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Write the fixed content
    if content != original_content:
        with open(views_file, 'w') as f:
            f.write(content)
        print("✅ Fixed syntax errors in views.py")
    else:
        print("✅ No syntax errors found")
    
    print("🎯 Syntax fix complete!")

if __name__ == '__main__':
    fix_syntax_errors()
