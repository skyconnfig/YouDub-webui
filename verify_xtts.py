#!/usr/bin/env python3
"""验证 XTTS 模型"""
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
os.environ['TTS_HOME'] = os.path.join(project_root, 'models', 'TTS')

print("验证 XTTS 模型...")
print(f"模型目录: {os.environ['TTS_HOME']}")

try:
    from TTS.api import TTS
    from io import StringIO
    
    # 自动同意协议
    old_stdin = sys.stdin
    sys.stdin = StringIO('y\n')
    
    print("\n加载模型...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    
    sys.stdin = old_stdin
    
    print("✅ XTTS 模型加载成功！")
    print(f"模型设备: {tts.device}")
    
except Exception as e:
    print(f"❌ 加载失败: {e}")
    import traceback
    traceback.print_exc()
