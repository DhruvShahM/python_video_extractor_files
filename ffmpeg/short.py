import subprocess
import tkinter as tk
from tkinter import filedialog

def select_file(title, filetypes):
    """ Open a file selection dialog """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    return filedialog.askopenfilename(title=title, filetypes=filetypes)

def save_file(title, defaultextension, filetypes):
    """ Open a save file dialog """
    root = tk.Tk()
    root.withdraw()
    return filedialog.asksaveasfilename(title=title, defaultextension=defaultextension, filetypes=filetypes)

def convert_video():
    input_file = select_file("Select Input Video", [("MP4 Files", "*.mp4"), ("All Files", "*.*")])
    if not input_file:
        print("No input file selected.")
        return
    
    output_file = save_file("Save Converted Video As", ".mp4", [("MP4 Files", "*.mp4")])
    if not output_file:
        print("No output file selected.")
        return

    # User input for trimming the video
    try:
        start_time = int(input("⏳ Enter start time (in seconds): "))
        duration = int(input("🎬 Enter duration of short video (in seconds): "))
    except ValueError:
        print("❌ Invalid input! Please enter numbers only.")
        return

    resolution = "1080:1920"  # Mobile screen resolution
    
    command = [
        "ffmpeg",
        "-i", input_file,
        "-ss", str(start_time),  # Start time
        "-t", str(duration),  # Duration of the clip
        "-vf", f"scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "h264_nvenc",
        "-crf", "18",
        "-preset", "slow",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_file
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"✅ Converted video saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print("❌ Error during conversion:", e)

# Run the script
convert_video()
