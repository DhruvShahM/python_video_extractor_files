import tkinter as tk
from tkinter import filedialog
from moviepy import VideoFileClip  # Using video.io.VideoFileClip as requested

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
        # Load the video file
        video = VideoFileClip(input_path)
        total_duration = video.duration  # Get total duration in seconds
        
        print(f"✅ Video Loaded Successfully!")
        print(f"📌 Video Duration: {total_duration:.2f} seconds")
        print(f"📌 Video FPS: {video.fps}")
        print(f"📌 Video Resolution: {video.size}")

        # Ask user for the cut time
        cut_time = float(input(f"Enter the cut time (seconds) before which the video should be kept (0-{int(total_duration)}): "))
        if cut_time > total_duration or cut_time < 0:
            print("❌ Invalid time! Enter a value between 0 and the total duration.")
            return

        # Trim the video from 0 to cut_time
        cut_video = video.subclipped(0, cut_time)

        print("⏳ Processing video... Please wait.")
        cut_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"✅ Video saved successfully: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

# Run the function
cut_video_before_time()




# If the total video duration is **100.47 seconds** and you want to cut the last **8 seconds**, then:  

# ### **Formula**  
# ```
# Cut time = Total Duration - Seconds to Cut
# ```
# ```
# Cut time = 100.47 - 8 = 92.47 seconds
# ```

# ### **What value should you enter?**  
# 👉 **Enter `92.47`** when prompted:  
# ```
# Enter the cut time (seconds) before which the video should be kept (0-100): 92.47
# ```
# This will **keep the first 92.47 seconds** and remove the last 8 seconds.

# ---

# ### **Alternative (Rounding)**
# If you want a **whole number**, you can enter **`92`** instead of `92.47`.  
# - This will **keep the first 92 seconds** and remove the last **8.47** seconds.  

# Let me know if you need further clarification! 🚀🔥