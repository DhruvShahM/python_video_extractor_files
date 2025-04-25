import os
import subprocess
from tkinter import (
    Tk, filedialog, Label, Button, Checkbutton,
    IntVar, BooleanVar, Text, Scrollbar, END,
    Frame, W, E, StringVar, OptionMenu
)
from PIL import Image

def get_video_duration(video_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video_path],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        return float(result.stdout.strip())
    except:
        return 5.0

def get_resize_dimensions(res):
    if res == "720p":
        return (1280, 720)
    elif res == "1080p":
        return (1920, 1080)
    else:
        return None  # Original size

def extract_thumbnails(video_path, output_folder, strategies, preview=False, log_output=None, format_ext="JPEG", resolution="720p"):
    filename = os.path.basename(video_path)
    name, _ = os.path.splitext(filename)
    duration = get_video_duration(video_path)
    resize_dims = get_resize_dimensions(resolution)

    timestamps = []

    if strategies["start"].get():
        timestamps.append((0.0, f"{name}_start.{format_ext.lower()}"))

    if strategies["20%"].get():
        timestamps.append((duration * 0.2, f"{name}_20percent.{format_ext.lower()}"))

    if strategies["middle"].get():
        timestamps.append((duration * 0.5, f"{name}_middle.{format_ext.lower()}"))

    if strategies["multi"].get():
        for percent in [0.1, 0.5, 0.9]:
            ts = duration * percent
            suffix = f"{int(percent * 100)}percent"
            timestamps.append((ts, f"{name}_{suffix}.{format_ext.lower()}"))

    for ts, out_filename in timestamps:
        temp_path = os.path.join(output_folder, "temp_thumb.jpg")
        out_path = os.path.join(output_folder, out_filename)

        subprocess.run([
            "ffmpeg", "-y", "-ss", str(ts), "-i", video_path,
            "-vframes", "1", "-q:v", "2", temp_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not os.path.exists(temp_path):
            if log_output:
                log_output.insert(END, f"❌ Failed: {out_filename}\n")
            continue

        img = Image.open(temp_path)
        if resize_dims:
            img = img.resize(resize_dims)
        img.save(out_path, format=format_ext, quality=90)

        if log_output:
            log_output.insert(END, f"✅ Saved: {out_path}\n")

        if preview:
            img.show(title=out_filename)

        os.remove(temp_path)

def run_generator():
    files = filedialog.askopenfilenames(
        title="Select Video Files",
        filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")]
    )
    if not files:
        return

    output_folder = os.path.dirname(files[0])
    log_output.insert(END, f"\n📁 Output Folder: {output_folder}\n\n")
    for file in files:
        extract_thumbnails(
            file,
            output_folder,
            strategies,
            preview=preview_var.get(),
            log_output=log_output,
            format_ext=format_var.get(),
            resolution=resolution_var.get()
        )

# GUI Setup
root = Tk()
root.title("🎞️ Auto Thumbnail Generator")

# Strategy checkboxes
strategies = {
    "start": IntVar(value=1),
    "20%": IntVar(value=1),
    "middle": IntVar(value=1),
    "multi": IntVar(value=0)
}
preview_var = BooleanVar(value=False)

Label(root, text="🧠 Choose Thumbnail Strategies:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=W, padx=10, pady=5)

row_idx = 1
for key, var in strategies.items():
    Checkbutton(root, text=f"{key} frame", variable=var).grid(row=row_idx, column=0, sticky=W, padx=20)
    row_idx += 1

Checkbutton(root, text="👀 Preview Thumbnails", variable=preview_var).grid(row=row_idx, column=0, sticky=W, padx=20)
row_idx += 1

# Save options
Label(root, text="🖼️ Image Format:").grid(row=row_idx, column=0, sticky=W, padx=20)
format_var = StringVar(value="JPEG")
OptionMenu(root, format_var, "JPEG", "PNG", "WEBP").grid(row=row_idx, column=0, sticky=E, padx=20)
row_idx += 1

Label(root, text="📏 Resolution:").grid(row=row_idx, column=0, sticky=W, padx=20)
resolution_var = StringVar(value="720p")
OptionMenu(root, resolution_var, "720p", "1080p", "original").grid(row=row_idx, column=0, sticky=E, padx=20)
row_idx += 1

# Start button
Button(root, text="📂 Select Videos & Generate Thumbnails", command=run_generator, bg="green", fg="white").grid(row=row_idx, column=0, pady=10, padx=10, sticky=E+W)
row_idx += 1

# Output log
frame = Frame(root)
frame.grid(row=row_idx, column=0, padx=10, pady=10)
log_output = Text(frame, height=15, width=80)
scroll = Scrollbar(frame, command=log_output.yview)
log_output.configure(yscrollcommand=scroll.set)
log_output.pack(side="left")
scroll.pack(side="right", fill="y")

root.mainloop()
