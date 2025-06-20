from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SpotCreate(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float
    photo_url: Optional[str] = None


class SpotOut(SpotCreate):
    id: str  
    category: str
    upvotes: int
    created_at: datetime


class CommentCreate(BaseModel):
    spot_id: str  
    comment: str  


class CommentOut(CommentCreate):
    id: str  
    user_id: str
    username: str
    created_at: Optional[datetime] = None
