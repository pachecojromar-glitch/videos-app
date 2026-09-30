from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/videos/{video_id}/comments", tags=["Comentarios"])

def _check_video(db: Session, video_id: int) -> None:
    if not db.get(models.Video, video_id):
        raise HTTPException(404, "Video no encontrado")

@router.post("", response_model=schemas.CommentOut, status_code=201)
def create_comment(
    video_id: int,
    data: schemas.CommentCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    _check_video(db, video_id)
    comment = models.Comment(content=data.content, user_id=user.id, video_id=video_id)
    db.add(comment)
    db.commit()
    return (
        db.query(models.Comment)
        .options(joinedload(models.Comment.author))
        .filter(models.Comment.id == comment.id)
        .one()
    )

@router.get("", response_model=list[schemas.CommentOut])
def list_comments(video_id: int, db: Session = Depends(get_db)):
    _check_video(db, video_id)
    return (
        db.query(models.Comment)
        .options(joinedload(models.Comment.author))
        .filter(models.Comment.video_id == video_id)
        .order_by(models.Comment.created_at.desc())
        .all()
    )
