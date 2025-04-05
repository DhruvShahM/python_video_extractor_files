import tkinter as tk
from tkinter import filedialog
import ffmpeg
import os

def select_video():
    file_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video Files", "*.mp4;*.mkv;*.avi;*.mov")])
    video_entry.delete(0, tk.END)
    video_entry.insert(0, file_path)

def select_audio():
    file_path = filedialog.askopenfilename(title="Select Audio File", filetypes=[("Audio Files", "*.mp3;*.wav;*.aac")])
    audio_entry.delete(0, tk.END)
    audio_entry.insert(0, file_path)

def merge_audio_video():
    video_path = video_entry.get()
    audio_path = audio_entry.get()
    
    if not video_path or not audio_path:
        status_label.config(text="Please select both video and audio files.")
        return
    
    output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 File", "*.mp4")])
    if not output_path:
        return
    
    try:
        input_video = ffmpeg.input(video_path)
        input_audio = ffmpeg.input(audio_path)
        
        ffmpeg.output(
            input_video, input_audio, output_path, 
            vcodec='libx264', acodec='aac', audio_bitrate='128k', ar='44100', 
            movflags='+faststart', shortest=None
        ).run()
        
        status_label.config(text=f"Merging complete. Saved as: {output_path}")
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}")

root = tk.Tk()
root.title("Audio-Video Merger")

# Video selection
video_label = tk.Label(root, text="Select Video:")
video_label.pack()
video_entry = tk.Entry(root, width=50)
video_entry.pack()
video_button = tk.Button(root, text="Browse", command=select_video)
video_button.pack()

# Audio selection
audio_label = tk.Label(root, text="Select Audio:")
audio_label.pack()
audio_entry = tk.Entry(root, width=50)
audio_entry.pack()
audio_button = tk.Button(root, text="Browse", command=select_audio)
audio_button.pack()

# Merge button
merge_button = tk.Button(root, text="Merge Audio with Video", command=merge_audio_video)
merge_button.pack()

# Status label
status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()