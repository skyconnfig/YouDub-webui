#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理不需要的模型文件
根据当前配置，只保留需要的模型
"""
import os
import shutil
from pathlib import Path

def get_project_root():
    return Path(__file__).parent.parent.absolute()

def clean_unused_models():
    project_root = get_project_root()
    models_dir = project_root / "models"
    
    print("\n" + "="*60)
    print("清理不需要的模型文件")
    print("="*60)
    
    # 当前使用的模型
    print("\n[当前使用]")
    print("  - Whisper: medium")
    print("  - Demucs: htdemucs")
    print("  - TTS: Bytedance (不需要本地模型)")
    
    deleted = []
    total_freed = 0
    
    # 1. 清理 Whisper small 模型 (如果存在 medium)
    whisper_dir = models_dir / "ASR" / "whisper"
    if whisper_dir.exists():
        small_model = whisper_dir / "small.pt"
        if small_model.exists():
            size = small_model.stat().st_size / (1024**2)
            print(f"\n[删除] Whisper small.pt ({size:.1f} MB)")
            print(f"  原因: 现在使用 medium 模型")
            small_model.unlink()
            deleted.append(f"Whisper small.pt: {size:.1f} MB")
            total_freed += size
    
    # 2. 清理 Demucs htdemucs_ft 模型
    demucs_dir = models_dir / "torch_hub" / "checkpoints"
    if demucs_dir.exists():
        for f in demucs_dir.glob("*htdemucs_ft*"):
            size = f.stat().st_size / (1024**2)
            print(f"\n[删除] {f.name} ({size:.1f} MB)")
            print(f"  原因: 现在使用 htdemucs 模型")
            f.unlink()
            deleted.append(f"Demucs {f.name}: {size:.1f} MB")
            total_freed += size
    
    # 3. 清理 XTTS 模型 (使用 Bytedance 不需要)
    xtts_dir = models_dir / "TTS"
    if xtts_dir.exists():
        # XTTS 模型很大，可以选择是否删除
        xtts_model = xtts_dir / "xtts_v2"
        if xtts_model.exists():
            size = sum(f.stat().st_size for f in xtts_model.rglob("*") if f.is_file()) / (1024**2)
            print(f"\n[注意] XTTS 模型: {xtts_model} ({size:.1f} MB)")
            print(f"  原因: 使用 Bytedance TTS，不需要本地 XTTS 模型")
            print(f"  如果需要释放空间，可以手动删除此目录")
    
    print("\n" + "="*60)
    if deleted:
        print("已清理:")
        for d in deleted:
            print(f"  - {d}")
        print(f"\n共释放: {total_freed:.1f} MB")
    else:
        print("没有需要清理的模型")
    print("="*60)

if __name__ == "__main__":
    clean_unused_models()
