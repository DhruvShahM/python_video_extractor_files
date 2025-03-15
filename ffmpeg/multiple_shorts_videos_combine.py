import subprocess
import tkinter as tk
from tkinter import filedialog
import os

def select_files(title, filetypes):
    """ Open a file selection dialog for multiple files """
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilenames(title=title, filetypes=filetypes)

def save_file(title, defaultextension, filetypes):
    """ Open a save file dialog """
    root = tk.Tk()
    root.withdraw()
    return filedialog.asksaveasfilename(title=title, defaultextension=defaultextension, filetypes=filetypes)

def merge_videos():
    # Select multiple video clips to merge
    input_files = select_files("Select Video Clips to Merge", [("MP4 Files", "*.mp4")])
    if not input_files:
        print("❌ No clips selected.")
        return

    # Sort clips in ascending order
    sorted_files = sorted(input_files)

    # Choose output file
    output_file = save_file("Save Merged Video As", ".mp4", [("MP4 Files", "*.mp4")])
    if not output_file:
        print("❌ No output file selected.")
        return

    # Create a temporary text file listing all video clips
    list_file = "file_list.txt"
    with open(list_file, "w") as f:
        for file in sorted_files:
            f.write(f"file '{file}'\n")

    # FFmpeg command to merge videos
    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_file
    ]

    print(f"🚀 Merging {len(sorted_files)} clips... Saving to: {output_file}")
    
    try:
        subprocess.run(command, check=True)
        print(f"✅ Merged video saved successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during merging: {e}")
    finally:
        os.remove(list_file)  # Cleanup temporary file

# Run the script
merge_videos()
