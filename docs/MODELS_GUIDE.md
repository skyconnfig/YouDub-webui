# YouDub 模型管理指南

## 📁 模型存储位置

现在所有模型都会存储在项目目录的 `models/` 文件夹中：

```
YouDub-webui/
├── models/
│   ├── ASR/whisper/          # Whisper语音识别模型
│   ├── torch_hub/            # Demucs人声分离模型
│   └── TTS/                  # TTS语音合成模型
```

**好处：**
- ✅ 模型不会占用C盘空间
- ✅ 重装系统后模型不会丢失
- ✅ 可以复制整个项目到其他电脑直接使用
- ✅ 避免重复下载

---

## 🚀 快速开始

### 1. 运行配置检测（推荐）

```bash
# Windows
detect_config.bat

# 或手动运行
python detect_optimal_config.py
```

这将自动检测你的硬件并推荐最优配置。

### 2. 管理模型文件

```bash
# Windows 交互式菜单
manage_models.bat

# 或命令行模式
python manage_models.py info      # 查看模型状态
python manage_models.py migrate   # 迁移系统缓存到本地
python manage_models.py download medium  # 下载Whisper medium模型
```

---

## 📥 模型下载指南

### Whisper 模型（语音识别）

| 模型 | 大小 | 速度 | 质量 | 推荐度 |
|------|------|------|------|--------|
| tiny | 39 MB | 极快 | 较低 | ⭐ |
| base | 74 MB | 很快 | 一般 | ⭐⭐ |
| small | 244 MB | 快 | 良好 | ⭐⭐⭐⭐ |
| medium | 769 MB | 中等 | 很好 | ⭐⭐⭐⭐⭐ |
| large | 1550 MB | 慢 | 最佳 | ⭐⭐⭐⭐ |

**推荐：**
- **RTX 4060 (8GB)**: medium
- **更高端显卡**: large

**下载命令：**
```bash
python manage_models.py download medium
```

### Demucs 模型（人声分离）

首次运行时会自动下载，已配置下载到本地目录。

### TTS 模型（语音合成）

首次运行时会自动下载，已配置下载到本地目录。

**建议：** 使用 Bytedance TTS（火山引擎），不占用本地显存，速度更快。

---

## 🔄 迁移已有模型

如果你之前已经下载过模型，它们在系统缓存中，可以迁移到本地：

```bash
manage_models.bat
# 选择选项 2: 迁移系统缓存到本地
```

或命令行：
```bash
python manage_models.py migrate
```

这将自动复制：
- `~/.cache/torch/hub/` → `./models/torch_hub/`
- `~/.local/share/tts/` → `./models/TTS/`

---

## 🧹 清理系统缓存

迁移完成后，可以清理系统缓存释放空间：

```bash
manage_models.bat
# 选择选项 4: 清理系统缓存
```

⚠️ **注意：** 清理前确保迁移已完成！

---

## 💾 模型备份

所有模型都在 `models/` 目录，可以直接：

1. **压缩备份：**
   ```bash
   # 压缩整个models目录
   tar -czvf youdub_models_backup.tar.gz models/
   ```

2. **复制到其他电脑：**
   - 复制 `models/` 目录到新电脑
   - 无需重新下载，直接使用

---

## ⚙️ 环境变量说明

程序自动设置以下环境变量（在 `app.py` 中）：

```python
TORCH_HOME = ./models/torch_hub      # Demucs模型位置
TTS_HOME = ./models/TTS              # TTS模型位置
```

**不要手动修改这些变量**，已通过代码自动配置。

---

## 🐛 常见问题

### Q: 模型下载很慢？

**A:** 已在 `app.py` 中配置 HuggingFace 镜像：
```python
HF_ENDPOINT = https://hf-mirror.com
```

如需其他镜像，修改 `.env` 文件：
```
HF_ENDPOINT=https://hf-mirror.com
```

### Q: 显存不足？

**A:** 参考 `detect_optimal_config.py` 的输出，使用推荐的模型大小。

### Q: 如何切换模型？

**A:** 在Gradio界面中修改 `Whisper Model` 选项：
- small → 更快
- medium → 平衡
- large → 更好质量（需要更多显存）

---

## 📊 模型大小参考

完整安装后 `models/` 目录大小：

| 组件 | 大小 | 必需 |
|------|------|------|
| Whisper medium | ~800 MB | ✅ 推荐 |
| Whisper large | ~1.5 GB | 可选 |
| Demucs htdemucs_ft | ~300 MB | ✅ 必需 |
| TTS XTTS v2 | ~400 MB | 如不用Bytedance |
| **总计** | **~1.5-2.5 GB** | - |

确保磁盘有足够空间！

---

## 🎯 最佳实践

1. **首次使用：**
   ```bash
   detect_config.bat          # 检测最优配置
   manage_models.bat          # 下载所需模型
   python app.py              # 启动应用
   ```

2. **日常使用：**
   ```bash
   python app.py              # 直接启动，模型已就绪
   ```

3. **换电脑：**
   - 复制整个项目文件夹（包含 `models/`）
   - 在新电脑上直接运行，无需重新下载

---

## 🆘 需要帮助？

运行诊断：
```bash
python manage_models.py info
```

查看详细输出，确认：
- 模型文件是否存在
- 路径是否正确
- 文件大小是否正常
