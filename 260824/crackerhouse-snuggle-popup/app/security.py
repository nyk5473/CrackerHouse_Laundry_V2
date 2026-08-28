"""
간단한 인증 유틸리티 (데모/발표용 수준)
- 비밀번호 해시: 표준 라이브러리 hashlib.pbkdf2_hmac 사용 (외부 의존성 없이 동작)
- 로그인 세션: itsdangerous로 서명된 쿠키 발급 (JWT 없이도 위변조 방지)

주의: 실제 서비스 배포 시에는 HTTPS + 더 강한 시크릿 키 관리, rate limit 등을
추가로 적용해야 합니다. 여기서는 팀 프로젝트 발표/데모 목적에 맞춘 구성입니다.
"""
import hashlib
import hmac
import os
import secrets

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SECRET_KEY = os.environ.get("POPUP_SECRET_KEY", "crackerhouse-x-snuggle-dev-secret-change-me")
SESSION_COOKIE_NAME = "popup_admin_session"
SESSION_MAX_AGE_SECONDS = 8 * 60 * 60  # 8시간

_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="admin-session")


def hash_password(raw_password: str, salt: str | None = None) -> str:
    """pbkdf2_hmac 기반 해시. 반환값 형식: "salt$hexhash" """
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", raw_password.encode("utf-8"), salt.encode("utf-8"), 200_000)
    return f"{salt}${digest.hex()}"


def verify_password(raw_password: str, stored_hash: str) -> bool:
    try:
        salt, _ = stored_hash.split("$", 1)
    except ValueError:
        return False
    candidate = hash_password(raw_password, salt=salt)
    return hmac.compare_digest(candidate, stored_hash)


def create_session_token(admin_id: int, username: str) -> str:
    return _serializer.dumps({"admin_id": admin_id, "username": username})


def read_session_token(token: str) -> dict | None:
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE_SECONDS)
        return data
    except (BadSignature, SignatureExpired):
        return None
