import urllib.request
try:
    html = urllib.request.urlopen('https://nyk5473.github.io/CrackerHouse_Laundry_V2/sns_event.html').read().decode('utf-8')
    idx = html.find('DOMContentLoaded')
    print(f"Found DOMContentLoaded at: {idx}")
except Exception as e:
    print(f"Error: {e}")
