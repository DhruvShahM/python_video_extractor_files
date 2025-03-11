import tkinter as tk
from tkinter import filedialog
import subprocess
import os

# Function to choose a single file
def choose_file(prompt):
    tk.Tk().withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title=prompt, 
        filetypes=[("Video Files", "*.mp4;*.mkv"), ("MP4 Files", "*.mp4"), ("MKV Files", "*.mkv"), ("All Files", "*.*")]
    )
    return file_path

# Function to choose the save location
def choose_save_location():
    tk.Tk().withdraw()
    folder_selected = filedialog.askdirectory(title="Select a folder to save the merged video")
    return folder_selected

# Function to get video resolution using FFmpeg
def get_video_resolution(video_path):
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0", 
        "-show_entries", "stream=width,height", "-of", "csv=p=0", video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        width, height = map(int, result.stdout.strip().split(','))
        return width, height
    return None, None

# Ask for the first video
video1_path = choose_file("Select the first video file")
if not video1_path:
    print("No file selected. Exiting.")
    exit()

# Ask for the second video
video2_path = choose_file("Select the second video file")
if not video2_path:
    print("No file selected. Exiting.")
    exit()

# Ask for the destination folder
save_folder = choose_save_location()
if not save_folder:
    print("No folder selected. Exiting.")
    exit()

# Define output file path
output_file = os.path.join(save_folder, "merged_output.mp4")

# Get the resolution of the first video (to match others)
target_width, target_height = get_video_resolution(video1_path)

if not target_width or not target_height:
    print("Error reading video resolution. Exiting.")
    exit()

# Temporary resized second video
temp_video2 = os.path.join(save_folder, "temp_resized.mp4")

# Resize second video to match the first video's resolution
resize_cmd = [
    "ffmpeg", "-i", video2_path, "-vf", f"scale={target_width}:{target_height}", "-c:a", "copy", temp_video2
]

try:
    subprocess.run(resize_cmd, check=True)
    print(f"Resized second video to {target_width}x{target_height}")
except subprocess.CalledProcessError as e:
    print(f"Error resizing video: {e}")
    exit()

# Run FFmpeg command to merge videos
merge_cmd = [
    "ffmpeg", "-i", video1_path, "-i", temp_video2, "-filter_complex",
    "[0:v:0][0:a:0][1:v:0][1:a:0]concat=n=2:v=1:a=1[outv][outa]",
    "-map", "[outv]", "-map", "[outa]", output_file
]

try:
    subprocess.run(merge_cmd, check=True)
    print(f"Videos merged successfully into {output_file}!")
except subprocess.CalledProcessError as e:
    print(f"Error merging videos: {e}")

# Remove the temporary resized video
if os.path.exists(temp_video2):
    os.remove(temp_video2)
