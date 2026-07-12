#!/usr/bin/env python3
import os
import re
import json
import sys

failed = False
def fail(msg):
    global failed
    print(f"SEO LINT ERROR: {msg}")
    failed = True

def strip_tags(text):
    return re.sub(r'<[^>]+>', '', text).strip()

def check_html_file(filepath, content, seo_config):
    # Determine target keywords for this file
    # Ensure forward slashes for matching keys
    rel_path = filepath.replace('\\', '/')
    page_override = seo_config.get("page_overrides", {}).get(rel_path, {})
    target_keywords = page_override.get("target_keywords", seo_config.get("global_keywords", []))
    target_keywords_lower = [kw.lower() for kw in target_keywords]

    # 1 & 6. Title length and keyword
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    if not title_match:
        fail(f"{filepath}: Missing <title> tag.")
        title_text = ""
    else:
        title_text = title_match.group(1).strip()
        t_len = len(title_text)
        if t_len < 25 or t_len > 65:
            fail(f"{filepath}: <title> length {t_len} is outside 25-65 chars range.")
        
        has_kw = any(kw in title_text.lower() for kw in target_keywords_lower)
        if not has_kw and target_keywords_lower:
            fail(f"{filepath}: <title> missing target keyword (targets: {target_keywords}).")

    # 2 & 6. Meta Description length and keyword
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE | re.DOTALL)
    if not desc_match:
        fail(f"{filepath}: Missing <meta name=\"description\"> tag.")
    else:
        desc_text = desc_match.group(1).strip()
        d_len = len(desc_text)
        if d_len < 60 or d_len > 160:
            fail(f"{filepath}: Meta description length {d_len} is outside 60-160 chars range.")
        
        has_kw = any(kw in desc_text.lower() for kw in target_keywords_lower)
        if not has_kw and target_keywords_lower:
            fail(f"{filepath}: Meta description missing target keyword.")

    # 3. Headings (Exactly one h1, no skipping, different from title, keyword in h1)
    # Find all h tags
    h_tags = re.findall(r'<(h[1-6])[^>]*>(.*?)</\1>', content, re.IGNORECASE | re.DOTALL)
    
    h1_count = 0
    h1_text = ""
    current_level = 0
    
    for tag_name, tag_inner in h_tags:
        level = int(tag_name[1])
        
        if level == 1:
            h1_count += 1
            h1_text = strip_tags(tag_inner)
        
        if current_level == 0:
            if level != 1:
                fail(f"{filepath}: First heading is {tag_name}, expected h1.")
        else:
            if level > current_level + 1:
                fail(f"{filepath}: Skipped heading level from h{current_level} to h{level}.")
        
        current_level = level

    if h1_count != 1:
        fail(f"{filepath}: Found {h1_count} <h1> tags, expected exactly 1.")
    else:
        if h1_text.lower() == title_text.lower():
            fail(f"{filepath}: <h1> text is exactly equal to <title>. They should differ.")
        
        has_kw = any(kw in h1_text.lower() for kw in target_keywords_lower)
        if not has_kw and target_keywords_lower:
            fail(f"{filepath}: <h1> missing target keyword.")

    # 4. Images (alt text length, non-generic, decorative exemptions)
    img_tags = re.finditer(r'<img\s+([^>]+)>', content, re.IGNORECASE)
    generic_words = ["image", "screenshot", "picture", "photo"]
    
    for match in img_tags:
        attrs = match.group(1)
        # Check exemption
        if 'role="presentation"' in attrs or "role='presentation'" in attrs or 'data-decorative="true"' in attrs or "data-decorative='true'" in attrs:
            continue
            
        alt_match = re.search(r'alt=["\'](.*?)["\']', attrs, re.IGNORECASE)
        if not alt_match:
            fail(f"{filepath}: <img> missing alt attribute (add role=\"presentation\" if decorative).")
            continue
            
        alt_text = alt_match.group(1).strip()
        words = alt_text.split()
        if len(words) <= 3 and len(words) > 0:
            fail(f"{filepath}: alt text '{alt_text}' is too short (<= 3 words).")
            
        if any(gw in alt_text.lower() for gw in generic_words):
            fail(f"{filepath}: alt text '{alt_text}' contains generic word.")

    # 5. Canonical Tags
    canon_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']', content, re.IGNORECASE)
    if not canon_match:
        fail(f"{filepath}: Missing <link rel=\"canonical\"> tag.")
    else:
        canon_href = canon_match.group(1).strip()
        # Verify it matches the sitemap format
        url_path = rel_path.replace("\\", "/")
        if url_path == "website/index.html":
            expected_href = "https://foldwork.dev"
        else:
            expected_href = "https://foldwork.dev/" + url_path.replace("website/", "").replace(".html", "")
            
        if canon_href != expected_href and canon_href != expected_href + "/":
            fail(f"{filepath}: Canonical tag '{canon_href}' does not match expected '{expected_href}'.")

def main():
    try:
        with open('website/data/seo_config.json', 'r') as f:
            seo_config = json.load(f)
    except Exception as e:
        print(f"Error loading seo_config.json: {e}")
        sys.exit(1)

    exclude_dirs = ["partials", "data", "api", "css"]
    exclude_files = ["404.html"]

    for root, dirs, files in os.walk('website'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".html") and file not in exclude_files:
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                check_html_file(filepath, content, seo_config)

    if failed:
        sys.exit(1)
    else:
        print("SEO Lint passed.")

if __name__ == "__main__":
    main()
