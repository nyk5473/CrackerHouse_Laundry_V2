import re
html = open('laundry.html', encoding='utf-8').read()
matches = re.findall(r'<a.*?href="index\.html".*?>(.*?)</a>', html, re.DOTALL)
print("laundry.html:", [m.strip() for m in matches])

html = open('promo.html', encoding='utf-8').read()
matches = re.findall(r'<a.*?href="index\.html".*?>(.*?)</a>', html, re.DOTALL)
print("promo.html:", [m.strip() for m in matches])

html = open('reservation.html', encoding='utf-8').read()
matches = re.findall(r'<a.*?href="index\.html".*?>(.*?)</a>', html, re.DOTALL)
print("reservation.html:", [m.strip() for m in matches])
