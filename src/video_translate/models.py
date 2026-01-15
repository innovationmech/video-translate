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


@dataclass
class TimelineItem:
    """时间线条目"""

    time: str  # 格式: HH:MM:SS
    description: str

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "time": self.time,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TimelineItem":
        """从字典创建"""
        return cls(
            time=data.get("time", "00:00:00"),
            description=data.get("description", ""),
        )


@dataclass
class SummaryResult:
    """视频内容总结结果"""

    title: str  # 视频标题
    overview: str  # 一句话概述
    key_points: list[str]  # 关键要点列表
    topics: list[str]  # 主题标签
    timeline: list[TimelineItem]  # 时间线
    language: str = ""  # 总结语言

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "title": self.title,
            "overview": self.overview,
            "key_points": self.key_points,
            "topics": self.topics,
            "timeline": [item.to_dict() for item in self.timeline],
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SummaryResult":
        """从字典创建"""
        timeline = [TimelineItem.from_dict(item) for item in data.get("timeline", [])]
        return cls(
            title=data.get("title", ""),
            overview=data.get("overview", ""),
            key_points=data.get("key_points", []),
            topics=data.get("topics", []),
            timeline=timeline,
            language=data.get("language", ""),
        )

    def to_json(self, indent: int = 2) -> str:
        """转换为 JSON 字符串"""
        import json

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "SummaryResult":
        """从 JSON 字符串创建"""
        import json

        data = json.loads(json_str)
        return cls.from_dict(data)
