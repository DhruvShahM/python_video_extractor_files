import tkinter as tk
from tkinter import filedialog
import ffmpeg
import os

# Function to select multiple videos
def select_multiple_videos():
    return filedialog.askopenfilenames(title="Select Multiple Videos", filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])

# Function to select one additional video
def select_single_video():
    return filedialog.askopenfilename(title="Select One Additional Video", filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])

# Function to select the output folder
def select_output_folder():
    return filedialog.askdirectory(title="Select Output Folder")

# Function to convert video to TS format for smooth merging
def convert_to_ts(video_path, output_ts):
    ffmpeg.input(video_path).output(output_ts, format="mpegts", vcodec="libx264", acodec="aac", strict="experimental").run(overwrite_output=True)

# Function to merge two videos properly
def merge_videos(video1, video2, output_path):
    # Extract original filename without extension
    original_filename = os.path.splitext(os.path.basename(video1))[0]
    ts1 = f"temp1.ts"
    ts2 = f"temp2.ts"

    # Convert videos to TS format
    convert_to_ts(video1, ts1)
    convert_to_ts(video2, ts2)

    # Define the output filename with "_merged" appended
    output_file = os.path.join(output_path, f"{original_filename}_merged.mp4")

    # Concatenate the videos
    ffmpeg.input(f"concat:{ts1}|{ts2}", format="mpegts").output(output_file, vcodec="copy", acodec="copy").run(overwrite_output=True)

    # Remove temporary files
    os.remove(ts1)
    os.remove(ts2)

    print(f"✅ Merged video saved: {output_file}")

# Main execution
root = tk.Tk()
root.withdraw()  # Hide the Tkinter window

selected_videos = select_multiple_videos()
if not selected_videos:
    print("❌ No videos selected!")
    exit()

single_video = select_single_video()
if not single_video:
    print("❌ No additional video selected!")
    exit()

output_folder = select_output_folder()
if not output_folder:
    print("❌ No output folder selected!")
    exit()

# Merge each selected video separately with the single selected video
for video in selected_videos:
    merge_videos(video, single_video, output_folder)

print("🎉 All videos merged successfully!")


# subscribe video path
# C:\Users\dhruv\OneDrive\Resueable_Videos\Shorts