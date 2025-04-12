import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pydub import AudioSegment, effects
import noisereduce as nr
import numpy as np
import os
from scipy.signal import butter, lfilter
from concurrent.futures import ThreadPoolExecutor
import soundfile as sf
import pyloudnorm as pyln

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
    reduced = samples - 0.45 * sibilant  # more aggressive
    return numpy_to_audio(reduced, audio_segment.sample_width, sample_rate)


# Add subtle reverb with customizable decay
def add_reverb(audio_segment, decay=-8, fade_duration=600):
    reverb_echo = audio_segment - decay
    reverb_echo = reverb_echo.fade(to_gain=-20.0, start=0, duration=fade_duration)
    return audio_segment.overlay(reverb_echo, gain_during_overlay=-3)

# Apply tone setting (with additional EQ adjustments)
def apply_tone(audio_segment):
    global tone_setting
    if tone_setting == "Podcast":
        return audio_segment.apply_gain_stereo(-1.0, 2.0)
    elif tone_setting == "Warm":
        return audio_segment.low_pass_filter(3200).apply_gain(-1)
    elif tone_setting == "Bright":
        return audio_segment.high_pass_filter(2800).apply_gain(2)
    return audio_segment

# Apply loudness normalization (LUFS)
def normalize_loudness(audio_segment, target_lufs=-16):
    samples = audio_to_numpy(audio_segment)
    sample_rate = audio_segment.frame_rate
    # Normalize to target LUFS
    meter = pyln.Meter(sample_rate)
    loudness = meter.integrated_loudness(samples)
    gain_db = target_lufs - loudness
    return audio_segment.apply_gain(gain_db)

# Equalizer: Apply custom EQ filters (e.g., Bass, Mid, Treble adjustments)
def apply_eq(audio_segment, bass=0, mid=0, treble=0):
    if bass != 0:
        audio_segment = audio_segment.low_pass_filter(100) if bass < 0 else audio_segment.high_pass_filter(100)
    if mid != 0:
        audio_segment = audio_segment.low_pass_filter(2000) if mid < 0 else audio_segment.high_pass_filter(2000)
    if treble != 0:
        audio_segment = audio_segment.high_pass_filter(3000) if treble > 0 else audio_segment.low_pass_filter(3000)
    return audio_segment

# Final limiter to ensure no clipping
def apply_final_limiter(audio_segment, max_dbfs=-1.0):
    peak = audio_segment.max_dBFS
    gain = max_dbfs - peak
    return audio_segment.apply_gain(gain)

# Full enhancement pipeline
def enhance_audio(audio_segment):
    # Clean low-end
    audio_segment = effects.high_pass_filter(audio_segment, cutoff=80)

    # Normalize overall volume
    audio_segment = effects.normalize(audio_segment)

    # Soft compression to retain vocal feel
    audio_segment = effects.compress_dynamic_range(
        audio_segment,
        threshold=-21.0,
        ratio=2.0,
    )

    # De-ess for "S" and "Sh" harshness
    audio_segment = de_ess(audio_segment)

    # Tone preference: Podcast, Warm, Bright
    audio_segment = apply_tone(audio_segment)

    # Simulate high-shelf EQ for clarity — moderate boost
    highs = audio_segment.high_pass_filter(4000).apply_gain(1.5)
    audio_segment = audio_segment.overlay(highs)

    # Presence crispness — safer now
    crisp_boost = audio_segment.high_pass_filter(2500).apply_gain(1.0)
    audio_segment = audio_segment.overlay(crisp_boost)

    # Subtle reverb
    audio_segment = add_reverb(audio_segment)

    # Boost — reduced to +5.5dB to avoid distortion
    audio_segment = audio_segment.apply_gain(5.5)

    # Final smart limiter (soft-clipper like behavior)
    audio_segment = apply_final_limiter(audio_segment, max_dbfs=-1.0)

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

# File preview function
def preview_audio(audio_segment):
    audio_segment.export("temp_preview.wav", format="wav")
    os.system("start temp_preview.wav")  # Play the audio on Windows, use "open" for macOS

# Main processing function with progress feedback
def process_audio(input_file, output_dir, progress_bar, input_files):
    try:
        filename = os.path.basename(input_file)
        name, _ = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"{name}_enhanced.wav")

        print(f"Processing: {filename}")
        audio = load_audio(input_file)
        reduced_audio = reduce_noise(audio)
        final_audio = enhance_audio(reduced_audio)
        final_audio.export(output_path, format="wav")
        print(f"Saved: {output_path}")

        # Update progress bar
        progress_bar['value'] += 100 / len(input_files)
        root.update_idletasks()

    except Exception as e:
        print(f"Error processing {input_file}: {e}")

# Multi-threaded file processing
def process_files_parallel(input_files, output_dir, progress_bar):
    with ThreadPoolExecutor() as executor:
        for input_file in input_files:
            executor.submit(process_audio, input_file, output_dir, progress_bar, input_files)

# File selector
def select_files():
    global input_files
    input_files = filedialog.askopenfilenames(title="Select WAV Files", filetypes=[("WAV Files", "*.wav")])
    if not input_files:
        return
    output_dir = filedialog.askdirectory(title="Select Output Directory")
    if not output_dir:
        return

    progress_bar['maximum'] = len(input_files) * 100
    process_files_parallel(input_files, output_dir, progress_bar)

    messagebox.showinfo("Done", "All files processed!")

# GUI app with real-time user feedback
def main():
    def run_with_tone(tone):
        global tone_setting
        tone_setting = tone
        root.withdraw()
        select_files()
        root.deiconify()

    global root, progress_bar
    root = tk.Tk()
    root.title("Audio Enhancer - Voice Tone & Batch Noise Reduction")

    ttk.Label(root, text="🎙️ Select Voice Tone:").pack(pady=10)
    for t in ["Podcast", "Warm", "Bright"]:
        ttk.Button(root, text=t, command=lambda tone=t: run_with_tone(tone)).pack(pady=5)

    ttk.Button(root, text="📤 Load Noise Sample", command=set_noise_profile).pack(pady=15)
    ttk.Button(root, text="🎧 Enhance Files", command=select_files).pack(pady=10)

    # Progress bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
