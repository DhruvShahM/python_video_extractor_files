import subprocess
import tkinter as tk
from tkinter import filedialog

def choose_and_auto_edit():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Open file dialog to select a video file
    file_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[("Video Files", "*.mkv *.mp4 *.mov *.avi *.flv")]
    )

    if not file_path:
        print("No file selected. Exiting...")
        return

    command = ["auto-editor", file_path, "--export", "resolve"]
    
    try:
        subprocess.run(command, check=True)
        print("Auto-editing completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Run the function
choose_and_auto_edit()
