# -*- coding: utf-8 -*-
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import math # Needed for int() conversion of half_time for adelay

# --- Configuration ---
FFMPEG_PATH = "ffmpeg"
FFPROBE_PATH = "ffprobe"
# --- End Configuration ---

# --- GUI Functions (select_main_videos, select_start_overlay, etc.) ---
# ... (Keep these exactly as they were in the previous version) ...
def select_main_videos():
    files = filedialog.askopenfilenames(parent=root, title="Select Main Videos", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if files: main_videos_var.set("\n".join(files))
def select_start_overlay():
    file_path = filedialog.askopenfilename(parent=root, title="Select Subscribe Overlay (Start)", filetypes=[("MP4 files", "*.mp4"), ("MOV files", "*.mov"), ("All files", "*.*")])
    if file_path: start_overlay_var.set(file_path)
def select_middle_overlay():
    file_path = filedialog.askopenfilename(parent=root, title="Select Subscribe Overlay (Middle)", filetypes=[("MP4 files", "*.mp4"), ("MOV files", "*.mov"), ("All files", "*.*")])
    if file_path: middle_overlay_var.set(file_path)
def select_output_folder():
    folder_path = filedialog.askdirectory(parent=root, title="Select Output Folder")
    if folder_path: output_folder_var.set(folder_path)
# --- End GUI Functions ---


# --- Utility Functions (has_audio_stream, get_video_duration, check_ffmpeg_availability) ---
# ... (Keep these exactly as they were in the previous version) ...
def has_audio_stream(filepath):
    cmd = [ FFPROBE_PATH, "-v", "error", "-show_streams", "-select_streams", "a", "-of", "default=noprint_wrappers=1:nokey=1", filepath ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        return bool(result.stdout.strip())
    except Exception: return False # Simplified error handling for brevity
def get_video_duration(filepath):
    cmd = [ FFPROBE_PATH, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        return float(result.stdout.strip())
    except Exception as e:
         print(f"Error getting duration for {os.path.basename(filepath)}: {e}")
         messagebox.showerror("ffprobe Error", f"Failed to get duration for:\n{os.path.basename(filepath)}")
         return None
def check_ffmpeg_availability():
    try:
         subprocess.run([FFMPEG_PATH, "-version"], capture_output=True, check=True, timeout=5)
         return True
    except Exception as e:
         messagebox.showerror("Error", f"'{FFMPEG_PATH}' not found or failed execution. Ensure FFmpeg is installed and in PATH.\nError: {e}")
         return False
# --- End Utility Functions ---

def process_videos():
    """Processes the selected videos with the specified overlays using adelay."""
    if not check_ffmpeg_availability():
        return

    main_videos_text = main_videos_var.get()
    start_overlay = start_overlay_var.get()
    middle_overlay = middle_overlay_var.get()
    output_folder = output_folder_var.get()

    if not all([main_videos_text, start_overlay, middle_overlay, output_folder]):
        messagebox.showerror("Input Error", "Please select all files and folders.")
        return

    main_videos = [line for line in main_videos_text.splitlines() if line.strip()]
    if not main_videos:
         messagebox.showerror("Input Error", "No valid main video file paths provided.")
         return

    # --- File Checks ---
    if not os.path.exists(start_overlay): messagebox.showerror("File Not Found", f"Start overlay not found:\n{start_overlay}"); return
    if not os.path.exists(middle_overlay): messagebox.showerror("File Not Found", f"Middle overlay not found:\n{middle_overlay}"); return
    if not os.path.isdir(output_folder): messagebox.showerror("Folder Not Found", f"Output folder not found:\n{output_folder}"); return
    if not has_audio_stream(middle_overlay): messagebox.showerror("Audio Missing", f"Middle Overlay:\n{os.path.basename(middle_overlay)}\n\nHas NO audio track. Cannot proceed."); return
    if not has_audio_stream(start_overlay): messagebox.showwarning("Audio Missing", f"Start Overlay:\n{os.path.basename(start_overlay)}\n\nHas no audio track. Continuing without its audio.")
    # --- End File Checks ---

    processing_successful_count = 0
    processing_failed_count = 0
    total_videos = len(main_videos)

    for index, main_video in enumerate(main_videos):
        print(f"\nProcessing video {index + 1}/{total_videos}: {os.path.basename(main_video)}")

        if not os.path.exists(main_video):
             print(f"Skipping missing file: {main_video}")
             messagebox.showwarning("File Not Found", f"Main video file not found, skipping:\n{os.path.basename(main_video)}")
             processing_failed_count += 1
             continue

        duration = get_video_duration(main_video)
        if duration is None or duration <= 0:
            print(f"Skipping due to duration error/invalid duration ({duration}s): {os.path.basename(main_video)}")
            processing_failed_count += 1
            continue

        half_time_sec = duration / 2.0
        delay_ms = int(half_time_sec * 1000)
        adelay_value = f"{delay_ms}|{delay_ms}" # Format for adelay e.g., "15000|15000"

        start_overlay_duration = 5.0
        middle_overlay_duration = 5.0
        middle_overlay_end_time = min(half_time_sec + middle_overlay_duration, duration)

        base_name = os.path.splitext(os.path.basename(main_video))[0]
        output_filename = f"{base_name}_with_dual_overlay.mp4"
        output_path = os.path.join(output_folder, output_filename)

        # --- *** Fixed Filter Complex using adelay *** ---
        filter_complex = f"""
        [1:v]scale=iw/3:ih/3[start_v];
        [2:v]scale=iw/3:ih/3[middle_v_scaled];
        [middle_v_scaled]setpts=PTS-STARTPTS+{half_time_sec}/TB[middle_v];
        [0:v][start_v]overlay=W-w-20:H-h-20:enable='lt(t,{start_overlay_duration})'[tmp1];
        [tmp1][middle_v]overlay=W-w-20:H-h-20:enable='between(t,{half_time_sec},{middle_overlay_end_time})'[vout];
        
        [1:a]atrim=0:{start_overlay_duration},asetpts=PTS-STARTPTS,volume=1.5[start_a];
        [2:a]atrim=0:{middle_overlay_duration},asetpts=PTS-STARTPTS,adelay={adelay_value}|{adelay_value},volume=1.8[middle_a];
        [0:a]volume=0.8[main_a];
        [main_a][start_a]amix=inputs=2:duration=first:dropout_transition=2[tmpa];
        [tmpa][middle_a]amix=inputs=2:duration=first:dropout_transition=2[aout]
        """
        # --- *** End Filter Complex *** ---
        filter_complex = ' '.join(filter_complex.split()) # Clean up whitespace

        ffmpeg_cmd = [
            FFMPEG_PATH,
            "-i", main_video,
            "-i", start_overlay,
            "-i", middle_overlay,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",  # Increased audio bitrate for better quality
            "-movflags", "+faststart",
            "-y",
            output_path
        ]

        print("--- Running FFmpeg ---")
        print("Command:", " ".join(f'"{arg}"' if " " in arg else arg for arg in ffmpeg_cmd))
        print(f"Target middle audio start time: {half_time_sec:.2f}s ({delay_ms}ms delay)")

        try:
            process = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
            print(f"Successfully processed: {output_filename}")
            if process.stderr:
                 print(f"FFmpeg console output (stderr) for {output_filename}:\n{process.stderr.strip()}")
            processing_successful_count += 1
        except subprocess.CalledProcessError as e:
            error_message = f"FFmpeg failed for:\n{os.path.basename(main_video)}\n\nReturn Code: {e.returncode}\nError:\n"
            stderr_tail = "\n".join(e.stderr.strip().splitlines()[-15:])
            error_message += stderr_tail[:1000]
            if len(stderr_tail) > 1000: error_message += "\n..."
            print("--- FFmpeg Error ---")
            print(f"Failed processing: {os.path.basename(main_video)}")
            print(f"stderr:\n{e.stderr.strip()}")
            messagebox.showerror("FFmpeg Error", error_message)
            processing_failed_count += 1
            continue
        except Exception as e:
            print(f"An unexpected error occurred while running FFmpeg for {os.path.basename(main_video)}: {e}")
            messagebox.showerror("Execution Error", f"Unexpected error running FFmpeg for:\n{os.path.basename(main_video)}\n\n{e}")
            processing_failed_count += 1
            continue
        finally:
             print("-" * 20)

    # --- Processing Finished ---
    print("\n=== Processing Complete ===")
    print(f"Successfully processed: {processing_successful_count}")
    print(f"Failed/Skipped: {processing_failed_count}")

    if processing_failed_count == 0 and processing_successful_count > 0:
        messagebox.showinfo("Success", f"All {processing_successful_count} videos processed successfully!")
    elif processing_successful_count > 0:
        messagebox.showwarning("Finished with Errors", f"Processing finished.\n\nSuccessfully processed: {processing_successful_count}\nFailed/Skipped: {processing_failed_count}\n\nPlease check the console output for error details.")
    elif processing_failed_count > 0 :
         messagebox.showerror("Processing Failed", f"No videos were processed successfully.\nFailed/Skipped: {processing_failed_count}\n\nPlease check the console output for error details.")
    else:
         messagebox.showinfo("Finished", "No videos were selected or processed.")

# --- GUI Setup (Keep as before) ---
root = tk.Tk()
root.title("Video Dual Overlay Tool (Start + Middle)")
root.geometry("750x500")

main_videos_var = tk.StringVar()
start_overlay_var = tk.StringVar()
middle_overlay_var = tk.StringVar()
output_folder_var = tk.StringVar()

main_frame = tk.Frame(root, padx=15, pady=15)
main_frame.pack(fill=tk.BOTH, expand=True)

# ... (Keep all the Label, Entry, Button packing as before) ...
tk.Label(main_frame, text="1. Select Main Videos (One per line):").pack(anchor='w')
main_videos_entry = tk.Entry(main_frame, textvariable=main_videos_var, width=90)
main_videos_entry.pack(fill=tk.X, expand=True)
tk.Button(main_frame, text="Browse Main Videos", command=select_main_videos).pack(pady=(0, 10))

tk.Label(main_frame, text="2. Select Start Overlay (Displays 0s-5s):").pack(anchor='w', pady=(10, 0))
tk.Entry(main_frame, textvariable=start_overlay_var, width=90).pack(fill=tk.X, expand=True)
tk.Button(main_frame, text="Browse Start Overlay", command=select_start_overlay).pack(pady=(0, 10))

tk.Label(main_frame, text="3. Select Middle Overlay (Displays 5s at Midpoint):").pack(anchor='w', pady=(10, 0))
tk.Entry(main_frame, textvariable=middle_overlay_var, width=90).pack(fill=tk.X, expand=True)
tk.Button(main_frame, text="Browse Middle Overlay", command=select_middle_overlay).pack(pady=(0, 10))

tk.Label(main_frame, text="4. Select Output Folder:").pack(anchor='w', pady=(10, 0))
tk.Entry(main_frame, textvariable=output_folder_var, width=90).pack(fill=tk.X, expand=True)
tk.Button(main_frame, text="Select Output Folder", command=select_output_folder).pack(pady=(0, 15))

process_button = tk.Button(
    main_frame, text="Process Videos", command=process_videos,
    bg="#4CAF50", fg="white", font=('Segoe UI', 10, 'bold'),
    padx=20, pady=10
)
process_button.pack(pady=20)

# --- Start GUI ---
root.mainloop()

