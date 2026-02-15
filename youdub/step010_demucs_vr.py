import shutil
from demucs.api import Separator
import os
from loguru import logger
import time
from .utils import save_wav, normalize_wav
import torch

# 设置模型下载目录 - 使用已有的 Demucs 模型
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 检查是否有已有的 Demucs 模型
demucs_local_dir = os.path.join(project_root, 'models', 'Demucs')
torch_hub_dir = os.path.join(project_root, 'models', 'torch_hub', 'checkpoints')

# 如果本地有 Demucs 模型，链接到 torch hub 目录
if os.path.exists(demucs_local_dir) and any(f.endswith('.th') for f in os.listdir(demucs_local_dir)):
    logger.info(f'Found local Demucs models in: {demucs_local_dir}')
    os.makedirs(torch_hub_dir, exist_ok=True)
    
    # 创建符号链接或复制模型文件
    for model_file in os.listdir(demucs_local_dir):
        if model_file.endswith('.th'):
            src = os.path.join(demucs_local_dir, model_file)
            dst = os.path.join(torch_hub_dir, model_file)
            if not os.path.exists(dst):
                try:
                    os.symlink(src, dst)
                    logger.info(f'Linked model: {model_file}')
                except OSError:
                    # Windows 可能需要管理员权限才能创建符号链接，复制文件代替
                    shutil.copy2(src, dst)
                    logger.info(f'Copied model: {model_file}')
    
    # 设置 torch hub 目录
    torch.hub.set_dir(os.path.join(project_root, 'models', 'torch_hub'))
    logger.info(f'Demucs models will be loaded from local: {torch_hub_dir}')
else:
    # 使用默认下载目录
    torch.hub.set_dir(torch_hub_dir)
    logger.info(f'Demucs models will be downloaded to: {torch_hub_dir}')

auto_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
separator = None

def init_demucs():
    global separator
    separator = load_model()
    
def load_model(model_name: str = "htdemucs_ft", device: str = 'auto', progress: bool = True, shifts: int=5) -> Separator:
    global separator
    if separator is not None:
        logger.info(f'Demucs model already loaded')
        return
    
    logger.info(f'Loading Demucs model: {model_name}')
    t_start = time.time()
    separator = Separator(model_name, device=auto_device if device=='auto' else device, progress=progress, shifts=shifts)
    t_end = time.time()
    logger.info(f'Demucs model loaded in {t_end - t_start:.2f} seconds')

def reload_model(model_name: str = "htdemucs_ft", device: str = 'auto', progress: bool = True, shifts: int=5) -> Separator:
    global separator
    logger.info(f'Reloading Demucs model: {model_name}')
    t_start = time.time()
    separator = Separator(model_name, device=auto_device if device=='auto' else device, progress=progress, shifts=shifts)
    t_end = time.time()
    logger.info(f'Demucs model reloaded in {t_end - t_start:.2f} seconds')
    
def separate_audio(folder: str, model_name: str = "htdemucs_ft", device: str = 'auto', progress: bool = True, shifts: int = 5) -> None:
    global separator
    audio_path = os.path.join(folder, 'audio.wav')
    if not os.path.exists(audio_path):
        return
    vocal_output_path = os.path.join(folder, 'audio_vocals.wav')
    instruments_output_path = os.path.join(folder, 'audio_instruments.wav')
    
    if os.path.exists(vocal_output_path) and os.path.exists(instruments_output_path):
        logger.info(f'Audio already separated in {folder}')
        return
    
    logger.info(f'Separating audio from {folder}')
    load_model(model_name, device, progress, shifts)
    t_start = time.time()
    try:
        origin, separated = separator.separate_audio_file(audio_path)
    except:
        # reload_model(model_name, device, progress, shifts)
                # origin, separated = separator.separate_audio_file(audio_path)
        time.sleep(5)
        logger.error(f'Error separating audio from {folder}')
        raise Exception(f'Error separating audio from {folder}')
    t_end = time.time()
    logger.info(f'Audio separated in {t_end - t_start:.2f} seconds')
    
    vocals = separated['vocals'].numpy().T
    instruments = None
    for k, v in separated.items():
        if k == 'vocals':
            continue
        if instruments is None:
            instruments = v
        else:
            instruments += v
    instruments = instruments.numpy().T
    
    vocal_output_path = os.path.join(folder, 'audio_vocals.wav')
    instruments_output_path = os.path.join(folder, 'audio_instruments.wav')
    
    save_wav(vocals, vocal_output_path, sample_rate=44100)
    logger.info(f'Vocals saved to {vocal_output_path}')
    
    save_wav(instruments, instruments_output_path, sample_rate=44100)
    logger.info(f'Instruments saved to {instruments_output_path}')
    
def extract_audio_from_video(folder: str) -> bool:
    # Try mp4 first, then webm
    video_extensions = ['.mp4', '.webm']
    video_path = None
    for ext in video_extensions:
        video_path_candidate = os.path.join(folder, f'download{ext}')
        if os.path.exists(video_path_candidate):
            video_path = video_path_candidate
            break
    
    if video_path is None:
        logger.warning(f'No video file found in {folder}')
        return False
    
    audio_path = os.path.join(folder, 'audio.wav')
    if os.path.exists(audio_path):
        logger.info(f'Audio already extracted in {folder}')
        return True
    logger.info(f'Extracting audio from {video_path}')

    os.system(
        f'ffmpeg -loglevel error -i "{video_path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{audio_path}"')
    # load wav and use save_wav_norm to normalize the wav
    # normalize_wav(audio_path)
    
    time.sleep(1)
    logger.info(f'Audio extracted from {folder}')
    return True
    
def separate_all_audio_under_folder(root_folder: str, model_name: str = "htdemucs_ft", device: str = 'auto', progress: bool = True, shifts: int = 5) -> None:
    global separator
    for subdir, dirs, files in os.walk(root_folder):
        # Check for any supported video format
        has_video = any(f.startswith('download') and (f.endswith('.mp4') or f.endswith('.webm')) for f in files)
        if not has_video:
            continue
        if 'audio.wav' not in files:
            extract_audio_from_video(subdir)
        if 'audio_vocals.wav' not in files:
            separate_audio(subdir, model_name, device, progress, shifts)

    logger.info(f'All audio separated under {root_folder}')
    return f'All audio separated under {root_folder}'
    
if __name__ == '__main__':
    folder = r"videos"
    separate_all_audio_under_folder(folder, shifts=0)
    
    
