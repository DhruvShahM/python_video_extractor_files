import tkinter as tk
from tkinter import filedialog
import subprocess

def cut_video_before_time():
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
        result = subprocess.run([
            "ffprobe", "-i", input_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"
        ], capture_output=True, text=True)
        
        total_duration = float(result.stdout.strip())
        print(f"✅ Video Loaded Successfully!")
        print(f"📌 Video Duration: {total_duration:.2f} seconds")
        
        # Ask user for the cut time
        cut_time = float(input(f"Enter the cut time (seconds) before which the video should be kept (0-{int(total_duration)}): "))
        if cut_time > total_duration or cut_time < 0:
            print("❌ Invalid time! Enter a value between 0 and the total duration.")
            return

        print("⏳ Processing video... Please wait.")
        
        # Use ffmpeg to cut the video
        command = [
            "ffmpeg", "-i", input_path, "-t", str(cut_time), "-c", "copy", output_path
        ]
        
        subprocess.run(command, check=True)
        
        print(f"✅ Video saved successfully: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

# Run the function
cut_video_before_time()
