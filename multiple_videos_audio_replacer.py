import os
import tkinter as tk
from tkinter import filedialog, simpledialog
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

def replace_audio(video_path, audio_path, output_path):
    try:
        video = VideoFileClip(video_path)
        new_audio = AudioFileClip(audio_path)
        video = video.with_audio(new_audio)
        video.write_videofile(output_path, codec="h264_nvenc", audio_codec="aac", fps=30)
        print(f"Processed: {os.path.basename(video_path)} -> {os.path.basename(audio_path)}")
    except Exception as e:
        print(f"Error processing {video_path}: {e}")

def select_files():
    root = tk.Tk()
    root.withdraw()

    # Allow MKV and MP4 videos
    video_paths = filedialog.askopenfilenames(title="Select Video Files", 
                                              filetypes=[("Video Files", "*.mkv;*.mp4"), ("MKV files", "*.mkv"), ("MP4 files", "*.mp4"), ("All files", "*.*")])
    # Allow WAV audio
    audio_paths = filedialog.askopenfilenames(title="Select Audio Files", 
                                              filetypes=[("WAV files", "*.wav"), ("All files", "*.*")])

    if not video_paths or not audio_paths:
        print("File selection canceled.")
        return

    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        print("Output folder selection canceled.")
        return

    # Ask user for output format (MKV or MP4)
    output_format = simpledialog.askstring("Output Format", "Enter output format (mp4/mkv):", initialvalue="mp4").strip().lower()
    if output_format not in ["mp4", "mkv"]:
        print("Invalid format selected. Defaulting to MP4.")
        output_format = "mp4"

    video_dict = {os.path.splitext(os.path.basename(v))[0]: v for v in video_paths}
    audio_dict = {os.path.splitext(os.path.basename(a))[0]: a for a in audio_paths}

    for name, video_path in video_dict.items():
        if name in audio_dict:
            audio_path = audio_dict[name]
            output_path = os.path.join(output_folder, f"{name}_output.{output_format}")
            replace_audio(video_path, audio_path, output_path)
        else:
            print(f"No matching audio found for {name}")

# Run the file selection
select_files()
