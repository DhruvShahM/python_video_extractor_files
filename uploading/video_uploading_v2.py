import os
import json
import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# Constants
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]
CLIENT_SECRET_FILE = "C:/Users/dhruv/Videos/Video_Extractor_Python_Files/python_video_extractor_files/uploading/client_secret.json"
METADATA_FILE = "C:/Users/dhruv/Videos/Video_Extractor_Python_Files/python_video_extractor_files/uploading/metadata.json"


def get_authenticated_service():
    """Authenticate and return a YouTube API service instance."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)


def get_playlist_id(youtube, playlist_name):
    """Fetches the playlist ID by name."""
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    )
    response = request.execute()
    for playlist in response.get("items", []):
        if playlist["snippet"]["title"].lower() == playlist_name.lower():
            return playlist["id"]
    return None


def upload_video(youtube, video_data):
    """Uploads a single video to YouTube with progress tracking."""
    video_file = video_data["videoFile"]
    if not os.path.exists(video_file):
        print(f"❌ Video file not found: {video_file}")
        return

    print(f"📤 Uploading: {video_data['title']}")

    request_body = {
        "snippet": {
            "title": video_data["title"],
            "description": video_data["description"],
            "tags": video_data["tags"],
            "categoryId": video_data["categoryId"]
        },
        "status": {
            "privacyStatus": video_data["privacyStatus"],
            "selfDeclaredMadeForKids": video_data.get("madeForKids", False)
        }
    }

    # Handle Age Restriction (18+)
    if video_data.get("ageRestriction", False):
        request_body["status"]["madeForKids"] = False
        request_body["status"]["selfDeclaredMadeForKids"] = False
        request_body["status"]["ageRestricted"] = True  # Ensures age restriction

    # Scheduling Video for Future Publish (If specified)
    if "publishAt" in video_data:
        request_body["status"]["privacyStatus"] = "private"
        request_body["status"]["publishAt"] = video_data["publishAt"]

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"🚀 Upload Progress: {int(status.progress() * 100)}%")

    video_id = response['id']
    print(f"✅ Video Uploaded Successfully: {video_data['title']} (ID: {video_id})\n")

    # Upload Thumbnail if specified
    if "thumbnail" in video_data:
        upload_thumbnail(youtube, video_id, video_data["thumbnail"])

    # Add to Playlist if specified
    if "playlistName" in video_data:
        playlist_id = get_playlist_id(youtube, video_data["playlistName"])
        if playlist_id:
            add_to_playlist(youtube, video_id, playlist_id)
        else:
            print(f"❌ Playlist '{video_data['playlistName']}' not found.")


def upload_thumbnail(youtube, video_id, thumbnail_path):
    """Uploads a custom thumbnail for the video."""
    if os.path.exists(thumbnail_path):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        print(f"✅ Thumbnail Uploaded for Video ID: {video_id}")
    else:
        print(f"❌ Thumbnail file not found: {thumbnail_path}")


def add_to_playlist(youtube, video_id, playlist_id):
    """Adds a video to the specified YouTube playlist by playlist ID."""
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id}
            }
        }
    )
    request.execute()
    print(f"✅ Video added to playlist ID {playlist_id}")


if __name__ == "__main__":
    if not os.path.exists(CLIENT_SECRET_FILE):
        print("❌ Missing client_secret.json file!")
        exit()

    if not os.path.exists(METADATA_FILE):
        print("❌ Missing metadata.json file!")
        exit()

    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    if "videos" not in metadata or not metadata["videos"]:
        print("❌ No videos found in metadata.json!")
        exit()

    youtube = get_authenticated_service()

    # Iterate over each video in metadata.json and upload
    for video in metadata["videos"]:
        upload_video(youtube, video)
        time.sleep(10)  # Optional delay to prevent rate limit issues
