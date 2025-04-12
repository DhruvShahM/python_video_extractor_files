import librosa
import soundfile as sf
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
from scipy.signal import butter, filtfilt
import scipy
import audioread
from scipy.io import wavfile

# Define butter bandpass filter function
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

# Function to apply mild equalization (light bandpass filter)
def apply_equalization(y, sr):
    # Fine-tuned bandpass filter range for voice clarity
    lowcut = 150.0
    highcut = 8000.0
    b, a = butter_bandpass(lowcut, highcut, sr)
    y_filtered = filtfilt(b, a, y)  # Apply bandpass filter
    return y_filtered

# Apply mild dynamic range compression to prevent clipping
def apply_compression(y, threshold=0.75, ratio=2.0):
    # Light compression: apply it only when the amplitude exceeds the threshold
    y_compressed = np.copy(y)
    y_compressed[np.abs(y_compressed) > threshold] = np.sign(y_compressed[np.abs(y_compressed) > threshold]) * threshold
    return y_compressed

# Apply light saturation effect to add warmth and harmonics to the voice
def apply_saturation(y, gain=1.2):
    # Soft clipping to simulate analog saturation
    y_saturated = np.tanh(y * gain)  # Applying a tanh function to simulate saturation
    return y_saturated

# Normalize audio to a target loudness level (RMS normalization)
def normalize_audio(y, target_rms=0.1):
    rms = np.sqrt(np.mean(y**2))
    normalization_factor = target_rms / rms
    y_normalized = y * normalization_factor
    return y_normalized

# LUFS Normalization - Calculate loudness and normalize based on LUFS
def normalize_lufs(y, sr, target_lufs=-16.0):
    # Using librosa to compute loudness (RMS level)
    rms = np.sqrt(np.mean(y**2))
    # Adjust based on target LUFS
    normalization_factor = 10**((target_lufs - librosa.core.amplitude_to_db(rms)) / 20)
    return y * normalization_factor

# De-essing (Reducing sibilance)
def deess(y, sr, freq=5000, q=30, threshold=0.05):
    """Apply a de-esser filter to reduce harsh 's' sounds."""
    # De-essing in the high frequencies around the "sibilance" range
    nyquist = 0.5 * sr
    lowcut = freq - 500
    highcut = freq + 500
    b, a = butter_bandpass(lowcut, highcut, sr, order=4)
    y_filtered = filtfilt(b, a, y)

    # Attenuate the sibilant frequencies if they exceed the threshold
    y_deessed = np.where(np.abs(y_filtered) > threshold, y_filtered * 0.5, y)
    return y_deessed

# Ensure the audio is finite (no NaNs or infinities)
def check_finite(y):
    if not np.all(np.isfinite(y)):
        print("Warning: Audio contains NaN or Inf values. Replacing with zeros.")
        y = np.nan_to_num(y)
    return y

# Function to handle the audio processing
def process_audio(input_path, output_path):
    try:
        # Load the audio file
        print(f"Loading audio from {input_path}...")
        y, sr = librosa.load(input_path, sr=None)

        # Step 1: Ensure audio is finite
        y = check_finite(y)

        # Step 2: Apply Equalization (Light bandpass filtering)
        print("Applying equalization...")
        y_eq = apply_equalization(y, sr)

        # Step 3: Apply Light Compression
        print("Applying compression...")
        y_compressed = apply_compression(y_eq)

        # Step 4: Apply Saturation Effect for warmth and fullness
        print("Applying saturation effect...")
        y_saturated = apply_saturation(y_compressed)

        # Step 5: Apply De-essing for high frequencies if necessary
        print("Applying de-essing...")
        y_deessed = deess(y_saturated, sr)

        # Step 6: Normalize Audio to LUFS (target loudness)
        print("Normalizing audio...")
        y_normalized = normalize_lufs(y_deessed, sr)

        # Step 7: Save the processed audio
        print(f"Saving processed audio to {output_path}...")
        sf.write(output_path, y_normalized, sr)

        messagebox.showinfo("Success", f"Audio processed and saved as {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to open the input file
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3;*.flac")])
    if file_path:
        entry_input.delete(0, tk.END)
        entry_input.insert(0, file_path)

# Function to open the output file dialog
def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
    if file_path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, file_path)

# Function to trigger the audio processing
def start_processing():
    input_path = entry_input.get()
    output_path = entry_output.get()

    if not input_path or not output_path:
        messagebox.showwarning("Input/Output Error", "Please select both input and output files.")
        return
    
    # Process the audio
    process_audio(input_path, output_path)

# Create the main window
root = tk.Tk()
root.title("Podcast Audio Processing")

# Input file label and entry
label_input = tk.Label(root, text="Select Input Audio File")
label_input.pack(pady=5)
entry_input = tk.Entry(root, width=50)
entry_input.pack(pady=5)
btn_input = tk.Button(root, text="Browse", command=open_file)
btn_input.pack(pady=5)

# Output file label and entry
label_output = tk.Label(root, text="Select Output Audio File")
label_output.pack(pady=5)
entry_output = tk.Entry(root, width=50)
entry_output.pack(pady=5)
btn_output = tk.Button(root, text="Browse", command=save_file)
btn_output.pack(pady=5)

# Process button
btn_process = tk.Button(root, text="Process Audio", command=start_processing)
btn_process.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()
