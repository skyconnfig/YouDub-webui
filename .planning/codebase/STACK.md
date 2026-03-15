# Technology Stack

## Languages & Runtime

- **Python**: 3.10+ (primary language)
- **Bash**: Windows batch scripts (.bat) for automation

## Core Frameworks

- **Gradio** (>=4.0.0): Web UI framework for the interactive interface
- **Loguru** (>=0.7.0): Structured logging
- **python-dotenv** (>=1.0.0): Environment variable management
- **requests** (>=2.31.0): HTTP client

## AI/ML Dependencies

### Speech Recognition
- **WhisperX**: Speech-to-text with word-level timestamps
- **openai-whisper**: OpenAI's Whisper model

### Audio Processing
- **Demucs**: Audio source separation (vocals/instruments)
- **scipy**: Signal processing
- **librosa**: Audio analysis
- **audiostretchy**: Audio time-stretching

### Text-to-Speech (TTS)
- **TTS** (>=0.22.0): Coqui TTS with XTTS voice cloning
- **gruut**: Text-to-speech preprocessing
- **pypinyin**: Chinese pinyin conversion

### Translation
- **OpenAI** (>=1.0.0): GPT models for translation
- Compatible with Groq API for faster inference

## Video Processing

- **yt-dlp** (>=2025.0.0): Video downloading from YouTube/other platforms

## Upload & Integration

- **bilibili_toolman** (>=1.0.7): Bilibili API integration for uploads

## System Utilities

- **psutil**: System resource monitoring

## Configuration

- Environment variables via `.env` file
- JSON configuration for terminology consistency

## Dependencies Not Included (Must Install Separately)

- **ffmpeg**: System-level video encoding (winget install Gyan.FFmpeg on Windows)
- **PyTorch**: With CUDA support for GPU acceleration (installed separately)

## File References

- Main entry: `app.py`
- Pipeline orchestration: `youdub/do_everything.py`
- Requirements: `requirements.txt`
- Environment template: `.env.example`
