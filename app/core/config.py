from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "miniface-api"
    app_version: str = "0.1.0"

    database_url: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    media_dir: str = "uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


try:
    settings = Settings()
except ValidationError as exc:
    missing_fields = ", ".join(error["loc"][0] for error in exc.errors())
    raise RuntimeError(
        "Faltan variables de entorno obligatorias para iniciar la API: "
        f"{missing_fields}.\n"
        "Pasos: 1) copia '.env.example' a '.env', "
        "2) agrega DATABASE_URL y SECRET_KEY, "
        "3) vuelve a ejecutar el servidor."
    ) from exc
