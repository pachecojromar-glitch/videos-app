"""Almacenamiento de archivos: carpeta local (desarrollo) o Amazon S3 (produccion).

En S3 no se usan credenciales en el codigo: boto3 toma las del IAM Role de la EC2.
"""
import os
import shutil
import uuid
from urllib.parse import urlparse
from fastapi import UploadFile
from .config import settings

def _bucket(kind: str) -> str:
    return settings.s3_videos_bucket if kind == "videos" else settings.s3_thumbnails_bucket

def _s3():
    import boto3
    return boto3.client("s3", region_name=settings.aws_region)

def save_file(kind: str, upload: UploadFile) -> str:
    """Guarda el archivo y devuelve su URL publica. kind: 'videos' o 'thumbnails'."""
    ext = os.path.splitext(upload.filename or "")[1].lower()
    name = f"{uuid.uuid4().hex}{ext}"
    upload.file.seek(0)

    if settings.storage_backend == "s3":
        bucket = _bucket(kind)
        _s3().upload_fileobj(
            upload.file, bucket, name,
            ExtraArgs={"ContentType": upload.content_type or "application/octet-stream"},
        )
        return f"https://{bucket}.s3.{settings.aws_region}.amazonaws.com/{name}"

    folder = os.path.join(settings.media_dir, kind)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, name), "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return f"{settings.public_base_url}/media/{kind}/{name}"

def delete_file(kind: str, url: str) -> None:
    """Borra el archivo (si falla no interrumpe la operacion)."""
    name = os.path.basename(urlparse(url).path)
    if not name:
        return
    try:
        if settings.storage_backend == "s3":
            _s3().delete_object(Bucket=_bucket(kind), Key=name)
        else:
            path = os.path.join(settings.media_dir, kind, name)
            if os.path.exists(path):
                os.remove(path)
    except Exception as exc:  # noqa: BLE001
        print(f"No se pudo borrar {kind}/{name}: {exc}")
