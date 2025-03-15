import os
import moviepy as mp
from tkinter import Tk, filedialog

def extract_audio_from_videos():
    # Open file dialog to select multiple videos
    Tk().withdraw()  # Hide the root window
    video_files = filedialog.askopenfilenames(title="Select Video Files", filetypes=[("Video Files", "*.mp4;*.mkv;*.avi;*.mov;*.flv")])
    
    if not video_files:
        print("No files selected.")
        return

    # Ask user to select output folder
    output_dir = filedialog.askdirectory(title="Select Output Folder")
    if not output_dir:
        print("No output folder selected.")
        return

    for video_path in video_files:
        try:
            video = mp.VideoFileClip(video_path)
            output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(video_path))[0] + ".wav")
            video.audio.write_audiofile(output_file, codec='pcm_s16le')
            print(f"Extracted: {output_file}")
        except Exception as e:
            print(f"Error processing {video_path}: {e}")

if __name__ == "__main__":
    extract_audio_from_videos()
