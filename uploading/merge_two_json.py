import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def merge_json():
    root = tk.Tk()
    root.withdraw()
    
    folder = filedialog.askdirectory(title="Select Folder Containing JSON Files")
    if not folder:
        messagebox.showerror("Error", "No folder selected!")
        return
    
    file1_path = filedialog.askopenfilename(title="Select First JSON File", initialdir=folder, filetypes=[("JSON Files", "*.json")])
    if not file1_path:
        messagebox.showerror("Error", "No first file selected!")
        return
    
    file2_path = filedialog.askopenfilename(title="Select Second JSON File", initialdir=folder, filetypes=[("JSON Files", "*.json")])
    if not file2_path:
        messagebox.showerror("Error", "No second file selected!")
        return
    
    output_file = filedialog.asksaveasfilename(title="Save Merged JSON As", initialdir=folder, defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if not output_file:
        messagebox.showerror("Error", "No output file selected!")
        return
    
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        data1 = json.load(f1)
        data2 = json.load(f2)
    
    merged_data = {
        "choose_filename": os.path.basename(output_file),
        "users": data1.get("users", []) + data2.get("users", []),
        "metadata": [data1.get("metadata", {}), data2.get("metadata", {})]
    }
    
    if "extra_field" in data1:
        merged_data["extra_fields"] = {"file1_extra": data1["extra_field"]}
    
    with open(output_file, 'w') as f_out:
        json.dump(merged_data, f_out, indent=4)
    
    messagebox.showinfo("Success", f"Merged JSON saved as {output_file}")

# Execute script
merge_json()