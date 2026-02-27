from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_n8n_api_key
from app.core.config import settings
from app.db.session import get_db
from app.models.post import Post
from app.models.user import User
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


@router.post("/n8n/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
@router.post("/n8n/post", response_model=PostOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_post_from_n8n(
    content: str = Form(..., min_length=1, max_length=2000),
    image: UploadFile | None = File(default=None),
    author_email: str | None = Form(default=None),
    _: None = Depends(require_n8n_api_key),
    db: Session = Depends(get_db),
) -> Post:
    target_email = author_email or settings.n8n_default_author_email
    if not target_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="author_email is required when N8N_DEFAULT_AUTHOR_EMAIL is not configured",
        )

    user = db.scalar(select(User).where(User.email == target_email))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author user not found")

    image_url = _save_upload_image(image) if image else None

    post = Post(content=content, image_url=image_url, owner_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
