import moviepy as mp
from moviepy.video.tools.subtitles import SubtitlesClip
from tkinter import Tk, Button, Label, filedialog
from moviepy.video.fx.Resize import Resize  # Import only the 'resize' function
from faster_whisper import WhisperModel
import os

# Subtitle rendering function
def subtitle_generator(txt):
    return mp.TextClip(txt, font='Arial-Bold', fontsize=40, color='white', bg_color='black')

# Generate SRT from video using Whisper
def generate_subtitles(video_path, srt_path):
    model = WhisperModel("base", compute_type="int8", device="cpu")  # You can change to "medium" or "large"
    segments, _ = model.transcribe(video_path)

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments):
            start = segment.start
            end = segment.end
            text = segment.text.strip()
            f.write(f"{i+1}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{text}\n\n")

# Format timestamp for SRT
def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# Main video processing function
def process_video():
    video_path = filedialog.askopenfilename(title="Select Input Video", filetypes=[("MP4 files", "*.mp4")])
    if not video_path:
        return

    output_path = filedialog.asksaveasfilename(title="Save Output Video As", defaultextension=".mp4",
                                                filetypes=[("MP4 files", "*.mp4")])
    if not output_path:
        return

    # Generate subtitle file
    srt_path = "auto_subtitles.srt"
    generate_subtitles(video_path, srt_path)

    # Load and resize video
    try:
        video = mp.VideoFileClip(video_path)
        video = Resize(new_size=(1080, 1920))        # ✅ Correct # Resize by width, keeping aspect ratio
    except Exception as e:
        print(f"Error loading or resizing video: {e}")
        if os.path.exists(srt_path):
            os.remove(srt_path)
        return

    # Load subtitles from auto-generated file
    try:
        subtitles = SubtitlesClip(srt_path, subtitle_generator)
        subtitles = subtitles.set_position(('center', 'bottom')).set_duration(video.duration)
    except Exception as e:
        print(f"Error loading subtitles: {e}")
        # video.close()
        if os.path.exists(srt_path):
            os.remove(srt_path)
        return

    # Composite and save
    try:
        final = mp.CompositeVideoClip([video, subtitles])
        final.write_videofile(output_path, fps=24)
    except Exception as e:
        print(f"Error compositing or saving video: {e}")
    finally:
        video.close()
        subtitles.close()
        if os.path.exists(srt_path):
            os.remove(srt_path)  # Clean up generated subtitle file

# GUI setup
root = Tk()
root.title("Auto Subtitle Video Generator")
root.geometry("400x200")

Label(root, text="Auto-Generate English Subtitles", font=("Arial", 14)).pack(pady=20)
Button(root, text="Select Video and Generate", command=process_video, font=("Arial", 12)).pack(pady=10)

root.mainloop()