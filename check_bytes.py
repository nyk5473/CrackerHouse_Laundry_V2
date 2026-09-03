with open('inventory.html', 'r', encoding='utf-8') as f:
    c = f.read()
idx = c.find('alert(\"✅')
if idx != -1:
    print(repr(c[idx:idx+100].encode('utf-8')))
