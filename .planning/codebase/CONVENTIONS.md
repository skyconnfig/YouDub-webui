# Coding Conventions

## Import Organization

Follow this order in all Python files:
1. Standard library imports (os, json, re, etc.)
2. Third-party imports (loguru, requests, gradio, etc.)
3. Local imports (from .module import func)

Example from `youdub/step020_whisperx.py`:
```python
import os
from pathlib import Path
from typing import Any

import whisperx
from loguru import logger
```

## Naming Conventions

- **Functions**: snake_case (e.g., `download_single_video`, `process_all_under_folder`)
- **Modules**: snake_case with step prefixes (e.g., `step000_video_downloader.py`)
- **Constants**: UPPER_CASE in `.env` file
- **Variables**: snake_case

## Type Hints

Use type hints for function parameters and return values where clear.

Example: `def sanitize_filename(filename: str) -> str:`

## Logging

Use `loguru` logger exclusively:
```python
from loguru import logger
logger.info("Processing video")
logger.warning("Missing audio track")
logger.error(f"Failed to download: {e}")
```

## Error Handling

- Use try/except blocks with specific exceptions
- Log errors with context before returning/raising
- Check for file existence before operations
- Gracefully handle missing optional dependencies

## Code Patterns

### Step Modules Pattern
Each step module exposes a main function that processes a folder:

```python
def process_all_under_folder(folder: str, **options) -> None:
    """Process all items in the given folder."""
    pass
```

### Folder Structure
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

### Lazy Imports
Heavy dependencies (demucs, whisperx, TTS) are imported lazily in functions, not at module level. This prevents slow startup and avoids importing ML libraries until needed.

Example:
```python
# Don't do this at module level:
# import demucs  # Slow!

# Do this inside functions:
def process_audio():
    import demucs  # Only imports when needed
    # ...
```

## File References

- Main entry: `app.py`
- Step modules: `youdub/step*.py`
- Utilities: `youdub/utils.py`, `youdub/terminology.py`
- Environment: `.env`, `.env.example`
