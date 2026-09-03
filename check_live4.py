import urllib.request
try:
    html = urllib.request.urlopen('https://nyk5473.github.io/CrackerHouse_Laundry_V2/sns_event.html').read().decode('utf-8')
    idx = html.find('checkStaffState()')
    print(f"Found checkStaffState at: {idx}")
    print(repr(html[-200:]))
except Exception as e:
    print(f"Error: {e}")
