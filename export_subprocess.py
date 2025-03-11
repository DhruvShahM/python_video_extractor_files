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

    # Automatically edit and export as a video file
    output_video = file_path.rsplit(".", 1)[0] + "_edited.mp4"
    command = ["auto-editor", file_path, "-o", output_video]

    try:
        subprocess.run(command, check=True)
        print(f"Final video exported successfully: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Run the function
choose_and_auto_edit()
