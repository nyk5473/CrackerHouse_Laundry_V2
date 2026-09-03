import os
import re
content = open('sns_event.html', 'r', encoding='utf-8').read()
matches = re.findall(r'<a.*?href="index\.html".*?</a>', content, flags=re.DOTALL)
for i, m in enumerate(matches):
    print(f"Match {i}: {m.strip()}")
