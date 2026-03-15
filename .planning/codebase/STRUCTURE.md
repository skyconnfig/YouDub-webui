# YouDub-webui Structure

## Directory Layout

D:/YouDub-webui/
├── .env                          # Environment variables (API keys, secrets)
├── .env.example                  # Template for .env
├── .gitignore                    # Git ignore rules
├── AGENTS.md                     # AI agent guidelines
├── README.md                     # Project README
├── TODO.md                       # Todo list
├── app.py                        # Main entry point - Gradio web UI
├── requirements.txt              # Python dependencies
├── auto_config.json              # Auto-configuration
├── package.json                  # Node.js dependencies (for yt-dlp player)
│
├── .gradio/                      # Gradio temporary files
├── .planning/                    # Planning documentation
│   └── codebase/                 # Codebase documentation
│       ├── ARCHITECTURE.md       # Architecture documentation
│       └── STRUCTURE.md          # This file
│
├── .sisyphus/                    # Sisyphus (CI/CD) files
├── .vscode/                      # VSCode settings
│
├── config/                       # Configuration files
│   ├── bilibili.txt              # Bilibili credentials
│   ├── cookies.txt               # YouTube cookies for authentication
│   ├── terminology.json          # Custom translation terminology
│   └── terminology.json.example  # Template for terminology
│
├── docs/                         # Documentation
│
├── ffmpeg/                       # FFmpeg binaries (optional)
│   └── bin/
│       ├── ffmpeg.exe
│       └── ffprobe.exe
│
├── models/                       # Local model storage
│   ├── ASR/
│   │   └── whisper/              # Whisper models
│   ├── Demucs/                   # Demucs source separation models
│   ├── hf_cache/                 # HuggingFace cache
│   ├── TTS/                      # TTS models
│   └── torch_hub/                # PyTorch Hub models
│
├── scripts/                      # Build and setup scripts
│   └── setup_windows.bat         # Windows setup script
│
├── tools/                        # Utility tools
│
├── videos/                       # Working directory - video processing
│   └── {uploader}/
│       └── {date} {title}/
│           ├── download.mp4
│           ├── audio.wav
│           └── ...
│
└── youdub/                       # Main Python package
    ├── __init__.py               # Package init (empty)
    │
    ├── do_everything.py         # Pipeline orchestration
    │
    ├── utils.py                  # Utility functions
    │   ├── sanitize_filename()  # Clean filenames
    │   ├── save_wav()           # Save audio to WAV
    │   ├── save_wav_norm()      # Save normalized audio
    │   └── normalize_wav()     # Normalize audio
    │
    ├── terminology.py            # Translation terminology manager
    │   ├── DEFAULT_TERMINOLOGY  # 500+ AI/tech terms
    │   └── TerminologyManager   # Term management class
    │
    ├── cn_tx.py                  # Chinese text normalization
    │   ├── TextNorm             # Main normalizer class
    │   ├── chn2num()            # Chinese to number
    │   ├── num2chn()            # Number to Chinese
    │   └── normalize_nsw()      # Normalize numbers/symbols
    │
    ├── step000_video_downloader.py    # Video download (yt-dlp)
    │   ├── download_from_url()        # Main entry
    │   ├── get_info_list_from_url()   # Extract video info
    │   ├── download_single_video()    # Download single video
    │   ├── get_target_folder()         # Get output folder
    │   ├── sanitize_title()            # Clean title
    │   ├── find_cookies_file()         # Find cookies
    │   ├── get_ydl_opts()              # yt-dlp options
    │   └── DENO_PATH                  # Deno runtime setup
    │
    ├── step010_demucs_vr.py           # Audio separation (Demucs)
    │   ├── separate_all_audio_under_folder()
    │   ├── separate_audio()           # Separate single video
    │   ├── extract_audio_from_video() # Extract audio from video
    │   ├── check_ffmpeg()             # Check ffmpeg
    │   ├── load_model()               # Load Demucs model
    │   ├── init_demucs()              # Initialize Demucs
    │   └── separator                  # Global model state
    │
    ├── step020_whisperx.py            # Speech recognition
    │   ├── transcribe_all_audio_under_folder()
    │   ├── transcribe_audio()         # Transcribe single audio
    │   ├── load_whisper_model()       # Load Whisper
    │   ├── load_align_model()         # Load alignment model
    │   ├── load_diarize_model()      # Load diarization
    │   ├── merge_segments()          # Merge segments
    │   ├── generate_speaker_audio()  # Extract speaker samples
    │   ├── whisper_model              # Global model
    │   └── diarize_model             # Global model
    │
    ├── step030_translation.py         # LLM translation
    │   ├── translate_all_transcript_under_folder()
    │   ├── translate()                # Translate single video
    │   ├── _translate()               # Core translation
    │   ├── summarize()                # Generate video summary
    │   ├── split_sentences()          # Split by sentences
    │   ├── valid_translation()        # Validate translation
    │   ├── translation_postprocess()  # Post-process
    │   ├── get_translation_client()   # Get LLM client
    │   ├── get_terminology_manager()  # Get term manager
    │   └── TRANSLATION_BACKEND        # Config: ollama/groq/openai
    │
    ├── step040_tts.py                 # TTS orchestration
    │   ├── generate_all_wavs_under_folder()
    │   ├── generate_wavs()            # Generate TTS for video
    │   ├── preprocess_text()          # Clean text for TTS
    │   ├── adjust_audio_length()      # Match timing
    │   ├── _get_bytedance_tts()      # Lazy load Bytedance
    │   └── _get_xtts_tts()           # Lazy load XTTS
    │
    ├── step041_tts_bytedance.py       # Bytedance Cloud TTS
    │   ├── tts()                      # Generate speech
    │   ├── generate_embedding()      # Speaker embedding
    │   ├── generate_speaker_to_voice_type()
    │   ├── get_available_speakers()  # List voices
    │   ├── _init_pyannote()          # Lazy load pyannote
    │   └── BYTEDANCE_APPID, ACCESS_TOKEN
    │
    ├── step042_tts_xtts.py            # XTTS Local TTS
    │   ├── tts()                      # Generate speech
    │   ├── load_model()              # Load XTTS model
    │   ├── init_TTS()                # Initialize TTS
    │   ├── clean_quotes()            # Clean quotes
    │   ├── dedup_repeated_sentences() # Remove LLM repetition
    │   ├── model                     # Global model
    │   └── model_lock                # Thread lock for GPU
    │
    ├── step050_synthesize_video.py   # Video synthesis
    │   ├── synthesize_all_video_under_folder()
    │   ├── synthesize_video()        # Synthesize single video
    │   ├── get_ffmpeg_path()        # Find ffmpeg
    │   ├── get_video_encoder_config() # Get encoder (NVENC/x264)
    │   ├── get_audio_encoder_config() # AAC encoder
    │   ├── generate_srt()           # Generate subtitles
    │   ├── split_text()             # Split text for subs
    │   ├── get_aspect_ratio()       # Get video aspect ratio
    │   └── convert_resolution()     # Calculate resolution
    │
    ├── step060_genrate_info.py      # Metadata generation
    │   ├── generate_all_info_under_folder()
    │   ├── generate_info()          # Generate for single video
    │   ├── resize_thumbnail()      # Resize thumbnail
    │   └── generate_summary_txt()   # Generate summary file
    │
    └── step070_upload_bilibili.py    # Bilibili upload
        ├── upload_all_videos_under_folder()
        ├── upload_video()           # Upload single video
        ├── bili_login()            # Create session
        ├── check_upload_permission() # Check account status
        └── Submission              # bilibili-toolman class
