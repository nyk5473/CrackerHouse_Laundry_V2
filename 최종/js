/**
 * Cracker House X Snuggle Collaboration API Communication Module
 */
const API_BASE = "http://localhost:8000/api";

const ApiService = {
  // ── ☕ 팝업 및 체험존 정보 ──
  async getPopupInfo() {
    try {
      const response = await fetch(`${API_BASE}/popup`);
      if (!response.ok) throw new Error("팝업 정보를 불러오지 못했습니다.");
      return await response.json();
    } catch (error) {
      console.error(error);
      return null;
    }
  },

  async getPopupZones() {
    try {
      const response = await fetch(`${API_BASE}/popup/zones`);
      if (!response.ok) throw new Error("체험존 정보를 불러오지 못했습니다.");
      return await response.json();
    } catch (error) {
      console.error(error);
      return [];
    }
  },

  // ── 👕 상품 정보 ──
  async getProducts(brand = null, category = null) {
    const allProducts = [
      { id: 1, name: "크래커하우스 빈티지 피그먼트 티셔츠", description: "부드러운 워싱이 돋보이는 오버핏 피그먼트 반팔 티셔츠", price: 45000, brand: "KRACKER_HOUSE", category: "Apparel", stock: 100, image_url: "images/mock_product_2.png" },
      { id: 2, name: "크래커하우스 백로고 티셔츠", description: "뒷면 그래픽 로고 포인트 시그니처 옐로우 티셔츠", price: 42000, brand: "KRACKER_HOUSE", category: "Apparel", stock: 50, image_url: "images/mock_product_1.png" },
      { id: 3, name: "크래커하우스 헤비웨이트 피그먼트 후디", description: "도톰한 탄력감과 투박한 워크웨어 라인의 후드 집업", price: 89000, brand: "KRACKER_HOUSE", category: "Apparel", stock: 65, image_url: "images/kracker_basic_t_shirts_red.jpg" },
      { id: 4, name: "크래커하우스 워크웨어 데님 카펜터 팬츠", description: "견고한 스티치 디테일의 빈티지 스트레이트 데님", price: 98000, brand: "KRACKER_HOUSE", category: "Apparel", stock: 40, image_url: "images/kracker_basic_t_shirts_yellow.jpg" },
      { id: 5, name: "크래커하우스 x 스너글 콜라보 에코백", description: "두 브랜드 감성이 담긴 리미티드 캔버스 백", price: 29000, brand: "KRACKER_HOUSE", category: "Accessories", stock: 200, image_url: "images/collab_collection.jpg" },
      { id: 6, name: "스너글 빈티지 바닐라 섬유유연제", description: "갓 세탁한 맑은 향과 포근한 가을 바닐라 잔향의 조화", price: 16500, brand: "SNUGGLE", category: "Care", stock: 500, image_url: "images/vintage_vanilla.jpg" },
      { id: 7, name: "스너글 블루 스파클 룸스프레이", description: "공간을 깨끗하고 시원하게 채워주는 섬유 향수", price: 18000, brand: "SNUGGLE", category: "Care", stock: 150, image_url: "images/collab_collection.jpg" },
      { id: 8, name: "스너글 베어 한정판 인형", description: "콜라보레이션 기념 한정판 포근한 스너글 베어 굿즈", price: 22000, brand: "SNUGGLE", category: "Goods", stock: 30, image_url: "images/collab_collection.jpg" }
    ];

    const getFilteredMock = () => {
      let filtered = allProducts;
      if (brand) {
        const b = brand.toUpperCase();
        if (b.includes("KRACKER") || b.includes("CRACKER")) {
          filtered = filtered.filter(p => p.brand.includes("KRACKER") || p.brand.includes("CRACKER"));
        } else if (b.includes("SNUGGLE")) {
          filtered = filtered.filter(p => p.brand.includes("SNUGGLE"));
        }
      }
      return { total: filtered.length, items: filtered };
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 800);
      let url = `${API_BASE}/products?`;
      if (brand) url += `brand=${brand}&`;
      if (category) url += `category=${category}&`;
      
      const response = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (!response.ok) return getFilteredMock();
      const data = await response.json();
      if (!data || !data.items || data.items.length === 0) return getFilteredMock();
      return data;
    } catch (error) {
      return getFilteredMock();
    }
  },

  async getProductDetail(id) {
    try {
      const response = await fetch(`${API_BASE}/products/${id}`);
      if (!response.ok) throw new Error("상품 상세 정보를 불러오지 못했습니다.");
      return await response.json();
    } catch (error) {
      console.error(error);
      return null;
    }
  },

  // ── 📅 예약 및 현장 대기 ──
  async createPreReservation(name, phone, email, reservationDate, reservationTime, peopleCount) {
    try {
      const response = await fetch(`${API_BASE}/reservations/pre`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          phone,
          email: email || null,
          reservation_date: reservationDate,
          reservation_time: reservationTime,
          people_count: parseInt(peopleCount)
        })
      });
      const data = await response.json();
      if (!response.ok) {
        return { success: false, message: data.detail || "예약에 실패했습니다." };
      }
      return { success: true, data };
    } catch (error) {
      console.error(error);
      return { success: false, message: "서버와의 통신 오류가 발생했습니다." };
    }
  },

  async createOnsiteReservation(name, phone, peopleCount) {
    try {
      const response = await fetch(`${API_BASE}/reservations/onsite`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, people_count: parseInt(peopleCount) })
      });
      const data = await response.json();
      if (!response.ok) {
        return { success: false, message: data.detail || "대기 등록에 실패했습니다." };
      }
      return { success: true, data };
    } catch (error) {
      console.warn("Backend failed, using mock kiosk data.");
      window.mockKioskData = window.mockKioskData || [];
      const newReservation = {
        name: name,
        phone: phone,
        people_count: parseInt(peopleCount),
        waiting_number: 100 + window.mockKioskData.length + 1,
        ahead_count: window.mockKioskData.length
      };
      window.mockKioskData.push(newReservation);
      return { success: true, data: newReservation };
    }
  },

  async getWaitingStatus(phone) {
    try {
      const response = await fetch(`${API_BASE}/reservations/waiting-status/${phone}`);
      const data = await response.json();
      if (!response.ok) {
        return { success: false, message: data.detail || "대기 조회를 할 수 없습니다." };
      }
      return { success: true, data };
    } catch (error) {
      console.warn("Backend failed, using mock kiosk data.");
      window.mockKioskData = window.mockKioskData || [];
      const found = window.mockKioskData.find(r => r.phone === phone);
      if (found) {
        return { success: true, data: found };
      }
      return { success: false, message: "등록된 예약 정보가 없습니다." };
    }
  },

  // ── 🧺 빨랫줄 (폴라로이드) ──
  async getLaundryPins() {
    try {
      const response = await fetch(`${API_BASE}/laundry-line`);
      if (response.ok) {
        const data = await response.json();
        if (data && data.items && data.items.length > 0) return data;
      }
    } catch (error) {
      console.warn("서버 통신 실패. 프론트엔드 임시 DB를 사용합니다.");
    }

    let localPins = [];
    try {
      const stored = localStorage.getItem('kracker_local_pins');
      if (stored) localPins = JSON.parse(stored);
    } catch (e) {}

    if (!localPins || localPins.length === 0) {
      localPins = [
        { id: "pin-1", nickname: "포근포근곰", message: "스너글 블루스파클 향 너무 좋아용! 세탁기 포토존 대박 🧺🧸", pin_type: "PHOTO", image_url: "images/snuggle_photo_sample.jpg" },
        { id: "pin-2", nickname: "크래커덕후", message: "바삭 쿠키 세트랑 섬유유연제 샘플 굿즈까지 대만족!! 🍪", pin_type: "PHOTO", image_url: "images/mock_laundry_1.jpg" },
        { id: "pin-3", nickname: "스타필드나들이", message: "빨랫줄에 내 사진 집게로 다니까 인스타 갬성 느껴져요 ✨", pin_type: "PHOTO", image_url: "images/mock_laundry_2.jpg" }
      ];
      localStorage.setItem('kracker_local_pins', JSON.stringify(localPins));
    }

    return { total: localPins.length, items: localPins };
  },

  async createLaundryPin(nickname, message, pinType, imageFile) {
    const fileToBase64 = (file) => {
      return new Promise((resolve) => {
        if (!file || typeof file === "string") {
          resolve(file || "images/snuggle_photo_sample.jpg");
          return;
        }
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = () => resolve("images/snuggle_photo_sample.jpg");
        reader.readAsDataURL(file);
      });
    };

    try {
      const formData = new FormData();
      formData.append("nickname", nickname);
      if (message) formData.append("message", message);
      formData.append("pin_type", pinType);
      if (imageFile && typeof imageFile !== "string") {
        formData.append("image", imageFile);
      }

      const response = await fetch(`${API_BASE}/laundry-line`, {
        method: "POST",
        body: formData
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "업로드 실패");
      }
      return { success: true, message: data.message };
    } catch (error) {
      console.warn("서버 통신 실패. 로컬 DB에 영구 저장합니다.");
      let localPins = [];
      try {
        const stored = localStorage.getItem('kracker_local_pins');
        if (stored) localPins = JSON.parse(stored);
      } catch (e) {}

      const base64Img = await fileToBase64(imageFile);

      const newPin = {
        id: `pin-${Date.now()}`,
        nickname: nickname || "익명",
        message: message || "",
        pin_type: pinType || "PHOTO",
        image_url: base64Img,
        is_approved: true,
        created_at: new Date().toLocaleString()
      };
      localPins.unshift(newPin);
      localStorage.setItem('kracker_local_pins', JSON.stringify(localPins));

      return { success: true, message: "성공적으로 등록되었습니다!" };
    }
  },

  // ── 🔐 관리자 기능 ──
  async adminLogin(email, password) {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await fetch(`${API_BASE}/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData
      });
      const data = await response.json();
      if (!response.ok) {
        return { success: false, message: data.detail || "로그인 정보가 올바르지 않습니다." };
      }
      sessionStorage.setItem("admin_token", data.access_token);
      return { success: true };
    } catch (error) {
      console.error(error);
      return { success: false, message: "서버 통신 오류가 발생했습니다." };
    }
  }
};
