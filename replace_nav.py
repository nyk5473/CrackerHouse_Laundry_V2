import re
import os

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

for filename in html_files:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Search for <a href="index.html" ...> // MAIN HOME </a>
    pattern = r'(<a[^>]*href=")(index\.html)("[^>]*>\s*)//\s*MAIN\s*HOME(\s*</a>)'
    replacement = r'\1#\3&#8592; 뒤로가기\4'
    
    # But wait, we need to add onclick="event.preventDefault(); history.back();" to the <a> tag.
    # It's safer to just replace the whole thing or modify the href and add onclick.
    
    def replacer(match):
        a_tag = match.group(0)
        # replace href="index.html" with href="#" onclick="event.preventDefault(); history.back();"
        a_tag = a_tag.replace('href="index.html"', 'href="#" onclick="event.preventDefault(); history.back();"')
        # replace // MAIN HOME with &#8592; 뒤로가기
        a_tag = re.sub(r'//\s*MAIN\s*HOME', '&#8592; 뒤로가기', a_tag)
        return a_tag
        
    new_content, count = re.subn(pattern, replacer, content)
    
    if count > 0:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {count} nav links in {filename}")

