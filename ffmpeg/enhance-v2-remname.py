import os
import tkinter as tk
from tkinter import filedialog

# Open a dialog to select a folder
root = tk.Tk()
root.withdraw()  # Hide the root window

folder_path = filedialog.askdirectory(title="Select Folder Containing Files")
if not folder_path:
    print("No folder selected. Exiting...")
    exit()

# Iterate through files in the selected folder
for filename in os.listdir(folder_path):
    if "-enhanced-v2" in filename:
        new_filename = filename.replace("-enhanced-v2", "")
        old_file = os.path.join(folder_path, filename)
        new_file = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(old_file, new_file)
        print(f'Renamed: "{filename}" → "{new_filename}"')

print("Renaming completed.")
