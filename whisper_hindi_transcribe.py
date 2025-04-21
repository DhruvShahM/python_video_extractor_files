import sys
import json
from faster_whisper import WhisperModel

# Get the input audio path and output JSON file path from command-line arguments
audio_path = sys.argv[1]
output_path = sys.argv[2]

# Load the Whisper model (base size) with int8 precision on CPU
model = WhisperModel("base", device="cpu", compute_type="int8")

# Transcribe the audio in Hindi using beam search and get word timestamps
segments, _ = model.transcribe(audio_path, beam_size=5, word_timestamps=True, language="hi")


# Extract and structure words with timestamps
words = []
for segment in segments:
    for word in segment.words:
        words.append({
            "word": word.word.strip(),
            "start": word.start,
            "end": word.end
        })

# Save the result to a JSON file
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(words, f, indent=2, ensure_ascii=False)  # ensure_ascii=False keeps Hindi characters readable
