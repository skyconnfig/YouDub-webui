# -*- coding: utf-8 -*-
import json
import os
import subprocess
import time
import shutil
from dotenv import load_dotenv

from loguru import logger

load_dotenv()

# 视频编码配置
VIDEO_ENCODER = os.getenv('VIDEO_ENCODER', 'auto')  # auto, nvenc, x264
VIDEO_QUALITY = os.getenv('VIDEO_QUALITY', 'high')  # high, medium, low

def get_video_encoder_config():
    """
    获取视频编码器配置
    自动检测并使用最佳编码方案
    """
    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path:
        logger.warning("未找到 ffmpeg，使用默认 libx264 编码")
        return 'libx264', ['-crf', '23', '-preset', 'medium']
    
    # 检测 NVENC 支持
    try:
        result = subprocess.run([ffmpeg_path, '-encoders'], 
                              capture_output=True, text=True, timeout=10)
        has_nvenc = 'h264_nvenc' in result.stdout
    except:
        has_nvenc = False
    
    # 根据配置和硬件选择编码器
    if VIDEO_ENCODER == 'nvenc' and has_nvenc:
        logger.info("使用 NVIDIA NVENC 硬件编码")
        # NVENC 参数：高质量、VBR模式
        return 'h264_nvenc', [
            '-preset', 'p4',           # 预设: p1(快) 到 p7(慢)
            '-rc', 'vbr',              # 可变码率
            '-cq', '20',               # 质量等级 (0-51, 越小越好)
            '-b:v', '0',               # 不限制码率
            '-maxrate', '50M',         # 最大码率
            '-bufsize', '100M'         # 缓冲大小
        ]
    elif VIDEO_ENCODER == 'x264' or not has_nvenc:
        logger.info("使用 libx264 软件编码")
        # x264 参数：基于质量等级
        if VIDEO_QUALITY == 'high':
            return 'libx264', [
                '-crf', '18',          # 高质量 (18-23为视觉无损)
                '-preset', 'slow',     # 慢预设，更好压缩
                '-tune', 'film'        # 优化电影内容
            ]
        elif VIDEO_QUALITY == 'medium':
            return 'libx264', [
                '-crf', '21',
                '-preset', 'medium'
            ]
        else:  # low
            return 'libx264', [
                '-crf', '25',
                '-preset', 'fast'
            ]
    else:
        # auto 模式：优先使用 NVENC
        if has_nvenc:
            logger.info("自动检测到 NVIDIA GPU，使用 NVENC 硬件编码")
            return 'h264_nvenc', [
                '-preset', 'p4',
                '-rc', 'vbr', 
                '-cq', '20',
                '-b:v', '0',
                '-maxrate', '50M',
                '-bufsize', '100M'
            ]
        else:
            logger.info("未检测到 NVIDIA GPU，使用 libx264 软件编码")
            return 'libx264', [
                '-crf', '20',
                '-preset', 'slow'
            ]

def get_audio_encoder_config():
    """获取音频编码配置"""
    return [
        '-c:a', 'aac',
        '-b:a', '192k',      # 音频码率
        '-ar', '48000'       # 采样率
    ]


def split_text(input_data,
               punctuations=['，', '；', '：', '。', '？', '！', '\n', '”']):
    # Chinese punctuation marks for sentence ending

    # Function to check if a character is a Chinese ending punctuation
    def is_punctuation(char):
        return char in punctuations

    # Process each item in the input data
    output_data = []
    for item in input_data:
        start = item["start"]
        text = item["translation"]
        speaker = item.get("speaker", "SPEAKER_00")
        original_text = item["text"]
        sentence_start = 0

        # Calculate the duration for each character
        duration_per_char = (item["end"] - item["start"]) / len(text)
        for i, char in enumerate(text):
            # If the character is a punctuation, split the sentence
            if not is_punctuation(char) and i != len(text) - 1:
                continue
            if i - sentence_start < 5 and i != len(text) - 1:
                continue
            if i < len(text) - 1 and is_punctuation(text[i+1]):
                continue
            sentence = text[sentence_start:i+1]
            sentence_end = start + duration_per_char * len(sentence)

            # Append the new item
            output_data.append({
                "start": round(start, 3),
                "end": round(sentence_end, 3),
                "text": original_text,
                "translation": sentence,
                "speaker": speaker
            })

            # Update the start for the next sentence
            start = sentence_end
            sentence_start = i + 1

    return output_data
    
def format_timestamp(seconds):
    """Converts seconds to the SRT time format."""
    millisec = int((seconds - int(seconds)) * 1000)
    hours, seconds = divmod(int(seconds), 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millisec:03}"

def generate_srt(translation, srt_path, speed_up=1, max_line_char=30):
    translation = split_text(translation)
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, line in enumerate(translation):
            start = format_timestamp(line['start']/speed_up)
            end = format_timestamp(line['end']/speed_up)
            text = line['translation']
            line = len(text)//(max_line_char+1) + 1
            avg = min(round(len(text)/line), max_line_char)
            text = '\n'.join([text[i*avg:(i+1)*avg]
                             for i in range(line)])
            f.write(f'{i+1}\n')
            f.write(f'{start} --> {end}\n')
            f.write(f'{text}\n\n')


def get_aspect_ratio(video_path):
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
               '-show_entries', 'stream=width,height', '-of', 'json', video_path]
    result = subprocess.run(command, capture_output=True, text=True)
    dimensions = json.loads(result.stdout)['streams'][0]
    return dimensions['width'] / dimensions['height']


def convert_resolution(aspect_ratio, resolution='1080p'):
    if aspect_ratio < 1:
        width = int(resolution[:-1])
        height = int(width / aspect_ratio)
    else:
        height = int(resolution[:-1])
        width = int(height * aspect_ratio)
    # make sure width and height are divisibal by 2
    width = width - width % 2
    height = height - height % 2
    
    # return f'{width}x{height}'
    return width, height
    
def synthesize_video(folder, subtitles=True, speed_up=1.05, fps=30, resolution='1080p'):
    """
    合成视频，使用优化的编码参数
    
    环境变量配置：
    - VIDEO_ENCODER: 视频编码器 (auto/nvenc/x264)
    - VIDEO_QUALITY: 视频质量 (high/medium/low)
    """
    if os.path.exists(os.path.join(folder, 'video.mp4')):
        logger.info(f'Video already synthesized in {folder}')
        return
    
    translation_path = os.path.join(folder, 'translation.json')
    input_audio = os.path.join(folder, 'audio_combined.wav')
    
    # Support both .mp4 and .webm formats
    input_video_mp4 = os.path.join(folder, 'download.mp4')
    input_video_webm = os.path.join(folder, 'download.webm')
    if os.path.exists(input_video_mp4):
        input_video = input_video_mp4
    elif os.path.exists(input_video_webm):
        input_video = input_video_webm
    else:
        logger.warning(f'No input video found in {folder}')
        return
    
    if not os.path.exists(translation_path) or not os.path.exists(input_audio):
        return
    
    with open(translation_path, 'r', encoding='utf-8') as f:
        translation = json.load(f)
        
    srt_path = os.path.join(folder, 'subtitles.srt')
    output_video = os.path.join(folder, 'video.mp4')
    generate_srt(translation, srt_path, speed_up)
    srt_path = srt_path.replace('\\', '/')
    aspect_ratio = get_aspect_ratio(input_video)
    width, height = convert_resolution(aspect_ratio, resolution)
    resolution_str = f'{width}x{height}'
    font_size = int(width/128)
    outline = int(round(font_size/8))
    video_speed_filter = f"setpts=PTS/{speed_up}"
    audio_speed_filter = f"atempo={speed_up}"
    subtitle_filter = f"subtitles={srt_path}:force_style='FontName=Arial,FontSize={font_size},PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline={outline},WrapStyle=2'"
    
    if subtitles:
        filter_complex = f"[0:v]{video_speed_filter},{subtitle_filter}[v];[1:a]{audio_speed_filter}[a]"
    else:
        filter_complex = f"[0:v]{video_speed_filter}[v];[1:a]{audio_speed_filter}[a]"
    
    # 获取优化的编码配置
    video_codec, video_params = get_video_encoder_config()
    audio_params = get_audio_encoder_config()
    
    logger.info(f"开始视频合成: {folder}")
    logger.info(f"视频编码器: {video_codec}, 分辨率: {resolution_str}, 帧率: {fps}")
    
    # 构建 ffmpeg 命令
    ffmpeg_command = [
        'ffmpeg',
        '-hide_banner',          # 隐藏版本信息
        '-loglevel', 'warning',  # 只显示警告和错误
        '-stats',                # 显示编码进度
        '-i', input_video,
        '-i', input_audio,
        '-filter_complex', filter_complex,
        '-map', '[v]',
        '-map', '[a]',
        '-r', str(fps),
        '-s', resolution_str,
        '-c:v', video_codec,
    ]
    
    # 添加视频编码参数
    ffmpeg_command.extend(video_params)
    
    # 添加音频编码参数
    ffmpeg_command.extend(audio_params)
    
    # 输出文件
    ffmpeg_command.extend([output_video, '-y'])
    
    # 执行编码
    logger.info(f"使用命令: {' '.join(ffmpeg_command[:10])}...")
    result = subprocess.run(ffmpeg_command, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"视频合成失败: {result.stderr}")
        # 如果 NVENC 失败，回退到软件编码
        if video_codec == 'h264_nvenc':
            logger.warning("NVENC 编码失败，尝试使用软件编码...")
            ffmpeg_command[ffmpeg_command.index('h264_nvenc')] = 'libx264'
            # 替换视频参数
            idx = ffmpeg_command.index('-cq') if '-cq' in ffmpeg_command else -1
            if idx > 0:
                ffmpeg_command[idx:idx+6] = ['-crf', '20', '-preset', 'medium']
            result = subprocess.run(ffmpeg_command, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"视频合成失败: {result.stderr}")
    
    # 验证输出文件
    if os.path.exists(output_video):
        file_size = os.path.getsize(output_video) / (1024 * 1024)  # MB
        logger.info(f"视频合成完成: {output_video} ({file_size:.1f} MB)")
    else:
        raise Exception("视频合成失败：未生成输出文件")
    
    time.sleep(0.5)
    

def synthesize_all_video_under_folder(folder, subtitles=True, speed_up=1.05, fps=30, resolution='1080p'):
    for root, dirs, files in os.walk(folder):
        # Check for either .mp4 or .webm input files
        has_input = 'download.mp4' in files or 'download.webm' in files
        if has_input and 'video.mp4' not in files:
            synthesize_video(root, subtitles=subtitles,
                             speed_up=speed_up, fps=fps, resolution=resolution)
    return f'Synthesized all videos under {folder}'
if __name__ == '__main__':
    folder = r'videos\3Blue1Brown\20231207 Im still astounded this is true'
    synthesize_all_video_under_folder(folder, subtitles=True)
