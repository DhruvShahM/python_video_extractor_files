import ffmpeg
import os
import tkinter as tk
from tkinter import filedialog

def select_files():
    """Open file dialog to select multiple video files."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    files = filedialog.askopenfilenames(title="Select Video Files", filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")])
    return list(files)

def select_output_folder():
    """Open folder dialog to select output folder."""
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Output Folder")
    return folder

def merge_videos(video_files, output_folder):
    if not video_files:
        print("No video files selected. Exiting...")
        return

    if not output_folder:
        print("No output folder selected. Exiting...")
        return

    output_file = os.path.join(output_folder, "merged_video.mp4")

    list_file = os.path.join(output_folder, "input_videos.txt")
    
    with open(list_file, "w") as f:
        for video in video_files:
            f.write(f"file '{video}'\n")

    try:
        ffmpeg.input(list_file, format='concat', safe=0).output(output_file, c='copy').run(overwrite_output=True)
        print(f"Videos merged successfully into {output_file}")
    except ffmpeg.Error as e:
        print("Error merging videos:", e)
    
    os.remove(list_file)

if __name__ == "__main__":
    video_list = select_files()
    output_folder = select_output_folder()
    merge_videos(video_list, output_folder)
