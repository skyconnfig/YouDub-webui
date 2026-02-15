# YouTube 下载问题解决方案

## 问题 1: 缺少 JavaScript 运行时

### 安装 Deno (推荐)

**Windows PowerShell (管理员):**
```powershell
# 使用 winget 安装
winget install deno

# 或者使用 PowerShell 脚本
irm https://deno.land/install.ps1 | iex
```

**手动安装:**
1. 下载 Deno: https://github.com/denoland/deno/releases
2. 解压并将 deno.exe 添加到系统 PATH
3. 验证安装: `deno --version`

### 安装 Node.js (备选)
```powershell
# 使用 winget
winget install OpenJS.NodeJS

# 或者从官网下载安装
# https://nodejs.org/
```

---

## 问题 2: YouTube 登录验证

### 方案 A: 使用浏览器 Cookie (推荐)

**步骤 1: 安装浏览器扩展**
- 安装 "Get cookies.txt LOCALLY" 扩展 (Chrome/Edge)
- 或 "Cookie-Editor" 扩展

**步骤 2: 导出 Cookie**
1. 在浏览器中登录 YouTube (play.google.com)
2. 确保能看到 YouTube 首页
3. 点击扩展图标
4. 导出为 `cookies.txt` 格式
5. 保存到项目根目录 `D:\YouDub-webui\`

**步骤 3: 修改代码支持 Cookie**

编辑 `youdub/step000_video_downloader.py`，在 `get_ydl_opts` 函数中添加：

```python
def get_ydl_opts(extra_opts=None):
    """Get base yt-dlp options with proxy support"""
    opts = {
        'format': 'best',
        'ignoreerrors': True,
    }
    
    # Add proxy if configured
    if PROXY_URL:
        opts['proxy'] = PROXY_URL
    
    # Add cookies for YouTube authentication
    cookie_file = 'cookies.txt'
    if os.path.exists(cookie_file):
        opts['cookiefile'] = cookie_file
        logger.info(f"Using cookies from {cookie_file}")
    
    # Add extra options
    if extra_opts:
        opts.update(extra_opts)
    
    return opts
```

### 方案 B: 使用 cookies-from-browser (更简单)

编辑 `youdub/step000_video_downloader.py`：

```python
def get_ydl_opts(extra_opts=None):
    """Get base yt-dlp options with proxy support"""
    opts = {
        'format': 'best',
        'ignoreerrors': True,
        # 自动从浏览器获取 cookies
        'cookiesfrombrowser': ('chrome',),  # 或 ('edge',), ('firefox',)
    }
    
    # Add proxy if configured
    if PROXY_URL:
        opts['proxy'] = PROXY_URL
    
    # Add extra options
    if extra_opts:
        opts.update(extra_opts)
    
    return opts
```

**注意:** 使用 `cookiesfrombrowser` 时需要：
1. 关闭浏览器（或创建独立的浏览器 profile）
2. 确保 yt-dlp 能访问浏览器的数据目录

---

## 快速修复步骤

### 1. 安装 Deno
```powershell
winget install deno
# 重启终端
```

### 2. 添加 Cookie 支持
我会帮你修改代码，自动检测并使用 cookies.txt 文件。

### 3. 获取 YouTube Cookie
1. 在浏览器中登录 YouTube
2. 使用扩展导出 cookies.txt
3. 放到项目目录

---

## 替代方案

如果上述方法都无效，可以：

### 使用其他下载工具
1. 使用 [yt-dlp 命令行](https://github.com/yt-dlp/yt-dlp) 手动下载
2. 使用 [4K Video Downloader](https://www.4kdownload.com/)
3. 使用 [JDownloader](https://jdownloader.org/)

### 手动下载流程
1. 用其他工具下载视频
2. 放入正确的文件夹结构：
   ```
   videos/
   └── {频道名称}/
       └── {日期} {视频标题}/
           ├── download.mp4
           └── ...
   ```
3. 使用 YouDub-webui 的后续步骤处理

---

## 常见问题

### Q: 为什么需要登录？
A: YouTube 检测到异常流量时需要验证用户不是机器人。

### Q: Cookie 会过期吗？
A: 会，通常需要定期重新导出（几周到几个月）。

### Q: 使用 Cookie 安全吗？
A: Cookie 文件包含登录凭证，请勿分享给他人或上传到公共仓库。

### Q: 不想用 Cookie 怎么办？
A: 可以手动下载视频，然后使用本工具进行翻译和配音处理。
