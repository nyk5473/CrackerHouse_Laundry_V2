import urllib.request
try:
    html = urllib.request.urlopen('https://nyk5473.github.io/CrackerHouse_Laundry_V2/sns_event.html').read().decode('utf-8')
    print(f"Total length: {len(html)}")
except Exception as e:
    print(f"Error: {e}")
