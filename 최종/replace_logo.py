import os
import glob
import re

html_files = glob.glob("*.html")
replacement = '<img src="kracker_logo_new.png" alt="KRACKER LAUNDRY" style="height:36px; object-fit:contain;">'

for file in html_files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "kracker_laundry_logo_v2.png" in content:
        new_content = re.sub(r'<img src="images/kracker_laundry_logo_v2\.png"[^>]*>', replacement, content)
        with open(file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {file}")
