import urllib.request
html = urllib.request.urlopen('https://nyk5473.github.io/CrackerHouse_Laundry_V2/sns_event.html').read().decode('utf-8')
idx = html.find('function handleStaffLogin')
print(html[idx:idx+400])
