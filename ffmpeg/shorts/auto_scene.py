import os
import re
import subprocess
from tkinter import Tk, filedialog

# Hide Tkinter root window
root = Tk()
root.withdraw()

# File selection dialog for multiple videos
file_paths = filedialog.askopenfilenames(
    title="Select video files",
    filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")]
)

# Output resolution for vertical video
output_width = 1080
output_height = 1920

# FFmpeg binary paths
ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"  # Provide full path if needed

# Centering and padding filter
filter_complex = (
    f"scale={output_width}:-1,setsar=1,pad={output_width}:{output_height}:(ow-iw)/2:(oh-ih)/2"
)

def get_video_duration(input_path):
    """Get video duration in seconds using ffprobe"""
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

def detect_scene_changes(input_path, threshold=0.4):
    """Returns a list of scene change timestamps in seconds"""
    try:
        result = subprocess.run(
            [
                ffmpeg_path,
                "-i", input_path,
                "-filter_complex", f"select='gt(scene,{threshold})',metadata=print",
                "-an", "-f", "null", "-"
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        timestamps = []
        for line in result.stderr.splitlines():
            match = re.search(r"pts_time:([\d.]+)", line)
            if match:
                timestamps.append(float(match.group(1)))
        return timestamps
    except Exception as e:
        print(f"❌ Error detecting scene changes: {e}")
        return []

# Process each selected video
for input_path in file_paths:
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        continue

    print(f"📼 Processing file: {input_path}")
    duration_seconds = get_video_duration(input_path)
    if duration_seconds is None:
        continue

    scene_timestamps = detect_scene_changes(input_path)
    if not scene_timestamps:
        print("⚠️ No scene changes detected, skipping...")
        continue

    # Add video end as final timestamp
    scene_timestamps.append(duration_seconds)

    input_dir, input_file = os.path.split(input_path)
    filename, ext = os.path.splitext(input_file)

    for i in range(len(scene_timestamps) - 1):
        start = scene_timestamps[i]
        end = scene_timestamps[i + 1]
        segment_duration = end - start

        output_file = os.path.join(input_dir, f"{filename}_scene_{i+1}.mp4")

        command = [
            ffmpeg_path,
            "-ss", str(start),
            "-i", input_path,
            "-t", str(segment_duration),
            "-vf", filter_complex,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            output_file
        ]

        print(f"🎬 Scene {i+1}: {start:.2f}s → {end:.2f}s")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Saved: {output_file}\n")
        else:
            print(f"❌ Error processing scene {i+1}:\n{result.stderr}\n")
