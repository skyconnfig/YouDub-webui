#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouDub 模型管理工具
管理所有AI模型文件，支持查看、迁移、清理功能
"""

import os
import sys
import shutil
from pathlib import Path
from loguru import logger

class ModelManager:
    def __init__(self):
        # 项目目录（tools的上级目录）
        self.project_root = Path(__file__).parent.parent.absolute()
        # 本地模型目录
        self.local_models_dir = self.project_root / "models"
        # 系统缓存目录
        self.home_dir = Path.home()
        self.torch_hub_default = self.home_dir / ".cache" / "torch" / "hub"
        self.hf_cache_default = self.home_dir / ".cache" / "huggingface"
        self.tts_cache_default = self.home_dir / ".local" / "share" / "tts"
        
    def get_model_info(self):
        """获取所有模型信息"""
        info = {
            "local_models": {},
            "system_cache": {},
            "summary": {
                "total_size_gb": 0,
                "model_count": 0
            }
        }
        
        # 检查本地模型
        print("\n" + "="*60)
        print("[本地模型] 存储位置: {}".format(self.local_models_dir))
        print("="*60)
        
        # Whisper模型
        whisper_dir = self.local_models_dir / "ASR" / "whisper"
        if whisper_dir.exists():
            models = list(whisper_dir.glob("*.pt"))
            info["local_models"]["whisper"] = {
                "path": str(whisper_dir),
                "models": [m.name for m in models],
                "size_gb": sum(m.stat().st_size for m in models) / (1024**3) if models else 0
            }
            print(f"  Whisper模型: {len(models)}个文件")
            for m in models:
                size_mb = m.stat().st_size / (1024**2)
                print(f"    - {m.name}: {size_mb:.1f} MB")
        else:
            print("  Whisper模型: 未找到")
            
        # Demucs模型 (torch hub)
        demucs_dir = self.local_models_dir / "torch_hub"
        if demucs_dir.exists():
            size_gb = self._get_dir_size(demucs_dir) / (1024**3)
            info["local_models"]["demucs"] = {
                "path": str(demucs_dir),
                "size_gb": size_gb
            }
            print(f"  Demucs模型: {size_gb:.2f} GB")
        else:
            print("  Demucs模型: 未找到")
            
        # TTS模型
        tts_dir = self.local_models_dir / "TTS"
        if tts_dir.exists():
            size_gb = self._get_dir_size(tts_dir) / (1024**3)
            info["local_models"]["tts"] = {
                "path": str(tts_dir),
                "size_gb": size_gb
            }
            print(f"  TTS模型: {size_gb:.2f} GB")
        else:
            print("  TTS模型: 未找到")
            
        # 检查系统缓存中的模型
        print("\n" + "="*60)
        print("[系统缓存] 可迁移到本地")
        print("="*60)
        
        if self.torch_hub_default.exists():
            size_gb = self._get_dir_size(self.torch_hub_default) / (1024**3)
            info["system_cache"]["torch_hub"] = {
                "path": str(self.torch_hub_default),
                "size_gb": size_gb
            }
            print(f"  Torch Hub缓存: {size_gb:.2f} GB")
            print(f"    路径: {self.torch_hub_default}")
        
        if self.hf_cache_default.exists():
            size_gb = self._get_dir_size(self.hf_cache_default) / (1024**3)
            info["system_cache"]["huggingface"] = {
                "path": str(self.hf_cache_default),
                "size_gb": size_gb
            }
            print(f"  HuggingFace缓存: {size_gb:.2f} GB")
            print(f"    路径: {self.hf_cache_default}")
            
        if self.tts_cache_default.exists():
            size_gb = self._get_dir_size(self.tts_cache_default) / (1024**3)
            info["system_cache"]["tts"] = {
                "path": str(self.tts_cache_default),
                "size_gb": size_gb
            }
            print(f"  TTS缓存: {size_gb:.2f} GB")
            print(f"    路径: {self.tts_cache_default}")
        
        return info
    
    def _get_dir_size(self, path):
        """获取目录大小"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total += os.path.getsize(fp)
        except:
            pass
        return total
    
    def migrate_models(self):
        """迁移系统缓存到本地目录"""
        print("\n" + "="*60)
        print("[模型迁移] 将系统缓存迁移到项目目录")
        print("="*60)
        
        # 迁移Torch Hub模型
        if self.torch_hub_default.exists():
            target = self.local_models_dir / "torch_hub"
            if not target.exists():
                print(f"\n迁移 Demucs 模型...")
                print(f"  从: {self.torch_hub_default}")
                print(f"  到: {target}")
                try:
                    shutil.copytree(self.torch_hub_default, target)
                    print(f"  完成!")
                except Exception as e:
                    print(f"  错误: {e}")
            else:
                print(f"\nDemucs模型已在本地，跳过迁移")
        
        # 迁移TTS模型
        if self.tts_cache_default.exists():
            target = self.local_models_dir / "TTS"
            if not target.exists():
                print(f"\n迁移 TTS 模型...")
                print(f"  从: {self.tts_cache_default}")
                print(f"  到: {target}")
                try:
                    shutil.copytree(self.tts_cache_default, target)
                    print(f"  完成!")
                except Exception as e:
                    print(f"  错误: {e}")
            else:
                print(f"\nTTS模型已在本地，跳过迁移")
        
        print("\n迁移完成!")
    
    def clean_cache(self):
        """清理系统缓存"""
        print("\n" + "="*60)
        print("[清理缓存] 删除系统缓存中的模型文件")
        print("="*60)
        print("警告: 这将删除系统缓存中的模型文件!")
        print("本地模型不会被删除。")
        confirm = input("\n确认删除? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("已取消")
            return
        
        deleted = []
        
        # 清理Torch Hub
        if self.torch_hub_default.exists():
            try:
                shutil.rmtree(self.torch_hub_default)
                deleted.append(f"Torch Hub: {self.torch_hub_default}")
            except Exception as e:
                print(f"删除失败 {self.torch_hub_default}: {e}")
        
        # 清理HuggingFace
        if self.hf_cache_default.exists():
            try:
                shutil.rmtree(self.hf_cache_default)
                deleted.append(f"HuggingFace: {self.hf_cache_default}")
            except Exception as e:
                print(f"删除失败 {self.hf_cache_default}: {e}")
        
        # 清理TTS
        if self.tts_cache_default.exists():
            try:
                shutil.rmtree(self.tts_cache_default)
                deleted.append(f"TTS: {self.tts_cache_default}")
            except Exception as e:
                print(f"删除失败 {self.tts_cache_default}: {e}")
        
        if deleted:
            print("\n已删除:")
            for d in deleted:
                print(f"  - {d}")
        else:
            print("\n没有可删除的缓存")
    
    def download_whisper_model(self, model_name="medium"):
        """下载Whisper模型"""
        print(f"\n下载 Whisper {model_name} 模型...")
        try:
            import whisper
            model_dir = self.local_models_dir / "ASR" / "whisper"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"模型将保存到: {model_dir}")
            model = whisper.load_model(model_name, download_root=str(model_dir))
            print(f"下载完成!")
            del model
        except Exception as e:
            print(f"下载失败: {e}")
            print("请确保已安装whisper: pip install openai-whisper")
    
    def show_menu(self):
        """显示菜单"""
        while True:
            print("\n" + "="*60)
            print("YouDub 模型管理工具")
            print("="*60)
            print("[1] 查看模型状态")
            print("[2] 迁移系统缓存到本地")
            print("[3] 下载Whisper模型")
            print("[4] 清理系统缓存")
            print("[5] 退出")
            print("="*60)
            
            choice = input("\n选择操作 (1-5): ").strip()
            
            if choice == '1':
                self.get_model_info()
            elif choice == '2':
                self.migrate_models()
            elif choice == '3':
                print("\n可用模型: tiny, base, small, medium, large")
                model = input("输入模型名称 (默认 medium): ").strip() or "medium"
                self.download_whisper_model(model)
            elif choice == '4':
                self.clean_cache()
            elif choice == '5':
                print("再见!")
                break
            else:
                print("无效选择")

def main():
    """主函数"""
    manager = ModelManager()
    
    if len(sys.argv) > 1:
        # 命令行模式
        cmd = sys.argv[1]
        if cmd == "info":
            manager.get_model_info()
        elif cmd == "migrate":
            manager.migrate_models()
        elif cmd == "clean":
            manager.clean_cache()
        elif cmd == "download":
            model = sys.argv[2] if len(sys.argv) > 2 else "medium"
            manager.download_whisper_model(model)
        else:
            print("未知命令")
            print("用法: python manage_models.py [info|migrate|clean|download <model>]")
    else:
        # 交互模式
        manager.show_menu()

if __name__ == "__main__":
    main()
