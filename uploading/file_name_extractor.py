import os
import json
import tkinter as tk
from tkinter import filedialog
import sys

def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_selected = filedialog.askdirectory(title="Select Folder")
    return folder_selected

def get_files_json(folder_path):
    if not folder_path:
        print("No folder selected.")
        return []
    
    property_name = input("Enter the property name (default: videoFile): ").strip()
    if not property_name:
        property_name = "videoFile"
    
    files = [
        {property_name: os.path.join(folder_path, file).replace("\\", "/")}
        for file in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, file))
    ]
    
    return files

def update_existing_json(new_data):
    root = tk.Tk()
    root.withdraw()
    json_file_path = filedialog.askopenfilename(title="Select Existing JSON File", filetypes=[("JSON files", "*.json")])
    
    if not json_file_path:
        print("No JSON file selected.")
        return
    
    try:
        with open(json_file_path, "r") as file:
            existing_data = json.load(file)
        
        if isinstance(existing_data, list):
            for i in range(min(len(existing_data), len(new_data))):
                existing_data[i].update(new_data[i])
        
        with open(json_file_path, "w") as file:
            json.dump(existing_data, file, indent=4)
        
        print("JSON file updated successfully.")
    except Exception as e:
        print("Error updating JSON file:", e)

if __name__ == "__main__":
    folder = select_folder()
    new_json_data = get_files_json(folder)
    print(json.dumps(new_json_data, indent=4))
    sys.exit()  # Ensures no further code execution
