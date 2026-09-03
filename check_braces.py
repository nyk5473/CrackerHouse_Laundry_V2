import re
html = open('inventory.html', encoding='utf-8').read()
m = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if m:
    js = m.group(1)
    print("Total {:", js.count('{'))
    print("Total }:", js.count('}'))
    print("Total (:", js.count('('))
    print("Total ):", js.count(')'))
