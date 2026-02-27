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

    post = Post(content=payload.content, owner_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
