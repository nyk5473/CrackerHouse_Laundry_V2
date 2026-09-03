import os
html_files = [f for f in os.listdir('최종') if f.endswith('.html')]
for filename in html_files:
    content = open(os.path.join('최종', filename), 'r', encoding='utf-8').read()
    if 'MAIN HOME' in content:
        print(f"Found MAIN HOME in 최종/{filename}")
