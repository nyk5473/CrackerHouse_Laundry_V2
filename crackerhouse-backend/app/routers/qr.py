"""
📱 QR코드 라우터
- GET /api/qr          : 현장용 QR코드 이미지 반환 (업로드 페이지 링크)
- GET /api/qr/download : QR코드 PNG 다운로드
"""
import io
import os
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, FileResponse

router = APIRouter(prefix="/api/qr", tags=["📱 QR코드"])


def _make_qr(url: str) -> io.BytesIO:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        back_color="#FAFAF8",
        fill_color="#2A2A2A",
    )
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


@router.get("", summary="현장 QR코드 이미지 반환")
def get_qr(
    url: str = Query(..., description="QR코드로 인코딩할 URL (프론트 업로드 페이지 주소)")
):
    """
    현장 인쇄용 QR코드를 PNG 이미지로 반환합니다.
    방문객이 스캔하면 폴라로이드 업로드 페이지로 이동합니다.
    """
    buf = _make_qr(url)
    return StreamingResponse(buf, media_type="image/png")


@router.get("/download", summary="QR코드 PNG 다운로드")
def download_qr(
    url: str = Query(..., description="QR코드로 인코딩할 URL"),
    filename: str = Query(default="crackerhouse_qr", description="다운로드 파일명"),
):
    buf = _make_qr(url)
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{filename}.png"'},
    )
