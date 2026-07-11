#!/usr/bin/env python3
import os
import re

def main():
    # Read partials
    with open('website/partials/nav.html', 'r', encoding='utf-8') as f:
        nav_content = f.read().strip()
    
    with open('website/partials/footer.html', 'r', encoding='utf-8') as f:
        footer_content = f.read().strip()

    # Regex patterns to match the blocks (including the comments themselves)
    nav_pattern = re.compile(r'<!-- BEGIN NAV -->.*?<!-- END NAV -->', re.DOTALL)
    footer_pattern = re.compile(r'<!-- BEGIN FOOTER -->.*?<!-- END FOOTER -->', re.DOTALL)

    # Walk through all HTML files
    for root_dir, _, files in os.walk('website'):
        if 'partials' in root_dir:
            continue
            
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root_dir, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace nav and footer
                if nav_pattern.search(content):
                    content = nav_pattern.sub(nav_content, content)
                
                if footer_pattern.search(content):
                    content = footer_pattern.sub(footer_content, content)
                
                # Only write if changes were made
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Assembled partials in {filepath}")

if __name__ == '__main__':
    main()
