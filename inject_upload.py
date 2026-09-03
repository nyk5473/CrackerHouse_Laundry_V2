import os
import re

files = {
    'inventory.html': ('exportOrderReport', 'KRACKER_LAUNDRY_Order_Report.csv'),
    'reservation.html': ('exportResCsv', 'KRACKER_LAUNDRY_PreReservation_List.csv'),
    'sns_event.html': ('exportLaundryCsv', 'KRACKER_LAUNDRY_Review_Report.csv')
}

upload_code = """
      // Upload to Cloudflare R2
      const formData = new FormData();
      formData.append('file', blob, "__FILENAME__");
      formData.append('filename', "__FILENAME__");
      
      fetch('/api/upload-csv', { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log("Uploaded successfully to Cloudflare R2", data.key);
                alert("Cloudflare R2에 성공적으로 백업(업로드) 되었습니다!\\n(파일명: " + data.key + ")");
            } else {
                console.error("Upload error:", data);
                alert("업로드 실패: " + (data.error || "알 수 없는 오류"));
            }
        })
        .catch(err => {
            console.error("Network error during upload:", err);
            // Ignore error gracefully if running locally
        });
"""

for filepath, (func_name, filename) in files.items():
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'(document\.body\.removeChild\([^)]+\);\s*)(\})'
    
    match = re.search(pattern, content)
    if match:
        injected = upload_code.replace('__FILENAME__', filename)
        new_content = content[:match.start(2)] + injected + "    " + match.group(2) + content[match.end(2):]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
    else:
        print(f"Could not find injection point for {filepath}")
