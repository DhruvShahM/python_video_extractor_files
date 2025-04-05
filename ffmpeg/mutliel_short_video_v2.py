import os
import ffmpeg
import tkinter as tk
from tkinter import filedialog, messagebox

def get_video_resolution(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
        return int(video_stream['width']), int(video_stream['height'])
    except Exception as e:
        print(f"❌ Could not get resolution for {file_path}: {e}")
        return None, None

def zoom_and_export(file_path, output_dir):
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    output_file = os.path.join(output_dir, f"{name}_zoomed{ext}")

    width, height = get_video_resolution(file_path)
    if width is None or height is None:
        return

    print(f"🎬 Processing: {filename} → {os.path.basename(output_file)} ({width}x{height})")

    if width >= 1080 and height >= 1920:
        zoom_crop_filter = "crop=1080:1920"
    else:
        zoom_crop_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"

    try:
        (
            ffmpeg
            .input(file_path)
            .output(output_file, vf=zoom_crop_filter, acodec='aac', vcodec='libx264', strict='experimental')
            .run(overwrite_output=True)
        )
        print(f"✅ Exported: {output_file}")
    except ffmpeg.Error as e:
        print(f"❌ Error processing {filename}:")
        print(e.stderr.decode())

def select_input_files():
    files = filedialog.askopenfilenames(
        title="Select Video Files",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if files:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, ";".join(files))

def select_output_folder():
    folder = filedialog.askdirectory(title="Select Output Folder")
    output_entry.delete(0, tk.END)
    output_entry.insert(0, folder)

def process_videos():
    input_files_str = input_entry.get()
    output_dir = output_entry.get()

    if not input_files_str or not output_dir:
        messagebox.showerror("Error", "Please select input files and output folder.")
        return

    input_files = input_files_str.split(";")

    for video in input_files:
        if os.path.isfile(video):
            zoom_and_export(video, output_dir)

    messagebox.showinfo("Done", f"✅ Processed {len(input_files)} videos.")

# GUI Setup
root = tk.Tk()
root.title("🎞️ Multi Video Zoom & Crop Tool")
root.geometry("600x220")

tk.Label(root, text="Selected Video Files:").pack(pady=(10, 0))
input_entry = tk.Entry(root, width=70)
input_entry.pack()
tk.Button(root, text="Browse Videos", command=select_input_files).pack(pady=(0, 10))

tk.Label(root, text="Output Folder:").pack()
output_entry = tk.Entry(root, width=70)
output_entry.pack()
tk.Button(root, text="Browse Output Folder", command=select_output_folder).pack(pady=(0, 10))

tk.Button(root, text="🚀 Start Processing", command=process_videos, bg="green", fg="white").pack(pady=10)

root.mainloop()
