import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment, effects
from pydub.silence import detect_nonsilent
import noisereduce as nr
import numpy as np
import os

# Load and convert to mono
def load_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    if audio.channels > 1:
        audio = audio.set_channels(1)
    return audio

# AudioSegment → NumPy
def audio_to_numpy(audio):
    return np.array(audio.get_array_of_samples()).astype(np.float32)

# NumPy → AudioSegment
def numpy_to_audio(samples, sample_width, frame_rate):
    samples = np.clip(samples, -32768, 32767)
    int_samples = samples.astype(np.int16)
    return AudioSegment(
        int_samples.tobytes(),
        frame_rate=frame_rate,
        sample_width=sample_width,
        channels=1
    )

# Optional Silence Trimming
def trim_silence(audio_segment, silence_thresh=-40, min_silence_len=400):
    non_silents = detect_nonsilent(audio_segment, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    if not non_silents:
        return audio_segment
    start = non_silents[0][0]
    end = non_silents[-1][1]
    return audio_segment[start:end]

# Noise reduction using noisereduce
def reduce_noise(audio_segment):
    samples = audio_to_numpy(audio_segment)
    sample_rate = audio_segment.frame_rate
    reduced = nr.reduce_noise(y=samples, sr=sample_rate, stationary=False, prop_decrease=0.9)
    return numpy_to_audio(reduced, audio_segment.sample_width, sample_rate)

# Advanced reverb blending
def add_reverb(audio_segment):
    reverb_echo = audio_segment - 8
    reverb_echo = reverb_echo.fade(to_gain=-20.0, start=0, duration=600)
    return audio_segment.overlay(reverb_echo, gain_during_overlay=-3)

# Voice clarity + presence boost
def clarity_boost(audio_segment):
    boosted = audio_segment.apply_gain_stereo(-0.5, 2.5)  # Brighten upper mids
    return boosted

# Final limiter to prevent clipping
def apply_final_limiter(audio_segment, max_dbfs=-1.0):
    peak = audio_segment.max_dBFS
    gain = max_dbfs - peak
    return audio_segment.apply_gain(gain)

# Enhancement pipeline
def enhance_audio(audio_segment):
    # Optional: Trim silence at beginning and end
    # audio_segment = trim_silence(audio_segment)

    audio_segment = effects.high_pass_filter(audio_segment, cutoff=90)
    audio_segment = effects.normalize(audio_segment)
    audio_segment = effects.compress_dynamic_range(audio_segment, threshold=-20.0, ratio=3.5)
    audio_segment = clarity_boost(audio_segment)
    audio_segment = add_reverb(audio_segment)
    audio_segment = apply_final_limiter(audio_segment)
    return audio_segment

# Full processing
def process_audio(input_path, output_dir):
    try:
        filename = os.path.basename(input_path)
        name, _ = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"{name}_enhanced.wav")

        print(f"Processing: {filename}")

        audio = load_audio(input_path)
        reduced_audio = reduce_noise(audio)
        final_audio = enhance_audio(reduced_audio)

        final_audio.export(output_path, format="wav")
        print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error processing {input_path}: {e}")

# GUI file selection
def select_files():
    input_files = filedialog.askopenfilenames(
        title="Select WAV Audio Files",
        filetypes=[("WAV Files", "*.wav")]
    )
    if not input_files:
        return

    output_dir = filedialog.askdirectory(title="Select Output Directory")
    if not output_dir:
        return

    for input_file in input_files:
        process_audio(input_file, output_dir)

    messagebox.showinfo("Done", "All files processed and saved!")

def main():
    root = tk.Tk()
    root.withdraw()
    select_files()
    root.destroy()

if __name__ == "__main__":
    main()
