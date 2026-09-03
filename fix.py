import os, glob
for fp in glob.glob('*.html'):
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    if '백업되었습니다!\n(구글' in c:
        c = c.replace('백업되었습니다!\n(구글', '백업되었습니다!\\n(구글')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'Fixed {fp}')
