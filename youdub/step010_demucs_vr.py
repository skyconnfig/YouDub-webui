import shutil
from demucs.api import Separator
import os
from loguru import logger
import time
import subprocess
from .utils import save_wav, normalize_wav
import torch
import shutil

def check_ffmpeg():
    """检查 ffmpeg 是否可用"""
    # 首先尝试从系统 PATH 中查找
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    # 尝试常见的 Windows 安装路径
    common_paths = [
        r'C:\ffmpeg\bin\ffmpeg.exe',
        r'C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe',
        r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
        r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # 检查项目目录下的 ffmpeg（支持相对路径）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_ffmpeg_paths = [
        os.path.join(project_root, 'ffmpeg', 'bin', 'ffmpeg.exe'),
        os.path.join(project_root, 'ffmpeg', 'ffmpeg-8.0.1-essentials_build', 'bin', 'ffmpeg.exe'),
        os.path.join(project_root, 'ffmpeg.exe'),
        # 支持 D:\YouDub-webui 这样的绝对路径项目目录
        r'D:\YouDub-webui\ffmpeg\bin\ffmpeg.exe',
        r'D:\YouDub-webui\ffmpeg\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe',
    ]
    
    for path in project_ffmpeg_paths:
        if os.path.exists(path):
            logger.info(f"找到项目目录下的 ffmpeg: {path}")
            return path
    
    return None

def get_ffmpeg_install_guide():
    """返回 ffmpeg 安装指导"""
    return """
ffmpeg 未安装或未添加到系统 PATH。请按照以下步骤安装：

方法1 - 使用 winget 安装（推荐）：
  1. 打开 PowerShell 或命令提示符（管理员）
  2. 运行：winget install Gyan.FFmpeg
  3. 安装完成后重启程序

方法2 - 手动安装：
  1. 访问 https://github.com/BtbN/FFmpeg-Builds/releases
  2. 下载 ffmpeg-master-latest-win64-gpl.zip
  3. 解压到 C:\ffmpeg
  4. 将 C:\ffmpeg\bin 添加到系统 PATH：
     - 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
     - 在"系统变量"中找到 Path，点击编辑
     - 添加 C:\ffmpeg\bin
  5. 重启程序

方法3 - 如果已安装但程序找不到：
  在 .env 文件中添加：
  FFMPEG_PATH=C:\\path\\to\\your\\ffmpeg.exe
"""

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

def init_demucs(model_name='htdemucs', device='auto', shifts=0):
    global separator
    separator = load_model(model_name, device, True, shifts)
    
def load_model(model_name: str = "htdemucs", device: str = 'auto', progress: bool = True, shifts: int=0) -> Separator:
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
    # 检查文件夹是否存在
    if not os.path.exists(folder):
        raise Exception(f"文件夹不存在: {folder}")
    
    # 检查 ffmpeg
    ffmpeg_path = check_ffmpeg()
    if not ffmpeg_path:
        error_msg = get_ffmpeg_install_guide()
        logger.error(error_msg)
        raise Exception(f"ffmpeg 未安装\n{error_msg}")
    
    logger.info(f"使用 ffmpeg: {ffmpeg_path}")
    
    video_path = None
    try:
        files = os.listdir(folder)
    except Exception as e:
        raise Exception(f"无法读取文件夹 {folder}: {e}")
    
    for file in files:
        if file.startswith('download') and (file.endswith('.mp4') or file.endswith('.webm')):
            video_path = os.path.join(folder, file)
            break
    
    if video_path is None:
        logger.warning(f'No video file found in {folder}')
        return False
    
    # 检查视频文件是否存在
    if not os.path.exists(video_path):
        raise Exception(f"视频文件不存在: {video_path}")
    
    logger.info(f"找到视频文件: {video_path}")
    
    audio_path = os.path.join(folder, 'audio.wav')
    if os.path.exists(audio_path):
        logger.info(f'Audio already extracted in {folder}')
        return True
    
    logger.info(f'Extracting audio from {video_path}')
    
    # 使用找到的 ffmpeg 路径
    cmd = f'"{ffmpeg_path}" -loglevel error -i "{video_path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{audio_path}"'
    logger.info(f"执行命令: {cmd}")
    result = os.system(cmd)
    
    if result != 0:
        # 尝试获取更详细的错误信息
        try:
            test_cmd = f'"{ffmpeg_path}" -version'
            test_result = os.system(test_cmd)
            if test_result != 0:
                raise Exception(f"ffmpeg 无法执行，请检查路径是否正确: {ffmpeg_path}")
        except Exception as e:
            logger.error(f"测试 ffmpeg 失败: {e}")
        
        raise Exception(f"ffmpeg 音频提取失败，请检查视频文件是否损坏: {video_path}")
    
    # 验证音频文件是否成功创建
    if not os.path.exists(audio_path):
        raise Exception(f"ffmpeg 未能创建音频文件: {audio_path}")
    
    logger.info(f'Audio extracted from {folder}')
    return True
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
    
    
