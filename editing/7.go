package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/ncruces/zenity"
)

type Word struct {
	Word  string  `json:"word"`
	Start float64 `json:"start"`
	End   float64 `json:"end"`
}

func formatTime(seconds float64) string {
	d := time.Duration(seconds * float64(time.Second))
	h := int(d.Hours())
	m := int(d.Minutes()) % 60
	s := int(d.Seconds()) % 60
	cs := int(d.Milliseconds()/10) % 100
	return fmt.Sprintf("%01d:%02d:%02d.%02d", h, m, s, cs)
}

func getVideoDuration(filePath string) (float64, error) {
	cmd := exec.Command("ffprobe", "-v", "error", "-show_entries", "format=duration",
		"-of", "json", filePath)

	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	if err != nil {
		return 0, err
	}

	var result struct {
		Format struct {
			Duration string `json:"duration"`
		} `json:"format"`
	}
	if err := json.Unmarshal(out.Bytes(), &result); err != nil {
		return 0, err
	}

	return strconv.ParseFloat(result.Format.Duration, 64)
}

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

	header := `[Script Info]
Title: Animated Subs
ScriptType: v4.00+
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,16,&H00FFFF,&H40000000,-1,0,0,0,100,100,0,0,1,1,0,2,20,20,65,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

`
	f.WriteString(header)

	var line []Word
	const maxWordsPerLine = 3
	const maxDurationPerLine = 5.0

	flushLine := func() {
		if len(line) == 0 {
			return
		}
		start := line[0].Start
		end := line[len(line)-1].End
		text := ""
		for i, w := range line {
			kDur := int((w.End - w.Start) * 100)
			if i == 0 {
				text += fmt.Sprintf("{\\k%d}{\\c&HFFFFFF&}%s ", kDur, w.Word)
			} else {
				text += fmt.Sprintf("{\\k%d}{\\c&H00FFFF&}%s ", kDur, w.Word)
			}
		}
		lineStr := fmt.Sprintf("Dialogue: 0,%s,%s,Default,,0,0,0,,%s\n", formatTime(start), formatTime(end), text)
		f.WriteString(lineStr)
		line = nil
	}

	for _, w := range words {
		if len(line) < maxWordsPerLine && (len(line) == 0 || w.End-line[0].Start <= maxDurationPerLine) {
			line = append(line, w)
		} else {
			flushLine()
			line = append(line, w)
		}
	}
	flushLine()

	fmt.Println("🎬 Burning subtitles and overlaying GIFs...")
	duration, err := getVideoDuration(inputVideo)
	if err != nil {
		log.Fatal("Error getting video duration:", err)
	}
	startSecond := duration - 10
	overlayEnable := fmt.Sprintf("enable='lt(t,15)+gte(t,%.2f)'", startSecond)

	// cmd = exec.Command("ffmpeg", "-y",
	// 	"-i", inputVideo,
	// 	"-ignore_loop", "0", "-i", "Subscribe.gif",
	// 	"-filter_complex",
	// 	fmt.Sprintf(
	// 		"[0:v][1:v]overlay=10:10:enable='between(t,2,10)',ass=%s", assPath),
	// 	"-map", "0:a",
	// 	"-c:v", "libx264", "-crf", "23", "-preset", "fast",
	// 	"-c:a", "aac", "-shortest",
	// 	outputVideo)

	// only subscirbe button with infinite loop
	// cmd = exec.Command("ffmpeg", "-y",
	// 	"-i", inputVideo,
	// 	"-stream_loop", "-1", "-i", "new_subscribe.gif", // 👈 Infinite loop GIF
	// 	"-filter_complex",
	// 	fmt.Sprintf("[0:v][1:v]overlay=10:10:enable='gte(t,1)',ass=%s", assPath),
	// 	"-map", "0:a",
	// 	"-c:v", "libx264", "-crf", "23", "-preset", "fast",
	// 	"-c:a", "aac", "-shortest",
	// 	outputVideo)

	// From the start (0s) to 15s, and
	// From the last 10 seconds of the video (i.e., duration - 10 to duration)
	cmd = exec.Command("ffmpeg", "-y",
		"-i", inputVideo,
		"-stream_loop", "-1", "-i", "new_subscribe.gif",
		"-filter_complex",
		fmt.Sprintf("[0:v][1:v]overlay=10:10:%s,ass=%s", overlayEnable, assPath),
		"-map", "0:a",
		"-c:v", "libx264", "-crf", "23", "-preset", "fast",
		"-c:a", "aac", "-shortest",
		outputVideo)

	// cmd = exec.Command("ffmpeg", "-y",
	// 	"-i", inputVideo,
	// 	"-stream_loop", "-1", "-i", "Subscribe.gif",
	// 	"-stream_loop", "-1", "-i", "Like.gif",
	// 	"-filter_complex",
	// 	fmt.Sprintf(
	// 		`[0:v][1:v]overlay=10:10:enable='between(mod(t\,10)\,0\,5)'[tmp1];
	// 	 [tmp1][2:v]overlay=10:100:enable='between(mod(t\,10)\,5\,10)',ass=%s`,
	// 		assPath),
	// 	"-map", "0:a",
	// 	"-c:v", "libx264", "-crf", "23", "-preset", "fast",
	// 	"-c:a", "aac", "-shortest",
	// 	outputVideo)

	// multiple gifs
	// cmd = exec.Command("ffmpeg", "-y",
	// 	"-i", inputVideo,
	// 	"-stream_loop", "-1", "-i", "Subscribe.gif",
	// 	"-stream_loop", "-1", "-i", "Like.gif",
	// 	"-filter_complex",
	// 	fmt.Sprintf(
	// 		`[0:v][1:v]overlay=10:10:enable='between(mod(t\,10)\,0\,5)'[tmp1];
	// 	 [2:v]crop=iw:ih-90[like_cropped];
	// 	 [tmp1][like_cropped]overlay=10:100:enable='between(mod(t\,10)\,5\,10)',ass=%s`,
	// 		assPath),
	// 	"-map", "0:a",
	// 	"-c:v", "libx264", "-crf", "23", "-preset", "fast",
	// 	"-c:a", "aac", "-shortest",
	// 	outputVideo)

	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		fmt.Println("FFmpeg subtitle burn failed:", err)
		return
	}

	os.Remove(audioPath)
	os.Remove(transcriptPath)
	os.Remove(assPath)

	fmt.Println("✅ Done:", outputVideo)
}

func main() {
	os.Setenv("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
	inputVideos, err := zenity.SelectFileMultiple(
		zenity.Title("Select Input Videos"),
		zenity.FileFilter{Name: "Videos", Patterns: []string{"*.mp4", "*.mov", "*.mkv"}},
	)
	if err != nil || len(inputVideos) == 0 {
		fmt.Println("No input videos selected.")
		return
	}

	outputDir, err := zenity.SelectFile(
		zenity.Title("Select Output Folder"),
		zenity.Directory(),
	)
	if err != nil || outputDir == "" {
		fmt.Println("No output folder selected.")
		return
	}

	for _, input := range inputVideos {
		base := strings.TrimSuffix(filepath.Base(input), filepath.Ext(input))
		output := filepath.Join(outputDir, base+"_subtitled.mp4")
		processVideo(input, output)
	}

	fmt.Println("🎉 All videos processed!")
}

// Also, if you want to display the GIF continuously, not just between 2s and 10s, you should remove the enable='between(t,2,10)' part from the overlay filter.

// Perfect — you want to show the Subscribe.gif only from 25s to 35s during your 60-second video.

// You can do that using FFmpeg’s enable='between(t,25,35)' in the overlay filter.

// First 15 seconds: lt(t,15)

// Last 10 seconds: gte(t, duration-10)

// You dynamically inject duration in the Go code.

// Let me know if you also want to fade in/out the GIF during these segments!
