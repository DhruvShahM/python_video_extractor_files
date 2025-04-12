import os
import subprocess
from tkinter import Tk, filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed

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
ffprobe_path = "ffprobe"

# Centering filter
filter_complex = (
    f"scale={output_width}:-1,setsar=1,pad={output_width}:{output_height}:(ow-iw)/2:(oh-ih)/2"
)

def get_video_duration(input_path):
    """Get video duration in seconds using ffprobe."""
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
        return None

def process_video(input_path):
    """Process a single video: auto-edit -> extract audio -> pad -> save final."""
    if not os.path.exists(input_path):
        return f"❌ File not found: {input_path}"

    filename_base = os.path.splitext(os.path.basename(input_path))[0]
    input_dir = os.path.dirname(input_path)

    auto_edited_video = os.path.join(input_dir, f"{filename_base}_edited.mp4")
    temp_audio = os.path.join(input_dir, f"{filename_base}_edited.wav")
    final_output = os.path.join(input_dir, f"{filename_base}_final.mp4")

    # === Step 1: Auto-edit video ===
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
        print(f"✅ Auto-edited video created: {auto_edited_video}")
    except subprocess.CalledProcessError as e:
        return f"❌ Auto-editing failed for {input_path}: {e}"

    # === Step 2: Extract audio ===
    extract_audio_cmd = [
        ffmpeg_path, "-i", auto_edited_video,
        "-vn",
        "-acodec", "pcm_s16le",
        temp_audio
    ]
    try:
        subprocess.run(extract_audio_cmd, check=True)
        print(f"🎧 Extracted audio to: {temp_audio}")
    except subprocess.CalledProcessError as e:
        return f"❌ Audio extraction failed for {input_path}: {e}"

    # === Step 3: Center and pad video ===
    duration = get_video_duration(auto_edited_video)
    if duration is None:
        return f"❌ Could not get duration for {auto_edited_video}"

    ffmpeg_center_cmd = [
        ffmpeg_path,
        "-i", auto_edited_video,
        "-t", str(int(duration)),
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-y",
        final_output
    ]

    print(f"🎬 Centering and padding: {final_output}")
    result = subprocess.run(ffmpeg_center_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Final video saved: {final_output}")
    else:
        return f"❌ Error during final processing:\n{result.stderr}"

    # === Step 4: Clean up temporary audio ===
    try:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
            print(f"🧹 Temp audio deleted: {temp_audio}")
    except Exception as e:
        print(f"⚠️ Could not delete temp audio: {e}")

    return f"🎉 Finished: {input_path}"

# === Run all processing tasks in parallel ===
if file_paths:
    max_threads = min(4, len(file_paths))  # Adjust based on your system
    print(f"🚀 Starting batch processing with {max_threads} threads...\n")

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(process_video, path) for path in file_paths]

        for future in as_completed(futures):
            print(future.result())

    print("\n✅ All videos processed.")
else:
    print("⚠️ No files selected.")
