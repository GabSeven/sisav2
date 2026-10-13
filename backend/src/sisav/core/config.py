from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SISAV 2"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://sisav:sisav@db:5432/sisav"

    jwt_secret: str = "dev-secret-troque-em-producao-1234567890"
    jwt_access_minutes: int = 15
    jwt_refresh_days: int = 7
    bcrypt_rounds: int = 12

    seed_password: str = "senha-seed"
    seed_usuario: str = "professor_teste"

_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings