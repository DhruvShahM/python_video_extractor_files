import json
import tkinter as tk
from tkinter import filedialog

def generate_prompts(data):
    prompts = []
    prompt_template = ("`Generate a YouTube script in Hinglish on {object}, "
                       "The script should jump straight into the main content without an intro or conclusion. Keep it engaging, "
                       "conversational, and provide clear explanations with examples where needed. Use a mix of Hindi and English "
                       "to keep it natural and easy to follow.Don't include any code in the script—just explanations" )
    
    for item in data:
        if item.get("slide_type") == "text" or item.get("slide_type") == "table":
            object_data = {"title": item["title"], "content": item["content"]}
            prompts.append(prompt_template.format(object=json.dumps(object_data, ensure_ascii=False)))
    
    return prompts

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select JSON File", filetypes=[("JSON Files", "*.json")])
    return file_path

def save_file(prompts):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(title="Save JSON File", defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    
    if file_path:
        with open(file_path, "w", encoding="utf-8") as prompts_file:
            json.dump(prompts, prompts_file, ensure_ascii=False, indent=4)
        print(f"Prompts have been saved to {file_path}")
    else:
        print("Save operation canceled.")

# Select input JSON file
input_file = select_file()
if input_file:
    with open(input_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    
    # Generate prompts
    prompts_list = generate_prompts(json_data)
    
    # Save output JSON file
    save_file(prompts_list)
else:
    print("File selection canceled.")