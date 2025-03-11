import subprocess
import tkinter as tk
from tkinter import filedialog
from moviepy.video.io.VideoFileClip import VideoFileClip

def process_video():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Open file dialog to select a video file
    file_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[("Video Files", "*.mkv *.mp4 *.mov *.avi *.flv")]
    )

    if not file_path:
        print("No file selected. Exiting...")
        return

    # Step 1: Auto-edit the video
    output_video = file_path.rsplit(".", 1)[0] + "_edited.mp4"
    command = ["auto-editor", file_path, "-o", output_video]

    try:
        subprocess.run(command, check=True)
        print(f"Final video exported successfully: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error during video editing: {e}")
        return

    # Step 2: Extract audio from the edited video
    output_audio = output_video.rsplit(".", 1)[0] + ".wav"
    
    try:
        video = VideoFileClip(output_video)  # Load the edited video
        audio = video.audio
        audio.write_audiofile(output_audio, codec="pcm_s16le")
        print(f"Audio extracted and saved as: {output_audio}")
        video.close()
    except Exception as e:
        print(f"Error during audio extraction: {e}")

# Run the function
process_video()
