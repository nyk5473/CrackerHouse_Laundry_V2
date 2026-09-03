import os
html_files = [f for f in os.listdir('.') if f.endswith('.html')]
for filename in html_files:
    content = open(filename, 'r', encoding='utf-8').read()
    if 'MAIN HOME' in content:
        print(f"Found MAIN HOME in {filename}")
