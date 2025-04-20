import os
import subprocess
from tkinter import Tk, filedialog
import sys # Import sys to check Python version

# Hide the Tkinter root window
root = Tk()
root.withdraw()

# File selection dialog for multiple videos
file_paths = filedialog.askopenfilenames(
    title="Select video files",
    filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv *.flv")]
)

# Output resolution
output_width = 1080
output_height = 1920

# --- Loudness Normalization Settings (using FFmpeg's loudnorm filter) ---
# These settings tell FFmpeg to normalize the audio to meet common standards.
target_integrated_lufs = -14.0  # YouTube/Spotify/etc. recommend around -14 LUFS
target_true_peak_db = -1.0     # Recommended max true peak to prevent clipping
# Optional: target_loudness_range = 11.0 # Recommended range (dynamic control, often less critical for online)

# FFmpeg binary paths
ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"  # Use full path if needed

# Filter for centering (Video filter -vf)
filter_complex_video = (
    f"scale={output_width}:-1,setsar=1,pad={output_width}:{output_height}:(ow-iw)/2:(oh-ih)/2"
)

# Audio filter for Loudness Normalization (-af)
# We use the loudnorm filter to achieve the target LUFS and True Peak.
# 'print_format=summary' is helpful for debugging - FFmpeg will print details about the normalization.
filter_complex_audio = (
    f"loudnorm=i={target_integrated_lufs}:tp={target_true_peak_db}:print_format=summary"
    # Add :lra={target_loudness_range} if you define target_loudness_range
)


def get_video_duration(input_path):
    """Returns duration in seconds using ffprobe"""
    try:
        result = subprocess.run(
            [ffprobe_path, "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Capture stderr as well
            text=True # Use text=True for Python 3.7+
        )
        if result.returncode != 0:
             print(f"❌ ffprobe error getting duration for {input_path}: {result.stderr.strip()}")
             return None
        duration_str = result.stdout.strip()
        if not duration_str:
             print(f"⚠️ ffprobe returned no duration for {input_path}.")
             return None
        return float(duration_str)
    except FileNotFoundError:
        print(f"❌ Error: ffprobe not found. Make sure it's installed and in your PATH.")
        return None
    except Exception as e:
        print(f"❌ Unexpected error getting duration for {input_path}: {e}")
        return None

# Function to check for audio stream
def has_audio_stream(input_path):
    """Checks if a video file has an audio stream using ffprobe"""
    try:
        # Probe only audio streams and check for 'audio' codec type
        result = subprocess.run(
            [ffprobe_path, "-v", "error", "-select_streams", "a:0", # Select the first audio stream
             "-show_entries", "stream=codec_type", "-of", "default=noprint_wrappers=1:nokey=1", input_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        # If stdout is 'audio', it has an audio stream
        return result.stdout.strip().lower() == "audio"
    except FileNotFoundError:
        # ffprobe not found, can't check
        return True # Assume audio might be there if ffprobe isn't found? Or False? Let's return False as we can't confirm.
        # print(f"❌ Error: ffprobe not found during audio check.")
        # return False
    except Exception as e:
        print(f"❌ Unexpected error checking audio stream for {input_path}: {e}")
        return False


# --- Main Processing Loop ---
for input_path in file_paths:
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        continue

    print(f"\n--- Processing {os.path.basename(input_path)} ---")

    # === Step 1: Auto-edit video ===
    filename_base = os.path.splitext(os.path.basename(input_path))[0]
    input_dir = os.path.dirname(input_path)
    auto_edited_video = os.path.join(input_dir, f"{filename_base}_edited.mp4")

    auto_edit_cmd = [
        "auto-editor", input_path,
        "-o", auto_edited_video,
        "--no-open",
        "--frame-rate", "30",
        "--silent-speed", "99999"
        # auto-editor should preserve the audio stream by default
    ]

    print(f"⚙️ Auto-editing: {input_path}")
    try:
        # Let auto-editor print its own output
        subprocess.run(auto_edit_cmd, check=True)
        print(f"✅ Auto-edited video created: {auto_edited_video}")
    except FileNotFoundError:
         print(f"❌ Error: auto-editor not found. Make sure it's installed and in your PATH.")
         continue
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during auto-editing (return code {e.returncode}): {e}")
        print(f"   Command: {' '.join(e.cmd)}")
        # auto-editor prints errors to stderr usually, printing it helps debug
        if e.stderr: print(f"   Stderr/Stdout:\n{e.stderr}")
        continue
    except Exception as e:
         print(f"❌ Unexpected error during auto-editing: {e}")
         continue

    # Check if the intermediate video file was actually created
    if not os.path.exists(auto_edited_video):
        print(f"❌ Auto-edited video file was NOT created by auto-editor.")
        continue # Can't proceed without the file

    # Check: Verify intermediate video has audio
    print(f"🔍 Checking for audio stream in {os.path.basename(auto_edited_video)}...")
    has_audio = has_audio_stream(auto_edited_video)
    if not has_audio:
        print(f"⚠️ Warning: Auto-edited video '{os.path.basename(auto_edited_video)}' appears to have no audio track.")
        print("   Loudness normalization cannot be applied without audio.")
        # Decide if you want to skip the rest of the processing or proceed without audio
        # For now, let's continue, but the final video will have no audio.
        apply_loudnorm = False
    else:
        print(f"✅ Audio stream found in {os.path.basename(auto_edited_video)}.")
        apply_loudnorm = True # Proceed with audio processing


    # === Step 3: Center and pad the video AND normalize loudness ===
    duration_seconds = get_video_duration(auto_edited_video)
    if duration_seconds is None:
         print(f"Skipping final processing for {os.path.basename(auto_edited_video)} due to missing duration.")
         continue

    max_duration = duration_seconds # Use the actual duration
    final_output = os.path.join(input_dir, f"{filename_base}_final_normalized.mp4") # Changed output name

    ffmpeg_cmd = [
        ffmpeg_path,
        "-i", auto_edited_video,
        "-t", str(max_duration), # Use the actual duration
        "-vf", filter_complex_video, # Video filter for centering/padding
    ]

    # Add the audio filter ONLY if an audio stream was found
    if apply_loudnorm:
         ffmpeg_cmd.extend(["-af", filter_complex_audio])
    else:
        # If no audio stream, explicitly tell FFmpeg not to expect one,
        # otherwise it might throw an error or wait forever.
        # We should also copy the audio stream if apply_loudnorm is False
        # to preserve it if it *did* exist but ffprobe check failed.
        # However, the goal is normalization, so let's just skip audio entirely
        # if the check failed and warn the user.
        # If you wanted to copy the audio without normalization if the check failed,
        # you could use -c:a copy here, but that's complicated with potential -af.
        # Sticking to simple: if no audio found by check, no audio output.
        ffmpeg_cmd.append("-an") # No audio output stream


    # Add common encoding options and output file
    ffmpeg_cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        # Only add audio encoder if we are applying the filter (and thus have audio)
        "-c:a", "aac",
        "-b:a", "128k",
        "-y", # Overwrite output file without asking
        final_output
    ])

    print(f"🎬 Processing centered video with loudness normalization: {os.path.basename(final_output)}")
    if not apply_loudnorm:
        print("   (Note: Audio normalization skipped due to no audio stream detected)")

    # Print the FFmpeg command being executed (useful for debugging)
    # print("Executing FFmpeg command:", " ".join(ffmpeg_cmd))

    # --- Execute FFmpeg and capture output ---
    try:
        # Use check=True to raise CalledProcessError on failure
        # capture_output=True captures stdout and stderr
        result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)

        # Print FFmpeg's standard output (where it shows filtergraphs, loudnorm summary, etc.)
        if result.stdout:
            print("--- FFmpeg STDOUT ---")
            print(result.stdout)
            print("---------------------")

        print(f"✅ Final video saved: {final_output}")

    except FileNotFoundError:
         print(f"❌ Error: ffmpeg not found. Make sure it's installed and in your PATH.")
         # You might want to exit the loop or script here if ffmpeg is essential
         continue
    except subprocess.CalledProcessError as e:
        print(f"❌ Error processing final video (return code {e.returncode}):")
        print(f"   Command: {' '.join(e.cmd)}")
        print(f"--- FFmpeg STDERR ---")
        print(e.stderr) # FFmpeg errors usually go to stderr
        print("---------------------")
        # Print stdout as well, might contain useful info before the error
        if e.stdout:
             print("--- FFmpeg STDOUT (before error) ---")
             print(e.stdout)
             print("------------------------------------")
        continue # Continue to the next file if there was an error

    except Exception as e:
         print(f"❌ Unexpected error during final processing: {e}")
         continue


    # === Step 4: Clean up temp audio (if it were used) ===
    # The previous temp_audio file creation (Step 2) was commented out as it wasn't
    # used in the final FFmpeg command. Cleaning up the file path variable isn't needed.
    # If you ever reinstate Step 2, add cleanup code here using the temp_audio path.


    print("--------------------------------------------------")

print("\n✨ Processing complete for all selected files.")