import os
import subprocess
from tkinter import Tk, filedialog
from PIL import Image

def select_video_files():
    """Open dialog to select multiple video files"""
    root = Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(
        title="Select Video Files",
        filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")]
    )
    root.destroy()
    return list(files)

def get_video_duration(video_path):
    """Get duration of video in seconds"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        return float(result.stdout.strip())
    except:
        return 5.0  # fallback duration

def extract_thumbnail(video_path, output_folder, preview=False):
    """Extract and save thumbnail at 20% mark"""
    filename = os.path.basename(video_path)
    name, _ = os.path.splitext(filename)
    thumbnail_path = os.path.join(output_folder, f"{name}_thumbnail.jpg")
    temp_path = os.path.join(output_folder, "temp_thumb.jpg")

    # Get duration
    duration = get_video_duration(video_path)
    timestamp = duration * 0.2

    # Extract thumbnail
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(timestamp), "-i", video_path,
        "-vframes", "1", "-q:v", "2", temp_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not os.path.exists(temp_path):
        print(f"❌ Failed to extract thumbnail from {filename}")
        return

    # Resize and save
    img = Image.open(temp_path).resize((1280, 720))
    img.save(thumbnail_path, "JPEG", quality=90)
    print(f"✅ Saved: {thumbnail_path}")

    if preview:
        img.show(title=filename)

    os.remove(temp_path)

def batch_generate_thumbnails(preview=False):
    """Main function to batch generate thumbnails"""
    video_files = select_video_files()
    if not video_files:
        print("No video files selected.")
        return

    output_folder = os.path.dirname(video_files[0])
    print(f"\n📁 Saving thumbnails to: {output_folder}\n")

    for video in video_files:
        extract_thumbnail(video, output_folder, preview)

if __name__ == "__main__":
    batch_generate_thumbnails(preview=False)  # Set preview=True to see thumbnails
