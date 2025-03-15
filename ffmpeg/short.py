import subprocess
import tkinter as tk
from tkinter import filedialog

def convert_to_mobile_short(input_file, output_file, start_time=0, duration=30, resolution="720x1280"):
    """
    Converts an original video to a mobile-friendly short video (9:16 format) using FFmpeg.
    
    :param input_file: Path to the original video file.
    :param output_file: Path to save the short video.
    :param start_time: Start time (in seconds) for the short video.
    :param duration: Duration (in seconds) for the short video.
    :param resolution: Resolution of the output video (default: 720x1280).
    """
    width, height = resolution.split("x")

    # FFmpeg command to convert to vertical video (9:16)
    command = [
        "ffmpeg",
        "-i", input_file,             # Input video file
        "-ss", str(start_time),       # Start time
        "-t", str(duration),          # Duration
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264",            # Video codec
        "-crf", "23",                 # Quality
        "-preset", "fast",            # Encoding speed
        "-c:a", "aac",                # Audio codec
        "-b:a", "128k",               # Audio bitrate
        "-y",                         # Overwrite output
        output_file
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"✅ Mobile short video saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")

# Initialize Tkinter
root = tk.Tk()
root.withdraw()  # Hide main window

# File selection dialogs
input_video = filedialog.askopenfilename(title="Select the Original Video", filetypes=[("MP4 files", "*.mp4"), ("All Files", "*.*")])
if not input_video:
    print("❌ No file selected. Exiting...")
    exit()

output_video = filedialog.asksaveasfilename(title="Save Short Video As", defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
if not output_video:
    print("❌ No output file specified. Exiting...")
    exit()

# User inputs
start_time = int(input("⏳ Enter start time (in seconds): "))
duration = int(input("🎬 Enter duration of short video (in seconds): "))
resolution = input("📱 Enter resolution for mobile video (default: 720x1280): ") or "720x1280"

# Convert video to mobile-friendly short
convert_to_mobile_short(input_video, output_video, start_time, duration, resolution)
