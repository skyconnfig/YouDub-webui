# coding=utf-8
"""
Edge-TTS (Microsoft Edge Text-to-Speech) engine module for YouDub.

This module provides free, high-quality TTS using Microsoft's Edge TTS service.
No API key required - uses the edge-tts library.

Key features:
- Free and high-quality neural voices
- Supports multiple languages including Chinese
- No API key needed
- Async implementation with retry logic
"""

import asyncio
import os
import time

import librosa
from loguru import logger

# Lazy import edge-tts to avoid import issues at startup
edge_tts = None


def _get_edge_tts():
    """Lazily import edge-tts to avoid startup dependency issues"""
    global edge_tts
    if edge_tts is None:
        import edge_tts as _edge_tts
        edge_tts = _edge_tts
    return edge_tts


# Default Chinese voices
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"  # Female - most natural
MALE_VOICE = "zh-CN-YunxiNeural"  # Male voice

# Voice options mapping for different speaker types
VOICE_OPTIONS = {
    "female": "zh-CN-XiaoxiaoNeural",
    "male": "zh-CN-YunxiNeural",
    "news": "zh-CN-YunyangNeural",
    "default": "zh-CN-XiaoxiaoNeural",
}


def _select_voice(voice_type: str = None) -> str:
    """Select appropriate voice based on voice_type parameter"""
    if voice_type is None:
        return DEFAULT_VOICE
    
    # Check if it's a direct voice name
    if "Neural" in voice_type:
        return voice_type
    
    # Map common voice type names
    return VOICE_OPTIONS.get(voice_type.lower(), DEFAULT_VOICE)


async def _generate_speech_async(text: str, voice: str, output_path: str) -> None:
    """Async function to generate speech using edge-tts"""
    etts = _get_edge_tts()
    communicate = etts.Communicate(text, voice)
    await communicate.save(output_path)


def tts(text: str, output_path: str, speaker_wav: str = None, voice_type: str = None) -> None:
    """
    Generate speech using Edge-TTS engine.
    
    Args:
        text: Text to synthesize
        output_path: Path to save output WAV file
        speaker_wav: Reference audio for voice cloning (NOT USED in Edge-TTS, kept for API compatibility)
        voice_type: Voice type selection - can be:
            - None: Default female voice
            - "female": zh-CN-XiaoxiaoNeural
            - "male": zh-CN-YunxiNeural  
            - "news": zh-CN-YunyangNeural
            - Direct voice name like "zh-CN-XiaoxiaoNeural"
    
    Returns:
        None - saves audio to output_path
    
    Raises:
        RuntimeError: If TTS fails after all retries
    """
    # Check if file already exists
    if os.path.exists(output_path):
        logger.info(f'Edge-TTS {text} 已存在: {output_path}')
        return
    
    # Select voice
    voice = _select_voice(voice_type)
    logger.debug(f"Using Edge-TTS voice: {voice}")
    
    # Retry logic
    last_error = None
    for retry in range(3):
        try:
            # Run async edge-tts in sync context
            asyncio.run(_generate_speech_async(text, voice, output_path))
            
            # Verify file was created
            if os.path.exists(output_path):
                logger.info(f'Edge-TTS 生成成功: {text[:30]}... -> {output_path}')
                return
            else:
                raise RuntimeError("Output file was not created")
                
        except Exception as e:
            last_error = e
            logger.warning(f'Edge-TTS 失败 (retry {retry + 1}/3): {e}')
            if retry < 2:
                time.sleep(1)
    
    # All retries failed
    raise RuntimeError(f"Edge-TTS failed after 3 retries: {last_error}")


def list_available_voices() -> list:
    """List all available Edge-TTS voices (requires network)"""
    etts = _get_edge_tts()
    return asyncio.run(etts.list_voices())


if __name__ == '__main__':
    # Test voice generation
    test_text = "你好，这是一个测试。"
    test_output = "test_edge_tts.wav"
    
    print(f"Testing Edge-TTS with: {test_text}")
    tts(test_text, test_output)
    print(f"Generated: {test_output}")
