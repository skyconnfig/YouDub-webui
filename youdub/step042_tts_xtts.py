import os
from loguru import logger
import numpy as np
import torch
import time
from .utils import save_wav

# Lazy import TTS to avoid dependency issues at startup
TTS = None
try:
    from TTS.api import TTS
except ImportError as e:
    logger.warning(f"TTS not available: {e}")

model = None

def init_TTS():
    load_model()
    
def load_model(model_path="tts_models/multilingual/multi-dataset/xtts_v2", device='auto'):
    global model
    if model is not None:
        return
    
    if TTS is None:
        raise RuntimeError("TTS not available. Please install: pip install TTS")
    
    if device=='auto':
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f'Loading TTS model from {model_path}')
    t_start = time.time()
    model = TTS(model_path).to(device)
    t_end = time.time()
    logger.info(f'TTS model loaded in {t_end - t_start:.2f}s')
    

def tts(text, output_path, speaker_wav, model_name="tts_models/multilingual/multi-dataset/xtts_v2", device='auto', language='zh-cn'):
    global model
    
    if os.path.exists(output_path):
        logger.info(f'TTS {text} 已存在')
        return
    
    if model is None:
        load_model(model_name, device)
    
    last_error = None
    for retry in range(3):
        try:
            wav = model.tts(text, speaker_wav=speaker_wav, language=language)
            wav = np.array(wav)
            save_wav(wav, output_path)
            logger.info(f'TTS {text}')
            return  # Success - exit function
        except Exception as e:
            last_error = e
            logger.warning(f'TTS {text} 失败 (retry {retry + 1}/3): {e}')
            if retry < 2:
                time.sleep(1)  # Sleep between retries
    
    # All retries failed - raise error
    raise RuntimeError(f"XTTS failed after 3 retries: {last_error}")


if __name__ == '__main__':
    speaker_wav = r'videos\TED-Ed\20231121 Why did the US try to kill all the bison？ - Andrew C. Isenberg\audio_vocals.wav'
    while True:
        text = input('请输入：')
        tts(text, f'playground/{text}.wav', speaker_wav)
        
