import json
import tkinter as tk
from tkinter import filedialog, messagebox

def select_json_file(prompt):
    """ Opens a file dialog to select a JSON file. """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title=prompt, filetypes=[("JSON files", "*.json")])
    return file_path

def save_json_file():
    """ Opens a file dialog to select a save location for the updated JSON file. """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.asksaveasfilename(
        title="Save Updated JSON File",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )
    return file_path

def replace_text_content(old_json_path, new_json_path, output_path):
    """ Updates 'content' in slides where 'slide_type' is 'text' based on matching titles. """
    
    # Load old JSON file
    with open(old_json_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    # Load new JSON file
    with open(new_json_path, "r", encoding="utf-8") as f:
        new_data = json.load(f)

    # Create a mapping of new content based on title for 'text' slides
    text_content_updates = {
        slide["title"]: slide["content"]
        for slide in new_data if slide.get("slide_type") == "text"
    }

    # Update old slides
    for slide in old_data:
        if slide.get("slide_type") == "text" and slide.get("title") in text_content_updates:
            slide["content"] = text_content_updates[slide["title"]]

    # Save updated JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(old_data, f, indent=4, ensure_ascii=False)

    messagebox.showinfo("Success", f"Updated JSON saved at:\n{output_path}")
    print(f"Updated JSON saved at: {output_path}")

def main():
    """ Main function to select JSON files and update content. """
    
    # Select old JSON file
    old_json = select_json_file("Select the old JSON file")
    if not old_json:
        messagebox.showwarning("No File Selected", "Old JSON file selection canceled.")
        return

    # Select new JSON file
    new_json = select_json_file("Select the new JSON file")
    if not new_json:
        messagebox.showwarning("No File Selected", "New JSON file selection canceled.")
        return

    # Select output file location
    output_json = save_json_file()
    if not output_json:
        messagebox.showwarning("No File Selected", "Output JSON file selection canceled.")
        return

    # Replace content
    replace_text_content(old_json, new_json, output_json)

if __name__ == "__main__":
    main()
