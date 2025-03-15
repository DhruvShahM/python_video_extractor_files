import subprocess
import tkinter as tk
from tkinter import filedialog

def select_file(file_type):
    """Opens a file dialog to select a file."""
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    if file_type == "input":
        file_path = filedialog.askopenfilename(title="Select Input Video",
                                               filetypes=[("Video Files", "*.mp4;*.mkv;*.avi;*.mov")])
    else:
        file_path = filedialog.asksaveasfilename(title="Save Output Video As",
                                                 defaultextension=".mp4",
                                                 filetypes=[("MP4 Video", "*.mp4")])
    return file_path

def remove_noise():
    """Removes noise from the selected video file using FFmpeg."""
    input_video = select_file("input")
    if not input_video:
        print("No input file selected.")
        return

    output_video = select_file("output")
    if not output_video:
        print("No output file selected.")
        return

    command = [
        "ffmpeg",
        "-i", input_video,          # Input video
        "-c:v", "copy",             # Copy video stream without re-encoding
        "-af", "afftdn",            # Apply audio noise removal filter
        output_video                 # Output file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Noise removed successfully! Saved as: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Run the function
remove_noise()
