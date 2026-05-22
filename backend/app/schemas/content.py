from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.content import Topic, PostStatus, Sentiment
from app.schemas.auth import UniversityOut


class WatchlistMatchOut(BaseModel):
    name: str
    university_domain: str | None = None
    role: str | None = None


class AuthorOut(BaseModel):
    id: UUID
    display_name: str
    university: UniversityOut | None = Field(default=None, validation_alias="university_link")
    model_config = {"from_attributes": True}


class PostCreate(BaseModel):
    title: str = Field(min_length=4, max_length=200)
    body: str = Field(min_length=10, max_length=10000)
    topic: Topic
    sentiment: Sentiment


class PostOut(BaseModel):
    id: UUID
    title: str
    body: str
    topic: Topic
    sentiment: Sentiment
    status: PostStatus
    score: int
    upvotes: int
    downvotes: int
    comment_count: int
    author: AuthorOut
    university: UniversityOut | None
    created_at: datetime
    my_vote: int = 0
    user_vote: int | None = None  # deprecated alias for my_vote
    is_hidden: bool = False
    hidden_reason: str | None = None
    watchlist_matches: list[WatchlistMatchOut] | None = None

    model_config = {"from_attributes": True}


class PostFeedQuery(BaseModel):
    topic: Topic | None = None
    university_id: UUID | None = None
    country: str | None = Field(default=None, min_length=2, max_length=2)
    sort: str = Field(default="new", pattern="^(new|top|hot)$")
    cursor: str | None = None
    limit: int = Field(default=20, ge=1, le=50)


class VoteIn(BaseModel):
    value: int = Field(description="1 for upvote, -1 for downvote, 0 to clear")

    @field_validator("value")
    @classmethod
    def validate_vote_value(cls, v: int) -> int:
        if v not in (-1, 0, 1):
            raise ValueError("value must be -1, 0, or 1")
        return v

    model_config = {"json_schema_extra": {"example": {"value": 1}}}


class VoteCountsOut(BaseModel):
    upvotes: int
    downvotes: int
    score: int
    my_vote: int


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    parent_comment_id: UUID | None = None


class CommentOut(BaseModel):
    id: UUID
    body: str
    post_id: UUID
    parent_comment_id: UUID | None
    is_deleted: bool
    score: int
    upvotes: int
    downvotes: int
    author: AuthorOut
    created_at: datetime
    my_vote: int = 0
    is_hidden: bool = False
    hidden_reason: str | None = None
    watchlist_matches: list[WatchlistMatchOut] | None = None

    model_config = {"from_attributes": True}
