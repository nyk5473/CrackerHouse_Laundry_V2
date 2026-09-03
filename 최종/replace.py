import os
import glob

directory = 'crackerhouse-frontend'
files = glob.glob(os.path.join(directory, '*.html')) + glob.glob(os.path.join(directory, 'js', '*.js'))

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace old index.html to promo.html
    content = content.replace('index.html', 'promo.html')
    # Replace gate.html to index.html (the new main page)
    content = content.replace('gate.html', 'index.html')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
print('Done!')
