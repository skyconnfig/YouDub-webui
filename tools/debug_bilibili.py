"""
调试 Bilibili 上传问题的脚本
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

def debug_preupload():
    """调试 preupload API 返回的内容"""
    from bilibili_toolman.bilisession.web import BiliSession
    
    SESSDATA = os.getenv('BILI_SESSDATA')
    BILI_JCT = os.getenv('BILI_BILI_JCT')
    
    if not SESSDATA or not BILI_JCT:
        print("错误：缺少 SESSDATA 或 BILI_JCT")
        return
    
    session = BiliSession(f'SESSDATA={SESSDATA};bili_jct={BILI_JCT}')
    
    # 测试 _preupload
    print("\n=== 测试 _preupload API ===")
    test_video_path = r"videos\Profit Studio\20260214 Stop Building Websites Build REAL Web Apps with Google AI Supabase\video.mp4"
    
    if not os.path.exists(test_video_path):
        print(f"视频文件不存在: {test_video_path}")
        # 尝试找任何一个视频文件
        for root, dirs, files in os.walk('videos'):
            if 'video.mp4' in files:
                test_video_path = os.path.join(root, 'video.mp4')
                print(f"找到视频文件: {test_video_path}")
                break
    
    if os.path.exists(test_video_path):
        basename = os.path.basename(test_video_path)
        size = os.path.getsize(test_video_path)
        
        print(f"视频文件: {basename}")
        print(f"文件大小: {size} bytes")
        
        # 调用 _preupload
        response = session._preupload(name=basename, size=size)
        print(f"\n_preupload 响应状态码: {response.status_code}")
        print(f"_preupload 响应内容:")
        try:
            config = response.json()
            print(json.dumps(config, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"解析 JSON 失败: {e}")
            print(f"原始响应: {response.text}")
    else:
        print("未找到视频文件进行测试")

if __name__ == '__main__':
    debug_preupload()
