#!/usr/bin/env python
"""
Emergency Template Authentication Fix
Removes all user authentication dependencies from templates
"""
import os
import re
from pathlib import Path

def fix_template_authentication():
    """Fix all user authentication references in templates"""
    
    print("🔧 EMERGENCY TEMPLATE FIX: Removing user authentication from templates")
    
    # Find all HTML templates
    template_dir = Path("studio/templates")
    html_files = list(template_dir.rglob("*.html"))
    
    total_fixes = 0
    
    for html_file in html_files:
        print(f"🔍 Checking {html_file}")
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace user authentication blocks with comments
            # Replace {% if user.is_authenticated %} blocks
            content = re.sub(
                r'{%\s*if\s+user\.is_authenticated\s*%}.*?{%\s*endif\s*%}',
                '<!-- User authentication removed -->',
                content,
                flags=re.DOTALL
            )
            
            # Replace {% if user.is_authenticated %} ... {% else %} ... {% endif %} blocks
            content = re.sub(
                r'{%\s*if\s+user\.is_authenticated\s*%}.*?{%\s*else\s*%}(.*?){%\s*endif\s*%}',
                r'\\1',  # Keep only the else part
                content,
                flags=re.DOTALL
            )
            
            # Replace other user references
            content = re.sub(r'{{\s*user\.[^}]+\s*}}', '<!-- User info removed -->', content)
            content = re.sub(r'{%\s*if\s+user\s*%}.*?{%\s*endif\s*%}', '<!-- User check removed -->', content, flags=re.DOTALL)
            
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ Fixed authentication issues in {html_file.name}")
                total_fixes += 1
            else:
                print(f"  ➖ No authentication issues in {html_file.name}")
                
        except Exception as e:
            print(f"  ❌ Error processing {html_file}: {e}")
    
    print(f"🎯 Template authentication fix complete! Fixed {total_fixes} files")

if __name__ == '__main__':
    fix_template_authentication()
