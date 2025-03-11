import torch
import torchaudio
import noisereduce as nr
import deepfilternet
import tkinter as tk
from tkinter import filedialog

def choose_file():
    """Open file dialog to choose an input WAV file."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select a WAV File", filetypes=[("WAV Files", "*.wav")])
    return file_path

def choose_output_file():
    """Open file dialog to choose output file location."""
    root = tk.Tk()
    root.withdraw()
    output_path = filedialog.asksaveasfilename(title="Save Enhanced Audio As", defaultextension=".wav",
                                               filetypes=[("WAV Files", "*.wav")])
    return output_path

def load_audio(file_path):
    """Loads an audio file and ensures it's in the correct format."""
    waveform, sample_rate = torchaudio.load(file_path)
    
    # Convert stereo to mono
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    
    return waveform, sample_rate

def remove_noise(waveform, sample_rate):
    """Applies noise reduction using Noisereduce."""
    waveform_np = waveform.numpy()
    reduced_waveform = nr.reduce_noise(y=waveform_np, sr=sample_rate)
    return torch.tensor(reduced_waveform)

def enhance_speech(waveform, sample_rate):
    """Applies speech enhancement using DeepFilterNet2."""
    model = deepfilternet.DeepFilterNet2()
    enhanced_waveform = model.enhance(waveform.numpy(), sample_rate)
    return torch.tensor(enhanced_waveform)

def save_audio(waveform, sample_rate, output_file):
    """Saves the processed audio file."""
    torchaudio.save(output_file, waveform, sample_rate)

if __name__ == "__main__":
    # Choose input file
    input_file = choose_file()
    if not input_file:
        print("No file selected. Exiting...")
        exit()

    # Choose output file
    output_file = choose_output_file()
    if not output_file:
        print("No output file selected. Exiting...")
        exit()

    # Load audio
    waveform, sample_rate = load_audio(input_file)

    # Remove noise
    denoised_waveform = remove_noise(waveform, sample_rate)

    # Enhance speech
    enhanced_waveform = enhance_speech(denoised_waveform, sample_rate)

    # Save the enhanced audio
    save_audio(enhanced_waveform, sample_rate, output_file)

    print(f"✅ Enhanced audio saved as: {output_file}")
