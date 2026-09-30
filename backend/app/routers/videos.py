from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from .. import models, schemas, storage
from ..config import settings
from ..database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/videos", tags=["Videos"])

VIDEO_TYPES = {"video/mp4"}
VIDEO_EXTS = {".mp4"}
IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}

def _ext(name: str | None) -> str:
    name = (name or "").lower()
    return name[name.rfind("."):] if "." in name else ""

def _size(f: UploadFile) -> int:
    f.file.seek(0, 2)
    size = f.file.tell()
    f.file.seek(0)
    return size

def _validate(f: UploadFile, types: set, exts: set, max_mb: int, label: str) -> None:
    if f.content_type not in types or _ext(f.filename) not in exts:
        raise HTTPException(400, f"{label}: formato no permitido (permitidos: {', '.join(sorted(exts))})")
    if _size(f) > max_mb * 1024 * 1024:
        raise HTTPException(413, f"{label}: supera el máximo de {max_mb} MB")

def _query(db: Session):
    return db.query(models.Video).options(joinedload(models.Video.owner))

def _get_or_404(db: Session, video_id: int) -> models.Video:
    video = _query(db).filter(models.Video.id == video_id).first()
    if not video:
        raise HTTPException(404, "Video no encontrado")
    return video

@router.post("", response_model=schemas.VideoOut, status_code=201)
def create_video(
    title: str = Form(..., min_length=1, max_length=200),
    description: str = Form(""),
    video: UploadFile = File(...),
    thumbnail: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    _validate(video, VIDEO_TYPES, VIDEO_EXTS, settings.max_video_mb, "Video")
    _validate(thumbnail, IMAGE_TYPES, IMAGE_EXTS, settings.max_thumbnail_mb, "Miniatura")

    video_url = storage.save_file("videos", video)
    try:
        thumb_url = storage.save_file("thumbnails", thumbnail)
    except Exception:
        storage.delete_file("videos", video_url)
        raise HTTPException(500, "No se pudo guardar la miniatura")

    item = models.Video(
        title=title, description=description,
        video_url=video_url, thumbnail_url=thumb_url, user_id=user.id,
    )
    db.add(item)
    db.commit()
    return _get_or_404(db, item.id)

@router.get("", response_model=list[schemas.VideoOut])
def list_videos(
    user_id: int | None = None,
    q: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = _query(db)
    if user_id is not None:
        query = query.filter(models.Video.user_id == user_id)
    if q:
        query = query.filter(models.Video.title.ilike(f"%{q}%"))
    return query.order_by(models.Video.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{video_id}", response_model=schemas.VideoOut)
def get_video(video_id: int, db: Session = Depends(get_db)):
    """Devuelve el video y suma una vista."""
    video = _get_or_404(db, video_id)
    video.views += 1
    db.commit()
    return _get_or_404(db, video_id)

@router.get("/{video_id}/recommended", response_model=list[schemas.VideoOut])
def recommended(video_id: int, limit: int = Query(6, ge=1, le=20), db: Session = Depends(get_db)):
    """Otros videos (aleatorios) para la barra de recomendados."""
    return (
        _query(db)
        .filter(models.Video.id != video_id)
        .order_by(func.random())
        .limit(limit)
        .all()
    )

@router.put("/{video_id}", response_model=schemas.VideoOut)
def update_video(
    video_id: int,
    data: schemas.VideoUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    video = _get_or_404(db, video_id)
    if video.user_id != user.id:
        raise HTTPException(403, "Solo el dueño puede editar este video")
    if data.title is not None:
        video.title = data.title
    if data.description is not None:
        video.description = data.description
    db.commit()
    return _get_or_404(db, video_id)

@router.delete("/{video_id}", status_code=204)
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    video = _get_or_404(db, video_id)
    if video.user_id != user.id:
        raise HTTPException(403, "Solo el dueño puede eliminar este video")
    video_url, thumb_url = video.video_url, video.thumbnail_url
    db.delete(video)
    db.commit()
    storage.delete_file("videos", video_url)
    storage.delete_file("thumbnails", thumb_url)
