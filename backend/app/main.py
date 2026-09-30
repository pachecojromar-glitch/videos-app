import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .database import Base, engine
from .routers import users, videos, comments

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Plataforma de Videos", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # luego lo restringimos a la URL del bucket frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

# En modo local los archivos se sirven desde /media (en S3 no hace falta)
if settings.storage_backend == "local":
    os.makedirs(settings.media_dir, exist_ok=True)
    app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

app.include_router(users.router)
app.include_router(videos.router)
app.include_router(comments.router)

@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
