import tkinter as tk
from tkinter import filedialog
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Function to choose a single file
def choose_file(prompt):
    tk.Tk().withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title=prompt, filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")])
    return file_path

# Ask for the first video
video1_path = choose_file("Select the first video file")
if not video1_path:
    print("No file selected. Exiting.")
    exit()

# Ask for the second video
video2_path = choose_file("Select the second video file")
if not video2_path:
    print("No file selected. Exiting.")
    exit()

# Load videos
video1 = VideoFileClip(video1_path)
video2 = VideoFileClip(video2_path)

# Concatenate videos
final_video = concatenate_videoclips([video1, video2])

# Save the output
output_filename = "output.mp4"
final_video.write_videofile(output_filename, codec="libx264", fps=video1.fps)

print(f"Videos merged successfully into {output_filename}!")
