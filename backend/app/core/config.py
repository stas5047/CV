from functools import lru_cache
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    admin_email: str = Field(alias="ADMIN_EMAIL")
    admin_password: str = Field(min_length=8, alias="ADMIN_PASSWORD")
    allow_public_registration: bool = Field(default=True, alias="ALLOW_PUBLIC_REGISTRATION")
    storage_root: str = Field(default="/app/storage", alias="STORAGE_ROOT")
    models_root: str = Field(default="/app/storage/models", alias="MODELS_ROOT")
    backend_cors_origins: Annotated[list[str], NoDecode] = Field(alias="BACKEND_CORS_ORIGINS")
    max_image_size_mb: int = Field(default=20, alias="MAX_IMAGE_SIZE_MB")
    max_video_size_mb: int = Field(default=500, alias="MAX_VIDEO_SIZE_MB")
    run_migrations_on_start: bool = Field(default=True, alias="RUN_MIGRATIONS_ON_START")
    run_seed_on_start: bool = Field(default=True, alias="RUN_SEED_ON_START")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        elif isinstance(value, list):
            origins = [str(origin).strip() for origin in value if str(origin).strip()]
        else:
            raise ValueError("BACKEND_CORS_ORIGINS must be a comma-separated string or list")

        if not origins:
            raise ValueError("BACKEND_CORS_ORIGINS must include at least one explicit origin")
        if "*" in origins:
            raise ValueError("Wildcard CORS origins are not allowed")
        return origins

    def __repr__(self) -> str:
        return (
            "Settings("
            "database_url='********', "
            "jwt_secret_key='********', "
            f"jwt_algorithm={self.jwt_algorithm!r}, "
            f"access_token_expire_minutes={self.access_token_expire_minutes!r}, "
            f"admin_email={self.admin_email!r}, "
            "admin_password='********', "
            f"allow_public_registration={self.allow_public_registration!r}, "
            f"storage_root={self.storage_root!r}, "
            f"models_root={self.models_root!r}, "
            f"backend_cors_origins={self.backend_cors_origins!r}, "
            f"max_image_size_mb={self.max_image_size_mb!r}, "
            f"max_video_size_mb={self.max_video_size_mb!r}, "
            f"run_migrations_on_start={self.run_migrations_on_start!r}, "
            f"run_seed_on_start={self.run_seed_on_start!r}"
            ")"
        )

    def sensitive_log_values(self) -> tuple[str, ...]:
        return (
            self.database_url,
            self.jwt_secret_key,
            self.admin_password,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
