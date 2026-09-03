import urllib.request
html = urllib.request.urlopen('https://nyk5473.github.io/CrackerHouse_Laundry_V2/index.html').read().decode('utf-8')
idx = html.find('sns_event.html?mode=staff')
print(repr(html[idx-100:idx+100]))
