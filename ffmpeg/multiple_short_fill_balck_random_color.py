import subprocess
import tkinter as tk
from tkinter import filedialog
import re
import sys
import time
import random
from colorama import Fore, Style, init
import os

init(autoreset=True)

def select_files(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilenames(title=title, filetypes=filetypes)

def select_folder(title):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title=title)

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

def generate_random_color():
    return "#" + "".join(random.choices("0123456789ABCDEF", k=6))

def convert_videos():
    input_files = select_files("Select Input Videos", [("MP4 Files", "*.mp4"), ("All Files", "*.*")])
    if not input_files:
        print(Fore.RED + "No input files selected.")
        return
    
    output_folder = select_folder("Select Output Folder")
    if not output_folder:
        print(Fore.RED + "No output folder selected.")
        return
    
    for input_file in input_files:
        print(Fore.CYAN + f"\nProcessing file: {input_file}")
        output_file = os.path.join(output_folder, os.path.basename(input_file))
        
        try:
            start_time = parse_time(input(Fore.YELLOW + "⏳ Enter start time (mm:ss or seconds): " + Style.RESET_ALL))
            duration = parse_time(input(Fore.YELLOW + "🎬 Enter duration of short video (mm:ss or seconds): " + Style.RESET_ALL))
        except ValueError as e:
            print(Fore.RED + f"❌ {e}")
            continue
        
        print(Fore.CYAN + "📏 Select Resolution:")
        print("1. 1080x1920 (Default)")
        print("2. 720x1280")
        print("3. 480x854")
        res_choice = input(Fore.YELLOW + "Enter choice (1-3): " + Style.RESET_ALL)
        resolutions = {"1": "1080:1920", "2": "720:1280", "3": "480:854"}
        resolution = resolutions.get(res_choice, "1080:1920")
        
        color_code = generate_random_color()
        print(Fore.MAGENTA + f"🎨 Randomly selected background color: {color_code}")
        
        command = [
            "ffmpeg",
            "-i", input_file,
            "-ss", str(start_time),
            "-t", str(duration),
            "-vf", f"scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2:color={color_code}",
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
    convert_videos()