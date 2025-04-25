import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def merge_music_with_video_audio(video_path, music_path, output_path, music_volume=0.2, delay_ms=0):
    try:
        volume_filter = f"volume={music_volume}"
        delay_filter = f",adelay={delay_ms}|{delay_ms}" if delay_ms > 0 else ""

        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-i", music_path,
            "-filter_complex",
            f"[1:a]{volume_filter}{delay_filter}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]

        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", f"Merged output saved to:\n{output_path}")
        
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error while merging audio:\n{e}")

def browse_video():
    path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")])
    video_entry.delete(0, tk.END)
    video_entry.insert(0, path)

def browse_music():
    path = filedialog.askopenfilename(title="Select Background Music File", filetypes=[("Audio Files", "*.mp3 *.wav")])
    music_entry.delete(0, tk.END)
    music_entry.insert(0, path)

def browse_output():
    path = filedialog.asksaveasfilename(title="Save Output As", defaultextension=".mp4", filetypes=[("MP4 Files", "*.mp4")])
    output_entry.delete(0, tk.END)
    output_entry.insert(0, path)

def start_merge():
    video = video_entry.get()
    music = music_entry.get()
    output = output_entry.get()
    
    try:
        volume = float(volume_entry.get())
        delay = int(delay_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Volume must be a float, Delay must be an integer.")
        return

    if not video or not music or not output:
        messagebox.showwarning("Missing Input", "Please select all required files.")
        return

    merge_music_with_video_audio(video, music, output, music_volume=volume, delay_ms=delay)

# GUI setup
root = tk.Tk()
root.title("Video + Background Music Merger")

tk.Label(root, text="Video File (with voiceover):").grid(row=0, column=0, sticky="e")
video_entry = tk.Entry(root, width=50)
video_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_video).grid(row=0, column=2)

tk.Label(root, text="Background Music File:").grid(row=1, column=0, sticky="e")
music_entry = tk.Entry(root, width=50)
music_entry.grid(row=1, column=1)
tk.Button(root, text="Browse", command=browse_music).grid(row=1, column=2)

tk.Label(root, text="Output File:").grid(row=2, column=0, sticky="e")
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=2, column=1)
tk.Button(root, text="Browse", command=browse_output).grid(row=2, column=2)

tk.Label(root, text="Music Volume (0.0 - 1.0):").grid(row=3, column=0, sticky="e")
volume_entry = tk.Entry(root)
volume_entry.insert(0, "0.2")
volume_entry.grid(row=3, column=1)

tk.Label(root, text="Music Delay (ms):").grid(row=4, column=0, sticky="e")
delay_entry = tk.Entry(root)
delay_entry.insert(0, "3000")
delay_entry.grid(row=4, column=1)

tk.Button(root, text="Merge and Save", command=start_merge, bg="#4CAF50", fg="white", padx=10).grid(row=5, column=1, pady=10)

root.mainloop()
