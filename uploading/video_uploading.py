import os
import json
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# Constants
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = "C:/Users/dhruv/Videos/Video_Extractor_Python_Files/python_video_extractor_files/uploading/client_secret.json"
METADATA_FILE = "C:/Users/dhruv/Videos/Video_Extractor_Python_Files/python_video_extractor_files/uploading/metadata.json"

def get_authenticated_service():
    """Authenticate and return a YouTube API service instance."""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

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

    print(f"✅ Video Uploaded Successfully: {video_data['title']} (ID: {response['id']})\n")

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
