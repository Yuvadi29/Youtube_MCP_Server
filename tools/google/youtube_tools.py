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


class YoutubeTool:
    """
    Toolkit for interacting with Youtube Data API
    """

    API_NAME = "youtube"
    API_VERSION = "v3"
    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

    def __init__(self, client_secret: str) -> None:
        self.client_secret - client_secret
        self._init_youtube_service()

    def _init_youtube_service(self):
        """
        Initialize the Youtube Data API service.
        """
        self.service = create_service(
            self.client_secret, self.API_NAME, self.API_VERSION, self.SCOPES
        )
        if not self.service:
            raise Exception("Failed to create Youtube Service")

    @property
    def youtube_service(self) -> Resource:
        """
        Return Youtube Data API service instance
        """
        return self.service

    def get_channel_info(self, channel_id: str) -> ChannelInfo:
        """
        Get Information about a Youtube Channel based on the provided Channel ID.

        Args:
            channel_id: The ID of Youtube Channel.

        Returns:
            ChannelInfo: Information about the Youtube Channel
        """

        if channel_id.startswith("UC"):
            request = self.service.channels().list(
                part="snippet, statistics", id=channel_id
            )
        elif channel_id.startswith("@"):
            request = self.service.channels().list(
                part="snippet, statistics", forHandle=channel_id
            )
        else:
            return "Invalid Channel ID"

        response = request.execute()

        channel_info = ChannelInfo(
            channel_id=response["items"][0].get("id"),
            channel_title=response["items"][0]["snippet"].get("title"),
            description=response["items"][0]["snippet"].get("description"),
            published_at=response["items"][0]["snippet"].get("publishedAt"),
            country=response["items"][0]["snippet"].get("country"),
            view_count=response["items"][0]["statistics"].get("viewCount"),
            subscriber_count=response["items"][0]["statistics"].get("subscriberCount"),
            video_count=response["items"][0]["statistics"].get("videoCount"),
        )

        return channel_info.model_dump_json()

    def search_channel(
        self,
        channel_name: str,
        published_after: str = None,
        published_before: str = None,
        region_code: str = "US",
        order: str = "relevance",
        max_results: int = 50,
    ) -> str:
        """
        Searches for Youtube Channels based on provided channel Name.

        Args:
            channel_name: The name of the channel to search for.
            order: The order in which to return results. Options are date, rating, relevance, title, videoCount and viewCount
            max_results: THe maximum number of results to return
        """

        lst = []
        total_results = 0
        next_page_token = None

        while len(lst) < max_results:
            current_max = min(50, max_results - len(lst))

            request = self.service.search().list(
                part="snippet",
                q=channel_name,
                type="channel",
                maxResults=current_max,
                order=order,
                publishedAfter=published_after,
                publishedBefore=published_before,
                regionCode=region_code,
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response["items"]:
                channel_id = item["id"].get("channelId")
                channel_title = item["snippet"].get("title")
                channel_description = item["snippet"].get("description")
                channel_published_at = item["snippet"].get("publishedAt")
                channel_info = ChannelInfo(
                    channel_id=channel_id,
                    channel_title=channel_title,
                    description=channel_description,
                    published_at=channel_published_at,
                )
                lst.append(channel_info)

            total_results = response["pageInfo"]["totalResults"]
            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        return ChannelResults(
            total_results=total_results, channels=lst
        ).model_dump_json()

    def search_playlist(
        self,
        query: str,
        published_after: str = None,
        published_before: str = None,
        region_code: str = "US",
        order: str = "date",
        max_results: int = 50,
    ) -> str:
        """
        Searches for Youtube Playlist based on provided query.
        """

        lst = []
        total_results = 0
        next_page_token = None

        while len(lst) < max_results:
            current_max = min(50, max_results - len(lst))

            request = self.service.search().list(
                part="snippet",
                q=query,
                type="playlist",
                maxResults=current_max,
                order=order,
                publishedAfter=published_after,
                publishedBefore=published_before,
                regionCode=region_code,
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response["items"]:
                playlist_id = item["id"].get("playlistId")
                playlist_title = item["snippet"].get("title")
                channel_id = item["snippet"].get("channelId")
                playlist_description = item["snippet"].get("description")
                playlist_published_at = item["snippet"].get("publishedAt")
                playlist_info = PlaylistInfo(
                    playlist_id=playlist_id,
                    playlist_title=playlist_title,
                    channel_id=channel_id,
                    description=playlist_description,
                    published_at=playlist_published_at,
                )
                lst.append(playlist_info)

            total_results = response["pageInfo"]["totalResults"]
            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        return PlaylistResults(
            total_results=total_results, playlists=lst
        ).model_dump_json()

    def search_videos(
        self,
        query: str,
        published_after: str = None,
        published_before: str = None,
        region_code: str = "US",
        video_duration: str = "any",
        order: str = "date",
        max_results: int = 50,
    ) -> str:
        """
        Searches for Youtube videos based on provided query.
        """

        lst = []
        total_results = 0
        next_page_token = None

        while len(lst) < max_results:
            current_max = min(50, max_results - len(lst))

            request = self.service.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=current_max,
                order=order,
                publishedAfter=published_after,
                publishedBefore=published_before,
                videoDuration=video_duration,
                regionCode=region_code,
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response["items"]:
                channel_id = item["id"].get("channelId")
                channel_title = item["snippet"].get("channelTitle")
                video_id = item["id"].get("videoId")
                video_title = item["snippet"].get("itle")
                video_description = item["snippet"].get("description")
                video_published = item["snippet"].get("publishTime")
                video_info = VideoInfo(
                    channel_id=channel_id,
                    channel_title=channel_title,
                    video_id=video_id,
                    video_title=video_title,
                    description=video_description,
                    published_at=video_published,
                )
                lst.append(video_info)

            total_results = response["pageInfo"]["totalResults"]
            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        return VideoResults(total_results=total_results, videos=lst).model_dump_json()

    def get_video_info(self, video_ids: str, max_results: int = 50) -> str:
        """
        Retrieves detailed information about Youtube Videos based on the provided video IDs.
        """

        if len(video_ids) == 1:
            video_ids = extreact_video_id(video_ids)
            if not video_ids:
                return "Error: Invalid Video ID or Url"

        lst = []
        total_results = 0
        next_page_token = None

        while len(lst) < max_results:
            current_max = min(50, max_results - len(lst))

            request = self.service.videos().list(
                part="id,snippet,contentDetails,statistics,paidProductPlacementDetails,TopicDetails",
                id=video_ids,
                maxResulst=current_max,
                pageToken=next_page_token,
            )
            response = request.execute()

            for item in response["items"]:
                snippet = item["snippet"]
                content_details = item.get("contentDetails", {})
                statistics = item.get("statistics", {})
                topic_details = item.get("topicDetails", {})

                video_info = VideoInfo(
                    channel_id=snippet["channelId"],
                    channel_title=snippet["channelTitle"],
                    video_id=item["id"],
                    video_title=snippet["title"],
                    description=snippet.get("description", ""),
                    published_at=snippet["publishedAt"],
                    tags=snippet.get("tags", []),
                    duration=content_details.get("duration"),
                    dimension=content_details.get("dimension"),
                    view_count=statistics.get("viewCount"),
                    like_count=statistics.get("likeCount", 0),
                    comment_count=statistics.get("commentCount", 0),
                    topic_categories=topic_details.get("topicCategories", []),
                    has_paid_product_placement=snippet.get("hasPaidPromotion", False),
                )
                lst.append(video_info)

            total_results = response["pageInfo"]["totalResults"]
            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        return VideoResults(total_results=total_results, videos=lst).model_dump_json()
