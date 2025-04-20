import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

class VideoOverlayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Overlay Multiple Videos")
        self.root.geometry("600x400")

        self.main_video_path = None
        self.overlay_video_paths = []

        # UI components
        tk.Button(root, text="Select Main Video", command=self.select_main_video).pack(pady=10)
        tk.Button(root, text="Select Overlay Videos", command=self.select_overlay_videos).pack(pady=10)
        tk.Button(root, text="Generate Output", command=self.generate_output).pack(pady=10)

        self.overlay_listbox = tk.Listbox(root)
        self.overlay_listbox.pack(pady=10, fill="both", expand=True)

    def select_main_video(self):
        path = filedialog.askopenfilename(title="Select Main Video", filetypes=[("MP4 files", "*.mp4")])
        if path:
            self.main_video_path = path
            messagebox.showinfo("Main Video Selected", os.path.basename(path))

    def select_overlay_videos(self):
        paths = filedialog.askopenfilenames(title="Select Overlay Videos", filetypes=[("MP4 files", "*.mp4")])
        if paths:
            self.overlay_video_paths = paths
            self.overlay_listbox.delete(0, tk.END)
            for p in paths:
                self.overlay_listbox.insert(tk.END, os.path.basename(p))

    def generate_output(self):
        if not self.main_video_path or not self.overlay_video_paths:
            messagebox.showerror("Missing Input", "Please select both main and overlay videos.")
            return

        output_path = filedialog.asksaveasfilename(title="Save Output Video As", defaultextension=".mp4",
                                                filetypes=[("MP4 files", "*.mp4")])
        if not output_path:
            return

        num_inputs = len(self.overlay_video_paths)
        inputs = [f'-i "{self.main_video_path}"'] + [f'-i "{p}"' for p in self.overlay_video_paths]
        input_str = ' '.join(inputs)

        filter_complex = ""
        overlay_str = ""
        last_video = "[0:v]"
        offset_y = 0
        audio_inputs = []

        # Build video overlay filters
        for i, overlay_path in enumerate(self.overlay_video_paths):
            scale_label = f"[ov{i}]"
            overlay_label = f"[tmp{i}]"

            # Get duration of the overlay video using ffprobe
            cmd = [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", overlay_path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            overlay_duration = float(result.stdout.strip())

            filter_complex += f"[{i+1}:v] scale=200:-1 {scale_label}; "
            filter_complex += (
                f"{last_video}{scale_label} overlay=W-w-10:H-h-{10 + offset_y}:enable='lte(t,{overlay_duration})' {overlay_label}; "
            )

            last_video = overlay_label
            offset_y += 110
            audio_inputs.append(f"[{i+1}:a]")



        # Audio mix: include main video + all overlays
        all_audio_inputs = '[0:a]' + ''.join(audio_inputs)
        num_audio_inputs = len(audio_inputs) + 1
        filter_complex += f"{all_audio_inputs} amix=inputs={num_audio_inputs}:duration=longest [mixed_audio]"

        full_cmd = f'ffmpeg {input_str} -filter_complex "{filter_complex}" -map "{last_video}" -map "[mixed_audio]" -y "{output_path}"'

        print("Running FFmpeg command:")
        print(full_cmd)

        try:
            subprocess.run(full_cmd, shell=True, check=True)
            messagebox.showinfo("Success", "Output video generated successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("FFmpeg Error", f"Failed to process video.\n\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoOverlayApp(root)
    root.mainloop()
