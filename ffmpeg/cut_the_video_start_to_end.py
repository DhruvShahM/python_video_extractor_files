import tkinter as tk
from tkinter import filedialog
import subprocess

def cut_video():
    root = tk.Tk()
    root.withdraw()  # Hide Tkinter window

    # Select input video file
    input_path = filedialog.askopenfilename(title="Select Video File", 
                                            filetypes=[("MP4 files", "*.mp4"), ("All Files", "*.*")])
    if not input_path:
        print("❌ No file selected. Exiting...")
        return

    # Select output video file
    output_path = filedialog.asksaveasfilename(title="Save Output Video As", 
                                               defaultextension=".mp4",
                                               filetypes=[("MP4 files", "*.mp4"), ("All Files", "*.*")])
    if not output_path:
        print("❌ No output file selected. Exiting...")
        return

    try:
        # Get video duration using ffprobe
        cmd_duration = ["ffprobe", "-i", input_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
        total_duration = float(subprocess.check_output(cmd_duration).decode().strip())

        print(f"✅ Video Loaded Successfully!")
        print(f"📌 Video Duration: {total_duration:.2f} seconds")

        # Ask user for start and end times
        start_time = float(input(f"Enter the start time in seconds (0 - {int(total_duration)}): "))
        end_time = float(input(f"Enter the end time in seconds ({start_time} - {int(total_duration)}): "))

        if start_time < 0 or end_time > total_duration or start_time >= end_time:
            print("❌ Invalid time range! Please enter valid values.")
            return

        # Cut video using ffmpeg
        print("⏳ Processing video... Please wait.")
        cmd_cut = [
            "ffmpeg", "-i", input_path, "-vf", f"select='not(between(t,{start_time},{end_time}))',setpts=N/FRAME_RATE/TB",
            "-af", f"aselect='not(between(t,{start_time},{end_time}))',asetpts=N/SR/TB", "-c:v", "libx264", "-c:a", "aac", output_path
        ]
        subprocess.run(cmd_cut, check=True)
        
        print(f"✅ Video saved successfully: {output_path}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

# Run the function
cut_video()
