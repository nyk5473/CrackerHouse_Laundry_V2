import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

for filename in html_files:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # We want to replace console.error("Network error during upload:", err);
    # with alert("구글 드라이브 업로드 권한 오류가 발생했습니다. (401 Unauthorized 등)\n앱스 스크립트 배포 설정을 확인해주세요."); console.error(...);
    
    pattern = r'console\.error\("Network error during upload:", err\);'
    replacement = r'console.error("Network error during upload:", err);\n              alert("구글 드라이브 업로드에 실패했습니다. (권한 또는 네트워크 오류)\\n앱스 스크립트 배포 시 [접근 권한: 모든 사람]으로 설정되었는지 확인해 주세요.");'
    
    new_content, count = re.subn(pattern, replacement, content)
    
    if count > 0:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated catch block in {filename}")

