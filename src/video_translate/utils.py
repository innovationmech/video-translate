"""
工具函数模块
"""

import logging
from typing import Optional

# 设置日志
logger = logging.getLogger("video_translate")


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None):
    """配置日志"""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（可选）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.setLevel(level)


def format_timestamp(seconds: float) -> str:
    """将秒数转换为 SRT 时间戳格式 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_vtt_timestamp(seconds: float) -> str:
    """将秒数转换为 VTT 时间戳格式 (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def format_duration(seconds: float) -> str:
    """格式化时长为人类可读格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}小时{minutes}分{secs}秒"
    elif minutes > 0:
        return f"{minutes}分{secs}秒"
    else:
        return f"{secs}秒"


def get_device() -> str:
    """检测并返回可用的计算设备"""
    try:
        import torch
    except ImportError:
        return "cpu"
    
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def get_device_name(device: str) -> str:
    """获取设备的友好名称"""
    device_names = {
        "cuda": "NVIDIA GPU (CUDA)",
        "mps": "Apple Silicon GPU (MPS)",
        "cpu": "CPU"
    }
    return device_names.get(device, device)


class ProgressReporter:
    """进度报告器"""
    
    def __init__(self, use_emoji: bool = True):
        self.use_emoji = use_emoji
    
    def _icon(self, emoji: str, fallback: str = "") -> str:
        return emoji if self.use_emoji else fallback
    
    def info(self, message: str):
        print(f"{self._icon('ℹ️ ')}  {message}")
    
    def success(self, message: str):
        print(f"{self._icon('✅')} {message}")
    
    def error(self, message: str):
        print(f"{self._icon('❌')} {message}")
    
    def warning(self, message: str):
        print(f"{self._icon('⚠️ ')}  {message}")
    
    def step(self, step_num: int, total: int, message: str):
        print(f"{self._icon('📝')} [{step_num}/{total}] {message}")
    
    def loading(self, message: str):
        print(f"{self._icon('🎯')} {message}")
    
    def video(self, message: str):
        print(f"{self._icon('🎬')} {message}")
    
    def audio(self, message: str):
        print(f"{self._icon('🎤')} {message}")
    
    def translate(self, message: str):
        print(f"{self._icon('🌐')} {message}")
    
    def file(self, message: str):
        print(f"{self._icon('📄')} {message}")
    
    def device(self, message: str):
        print(f"{self._icon('💻')} {message}")
    
    def separator(self, char: str = "=", length: int = 60):
        print(char * length)
    
    def header(self, title: str):
        self.separator()
        print(f"{self._icon('🎥')} {title}")
        self.separator()


# 全局进度报告器实例
progress = ProgressReporter()
