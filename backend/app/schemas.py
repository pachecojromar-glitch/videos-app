from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

class UserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr

class UserProfile(UserOut):
    videos_count: int

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class VideoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    video_url: str
    thumbnail_url: str
    views: int
    created_at: datetime
    user_id: int
    owner: UserBrief

class VideoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None

class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)

class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str
    created_at: datetime
    user_id: int
    video_id: int
    author: UserBrief
