# YouDub-webui：一键把YouTube视频变成中文配音

**下载 → 翻译 → 配音 → 合成，全部自动！**

---

## ⭐ 新增功能 (2025.02)

### 🎤 Edge-TTS 语音合成引擎
- **免费高质量**：使用 Microsoft Edge TTS，无需 API Key
- **多引擎支持**：支持三种 TTS 引擎切换
  - **XTTS** (默认)：本地声音克隆，保留原音色
  - **Edge-TTS**：免费云端 TTS，无需本地模型
  - **ByteDance**：火山引擎 TTS

### ⚙️ 配置预设系统
- **高质量模式**：适合 8GB+ 显存电脑
- **快速模式**：适合批量处理
- **低显存模式**：适合 4GB 显存电脑

### 🔧 翻译提示词优化
- 更自然的翻译腔调
- 更好的上下文理解
- 术语一致性处理

---

## 5分钟快速开始

### 1️⃣ 下载代码
```bash
git clone https://github.com/skyconnfig/YouDub-webui.git
cd YouDub-webui
```

### 2️⃣ 安装（双击）
```
双击 scripts\setup_windows.bat
```

等它跑完...

### 3️⃣ 配置（一行搞定）
复制 `.env.example` 为 `.env`，填这个：

```env
# 翻译用免费的 Groq！
TRANSLATION_BACKEND = 'groq'
GROQ_API_KEY = '去 https://console.groq.com 申请免费的key'
```

### 4️⃣ 启动（双击）
```
双击 scripts\run_windows.bat
```

浏览器会自动打开 `http://localhost:7860`

### 5️⃣ 使用
1. 粘贴 YouTube 链接
2. 点 Submit
3. 等着拿中文配音视频！

---

## 🎛️ TTS 语音引擎选择

在 Gradio 界面中，可以选择不同的语音合成引擎：

| 引擎 | 特点 | 需要显存 |
|------|------|----------|
| **xtts** (默认) | 本地声音克隆，保留原音色 | 4GB+ |
| **edge** | 免费云端，无需本地模型 | 0 |
| **bytedance** | 火山引擎 TTS | 0 |

> 💡 **推荐**：有参考音频用 xtts，无参考音频用 edge

### Edge-TTS 音色选择
- `zh-CN-XiaoxiaoNeural` (女声 - 最自然)
- `zh-CN-YunxiNeural` (男声)
- `zh-CN-YunyangNeural` (男声 - 新闻风格)

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 打不开？ | 双击 `run_windows.bat` |
| 翻译失败？ | 检查 GROQ_API_KEY 对不对 |
| 下载失败？ | 开启代理 |
| 显存不够？ | Whisper 选 small，Demucs 选 htdemucs |

---

## 翻译服务对比

| 服务 | 收费 | 怎么弄 |
|------|------|--------|
| **Groq** | 免费！ | 去 groqconsole 申请 key |
| **Ollama** | 免费！ | 下载 ollama.com |
| OpenAI | 付费 | 买 api key |

**推荐 Groq，免费且速度快！**

---

## 配置说明

### 环境变量

```env
# 翻译（必选一个）
TRANSLATION_BACKEND = 'groq'        # groq / ollama / openai
GROQ_API_KEY = '你的key'

# B站上传（可选）
BILI_SESSDATA = '你的SESSDATA'
BILI_BILI_JCT = '你的bili_jct'

# 代理（打不开YouTube时）
HTTP_PROXY=http://127.0.0.1:10808
HTTPS_PROXY=http://127.0.0.1:10808
```

### 配置预设 (代码中)

| 预设 | Whisper | Demucs | 显存需求 | 适用场景 |
|------|---------|--------|----------|----------|
| `high_quality` | large | htdemucs_ft | 8GB+ | 最佳质量 |
| `balanced` | medium | htdemucs | 6GB | 均衡 |
| `fast` | small | htdemucs | 4GB | 快速处理 |
| `low_memory` | small | htdemucs | 4GB | 低显存 |

使用预设：
```python
from youdub.config_presets import load_preset

# 加载预设
config = load_preset('fast')
print(config)
```

---

## 安装新依赖

如果已经安装旧版本，需要安装新的依赖：

```bash
pip install edge-tts
```

---

## 推荐配置

**高配电脑**（8GB显存）
- Whisper: medium
- Demucs: htdemucs_ft
- 分辨率: 1080p

**低配电脑**（4GB显存）
- Whisper: small
- Demucs: htdemucs
- 分辨率: 720p
- Diarization: 关掉

---

## 常见报错

**ffmpeg找不到？**
- 项目已内置 ffmpeg，一般不用管
- 或者去 https://github.com/BtbN/FFmpeg-Builds/releases 下

**显存不够？**
- 改用 small 模型
- 关闭 Diarization
- TTS 引擎选择 "edge"（不占用显存）

**翻译不出来？**
- Groq: 检查 key 对不对
- Ollama: 确保 ollama 正在运行

**Edge-TTS 连接失败？**
- 检查网络，需要访问微软云服务
- 可切换到 xtts 或 bytedance 引擎

---

## 技术支持

- GitHub: https://github.com/skyconnfig/YouDub-webui/issues
- B站: https://space.bilibili.com/1263732318

---

**超简单！有问题重启试试！** 🚀
