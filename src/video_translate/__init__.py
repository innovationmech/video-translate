"""
视频字幕翻译工具

将英文视频自动识别语音、翻译成中文，并生成字幕文件或嵌入视频。
"""

__version__ = "1.0.0"
__author__ = "innovationmech"

from .config import Config, Language, TranslatorType, WhisperModel
from .models import SubtitleSegment
from .pipeline import TranslationPipeline
from .subtitle import SubtitleWriter
from .transcriber import Transcriber
from .translator import create_translator
from .video import VideoProcessor

__all__ = [
    "SubtitleSegment",
    "Config",
    "TranslatorType",
    "Language",
    "WhisperModel",
    "Transcriber",
    "create_translator",
    "SubtitleWriter",
    "VideoProcessor",
    "TranslationPipeline",
]
