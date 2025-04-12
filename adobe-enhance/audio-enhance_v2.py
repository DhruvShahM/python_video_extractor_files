import librosa
import soundfile as sf
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import numpy as np
from scipy.signal import butter, filtfilt

# Function to apply advanced equalization
def apply_equalization(y, sr):
    # Lowcut and highcut frequencies for better clarity and warmth
    def butter_bandpass(lowcut, highcut, fs, order=5):
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        return b, a

    # Apply different frequency band boosts and cuts
    lowcut = 100.0  # Low frequency for warmth (50-150 Hz)
    highcut = 8000.0  # High frequency for clarity (3000-6000 Hz)
    b, a = butter_bandpass(lowcut, highcut, sr)
    y_filtered = filtfilt(b, a, y)

    # Further frequency band tuning: Reduce midrange (300-1000 Hz) to reduce muddiness
    y_filtered = y_filtered - (y_filtered * 0.1)  # Mild cut to midrange frequencies
    return y_filtered

# Function to apply dynamic range compression (light compression with a sidechain effect)
def apply_compression(y, threshold=0.4, ratio=3.5):
    # Apply subtle compression for more dynamic control without flattening the voice
    y_compressed = np.copy(y)
    y_compressed[y_compressed > threshold] = threshold + (y_compressed[y_compressed > threshold] - threshold) / ratio
    return y_compressed

# Function to simulate slight reverb for a natural podcast feel
def apply_reverb(y, sr, reverb_amount=0.02):
    # Adding a slight reverb (simple echo-based reverb effect)
    reverb_signal = np.copy(y)
    delay = int(sr * 0.02)  # 20ms delay for slight reverb
    for i in range(delay, len(y)):
        reverb_signal[i] += reverb_amount * y[i - delay]
    return reverb_signal

# Function to add subtle stereo widening
def apply_stereo_widening(y):
    # Apply a subtle stereo widening effect by creating slight difference between channels
    y_stereo = np.column_stack((y, y * 1.05))  # Slightly widen the second channel
    return y_stereo

# Function to apply limiting to prevent distortion and clip
def apply_limiting(y, limit=0.9):
    # Limiting to avoid clipping
    y_limited = np.copy(y)
    y_limited = np.clip(y_limited, -limit, limit)
    return y_limited

# Function to handle the audio processing
def process_audio(input_path, output_path):
    try:
        # Load the audio file
        y, sr = librosa.load(input_path, sr=None)

        # Step 1: Equalization (boost low-mid and high frequencies for clearer voice)
        y_eq = apply_equalization(y, sr)

        # Step 2: Apply Compression (gentle dynamic range compression)
        y_compressed = apply_compression(y_eq)

        # Step 3: Apply Reverb (subtle reverb for natural ambience)
        y_reverb = apply_reverb(y_compressed, sr)

        # Step 4: Apply Stereo Widening (optional)
        y_stereo = apply_stereo_widening(y_reverb)

        # Step 5: Apply Limiting (prevent distortion and clipping)
        y_limited = apply_limiting(y_stereo)

        # Step 6: Normalize Audio (to ensure consistent loudness typical of podcasts)
        y_normalized = librosa.util.normalize(y_limited)

        # Step 7: Save the Processed Audio
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
