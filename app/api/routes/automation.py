import base64
import binascii
import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_n8n_api_key
from app.core.config import settings
from app.db.session import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.automation import N8NPostCreate
from app.schemas.post import PostOut

router = APIRouter(prefix="/automation", tags=["automation"])


def _save_upload_image(image: UploadFile) -> str:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

    upload_dir = Path(settings.media_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(image.filename or "").suffix or ".jpg"
    file_name = f"{uuid4().hex}{ext}"
    file_path = upload_dir / file_name

    with file_path.open("wb") as buffer:
        buffer.write(image.file.read())

    return f"/{settings.media_dir}/{file_name}"


def _save_binary_image(content: bytes, filename: str | None = None, mime_type: str | None = None) -> str:
    upload_dir = Path(settings.media_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(filename or "").suffix
    if not ext and mime_type:
        guessed_ext = mimetypes.guess_extension(mime_type)
        if guessed_ext:
            ext = guessed_ext
    if not ext:
        ext = ".jpg"

    file_name = f"{uuid4().hex}{ext}"
    file_path = upload_dir / file_name
    file_path.write_bytes(content)

    return f"/{settings.media_dir}/{file_name}"


def _decode_base64_image(image_base64: str) -> tuple[bytes, str | None]:
    raw_data = image_base64.strip()
    mime_type = None

    if raw_data.startswith("data:"):
        header, _, encoded = raw_data.partition(",")
        if not encoded:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image_base64 data URL")
        raw_data = encoded
        if ";base64" in header:
            mime_type = header[5:].split(";")[0] or None

    try:
        image_bytes = base64.b64decode(raw_data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image_base64 payload") from exc

    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="image_base64 is empty")

    return image_bytes, mime_type


@router.post("/n8n/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
@router.post("/n8n/post", response_model=PostOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_post_from_n8n(
    request: Request,
    content: str | None = Form(default=None, min_length=1, max_length=2000),
    image: UploadFile | None = File(default=None),
    author_email: str | None = Form(default=None),
    _: None = Depends(require_n8n_api_key),
    db: Session = Depends(get_db),
) -> Post:
    payload_content = content
    payload_author_email = author_email
    image_url = _save_upload_image(image) if image else None

    if payload_content is None:
        raw_json = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
        if raw_json:
            parsed_payload = N8NPostCreate.model_validate(raw_json)
            payload_content = parsed_payload.content
            payload_author_email = parsed_payload.author_email

            if parsed_payload.image_base64:
                image_bytes, mime_type = _decode_base64_image(parsed_payload.image_base64)
                image_url = _save_binary_image(
                    image_bytes,
                    filename=parsed_payload.image_filename,
                    mime_type=mime_type,
                )

    if payload_content is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Field required: content")

    target_email = payload_author_email or settings.n8n_default_author_email
    if not target_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="author_email is required when N8N_DEFAULT_AUTHOR_EMAIL is not configured",
        )

    user = db.scalar(select(User).where(User.email == target_email))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author user not found")

    post = Post(content=payload_content, image_url=image_url, owner_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
