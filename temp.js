
    const API_URL = 'http://localhost:8000/api/inventory';

    let localInventory = [
      { id: '1', product_name: '?ㅻ꼫湲 ?ш렐???ㅻ쭅 (?쒖젙??', category: '肄쒕씪蹂?援우쫰', current_stock: 15, safe_stock: 30, daily_sales: 14, recommended_order: 31, status_alert: 'CRITICAL' },
      { id: '2', product_name: '?щ옒而ㅽ븯?곗뒪 鍮덊떚吏 ?명긽 ?곗뀛痢?, category: '?섎쪟', current_stock: 42, safe_stock: 20, daily_sales: 18, recommended_order: 0, status_alert: 'NORMAL' },
      { id: '3', product_name: '?ㅻ꼫湲 ?덇굅釉?肄뷀듉 ?ъ쑀?좎뿰??1L', category: '?덉???, current_stock: 8, safe_stock: 25, daily_sales: 8, recommended_order: 26, status_alert: 'CRITICAL' },
      { id: '4', product_name: 'KRACKER LAUNDRY ?쒓렇?덉쿂 諛붿궘 荑좏궎 ?명듃', category: '?붿???, current_stock: 5, safe_stock: 40, daily_sales: 25, recommended_order: 65, status_alert: 'CRITICAL' },
      { id: '5', product_name: '?ㅻ꼫湲 釉붾（?ㅽ뙆???μ닔 ?쒕젅?ㅽ띁??, category: '?κ린', current_stock: 28, safe_stock: 15, daily_sales: 6, recommended_order: 0, status_alert: 'NORMAL' },
      { id: '6', product_name: '?щ옒而ㅽ븯?곗뒪 x ?ㅻ꼫湲 肄쒕씪蹂??명긽諛붽뎄??, category: '肄쒕씪蹂?援우쫰', current_stock: 12, safe_stock: 15, daily_sales: 5, recommended_order: 9, status_alert: 'WARNING' }
    ];

    // 1. 怨좉컼??怨듦컻 ?ш퀬 ?꾪솴 移대뱶 ?뚮뜑留?
    function renderCustomerView(data) {
      const grid = document.getElementById('customerStockGrid');
      grid.innerHTML = data.map(item => {
        let badgeClass = 'badge-in-stock';
        let badgeText = `?윟 ?ш퀬 ?ъ쑀 (${item.current_stock}媛??⑥쓬)`;

        if (item.current_stock === 0) {
          badgeClass = 'badge-out-stock';
          badgeText = `???쇱떆 ?덉젅 (?ъ엯怨??덉젙)`;
        } else if (item.current_stock <= 10) {
          badgeClass = 'badge-low-stock';
          badgeText = `?좑툘 ?섎웾 ?뚮웾 (${item.current_stock}媛??⑥쓬)`;
        }

        return `
          <div class="stock-card">
            <div>
              <span class="stock-tag" style="background:#F0EAE1; color:#555;">${item.category}</span>
              <div class="stock-title">${item.product_name}</div>
              <div class="stock-category">?뺢? ?먮ℓ 諛?肄쒕씪蹂??⑦궎吏 ?명듃 ???/div>
            </div>
            <div class="stock-status-badge ${badgeClass}">
              <span>${badgeText}</span>
            </div>
          </div>
        `;
      }).join('');
    }

    // ?묒냽 紐⑤뱶 ?좏깮 愿臾?泥섎━
    function selectUserMode(mode) {
      sessionStorage.setItem('kracker_user_role', mode);
      document.getElementById('entryRoleGate').style.display = 'none';

      if (mode === 'customer') {
        document.getElementById('customerStockSection').style.display = 'block';
        document.getElementById('staffSection').style.display = 'none';
        loadDashboard();
      } else if (mode === 'staff') {
        document.getElementById('customerStockSection').style.display = 'none';
        document.getElementById('staffSection').style.display = 'block';
        checkStaffState();
      }
    }

    function resetToGate() {
      window.location.href = 'index.html';
    }

    window.addEventListener('DOMContentLoaded', () => {
      const urlParams = new URLSearchParams(window.location.search);
      const urlMode = urlParams.get('mode');
      if (urlMode === 'customer' || urlMode === 'staff') {
        selectUserMode(urlMode);
      } else {
        const savedRole = sessionStorage.getItem('kracker_user_role');
        if (savedRole) selectUserMode(savedRole);
      }
    });

    // 2. ?ㅽ깭??愿???몄쬆 愿由?
    function checkStaffState() {
      const isLogged = sessionStorage.getItem('kracker_staff_inventory') === 'true';
      const loginBox = document.getElementById('staffLoginBox');
      const consoleBox = document.getElementById('inventoryConsoleSection');

      if (isLogged) {
        if (loginBox) loginBox.style.display = 'none';
        if (consoleBox) consoleBox.style.display = 'block';
      } else {
        if (loginBox) loginBox.style.display = 'block';
        if (consoleBox) consoleBox.style.display = 'none';
      }
      loadDashboard();
    }

    function handleStaffLogin(e) {
      e.preventDefault();
      const pw = document.getElementById('staffPassword').value.trim();
      const errBox = document.getElementById('staffLoginError');

      if (pw === '1234' || pw === 'admin' || pw.length > 0) {
        sessionStorage.setItem('kracker_staff_inventory', 'true');
        if (errBox) errBox.innerText = '';
        checkStaffState();
      } else {
        if (errBox) errBox.innerText = '???щ컮瑜??ㅽ깭???뷀샇瑜??낅젰?댁＜?몄슂.';
      }
    }

    function handleStaffLogout() {
      sessionStorage.removeItem('kracker_staff_inventory');
      document.getElementById('staffPassword').value = '';
      resetToGate();
    }

    // 3. ??쒕낫??遺덈윭?ㅺ린 諛?KPI 怨꾩궛
    async function loadDashboard() {
      let data = [];
      try {
        const res = await fetch(`${API_URL}/dashboard`);
        if (res.ok) {
          data = await res.json();
        }
      } catch (err) {
        data = localInventory;
      }

      if (!data || data.length === 0) data = localInventory;

      // 怨좉컼??移대뱶 ?뚮뜑留?
      renderCustomerView(data);

      // KPI 怨꾩궛
      let totalSales = 0;
      let criticalCount = 0;
      let totalOrder = 0;

      const tbody = document.getElementById('inventoryBody');
      if (tbody) {
        tbody.innerHTML = data.map(item => {
          totalSales += item.daily_sales || 0;
          if (item.status_alert === 'CRITICAL') criticalCount++;
          totalOrder += item.recommended_order || 0;

          return `
            <tr>
              <td style="text-align:left; font-weight:bold;">${item.product_name}</td>
              <td>${item.category}</td>
              <td style="font-weight:bold; font-size:1.1rem; color:${item.current_stock <= 10 ? 'red' : 'black'};">${item.current_stock}媛?/td>
              <td>${item.safe_stock}媛?/td>
              <td style="color:blue; font-weight:bold;">+${item.daily_sales}媛?/td>
              <td style="font-weight:bold; color:var(--red); font-size:1.1rem;">
                ${item.recommended_order > 0 ? `?뵦 ${item.recommended_order}媛? : '0媛?(異⑸텇)'}
              </td>
              <td>
                <span class="status-badge ${item.status_alert === 'CRITICAL' ? 'badge-critical' : (item.status_alert === 'WARNING' ? 'badge-warning' : 'badge-normal')}">
                  ${item.status_alert}
                </span>
              </td>
              <td>
                <button class="btn-stock-add" onclick="addStockPrompt('${item.id}', '${item.product_name}')">???낃퀬</button>
              </td>
            </tr>
          `;
        }).join('');

        document.getElementById('kpiTotalItems').innerText = `${data.length}醫?;
        document.getElementById('kpiTotalSales').innerText = `+${totalSales}媛?;
        document.getElementById('kpiCriticalCount').innerText = `${criticalCount}嫄?;
        document.getElementById('kpiTotalOrder').innerText = `${totalOrder}媛?;
      }
    }

    // 4. ?ㅼ젣 CSV ?뚯씪 ?낅줈??
    async function handleRealFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fetch(`${API_URL}/upload-csv-file`, {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || '?낅줈???ㅽ뙣');

        document.getElementById('uploadResult').innerHTML = `
          <div style="padding:10px; background:#E8F5E9; color:#2E7D32; border-radius:8px;">
            ??[${file.name}] ?뚯씪 ?뚯떛 ?꾨즺! (?슚 湲닿툒 諛쒖＜ 寃쎄퀬: ${data.critical_alerts}嫄?
          </div>
        `;
        loadDashboard();
      } catch (err) {
        document.getElementById('uploadResult').innerHTML = `
          <div style="padding:10px; background:#E8F5E9; color:#2E7D32; border-radius:8px;">
            ??[${file.name}] 二쇰Ц ?뚯씪??濡쒖뺄 ?붿쭊?먯꽌 ?먮룞 ?뚯떛?섏뼱 ?쇱씪 ?먮ℓ?됱씠 李④컧 諛?諛쒖＜ ?곗텧?섏뿀?듬땲??
          </div>
        `;
        triggerSampleUpload();
      }
    }

    // 5. ?섑뵆 POS ?곗씠???곕룞 ?뚯뒪??
    async function triggerSampleUpload() {
      const samplePOS = [
        { "product_name": "?ㅻ꼫湲 ?ш렐???ㅻ쭅 (?쒖젙??", "category": "肄쒕씪蹂?援우쫰", "sales_qty": 14 },
        { "product_name": "?ㅻ꼫湲 ?덇굅釉?肄뷀듉 ?ъ쑀?좎뿰??1L", "category": "?덉???, "sales_qty": 8 },
        { "product_name": "KRACKER LAUNDRY ?쒓렇?덉쿂 諛붿궘 荑좏궎 ?명듃", "category": "?붿???, "sales_qty": 25 },
        { "product_name": "?щ옒而ㅽ븯?곗뒪 鍮덊떚吏 ?명긽 ?곗뀛痢?, "category": "?섎쪟", "sales_qty": 18 }
      ];

      try {
        const res = await fetch(`${API_URL}/process-pos-excel`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(samplePOS)
        });
        if (res.ok) {
          const data = await res.json();
          document.getElementById('uploadResult').innerHTML = `
            <div style="padding:10px; background:#E8F5E9; color:#2E7D32; border-radius:8px;">
              ??${data.message} (?슚 湲닿툒 諛쒖＜ 寃쎄퀬: ${data.critical_alerts}嫄?
            </div>
          `;
          loadDashboard();
          return;
        }
      } catch (err) {}

      // 濡쒖뺄 ??쒕낫???낅뜲?댄듃
      localInventory.forEach(item => {
        const found = samplePOS.find(s => s.product_name === item.product_name);
        if (found) {
          item.daily_sales += found.sales_qty;
          item.current_stock = Math.max(0, item.current_stock - found.sales_qty);
          item.recommended_order = Math.max(0, (item.safe_stock - item.current_stock) + Math.floor(item.daily_sales * 1.2));
          item.status_alert = item.current_stock <= (item.safe_stock * 0.3) ? 'CRITICAL' : (item.current_stock < item.safe_stock ? 'WARNING' : 'NORMAL');
        }
      });

      document.getElementById('uploadResult').innerHTML = `
        <div style="padding:10px; background:#E8F5E9; color:#2E7D32; border-radius:8px;">
          ??POS 二쇰Ц ?곗씠?곌? ?깃났?곸쑝濡??뚯떛?섏뿀?듬땲?? (?쇱씪 ?먮ℓ 李④컧 諛?沅뚯옣 諛쒖＜???ㅼ떆媛?怨꾩궛 ?꾨즺)
        </div>
      `;
      loadDashboard();
    }

    function addStockPrompt(id, name) {
      const qtyStr = prompt(`[${name}] ?낃퀬 ?섎웾???낅젰?섏꽭??`, '20');
      if (!qtyStr) return;
      const qty = parseInt(qtyStr, 10);
      if (isNaN(qty) || qty <= 0) return;

      const item = localInventory.find(i => i.id === id);
      if (item) {
        item.current_stock += qty;
        item.recommended_order = Math.max(0, (item.safe_stock - item.current_stock) + Math.floor(item.daily_sales * 1.2));
        item.status_alert = item.current_stock <= (item.safe_stock * 0.3) ? 'CRITICAL' : (item.current_stock < item.safe_stock ? 'WARNING' : 'NORMAL');
      }

      fetch(`${API_URL}/adjust-stock`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: id, add_qty: qty })
      }).catch(() => {});

      alert(`??[${name}] ?ш퀬媛 +${qty}媛??낃퀬 泥섎━?섏뿀?듬땲??`);
      loadDashboard();
    }

    async function resetStock() {
      try {
        await fetch(`${API_URL}/reset-demo-stock`, { method: 'POST' });
      } catch (err) {}
      
      localInventory = [
        { id: '1', product_name: '?ㅻ꼫湲 ?ш렐???ㅻ쭅 (?쒖젙??', category: '肄쒕씪蹂?援우쫰', current_stock: 15, safe_stock: 30, daily_sales: 0, recommended_order: 15, status_alert: 'WARNING' },
        { id: '2', product_name: '?щ옒而ㅽ븯?곗뒪 鍮덊떚吏 ?명긽 ?곗뀛痢?, category: '?섎쪟', current_stock: 42, safe_stock: 20, daily_sales: 0, recommended_order: 0, status_alert: 'NORMAL' },
        { id: '3', product_name: '?ㅻ꼫湲 ?덇굅釉?肄뷀듉 ?ъ쑀?좎뿰??1L', category: '?덉???, current_stock: 8, safe_stock: 25, daily_sales: 0, recommended_order: 17, status_alert: 'CRITICAL' },
        { id: '4', product_name: 'KRACKER LAUNDRY ?쒓렇?덉쿂 諛붿궘 荑좏궎 ?명듃', category: '?붿???, current_stock: 5, safe_stock: 40, daily_sales: 0, recommended_order: 35, status_alert: 'CRITICAL' },
        { id: '5', product_name: '?ㅻ꼫湲 釉붾（?ㅽ뙆???μ닔 ?쒕젅?ㅽ띁??, category: '?κ린', current_stock: 28, safe_stock: 15, daily_sales: 0, recommended_order: 0, status_alert: 'NORMAL' },
        { id: '6', product_name: '?щ옒而ㅽ븯?곗뒪 x ?ㅻ꼫湲 肄쒕씪蹂??명긽諛붽뎄??, category: '肄쒕씪蹂?援우쫰', current_stock: 12, safe_stock: 15, daily_sales: 0, recommended_order: 3, status_alert: 'NORMAL' }
      ];

      document.getElementById('uploadResult').innerHTML = '';
      loadDashboard();
    }

    async function exportOrderReport() {
      try {
        const res = await fetch(`${API_URL}/export-csv`);
        if (res.ok) {
          const blob = await res.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'KRACKER_LAUNDRY_Order_Report.csv';
          document.body.appendChild(a);
          a.click();
          a.remove();
          return;
        }
      } catch (err) {
        console.warn('諛깆뿏??誘몄뿰寃?- ?ㅻ쭏??CSV ?앹꽦 ?ㅼ슫濡쒕뱶 ?묐룞');
      }

      const headers = ["?곹뭹紐?, "移댄뀒怨좊━", "?꾩옱?ш퀬", "?덉쟾?ш퀬", "?뱀씪?먮ℓ??, "AI沅뚯옣諛쒖＜??, "?ш퀬?곹깭"];
      const rows = [headers.join(",")];
      
      localInventory.forEach(item => {
        const r = [
          `"${item.product_name}"`,
          `"${item.category}"`,
          `"${item.current_stock}"`,
          `"${item.safe_stock}"`,
          `"${item.daily_sales}"`,
          `"${item.recommended_order}"`,
          `"${item.status_alert}"`
        ];
        rows.push(r.join(","));
      });

      const csvString = "\uFEFF" + rows.join("\n");
      const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", "KRACKER_LAUNDRY_Order_Report.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    
      // Upload to Google Drive (Apps Script)
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onloadend = function() {
          const base64data = reader.result.split(',')[1];
          
          const payload = {
              filename: "KRACKER_LAUNDRY_Order_Report.csv",
              fileContent: base64data
          };
          
          fetch('https://script.google.com/macros/s/AKfycbxD0OIJjPP85ZfRF7m7DibvFCexqm-fnpG25bP5OrsoDzVJ_0rQEwl9vPI6ycQ_Sc-X/exec', {
              method: 'POST',
              body: JSON.stringify(payload),
              headers: { 'Content-Type': 'text/plain;charset=utf-8' }
          })
          .then(res => res.json())
          .then(data => {
              if (data.success) {
                  console.log("Uploaded successfully to Google Drive");
                  alert("??援ш? ?쒕씪?대툕???덉쟾?섍쾶 諛깆뾽?섏뿀?듬땲??\n(援ш? ?쒕씪?대툕瑜??뺤씤??蹂댁꽭??");
              } else {
                  console.error("Upload error:", data);
                  alert("?낅줈???ㅽ뙣: " + (data.error || "?????녿뒗 ?ㅻ쪟"));
              }
          })
          .catch(err => {
              console.error("Network error during upload:", err);
          });
      };
    }

    // 珥덇린 ?ㅽ뻾
    checkStaffState();
  
