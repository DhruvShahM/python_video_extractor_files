import tkinter as tk
from tkinter import filedialog
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

def replace_audio(video_path, audio_path, output_path):
    # Load video file
    video = VideoFileClip(video_path)

    # Load new audio file
    new_audio = AudioFileClip(audio_path)

    # Set new audio to video
    video = video.with_audio(new_audio)  # Updated line

    # Write the output file
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")

# Open file dialog to choose video and audio files
def select_files():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    video_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("All files", "*.*")])
    audio_path = filedialog.askopenfilename(title="Select Audio File", filetypes=[("All files", "*.*")])

    if not video_path or not audio_path:
        print("File selection canceled.")
        return

    output_path = filedialog.asksaveasfilename(title="Save Output Video As", defaultextension=".mp4",
                                               filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])

    if not output_path:
        print("Output file selection canceled.")
        return

    replace_audio(video_path, audio_path, output_path)

# Run the file selection
select_files()
