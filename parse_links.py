import urllib.request
from bs4 import BeautifulSoup
html = urllib.request.urlopen('https://nyk5473.github.io/CrackerHouse_Laundry_V2/index.html').read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
links = soup.find_all('a')
for l in links:
    if l.get('href') and 'staff' in l.get('href'):
        print(f"Text: {l.text.strip()}, Href: {l.get('href')}")
