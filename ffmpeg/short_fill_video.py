import subprocess
import tkinter as tk
from tkinter import filedialog, simpledialog
import re
import sys
import time
from colorama import Fore, Style, init

init(autoreset=True)  # Initialize colorama for colored output

def select_file(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title=title, filetypes=filetypes)

def save_file(title, defaultextension, filetypes):
    root = tk.Tk()
    root.withdraw()
    return filedialog.asksaveasfilename(title=title, defaultextension=defaultextension, filetypes=filetypes)

def parse_time(time_str):
    match = re.match(r'^(\d+):(\d{2})$', time_str)
    if match:
        minutes, seconds = map(int, match.groups())
        return minutes * 60 + seconds
    elif time_str.isdigit():
        return int(time_str)
    else:
        raise ValueError("Invalid time format! Use mm:ss or seconds.")

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

    background_file = select_file("Select Background Video", [("MP4 Files", "*.mp4"), ("All Files", "*.*")])
    if not background_file:
        print(Fore.RED + "No background video selected.")
        return

    output_file = save_file("Save Converted Video As", ".mp4", [("MP4 Files", "*.mp4")])
    if not output_file:
        print(Fore.RED + "No output file selected.")
        return

    try:
        start_time = parse_time(input(Fore.YELLOW + "⏳ Enter start time (mm:ss or seconds): " + Style.RESET_ALL))
        duration = parse_time(input(Fore.YELLOW + "🎬 Enter duration of short video (mm:ss or seconds): " + Style.RESET_ALL))
    except ValueError as e:
        print(Fore.RED + f"❌ {e}")
        return

    print(Fore.CYAN + "📏 Select Resolution:")
    print("1. 1080x1920 (Default)")
    print("2. 720x1280")
    print("3. 480x854")
    res_choice = input(Fore.YELLOW + "Enter choice (1-3): " + Style.RESET_ALL)
    resolutions = {"1": "1080:1920", "2": "720:1280", "3": "480:854"}
    resolution = resolutions.get(res_choice, "1080:1920")

    command = [
        "ffmpeg",
        "-stream_loop", "-1", "-i", background_file,  # Loop background video
        "-i", input_file,
        "-ss", str(start_time),
        "-t", str(duration),
        "-filter_complex", f"[0:v]scale={resolution}[bg];[1:v]scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2",
        "-c:v", "h264_nvenc",
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
        total_steps = 100
        for i in range(total_steps):
            time.sleep(0.1)  # Simulated progress
            print_progress_bar(i + 1, total_steps)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print(Fore.GREEN + f"\n✅ Converted video saved as: {output_file}")
        else:
            print(Fore.RED + "\n❌ Error during conversion:", stderr)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + "\n❌ FFMPEG Error:", e)
    except Exception as e:
        print(Fore.RED + "\n❌ Unexpected Error:", e)

if __name__ == "__main__":
    convert_video()
