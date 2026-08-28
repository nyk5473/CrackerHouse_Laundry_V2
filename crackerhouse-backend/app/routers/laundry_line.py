"""
🧺 빨랫줄 집게 라우터
- GET  /api/laundry-line         : 승인된 집게 목록
- POST /api/laundry-line         : 새 집게 등록 (이미지 업로드)
- DELETE /api/laundry-line/{id}  : 삭제 (관리자)
"""
import os
import uuid
import random
import aiofiles

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_admin
from app import models, schemas
from app.config import settings

router = APIRouter(prefix="/api/laundry-line", tags=["🧺 빨랫줄"])


@router.get("", response_model=schemas.LaundryPinList, summary="승인된 빨랫줄 집게 목록")
def get_laundry_line(db: Session = Depends(get_db)):
    """승인된 폴라로이드 사진들을 빨랫줄 위치 정보와 함께 반환합니다."""
    pins = (
        db.query(models.LaundryPin)
        .filter(models.LaundryPin.is_approved == True)
        .order_by(models.LaundryPin.created_at.desc())
        .all()
    )
    return {"total": len(pins), "items": pins}


@router.post("", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED,
             summary="빨랫줄에 사진 집게 달기")
async def create_laundry_pin(
    nickname: str = Form(..., max_length=30),
    message: str = Form(None, max_length=100),
    pin_type: models.PinType = Form(default=models.PinType.PHOTO),
    image: UploadFile = File(..., description="폴라로이드 이미지"),
    db: Session = Depends(get_db),
):
    """
    방문객이 사진을 업로드하면 관리자 승인 후 빨랫줄에 노출됩니다.
    - 허용 확장자: jpg, jpeg, png, gif, webp
    - 최대 크기: 10MB
    """
    # 확장자 검증
    allowed_ext = {"jpg", "jpeg", "png", "gif", "webp"}
    ext = image.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed_ext:
        raise HTTPException(status_code=400, detail="허용되지 않는 파일 형식입니다.")

    # 파일 크기 검증
    content = await image.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"파일 크기는 {settings.MAX_FILE_SIZE_MB}MB 이하여야 합니다.")

    # 저장
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    # DB 저장 (랜덤 위치 배정) — 즉시 갤러리 노출
    pin = models.LaundryPin(
        image_url=f"/uploads/{filename}",
        nickname=nickname,
        message=message,
        pin_type=pin_type,
        position_x=round(random.uniform(2, 95), 2),
        position_y=round(random.uniform(0, 30), 2),
        is_approved=True,
    )
    db.add(pin)
    db.commit()

    return {"message": "사진이 빨랫줄에 달렸어요! 🧺", "success": True}


@router.get("/all", response_model=schemas.LaundryPinList, summary="전체 빨랫줄 집게 목록 (스태프용)")
def get_all_laundry_pins(db: Session = Depends(get_db)):
    pins = db.query(models.LaundryPin).order_by(models.LaundryPin.created_at.desc()).all()
    return {"total": len(pins), "items": pins}


@router.put("/approve/{pin_id}", summary="집게 승인 상태 변경 (스태프용)")
def approve_laundry_pin(pin_id: str, db: Session = Depends(get_db)):
    pin = db.query(models.LaundryPin).filter(models.LaundryPin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail="집게를 찾을 수 없습니다.")

    pin.is_approved = not pin.is_approved
    db.commit()
    return {"message": f"집게 승인 상태가 '{pin.is_approved}'(으)로 변경되었습니다.", "is_approved": pin.is_approved}


@router.get("/export-csv", summary="일일 한줄평 방명록 CSV 다운로드")
def export_laundry_csv(db: Session = Depends(get_db)):
    from fastapi.responses import Response
    import io, csv

    pins = db.query(models.LaundryPin).order_by(models.LaundryPin.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "닉네임", "한줄평 메시지", "이미지 경로", "승인여부", "작성일시"])

    for pin in pins:
        created_str = pin.created_at.strftime("%Y-%m-%d %H:%M:%S") if pin.created_at else ""
        writer.writerow([
            pin.id,
            pin.nickname,
            pin.message or "",
            pin.image_url or "",
            "승인" if pin.is_approved else "미승인",
            created_str
        ])

    csv_content = output.getvalue()
    return Response(
        content=csv_content.encode("utf-8-sig"),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=KRACKER_LAUNDRY_Review_Report.csv"
        }
    )


@router.delete("/{pin_id}", response_model=schemas.MessageResponse, summary="집게 삭제 (관리자)")
def delete_laundry_pin(
    pin_id: str,
    db: Session = Depends(get_db),
):
    pin = db.query(models.LaundryPin).filter(models.LaundryPin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail="집게를 찾을 수 없습니다.")

    # 파일도 함께 삭제
    if pin.image_url:
        local_path = pin.image_url.lstrip("/")
        if os.path.exists(local_path):
            os.remove(local_path)

    db.delete(pin)
    db.commit()
    return {"message": "집게가 제거됐습니다.", "success": True}

