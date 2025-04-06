import re
import json
from googleapiclient.discovery import Resource
from pydantic import BaseModel, Field
from tools.google.google_apis import create_service


class PlaylistInfo(BaseModel):
    playlist_id: str = Field(..., description="Playlist ID")
    playlist_title: str = Field(..., description="Playlist Title")
    channel_id: str = Field(..., description="Channel ID")
    description: str = Field(..., description="Playlist Description")
    published_at: str = Field(..., description="Playlist Published Time")


class PlaylistResults(BaseModel):
    total_results: int = Field(..., description="Total Number of Results")
    playlists: list[PlaylistInfo] = Field(..., description="Playlist Information")


class ChannelInfo(BaseModel):
    channel_id: str = Field(..., description="Channel ID")
    channel_title: str = Field(..., description="Channel Title")
    description: str = Field(..., description="Channel Description")
    published_at: str = Field(..., description="Channel Published Time")
    country: str = Field(..., description="Channel Country")
    view_count: str = Field(..., description="View Count")
    subscriber_count: str = Field(..., description="Subscriber Count")
    video_count: str = Field(..., description="Video Count")


class ChannelResults(BaseModel):
    total_results: int = Field(..., description="Total Number of Results")
    channels: list[ChannelInfo] = Field(..., description="Channel Information")


class VideoInfo(BaseModel):
    channel_id: str = Field(..., description="Channel ID")
    channel_title: str = Field(..., description="Channel Title")
    video_id: str = Field(..., description="Video ID")
    video_title: str = Field(..., description="Video Title")
    description: str = Field(..., description="Channel Description")
    published_at: str = Field(..., description="Channel Published Time")

    # Additional Information
    tags: list[str] = Field(None, description="Video Tags")
    duration: str = Field(None, description="Video Duration")
    dimension: str = Field(None, description="Video Dimension")
    view_count: str = Field(None, description="Video Count")
    like_count: str = Field(None, description="Like Count")
    comment_report: str = Field(None, description="Comment Count")
    topic_categories: str = Field(None, description="Topic Categories")
    has_paid_product_placement: str = Field(
        None, description="Has Paid Product Placement"
    )


class VideoResults(BaseModel):
    total_results: int = Field(..., description="Total Number of Results")
    videos: list[VideoInfo] = Field(..., description="Video Information")


def extreact_video_id(input_str: str) -> str | None:
    """
    Extract Youtube Video ID from a URL or ID String

    Args:
        input_str = URL or ID string to extract video ID from.

    Returns:
        str: Extracted Youtube Video ID
    """

    url_pattern = re.compile(
        r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
    )
    match = url_pattern.match(input_str)

    if match:
        return match.group(1)

    id_pattern = re.compile(r"^[a-zA-Z0-9_-]{11}")
    if id_pattern.match(input_str):
        return input_str

    return None
