html = open('index.html', encoding='utf-8').read()
idx = html.find('뒤로가기')
if idx != -1:
    print(html[idx-100:idx+100])
