# YouDub-webui：一键把YouTube视频变成中文配音

**下载 → 翻译 → 配音 → 合成，全部自动！**

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

**翻译不出来？**
- Groq: 检查 key 对不对
- Ollama: 确保 ollama 正在运行

---

## 技术支持

- GitHub: https://github.com/skyconnfig/YouDub-webui/issues
- B站: https://space.bilibili.com/1263732318

---

**超简单！有问题重启试试！** 🚀
