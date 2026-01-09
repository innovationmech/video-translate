"""
数据模型定义
"""

from dataclasses import dataclass
from enum import Enum


class SubtitleFormat(Enum):
    """字幕格式"""

    SRT = "srt"
    ASS = "ass"
    VTT = "vtt"


@dataclass
class SubtitleSegment:
    """字幕片段"""

    index: int
    start: float
    end: float
    text: str
    translated: str = ""

    @property
    def duration(self) -> float:
        """字幕持续时间（秒）"""
        return self.end - self.start

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "index": self.index,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "translated": self.translated,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SubtitleSegment":
        """从字典创建"""
        return cls(
            index=data["index"],
            start=data["start"],
            end=data["end"],
            text=data["text"],
            translated=data.get("translated", ""),
        )


@dataclass
class TranscriptionResult:
    """语音识别结果"""

    segments: list[SubtitleSegment]
    language: str
    duration: float

    @property
    def total_segments(self) -> int:
        return len(self.segments)


@dataclass
class TranslationResult:
    """翻译结果"""

    segments: list[SubtitleSegment]
    source_language: str
    target_language: str
    translator: str
