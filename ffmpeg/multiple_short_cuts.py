import subprocess
import tkinter as tk
from tkinter import filedialog
import os

def select_file(title, filetypes):
    """ Open a file selection dialog """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    return filedialog.askopenfilename(title=title, filetypes=filetypes)

def select_folder(title):
    """ Open a folder selection dialog """
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title=title)

def convert_video():
    input_file = select_file("Select Input Video", [("MP4 Files", "*.mp4"), ("All Files", "*.*")])
    if not input_file:
        print("❌ No input file selected.")
        return
    
    output_folder = select_folder("Select Output Folder")
    if not output_folder:
        print("❌ No output folder selected.")
        return

    try:
        num_clips = int(input("🔢 How many clips do you want to cut? "))
        if num_clips <= 0:
            print("❌ Invalid number! Must be at least 1.")
            return
    except ValueError:
        print("❌ Invalid input! Please enter a number.")
        return

    resolution = "1080:1920"  # Mobile screen resolution

    for i in range(num_clips):
        print(f"\n✂️ Clip {i + 1}:")
        try:
            start_time = int(input("⏳ Enter start time (in seconds): "))
            end_time = int(input("🎬 Enter end time (in seconds): "))

            if end_time <= start_time:
                print("❌ End time must be greater than start time!")
                continue

            duration = end_time - start_time  # Calculate duration automatically
        except ValueError:
            print("❌ Invalid input! Please enter numbers only.")
            continue

        output_file = os.path.join(output_folder, f"clip_{i + 1}.mp4")

        command = [
            "ffmpeg",
            "-y",  # Overwrite output file if exists
            "-ss", str(start_time),  # Fast seek (before input)
            "-i", input_file,
            "-ss", "0",  # Precise seek (after input)
            "-t", str(duration),  # Use calculated duration
            "-vf", f"scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "h264_nvenc",  # More compatible encoder
            "-crf", "18",
            "-preset", "slow",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_file
        ]
        
        print(f"🚀 Processing Clip {i + 1}... Saving to: {output_file}")
        try:
            subprocess.run(command, check=True)
            print(f"✅ Clip {i + 1} saved successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error during conversion of Clip {i + 1}:", e)

# Run the script
convert_video()
