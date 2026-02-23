# YouDub-webui: 优质视频中文化工具

## 简介
`YouDub-webui` 是一套完整的视频中文化工具包，旨在将 YouTube 和其他平台上的高质量视频翻译和配音成中文版本。本项目结合了最新的 AI 技术，包括语音识别、大型语言模型翻译以及 AI 声音克隆技术，为中文用户提供卓越的观看体验。

本项目是 `YouDub` 的网页交互版本，基于 `Gradio` 构建，提供便捷的一键式工作流。

## 主要特点
- **视频下载**: 支持链接直接下载，包括单个视频、播放列表和频道。
- **AI 语音识别**: 基于 WhisperX，提供精确文本转换、时间轴对齐及说话人识别。
- **LLM 翻译**: 结合 GPT 等大模型，实现地道且精准的翻译。
- **AI 声音克隆**: 使用 AI 声音克隆技术，保留原作者音色生成中文配音。
- **自动上传**: 一键上传至 Bilibili 平台。
- **弱网优化**: 专门针对 Bilibili 上传进行了稳定性补丁处理。

## 快速开始

### 1. 环境准备
```bash
git clone https://github.com/skyconnfig/YouDub-webui.git
cd YouDub-webui
```

### 2. 系统依赖 (Windows)
安装 `ffmpeg` (推荐使用 `winget`):
```bash
winget install Gyan.FFmpeg
```

### 3. 安装依赖
运行自动配置脚本:
```bash
scripts/setup_windows.bat
```

### 4. 配置文件
将 `.env.example` 复制为 `.env` 并填入必要信息（API Key, Bilibili Cookie 等）。

### 5. 启动项目
```bash
python app.py
```

## Bilibili 上传优化 (Patch)
如果你在上传过程中遇到 `KeyError: 'OK'` 或 `NoSuchUpload` 等错误（由于网络不稳定导致），请运行此补丁：
```bash
python patch_bilibili.py
```
此补丁会切换为单线程上传、增加重试次数并修复库中的响应识别逻辑。

## 许可证
本项目遵循 Apache License 2.0。

## 引用与致谢
- [WhisperX](https://github.com/m-bain/whisperX)
- [bilibili-toolman](https://github.com/mos9527/bilibili-toolman)
