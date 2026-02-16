import subprocess
import time
import json
import os
import traceback
from bilibili_toolman.bilisession.web import BiliSession
from bilibili_toolman.bilisession.common.submission import Submission
from dotenv import load_dotenv
from loguru import logger
from requests.exceptions import ProxyError
# Load environment variables
load_dotenv()

def check_upload_permission(session, video_path):
    """检查账户是否有上传权限"""
    import os.path
    basename = os.path.basename(video_path)
    size = os.path.getsize(video_path)
    
    try:
        response = session._preupload(name=basename, size=size)
        config = response.json()
        
        if config.get('OK') == 0 and config.get('code') == 601:
            # 账户需要完善信息
            return False, (
                "Bilibili 账户需要完善信息才能上传视频。\n\n"
                "错误信息：您未上传过视频，请先完善信息后再试\n\n"
                "解决方案：\n"
                "1. 在浏览器中登录 Bilibili (https://www.bilibili.com)\n"
                "2. 进入创作者中心 (https://member.bilibili.com/platform/upload)\n"
                "3. 完善账户信息：\n"
                "   - 上传头像\n"
                "   - 填写个人简介\n"
                "   - 完成实名认证（如需要）\n"
                "4. 手动上传一个测试视频（哪怕只传几秒钟）\n"
                "5. 完成以上步骤后，API 上传功能才会开通\n\n"
                "注意：这是 Bilibili 的账户限制，不是代码问题。\n"
                "必须完成账户初始化才能使用 API 上传功能。"
            )
        
        if 'auth' not in config:
            return False, (
                "无法获取上传授权（auth token）。\n\n"
                "API 响应内容：\n" + json.dumps(config, indent=2, ensure_ascii=False) + "\n\n"
                "可能的原因：\n"
                "1. 账户未完成实名认证\n"
                "2. 账户从未上传过视频\n"
                "3. 登录凭据已过期\n\n"
                "请尝试在浏览器中手动上传一个视频，然后再使用此工具。"
            )
        
        return True, None
    except Exception as e:
        return False, f"检查上传权限时出错: {e}"

def bili_login():
    SESSDATA = os.getenv('BILI_SESSDATA')
    BILI_JCT = os.getenv('BILI_BILI_JCT')
    
    if not SESSDATA or not BILI_JCT:
        raise Exception('BILIBILI 登录失败：缺少 SESSDATA 或 BILI_JCT 环境变量。请在 .env 文件中设置。')
    
    try:
        session = BiliSession(f'SESSDATA={SESSDATA};bili_jct={BILI_JCT}')
        logger.info(f"bilibili 会话已创建，准备上传...")
        return session
    except ProxyError as pe:
        logger.error(f"bilibili 登录失败 - 代理错误: {pe}")
        logger.debug(traceback.format_exc())
        raise Exception(
            "BILIBILI 登录失败：代理服务器连接错误。\n\n"
            "可能的原因：\n"
            "1. 系统配置了代理服务器，但代理服务器未运行或拒绝连接\n"
            "2. 代理服务器配置错误\n\n"
            "解决方案：\n"
            "方法1 - 禁用代理（推荐）：\n"
            "  • 检查系统代理设置：设置 → 网络和 Internet → 代理\n"
            "  • 关闭'使用代理服务器'选项\n"
            "  • 或删除 HTTP_PROXY/HTTPS_PROXY 环境变量\n\n"
            "方法2 - 修复代理：\n"
            "  • 确保代理软件（Clash/V2Ray/Shadowsocks等）正在运行\n"
            "  • 检查代理端口配置是否正确\n\n"
            "方法3 - 使用环境变量绕过代理：\n"
            "  • 在 .env 文件中添加：NO_PROXY=api.bilibili.com,member.bilibili.com\n\n"
            f"原始错误: {pe}"
        )
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
    
    # 检查账户上传权限
    logger.info("正在检查 Bilibili 账户上传权限...")
    can_upload, error_msg = check_upload_permission(session, video_path)
    if not can_upload:
        raise Exception(error_msg)
    logger.info("账户上传权限检查通过")
    
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
            except KeyError as ke:
                # 处理 bilibili_toolman 库中的 KeyError（如 'OK' 或 'auth' 键不存在）
                error_msg = str(ke)
                if error_msg == "'OK'":
                    raise Exception(
                        "视频上传失败：Bilibili API 返回了非预期的响应格式。\n"
                        "可能的原因：\n"
                        "1. 网络连接不稳定（上传进度达到 4% 后中断）\n"
                        "2. Bilibili 服务器暂时不可用\n"
                        "3. 上传的视频格式或大小不符合要求\n\n"
                        "建议：\n"
                        "1. 检查网络连接是否稳定\n"
                        "2. 等待几分钟后重试\n"
                        "3. 如果问题持续，尝试手动上传到 Bilibili"
                    )
                elif error_msg == "'auth'":
                    raise Exception(
                        "视频上传失败：无法获取上传授权（auth token）。\n\n"
                        "可能的原因：\n"
                        "1. Bilibili 账户没有上传权限（需要实名认证）\n"
                        "2. 账户被封禁或限制上传\n"
                        "3. 登录凭据已过期（SESSDATA 或 BILI_JCT 失效）\n"
                        "4. Bilibili API 响应格式变更\n\n"
                        "解决方案：\n"
                        "1. 确保 Bilibili 账户已完成实名认证\n"
                        "2. 在浏览器中登录 Bilibili，确认可以正常上传视频\n"
                        "3. 重新获取 SESSDATA 和 BILI_JCT（从浏览器 Cookie 中复制最新值）\n"
                        "4. 检查账户是否有任何限制或封禁通知\n\n"
                        "如果问题持续，建议：\n"
                        "• 尝试手动上传视频到 Bilibili 确认账户正常\n"
                        "• 检查 Bilibili 账户设置中的实名认证状态"
                    )
                else:
                    raise
            except Exception as upload_err:
                error_msg = str(upload_err)
                if "resp" in error_msg and "referenced before assignment" in error_msg:
                    raise Exception(
                        "视频上传失败：无法获取上传授权。\n\n"
                        "可能的原因：\n"
                        "1. Bilibili 账户没有上传权限（需要实名认证）\n"
                        "2. 登录凭据已过期（SESSDATA 或 BILI_JCT 失效）\n"
                        "3. Bilibili API 临时不可用\n\n"
                        "解决方案：\n"
                        "1. 确保 Bilibili 账户已完成实名认证\n"
                        "2. 重新获取 SESSDATA 和 BILI_JCT（从浏览器 Cookie 中复制最新值）\n"
                        "3. 尝试手动上传视频确认账户正常\n\n"
                        f"原始错误: {upload_err}"
                    )
                if error_msg == "'OK'":
                    raise Exception(
                        "视频上传失败：Bilibili API 返回了非预期的响应格式。\n"
                        "可能的原因：\n"
                        "1. 网络连接不稳定（上传进度达到 4% 后中断）\n"
                        "2. Bilibili 服务器暂时不可用\n"
                        "3. 上传的视频格式或大小不符合要求\n\n"
                        "建议：\n"
                        "1. 检查网络连接是否稳定\n"
                        "2. 等待几分钟后重试\n"
                        "3. 如果问题持续，尝试手动上传到 Bilibili"
                    )
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