import subprocess
import tkinter as tk
from tkinter import filedialog
import os

def process_video_with_audio_settings():
    """
    Processes a video using auto-editor and then applies recommended audio settings
    using ffmpeg post-processing.
    """
    root = tk.Tk()
    root.withdraw()

    # Ask the user to select a video file
    file_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=[("Video Files", "*.mkv *.mp4 *.mov *.avi *.flv")]
    )

    # Exit if no file is selected
    if not file_path:
        print("No file selected. Exiting...")
        return

    # Define output file paths
    # auto-editor output will be temporary before final ffmpeg processing
    auto_editor_output = file_path.rsplit(".", 1)[0] + "_edited_temp.mp4"
    final_output_video = file_path.rsplit(".", 1)[0] + "_final.mp4"

    print(f"Processing file: {file_path}")
    print(f"Temporary auto-editor output: {auto_editor_output}")
    print(f"Final output with audio processing: {final_output_video}")

    # --- Step 1: Auto-edit video using auto-editor ---
    print("\n--- Running auto-editor ---")
    auto_editor_command = [
        "auto-editor", file_path,
        "-o", auto_editor_output,
        "--no-open",
        "--frame-rate", "30",
        "--silent-speed", "99999" # Speeds up silent parts significantly
    ]

    try:
        subprocess.run(auto_editor_command, check=True)
        print(f"Auto-editor finished. Output: {auto_editor_output}")
    except FileNotFoundError:
        print("Error: auto-editor command not found.")
        print("Please ensure auto-editor is installed and in your system's PATH.")
        return
    except subprocess.CalledProcessError as e:
        print(f"Error during auto-editor process: {e}")
        # Clean up temp file if auto-editor failed partially
        if os.path.exists(auto_editor_output):
             try:
                 os.remove(auto_editor_output)
                 print(f"Cleaned up temporary file: {auto_editor_output}")
             except Exception as cleanup_error:
                 print(f"Error cleaning up temporary file: {cleanup_error}")
        return
    except Exception as e:
        print(f"An unexpected error occurred during auto-editor: {e}")
        return


    # Ensure the temporary auto-editor output file exists before proceeding
    if not os.path.exists(auto_editor_output):
        print(f"Auto-editor did not produce the expected output file: {auto_editor_output}. Aborting audio processing.")
        return

    # --- Step 2: Apply recommended audio settings using ffmpeg ---
    # This step re-encodes the audio stream of the auto-edited video
    # and applies loudness normalization.
    print("\n--- Applying recommended audio settings using ffmpeg ---")
    ffmpeg_command = [
        "ffmpeg", "-i", auto_editor_output,
        "-c:v", "copy", # Copy the video stream without re-encoding
        "-c:a", "aac", # Set audio codec to AAC (YouTube recommended)
        "-b:a", "192k", # Set audio bitrate to 192 kbps (YouTube recommended for stereo)
        "-ar", "48000", # Set audio sample rate to 48000 Hz (YouTube recommended)
        "-filter:a", "loudnorm=I=-14:LRA=11:TP=-1.5", # Apply loudness normalization (-14 LUFS integrated)
                                                   # LRA: Loudness Range, TP: True Peak ceiling
        "-y", # Overwrite output file without asking
        final_output_video
    ]

    # Note: The loudnorm filter can optionally be run in two passes for more accuracy.
    # This script uses a single pass for simplicity. For a two-pass approach,
    # you would run ffmpeg once with `loudnorm=print_stats=true` to get measurements,
    # and then run it again with `loudnorm=I=-14:LRA=11:TP=-1.5:measured_I=<val>:measured_LRA=<val>:measured_TP=<val>:measured_RMS=<val>`

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"FFmpeg finished. Final video exported with audio processing: {final_output_video}")
    except FileNotFoundError:
        print("Error: ffmpeg command not found.")
        print("Please ensure ffmpeg is installed and in your system's PATH.")
        return
    except subprocess.CalledProcessError as e:
        print(f"Error during ffmpeg audio processing: {e}")
        # Clean up potentially incomplete final output file
        if os.path.exists(final_output_video):
             try:
                 os.remove(final_output_video)
                 print(f"Cleaned up incomplete file: {final_output_video}")
             except Exception as cleanup_error:
                 print(f"Error cleaning up incomplete file: {cleanup_error}")
        return
    except Exception as e:
        print(f"An unexpected error occurred during ffmpeg processing: {e}")
        return

    # --- Step 3: Clean up the temporary auto-editor output file ---
    print("\n--- Cleaning up temporary files ---")
    try:
        if os.path.exists(auto_editor_output):
            os.remove(auto_editor_output)
            print(f"Temporary auto-editor file deleted: {auto_editor_output}")
        # The temporary WAV extraction step from the original script is removed
        # as it's not needed for this audio processing approach.
    except Exception as e:
        print(f"Error deleting temporary file: {e}")

# Run the process
if __name__ == "__main__":
    process_video_with_audio_settings()