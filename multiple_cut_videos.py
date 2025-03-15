import tkinter as tk
from tkinter import filedialog
from moviepy import VideoFileClip
from moviepy import concatenate_videoclips 

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

        # Ask user for the number of cuts
        num_cuts = int(input("Enter the number of cuts you want to make: "))
        cut_intervals = []

        for i in range(num_cuts):
            start_time = float(input(f"Enter start time for cut {i+1} (0 - {int(total_duration)}): "))
            end_time = float(input(f"Enter end time for cut {i+1} ({start_time} - {int(total_duration)}): "))
            
            if start_time < 0 or end_time > total_duration or start_time >= end_time:
                print("❌ Invalid time range! Please enter valid values.")
                return
            
            cut_intervals.append((start_time, end_time))

        # Create final video without the cut portions
        clips = []
        prev_end = 0
        
        for start_time, end_time in cut_intervals:
            if prev_end < start_time:
                clips.append(video.subclipped(prev_end, start_time))
            prev_end = end_time
        
        if prev_end < total_duration:
            clips.append(video.subclipped(prev_end, total_duration))
        
        final_video = concatenate_videoclips(clips)

        print("⏳ Processing video... Please wait.")
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"✅ Video saved successfully: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        video.close()
        if 'final_video' in locals():
            final_video.close()


# Run the function
cut_video()
