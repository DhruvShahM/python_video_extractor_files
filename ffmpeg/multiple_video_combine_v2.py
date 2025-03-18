import os
import ffmpeg
import tkinter as tk
from tkinter import filedialog

def choose_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(
        title="Select Video Files",
        filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")]
    )
    return list(file_paths)

def preprocess_videos(video_files, temp_folder="temp_videos"):
    """Convert videos to a uniform format and fix A/V sync issues."""
    os.makedirs(temp_folder, exist_ok=True)
    processed_files = []

    for index, file in enumerate(video_files):
        output_file = os.path.join(temp_folder, f"video_{index}.mp4")
        try:
            (
                ffmpeg
                .input(file)
                .output(output_file, format="mp4", vcodec="libx264", acodec="aac", 
                        strict="experimental", vsync="vfr", af="aresample=async=1")
                .run(overwrite_output=True)
            )
            processed_files.append(output_file)
        except ffmpeg.Error as e:
            print(f"Error processing {file}: {e.stderr.decode()}")

    return processed_files

def merge_videos(video_files, output_file="merged_video.mp4"):
    if not video_files:
        print("No files selected!")
        return

    temp_videos = preprocess_videos(video_files)

    # Create a text file listing all video files
    list_file = "video_list.txt"
    with open(list_file, "w") as f:
        for file in temp_videos:
            f.write(f"file '{file}'\n")

    # Run FFmpeg to merge videos with proper A/V synchronization
    try:
        (
            ffmpeg
            .input(list_file, format="concat", safe=0)
            .output(output_file, vcodec="libx264", acodec="aac", vsync="vfr", af="aresample=async=1")
            .run(overwrite_output=True)
        )
        print(f"✅ Videos merged successfully into {output_file}")
    except ffmpeg.Error as e:
        print(f"❌ Error: {e.stderr.decode()}")

    # Cleanup temporary files
    os.remove(list_file)
    for temp_file in temp_videos:
        os.remove(temp_file)
    os.rmdir("temp_videos")

if __name__ == "__main__":
    selected_files = choose_files()
    if selected_files:
        merge_videos(selected_files, "merged_video.mp4")
