import os
content = open('sns_event.html', 'r', encoding='utf-8').read()
idx = content.find('MAIN HOME')
if idx != -1:
    print(content[idx-100:idx+100])
else:
    print("Not found")
