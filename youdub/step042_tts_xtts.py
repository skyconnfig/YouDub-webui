import os
from loguru import logger
import numpy as np
import torch
import time
from .utils import save_wav

import threading

# Lazy import TTS to avoid dependency issues at startup
TTS = None
try:
    from TTS.api import TTS
except ImportError as e:
    logger.warning(f"TTS not available: {e}")

model = None
model_lock = threading.Lock() # Add lock for thread-safe GPU access

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
    

def clean_quotes(text: str) -> str:
    """清理文本中的多余引号，提升观看体验"""
    # 移除各种中英文引号
    quotes = ['"', '"', '“', '”', "'", "'", '‘', '’', '«', '»', '《', '》']
    text = text.strip()
    changed = True
    while changed:
        changed = False
        for q in quotes:
            if text.startswith(q):
                text = text[len(q):].strip()
                changed = True
            if text.endswith(q):
                text = text[:-len(q)].strip()
                changed = True
    return text


def dedup_repeated_sentences(text: str) -> str:
    """检测并去除翻译结果中的循环重复句子（LLM复读BUG）"""
    # 按中文标点和逗号分割
    delimiters = ['。', '！', '？', '，', '；']
    parts = [text]
    for d in delimiters:
        new_parts = []
        for p in parts:
            new_parts.extend(p.split(d) if d in p else [p])
            if d in p:
                # 稍后重新拼接时带上分隔符
                pass
        parts = new_parts
    
    # 简单方法：找出第一个重复的片段并截断
    # 如果文本中有某个句子重复超过3次，认为是复读，只保留第一次
    sentences = [s.strip() for s in text.replace('。', '。|').replace('，', '，|').replace('！', '！|').replace('？', '？|').split('|') if s.strip()]
    seen = {}
    clean_sentences = []
    for s in sentences:
        if s not in seen:
            seen[s] = 0
            clean_sentences.append(s)
        seen[s] += 1
        if seen[s] > 2:  # 连续出现超过2次，终止
            break
    
    result = ''.join(clean_sentences)
    if result != text:
        logger.warning(f'检测到翻译复读，已自动去重。原长度: {len(text)}，清洗后: {len(result)}')
    return result


def tts(text, output_path, speaker_wav, model_name="tts_models/multilingual/multi-dataset/xtts_v2", device='auto', language='zh-cn'):
    global model
    
    # 清理文本中的多余引号
    text = clean_quotes(text)
    # 去除翻译复读
    text = dedup_repeated_sentences(text)
    # XTTS 400 token 硬限制：中文约 82 个字符为安全阈值，强制截断
    MAX_ZH_CHARS = 80
    if len(text) > MAX_ZH_CHARS:
        # 尝试在标点处截断
        cut_point = MAX_ZH_CHARS
        for i in range(MAX_ZH_CHARS - 1, max(0, MAX_ZH_CHARS - 20), -1):
            if text[i] in '。，！？；':
                cut_point = i + 1
                break
        original_text = text
        text = text[:cut_point]
        logger.warning(f'文本过长 ({len(original_text)} chars)，已截断至 {len(text)} chars')
    
    if os.path.exists(output_path):
        logger.info(f'TTS {text} 已存在')
        return
    
    if model is None:
        load_model(model_name, device)
    
    last_error = None
    for retry in range(3):
        try:
            # 使用锁确保同一时间只有一个线程访问 GPU 资源，避免 CUDA 冲突
            with model_lock:
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
        
