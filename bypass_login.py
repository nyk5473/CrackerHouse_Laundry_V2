import os
import re

files = {
    'sns_event.html': 'kracker_staff_laundry',
    'inventory.html': 'kracker_staff_inventory',
    'reservation.html': 'kracker_staff_res',
    'waiting.html': 'kracker_staff_waiting'
}

for filepath, token in files.items():
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find else if (mode === 'staff') {
    # and insert sessionStorage.setItem(token, 'true');
    pattern = r'(else\s*if\s*\(\s*mode\s*===\s*\'staff\'\s*\)\s*\{)'
    replacement = r"\1\n          sessionStorage.setItem('" + token + r"', 'true');"
    
    new_content, count = re.subn(pattern, replacement, content)
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Bypassed login in {filepath}")
    else:
        print(f"Could not find injection point in {filepath}")
