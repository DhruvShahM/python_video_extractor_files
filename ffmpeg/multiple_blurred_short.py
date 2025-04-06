import os
import subprocess
from tkinter import Tk, filedialog

# Hide the Tkinter root window
root = Tk()
root.withdraw()

# File selection dialog for multiple videos
file_paths = filedialog.askopenfilenames(
    title="Select video files",
    filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")]
)

# Output resolution
output_width = 1080
output_height = 1920

# FFmpeg binary paths
ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"  # Use full path if needed

# Blur filter
filter_complex = (
    "split=2[main][bg];"
    f"[bg]scale={output_width}:{output_height}:force_original_aspect_ratio=increase,"
    f"crop={output_width}:{output_height},boxblur=10:1[blurred];"
    "[blurred][main]overlay=(W-w)/2:(H-h)/2"
)
# filter_complex = (
#     "split=2[main][blurred];"
#     "[blurred]scale=1080:1920:force_original_aspect_ratio=increase,"
#     "crop=1080:1920,"
#     "gblur=sigma=60,boxblur=20[bg];"
#     "[main]scale=-1:ih[fg];"
#     "[bg][fg]overlay=(W-w)/2:(H-h)/2"
# )
# filter_complex = (
#     "split=2[main][blurred];"
#     "[blurred]scale=1080:1920:force_original_aspect_ratio=increase,"
#     "crop=1080:1920,"
#     "gblur=sigma=60,boxblur=20[bg];"
#     "[main]scale=w=iw*0.85:h=-1,"
#     "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black[fg];"
#     "[bg][fg]overlay=0:0"
# )








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

# Process each video
for input_path in file_paths:
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        continue

    duration_seconds = get_video_duration(input_path)
    if duration_seconds is None:
        continue

    # Set max_duration based on full video length (e.g., half the original duration or up to 60 seconds)
    max_duration = int(duration_seconds) # customize as needed

    input_dir, input_file = os.path.split(input_path)
    filename, ext = os.path.splitext(input_file)
    output_file = os.path.join(input_dir, f"{filename}_short.mp4")

    command = [
        ffmpeg_path,
        "-i", input_path,
        "-t", str(max_duration),
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-y",  # overwrite without asking
        output_file
    ]

    print(f"🎬 Processing: {input_file} → {filename}_short.mp4 (duration: {max_duration}s)")
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Saved: {output_file}\n")
    else:
        print(f"❌ Error processing {input_file}:\n{result.stderr}\n")
