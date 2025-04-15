// package main

// import (
// 	"encoding/json"
// 	"fmt"
// 	"os"
// 	"os/exec"
// 	"strings"
// 	"time"

// 	"github.com/sqweek/dialog"
// )

// type Word struct {
// 	Word  string  `json:"word"`
// 	Start float64 `json:"start"`
// 	End   float64 `json:"end"`
// }

// func formatTime(seconds float64) string {
// 	d := time.Duration(seconds * float64(time.Second))
// 	h := int(d.Hours())
// 	m := int(d.Minutes()) % 60
// 	s := int(d.Seconds()) % 60
// 	cs := int(d.Milliseconds()/10) % 100
// 	return fmt.Sprintf("%01d:%02d:%02d.%02d", h, m, s, cs)
// }

// func main() {
// 	// Step 1: Pick input video
// 	inputVideo, err := dialog.File().Title("Select Input Video").Filter("Video files", "mp4", "mov", "mkv").Load()
// 	if err != nil {
// 		fmt.Println("No input video selected. Exiting.")
// 		return
// 	}

// 	// Step 2: Pick output video
// 	outputVideo, err := dialog.File().Title("Save Output Video As").Filter("MP4 file", "mp4").Save()
// 	if err != nil {
// 		fmt.Println("No output file selected. Exiting.")
// 		return
// 	}
// 	if !strings.HasSuffix(strings.ToLower(outputVideo), ".mp4") {
// 		outputVideo += ".mp4"
// 	}

// 	// Step 3: Extract audio from video
// 	fmt.Println("🔊 Extracting audio...")
// 	audioPath := "temp.wav"
// 	cmd := exec.Command("ffmpeg", "-y", "-i", inputVideo, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audioPath)
// 	cmd.Stdout = os.Stdout
// 	cmd.Stderr = os.Stderr
// 	if err := cmd.Run(); err != nil {
// 		fmt.Println("FFmpeg audio extraction failed:", err)
// 		return
// 	}

// 	// Step 4: Run Vosk transcription (calls a helper Python script)
// 	fmt.Println("🧠 Transcribing using Vosk...")
// 	transcriptPath := "transcript.json"
// 	cmd = exec.Command("python", "whisper_transcribe.py", audioPath, transcriptPath)
// 	cmd.Stdout = os.Stdout
// 	cmd.Stderr = os.Stderr
// 	if err := cmd.Run(); err != nil {
// 		fmt.Println("Vosk transcription failed:", err)
// 		return
// 	}

// 	// Step 5: Read transcript
// 	data, err := os.ReadFile(transcriptPath)
// 	if err != nil {
// 		fmt.Println("Error reading transcript file:", err)
// 		return
// 	}
// 	var words []Word
// 	if err := json.Unmarshal(data, &words); err != nil {
// 		fmt.Println("Error parsing JSON:", err)
// 		return
// 	}

// 	// Step 6: Generate ASS subtitles
// 	assPath := "subtitles.ass"
// 	f, err := os.Create(assPath)
// 	if err != nil {
// 		panic(err)
// 	}
// 	defer f.Close()

// 	// header := `[Script Info]
// 	// Title: Animated Subs from Vosk
// 	// ScriptType: v4.00+
// 	// PlayDepth: 0
// 	// Timer: 100.0000

// 	// [V4+ Styles]
// 	// Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
// 	// Style: Default,Arial,18,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,1.5,0,2,20,20,60,1

// 	// [Events]
// 	// Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
// 	// `

// 	header := `[Script Info]
// Title: Animated Subs for Shorts
// ScriptType: v4.00+
// PlayDepth: 0
// Timer: 100.0000

// [V4+ Styles]
// Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
// Style: Default,Arial Black,18,&H00FFFF00,&H00000000,-1,0,0,0,100,100,0,0,1,4,1,8,20,20,200,1

// [Events]
// Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

// 	`
// 	f.WriteString(header)

// 	var line []Word
// 	maxWords := 4
// 	maxDuration := 3.0

// 	flushLine := func() {
// 		if len(line) == 0 {
// 			return
// 		}
// 		start := line[0].Start
// 		end := line[len(line)-1].End
// 		text := ""
// 		for _, w := range line {
// 			kDur := int((w.End - w.Start) * 100)
// 			text += fmt.Sprintf("{\\k%d}%s ", kDur, w.Word)
// 		}
// 		lineStr := fmt.Sprintf("Dialogue: 0,%s,%s,Default,,0,0,0,,%s\n", formatTime(start), formatTime(end), text)
// 		f.WriteString(lineStr)
// 		line = nil
// 	}

// 	for _, w := range words {
// 		if len(line) == 0 || len(line) < maxWords && w.End-line[0].Start <= maxDuration {
// 			line = append(line, w)
// 		} else {
// 			flushLine()
// 			line = append(line, w)
// 		}
// 	}
// 	flushLine()

// 	// Step 7: Generate final video
// 	fmt.Println("🎬 Generating final video with subtitles...")
// 	cmd = exec.Command("ffmpeg", "-y", "-i", inputVideo, "-vf", fmt.Sprintf("ass=%s", assPath), "-c:a", "copy", outputVideo)
// 	cmd.Stdout = os.Stdout
// 	cmd.Stderr = os.Stderr
// 	if err := cmd.Run(); err != nil {
// 		fmt.Println("FFmpeg subtitle burn failed:", err)
// 		return
// 	}

// 	// Cleanup
// 	os.Remove(audioPath)
// 	os.Remove(transcriptPath)
// 	os.Remove(assPath)

// 	fmt.Println("✅ Done! Output saved to:", outputVideo)
// }
