from pydantic import BaseModel, Field


class N8NPostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    author_email: str | None = None
    image_base64: str | None = Field(
        default=None,
        description="Imagen en base64 (opcional). Puede ser base64 puro o data URL.",
    )
    image_filename: str | None = Field(
        default=None,
        description="Nombre de archivo sugerido para la imagen (opcional).",
    )
