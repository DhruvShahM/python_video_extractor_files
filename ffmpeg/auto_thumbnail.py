import os
import subprocess
from tkinter import Tk, filedialog, Label
from PIL import Image, ImageTk

def select_video_file():
    """Open dialog to select a single video file"""
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")]
    )
    root.destroy()
    return file_path

def show_youtube_thumbnail(video_path):
    """Extract and show a YouTube-optimized thumbnail"""
    thumbnail_path = "youtube_thumbnail.jpg"

    try:
        # Get video duration using ffprobe
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        duration = float(result.stdout.strip())
        timestamp = duration * 0.2  # 20% into the video
    except Exception as e:
        print("Failed to get duration, defaulting to 5s:", e)
        timestamp = 5

    # Extract thumbnail using ffmpeg
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path,
        "-vframes", "1", "-q:v", "2", "temp_thumb.jpg"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not os.path.exists("temp_thumb.jpg"):
        print("❌ Thumbnail was not created.")
        return

    # Resize to 1280x720 for YouTube
    img = Image.open("temp_thumb.jpg").resize((1280, 720))
    img.save(thumbnail_path, "JPEG", quality=90)

    # Show the thumbnail
    root = Tk()
    root.title("YouTube Thumbnail Preview (1280x720)")
    tk_img = ImageTk.PhotoImage(img.resize((640, 360)))  # smaller preview
    lbl = Label(root, image=tk_img)
    lbl.image = tk_img
    lbl.pack()
    root.mainloop()

    # Clean up temp
    os.remove("temp_thumb.jpg")
    print(f"✅ YouTube thumbnail saved as: {thumbnail_path}")

if __name__ == "__main__":
    video = select_video_file()
    if video:
        show_youtube_thumbnail(video)
    else:
        print("No video selected.")
