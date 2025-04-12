import tkinter as tk
from tkinter import filedialog
import ffmpeg
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to select multiple videos
def select_multiple_videos():
    return filedialog.askopenfilenames(title="Select Multiple Videos", filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])

# Function to select one additional video
def select_single_video():
    return filedialog.askopenfilename(title="Select One Additional Video", filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])

# Function to select the output folder
def select_output_folder():
    return filedialog.askdirectory(title="Select Output Folder")

# Function to convert video to TS format
def convert_to_ts(video_path, output_ts):
    ffmpeg.input(video_path).output(output_ts, format="mpegts", vcodec="libx264", acodec="aac", strict="experimental").run(overwrite_output=True)

# Function to merge two videos
def merge_videos(video1, video2, output_path):
    try:
        original_filename = os.path.splitext(os.path.basename(video1))[0]
        ts1 = f"{original_filename}_temp1.ts"
        ts2 = f"{original_filename}_temp2.ts"

        convert_to_ts(video1, ts1)
        convert_to_ts(video2, ts2)

        output_file = os.path.join(output_path, f"{original_filename}_merged.mp4")

        ffmpeg.input(f"concat:{ts1}|{ts2}", format="mpegts").output(output_file, vcodec="copy", acodec="copy").run(overwrite_output=True)

        os.remove(ts1)
        os.remove(ts2)

        print(f"✅ Merged video saved: {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Error merging {video1} and {video2}: {e}")
        return None

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    selected_videos = select_multiple_videos()
    if not selected_videos:
        print("❌ No videos selected!")
        exit()

    single_video = select_single_video()
    if not single_video:
        print("❌ No additional video selected!")
        exit()

    output_folder = select_output_folder()
    if not output_folder:
        print("❌ No output folder selected!")
        exit()

    print("🚀 Starting batch merging with parallel processing...")

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(merge_videos, video, single_video, output_folder) for video in selected_videos]

        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"🎬 Completed: {result}")

    print("🎉 All videos processed with parallel merging!")
