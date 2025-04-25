import os
import tkinter as tk
from tkinter import filedialog, messagebox

def delete_wav_files():
    # Open a folder selection dialog
    folder_path = filedialog.askdirectory(title="Select Folder to Delete .wav Files")
    
    if not folder_path:
        return  # User cancelled

    deleted_files = []

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.wav'):
            file_path = os.path.join(folder_path, filename)
            try:
                os.remove(file_path)
                deleted_files.append(filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {filename}.\n{str(e)}")

    # Show summary
    if deleted_files:
        messagebox.showinfo("Success", f"Deleted {len(deleted_files)} .wav files.")
    else:
        messagebox.showinfo("No Files Found", "No .wav files found in the selected folder.")

# GUI Setup
root = tk.Tk()
root.title("Delete .wav Files")
root.geometry("300x150")

label = tk.Label(root, text="Click to select folder and delete .wav files")
label.pack(pady=10)

btn = tk.Button(root, text="Select Folder", command=delete_wav_files)
btn.pack(pady=10)

root.mainloop()
