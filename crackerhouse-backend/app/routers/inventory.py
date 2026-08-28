"""
3단계: POS & 엑셀 연동 재고/발주 자동화 라우터
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/inventory", tags=["3단계: POS/엑셀 재고 자동화"])


# 초기 기본 재고 및 안전재고 시드 데이터
DEFAULT_INVENTORY = [
    {"name": "스너글 포근이 키링 (한정판)", "category": "콜라보 굿즈", "stock": 15, "safe": 30},
    {"name": "크래커하우스 빈티지 세탁 티셔츠", "category": "의류", "stock": 42, "safe": 20},
    {"name": "스너글 허거블 코튼 섬유유연제 1L", "category": "홈케어", "stock": 8, "safe": 25},
    {"name": "KRACKER LAUNDRY 시그니처 바삭 쿠키 세트", "category": "디저트", "stock": 5, "safe": 40},
    {"name": "스너글 블루스파클 향수 드레스퍼퓸", "category": "향기", "stock": 28, "safe": 15},
    {"name": "크래커하우스 x 스너글 콜라보 세탁바구니", "category": "콜라보 굿즈", "stock": 12, "safe": 15},
]


@router.get("/dashboard", response_model=List[schemas.StockOrderLogResponse], summary="실시간 재고 & 발주 추천 현황")
def get_inventory_dashboard(db: Session = Depends(get_db)):
    logs = db.query(models.StockOrderLog).all()

    # DB에 초기 데이터가 없으면 시드 데이터 생성
    if not logs:
        for item in DEFAULT_INVENTORY:
            log = models.StockOrderLog(
                product_name=item["name"],
                category=item["category"],
                current_stock=item["stock"],
                safe_stock=item["safe"],
                daily_sales=0,
                recommended_order=max(0, item["safe"] - item["stock"]),
                status_alert="CRITICAL" if item["stock"] < (item["safe"] * 0.5) else ("WARNING" if item["stock"] < item["safe"] else "NORMAL")
            )
            db.add(log)
        db.commit()
        logs = db.query(models.StockOrderLog).all()

    return logs


@router.post("/process-pos-excel", summary="POS / 스마트스토어 판매 데이터 파싱 & 발주량 산출")
def process_pos_excel(
    sales_data: List[Dict[str, Any]] = Body(...),
    db: Session = Depends(get_db)
):
    """
    POS 또는 스마트스토어 엑셀에서 추출한 판매 데이터 JSON 배열 수신
    예시: [{"product_name": "스너글 포근이 키링 (한정판)", "sales_qty": 12}, ...]
    """
    updated_items = []

    for row in sales_data:
        p_name = row.get("product_name")
        sales_qty = int(row.get("sales_qty", 0))

        log = db.query(models.StockOrderLog).filter(
            models.StockOrderLog.product_name == p_name
        ).first()

        if not log:
            # 신규 등록
            log = models.StockOrderLog(
                product_name=p_name,
                category=row.get("category", "기타"),
                current_stock=max(0, 50 - sales_qty),
                safe_stock=20,
                daily_sales=sales_qty,
                recommended_order=0,
                status_alert="NORMAL"
            )
            db.add(log)
        else:
            # 재고 차감 및 일일 판매량 업데이트
            log.daily_sales += sales_qty
            log.current_stock = max(0, log.current_stock - sales_qty)

        # 권장 발주량 계산: (안전재고 - 현재재고) + (일일 판매량 * 1.5 예측치)
        calc_order = (log.safe_stock - log.current_stock) + int(log.daily_sales * 1.2)
        log.recommended_order = max(0, calc_order)

        # 재고 상태 경고 지정
        if log.current_stock == 0 or log.current_stock <= (log.safe_stock * 0.3):
            log.status_alert = "CRITICAL"
        elif log.current_stock < log.safe_stock:
            log.status_alert = "WARNING"
        else:
            log.status_alert = "NORMAL"

        log.updated_at = datetime.utcnow()
        updated_items.append(log)

    db.commit()
    return {
        "success": True,
        "message": f"총 {len(updated_items)}개 상품의 POS 데이터가 성공적으로 파싱되어 재고 및 권장 발주량이 산출되었습니다.",
        "critical_alerts": sum(1 for item in updated_items if item.status_alert == "CRITICAL")
    }


@router.post("/reset-demo-stock", summary="시뮬레이션용 데이터 초기화")
def reset_demo_stock(db: Session = Depends(get_db)):
    db.query(models.StockOrderLog).delete()
    db.commit()

    for item in DEFAULT_INVENTORY:
        log = models.StockOrderLog(
            product_name=item["name"],
            category=item["category"],
            current_stock=item["stock"],
            safe_stock=item["safe"],
            daily_sales=0,
            recommended_order=max(0, item["safe"] - item["stock"]),
            status_alert="CRITICAL" if item["stock"] < (item["safe"] * 0.5) else ("WARNING" if item["stock"] < item["safe"] else "NORMAL")
        )
        db.add(log)
    db.commit()
    return {"message": "데모 재고 데이터가 초기화되었습니다."}


@router.post("/adjust-stock", summary="[스태프] 재고 수량/안전재고 직접 조정 및 입고")
def adjust_stock(
    product_id: str = Body(...),
    add_qty: int = Body(0),
    new_safe_stock: Optional[int] = Body(None),
    db: Session = Depends(get_db)
):
    log = db.query(models.StockOrderLog).filter(models.StockOrderLog.id == product_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="상품 재고 내역을 찾을 수 없습니다.")

    if add_qty > 0:
        log.current_stock += add_qty
    if new_safe_stock is not None and new_safe_stock >= 0:
        log.safe_stock = new_safe_stock

    # 발주 수량 및 경고 상태 재산출
    calc_order = (log.safe_stock - log.current_stock) + int(log.daily_sales * 1.2)
    log.recommended_order = max(0, calc_order)

    if log.current_stock == 0 or log.current_stock <= (log.safe_stock * 0.3):
        log.status_alert = "CRITICAL"
    elif log.current_stock < log.safe_stock:
        log.status_alert = "WARNING"
    else:
        log.status_alert = "NORMAL"

    log.updated_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "message": f"[{log.product_name}] 재고가 {log.current_stock}개(안전재고: {log.safe_stock}개)로 조정되었습니다.",
        "item": log
    }



@router.get("/export-csv", summary="일일 발주 보고서 CSV 다운로드")
def export_order_csv(db: Session = Depends(get_db)):
    from fastapi.responses import Response
    import io, csv

    logs = db.query(models.StockOrderLog).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["상품명", "카테고리", "현재재고", "안전재고", "당일판매량", "AI권장발주량", "재고상태"])

    for item in logs:
        writer.writerow([
            item.product_name,
            item.category,
            item.current_stock,
            item.safe_stock,
            item.daily_sales,
            item.recommended_order,
            item.status_alert
        ])

    csv_content = output.getvalue()
    return Response(
        content=csv_content.encode("utf-8-sig"), # Excel 한글 깨짐 방지 UTF-8 BOM
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=KRACKER_LAUNDRY_Order_Report.csv"
        }
    )


@router.post("/upload-csv-file", summary="실제 POS 엑셀(CSV) 파일 업로드 & 자동 파싱/차감")
async def upload_csv_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    실제 .csv 파일을 업로드 받아 UTF-8 / CP949 자동 인코딩 감지 후
    POS 판매 수량을 차감하고 안전재고 및 권장 발주량을 자동 계산합니다.
    """
    import csv, io

    contents = await file.read()
    
    # 인코딩 디코딩 시도
    decoded_text = ""
    for enc in ["utf-8-sig", "utf-8", "cp949", "euc-kr"]:
        try:
            decoded_text = contents.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if not decoded_text:
        raise HTTPException(status_code=400, detail="CSV 파일 인코딩을 읽을 수 없습니다. UTF-8 또는 CP949(EUC-KR) 인코딩으로 저장해 주세요.")

    csv_reader = csv.reader(io.StringIO(decoded_text))
    rows = list(csv_reader)

    if not rows:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    header = [h.strip() for h in rows[0]]
    
    # 컬럼 인덱스 찾기
    name_idx = -1
    qty_idx = -1
    cat_idx = -1

    for idx, col in enumerate(header):
        col_lower = col.lower()
        if "상품" in col_lower or "product" in col_lower or "품명" in col_lower:
            name_idx = idx
        elif "수량" in col_lower or "qty" in col_lower or "판매" in col_lower:
            qty_idx = idx
        elif "카테고리" in col_lower or "category" in col_lower or "분류" in col_lower:
            cat_idx = idx

    if name_idx == -1 or qty_idx == -1:
        # 헤더가 기본 형식이 아닌 경우 0번: 상품명, 1번: 수량으로 가정
        name_idx = 0
        qty_idx = 1 if len(header) > 1 else 0

    parsed_sales = []
    for row in rows[1:]:
        if len(row) <= max(name_idx, qty_idx):
            continue
        p_name = row[name_idx].strip()
        try:
            sales_qty = int(row[qty_idx].strip())
        except ValueError:
            sales_qty = 1

        cat_name = row[cat_idx].strip() if cat_idx != -1 and len(row) > cat_idx else "기타"
        if p_name:
            parsed_sales.append({"product_name": p_name, "sales_qty": sales_qty, "category": cat_name})

    if not parsed_sales:
        raise HTTPException(status_code=400, detail="유효한 판매 데이터 행을 찾지 못했습니다.")

    # 기존 파싱 함수 재활용
    return process_pos_excel(sales_data=parsed_sales, db=db)


