/**
 * Cracker House X Snuggle Collaboration Front-End Main Logic
 */

document.addEventListener("DOMContentLoaded", () => {

  

  // ── MOBILE MENU TOGGLE ──
  const navBurger = document.getElementById("navBurger");
  const navLinks = document.querySelector(".nav__links");

  if (navBurger) {
    navBurger.addEventListener("click", () => {
      navBurger.classList.toggle("active");
      // 간단 모바일 토글
      if (navLinks.style.display === "flex") {
        navLinks.style.display = "none";
      } else {
        navLinks.style.display = "flex";
        navLinks.style.flexDirection = "column";
        navLinks.style.position = "absolute";
        navLinks.style.top = "80px";
        navLinks.style.left = "0";
        navLinks.style.width = "100%";
        navLinks.style.backgroundColor = "rgba(250, 247, 240, 0.95)";
        navLinks.style.padding = "20px";
        navLinks.style.borderBottom = "1px solid rgba(18, 40, 76, 0.08)";
      }
    });
  }

  // ── PAGE DETECTOR & LOADERS ──
  const isIndexPage = document.getElementById("main-page") !== null;
  const isProductsPage = document.getElementById("productsGrid") !== null;
  const isGuestbookPage = document.getElementById("guestbookList") !== null;
  const isLaundryPage = document.getElementById("laundryLineRope") !== null;
  const isUploadPage = document.getElementById("uploadForm") !== null;
  const isReservationPage = document.getElementById("preReservationForm") !== null;
  const isKioskPage = document.getElementById("kioskRegisterForm") !== null;

  if (isIndexPage) loadIndexPage();
  if (isProductsPage) loadProductsPage();
  if (isGuestbookPage) loadGuestbookPage();
  if (isLaundryPage) loadLaundryPage();
  if (isUploadPage) initUploadPage();
  if (isReservationPage) initReservationPage();
  if (isKioskPage) initKioskPage();
});

// Helper: Format Date
function formatDate(dateStr) {
  const d = new Date(dateStr);
  return `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()}`;
}

// ── 1. INDEX PAGE LOAD ──
async function loadIndexPage() {
  loadProductsPage();
  const infoLocation = document.getElementById("infoLocation");
  const infoDate = document.getElementById("infoDate");
  const infoHours = document.getElementById("infoHours");
  const infoInsta = document.getElementById("infoInsta");
  const hashtagsDiv = document.getElementById("hashtags");
  const previewProducts = document.getElementById("previewProducts");
  const previewPins = document.getElementById("previewPins");
  const experienceZonesGrid = document.getElementById("experienceZonesGrid");

  // A. 팝업 기본 정보 연동
  const info = await ApiService.getPopupInfo();
  if (info) {
    if (infoLocation) infoLocation.textContent = info.location;
    if (infoDate) infoDate.textContent = `${formatDate(info.start_date)} - ${formatDate(info.end_date)}`;
    if (infoHours) infoHours.textContent = info.operating_hours;
    if (infoInsta) {
      infoInsta.textContent = info.instagram_url.split("/").pop() ? "@" + info.instagram_url.split("/").pop() : "인스타그램";
      infoInsta.href = info.instagram_url;
    }
    if (hashtagsDiv && info.hashtags) {
      hashtagsDiv.innerHTML = info.hashtags
        .split(",")
        .map(tag => `<span class="hashtag">${tag.trim()}</span>`)
        .join(" ");
    }
  }

  // B. 체험존 목록 연동
  const zones = await ApiService.getPopupZones();
  if (experienceZonesGrid && zones.length > 0) {
    experienceZonesGrid.innerHTML = zones.map(z => `
      <div class="zone-card">
        <div class="zone-card__img">${z.brand === "SNUGGLE" ? '🧸' : '👕'}</div>
        <div class="zone-card__content">
          <span class="zone-card__tag zone-card__tag--${z.brand === "SNUGGLE" ? 'snuggle' : 'cracker'}">
            ${z.brand === "SNUGGLE" ? 'Snuggle' : 'Cracker House'}
          </span>
          <h3>${z.name}</h3>
          <p>${z.description}</p>
        </div>
      </div>
    `).join("");
  }

  // C. 세탁소 굿즈 프리뷰 (상위 3개 노출)
  const prodRes = await ApiService.getProducts();
  if (previewProducts && prodRes.items) {
    const items = prodRes.items.slice(0, 3);
    if (items.length === 0) {
      previewProducts.innerHTML = "<p>등록된 상품이 없습니다.</p>";
    } else {
      previewProducts.innerHTML = items.map(p => `
        <div class="product-card">
          <div class="product-card__img">
            ${p.brand === "SNUGGLE" ? '🧺' : '👕'}
            <span class="product-card__brand">${p.brand === "SNUGGLE" ? 'SNUGGLE' : 'CRACKER'}</span>
          </div>
          <div class="product-card__info">
            <div>
              <span class="product-card__category">${p.category}</span>
              <h3>${p.name}</h3>
            </div>
            <p class="product-card__price">${p.price.toLocaleString()}원</p>
          </div>
        </div>
      `).join("");
    }
  }

  // D. 빨랫줄 사진 프리뷰
  const pinRes = await ApiService.getLaundryPins();
  if (previewPins && pinRes.items) {
    const items = pinRes.items.slice(0, 5); // 5개만
    if (items.length === 0) {
      previewPins.innerHTML = "<p style='color: #666; text-align: center; width: 100%;'>현장에서 올린 폴라로이드가 여기에 걸립니다!</p>";
    } else {
      previewPins.innerHTML = items.map((p, index) => {
        const left = 10 + index * 20; // 가로 정렬 분산
        const rotation = -15 + Math.random() * 30; // 약간 삐딱하게
        return `
          <div class="laundry-pin-item" style="left: ${left}%; --rotation: ${rotation}deg;">
            <img src="${p.image_url.startsWith('/images') ? '.' + p.image_url : 'http://localhost:8000' + p.image_url}" alt="폴라로이드" />
            <p>${p.nickname}</p>
          </div>
        `;
      }).join("");
    }
  }
}

// ── 2. PRODUCTS PAGE LOAD ──
async function loadProductsPage() {
  const productsGrid = document.getElementById("productsGrid");
  const tabBtns = document.querySelectorAll(".tab-btn");

  const renderProducts = async (brand = null) => {
    const res = await ApiService.getProducts(brand);
    const items = (res && res.items && res.items.length > 0) ? res.items : null;
    
    if (!items) {
      // DOM Fallback filtering
      const cards = productsGrid.querySelectorAll(".product-card");
      cards.forEach(card => {
        const cardBrand = (card.getAttribute("data-brand") || "").toUpperCase();
        if (!brand || brand === "all") {
          card.style.display = "flex";
        } else if (brand.toUpperCase().includes("KRACKER") || brand.toUpperCase().includes("CRACKER")) {
          if (cardBrand.includes("KRACKER") || cardBrand.includes("CRACKER")) {
            card.style.display = "flex";
          } else {
            card.style.display = "none";
          }
        } else if (brand.toUpperCase().includes("SNUGGLE")) {
          if (cardBrand.includes("SNUGGLE")) {
            card.style.display = "flex";
          } else {
            card.style.display = "none";
          }
        }
      });
      return;
    }

    productsGrid.innerHTML = items.map(p => {
      const hasRealImage = p.image_url && !p.image_url.includes("placeholder");
      const imgPath = p.image_url.startsWith('/') ? '.' + p.image_url : (p.image_url.startsWith('images/') ? p.image_url : 'images/' + p.image_url.split('/').pop());
      
      const imgContent = hasRealImage 
        ? `<img src="${imgPath}" alt="${p.name}" style="width: 100%; height: 100%; object-fit: cover; display: block;" onerror="this.src='images/${p.image_url.split('/').pop()}'; this.onerror=null;" />`
        : `<div style="font-size:40px; display:flex; align-items:center; justify-content:center; width:100%; height:100%; background:var(--card);">${p.brand.includes("SNUGGLE") ? '🧸' : '👕'}</div>`;

      const isKracker = p.brand.includes("KRACKER") || p.brand.includes("CRACKER");

      return `
        <div class="product-card" data-brand="${p.brand}" style="flex: 0 0 260px; width: 260px; background: var(--dark2); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; transition: var(--tr);">
          <div class="product-card__img" style="aspect-ratio: 4/3; overflow: hidden; position: relative;">
            ${imgContent}
            <span class="product-card__brand" style="position: absolute; top: 12px; left: 12px; font-family: var(--ff-mono); font-size: 9px; font-weight: 700; background: rgba(0,0,0,0.6); padding: 3px 7px; border-radius: 2px; color: var(--orange);">${isKracker ? '크래커' : '스너글'}</span>
          </div>
          <div class="product-card__info" style="padding: 20px; display: flex; flex-direction: column; justify-content: space-between; flex-grow: 1;">
            <div>
              <span class="product-card__category" style="font-family: var(--ff-mono); font-size: 10px; color: var(--clay); text-transform: uppercase;">${p.category}</span>
              <h3 style="font-size: 16px; font-weight: 700; color: var(--white); margin: 6px 0;">${p.name}</h3>
              <p style="font-size: 12px; color: var(--muted); margin-bottom: 12px;">${p.description || ''}</p>
            </div>
            <div>
              <p class="product-card__price" style="font-size: 16px; font-weight: 700; color: var(--orange);">${p.price.toLocaleString()}원</p>
            </div>
          </div>
        </div>
      `;
    }).join("");
  };

  // 초기 전체 로딩
  renderProducts();

  // 탭 클릭 이벤트
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.dataset.filter;
      
      // 즉시 DOM 필터링
      const cards = productsGrid.querySelectorAll(".product-card");
      if (cards.length > 0) {
        cards.forEach(card => {
          const cardBrand = (card.getAttribute("data-brand") || "").toUpperCase();
          if (filter === "all") {
            card.style.display = "flex";
          } else if (filter.includes("KRACKER") || filter.includes("CRACKER")) {
            if (cardBrand.includes("KRACKER") || cardBrand.includes("CRACKER")) {
              card.style.display = "flex";
            } else {
              card.style.display = "none";
            }
          } else if (filter.includes("SNUGGLE")) {
            if (cardBrand.includes("SNUGGLE")) {
              card.style.display = "flex";
            } else {
              card.style.display = "none";
            }
          }
        });
      } else {
        renderProducts(filter === "all" ? null : filter);
      }
    });
  });
}

      alert("업로드 실패: " + res.message);
    }
  });
}

// ── 6. RESERVATION PAGE INIT ──
function initReservationPage() {
  const form = document.getElementById("preReservationForm");
  const checkForm = document.getElementById("checkReservationForm");
  const checkResult = document.getElementById("checkResult");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("resName").value.trim();
      const phone = document.getElementById("resPhone").value.trim();
      const email = document.getElementById("resEmail").value.trim();
      const date = document.getElementById("resDate").value;
      const time = document.getElementById("resTime").value;
      const people = document.getElementById("resPeople").value;

      if (!name || !phone || !date || !time) {
        alert("필수 항목을 모두 입력해주세요!");
        return;
      }

      const res = await ApiService.createPreReservation(name, phone, email, date, time, people);
      if (res.success) {
        alert(`🎉 사전예약이 접수되었습니다!\n성함: ${res.data.name}\n예약일시: ${date} ${time}\n인원: ${people}명`);
        form.reset();
      } else {
        alert("예약 실패: " + res.message);
      }
    });
  }

  if (checkForm) {
    checkForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const phone = document.getElementById("checkPhone").value.trim();
      if (!phone) return;

      const res = await ApiService.getMyPreReservations(phone);
      if (res.total === 0) {
        checkResult.innerHTML = `<p style="color:#e63946; font-weight:600; text-align:center;">등록된 사전예약 내역이 없습니다.</p>`;
      } else {
        checkResult.innerHTML = res.items.map(item => `
          <div class="concept-card" style="border: 2px solid var(--color-primary); margin-top: 16px;">
            <h3>사전예약 내역</h3>
            <p style="margin-top: 10px;"><strong>예약 번호:</strong> ${item.id.slice(0,8)}</p>
            <p><strong>성함:</strong> ${item.name}</p>
            <p><strong>예약 일자:</strong> ${formatDate(item.reservation_date)}</p>
            <p><strong>예약 시간:</strong> ${item.reservation_time}</p>
            <p><strong>인원수:</strong> ${item.people_count}명</p>
            <p><strong>상태:</strong> 
              <span class="badge ${item.status === 'WAITING' ? 'badge--waiting' : item.status === 'COMPLETED' ? 'badge--completed' : 'badge--cancelled'}">
                ${item.status === 'WAITING' ? '예약 확정 (대기)' : item.status === 'COMPLETED' ? '입장 완료' : '예약 취소'}
              </span>
            </p>
          </div>
        `).join("");
      }
    });
  }
}

// ── 7. KIOSK PAGE INIT ──
function initKioskPage() {
  const registerForm = document.getElementById("kioskRegisterForm");
  const queryForm = document.getElementById("kioskQueryForm");
  const kioskMain = document.getElementById("kioskMain");
  const kioskRegisterScreen = document.getElementById("kioskRegisterScreen");
  const kioskQueryScreen = document.getElementById("kioskQueryScreen");
  const kioskSuccessScreen = document.getElementById("kioskSuccessScreen");
  const kioskQueryResultScreen = document.getElementById("kioskQueryResultScreen");

  // 네비게이션 트리거
  window.showScreen = (screenId) => {
    const screens = [kioskMain, kioskRegisterScreen, kioskQueryScreen, kioskSuccessScreen, kioskQueryResultScreen];
    screens.forEach(s => { if(s) s.style.display = "none"; });
    const target = document.getElementById(screenId);
    if (target) target.style.display = "block";
  };

  // 등록 제출
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("kioskName").value.trim();
      const phone = document.getElementById("kioskPhone").value.trim();
      const people = document.getElementById("kioskPeople").value;

      if (!name || !phone) {
        alert("이름과 휴대폰 번호를 입력해주세요.");
        return;
      }

      const res = await ApiService.createOnsiteReservation(name, phone, people);
      if (res.success) {
        document.getElementById("issuedNumber").textContent = res.data.waiting_number;
        document.getElementById("issuedName").textContent = res.data.name;
        showScreen("kioskSuccessScreen");
        registerForm.reset();
      } else {
        alert(res.message);
      }
    });
  }

  // 조회 제출
  if (queryForm) {
    queryForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const phone = document.getElementById("kioskQueryPhone").value.trim();
      if (!phone) return;

      const res = await ApiService.getWaitingStatus(phone);
      if (res.success) {
        document.getElementById("queryNumber").textContent = res.data.waiting_number;
        document.getElementById("queryName").textContent = res.data.name;
        document.getElementById("queryAhead").textContent = res.data.people_ahead;
        showScreen("kioskQueryResultScreen");
        queryForm.reset();
      } else {
        alert(res.message);
      }
    });
  }
}
