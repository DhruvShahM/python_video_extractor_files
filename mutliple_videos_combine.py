import os
import re
from tkinter import Tk, filedialog
from moviepy import VideoFileClip, concatenate_videoclips

def extract_floating_number(filename):
    """Extract floating number from filename"""
    match = re.search(r"[-+]?\d*\.\d+|\d+", filename)
    return float(match.group()) if match else float('inf')

def select_videos():
    """Open file dialog to select multiple videos"""
    Tk().withdraw()
    file_paths = filedialog.askopenfilenames(title="Select Video Files",
                                           filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])
    return sorted(file_paths, key=extract_floating_number)

def choose_output_folder():
    """Open file dialog to select output folder"""
    Tk().withdraw()
    folder_selected = filedialog.askdirectory(title="Select Output Folder")
    return folder_selected if folder_selected else os.getcwd()

def merge_videos(video_files):
    """Merge videos based on sorted order with resolution 1920x1080"""
    if not video_files:
        print("No videos selected.")
        return

    output_folder = choose_output_folder()
    output_filename = os.path.join(output_folder, "merged_output.mp4")

    clips = [VideoFileClip(vid).resized(width=1920, height=1080) for vid in video_files]  # Corrected resizing
    final_video = concatenate_videoclips(clips, method="compose")

    final_video.write_videofile(output_filename, codec="h264_nvenc", fps=30)
    print(f"Videos merged successfully into {output_filename}")

if __name__ == "__main__":
    videos = select_videos()
    merge_videos(videos)