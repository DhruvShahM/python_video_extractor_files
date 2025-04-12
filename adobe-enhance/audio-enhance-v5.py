import librosa
import soundfile as sf
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import numpy as np
from scipy.signal import butter, filtfilt

# Define Presets
PRESETS = {
    "Podcast Voice": {
        "lowcut": 150.0,
        "highcut": 8000.0,
        "compression_threshold": 0.75,
        "compression_ratio": 2.0,
        "saturation_gain": 1.2,
        "target_lufs": -16.0
    },
    "Warm Radio": {
        "lowcut": 80.0,
        "highcut": 6000.0,
        "compression_threshold": 0.65,
        "compression_ratio": 2.5,
        "saturation_gain": 1.5,
        "target_lufs": -14.0
    },
    "Crisp Vocals": {
        "lowcut": 200.0,
        "highcut": 9000.0,
        "compression_threshold": 0.6,
        "compression_ratio": 3.0,
        "saturation_gain": 1.3,
        "target_lufs": -15.0
    }
}

# Butter bandpass filter
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_equalization(y, sr, lowcut, highcut):
    b, a = butter_bandpass(lowcut, highcut, sr)
    y_filtered = filtfilt(b, a, y)
    return y_filtered

def apply_compression(y, threshold, ratio):
    y_compressed = np.copy(y)
    over_threshold = np.abs(y) > threshold
    y_compressed[over_threshold] = np.sign(y[over_threshold]) * (
        threshold + (np.abs(y[over_threshold]) - threshold) / ratio
    )
    return y_compressed

def apply_saturation(y, gain):
    return np.tanh(y * gain)

def normalize_lufs(y, sr, target_lufs):
    rms = np.sqrt(np.mean(y**2))
    normalization_factor = 10 ** ((target_lufs - librosa.amplitude_to_db(rms)) / 20)
    return y * normalization_factor

def deess(y, sr, freq=5000, q=30, threshold=0.05):
    lowcut = freq - 500
    highcut = freq + 500
    b, a = butter_bandpass(lowcut, highcut, sr, order=4)
    y_filtered = filtfilt(b, a, y)
    y_deessed = np.where(np.abs(y_filtered) > threshold, y_filtered * 0.5, y)
    return y_deessed

def check_finite(y):
    if not np.all(np.isfinite(y)):
        y = np.nan_to_num(y)
    return y

# Main audio processing function
def process_audio(input_path, output_path, preset_name):
    try:
        preset = PRESETS[preset_name]
        y, sr = librosa.load(input_path, sr=None)
        y = check_finite(y)

        y_eq = apply_equalization(y, sr, preset["lowcut"], preset["highcut"])
        y_compressed = apply_compression(y_eq, preset["compression_threshold"], preset["compression_ratio"])
        y_saturated = apply_saturation(y_compressed, preset["saturation_gain"])
        y_deessed = deess(y_saturated, sr)
        y_normalized = normalize_lufs(y_deessed, sr, preset["target_lufs"])

        sf.write(output_path, y_normalized, sr)
        messagebox.showinfo("Success", f"Audio processed using '{preset_name}' preset and saved as {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# GUI setup
root = tk.Tk()
root.title("Podcast Audio Processor with Presets")

# Input file
tk.Label(root, text="Select Input Audio File").pack(pady=5)
entry_input = tk.Entry(root, width=50)
entry_input.pack()
tk.Button(root, text="Browse", command=lambda: entry_input.insert(0, filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3;*.flac")]))).pack(pady=5)


# Output file
tk.Label(root, text="Select Output Audio File").pack(pady=5)
entry_output = tk.Entry(root, width=50)
entry_output.pack()
tk.Button(root, text="Browse", command=lambda: entry_output.insert(0, filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")]))).pack(pady=5)


# Preset dropdown
tk.Label(root, text="Select Audio Processing Preset").pack(pady=5)
preset_var = tk.StringVar(value="Podcast Voice")
preset_dropdown = ttk.Combobox(root, textvariable=preset_var, values=list(PRESETS.keys()), state="readonly", width=30)
preset_dropdown.pack(pady=5)

# Process button
tk.Button(root, text="Process Audio", command=lambda: start_processing()).pack(pady=20)

# Start processing function
def start_processing():
    input_path = entry_input.get()
    output_path = entry_output.get()
    preset_name = preset_var.get()

    if not input_path or not output_path:
        messagebox.showwarning("Missing Info", "Please provide both input and output file paths.")
        return

    process_audio(input_path, output_path, preset_name)

root.mainloop()
