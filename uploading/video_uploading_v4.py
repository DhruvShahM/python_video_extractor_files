import os
import json
import time
from datetime import datetime
import pytz
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
# Constants
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
CLIENT_SECRET_FILE = "C:/Users/dhruv/Videos/Video_Extractor_Python_Files/python_video_extractor_files/uploading/client_secret.json"
METADATA_FILE = "C:/Users/dhruv/Videos/Video_Extractor_Python_Files/python_video_extractor_files/uploading/metadata.json"
CATEGORY_MAP = {
    "Film & Animation": "1",
    "Autos & Vehicles": "2",
    "Music": "10",
    "Pets & Animals": "15",
    "Sports": "17",
    "Travel & Events": "19",
    "Gaming": "20",
    "People & Blogs": "22",
    "Comedy": "23",
    "Entertainment": "24",
    "News & Politics": "25",
    "Howto & Style": "26",
    "Education": "27",
    "Science & Technology": "28",
    "Nonprofits & Activism": "29"
}

# def get_authenticated_service():
#     """Authenticate and return a YouTube API service instance."""
#     flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
#     credentials = flow.run_local_server(port=0)
#     return build("youtube", "v3", credentials=credentials)

def get_authenticated_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def convert_ist_to_utc(ist_time_str):
    """Convert IST time string (YYYY-MM-DD HH:MM:SS) to UTC in RFC 3339 format."""
    ist = pytz.timezone("Asia/Kolkata")
    local_time = datetime.strptime(ist_time_str, "%Y-%m-%d %H:%M:%S")  
    local_time = ist.localize(local_time)  
    utc_time = local_time.astimezone(pytz.utc)  
    return utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")  

def get_playlist_id(youtube, playlist_name):
    """Retrieve the playlist ID by name, or create it if it doesn't exist."""
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50
    )
    response = request.execute()

    for playlist in response.get("items", []):
        if playlist["snippet"]["title"] == playlist_name:
            return playlist["id"]

    # If playlist not found, create a new one
    print(f"🆕 Creating new playlist: {playlist_name}")
    create_request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": playlist_name,
                "description": f"Playlist for {playlist_name}",
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    create_response = create_request.execute()
    return create_response["id"]

def upload_video(youtube, video_data):
    """Uploads a video to YouTube and adds it to a playlist if provided."""
    video_file = video_data["videoFile"]
    if not os.path.exists(video_file):
        print(f"❌ Video file not found: {video_file}")
        return

    print(f"📤 Uploading: {video_data['title']}")

    category_id = CATEGORY_MAP.get(video_data["categoryName"], "22")  # Default to "People & Blogs"

    request_body = {
        "snippet": {
            "title": video_data["title"],
            "description": video_data["description"],
            "tags": video_data.get("tags", []),
            "categoryId": category_id,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": video_data["privacyStatus"],
            "selfDeclaredMadeForKids": video_data.get("madeForKids", False),
            "embeddable": True,
            "publicStatsViewable": True,
        },
        "recordingDetails": {
            "location": {
                "latitude": 28.6139,
                "longitude": 77.2090
            }
        }
    }

    # Handle Scheduled Publishing
    if video_data.get("publishAt"):
        utc_publish_time = convert_ist_to_utc(video_data["publishAt"])
        print(f"📅 Scheduling Video at UTC: {utc_publish_time}")
        request_body["status"]["publishAt"] = utc_publish_time
        request_body["status"]["privacyStatus"] = "private"

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status,recordingDetails",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"🚀 Upload Progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"✅ Video Uploaded Successfully: {video_data['title']} (ID: {video_id})")

    # Upload Thumbnail if specified
    if "thumbnail" in video_data:
        upload_thumbnail(youtube, video_id, video_data["thumbnail"])    

    # Add to Playlist if playlistName is provided
    if "playlistName" in video_data and video_data["playlistName"]:
        playlist_id = get_playlist_id(youtube, video_data["playlistName"])
        add_video_to_playlist(youtube, video_id, playlist_id)

def add_video_to_playlist(youtube, video_id, playlist_id):
    """Adds a video to a specified YouTube playlist."""
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    request.execute()
    print(f"✅ Video added to playlist: {playlist_id}")

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
        time.sleep(10)  # Prevent rate limit issues
