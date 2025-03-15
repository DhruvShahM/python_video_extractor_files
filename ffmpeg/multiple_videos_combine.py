import os
import re
from tkinter import Tk, filedialog

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

def merge_videos_ffmpeg(video_files):
    """Merge videos using FFmpeg with h264_nvenc while preserving quality"""
    if not video_files:
        print("No videos selected.")
        return

    output_folder = choose_output_folder()
    output_filename = os.path.join(output_folder, "merged_output2.mp4").replace("\\", "/")

    list_file = os.path.join(output_folder, "video_list.txt").replace("\\", "/")
    
    with open(list_file, "w", encoding="utf-8") as f:
        for vid in video_files:
            f.write(f"file '{vid.replace('\\', '/')}\n")
    
    ffmpeg_cmd = (
        f"ffmpeg -f concat -safe 0 -i \"{list_file}\" -vf scale=1920:1080 "
        f"-c:v h264_nvenc -preset slow -cq 18 -c:a aac -b:a 320k \"{output_filename}\""
    )
    
    os.system(ffmpeg_cmd)
    print(f"Videos merged successfully into {output_filename}")

if __name__ == "__main__":
    videos = select_videos()
    merge_videos_ffmpeg(videos)
