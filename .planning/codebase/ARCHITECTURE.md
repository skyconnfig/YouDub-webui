# YouDub-webui Architecture

## Overview

YouDub-webui is a Python-based video dubbing/translation pipeline that downloads videos from YouTube and other platforms, transcribes audio using Whisper, translates content using LLMs, synthesizes speech using TTS (both cloud and local), and uploads the dubbed videos to Bilibili.

## Design Pattern: Sequential Pipeline Architecture

The application follows a sequential pipeline pattern where each step processes video data in a strict order. Each step module exposes a consistent interface and can be executed independently or as part of the full pipeline.

### Pipeline Steps

| Step | Module | Function | Description |
|------|--------|----------|-------------|
| 0 | step000_video_downloader.py | download_from_url | Download videos from URL (YouTube, Bilibili, etc.) using yt-dlp |
| 1 | step010_demucs_vr.py | separate_all_audio_under_folder | Audio source separation using Demucs (vocals vs instruments) |
| 2 | step020_whisperx.py | transcribe_all_audio_under_folder | Speech recognition using WhisperX with diarization |
| 3 | step030_translation.py | translate_all_transcript_under_folder | LLM-based translation using OpenAI/Groq/Ollama |
| 4 | step040_tts.py | generate_all_wavs_under_folder | TTS orchestration - delegates to Bytedance or XTTS |
| 5 | step041_tts_bytedance.py | tts | Bytedance Cloud TTS API |
| 6 | step042_tts_xtts.py | tts | Coqui XTTS local TTS model |
| 7 | step050_synthesize_video.py | synthesize_all_video_under_folder | Combine audio + video + subtitles using ffmpeg |
| 8 | step060_genrate_info.py | generate_all_info_under_folder | Generate metadata (thumbnail, summary text) |
| 9 | step070_upload_bilibili.py | upload_all_videos_under_folder | Upload to Bilibili using bilibili-toolman |

## Architecture Layers

### 1. UI Layer (Presentation)
**Location**: D:/YouDub-webui/app.py

- Gradio-based web interface
- Tabbed interface with separate tabs for each pipeline step
- Single entry point: app.launch()
- Each pipeline step has its own Gradio Interface

### 2. Orchestration Layer
**Location**: D:/YouDub-webui/youdub/do_everything.py

- Main orchestration function: do_everything()
- Handles parallel video processing using ThreadPoolExecutor
- Initializes ML models before processing (Demucs, WhisperX, XTTS)
- Manages GPU memory clearing between pipeline stages
- Handles retry logic and error recovery

### 3. Processing Layer (Step Modules)
**Location**: D:/YouDub-webui/youdub/step*.py

Each step module follows a consistent pattern:

Ctrl click to launch VS Code Native REPL

### 4. Utility Layer
**Location**: D:/YouDub-webui/youdub/

- utils.py - Audio file utilities (save_wav, normalize_wav)
- terminology.py - Translation terminology management (500+ AI/tech terms)
- cn_tx.py - Chinese text normalization (numbers, dates, money, etc.)

## Data Flow

### Input
- Video URL (YouTube, Bilibili, etc.)
- Processing parameters (resolution, models, languages, etc.)

### Processing Pipeline

URL -> Download -> Audio Separation -> Transcription -> Translation -> TTS Generation -> Video Synthesis -> Metadata -> Upload

### Intermediate Files (per video folder)

videos/{uploader}/{date} {title}/
├── download.mp4              # Original video (Step 0)
├── download.webm             # Alternative format
├── download.info.json        # Video metadata from yt-dlp
├── download.jpg/.png         # Thumbnail
├── audio.wav                 # Extracted audio (Step 1)
├── audio_vocals.wav          # Separated vocals (Step 1)
├── audio_instruments.wav     # Separated instruments (Step 1)
├── transcript.json           # Whisper output (Step 2)
├── summary.json              # Video summary (Step 3)
├── translation.json          # Translated subtitles (Step 3)
├── wavs/                     # Individual TTS segments (Step 4)
│   ├── 0000.wav
│   └── ...
├── audio_tts.wav             # Concatenated TTS audio (Step 4)
├── audio_combined.wav        # TTS + instruments (Step 4)
├── subtitles.srt             # Subtitle file (Step 5)
├── video.mp4                 # Final dubbed video (Step 5)
├── video.png                 # Thumbnail (Step 6)
├── video.txt                 # Summary text (Step 6)
└── bilibili.json            # Upload result (Step 7)

## Key Abstractions

### 1. Lazy Import Pattern
Heavy ML dependencies are imported lazily inside functions to avoid import-time errors.

### 2. Global Model State
ML models are cached in global variables to avoid reloading.

### 3. Idempotent Processing
Each step checks for existing output before processing.

### 4. Configuration via Environment Variables
All API keys and paths are configured via .env file.

### 5. Terminology Management
Translation module uses TerminologyManager for consistent terminology.

## Entry Points

### Primary Entry Point
**File**: D:/YouDub-webui/app.py

python app.py

Launches Gradio web UI with tabbed interface.

### Programmatic Entry Point
**File**: D:/YouDub-webui/youdub/do_everything.py

from youdub.do_everything import do_everything
do_everything(root_folder='videos', url='https://youtube.com/...', ...)

### Individual Step Entry Points
Each step can be run independently through Gradio or programmatically.

## Error Handling

### Retry Logic
- Translation: 30 retries per segment
- TTS: 3 retries per segment
- Upload: 5 retries per video

### GPU Memory Management
Called after each heavy ML step (Demucs, WhisperX, TTS).

### Graceful Degradation
- Missing ffmpeg: Detailed installation guide provided
- Missing Deno: Warning with installation instructions
- API failures: Detailed error messages with solutions

## Dependencies

### Core Dependencies
- gradio - Web UI
- yt-dlp - Video downloading
- demucs - Audio separation
- whisperx - Speech recognition
- openai - LLM translation (also supports Groq, Ollama)
- TTS - XTTS TTS (local)
- bilibili-toolman - Bilibili upload
- ffmpeg - Video processing (external)

### Utility Dependencies
- loguru - Logging
- python-dotenv - Environment configuration
- scipy, librosa - Audio processing
- PIL - Image processing
