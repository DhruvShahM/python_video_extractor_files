import os
import json
import time
from datetime import datetime
import pytz
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from concurrent.futures import ThreadPoolExecutor

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
CLIENT_SECRET_FILE = "C:/Users/dhruv/Videos/Video_Extractor_Python_Files/python_video_extractor_files/uploading/client_secret.json"
METADATA_FILE = "C:/Users/dhruv/Videos/Video_Extractor_Python_Files/python_video_extractor_files/uploading/metadata.json"
CATEGORY_MAP = { "Film & Animation": "1", "Autos & Vehicles": "2", "Music": "10", "Pets & Animals": "15", "Sports": "17", "Travel & Events": "19", "Gaming": "20", "People & Blogs": "22", "Comedy": "23", "Entertainment": "24", "News & Politics": "25", "Howto & Style": "26", "Education": "27", "Science & Technology": "28", "Nonprofits & Activism": "29" }

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
    ist = pytz.timezone("Asia/Kolkata")
    local_time = datetime.strptime(ist_time_str, "%Y-%m-%d %H:%M:%S")
    local_time = ist.localize(local_time)
    utc_time = local_time.astimezone(pytz.utc)
    return utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")

def get_playlist_id(youtube, playlist_name):
    request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
    response = request.execute()
    for playlist in response.get("items", []):
        if playlist["snippet"]["title"] == playlist_name:
            return playlist["id"]
    create_request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": playlist_name, "description": f"Playlist for {playlist_name}"},
            "status": {"privacyStatus": "public"}
        }
    )
    create_response = create_request.execute()
    return create_response["id"]

def upload_video(youtube, video_data):
    video_file = video_data["videoFile"]
    if not os.path.exists(video_file):
        print(f"❌ Video file not found: {video_file}")
        return
    category_id = CATEGORY_MAP.get(video_data["categoryName"], "22")
    request_body = {
        "snippet": {
            "title": video_data["title"],
            "description": video_data["description"],
            "tags": video_data.get("tags", []),
            "categoryId": category_id,
        },
        "status": {"privacyStatus": video_data["privacyStatus"]},
    }
    if "publishAt" in video_data:
        request_body["status"]["publishAt"] = convert_ist_to_utc(video_data["publishAt"])
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
    video_id = response["id"]
    if "thumbnail" in video_data and os.path.exists(video_data["thumbnail"]):
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(video_data["thumbnail"])).execute()
    if "playlistName" in video_data:
        playlist_id = get_playlist_id(youtube, video_data["playlistName"])
        add_video_to_playlist(youtube, video_id, playlist_id)

def add_video_to_playlist(youtube, video_id, playlist_id):
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

if __name__ == "__main__":
    if not os.path.exists(CLIENT_SECRET_FILE) or not os.path.exists(METADATA_FILE):
        print("❌ Missing required files!")
        exit()
    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        metadata = json.load(file)
    youtube = get_authenticated_service()
    with ThreadPoolExecutor(max_workers=min(3, len(metadata["videos"]))) as executor:
        executor.map(lambda video: upload_video(youtube, video), metadata["videos"])
    print("✅ All videos uploaded successfully!")
