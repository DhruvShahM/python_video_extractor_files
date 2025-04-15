// package main

// import (
// 	"encoding/json"
// 	"fmt"
// 	"os"
// 	"os/exec"
// 	"path/filepath"
// 	"strings"
// 	"time"

// 	"github.com/ncruces/zenity"
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

// func processVideo(inputVideo, outputVideo string) {
// 	fmt.Println("🔊 Extracting audio from:", inputVideo)
// 	audioPath := "temp.wav"
// 	cmd := exec.Command("ffmpeg", "-y", "-i", inputVideo, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audioPath)
// 	cmd.Stdout = os.Stdout
// 	cmd.Stderr = os.Stderr
// 	if err := cmd.Run(); err != nil {
// 		fmt.Println("FFmpeg audio extraction failed:", err)
// 		return
// 	}

// 	fmt.Println("🧠 Transcribing:", inputVideo)
// 	transcriptPath := "transcript.json"
// 	cmd = exec.Command("python", "whisper_hindi_transcribe.py", audioPath, transcriptPath)
// 	cmd.Stdout = os.Stdout
// 	cmd.Stderr = os.Stderr
// 	if err := cmd.Run(); err != nil {
// 		fmt.Println("Transcription failed:", err)
// 		return
// 	}

// 	data, err := os.ReadFile(transcriptPath)
// 	if err != nil {
// 		fmt.Println("Failed to read transcript:", err)
// 		return
// 	}
// 	var words []Word
// 	if err := json.Unmarshal(data, &words); err != nil {
// 		fmt.Println("JSON parse error:", err)
// 		return
// 	}

// 	assPath := "subtitles.ass"
// 	f, err := os.Create(assPath)
// 	if err != nil {
// 		fmt.Println("Subtitle file error:", err)
// 		return
// 	}
// 	defer f.Close()

// 	// Fullscreen subtitle style optimized for 1920x1080 videos
// 	header := `[Script Info]
// Title: Full Screen Subs
// ScriptType: v4.00+
// PlayResX: 1920
// PlayResY: 1080
// Timer: 100.0000

// [V4+ Styles]
// Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
// Style: FullScreen,Mangal,60,&H00FFFF&,&H64000000,-1,0,0,0,100,100,0,0,1,3,1,2,50,50,100,1

// [Events]
// Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
// `
// 	f.WriteString(header)

// 	var line []Word
// 	const maxWordsPerLine = 3
// 	const maxDurationPerLine = 5.0 // seconds

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
// 		lineStr := fmt.Sprintf("Dialogue: 0,%s,%s,FullScreen,,0,0,0,,%s\n", formatTime(start), formatTime(end), strings.TrimSpace(text))
// 		f.WriteString(lineStr)
// 		line = nil
// 	}

// 	for _, w := range words {
// 		if len(line) < maxWordsPerLine && (len(line) == 0 || w.End-line[0].Start <= maxDurationPerLine) {
// 			line = append(line, w)
// 		} else {
// 			flushLine()
// 			line = append(line, w)
// 		}
// 	}
// 	flushLine()

// 	fmt.Println("🎬 Burning subtitles into video...")
// 	cmd = exec.Command("ffmpeg", "-y", "-i", inputVideo, "-vf", fmt.Sprintf("ass=%s", assPath), "-c:a", "copy", outputVideo)
// 	cmd.Stdout = os.Stdout
// 	cmd.Stderr = os.Stderr
// 	if err := cmd.Run(); err != nil {
// 		fmt.Println("FFmpeg subtitle burn failed:", err)
// 		return
// 	}

// 	os.Remove(audioPath)
// 	os.Remove(transcriptPath)
// 	os.Remove(assPath)

// 	fmt.Println("✅ Done:", outputVideo)
// }

// func main() {
// 	// Select multiple video files
// 	inputVideos, err := zenity.SelectFileMultiple(
// 		zenity.Title("Select Input Videos"),
// 		zenity.FileFilter{Name: "Videos", Patterns: []string{"*.mp4", "*.mov", "*.mkv"}},
// 	)
// 	if err != nil || len(inputVideos) == 0 {
// 		fmt.Println("No input videos selected.")
// 		return
// 	}

// 	// Select output folder
// 	outputDir, err := zenity.SelectFile(
// 		zenity.Title("Select Output Folder"),
// 		zenity.Directory(),
// 	)
// 	if err != nil || outputDir == "" {
// 		fmt.Println("No output folder selected.")
// 		return
// 	}

// 	// Process videos one-by-one
// 	for _, input := range inputVideos {
// 		base := strings.TrimSuffix(filepath.Base(input), filepath.Ext(input))
// 		output := filepath.Join(outputDir, base+"_subtitled.mp4")
// 		processVideo(input, output)
// 	}

// 	fmt.Println("🎉 All videos processed!")
// }
