# AGENTS.md - YouDub-webui

Guidelines for AI agents working in this repository.

## Project Overview

**YouDub-webui** is a Python web UI for video dubbing/translation using Gradio. It downloads videos from YouTube, transcribes audio with Whisper, translates with LLMs, synthesizes speech with TTS, and uploads to Bilibili.

## Build/Run Commands

```bash
# Setup virtual environment and install dependencies
setup_windows.bat              # Windows automated setup

# Run the application
python app.py                  # Start Gradio web UI
run_windows.bat               # Windows shortcut

# Manual dependency installation
pip install -r requirements.txt
pip install TTS               # TTS must be installed separately
```

## Code Style Guidelines

### Imports
- Group imports: stdlib → third-party → local
- Use relative imports within the `youdub` package (`from .module import func`)
- Example:
```python
import os
import json

from loguru import logger

from .step000_video_downloader import download_from_url
```

### Naming Conventions
- Functions: `snake_case` (e.g., `download_single_video`)
- Modules: `snake_case` with step prefixes (e.g., `step000_video_downloader.py`)
- Constants: UPPER_CASE in `.env` file
- Variables: `snake_case`

### Type Hints
- Use type hints for function parameters and return values where clear
- Example: `def sanitize_filename(filename: str) -> str:`

### Logging
- Use `loguru` logger exclusively: `from loguru import logger`
- Log levels: `logger.info()`, `logger.warning()`, `logger.error()`

### Error Handling
- Use try/except blocks with specific exceptions
- Log errors with context before returning/raising
- Check for file existence before operations
- Gracefully handle missing optional dependencies

### Code Patterns

**Step Modules Pattern:**
Each step module exposes a main function that processes a folder:
```python
def process_all_under_folder(folder: str, **options) -> None:
    """Process all items in the given folder."""
    pass
```

**Folder Structure:**
```
videos/
└── {uploader}/
    └── {date} {title}/
        ├── download.mp4       # Downloaded video
        ├── vocals.wav         # Separated vocals
        ├── video.json         # Metadata
        ├── video.ass          # Subtitles
        └── ...
```

## Testing

This project has no formal test suite. To verify changes:

1. **Manual testing:** Run the specific step function with test data
2. **Integration testing:** Run `python app.py` and test via Gradio UI
3. **Check imports:** `python -c "from youdub import *"`

## Environment Setup

1. Copy `.env.example` to `.env`
2. Configure required API keys:
   - `OPENAI_API_KEY` - For translation
   - `HF_TOKEN` - For Whisper diarization
   - `BYTEDANCE_APPID`/`BYTEDANCE_ACCESS_TOKEN` - For TTS
   - `BILI_BASE64` - For Bilibili upload

## Important Notes

- The app uses Gradio for the web interface (see `app.py`)
- Processing is sequential: Download → Demucs → Whisper → Translate → TTS → Synthesize → Upload
- Heavy dependencies (demucs, whisperx, TTS) are imported lazily in functions, not at module level
- Windows batch scripts (.bat) are provided for convenience
- Virtual environment is recommended (created by setup_windows.bat)

## File Organization

```
youdub/
├── __init__.py
├── step000_video_downloader.py    # Video download
├── step010_demucs_vr.py           # Audio separation
├── step020_whisperx.py            # Speech recognition
├── step030_translation.py         # LLM translation
├── step040_tts.py                 # TTS orchestration
├── step041_tts_bytedance.py       # Bytedance TTS
├── step042_tts_xtts.py            # XTTS TTS
├── step050_synthesize_video.py    # Final video generation
├── step060_genrate_info.py        # Metadata generation
├── step070_upload_bilibili.py     # Upload to Bilibili
├── utils.py                       # Utility functions
└── do_everything.py               # Pipeline orchestration
```
