# Bilibili Cookie 配置指南

## 问题说明

Bilibili 现在加强了反爬机制，下载视频需要登录状态（Cookie）。如果出现 HTTP Error 412 错误，说明需要配置 Cookie。

## 解决方案

### 方法一：使用浏览器 Cookie（推荐）

1. **安装浏览器扩展**（推荐 Chrome/Edge）：
   - 安装 "Get cookies.txt locally" 扩展
   - 或使用 "Cookie-Editor" 扩展

2. **导出 Cookie**：
   - 登录 bilibili.com
   - 点击扩展图标
   - 导出为 cookies.txt 格式
   - 保存到项目根目录

3. **修改下载代码**：
   编辑 `youdub/step000_video_downloader.py`，在 ydl_opts 中添加：
   ```python
   ydl_opts = {
       'format': f'bestvideo[ext=mp4][height<={resolution}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
       'writeinfojson': True,
       'writethumbnail': True,
       'outtmpl': os.path.join(folder_path, sanitized_uploader, f'{upload_date} {sanitized_title}', 'download'),
       'ignoreerrors': True,
       'cookiefile': 'cookies.txt',  # 添加这一行
   }
   ```

### 方法二：手动下载视频

如果不想配置 Cookie，可以：
1. 使用其他工具（如 JDownloader、you-get）手动下载视频
2. 将下载的视频放入正确的文件夹结构：
   ```
   videos/
   └── {up主名称}/
       └── {日期} {视频标题}/
           ├── download.mp4
           └── ...
   ```
3. 然后使用 "全自动" 模式处理

### 方法三：下载 YouTube 视频

YouDub-webui 对 YouTube 的支持更好，可以尝试下载 YouTube 视频。

## 注意事项

- Cookie 文件包含敏感信息，请勿上传到公共仓库
- Bilibili Cookie 有过期时间，需要定期更新
- 建议将 cookies.txt 添加到 .gitignore
