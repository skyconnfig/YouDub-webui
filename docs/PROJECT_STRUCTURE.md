# 项目结构说明 / Project Structure

该文档记录了 YouDub-webui 的目录结构及各模块功能。

## 目录树
```text
YouDub-webui/
├── app.py                # 项目入口：Gradio WebUI
├── .env                  # 环境变量配置 (API Key, 登录凭据等)
├── requirements.txt      # Python 依赖项
├── youdub/               # 核心逻辑包
│   ├── step000...        # 视频下载 (YouTube/Bilibili)
│   ├── step010...        # 人声背景声分离 (Demucs)
│   ├── step020...        # 语音转文字 (WhisperX)
│   ├── step030...        # 翻译 (GPT/Ollama/Groq)
│   ├── step040...        # 语音合成 (TTS/XTTS/Bytedance)
│   ├── step050...        # 视频合成 (FFmpeg)
│   ├── step060...        # 生成发布信息
│   ├── step070...        # 上传 Bilibili
│   ├── terminology.py    # 术语管理
│   └── do_everything.py  # 全流程编排
├── config/               # 配置文件与凭据
│   ├── cookies.txt       # YouTube 登录 Cookie
│   ├── bilibili.txt      # Bilibili 登录 Cookie (原始)
│   └── terminology.json  # 自定义术语表
├── tools/                # 维护/管理工具脚本
│   ├── setup_bilibili.py # 配置 Bilibili 凭据
│   ├── download_xtts.py  # 预下载 XTTS 模型
│   ├── manage_models.py  # 模型管理
│   └── ...
├── scripts/              # Windows 快捷脚本 (.bat / .ps1)
│   ├── setup_windows.bat # 一键环境配置
│   ├── run_windows.bat   # 快速启动
│   └── ...
├── docs/                 # 项目文档与指南
├── models/               # 本地模型文件存储
└── videos/               # 处理结果输出目录
```

## 核心流程
1. **下载**: 从 URL 下载原视频及元数据。
2. **分离**: 提取人声用于后续克隆。
3. **识别**: 生成带时间戳的字幕。
4. **翻译**: 将字幕翻译为目标语言（支持术语一致性）。
5. **合成语音**: 根据译文生成配音。
6. **渲染**: 将配音、字幕与原视频合成为最终作品。
7. **发布**: 自动上传到 Bilibili 并填写简介。

## 开发规范
参考 `AGENTS.md` 了解代码风格、命名规范及错误处理原则。
