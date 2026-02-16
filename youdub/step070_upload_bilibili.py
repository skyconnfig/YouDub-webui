import subprocess
import time
import json
import os
import traceback
from bilibili_toolman.bilisession.web import BiliSession
from bilibili_toolman.bilisession.common.submission import Submission
from dotenv import load_dotenv
from loguru import logger
# Load environment variables
load_dotenv()

def bili_login():
    SESSDATA = os.getenv('BILI_SESSDATA')
    BILI_JCT = os.getenv('BILI_BILI_JCT')
    
    if not SESSDATA or not BILI_JCT:
        raise Exception('BILIBILI 登录失败：缺少 SESSDATA 或 BILI_JCT 环境变量。请在 .env 文件中设置。')
    
    try:
        session = BiliSession(f'SESSDATA={SESSDATA};bili_jct={BILI_JCT}')
        # 验证登录是否成功
        self_info = session.Self
        if self_info.get('code') != 0:
            raise Exception(f"BILIBILI 登录验证失败: {self_info.get('message', '未知错误')}")
        logger.info(f"bilibili 登录成功，用户: {self_info.get('data', {}).get('uname', 'unknown')}")
        return session
    except Exception as e:
        logger.error(f"bilibili 登录失败: {e}")
        logger.debug(traceback.format_exc())
        raise Exception(f'bilibili 登录失败，请检查 SESSDATA 和 bili_jct 是否有效: {e}')

def upload_video(folder):
    submission_result_path = os.path.join(folder, 'bilibili.json')
    if os.path.exists(submission_result_path):
        with open(submission_result_path, 'r', encoding='utf-8') as f:
            submission_result = json.load(f)
        if submission_result['results'][0]['code'] == 0:
            logger.info('Video already uploaded.')
            return True
        
    video_path = os.path.join(folder, 'video.mp4')
    cover_path = os.path.join(folder, 'video.png')

    # Load summary data
    with open(os.path.join(folder, 'summary.json'), 'r', encoding='utf-8') as f:
        summary = json.load(f)
    summary['title'] = summary['title'].replace('视频标题：', '').strip()
    summary['summary'] = summary['summary'].replace(
        '视频摘要：', '').replace('视频简介：', '').strip()
    tags = summary.get('tags', [])
    if not isinstance(tags, list):
        tags = []
    title = f'【中配】{summary["title"]} - {summary["author"]}'
    with open(os.path.join(folder, 'download.info.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    title_English = data['title']
    webpage_url = data['webpage_url']
    description = f'{title_English}\n' + \
        summary['summary'] + '\n\n项目地址：https://github.com/liuzhao1225/YouDub-webui\nYouDub 是一个开创性的开源工具，旨在将 YouTube 和其他平台上的高质量视频翻译和配音成中文版本。该工具结合了最新的 AI 技术，包括语音识别、大型语言模型翻译，以及 AI 声音克隆技术，提供与原视频相似的中文配音，为中文用户提供卓越的观看体验。'

    session = bili_login()
    # time.sleep(5)
    
    # Submit the submission
    for retry in range(5):
        try:
            logger.info(f"开始上传视频: {video_path}")
            
            # Check if video file exists
            if not os.path.exists(video_path):
                raise Exception(f"视频文件不存在: {video_path}")
            
            # Check if cover file exists
            if not os.path.exists(cover_path):
                logger.warning(f"封面文件不存在: {cover_path}，将尝试不上传封面")
                cover_path = None
            
            # Upload video and get endpoint
            logger.info("正在上传视频文件到 Bilibili...")
            try:
                video_endpoint, _ = session.UploadVideo(video_path)
            except Exception as upload_err:
                error_msg = str(upload_err)
                if "resp" in error_msg and "referenced before assignment" in error_msg:
                    raise Exception(f"视频上传失败：可能是登录凭据过期或网络问题。请检查 SESSDATA 和 BILI_JCT 是否有效。原始错误: {upload_err}")
                raise

            # Create a submission object
            submission = Submission(
                title=title,
                desc=description
            )

            # Add video to submission
            submission.videos.append(
                Submission(
                    title=title,
                    video_endpoint=video_endpoint
                )
            )

            # Upload and set cover
            if cover_path:
                logger.info(f"正在上传封面: {cover_path}")
                try:
                    cover_url = session.UploadCover(cover_path)
                    if cover_url:
                        submission.cover_url = cover_url
                        logger.info(f"封面上传成功: {cover_url}")
                    else:
                        logger.warning("封面上传失败，将继续尝试提交视频")
                except Exception as cover_err:
                    logger.warning(f"封面上传失败: {cover_err}，将继续尝试提交视频")

            # Set additional properties
            tags = ['YouDub', summary["author"], 'AI',
                    'ChatGPT'] + tags + ['中文配音', '科学', '科普', ]
            for tag in tags[:12]:
                if len(tag) > 20:
                    tag = tag[:20]
                submission.tags.append(tag)
            submission.thread = 201  # 科普 201, 科技
            submission.copyright = submission.COPYRIGHT_REUPLOAD
            submission.source = webpage_url
            
            logger.info("正在提交视频信息...")
            response = session.SubmitSubmission(submission, seperate_parts=False)
            
            if response['results'][0]['code'] != 0:
                error_code = response['results'][0].get('code', 'unknown')
                error_message = response['results'][0].get('message', '未知错误')
                raise Exception(f"提交失败: 错误码 {error_code}, 消息: {error_message}")
            
            logger.info(f"视频上传成功: {response}")
            with open(os.path.join(folder, 'bilibili.json'), 'w', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=4)
            return True
            
        except Exception as e:
            logger.error(f"第 {retry + 1}/5 次上传尝试失败:\n{e}")
            logger.debug(traceback.format_exc())
            if retry < 4:  # 不是最后一次重试
                logger.info(f"等待 10 秒后重试...")
                time.sleep(10)
    
    raise Exception('上传失败：已达到最大重试次数')

def upload_all_videos_under_folder(folder):
    for dir, _, files in os.walk(folder):
        if 'video.mp4' in files:
            upload_video(dir)
    return f'All videos under {folder} uploaded.'

if __name__ == '__main__':
    
    # Example usage
    # folder = r'F:\YouDub-webui\videos\DigiDigger\20200824 How do non-euclidean games work Bitwise'
    folder = r'videos\The Game Theorists\20210522 Game Theory What Level is Ashs Pikachu Pokemon'
    upload_all_videos_under_folder(folder)