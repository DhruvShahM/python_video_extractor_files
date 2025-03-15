import subprocess
import tkinter as tk
from tkinter import filedialog

def enhance_audio(input_file: str, output_file: str):
    """
    Enhance a video's audio to produce a podcast-like quality using FFmpeg's anlmdn and equalization filters.
    :param input_file: Path to the input video file.
    :param output_file: Path to the output video file with improved audio.
    """
    command = [
        "ffmpeg", "-i", input_file,
        "-af", "anlmdn=s=7:p=0.02,acompressor=ratio=3:attack=5:release=50,volume=3dB,aresample=48000",
        "-c:v", "copy",  # Copy video stream without re-encoding
        "-c:a", "aac", "-b:a", "192k",  # Output audio codec and bitrate
        output_file
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Enhanced podcast-like video saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during enhancement: {e}")

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select Input Video File", filetypes=[("Video Files", "*.mp4;*.mkv;*.avi;*.mov")])
    return file_path

def save_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(title="Save Output Video File", defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4"), ("MKV Video", "*.mkv"), ("AVI Video", "*.avi"), ("MOV Video", "*.mov")])
    return file_path

# File selection dialogs
input_video = select_file()
if input_video:
    output_video = save_file()
    if output_video:
        enhance_audio(input_video, output_video)
