import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def select_main_videos():
    files = filedialog.askopenfilenames(
        title="Select Main Videos",
        filetypes=[("MP4 files", "*.mp4")])
    if files:
        main_videos_var.set("\n".join(files))

def select_subscribe_video():
    file_path = filedialog.askopenfilename(
        title="Select Subscribe Overlay Video",
        filetypes=[("MP4 files", "*.mp4")])
    if file_path:
        subscribe_video_var.set(file_path)

def select_output_folder():
    folder_path = filedialog.askdirectory(title="Select Output Folder")
    if folder_path:
        output_folder_var.set(folder_path)

def process_videos():
    main_videos = main_videos_var.get().splitlines()
    subscribe_video = subscribe_video_var.get()
    output_folder = output_folder_var.get()

    if not all([main_videos, subscribe_video, output_folder]):
        messagebox.showerror("Error", "Please select all files and folders.")
        return

    for main_video in main_videos:
        base_name = os.path.splitext(os.path.basename(main_video))[0]
        output_path = os.path.join(output_folder, f"{base_name}_with_subscribe.mp4")

        ffmpeg_cmd = [
            "ffmpeg",
            "-i", main_video,
            "-i", subscribe_video,
            "-filter_complex",
            "[1:v]scale=iw/3:ih/3[scaled];"  # Resize overlay to 1/3 size
            "[0:v][scaled]overlay=W-w-20:H-h-20:enable='lt(t,5)'[vout];"  # Overlay only for 5s
            "[1:a]adelay=0|0,apad,atrim=duration=5[sa];"  # Delay sub audio, trim to 5s
            "[0:a][sa]amix=inputs=2:duration=first:dropout_transition=2[aout]",  # Mix audio
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "fast",
            "-y",
            output_path
        ]

        try:
            subprocess.run(ffmpeg_cmd, check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed on: {main_video}\n\n{e}")
            return

    messagebox.showinfo("Success", "All videos processed successfully!")

# GUI Setup
root = tk.Tk()
root.title("Batch Add Subscribe Overlay to Videos")
root.geometry("650x400")

main_videos_var = tk.StringVar()
subscribe_video_var = tk.StringVar()
output_folder_var = tk.StringVar()

tk.Label(root, text="Main Videos (Multiple):").pack()
tk.Entry(root, textvariable=main_videos_var, width=80).pack()
tk.Button(root, text="Select Videos", command=select_main_videos).pack(pady=5)

tk.Label(root, text="Subscribe Overlay Video:").pack()
tk.Entry(root, textvariable=subscribe_video_var, width=80).pack()
tk.Button(root, text="Browse", command=select_subscribe_video).pack(pady=5)

tk.Label(root, text="Output Folder:").pack()
tk.Entry(root, textvariable=output_folder_var, width=80).pack()
tk.Button(root, text="Select Folder", command=select_output_folder).pack(pady=5)

tk.Button(root, text="Process All Videos", command=process_videos, bg="green", fg="white").pack(pady=20)

root.mainloop()
