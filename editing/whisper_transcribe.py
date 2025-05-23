import sys
import json
from faster_whisper import WhisperModel

audio_path = sys.argv[1]
output_path = sys.argv[2]
# large-v3
model = WhisperModel("medium", compute_type="float16")  # or "int8" for less VRAM
segments, _ = model.transcribe(audio_path, beam_size=5, word_timestamps=True)

words = []
for segment in segments:
    for word in segment.words:
        words.append({
            "word": word.word.strip(),
            "start": word.start,
            "end": word.end
        })

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(words, f, indent=2)
