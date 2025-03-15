import os
import subprocess
import wave
import json
import srt
from vosk import Model, KaldiRecognizer
from moviepy import VideoFileClip

# Paths
VIDEO_PATH = r"C:/Users/dhruv/Videos/video_selected/1.1_126.mp4"
AUDIO_PATH = "temp_audio.wav"
MODEL_PATH = r"C:/Users/dhruv/Downloads/vosk-model-small-hi-0.22"
SRT_PATH = "subtitles.srt"
ASS_PATH = "subtitles.ass"
OUTPUT_VIDEO_PATH = r"C:/Users/dhruv/Videos/video_selected/1.1_126_subtitled.mp4"

# Step 1: Extract Audio from Video
def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le', fps=16000, nbytes=2, ffmpeg_params=["-ac", "1"])
    print("✅ Audio extracted successfully.")

# Step 2: Transcribe Audio using Vosk
def transcribe_audio(audio_path, model_path):
    model = Model(model_path)
    
    with wave.open(audio_path, "rb") as wf:
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        while True:
            data = wf.readframes(4000)
            if not data:
                break
            rec.AcceptWaveform(data)

        result = json.loads(rec.FinalResult())
        return result.get("result", [])

# Step 3: Convert Vosk Output to SRT
def create_srt(transcriptions, srt_file):
    subtitles = []
    
    for i, entry in enumerate(transcriptions):
        start_seconds = entry["start"]
        end_seconds = entry["end"]
        text = entry["word"]

        # Convert seconds to SRT timestamp format
        def format_time(seconds):
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = int((seconds - int(seconds)) * 1000)
            return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

        start_timestamp = format_time(start_seconds)
        end_timestamp = format_time(end_seconds)

        subtitles.append(srt.Subtitle(index=i+1,
                                      start=srt.srt_timestamp_to_timedelta(start_timestamp),
                                      end=srt.srt_timestamp_to_timedelta(end_timestamp),
                                      content=text))

    # Write to SRT file
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))

    print(f"✅ Subtitles saved to {srt_file}")

# Step 4: Convert SRT to ASS (FFmpeg prefers ASS format)
def convert_srt_to_ass(srt_path, ass_path):
    command = ["ffmpeg", "-i", srt_path, ass_path]
    subprocess.run(command, check=True)
    print(f"✅ Converted {srt_path} to {ass_path}")

# Step 5: Embed Subtitles in Video
def add_subtitles_to_video(video_path, subtitle_path, output_path):
    video_path = video_path.replace("\\", "/")
    subtitle_path = subtitle_path.replace("\\", "/")
    output_path = output_path.replace("\\", "/")

    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={subtitle_path}",
        "-c:a", "copy",
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print("✅ Subtitled video created successfully!")
    except subprocess.CalledProcessError as e:
        print("❌ Error adding subtitles:", e)

# Step 6: Run the Full Process
def generate_subtitled_video():
    extract_audio(VIDEO_PATH, AUDIO_PATH)
    transcriptions = transcribe_audio(AUDIO_PATH, MODEL_PATH)
    create_srt(transcriptions, SRT_PATH)
    convert_srt_to_ass(SRT_PATH, ASS_PATH)  # Convert SRT to ASS
    add_subtitles_to_video(VIDEO_PATH, ASS_PATH, OUTPUT_VIDEO_PATH)  # Embed subtitles
    print(f"🎬 Final video saved at {OUTPUT_VIDEO_PATH}")

# Run
if __name__ == "__main__":
    generate_subtitled_video()
