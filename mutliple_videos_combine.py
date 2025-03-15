import os
import re
from tkinter import Tk, filedialog
from moviepy import VideoFileClip
from moviepy import concatenate_videoclips 

def extract_floating_number(filename):
    """Extract floating number from filename"""
    match = re.search(r"[-+]?\d*\.\d+|\d+", filename)
    return float(match.group()) if match else float('inf')

def select_videos():
    """Open file dialog to select multiple videos"""
    Tk().withdraw()  # Hide the root window
    file_paths = filedialog.askopenfilenames(title="Select Video Files",
                                             filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])
    return sorted(file_paths, key=extract_floating_number)

def merge_videos(video_files, output_filename="merged_output.mp4"):
    """Merge videos based on sorted order"""
    if not video_files:
        print("No videos selected.")
        return
    
    clips = [VideoFileClip(vid) for vid in video_files]
    final_video = concatenate_videoclips(clips, method="compose")
    
    final_video.write_videofile(output_filename, codec="h264_nvenc", fps=30)
    print(f"Videos merged successfully into {output_filename}")

if __name__ == "__main__":
    videos = select_videos()
    merge_videos(videos)
