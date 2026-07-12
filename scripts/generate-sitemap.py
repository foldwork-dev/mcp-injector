#!/usr/bin/env python3
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone

def main():
    base_url = "https://foldwork.dev"
    website_dir = "website"
    sitemap_path = os.path.join(website_dir, "sitemap.xml")
    
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Priority defaults
    priorities = {
        "index.html": "1.0",
        "benchmarks.html": "0.9",
        "docs.html": "0.9",
    }
    
    # Exclude partials and internal things
    exclude_dirs = ["partials", "data", "api", "css"]
    exclude_files = ["404.html"]
    
    for root, dirs, files in os.walk(website_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".html") and file not in exclude_files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, website_dir)
                
                # Convert rel_path to URL path
                # Convert backslashes for Windows if any
                url_path = rel_path.replace("\\", "/")
                
                if url_path == "index.html":
                    url_path = ""
                else:
                    # e.g. "vs/repomix.html" -> "vs/repomix"
                    url_path = url_path.replace(".html", "")
                    
                full_url = f"{base_url}/{url_path}" if url_path else base_url
                
                url_elem = ET.SubElement(urlset, "url")
                loc = ET.SubElement(url_elem, "loc")
                loc.text = full_url
                
                lastmod = ET.SubElement(url_elem, "lastmod")
                # Using UTC ISO format
                lastmod.text = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                
                priority = priorities.get(rel_path, "0.5")
                pri_elem = ET.SubElement(url_elem, "priority")
                pri_elem.text = priority

    xml_str = ET.tostring(urlset, encoding='utf-8', method='xml')
    parsed_xml = minidom.parseString(xml_str)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")
    
    # Remove empty lines from pretty print
    pretty_xml = os.linesep.join([s for s in pretty_xml.splitlines() if s.strip()])
    
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
        
    print(f"Generated sitemap at {sitemap_path}")

if __name__ == '__main__':
    main()
