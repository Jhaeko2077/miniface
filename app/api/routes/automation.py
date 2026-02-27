import base64
import binascii
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
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


def _save_base64_image(image_base64: str, image_filename: str | None) -> str:
    raw_image = image_base64
    if image_base64.startswith("data:"):
        if "," not in image_base64:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid data URL format")
        _, raw_image = image_base64.split(",", 1)

    try:
        image_bytes = base64.b64decode(raw_image, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image_base64 payload") from exc

    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="image_base64 cannot be empty")

    upload_dir = Path(settings.media_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(image_filename or "").suffix or ".jpg"
    file_name = f"{uuid4().hex}{ext}"
    file_path = upload_dir / file_name

    with file_path.open("wb") as buffer:
        buffer.write(image_bytes)

    return f"/{settings.media_dir}/{file_name}"


@router.post("/n8n/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post_from_n8n(
    payload: N8NPostCreate,
    _: None = Depends(require_n8n_api_key),
    db: Session = Depends(get_db),
) -> Post:
    target_email = payload.author_email or settings.n8n_default_author_email
    if not target_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="author_email is required when N8N_DEFAULT_AUTHOR_EMAIL is not configured",
        )

    user = db.scalar(select(User).where(User.email == target_email))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author user not found")

    image_url = None
    if payload.image_base64:
        image_url = _save_base64_image(payload.image_base64, payload.image_filename)

    post = Post(content=payload.content, image_url=image_url, owner_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
