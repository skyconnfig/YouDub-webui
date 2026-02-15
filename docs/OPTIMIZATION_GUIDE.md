# YouDub 快速模式配置指南

## 🚀 推荐配置（速度优先）

### 方案 1：极速模式（适合快速预览）
```python
# 在 Gradio UI 中设置：
Resolution: 720p                    # 降低分辨率，下载更快
Demucs Model: htdemucs             # 比 htdemucs_ft 快 2 倍
Number of shifts: 0                # 最大速度提升（质量略降）
Whisper Model: small               # 比 large 快 4 倍
Whisper Batch Size: 64             # 提高批处理大小
Whisper Diarization: False         # 关闭说话人分离
Max Workers: 3                     # 并行处理 3 个视频
```

### 方案 2：平衡模式（推荐日常使用）
```python
# 在 Gradio UI 中设置：
Resolution: 1080p
Demucs Model: htdemucs_ft
Number of shifts: 1                # 质量与速度平衡
Whisper Model: medium              # 比 large 快 2 倍，质量仍可接受
Whisper Batch Size: 32
Whisper Diarization: False
Max Workers: 2
```

### 方案 3：质量模式（最终发布）
```python
# 在 Gradio UI 中设置：
Resolution: 1080p
Demucs Model: htdemucs_ft
Number of shifts: 5                # 最高质量
Whisper Model: large
Whisper Batch Size: 16
Whisper Diarization: True          # 启用说话人分离
Max Workers: 1                     # 单视频最高质量处理
```

---

## ⚡ 速度对比

| 配置 | 预估耗时 | 质量 | 适用场景 |
|------|----------|------|----------|
| 极速模式 | 3-5 分钟 | ⭐⭐⭐ | 快速预览、测试 |
| 平衡模式 | 6-10 分钟 | ⭐⭐⭐⭐ | 日常使用 |
| 质量模式 | 15-20 分钟 | ⭐⭐⭐⭐⭐ | 最终发布 |

---

## 🔧 其他优化建议

### 1. 使用 GPU 加速
确保已安装 CUDA 版本的 PyTorch：
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. 使用更快的 TTS
- 勾选 **Force Bytedance**：使用火山引擎 TTS（比 XTTS 快 3-5 倍）
- 需要配置 `APPID` 和 `ACCESS_TOKEN` 环境变量

### 3. 批量处理技巧
- 下载多个视频后，使用 **Max Workers: 2-3** 并行处理
- 夜间批量处理，设置 **Max Workers: 5**

### 4. 跳过已处理步骤
程序会自动检测已完成的步骤并跳过：
- `download.webm` / `download.mp4` - 视频已下载
- `audio_vocals.wav` - 人声已分离
- `transcript.json` - 语音识别完成
- `translation.json` - 翻译完成

---

## 📈 性能监控

在运行过程中观察日志：
- 如果看到 GPU 内存不足，降低 `Whisper Batch Size`
- 如果 CPU 使用率 100%，减少 `Max Workers`
- 如果网络慢，降低 `Resolution`

---

## 🎯 实际测试建议

先用一个短视频（1-2分钟）测试不同配置：
1. 使用极速模式跑通全流程
2. 对比质量模式，看质量差异是否可接受
3. 根据结果调整参数

---

## 💡 高级技巧

### 分离下载和处理
1. 先用 "Download Video" 界面批量下载多个视频
2. 再用 "Do Everything" 处理已下载的视频
3. 这样下载时就可以开始处理第一批

### 使用队列系统
修改 `max_workers` 根据你的硬件：
- **8GB 显存**: Max Workers = 1
- **16GB 显存**: Max Workers = 2
- **24GB+ 显存**: Max Workers = 3-5

### 优化 Demucs
如果主要处理人声视频，可以修改代码跳过人声分离：
```python
# 在 step010_demucs_vr.py 中，如果视频本身只有人声，直接复制音频
```
