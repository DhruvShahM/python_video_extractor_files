import os
import ffmpeg
import tkinter as tk
from tkinter import filedialog
import subprocess

def choose_file(title="Select a video file", file_types=(("MP4 files", "*.mp4"), ("All files", "*.*"))):
    """Open file dialog to choose a file."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title=title, filetypes=file_types)
    return file_path

def choose_output_file(default_name="output.mp4"):
    """Open save dialog to choose output file location."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", initialfile=default_name,
                                             filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    return file_path

def get_video_duration(input_file):
    """Get the duration of the video using FFmpeg."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return float(result.stdout.strip()) if result.stdout else None
    except Exception as e:
        print("⚠️ Error getting video duration:", e)
        return None

def speed_up_video(input_file, output_file, speed_factor):
    """Speed up video and audio while maintaining synchronization."""
    try:
        if speed_factor > 2:
            print("⚠️ FFmpeg only allows `atempo` up to 2x per pass. Using multiple passes.")
        
        cmd = [
            "ffmpeg", "-y", "-i", input_file,
            "-filter_complex", f"[0:v]setpts={1/speed_factor}*PTS[v];[0:a]atempo={min(speed_factor, 2.0)}[a]",
            "-map", "[v]", "-map", "[a]", "-preset", "fast", output_file
        ]

        subprocess.run(cmd, check=True)
        print(f"✅ Video successfully sped up to {speed_factor:.2f}x and saved as {output_file}.")
    
    except subprocess.CalledProcessError as e:
        print("⚠️ FFmpeg error occurred.")
        print(f"Error: {e}")



def trim_video(input_file, output_file, start_time="00:00:00", end_time="00:01:00"):
    """Trim video to the desired duration."""
    try:
        (
            ffmpeg
            .input(input_file, ss=start_time, to=end_time)
            .output(output_file, c="copy")  # No re-encoding, fast processing
            .run(overwrite_output=True)
        )
        print(f"✅ Video successfully trimmed to {output_file}.")
    except ffmpeg.Error as e:
        print("⚠️ FFmpeg error occurred.")
        print("FFmpeg Output:", e.stdout or "No stdout output")
        print("FFmpeg Error:", e.stderr or "No stderr output")

if __name__ == "__main__":
    print("📂 Choose your input video file...")
    input_video = choose_file()

    if not input_video:
        print("❌ No input file selected. Exiting.")
        exit()

    print("💾 Choose where to save the output file...")
    output_video = choose_output_file()

    if not output_video:
        print("❌ No output file selected. Exiting.")
        exit()

    print("⏳ Checking video duration...")
    duration = get_video_duration(input_video)

    if duration is None:
        print("❌ Could not determine video duration. Exiting.")
        exit()

    print(f"🎬 Video duration: {duration:.2f} seconds")

    if duration <= 60:
        print("✅ Video is already under 1 minute. No changes needed.")
    elif duration <= 120:
        speed_factor = duration / 60  # Calculate speed factor to fit within 1 minute
        print(f"⚡ Speeding up video by {speed_factor:.2f}x to fit within 1 minute.")
        speed_up_video(input_video, output_video, speed_factor)
    else:
        print("✂️ Trimming the first 1 minute of the video.")
        trim_video(input_video, output_video, "00:00:00", "00:01:00")
