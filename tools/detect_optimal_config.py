import os
import sys
import json
import torch
import psutil
from pathlib import Path
from loguru import logger

class YouDubConfigOptimizer:
    """根据硬件配置自动优化YouDub参数"""
    
    def __init__(self):
        self.config = {}
        self.detect_hardware()
        
    def detect_hardware(self):
        """检测硬件配置"""
        logger.info("=" * 60)
        logger.info("[检测] 正在检测硬件配置...")
        logger.info("=" * 60)
        
        # GPU 检测
        self.gpu_available = torch.cuda.is_available()
        self.gpu_count = torch.cuda.device_count() if self.gpu_available else 0
        self.gpu_name = ""
        self.gpu_memory_gb = 0
        
        if self.gpu_available:
            for i in range(self.gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                self.gpu_name = gpu_name
                self.gpu_memory_gb = gpu_memory
                logger.info(f"✅ GPU {i}: {gpu_name}")
                logger.info(f"   显存: {gpu_memory:.1f} GB")
                logger.info(f"   CUDA: {torch.version.cuda}")
        else:
            logger.warning("❌ 未检测到GPU，将使用CPU模式（速度会很慢）")
        
        # CPU 检测
        self.cpu_count = psutil.cpu_count(logical=True)
        self.cpu_physical = psutil.cpu_count(logical=False)
        logger.info(f"✅ CPU: {self.cpu_physical} 物理核心 / {self.cpu_count} 逻辑核心")
        
        # 内存检测
        self.total_memory_gb = psutil.virtual_memory().total / 1024**3
        logger.info(f"✅ 内存: {self.total_memory_gb:.1f} GB")
        logger.info("=" * 60)
    
    def calculate_optimal_config(self):
        """根据硬件计算最优配置"""
        config = {
            "hardware": {
                "gpu_name": self.gpu_name,
                "gpu_memory_gb": self.gpu_memory_gb,
                "gpu_available": self.gpu_available,
                "cpu_cores": self.cpu_count,
                "memory_gb": self.total_memory_gb
            }
        }
        
        if not self.gpu_available:
            # CPU 模式（很慢）
            config.update({
                "mode": "cpu",
                "resolution": "720p",
                "demucs_model": "htdemucs",
                "demucs_shifts": 0,
                "whisper_model": "small",
                "whisper_batch_size": 8,
                "whisper_diarization": False,
                "max_workers": 1,
                "force_bytedance": True,
                "expected_time_per_video": "20-30分钟",
                "note": "无GPU，速度较慢，建议使用Bytedance TTS加速"
            })
        elif self.gpu_memory_gb < 8:
            # 低显存模式 (< 8GB)
            config.update({
                "mode": "low_vram",
                "resolution": "1080p",
                "demucs_model": "htdemucs",
                "demucs_shifts": 0,
                "whisper_model": "small",
                "whisper_batch_size": 8,
                "whisper_diarization": False,
                "max_workers": 1,
                "force_bytedance": True,
                "expected_time_per_video": "8-12分钟",
                "note": "显存较低，使用轻量级模型确保安全运行"
            })
        elif self.gpu_memory_gb < 12:
            # 中等显存模式 (8-12GB) - 你的RTX 4060在这里
            config.update({
                "mode": "balanced",
                "resolution": "1080p",
                "demucs_model": "htdemucs_ft",
                "demucs_shifts": 1,
                "whisper_model": "medium",
                "whisper_batch_size": 16,
                "whisper_diarization": False,
                "max_workers": 1,
                "force_bytedance": True,
                "expected_time_per_video": "6-10分钟",
                "note": "推荐配置：平衡速度与质量，适合日常制作"
            })
        elif self.gpu_memory_gb < 20:
            # 高显存模式 (12-20GB)
            config.update({
                "mode": "high_performance",
                "resolution": "1080p",
                "demucs_model": "htdemucs_ft",
                "demucs_shifts": 2,
                "whisper_model": "large",
                "whisper_batch_size": 24,
                "whisper_diarization": True,
                "max_workers": 1,
                "force_bytedance": False,
                "expected_time_per_video": "10-15分钟",
                "note": "可以开启说话人分离，使用large模型获得最佳质量"
            })
        else:
            # 顶级配置 (20GB+)
            config.update({
                "mode": "extreme",
                "resolution": "1080p",
                "demucs_model": "htdemucs_ft",
                "demucs_shifts": 2,
                "whisper_model": "large",
                "whisper_batch_size": 32,
                "whisper_diarization": True,
                "max_workers": 2,
                "force_bytedance": False,
                "expected_time_per_video": "8-12分钟（并行处理2个视频）",
                "note": "顶级配置，可同时处理2个视频"
            })
        
        self.config = config
        return config
    
    def print_config(self):
        """打印配置建议"""
        config = self.config
        
        print("\n" + "=" * 60)
        print("🎯 YouDub 最优配置推荐")
        print("=" * 60)
        print(f"\n📊 检测到的硬件:")
        print(f"   GPU: {config['hardware']['gpu_name'] or '无'}")
        print(f"   显存: {config['hardware']['gpu_memory_gb']:.1f} GB")
        print(f"   内存: {config['hardware']['memory_gb']:.1f} GB")
        print(f"   CPU核心: {config['hardware']['cpu_cores']}")
        
        print(f"\n⚙️  推荐模式: {config['mode'].upper()}")
        print(f"📌 配置说明: {config['note']}")
        print(f"⏱️  预估耗时: {config['expected_time_per_video']}/视频")
        
        print(f"\n📝 Gradio界面设置:")
        print(f"   Resolution:          {config['resolution']}")
        print(f"   Demucs Model:        {config['demucs_model']}")
        print(f"   Number of shifts:    {config['demucs_shifts']}")
        print(f"   Whisper Model:       {config['whisper_model']}")
        print(f"   Whisper Batch Size:  {config['whisper_batch_size']}")
        print(f"   Whisper Diarization: {config['whisper_diarization']}")
        print(f"   Max Workers:         {config['max_workers']}")
        print(f"   Force Bytedance:     {config['force_bytedance']}")
        
        print("\n" + "=" * 60)
        print("💡 提示:")
        if config['whisper_diarization']:
            print("   • 说话人分离已开启，如需更快可关闭")
        else:
            print("   • 如需识别多说话人，可手动开启Diarization（会更慢）")
        if config['force_bytedance']:
            print("   • 已推荐Bytedance TTS，确保.env中配置了APPID和ACCESS_TOKEN")
        if config['demucs_shifts'] > 0:
            print("   • 如需更快，可将shifts降到0（质量略降）")
        print("=" * 60 + "\n")
    
    def save_config(self):
        """保存配置到文件"""
        config_path = Path(__file__).parent.parent / "auto_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ 配置已保存到: {config_path}")
        return config_path
    
    def export_for_gradio(self):
        """导出Gradio可用的默认值"""
        config = self.config
        gradio_defaults = {
            "resolution": config['resolution'].replace('p', ''),
            "demucs_model": config['demucs_model'],
            "demucs_shifts": config['demucs_shifts'],
            "whisper_model": config['whisper_model'],
            "whisper_batch_size": config['whisper_batch_size'],
            "whisper_diarization": config['whisper_diarization'],
            "max_workers": config['max_workers'],
            "force_bytedance": config['force_bytedance']
        }
        return gradio_defaults

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("YouDub 智能配置优化工具")
    print("=" * 60 + "\n")
    
    optimizer = YouDubConfigOptimizer()
    optimizer.calculate_optimal_config()
    optimizer.print_config()
    config_path = optimizer.save_config()
    
    # 导出Gradio默认值
    gradio_config = optimizer.export_for_gradio()
    print("📝 Gradio 默认参数（可复制到app.py）:")
    print("-" * 60)
    for key, value in gradio_config.items():
        print(f"{key}: {value}")
    print("-" * 60)
    
    print(f"\n✅ 配置文件保存位置: {config_path}")
    print("💡 你可以在Gradio界面中按上述参数设置，")
    print("   或修改app.py中的默认值使其自动生效。\n")
    
    input("按Enter键退出...")

if __name__ == "__main__":
    main()
