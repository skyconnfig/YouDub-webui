#!/usr/bin/env python3
"""
验证本地模型是否能正确加载
"""
import os
import sys

# 设置项目根目录（tools的上级目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)

print("="*60)
print("YouDub 模型验证工具")
print("="*60)

# 1. 检查模型文件
print("\n[1] 检查本地模型文件...")
models_dir = os.path.join(project_root, 'models')

# Whisper 模型
whisper_dir = os.path.join(models_dir, 'ASR', 'whisper')
if os.path.exists(whisper_dir):
    whisper_models = [f for f in os.listdir(whisper_dir) if f.endswith('.pt')]
    print(f"✅ Whisper模型: {len(whisper_models)}个")
    for m in whisper_models:
        size = os.path.getsize(os.path.join(whisper_dir, m)) / (1024**2)
        print(f"   - {m}: {size:.1f} MB")
else:
    print("❌ Whisper模型目录不存在")

# Demucs 模型
demucs_dir = os.path.join(models_dir, 'Demucs')
if os.path.exists(demucs_dir):
    demucs_models = [f for f in os.listdir(demucs_dir) if f.endswith('.th')]
    print(f"✅ Demucs模型: {len(demucs_models)}个")
    for m in demucs_models:
        size = os.path.getsize(os.path.join(demucs_dir, m)) / (1024**2)
        print(f"   - {m}: {size:.1f} MB")
else:
    print("❌ Demucs模型目录不存在")

# 2. 测试导入
print("\n[2] 测试模块导入...")
try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
    print(f"   CUDA可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
except ImportError as e:
    print(f"❌ PyTorch导入失败: {e}")
    sys.exit(1)

try:
    from demucs.api import Separator
    print("✅ Demucs导入成功")
except ImportError as e:
    print(f"❌ Demucs导入失败: {e}")
    print("   请安装: pip install demucs")

# 3. 测试模型加载（可选，需要较多内存）
print("\n[3] 测试模型加载...")
test_load = input("是否测试加载Demucs模型? (需要约2GB内存) [y/N]: ").lower()

if test_load == 'y':
    try:
        print("   正在加载Demucs模型 (htdemucs_ft)...")
        separator = Separator("htdemucs_ft", device='cuda' if torch.cuda.is_available() else 'cpu', 
                             progress=False, shifts=0)
        print("✅ Demucs模型加载成功!")
        del separator
    except Exception as e:
        print(f"❌ Demucs模型加载失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("   跳过模型加载测试")

print("\n" + "="*60)
print("验证完成!")
print("="*60)
print("\n现在可以运行: python app.py")
input("\n按Enter键退出...")
