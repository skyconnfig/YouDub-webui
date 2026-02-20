# coding=utf-8
"""
Configuration Presets System for YouDub

This module provides preset configurations for different use cases:
- high_quality: Best quality, slower processing
- fast: Faster processing, moderate quality  
- low_memory: Low VRAM usage, suitable for 4GB GPUs
- balanced: Balance between quality and speed
"""

import json
import os
from typing import Dict, Any, Optional

from loguru import logger


# Default presets configuration
PRESETS: Dict[str, Dict[str, Any]] = {
    "high_quality": {
        "name": "高质量模式",
        "description": "最佳质量，适合高端电脑",
        "whisper_model": "large",
        "demucs_model": "htdemucs_ft",
        "resolution": "1080p",
        "target_resolution": "1080p",
        "whisper_batch_size": 4,
        "whisper_diarization": True,
        "speed_up": 1.0,
        "fps": 60,
        "max_workers": 1,
    },
    "fast": {
        "name": "快速模式",
        "description": "处理速度快，适合批量处理",
        "whisper_model": "small",
        "demucs_model": "htdemucs",
        "resolution": "720p",
        "target_resolution": "720p",
        "whisper_batch_size": 16,
        "whisper_diarization": False,
        "speed_up": 1.1,
        "fps": 30,
        "max_workers": 2,
    },
    "low_memory": {
        "name": "低显存模式",
        "description": "适合4GB显存电脑",
        "whisper_model": "small",
        "demucs_model": "htdemucs",
        "resolution": "720p",
        "target_resolution": "720p",
        "whisper_batch_size": 8,
        "whisper_diarization": False,
        "whisper_min_speakers": 1,
        "whisper_max_speakers": 2,
        "speed_up": 1.05,
        "fps": 30,
        "max_workers": 1,
    },
    "balanced": {
        "name": "均衡模式",
        "description": "质量和速度的平衡",
        "whisper_model": "medium",
        "demucs_model": "htdemucs",
        "resolution": "720p",
        "target_resolution": "720p",
        "whisper_batch_size": 8,
        "whisper_diarization": False,
        "speed_up": 1.05,
        "fps": 30,
        "max_workers": 1,
    },
}


def get_preset_names() -> list:
    """Get list of available preset names"""
    return list(PRESETS.keys())


def load_preset(preset_name: str) -> Optional[Dict[str, Any]]:
    """
    Load a preset configuration by name.
    
    Args:
        preset_name: Name of the preset (high_quality, fast, low_memory, balanced)
    
    Returns:
        Dictionary with preset configuration, or None if preset not found
    """
    if preset_name not in PRESETS:
        logger.warning(f"Preset '{preset_name}' not found. Available: {get_preset_names()}")
        return None
    
    # Return a copy to avoid mutation
    return PRESETS[preset_name].copy()


def save_preset(preset_name: str, config: Dict[str, Any], config_dir: str = "config") -> bool:
    """
    Save a custom preset to config directory.
    
    Args:
        preset_name: Name for the preset
        config: Configuration dictionary
        config_dir: Directory to save presets
    
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    preset_path = os.path.join(config_dir, f"preset_{preset_name}.json")
    
    try:
        with open(preset_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved preset '{preset_name}' to {preset_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save preset: {e}")
        return False


def load_custom_presets(config_dir: str = "config") -> Dict[str, Dict[str, Any]]:
    """
    Load all custom presets from config directory.
    
    Args:
        config_dir: Directory containing preset files
    
    Returns:
        Dictionary of custom presets
    """
    custom_presets = {}
    
    if not os.path.exists(config_dir):
        return custom_presets
    
    for filename in os.listdir(config_dir):
        if filename.startswith("preset_") and filename.endswith(".json"):
            preset_name = filename[7:-5]  # Remove "preset_" and ".json"
            preset_path = os.path.join(config_dir, filename)
            
            try:
                with open(preset_path, 'r', encoding='utf-8') as f:
                    custom_presets[preset_name] = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load preset {filename}: {e}")
    
    return custom_presets


def get_all_presets() -> Dict[str, Dict[str, Any]]:
    """
    Get all available presets (built-in + custom).
    
    Returns:
        Dictionary of all presets
    """
    all_presets = PRESETS.copy()
    all_presets.update(load_custom_presets())
    return all_presets


def apply_preset_to_kwargs(preset_name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply preset values to kwargs, preserving any explicitly passed values.
    
    Args:
        preset_name: Name of preset to apply
        kwargs: Keyword arguments to update with preset values
    
    Returns:
        Updated kwargs dictionary
    """
    preset = load_preset(preset_name)
    if preset is None:
        return kwargs
    
    # Apply preset values, but don't override explicitly passed values
    for key, value in preset.items():
        if key not in kwargs or kwargs[key] is None:
            kwargs[key] = value
    
    return kwargs


if __name__ == '__main__':
    # Test preset system
    print("Available presets:", get_preset_names())
    print("\nHigh Quality preset:", load_preset("high_quality"))
    print("\nFast preset:", load_preset("fast"))
    print("\nLow Memory preset:", load_preset("low_memory"))
