import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

for filename in html_files:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Change window.location.href = 'index.html'; inside resetToGate()
    # to window.history.back();
    pattern = r'(function\s+resetToGate\(\)\s*\{\s*)window\.location\.href\s*=\s*\'index\.html\';'
    replacement = r'\1window.history.back();'
    new_content, count = re.subn(pattern, replacement, content)

    # 2. Change the button texts that call resetToGate() to &#8592; 뒤로가기
    # specifically matching CHANGE MODE and 모드 다시 선택 화면으로 돌아가기
    new_content = re.sub(r'&#8634;\s*CHANGE\s*MODE', '&#8592; 뒤로가기', new_content)
    new_content = re.sub(r'&#8592;\s*모드\s*다시\s*선택\s*화면으로\s*돌아가기', '&#8592; 뒤로가기', new_content)
    
    if content != new_content:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filename}")

