import os
import ffmpeg
import wave
import json
import srt
from vosk import Model, KaldiRecognizer
from moviepy import VideoFileClip
from datetime import timedelta

# Paths
VIDEO_PATH = r"C:/Users/dhruv/Videos/video_selected/1.1_126.mp4"
AUDIO_PATH = "temp_audio.wav"
MODEL_PATH = r"C:/Users/dhruv/Downloads/vosk-model-small-hi-0.22"
SRT_PATH = "subtitles.srt"

# Extract audio from video and convert to WAV (16kHz, Mono)
def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec='pcm_s16le', fps=16000, nbytes=2, ffmpeg_params=["-ac", "1"])
    print("✅ Audio extracted successfully.")

# Transcribe audio using Vosk
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

# Convert Vosk output to SRT format
def create_srt(transcriptions, srt_file):
    subtitles = []
    sentence = []
    start_time = None

    for entry in transcriptions:
        word = entry["word"]
        start_seconds = entry["start"]
        end_seconds = entry["end"]

        if not start_time:
            start_time = start_seconds  # Start of sentence

        sentence.append(word)

        # End sentence if duration > 2.5 seconds or if punctuation is detected
        if end_seconds - start_time > 2.5 or word in ".?!।":
            # Convert timestamps to timedelta
            start_delta = timedelta(seconds=start_time)
            end_delta = timedelta(seconds=end_seconds)
            
            # Create subtitle block
            subtitles.append(srt.Subtitle(index=len(subtitles) + 1,
                                          start=start_delta,
                                          end=end_delta,
                                          content=" ".join(sentence)))

            # Reset sentence
            sentence = []
            start_time = None

    # Write to SRT file
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))

    print("✅ Subtitles generated successfully.")

# Main function to generate Hindi subtitles
def generate_hindi_subtitles():
    extract_audio(VIDEO_PATH, AUDIO_PATH)
    transcriptions = transcribe_audio(AUDIO_PATH, MODEL_PATH)
    create_srt(transcriptions, SRT_PATH)
    print(f"✅ Subtitles saved to {SRT_PATH}")

# Run the script
if __name__ == "__main__":
    generate_hindi_subtitles()
