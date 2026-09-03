html = open('sns_event.html', encoding='utf-8').read()
print(f"Total length: {len(html)}")
print(repr(html[-200:]))
