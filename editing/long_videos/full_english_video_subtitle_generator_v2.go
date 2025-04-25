package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/ncruces/zenity"
)

// Word represents a transcribed word with its timing.
type Word struct {
	Word  string  `json:"word"`
	Start float64 `json:"start"`
	End   float64 `json:"end"`
}

// formatTime converts seconds to ASS time format (H:MM:SS.cs).
func formatTime(seconds float64) string {
	d := time.Duration(seconds * float64(time.Second))
	h := int(d.Hours())
	m := int(d.Minutes()) % 60
	s := int(d.Seconds()) % 60
	cs := int(d.Milliseconds()/10) % 100 // Centiseconds
	return fmt.Sprintf("%01d:%02d:%02d.%02d", h, m, s, cs)
}

// processVideo extracts audio, transcribes it, generates ASS subtitles, and burns them into the video.
func processVideo(inputVideo, outputVideo string) {
	fmt.Println("🔊 Extracting audio from:", inputVideo)
	audioPath := "temp.wav"
	cmd := exec.Command("ffmpeg", "-y", "-i", inputVideo, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audioPath)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		fmt.Println("FFmpeg audio extraction failed:", err)
		return
	}

	fmt.Println("🧠 Transcribing:", inputVideo)
	transcriptPath := "transcript.json"
	// Ensure whisper_transcribe.py is in the same directory or adjust the path
	cmd = exec.Command("python", "whisper_transcribe.py", audioPath, transcriptPath)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		fmt.Println("Transcription failed:", err)
		return
	}

	data, err := os.ReadFile(transcriptPath)
	if err != nil {
		fmt.Println("Failed to read transcript:", err)
		return
	}
	var words []Word
	if err := json.Unmarshal(data, &words); err != nil {
		fmt.Println("JSON parse error:", err)
		return
	}

	assPath := "subtitles.ass"
	f, err := os.Create(assPath)
	if err != nil {
		fmt.Println("Subtitle file error:", err)
		return
	}
	defer f.Close()

	// ASS subtitle style optimized for 1920x1080 videos with a bold, white,
	// rounded-looking (renderer dependent) text and a semi-transparent black background box.
	// This style is based on the "Bold Rounded Highlight Subtitle" description.
	header := `[Script Info]
Title: Bold Rounded Highlight Subtitle
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
Timer: 100.0000
ScaledBorderAndShadow: yes ; Recommended for consistent appearance across renderers

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: FullScreen,Montserrat,60,&H00FFFFFF&,&H000000FF&,&H00000000&,&H33000000&,-1,0,0,0,100,100,0,0,3,3,1,2,50,50,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
`
	f.WriteString(header)

	var line []Word
	const maxWordsPerLine = 5      // Adjusted for potentially longer lines with background
	const maxDurationPerLine = 4.0 // Adjusted duration limit

	flushLine := func() {
		if len(line) == 0 {
			return
		}
		start := line[0].Start
		end := line[len(line)-1].End
		text := ""
		for _, w := range line {
			// \\k duration is in centiseconds
			kDur := int((w.End - w.Start) * 100)
			// Use {\kX} for karaoke effect (highlighting)
			text += fmt.Sprintf("{\\k%d}%s ", kDur, w.Word)
		}
		// Remove trailing space and format as ASS Dialogue line
		lineStr := fmt.Sprintf("Dialogue: 0,%s,%s,FullScreen,,0,0,0,,%s\n", formatTime(start), formatTime(end), strings.TrimSpace(text))
		f.WriteString(lineStr)
		line = nil
	}

	for _, w := range words {
		// Basic line breaking logic based on word count and duration
		if len(line) < maxWordsPerLine && (len(line) == 0 || w.End-line[0].Start <= maxDurationPerLine) {
			line = append(line, w)
		} else {
			flushLine()
			line = append(line, w)
		}
	}
	flushLine() // Flush any remaining words in the last line

	fmt.Println("🎬 Burning subtitles into video...")
	// Use the ASS filter to burn the subtitles
	cmd = exec.Command("ffmpeg", "-y", "-i", inputVideo, "-vf", fmt.Sprintf("ass=%s", assPath), "-c:a", "copy", outputVideo)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		fmt.Println("FFmpeg subtitle burn failed:", err)
		return
	}

	// Clean up temporary files
	os.Remove(audioPath)
	os.Remove(transcriptPath)
	os.Remove(assPath)

	fmt.Println("✅ Done:", outputVideo)
}

func main() {
	// Select multiple video files using a file dialog
	inputVideos, err := zenity.SelectFileMultiple(
		zenity.Title("Select Input Videos"),
		zenity.FileFilter{Name: "Videos", Patterns: []string{"*.mp4", "*.mov", "*.mkv"}},
	)
	if err != nil || len(inputVideos) == 0 {
		fmt.Println("No input videos selected or an error occurred:", err)
		return
	}

	// Select output folder using a directory dialog
	outputDir, err := zenity.SelectFile(
		zenity.Title("Select Output Folder"),
		zenity.Directory(),
	)
	if err != nil || outputDir == "" {
		fmt.Println("No output folder selected or an error occurred:", err)
		return
	}

	// Process videos one-by-one
	for _, input := range inputVideos {
		base := strings.TrimSuffix(filepath.Base(input), filepath.Ext(input))
		output := filepath.Join(outputDir, base+"_subtitled.mp4")
		processVideo(input, output)
	}

	fmt.Println("🎉 All videos processed!")
}
