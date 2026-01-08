"""
视频字幕翻译工具

将英文视频自动识别语音、翻译成中文，并生成字幕文件或嵌入视频。
"""

__version__ = "1.0.0"
__author__ = "Video Translate Team"

from .models import SubtitleSegment
from .config import Config, TranslatorType
from .transcriber import Transcriber
from .translator import create_translator
from .subtitle import SubtitleWriter
from .video import VideoProcessor
from .pipeline import TranslationPipeline

__all__ = [
    "SubtitleSegment",
    "Config",
    "TranslatorType",
    "Transcriber",
    "create_translator",
    "SubtitleWriter",
    "VideoProcessor",
    "TranslationPipeline",
]
