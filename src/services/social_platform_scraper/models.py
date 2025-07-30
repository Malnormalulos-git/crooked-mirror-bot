from dataclasses import dataclass
from enum import Enum


class MediaType(Enum):
    IMAGE = "image",
    VIDEO = "video",


class SocialPlatform(Enum):
    TWITTER = "twitter"
    # FACEBOOK = "facebook"
    # INSTAGRAM = "instagram"


@dataclass(frozen=True)
class MediaItem:
    type: MediaType
    url: str


@dataclass(frozen=True)
class PostStats:
    likes: int
    shares: int
    comments: int
    views: str | None = None


@dataclass(frozen=True)
class SocialPost:
    id: str
    platform: SocialPlatform
    text: str
    author: str
    created_at: str
    stats: PostStats
    media: set[MediaItem]
