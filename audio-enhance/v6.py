import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pydub import AudioSegment, effects
from pydub.silence import detect_nonsilent
import noisereduce as nr
import numpy as np
import os
import matplotlib.pyplot as plt

# Globals
noise_profile = None
tone_setting = "Podcast"

# Load and convert to mono
def load_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    if audio.channels > 1:
        audio = audio.set_channels(1)
    return audio

# AudioSegment ↔ NumPy
def audio_to_numpy(audio):
    return np.array(audio.get_array_of_samples()).astype(np.float32)

def numpy_to_audio(samples, sample_width, frame_rate):
    samples = np.clip(samples, -32768, 32767)
    int_samples = samples.astype(np.int16)
    return AudioSegment(
        int_samples.tobytes(),
        frame_rate=frame_rate,
        sample_width=sample_width,
        channels=1
    )

# Batch noise profiling
def set_noise_profile():
    global noise_profile
    file_path = filedialog.askopenfilename(
        title="Select Noise Sample",
        filetypes=[("WAV Files", "*.wav")]
    )
    if not file_path:
        return
    print(f"Loaded noise profile: {file_path}")
    noise_audio = load_audio(file_path)
    noise_profile = audio_to_numpy(noise_audio)

# De-esser: compress 4–8kHz
def de_ess(audio_segment):
    samples = audio_to_numpy(audio_segment)
    sample_rate = audio_segment.frame_rate

    from scipy.signal import butter, lfilter

    def bandpass_filter(data, low, high, fs, order=2):
        nyq = 0.5 * fs
        low /= nyq
        high /= nyq
        b, a = butter(order, [low, high], btype='band')
        return lfilter(b, a, data)

    sibilant = bandpass_filter(samples, 4000, 8000, sample_rate)
    compressed = samples - 0.5 * sibilant  # reduce high-frequency peaks
    return numpy_to_audio(compressed, audio_segment.sample_width, sample_rate)

# Apply reverb
def add_reverb(audio_segment):
    reverb_echo = audio_segment - 8
    reverb_echo = reverb_echo.fade(to_gain=-20.0, start=0, duration=600)
    return audio_segment.overlay(reverb_echo, gain_during_overlay=-3)

# Apply tone
def apply_tone(audio_segment):
    global tone_setting
    if tone_setting == "Podcast":
        return audio_segment.apply_gain_stereo(-1.0, 2.0)
    elif tone_setting == "Warm":
        return audio_segment.low_pass_filter(3000).apply_gain(-1)
    elif tone_setting == "Bright":
        return audio_segment.high_pass_filter(3000).apply_gain(1.5)
    return audio_segment

# Final limiter
def apply_final_limiter(audio_segment, max_dbfs=-1.0):
    peak = audio_segment.max_dBFS
    gain = max_dbfs - peak
    return audio_segment.apply_gain(gain)

# Full enhancement pipeline
def enhance_audio(audio_segment):
    audio_segment = effects.high_pass_filter(audio_segment, cutoff=90)
    audio_segment = effects.normalize(audio_segment)
    audio_segment = effects.compress_dynamic_range(audio_segment, threshold=-20.0, ratio=3.5)
    audio_segment = de_ess(audio_segment)
    audio_segment = apply_tone(audio_segment)
    audio_segment = add_reverb(audio_segment)
    audio_segment = apply_final_limiter(audio_segment)
    return audio_segment

# Noise reduction
def reduce_noise(audio_segment):
    global noise_profile
    samples = audio_to_numpy(audio_segment)
    sample_rate = audio_segment.frame_rate
    if noise_profile is not None:
        reduced = nr.reduce_noise(y=samples, y_noise=noise_profile, sr=sample_rate, prop_decrease=0.95)
    else:
        reduced = nr.reduce_noise(y=samples, sr=sample_rate)
    return numpy_to_audio(reduced, audio_segment.sample_width, sample_rate)

# Waveform visualization
def show_waveform(original, processed):
    fig, axs = plt.subplots(2, 1, figsize=(10, 4), sharex=True)
    axs[0].plot(audio_to_numpy(original), color='gray')
    axs[0].set_title("Original Audio")
    axs[1].plot(audio_to_numpy(processed), color='green')
    axs[1].set_title("Enhanced Audio")
    plt.tight_layout()
    plt.show()

# Main processing
def process_audio(input_path, output_dir):
    try:
        filename = os.path.basename(input_path)
        name, _ = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"{name}_enhanced.wav")

        print(f"Processing: {filename}")
        audio = load_audio(input_path)
        reduced_audio = reduce_noise(audio)
        final_audio = enhance_audio(reduced_audio)

        show_waveform(audio, final_audio)

        final_audio.export(output_path, format="wav")
        print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error processing {input_path}: {e}")

# File selector
def select_files():
    input_files = filedialog.askopenfilenames(title="Select WAV Files", filetypes=[("WAV Files", "*.wav")])
    if not input_files:
        return
    output_dir = filedialog.askdirectory(title="Select Output Directory")
    if not output_dir:
        return
    for input_file in input_files:
        process_audio(input_file, output_dir)
    messagebox.showinfo("Done", "All files processed!")

# GUI app
def main():
    def run_with_tone(tone):
        global tone_setting
        tone_setting = tone
        root.withdraw()
        select_files()
        root.deiconify()

    global root
    root = tk.Tk()
    root.title("Advanced Audio Enhancer")

    ttk.Label(root, text="🎙️ Select Voice Tone:").pack(pady=10)
    for t in ["Podcast", "Warm", "Bright"]:
        ttk.Button(root, text=t, command=lambda tone=t: run_with_tone(tone)).pack(pady=5)

    ttk.Button(root, text="📤 Load Noise Sample", command=set_noise_profile).pack(pady=15)
    ttk.Button(root, text="🎧 Enhance Files", command=select_files).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
