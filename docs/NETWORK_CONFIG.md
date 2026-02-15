# 网络配置指南

## SSL 证书验证错误

如果你遇到类似以下错误：
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Hostname mismatch
```

这通常是因为网络环境问题，可能需要配置代理。

## 配置代理

### 方法 1：环境变量（推荐）

在运行程序前设置环境变量：

**Windows PowerShell:**
```powershell
$env:HTTP_PROXY = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"
python app.py
```

**Windows CMD:**
```cmd
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890
python app.py
```

**或者永久设置到 .env 文件：**
```
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 方法 2：修改代码（临时方案）

如果上述方法无效，可以禁用 SSL 验证（不推荐用于生产环境）：

编辑 `youdub/step000_video_downloader.py`，在 `get_ydl_opts` 函数中添加：

```python
def get_ydl_opts(extra_opts=None):
    """Get base yt-dlp options with proxy support"""
    opts = {
        'format': 'best',
        'ignoreerrors': True,
        'nocheckcertificate': True,  # 添加这一行禁用 SSL 验证
    }
    # ... rest of the code
```

## 常见代理端口

| 代理工具 | 默认 HTTP 端口 | 默认 SOCKS5 端口 |
|---------|---------------|-----------------|
| Clash | 7890 | 7891 |
| Clash Verge | 7897 | - |
| v2rayN | 10809 | 10808 |
| Shadowsocks | - | 1080 |

## 验证代理

在浏览器中访问以下网址验证代理是否正常工作：
- YouTube: https://www.youtube.com
- Google: https://www.google.com

## 测试下载

配置好代理后，先尝试下载一个 YouTube 视频测试：
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## 如果仍然无法下载

1. 确保 yt-dlp 是最新版本：
   ```bash
   pip install -U yt-dlp
   ```

2. 检查防火墙或安全软件是否拦截了 Python 的网络请求

3. 尝试使用其他网络环境

4. 手动下载视频：
   - 使用其他工具下载视频
   - 放入正确的文件夹结构
   - 使用本工具进行后续处理
