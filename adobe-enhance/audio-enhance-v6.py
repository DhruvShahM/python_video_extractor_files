import librosa
import soundfile as sf
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from scipy.signal import butter, filtfilt
import noisereduce as nr  # Importing noise reduction library

# ------------------ Audio Processing Functions ------------------ #

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_highpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    low = cutoff / nyquist
    b, a = butter(order, [low], btype='high')
    return b, a

def apply_equalization(y, sr, lowcut=150.0, highcut=8000.0):
    b, a = butter_bandpass(lowcut, highcut, sr)
    return filtfilt(b, a, y)

def apply_compression(y, threshold=0.75, ratio=2.0):
    y_compressed = np.copy(y)
    y_compressed[np.abs(y_compressed) > threshold] = np.sign(y_compressed[np.abs(y_compressed) > threshold]) * threshold
    return y_compressed

def apply_saturation(y, gain=1.2):
    return np.tanh(y * gain)

def normalize_lufs(y, sr, target_lufs=-16.0):
    rms = np.sqrt(np.mean(y**2))
    normalization_factor = 10**((target_lufs - librosa.core.amplitude_to_db(rms)) / 20)
    return y * normalization_factor

def deess(y, sr, freq=5000, q=30, threshold=0.05):
    nyquist = 0.5 * sr
    lowcut = freq - 500
    highcut = freq + 500
    b, a = butter_bandpass(lowcut, highcut, sr, order=4)
    y_filtered = filtfilt(b, a, y)
    y_deessed = np.where(np.abs(y_filtered) > threshold, y_filtered * 0.5, y)
    return y_deessed

def check_finite(y):
    if not np.all(np.isfinite(y)):
        print("Warning: Audio contains NaN or Inf values. Replacing with zeros.")
        y = np.nan_to_num(y)
    return y

# ------------------ High-Pass Filter for Puffy Sound ------------------ #
def remove_puffy_sound(y, sr, cutoff=100.0):
    print("Removing puffy sound (high-pass filter)...")
    b, a = butter_highpass(cutoff, sr)
    return filtfilt(b, a, y)

# ------------------ Noise Reduction ------------------ #

def reduce_noise(y, sr):
    """
    Apply noise reduction to audio data using the noisereduce library.
    This function reduces background noise like vehicle horns, hum, etc.
    """
    print("Applying noise reduction...")
    return nr.reduce_noise(y=y, sr=sr)

# ------------------ Preset Configs ------------------ #

PRESETS = {
    "Warm Radio": {
        "lowcut": 100.0,
        "highcut": 6000.0,
        "compression_threshold": 0.7,
        "saturation_gain": 1.1,
        "target_lufs": -18.0
    },
    "Podcast Voice": {
        "lowcut": 120.0,
        "highcut": 7500.0,
        "compression_threshold": 0.72,
        "saturation_gain": 1.2,
        "target_lufs": -16.0
    },
    "Crisp Vocals": {
        "lowcut": 150.0,
        "highcut": 8500.0,
        "compression_threshold": 0.75,
        "saturation_gain": 1.3,
        "target_lufs": -14.0
    }
}

# ------------------ Audio Processing Logic ------------------ #

def process_audio(input_path, output_path, preset_name):
    try:
        print(f"Loading audio from {input_path}...")
        y, sr = librosa.load(input_path, sr=None)

        y = check_finite(y)
        y = reduce_noise(y, sr)  # Apply noise reduction

        # Remove Puffy Sound (Low-Frequency Boominess)
        y = remove_puffy_sound(y, sr)

        config = PRESETS[preset_name]

        print("Applying equalization...")
        y = apply_equalization(y, sr, config["lowcut"], config["highcut"])

        print("Applying compression...")
        y = apply_compression(y, config["compression_threshold"])

        print("Applying saturation...")
        y = apply_saturation(y, config["saturation_gain"])

        print("Applying de-essing...")
        y = deess(y, sr)

        print("Normalizing...")
        y = normalize_lufs(y, sr, config["target_lufs"])

        print(f"Saving processed audio to {output_path}...")
        sf.write(output_path, y, sr)

        messagebox.showinfo("Success", f"Audio processed and saved as {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# ------------------ GUI ------------------ #

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3;*.flac")])
    if file_path:
        entry_input.delete(0, tk.END)
        entry_input.insert(0, file_path)

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
    if file_path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, file_path)

def start_processing():
    input_path = entry_input.get()
    output_path = entry_output.get()
    preset_name = preset_var.get()

    if not input_path or not output_path:
        messagebox.showwarning("Input/Output Error", "Please select both input and output files.")
        return

    process_audio(input_path, output_path, preset_name)

root = tk.Tk()
root.title("Podcast Audio Enhancer")

label_input = tk.Label(root, text="Select Input Audio File")
label_input.pack(pady=5)
entry_input = tk.Entry(root, width=50)
entry_input.pack(pady=5)
btn_input = tk.Button(root, text="Browse", command=open_file)
btn_input.pack(pady=5)

label_output = tk.Label(root, text="Select Output Audio File")
label_output.pack(pady=5)
entry_output = tk.Entry(root, width=50)
entry_output.pack(pady=5)
btn_output = tk.Button(root, text="Browse", command=save_file)
btn_output.pack(pady=5)

# Preset Selection Dropdown
label_preset = tk.Label(root, text="Select Audio Preset")
label_preset.pack(pady=5)
preset_var = tk.StringVar(root)
preset_var.set("Crisp Vocals")  # Default
preset_menu = tk.OptionMenu(root, preset_var, *PRESETS.keys())
preset_menu.pack(pady=5)

btn_process = tk.Button(root, text="Process Audio", command=start_processing)
btn_process.pack(pady=20)

root.mainloop()
