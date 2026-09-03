with open('inventory.html', 'r', encoding='utf-8') as f:
    c = f.read()
idx = c.find('alert(\"✅')
print(repr(c[idx:idx+100]))
