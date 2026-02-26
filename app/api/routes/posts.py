from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostOut

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    content: str = Form(...),
    image: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Post:
    image_url = None

    if image:
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

        upload_dir = Path(settings.media_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(image.filename or "").suffix or ".jpg"
        file_name = f"{uuid4().hex}{ext}"
        file_path = upload_dir / file_name

        with file_path.open("wb") as buffer:
            buffer.write(image.file.read())

        image_url = f"/{settings.media_dir}/{file_name}"

    post = Post(content=content, image_url=image_url, owner_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("", response_model=list[PostOut])
def list_posts(db: Session = Depends(get_db)) -> list[Post]:
    return list(db.scalars(select(Post).order_by(Post.created_at.desc())))
