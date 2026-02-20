import re
import string
import time
import threading
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from scipy.io import wavfile
from loguru import logger


class ProcessingStep(Enum):
    """Processing pipeline steps"""
    DOWNLOAD = "download"
    DEMUCS = "demucs"
    WHISPER = "whisper"
    TRANSLATION = "translation"
    TTS = "tts"
    SYNTHESIZE = "synthesize"
    UPLOAD = "upload"


@dataclass
class ProgressInfo:
    """Progress information for a processing step"""
    step: ProcessingStep
    current: int = 0
    total: int = 0
    message: str = ""
    percentage: float = 0.0
    start_time: float = field(default_factory=time.time)
    eta_seconds: float = 0.0
    
    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time


class ProgressCallback:
    """
    Progress callback system for YouDub processing pipeline.
    
    Provides unified progress tracking across all processing steps.
    Can be used with Gradio progress bars or console output.
    
    Usage:
        callback = ProgressCallback()
        
        # Set up progress
        callback.set_step(ProcessingStep.TTS, total=100)
        
        # Update progress
        callback.update(50, "Processing segment 50/100")
        
        # Get progress for UI
        progress_dict = callback.get_progress()
    """
    
    def __init__(self, callback_fn: Optional[Callable] = None):
        """
        Initialize progress callback.
        
        Args:
            callback_fn: Optional callback function to call on progress updates.
                        Signature: fn(step, current, total, message)
        """
        self._callback_fn = callback_fn
        self._progress: Dict[ProcessingStep, ProgressInfo] = {}
        self._current_step: Optional[ProcessingStep] = None
        self._lock = threading.Lock()
        self._cancelled = False
    
    def set_step(self, step: ProcessingStep, total: int, message: str = "") -> None:
        """Set the current step and total items"""
        with self._lock:
            self._current_step = step
            self._progress[step] = ProgressInfo(
                step=step,
                total=total,
                message=message or f"Starting {step.value}..."
            )
            self._notify(step, 0, total, message or f"Starting {step.value}...")
    
    def update(self, current: int, message: str = "") -> None:
        """Update progress for current step"""
        with self._lock:
            if self._current_step is None:
                return
            
            step = self._current_step
            if step not in self._progress:
                return
            
            progress = self._progress[step]
            progress.current = current
            
            if progress.total > 0:
                progress.percentage = (current / progress.total) * 100
                # Estimate ETA
                if current > 0:
                    elapsed = progress.elapsed_seconds
                    rate = current / elapsed
                    remaining = progress.total - current
                    progress.eta_seconds = remaining / rate if rate > 0 else 0
            
            if message:
                progress.message = message
            
            self._notify(step, current, progress.total, message)
    
    def increment(self, message: str = "") -> None:
        """Increment progress by 1"""
        with self._lock:
            if self._current_step and self._current_step in self._progress:
                current = self._progress[self._current_step].current + 1
                self.update(current, message)
    
    def _notify(self, step: ProcessingStep, current: int, total: int, message: str) -> None:
        """Notify callback function if set"""
        if self._callback_fn:
            try:
                self._callback_fn(step, current, total, message)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress as dictionary for UI display"""
        with self._lock:
            if self._current_step and self._current_step in self._progress:
                p = self._progress[self._current_step]
                return {
                    "step": p.step.value,
                    "current": p.current,
                    "total": p.total,
                    "percentage": p.percentage,
                    "message": p.message,
                    "elapsed_seconds": p.elapsed_seconds,
                    "eta_seconds": p.eta_seconds,
                }
            return {"step": "idle", "current": 0, "total": 0, "percentage": 0}
    
    def get_progress_tuple(self) -> tuple:
        """Get progress as (current, total) tuple for Gradio progress"""
        with self._lock:
            if self._current_step and self._current_step in self._progress:
                p = self._progress[self._current_step]
                return (p.current, p.total)
            return (0, 1)
    
    def cancel(self) -> None:
        """Request cancellation of current operation"""
        self._cancelled = True
        logger.info("Progress callback: cancellation requested")
    
    @property
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled"""
        return self._cancelled
    
    def reset(self) -> None:
        """Reset progress state"""
        with self._lock:
            self._progress.clear()
            self._current_step = None
            self._cancelled = False

def sanitize_filename(filename: str) -> str:
    # Define a set of valid characters
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    # Keep only valid characters
    sanitized_filename = ''.join(c for c in filename if c in valid_chars)

    # Replace multiple spaces with a single space
    sanitized_filename = re.sub(' +', ' ', sanitized_filename)

    return sanitized_filename


def save_wav(wav: np.ndarray, output_path: str, sample_rate=24000):
    # wav_norm = wav * (32767 / max(0.01, np.max(np.abs(wav))))
    wav_norm = wav * 32767
    wavfile.write(output_path, sample_rate, wav_norm.astype(np.int16))

def save_wav_norm(wav: np.ndarray, output_path: str, sample_rate=24000):
    wav_norm = wav * (32767 / max(0.01, np.max(np.abs(wav))))
    wavfile.write(output_path, sample_rate, wav_norm.astype(np.int16))
    
def normalize_wav(wav_path: str) -> None:
    sample_rate, wav = wavfile.read(wav_path)
    wav_norm = wav * (32767 / max(0.01, np.max(np.abs(wav))))
    wavfile.write(wav_path, sample_rate, wav_norm.astype(np.int16))