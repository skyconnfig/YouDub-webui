# External Integrations

## AI/ML APIs

### OpenAI API
- **Purpose**: Translation using GPT models
- **File**: `youdub/step030_translation.py`
- **Config**: `OPENAI_API_KEY`, `OPENAI_API_BASE`, `MODEL_NAME` in `.env`
- Supports Groq API for faster inference (compatible endpoint)

### HuggingFace
- **Purpose**: Whisper diarization models
- **File**: `youdub/step020_whisperx.py`
- **Config**: `HF_TOKEN` in `.env`
- Models downloaded from HuggingFace Hub

### Bytedance Volcano Engine
- **Purpose**: Cloud TTS (text-to-speech)
- **File**: `youdub/step041_tts_bytedance.py`
- **Config**: `BYTEDANCE_APPID`, `BYTEDANCE_ACCESS_TOKEN` in `.env`

## Video/Audio Processing

### YouTube (via yt-dlp)
- **Purpose**: Video downloading from YouTube and other platforms
- **File**: `youdub/step000_video_downloader.py`
- **Config**: `HTTP_PROXY`, `HTTPS_PROXY` for network access

### Demucs
- **Purpose**: Audio source separation (vocals vs instruments)
- **File**: `youdub/step010_demucs_vr.py`
- **Type**: Local ML model (via git+https://github.com/facebookresearch/demucs)

### WhisperX
- **Purpose**: Speech recognition with word-level timestamps
- **File**: `youdub/step020_whisperx.py`
- **Type**: Local ML model (via git+https://github.com/m-bain/whisperx.git)

### Coqui TTS (XTTS)
- **Purpose**: Voice cloning and TTS
- **File**: `youdub/step042_tts_xtts.py`
- **Type**: Local model (TTS>=0.22.0)

## Upload Integration

### Bilibili
- **Purpose**: Automated video upload to Bilibili
- **File**: `youdub/step070_upload_bilibili.py`
- **Config**: `BILI_SESSDATA`, `BILI_BILI_JCT`, `BILI_BASE64`
- **Library**: bilibili_toolman (>=1.0.7)
- Network handling: Proxy configuration via `NO_PROXY` for Bilibili domains

## Local Processing

### FFmpeg
- **Purpose**: Video encoding/decoding
- **Config**: `FFMPEG_PATH` (optional, if not in PATH)
- Must be installed separately (not Python package)

### PyTorch
- **Purpose**: ML model inference
- **Note**: GPU (CUDA) support recommended for performance
- Installed separately from requirements.txt

## Configuration Files

- `.env`: Main configuration (API keys, tokens)
- `.env.example`: Template with documented variables
- `config/terminology.json`: Custom translation terminology
- `config/bilibili.txt`: Bilibili upload configuration
- `config/cookies.txt`: Browser cookies for authentication
