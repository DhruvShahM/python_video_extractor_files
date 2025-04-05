import subprocess
import tkinter as tk
from tkinter import filedialog
import sys
import time
from colorama import Fore, Style, init

init(autoreset=True)

def select_file(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title=title, filetypes=filetypes)

def save_file(title, defaultextension, filetypes):
    root = tk.Tk()
    root.withdraw()
    return filedialog.asksaveasfilename(title=title, defaultextension=defaultextension, filetypes=filetypes)

def print_progress_bar(iteration, total, length=50):
    percent = (iteration / total) * 100
    bar = "█" * int(length * (iteration / total)) + "-" * (length - int(length * (iteration / total)))
    sys.stdout.write(f"\r{Fore.GREEN}Processing: |{bar}| {percent:.2f}% Complete {Style.RESET_ALL}")
    sys.stdout.flush()

def convert_video():
    input_file = select_file("Select Input Video", [("MP4 Files", "*.mp4"), ("All Files", "*.*")])
    if not input_file:
        print(Fore.RED + "No input file selected.")
        return

    output_file = save_file("Save Converted Video As", ".mp4", [("MP4 Files", "*.mp4")])
    if not output_file:
        print(Fore.RED + "No output file selected.")
        return

    print(Fore.CYAN + "🎬 Converting to vertical short with proper blurred background...")

    short_duration_seconds = 60  # Modify if needed

    filter_complex = (
        "split=2[main][bg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=10:1[blurred];"
        "[blurred][main]overlay=(W-w)/2:(H-h)/2"
    )


    command = [
        "ffmpeg",
        "-i", input_file,
        "-t", str(short_duration_seconds),
        "-vf", filter_complex,
        "-c:v", "h264_nvenc",  # Use "libx264" if NVENC not available
        "-crf", "18",
        "-preset", "slow",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_file
    ]

    try:
        print(Fore.BLUE + "🚀 Starting video conversion...")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for i in range(100):
            time.sleep(0.05)
            print_progress_bar(i + 1, 100)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print(Fore.GREEN + f"\n✅ Converted short video saved as: {output_file}")
        else:
            print(Fore.RED + "\n❌ Error during conversion:\n" + stderr)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + "\n❌ FFMPEG Error:", e)
    except Exception as e:
        print(Fore.RED + "\n❌ Unexpected Error:", e)

if __name__ == "__main__":
    convert_video()
