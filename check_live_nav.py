import urllib.request
html = urllib.request.urlopen('https://nyk5473.github.io/CrackerHouse_Laundry_V2/sns_event.html').read().decode('utf-8')
idx = html.find('뒤로가기')
if idx != -1:
    print(html[idx-100:idx+100])
else:
    print('Not found in live site')
