#!/usr/bin/env python3
"""
预下载 XTTS 模型
"""
import os
import sys

# 设置模型下载目录
project_root = os.path.dirname(os.path.abspath(__file__))
os.environ['TTS_HOME'] = os.path.join(project_root, 'models', 'TTS')

print("="*60)
print("XTTS 模型下载工具")
print("="*60)
print(f"\n模型将下载到: {os.environ['TTS_HOME']}")
print("\n开始下载 XTTS v2 模型...")
print("这可能需要几分钟，取决于网络速度。")
print("="*60 + "\n")

try:
    from TTS.api import TTS
    from io import StringIO
    
    # 自动同意协议
    old_stdin = sys.stdin
    sys.stdin = StringIO('y\n')
    
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    print(f"正在下载: {model_name}")
    tts = TTS(model_name)
    
    sys.stdin = old_stdin
    
    print("\n" + "="*60)
    print("✅ 模型下载完成！")
    print("="*60)
    print(f"\n模型位置: {os.environ['TTS_HOME']}")
    print("现在可以运行: python app.py")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
