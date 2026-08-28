from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "빈티지 코인 세탁소 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 데이터베이스
    DATABASE_URL: str = "sqlite:///./crackerhouse.db"

    # JWT
    SECRET_KEY: str = "crackerhouse-laundromat-secret-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # 파일 업로드
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10

    # 관리자 초기 계정
    ADMIN_EMAIL: str = "admin@crackerhouse.kr"
    ADMIN_PASSWORD: str = "crackerhouse2024!"

    # CORS — 데모/팝업 환경: file:// 및 로컬 개발서버 모두 허용
    ALLOWED_ORIGINS: str = "*"

    @property
    def allowed_origins_list(self) -> List[str]:
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
