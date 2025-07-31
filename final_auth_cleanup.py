#!/usr/bin/env python
"""
Final Authentication Cleanup
Removes ALL remaining authentication references
"""
import os
import re
from pathlib import Path

def final_auth_cleanup():
    """Remove all remaining authentication references"""
    
    print("🧹 FINAL CLEANUP: Removing ALL authentication references")
    
    # Find all HTML templates
    template_dirs = [
        Path("studio/templates"),
        Path("templates") if Path("templates").exists() else None
    ]
    
    html_files = []
    for template_dir in template_dirs:
        if template_dir:
            html_files.extend(list(template_dir.rglob("*.html")))
    
    total_fixes = 0
    
    for html_file in html_files:
        print(f"🔍 Cleaning {html_file}")
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remove all account_ URL references
            content = re.sub(r'{% url [\'"]account_[^\'"]*[\'"] %}', '"#"', content)
            content = re.sub(r'{% url [\'"]socialaccount_[^\'"]*[\'"] %}', '"#"', content)
            
            # Remove socialaccount template tags and references
            content = re.sub(r'{% load socialaccount %}.*?(?={% endload %}|$)', '', content, flags=re.DOTALL)
            content = re.sub(r'{% get_providers.*?%}', '', content)
            content = re.sub(r'socialaccount_providers', 'none', content)
            content = re.sub(r'user\.socialaccount_set\.all', 'none', content)
            
            # Remove user authentication blocks more thoroughly
            content = re.sub(r'{% if user\.is_authenticated %}.*?{% endif %}', '<!-- User authentication removed -->', content, flags=re.DOTALL)
            content = re.sub(r'{% if user\.is_authenticated %}.*?{% else %}.*?{% endif %}', '<!-- User authentication removed -->', content, flags=re.DOTALL)
            content = re.sub(r'{% if user %}.*?{% endif %}', '<!-- User check removed -->', content, flags=re.DOTALL)
            
            # Remove user object references
            content = re.sub(r'{{ user\.[^}]* }}', '<!-- User info removed -->', content)
            content = re.sub(r'user\.', 'none.', content)
            
            # Replace auth-dependent links with placeholders
            content = content.replace('href="{% url \'account_login\' %}"', 'href="#" onclick="alert(\'Authentication disabled\')"')
            content = content.replace('href="{% url \'account_signup\' %}"', 'href="#" onclick="alert(\'Authentication disabled\')"')
            content = content.replace('href="{% url \'account_logout\' %}"', 'href="#" onclick="alert(\'Authentication disabled\')"')
            content = content.replace('href="{% url \'account_settings\' %}"', 'href="#" onclick="alert(\'Authentication disabled\')"')
            
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✅ Cleaned {html_file.name}")
                total_fixes += 1
            else:
                print(f"  ➖ No changes needed in {html_file.name}")
                
        except Exception as e:
            print(f"  ❌ Error processing {html_file}: {e}")
    
    print(f"🎯 Final cleanup complete! Cleaned {total_fixes} files")

if __name__ == '__main__':
    final_auth_cleanup()
