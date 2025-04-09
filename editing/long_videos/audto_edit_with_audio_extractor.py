import subprocess
import tkinter as tk
from tkinter import filedialog
import os

def process_video():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[("Video Files", "*.mkv *.mp4 *.mov *.avi *.flv")]
    )

    if not file_path:
        print("No file selected. Exiting...")
        return

    output_video = file_path.rsplit(".", 1)[0] + "_edited.mp4"
    output_audio = output_video.rsplit(".", 1)[0] + ".wav"

    # Step 1: Auto-edit video
    command = [
        "auto-editor", file_path,
        "-o", output_video,
        "--no-open",
        "--frame-rate", "30",
        "--silent-speed", "99999"
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Final video exported: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error during video editing: {e}")
        return

    # Step 2: Extract audio using ffmpeg
    ffmpeg_command = [
        "ffmpeg", "-i", output_video,
        "-vn",
        "-acodec", "pcm_s16le",
        output_audio
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Audio extracted: {output_audio}")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        return

    # Step 3: Clean up the WAV file
    try:
        if os.path.exists(output_audio):
            os.remove(output_audio)
            print(f"Temporary audio file deleted: {output_audio}")
    except Exception as e:
        print(f"Error deleting WAV file: {e}")

# Run
process_video()
