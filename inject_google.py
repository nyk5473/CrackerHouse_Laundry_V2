import os
import re

files = {
    'reservation.html': 'KRACKER_LAUNDRY_PreReservation_List.csv',
    'inventory.html': 'KRACKER_LAUNDRY_Order_Report.csv',
    'sns_event.html': 'KRACKER_LAUNDRY_Review_Report.csv'
}

google_url = "https://script.google.com/macros/s/AKfycbxD0OIJjPP85ZfRF7m7DibvFCexqm-fnpG25bP5OrsoDzVJ_0rQEwl9vPI6ycQ_Sc-X/exec"

google_code = """
      // Upload to Google Drive (Apps Script)
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onloadend = function() {
          const base64data = reader.result.split(',')[1];
          
          const payload = {
              filename: "__FILENAME__",
              fileContent: base64data
          };
          
          fetch('__URL__', {
              method: 'POST',
              body: JSON.stringify(payload),
              headers: { 'Content-Type': 'text/plain;charset=utf-8' }
          })
          .then(res => res.json())
          .then(data => {
              if (data.success) {
                  console.log("Uploaded successfully to Google Drive");
                  alert("✅ 구글 드라이브에 안전하게 백업되었습니다!\\n(구글 드라이브를 확인해 보세요)");
              } else {
                  console.error("Upload error:", data);
                  alert("업로드 실패: " + (data.error || "알 수 없는 오류"));
              }
          })
          .catch(err => {
              console.error("Network error during upload:", err);
          });
      };
"""

for filepath, filename in files.items():
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'// Upload to Cloudflare R2.*?// Ignore error gracefully if running locally\s*\}\);'
    
    injected = google_code.replace('__FILENAME__', filename).replace('__URL__', google_url)
    
    new_content, count = re.subn(pattern, injected.strip(), content, flags=re.DOTALL)
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
    else:
        print(f"Could not find Cloudflare block in {filepath}")
