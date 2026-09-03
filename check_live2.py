import urllib.request
html = urllib.request.urlopen('https://nyk5473.github.io/CrackerHouse_Laundry_V2/inventory.html').read().decode('utf-8')
idx = html.find('Uploaded successfully')
print(repr(html[idx:idx+150]))
