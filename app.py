import os
from dotenv import load_dotenv

# 设置 HuggingFace 镜像站 (解决网络问题)
load_dotenv()
hf_endpoint = os.getenv('HF_ENDPOINT')
if hf_endpoint:
    os.environ['HF_ENDPOINT'] = hf_endpoint
    os.environ['HF_HUB_ENDPOINT'] = hf_endpoint
    print(f"Using HuggingFace mirror: {hf_endpoint}")

# 设置模型下载目录为项目本地目录 (避免重复下载)
project_root = os.path.dirname(os.path.abspath(__file__))

# 设置 Torch Hub 目录（Demucs 模型）
torch_home = os.path.join(project_root, 'models', 'torch_hub')
os.environ['TORCH_HOME'] = torch_home

# 设置 TTS 目录
tts_home = os.path.join(project_root, 'models', 'TTS')
os.environ['TTS_HOME'] = tts_home

# 设置 HuggingFace 缓存目录（WhisperX 对齐模型、pyannote 模型等）
hf_cache_dir = os.path.join(project_root, 'models', 'hf_cache')
os.environ['HF_HOME'] = hf_cache_dir
os.environ['HUGGINGFACE_HUB_CACHE'] = os.path.join(hf_cache_dir, 'hub')
os.environ['TRANSFORMERS_CACHE'] = os.path.join(hf_cache_dir, 'transformers')

# 检查本地已有的 Demucs 模型
demucs_dir = os.path.join(project_root, 'models', 'Demucs')
if os.path.exists(demucs_dir) and any(f.endswith('.th') for f in os.listdir(demucs_dir)):
    print(f"[OK] Found local Demucs models: {demucs_dir}")
else:
    print(f"[INFO] Demucs models will be downloaded to: {torch_home}")

print(f"TTS models will be saved to: {tts_home}")
print(f"HF models will be saved to: {hf_cache_dir}")

import gradio as gr
from youdub.step000_video_downloader import download_from_url
from youdub.step010_demucs_vr import separate_all_audio_under_folder
from youdub.step020_whisperx import transcribe_all_audio_under_folder
from youdub.step030_translation import translate_all_transcript_under_folder
from youdub.step040_tts import generate_all_wavs_under_folder
from youdub.step050_synthesize_video import synthesize_all_video_under_folder
from youdub.step060_genrate_info import generate_all_info_under_folder
from youdub.step070_upload_bilibili import upload_all_videos_under_folder
from youdub.do_everything import do_everything
import os


do_everything_interface = gr.Interface(
    fn=do_everything,
    inputs=[
        gr.Textbox(label='Root Folder', value='videos'),  # Changed 'default' to 'value'
        gr.Textbox(label='Video URL', placeholder='Video or Playlist or Channel URL',
                   value='https://www.bilibili.com/list/1263732318'),  # Changed 'default' to 'value'
        gr.Slider(minimum=1, maximum=500, step=1, label='Number of videos to download', value=20),
        gr.Radio(['4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'], label='Resolution', value='1080p'),
        gr.Radio(['htdemucs', 'htdemucs_ft', 'htdemucs_6s', 'hdemucs_mmi', 'mdx', 'mdx_extra', 'mdx_q', 'mdx_extra_q', 'SIG'], label='Demucs Model', value='htdemucs_ft'),
        gr.Radio(['auto', 'cuda', 'cpu'], label='Demucs Device', value='auto'),
        gr.Slider(minimum=0, maximum=10, step=1, label='Number of shifts', value=5),
        gr.Radio(['large', 'medium', 'small', 'base', 'tiny'], label='Whisper Model', value='large'),
        gr.Textbox(label='Whisper Download Root', value='models/ASR/whisper'),
        gr.Slider(minimum=1, maximum=128, step=1, label='Whisper Batch Size', value=32),
        gr.Checkbox(label='Whisper Diarization', value=False),
        gr.Radio([None, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                 label='Whisper Min Speakers', value=None),
        gr.Radio([None, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                 label='Whisper Max Speakers', value=None),
        gr.Dropdown(['简体中文', '繁体中文', 'English', 'Deutsch', 'Français', 'русский'],
                    label='Translation Target Language', value='简体中文'),
        gr.Checkbox(label='Force Bytedance', value=False),
        gr.Checkbox(label='Subtitles', value=True),
        gr.Slider(minimum=0.5, maximum=2, step=0.05, label='Speed Up', value=1.05),
        gr.Slider(minimum=1, maximum=60, step=1, label='FPS', value=30),
        gr.Radio(['4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'], label='Resolution', value='1080p'),
        gr.Slider(minimum=1, maximum=5, step=1, label='Max Workers (并行处理视频数)', value=1),
        gr.Slider(minimum=1, maximum=10, step=1, label='Max Retries', value=3),
        gr.Checkbox(label='Auto Upload Video', value=True),
    ],
    outputs='text',
)
    
youtube_interface = gr.Interface(
    fn=download_from_url,
    inputs=[
        gr.Textbox(label='Video URL', placeholder='Video or Playlist or Channel URL',
                   value='https://www.bilibili.com/list/1263732318'),  # Changed 'default' to 'value'
        gr.Textbox(label='Output Folder', value='videos'),  # Changed 'default' to 'value'
        gr.Radio(['4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'], label='Resolution', value='1080p'),
        gr.Slider(minimum=1, maximum=100, step=1, label='Number of videos to download', value=5),
    ],
    outputs='text',
)

demucs_interface = gr.Interface(
    fn=separate_all_audio_under_folder,
    inputs = [
        gr.Textbox(label='Folder', value='videos'),  # Changed 'default' to 'value'
        gr.Radio(['htdemucs', 'htdemucs_ft', 'htdemucs_6s', 'hdemucs_mmi', 'mdx', 'mdx_extra', 'mdx_q', 'mdx_extra_q', 'SIG'], label='Model', value='htdemucs_ft'),
        gr.Radio(['auto', 'cuda', 'cpu'], label='Device', value='auto'),
        gr.Checkbox(label='Progress Bar in Console', value=True),
        gr.Slider(minimum=0, maximum=10, step=1, label='Number of shifts', value=5),
    ],
    outputs='text',
)

# transcribe_all_audio_under_folder(folder, model_name: str = 'large', download_root='models/ASR/whisper', device='auto', batch_size=32)
whisper_inference = gr.Interface(
    fn = transcribe_all_audio_under_folder,
    inputs = [
        gr.Textbox(label='Folder', value='videos'),  # Changed 'default' to 'value'
        gr.Radio(['large', 'medium', 'small', 'base', 'tiny'], label='Model', value='large'),
        gr.Textbox(label='Download Root', value='models/ASR/whisper'),
        gr.Radio(['auto', 'cuda', 'cpu'], label='Device', value='auto'),
        gr.Slider(minimum=1, maximum=128, step=1, label='Batch Size', value=32),
        gr.Checkbox(label='Diarization', value=False),
        gr.Radio([None, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                 label='Whisper Min Speakers', value=None),
        gr.Radio([None, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                 label='Whisper Max Speakers', value=None),
    ],
    outputs='text',
)

translation_interface = gr.Interface(
    fn=translate_all_transcript_under_folder,
    inputs = [
        gr.Textbox(label='Folder', value='videos'),  # Changed 'default' to 'value'
        gr.Dropdown(['简体中文', '繁体中文', 'English', 'Deutsch', 'Français', 'русский'],
                    label='Target Language', value='简体中文'),
    ],
    outputs='text',
)

tts_interafce = gr.Interface(
    fn=generate_all_wavs_under_folder,
    inputs = [
        gr.Textbox(label='Folder', value='videos'),  # Changed 'default' to 'value'
        gr.Checkbox(label='Force Bytedance', value=False),
    ],
    outputs='text',
)
syntehsize_video_interface = gr.Interface(
    fn=synthesize_all_video_under_folder,
    inputs = [
        gr.Textbox(label='Folder', value='videos'),  # Changed 'default' to 'value'
        gr.Checkbox(label='Subtitles', value=True),
        gr.Slider(minimum=0.5, maximum=2, step=0.05, label='Speed Up', value=1.05),
        gr.Slider(minimum=1, maximum=60, step=1, label='FPS', value=30),
        gr.Radio(['4320p', '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p'], label='Resolution', value='1080p'),
    ],
    outputs='text',
)

genearte_info_interface = gr.Interface(
    fn = generate_all_info_under_folder,
    inputs = [
        gr.Textbox(label='Folder', value='videos'),  # Changed 'default' to 'value'
    ],
    outputs='text',
)

upload_bilibili_interface = gr.Interface(
    fn = upload_all_videos_under_folder,
    inputs = [
        gr.Textbox(label='Folder', value='videos'),  # Changed 'default' to 'value'
    ],
    outputs='text',
)

app = gr.TabbedInterface(
    interface_list=[do_everything_interface,youtube_interface, demucs_interface,
                    whisper_inference, translation_interface, tts_interafce, syntehsize_video_interface, upload_bilibili_interface],
    tab_names=['全自动', '下载视频', '人声分离', '语音识别', '字幕翻译', '语音合成', '视频合成', '上传B站'],
    title='YouDub')
if __name__ == '__main__':
    app.launch()