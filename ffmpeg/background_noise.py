import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def remove_background_noise(video_path, output_video_path):
    audio_path = "temp_audio.aac"
    clean_audio_path = "clean_audio.aac"

    if not os.path.exists(video_path):
        messagebox.showerror("Error", f"File not found: {video_path}")
        return

    try:
        print("Extracting audio from video...")
        subprocess.run(["ffmpeg", "-i", video_path, "-vn", "-acodec", "aac", "-b:a", "128k", audio_path, "-y"], check=True)

        if not os.path.exists(audio_path):
            messagebox.showerror("Error", "Failed to extract audio. The input video may not have an audio stream.")
            return

        print("Reducing background noise and boosting volume...")
        noise_filters = (
            "highpass=f=100, "          # Removes low-frequency hum
            "lowpass=f=6000, "          # Filters out harsh high frequencies
            "afftdn=nr=20:nf=-30, "     # Strong noise suppression without distortion
            "loudnorm=i=-16:lra=8:tp=-1.5, "  # Standard volume normalization
            "volume=2.0"                # Boosts volume (adjustable)
        )

        subprocess.run(["ffmpeg", "-i", audio_path, "-af", noise_filters, clean_audio_path, "-y"], check=True)

        print("Replacing original audio with cleaned audio...")
        subprocess.run(["ffmpeg", "-i", video_path, "-i", clean_audio_path, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-map", "0:v:0", "-map", "1:a:0", "-shortest", output_video_path, "-y"], check=True)

        os.remove(audio_path)
        os.remove(clean_audio_path)

        messagebox.showinfo("Success", f"Noise-reduced video saved as:\n{output_video_path}")
        print(f"✅ Noise-reduced video saved as: {output_video_path}")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"FFmpeg failed:\n{e}")
        print(f"❌ FFmpeg error: {e}")

def main():
    root = tk.Tk()
    root.withdraw()

    video_file = filedialog.askopenfilename(title="Select Video File", filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")])
    if not video_file:
        print("No file selected. Exiting...")
        return

    output_file = filedialog.asksaveasfilename(title="Save Output Video As", defaultextension=".mp4", filetypes=[("MP4 Files", "*.mp4")])
    if not output_file:
        print("No output file selected. Exiting...")
        return

    remove_background_noise(video_file, output_file)

if __name__ == "__main__":
    main()
