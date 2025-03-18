import subprocess
import tkinter as tk
from tkinter import filedialog
import os

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

    # Define output paths
    output_video = file_path.rsplit(".", 1)[0] + "_edited.mp4"
    output_audio = file_path.rsplit(".", 1)[0] + ".wav"

    # Step 1: Auto-edit the video
    command = [
        "auto-editor", file_path, "-o", output_video, "--export", "default"
    ]

    try:
        subprocess.run(command, check=True)
        if not os.path.exists(output_video):
            print(f"Error: Edited video was not created: {output_video}")
            return
        print(f"Final video exported successfully: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error during video editing: {e}")
        return

    # Step 2: Extract audio only if the video file exists
    if os.path.exists(output_video):
        audio_command = [
            "ffmpeg", "-y", "-i", output_video, "-vn", "-acodec", "pcm_s16le", output_audio
        ]

        try:
            subprocess.run(audio_command, check=True)
            if os.path.exists(output_audio):
                print(f"Audio extracted and saved as: {output_audio}")
            else:
                print("Error: Audio extraction failed.")
        except subprocess.CalledProcessError as e:
            print(f"Error during audio extraction: {e}")
    else:
        print("Skipping audio extraction because the edited video was not found.")

# Run the function
process_video()
