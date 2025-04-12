import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment, effects
from pydub.silence import detect_nonsilent
import noisereduce as nr
import numpy as np
import os

# Force mono & load
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

# Auto noise reduction across the file
def reduce_noise(audio_samples, sample_rate):
    return nr.reduce_noise(
        y=audio_samples,
        sr=sample_rate,
        stationary=False,
        prop_decrease=0.9
    )

# Full enhancement pipeline
def enhance_audio(audio_segment):
    # Trim silence from start and end
    nonsilent = detect_nonsilent(audio_segment, min_silence_len=300, silence_thresh=-40)
    if nonsilent:
        start, end = nonsilent[0][0], nonsilent[-1][1]
        audio_segment = audio_segment[start:end]

    # High-pass filter to remove low-frequency hums
    audio_segment = effects.high_pass_filter(audio_segment, cutoff=100)

    # Normalize volume
    audio_segment = effects.normalize(audio_segment)

    # Optional stereo gain tweak
    audio_segment = audio_segment + AudioSegment.silent(duration=0)
    audio_segment = audio_segment.apply_gain_stereo(-1.0, 2.5)

    # ✅ Compression (without knee)
    audio_segment = effects.compress_dynamic_range(
        audio_segment,
        threshold=-18.0,
        ratio=4.0,
        attack=5,
        release=100
    )

    return audio_segment


# Process and export each file
def process_audio(input_path, output_dir):
    try:
        filename = os.path.basename(input_path)
        name, _ = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"{name}_cleaned.wav")

        print(f"Processing: {filename}...")

        audio = load_audio(input_path)
        audio_samples = audio_to_numpy(audio)
        sample_rate = audio.frame_rate

        reduced = reduce_noise(audio_samples, sample_rate)
        cleaned_audio = numpy_to_audio(reduced, audio.sample_width, sample_rate)
        final_audio = enhance_audio(cleaned_audio)

        final_audio.export(output_path, format="wav")
        print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error processing {input_path}: {e}")

# File selection and batch processing
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

    messagebox.showinfo("Done", "All selected audio files have been processed!")

# Tkinter main window
def main():
    root = tk.Tk()
    root.withdraw()
    select_files()
    root.destroy()

if __name__ == "__main__":
    main()
