import os
import re
import subprocess
import shutil
from loguru import logger

# Setup Deno for yt-dlp JavaScript runtime before importing yt_dlp
DENO_PATH = None
DENO_CANDIDATES = [
    os.path.expanduser("~/.deno/bin/deno.exe"),
    os.path.expanduser("~/.deno/bin/deno"),
    r"C:\Users\lixin\.deno\bin\deno.exe",
    r"C:\Program Files\deno\deno.exe",
    "deno",  # Try system PATH
]

for deno_candidate in DENO_CANDIDATES:
    if shutil.which(deno_candidate) or os.path.exists(deno_candidate):
        DENO_PATH = deno_candidate if shutil.which(deno_candidate) else deno_candidate
        # Add to PATH if not already there
        deno_dir = os.path.dirname(DENO_PATH) if os.path.exists(DENO_PATH) else os.path.dirname(shutil.which(deno_candidate))
        if deno_dir:
            current_path = os.environ.get('PATH', '')
            if deno_dir not in current_path:
                os.environ['PATH'] = deno_dir + os.pathsep + current_path
        # Set environment variable for yt-dlp to find Deno
        os.environ['YTDL_DENO_PATH'] = DENO_PATH
        os.environ['YTDLPSCRIPT_PATH'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'yt-dlp-player.js')
        break

# Import yt_dlp after setting up PATH
import yt_dlp

if DENO_PATH:
    logger.info(f"✅ Deno JS runtime found: {DENO_PATH}")
    # Verify Deno works
    try:
        result = subprocess.run([DENO_PATH, "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"✅ Deno version: {result.stdout.strip()}")
        else:
            logger.warning(f"⚠️ Deno test failed: {result.stderr}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to verify Deno: {e}")
else:
    logger.error("❌ Deno NOT FOUND! YouTube downloads will fail!")
    logger.error("❌ Please install Deno to fix YouTube download issues:")
    logger.error("   Windows PowerShell (Admin): winget install deno")
    logger.error("   OR: irm https://deno.land/install.ps1 | iex")
    logger.error("")
    logger.error("   After installation, restart this application.")
    logger.warning("⚠️ Without Deno, YouTube downloads may fail due to signature challenges")


# Get proxy settings from environment
PROXY_URL = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY') or os.getenv('http_proxy') or os.getenv('https_proxy')
if PROXY_URL:
    logger.info(f"Using proxy: {PROXY_URL}")


def sanitize_title(title):
    # Only keep numbers, letters, Chinese characters, and spaces
    title = re.sub(r'[^\w\u4e00-\u9fff \d_-]', '', title)
    # Replace multiple spaces with a single space
    title = re.sub(r'\s+', ' ', title)
    return title


def get_target_folder(info, folder_path):
    # Handle None info (e.g., when video download fails)
    if info is None:
        return None
    
    # Handle missing title
    title = info.get('title')
    if title is None:
        logger.warning(f"Video info missing title: {info.get('id', 'unknown')}")
        return None
    
    sanitized_title = sanitize_title(title)
    sanitized_uploader = sanitize_title(info.get('uploader', 'Unknown'))
    upload_date = info.get('upload_date', 'Unknown')
    if upload_date == 'Unknown':
        return None

    output_folder = os.path.join(
        folder_path, sanitized_uploader, f'{upload_date} {sanitized_title}')

    return output_folder

def download_single_video(info, folder_path, resolution='1080p'):
    # Handle None info
    if info is None:
        logger.warning("Cannot download video: info is None")
        return None
    
    # Get title with fallback
    title = info.get('title')
    if title is None:
        logger.warning(f"Cannot download video: missing title (id: {info.get('id', 'unknown')})")
        return None
    
    sanitized_title = sanitize_title(title)
    sanitized_uploader = sanitize_title(info.get('uploader', 'Unknown'))
    upload_date = info.get('upload_date', 'Unknown')
    if upload_date == 'Unknown':
        return None
    
    output_folder = os.path.join(folder_path, sanitized_uploader, f'{upload_date} {sanitized_title}')
    # Check for existing video in either mp4 or webm format
    if os.path.exists(os.path.join(output_folder, 'download.mp4')) or os.path.exists(os.path.join(output_folder, 'download.webm')):
        logger.info(f'Video already downloaded in {output_folder}')
        return output_folder
    
    resolution = resolution.replace('p', '')
    
    # Force MP4 format
    ydl_opts = get_ydl_opts({
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'writeinfojson': True,
        'writethumbnail': True,
        'outtmpl': os.path.join(folder_path, sanitized_uploader, f'{upload_date} {sanitized_title}', 'download'),
    })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([info['webpage_url']])
        logger.info(f'Video downloaded in {output_folder}')
        return output_folder
    except Exception as e:
        logger.error(f"Error downloading video {title}: {e}")
        return None

def download_videos(info_list, folder_path, resolution='1080p'):
    for info in info_list:
        download_single_video(info, folder_path, resolution)

def find_cookies_file():
    """Find cookies.txt file in current directory or parent directories"""
    current_dir = os.getcwd()
    # Check multiple possible locations
    possible_paths = [
        os.path.join(current_dir, 'cookies.txt'),
        os.path.join(current_dir, 'config', 'cookies.txt'),
        os.path.join(current_dir, '..', 'cookies.txt'),
        os.path.join(current_dir, '..', 'config', 'cookies.txt'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cookies.txt'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'cookies.txt'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    return None


def find_deno_executable():
    """Find Deno executable for JavaScript runtime"""
    possible_paths = [
        os.path.expanduser("~/.deno/bin/deno.exe"),
        os.path.expanduser("~/.deno/bin/deno"),
        r"C:\Users\lixin\.deno\bin\deno.exe",
        r"C:\Program Files\deno\deno.exe",
        "deno",  # Try system PATH
    ]
    
    for path in possible_paths:
        if os.path.exists(path) or path == "deno":
            return path
    return None


def get_ydl_opts(extra_opts=None):
    """Get base yt-dlp options with proxy, cookie, and JS runtime support"""
    opts = {
        # Default format - simplest possible
        'ignoreerrors': False,
        'no_warnings': False,
        # Disable SSL certificate verification (for proxy/mitm situations)
        'nocheckcertificate': True,
        # Add proper browser headers
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
        },
        # Enable remote components for EJS challenge solver
        # This is required for YouTube downloads with newer yt-dlp versions
        'remote_components': {'ejs:github'},
        # Also specify js_runtimes to ensure deno is used
        'js_runtimes': {'deno': {}},
    }
    
    # Add proxy if configured
    if PROXY_URL:
        opts['proxy'] = PROXY_URL
    
    # Add cookies if available (for YouTube authentication)
    cookie_file = find_cookies_file()
    if cookie_file:
        opts['cookiefile'] = cookie_file
        logger.info(f"Using cookies from {cookie_file}")
    
    # Set up verbose output for debugging
    opts['verbose'] = False  # Set to True if you need more debug info
    
    # Add extra options
    if extra_opts:
        opts.update(extra_opts)
    
    return opts


def get_info_list_from_url(url, num_videos):
    if isinstance(url, str):
        url = [url]

    # Download JSON information first
    ydl_opts = get_ydl_opts({
        'dumpjson': True,
        'playlistend': num_videos,
        # Add typical browser headers to avoid detection
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
    })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for u in url:
            try:
                logger.info(f"Extracting info from: {u}")
                result = ydl.extract_info(u, download=False)
                if result is None:
                    logger.error(f"Failed to extract info from URL: {u}")
                    continue
                    
                if 'entries' in result:
                    # Playlist
                    for video_info in result['entries']:
                        if video_info is not None:
                            yield video_info
                        else:
                            logger.warning("Skipping None entry in playlist")
                else:
                    # Single video
                    yield result
            except Exception as e:
                logger.error(f"Error extracting info from {u}: {e}")
                continue

def download_from_url(url, folder_path, resolution='1080p', num_videos=5):
    resolution = resolution.replace('p', '')
    if isinstance(url, str):
        url = [url]

    # Download JSON information first
    ydl_opts = get_ydl_opts({
        'dumpjson': True,
        'playlistend': num_videos,
    })

    video_info_list = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for u in url:
            try:
                result = ydl.extract_info(u, download=False)
                if result is None:
                    logger.error(f"Failed to extract info from URL: {u}")
                    continue
                    
                if 'entries' in result:
                    # Filter out None entries from playlist
                    valid_entries = [e for e in result['entries'] if e is not None]
                    video_info_list.extend(valid_entries)
                else:
                    video_info_list.append(result)
            except Exception as e:
                logger.error(f"Error extracting info from {u}: {e}")
                continue

    # Now download videos with sanitized titles
    download_videos(video_info_list, folder_path, resolution)
    return f"Downloaded {len(video_info_list)} videos to {folder_path}"


if __name__ == '__main__':
    # Example usage
    url = 'https://www.youtube.com/watch?v=3LPJfIKxwWc'
    folder_path = 'videos'
    download_from_url(url, folder_path)
