import tkinter as tk
from tkinter import filedialog
from moviepy import VideoFileClip
from moviepy import concatenate_videoclips  # Use editor module

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
        # Load the video file
        video = VideoFileClip(input_path)
        total_duration = video.duration  # Get total duration in seconds

        print(f"✅ Video Loaded Successfully!")
        print(f"📌 Video Duration: {total_duration:.2f} seconds")

        # Ask user for start and end times
        start_time = float(input(f"Enter the start time in seconds (0 - {int(total_duration)}): "))
        end_time = float(input(f"Enter the end time in seconds ({start_time} - {int(total_duration)}): "))

        if start_time < 0 or end_time > total_duration or start_time >= end_time:
            print("❌ Invalid time range! Please enter valid values.")
            return

        # Keep the video excluding the selected part
        first_part = video.subclipped(0, start_time)
        second_part = video.subclipped(end_time, total_duration)
        final_video = concatenate_videoclips([first_part, second_part])

        print("⏳ Processing video... Please wait.")
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"✅ Video saved successfully: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

# Run the function
cut_video()
