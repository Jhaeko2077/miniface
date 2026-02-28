from typing import Any

from pydantic import BaseModel, Field


class N8NPostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    author_email: str | None = None
    image_url: str | None = Field(
        default=None,
        description="URL pública de imagen (ej: Google Drive webContentLink).",
    )
    webContentLink: str | None = Field(
        default=None,
        description="Alias común de Google Drive para exponer una imagen pública.",
    )
    image_base64: str | None = Field(
        default=None,
        description="Imagen en base64 (opcional). Puede ser base64 puro o data URL.",
    )
    image_filename: str | None = Field(
        default=None,
        description="Nombre de archivo sugerido para la imagen (opcional).",
    )
    image_binary: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Objeto binario de n8n (ej: mimeType, fileName, fileExtension, id, data). "
            "Si incluye `data`, se decodifica como base64. Si incluye `id` filesystem-v2, "
            "se intentará leer desde N8N_BINARY_DATA_ROOT."
        ),
    )
