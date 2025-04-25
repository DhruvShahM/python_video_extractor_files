import os
import tkinter as tk
from tkinter import filedialog, simpledialog
import subprocess

def replace_audio(video_path, audio_path, output_path):
    try:
        command = [
            "ffmpeg", "-i", video_path, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-strict", "experimental",
            "-map", "0:v:0", "-map", "1:a:0", output_path
        ]
        subprocess.run(command, check=True)
        print(f"Processed: {os.path.basename(video_path)} -> {os.path.basename(audio_path)}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {video_path}: {e}")

def select_files():
    root = tk.Tk()
    root.withdraw()

    video_paths = filedialog.askopenfilenames(title="Select Video Files", 
                                              filetypes=[("Video Files", "*.mkv;*.mp4"), ("MKV files", "*.mkv"), ("MP4 files", "*.mp4"), ("All files", "*.*")])
    audio_paths = filedialog.askopenfilenames(title="Select Audio Files", 
                                              filetypes=[("WAV files", "*.wav"), ("All files", "*.*")])

    if not video_paths or not audio_paths:
        print("File selection canceled.")
        return

    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        print("Output folder selection canceled.")
        return

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
