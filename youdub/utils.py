import os
import re
import string
import numpy as np
import shutil
from scipy.io import wavfile

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


def cleanup_translated_folder(folder: str) -> str:
    """
    清理翻译后的文件夹中的中间文件，保留最终产物
    需要保留的文件:
    - download.mp4 (原视频)
    - video.mp4 (最终合成视频)
    - audio_tts.wav (TTS音频)
    - audio_combined.wav (合并后的音频)
    - translation.json (翻译后的字幕)
    - subtitles.srt (字幕文件)
    - video.png (缩略图)
    - video.txt (摘要)
    - wavs/ (TTS分段)
    - SPEAKER/ (说话人样本)
    
    会删除的中间文件:
    - audio.wav (原始提取的音频)
    - audio_vocals.wav (Demucs分离的人声)
    - audio_instruments.wav (Demucs分离的乐器)
    - download.info.json (yt-dlp元数据)
    - download.webp (下载的缩略图)
    - transcript.json (原始Whisper输出)
    - summary.json (视频摘要)
    """
    if not os.path.exists(folder):
        return f"文件夹不存在: {folder}"
    
    # 首先列出所有视频文件夹
    result = "=== 视频文件夹列表 ===\n\n"
    folders_info = []
    
    for uploader in sorted(os.listdir(folder)):
        uploader_path = os.path.join(folder, uploader)
        if not os.path.isdir(uploader_path):
            continue
        
        for video_folder in sorted(os.listdir(uploader_path)):
            video_path = os.path.join(uploader_path, video_folder)
            if not os.path.isdir(video_path):
                continue
            
            # 检查是否有最终视频
            has_video = os.path.exists(os.path.join(video_path, 'video.mp4'))
            has_translation = os.path.exists(os.path.join(video_path, 'translation.json'))
            
            # 计算文件夹大小
            total_size = 0
            try:
                for root, dirs, files in os.walk(video_path):
                    for f in files:
                        total_size += os.path.getsize(os.path.join(root, f))
            except:
                pass
            
            size_mb = total_size / (1024 * 1024)
            status = "✅" if has_video else "⏳"
            folders_info.append({
                'path': f"{uploader}/{video_folder}",
                'status': status,
                'size': size_mb,
                'has_video': has_video,
                'has_translation': has_translation
            })
    
    # 显示文件夹列表
    for i, f in enumerate(folders_info, 1):
        result += f"{i}. {f['path']}\n"
        result += f"   {f['status']} {'已完成' if f['has_video'] else '未完成'} | {f['size']:.1f} MB\n"
    
    result += "\n=== 清理中间文件 ===\n"
    result += "正在清理中间文件...\n\n"
    
    # 清理中间文件
    cleaned_count = 0
    deleted_files = []
    errors = []
    
    files_to_keep = {
        'download.mp4',
        'video.mp4',
        'audio_tts.wav',
        'audio_combined.wav',
        'translation.json',
        'subtitles.srt',
        'video.png',
        'video.txt',
    }
    
    intermediate_patterns = [
        'audio.wav',
        'audio_vocals.wav',
        'audio_instruments.wav',
        'download.info.json',
        'download.webp',
        'transcript.json',
        'summary.json',
    ]
    
    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename in files_to_keep:
                continue
            
            should_delete = False
            for pattern in intermediate_patterns:
                if filename == pattern:
                    should_delete = True
                    break
            
            if should_delete:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, folder)
                try:
                    os.remove(filepath)
                    deleted_files.append(rel_path)
                    cleaned_count += 1
                except Exception as e:
                    errors.append(f"{rel_path}: {str(e)}")
    
    # 清理空目录
    for root, dirs, files in os.walk(folder, topdown=False):
        for dirname in dirs:
            dirpath = os.path.join(root, dirname)
            try:
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
                    deleted_files.append(dirpath.replace(folder + os.sep, '') + '/')
                    cleaned_count += 1
            except Exception as e:
                pass
    
    if deleted_files:
        result += f"✅ 已清理 {cleaned_count} 个中间文件\n"
    else:
        result += "ℹ️ 没有需要清理的中间文件\n"
    
    if errors:
        result += f"⚠️ 清理出错: {len(errors)} 个\n"
    
    result += "\n提示：要删除整个文件夹，请在终端手动执行：\n"
    result += "  rm -rf videos/文件夹名称\n"
    
    return result


def list_video_folders(folder: str) -> str:
    """
    列出 videos 文件夹下所有已处理的视频
    """
    if not os.path.exists(folder):
        return f"文件夹不存在: {folder}"
    
    result = "=== 视频文件夹列表 ===\n\n"
    total_size = 0
    
    for uploader in sorted(os.listdir(folder)):
        uploader_path = os.path.join(folder, uploader)
        if not os.path.isdir(uploader_path):
            continue
        
        result += f"📁 {uploader}\n"
        
        for video_folder in sorted(os.listdir(uploader_path)):
            video_path = os.path.join(uploader_path, video_folder)
            if not os.path.isdir(video_path):
                continue
            
            has_video = os.path.exists(os.path.join(video_path, 'video.mp4'))
            has_translation = os.path.exists(os.path.join(video_path, 'translation.json'))
            
            total_size_folder = 0
            try:
                for root, dirs, files in os.walk(video_path):
                    for f in files:
                        total_size_folder += os.path.getsize(os.path.join(root, f))
            except:
                pass
            
            size_mb = total_size_folder / (1024 * 1024)
            total_size += total_size_folder
            
            status = "🎬" if has_video else "📝" if has_translation else "📄"
            result += f"  {status} {video_folder}\n"
            result += f"      {'✅ 已完成' if has_video else '⏳ 处理中'} | {size_mb:.1f} MB\n"
    
    result += f"\n总计: {total_size / (1024*1024*1024):.2f} GB"
    return result


def delete_video_folder(folder_path: str) -> str:
    """
    删除指定的视频文件夹
    """
    # 安全检查：确保路径在 videos 目录下
    folder_path = os.path.abspath(folder_path)
    
    if not os.path.exists(folder_path):
        return f"文件夹不存在: {folder_path}"
    
    # 计算大小
    total_size = 0
    try:
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                total_size += os.path.getsize(os.path.join(root, f))
    except:
        pass
    
    size_mb = total_size / (1024 * 1024)
    
    # 删除
    try:
        shutil.rmtree(folder_path)
        return f"✅ 已删除: {folder_path}\n释放空间: {size_mb:.1f} MB"
    except Exception as e:
        return f"❌ 删除失败: {str(e)}"