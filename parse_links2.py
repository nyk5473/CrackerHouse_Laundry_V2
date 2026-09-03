import urllib.request
import re
html = urllib.request.urlopen('https://nyk5473.github.io/CrackerHouse_Laundry_V2/index.html').read().decode('utf-8')
links = re.findall(r'<a.*?href="(.*?)".*?>(.*?)</a>', html, flags=re.DOTALL)
for href, text in links:
    if 'staff' in href:
        print(f"Href: {href.strip()} Text: {text.strip()}")
