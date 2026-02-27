from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
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


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    if post.image_url:
        image_relative = post.image_url.lstrip("/")
        image_path = Path(image_relative)
        if image_path.exists() and image_path.is_file():
            image_path.unlink(missing_ok=True)

    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
