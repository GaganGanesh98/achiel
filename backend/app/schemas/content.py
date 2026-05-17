from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.content import Topic, PostStatus
from app.schemas.auth import UniversityOut


class AuthorOut(BaseModel):
    id: UUID
    display_name: str
    university: UniversityOut | None
    model_config = {"from_attributes": True}


class PostCreate(BaseModel):
    title: str = Field(min_length=4, max_length=200)
    body: str = Field(min_length=10, max_length=10000)
    topic: Topic


class PostOut(BaseModel):
    id: UUID
    title: str
    body: str
    topic: Topic
    status: PostStatus
    score: int
    comment_count: int
    author: AuthorOut
    university: UniversityOut | None
    created_at: datetime
    user_vote: int | None = None  # populated per-request: 1, -1, or None

    model_config = {"from_attributes": True}


class PostFeedQuery(BaseModel):
    topic: Topic | None = None
    university_id: UUID | None = None
    country: str | None = Field(default=None, min_length=2, max_length=2)
    sort: str = Field(default="new", pattern="^(new|top|hot)$")
    cursor: str | None = None  # ISO datetime for keyset pagination
    limit: int = Field(default=20, ge=1, le=50)


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class CommentOut(BaseModel):
    id: UUID
    body: str
    status: PostStatus
    author: AuthorOut
    created_at: datetime
    model_config = {"from_attributes": True}


class VoteIn(BaseModel):
    value: int = Field(description="1 for upvote, -1 for downvote, 0 to clear")

    model_config = {"json_schema_extra": {"example": {"value": 1}}}


class ReportCreate(BaseModel):
    reason: str = Field(min_length=4, max_length=500)
