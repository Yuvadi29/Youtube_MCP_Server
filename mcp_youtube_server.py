import re
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from youtube_transcript_api import YouTubeTranscriptApi
from tools.google import YoutubeTool, extract_video_id

mcp = FastMCP(
    "Youtube MCP Server",
    dependencies=[
        "youtube_transcript_api",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
    ],
)

yt_tool = YoutubeTool(r"/Users/adityatrivedi/Desktop/Developer/Youtube-MCP-Server/client_secret.json")

mcp.add_tool(
    yt_tool.get_video_info,
    name="Get Video Info",
    description="Get video information from Youtube",
)
mcp.add_tool(
    yt_tool.get_channel_info,
    name="Get Channel Info",
    description="Get channel information from Youtube",
)
mcp.add_tool(
    yt_tool.search_channel,
    name="Search Channel",
    description="Search for Youtube Channels",
)
mcp.add_tool(
    yt_tool.search_playlist,
    name="Search Playlist",
    description="Search for Youtube Playlists",
)
mcp.add_tool(
    yt_tool.search_videos, name="Search Videos", description="Search for Youtube Videos"
)
mcp.add_tool(
    yt_tool.get_channel_videos,
    name="Get Channel Videos",
    description="Get videos uploaded by Youtube Channel",
)
mcp.add_tool(
    extract_video_id,
    name="Extract Video Id",
    description="Extract Youtube Video ID from a given string",
)


@mcp.tool(
    name="Download Youtube Video Transcript",
    description="Download the transcript of a Youtube Video",
)
def download_transcript(video_id: str, include_timestamp: bool = False) -> str:
    """
    Download the transcript for a Youtube Video.
    """
    if not video_id:
        return "Invalid Youtube Video ID or URL".format

    try:
        if include_timestamp:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = str(transcript)

        else:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = "\n".join([entry["text"] for entry in transcript])

        return transcript_text

    except Exception as e:
        return f"Error Downloading Transcript: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
