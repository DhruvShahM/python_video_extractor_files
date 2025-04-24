import os
import subprocess
from tkinter import Tk, filedialog

# Hide the Tkinter root window
root = Tk()
root.withdraw()

# File selection dialog for multiple videos
file_paths = filedialog.askopenfilenames(
    title="Select video files",
    filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv *.flv")]
)

# Output resolution
output_width = 1080
output_height = 1920

# FFmpeg binary paths
ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"  # Use full path if needed

# Filter for centering
filter_complex = (
    f"scale={output_width}:-1,setsar=1,pad={output_width}:{output_height}:(ow-iw)/2:(oh-ih)/2"
)

def get_video_duration(input_path):
    """Returns duration in seconds using ffprobe"""
    try:
        result = subprocess.run(
            [ffprobe_path, "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"❌ Could not get duration for {input_path}: {e}")
        return None

for input_path in file_paths:
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        continue

    # === Step 1: Auto-edit video ===
    filename_base = os.path.splitext(os.path.basename(input_path))[0]
    input_dir = os.path.dirname(input_path)
    auto_edited_video = os.path.join(input_dir, f"{filename_base}_edited.mp4")
    temp_audio = os.path.join(input_dir, f"{filename_base}_edited.wav")

    auto_edit_cmd = [
        "auto-editor", input_path,
        "-o", auto_edited_video,
        "--no-open",
        "--frame-rate", "30",
        "--silent-speed", "99999"
    ]

    print(f"⚙️ Auto-editing: {input_path}")
    try:
        subprocess.run(auto_edit_cmd, check=True)
        print(f"✅ Auto-edited video: {auto_edited_video}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during auto-editing: {e}")
        continue

    # === Step 2: Extract audio (optional cleanup) ===
    extract_audio_cmd = [
        ffmpeg_path, "-i", auto_edited_video,
        "-vn",
        "-acodec", "pcm_s16le",
        temp_audio
    ]

    try:
        subprocess.run(extract_audio_cmd, check=True)
        print(f"🎧 Audio extracted (temp): {temp_audio}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error extracting audio: {e}")
        continue

    # === Step 3: Center and pad the video ===
    duration_seconds = get_video_duration(auto_edited_video)
    if duration_seconds is None:
        continue

    max_duration = int(duration_seconds)
    final_output = os.path.join(input_dir, f"{filename_base}_final.mp4")

    ffmpeg_center_cmd = [
        ffmpeg_path,
        "-i", auto_edited_video,
        "-t", str(max_duration),
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-y",
        final_output
    ]

    print(f"🎬 Processing centered video: {final_output}")
    result = subprocess.run(ffmpeg_center_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Final video saved: {final_output}")
    else:
        print(f"❌ Error processing final video:\n{result.stderr}")

    # === Step 4: Clean up audio ===
    try:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
            print(f"🧹 Deleted temp audio: {temp_audio}")
    except Exception as e:
        print(f"⚠️ Error deleting temp audio: {e}")

    print("--------------------------------------------------")
