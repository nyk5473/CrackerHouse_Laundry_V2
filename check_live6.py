import urllib.request
try:
    html = urllib.request.urlopen('https://nyk5473.github.io/CrackerHouse_Laundry_V2/sns_event.html').read().decode('utf-8')
    idx1 = html.find('exportLaundryCsv')
    idx2 = html.find('DOMContentLoaded')
    idx3 = html.find('checkStaffState()')
    print(f"exportLaundryCsv at: {idx1}")
    print(f"DOMContentLoaded at: {idx2}")
    print(f"checkStaffState() at: {idx3}")
except Exception as e:
    print(f"Error: {e}")
