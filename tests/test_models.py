"""
数据模型测试
"""

import pytest
from video_translate.models import (
    SubtitleSegment,
    TranscriptionResult,
    TranslationResult,
    SubtitleFormat,
)


class TestSubtitleFormat:
    """测试字幕格式枚举"""

    def test_srt_format(self):
        """测试 SRT 格式值"""
        assert SubtitleFormat.SRT.value == "srt"

    def test_ass_format(self):
        """测试 ASS 格式值"""
        assert SubtitleFormat.ASS.value == "ass"

    def test_vtt_format(self):
        """测试 VTT 格式值"""
        assert SubtitleFormat.VTT.value == "vtt"


class TestSubtitleSegment:
    """测试字幕片段数据类"""

    def test_create_segment(self, sample_segment):
        """测试创建字幕片段"""
        assert sample_segment.index == 1
        assert sample_segment.start == 0.0
        assert sample_segment.end == 2.5
        assert sample_segment.text == "Hello, world!"
        assert sample_segment.translated == "你好，世界！"

    def test_create_segment_without_translation(self):
        """测试创建不带翻译的字幕片段"""
        segment = SubtitleSegment(index=1, start=0.0, end=2.5, text="Hello")
        assert segment.translated == ""

    def test_duration_property(self, sample_segment):
        """测试持续时间属性"""
        assert sample_segment.duration == 2.5

    def test_duration_calculation(self):
        """测试持续时间计算"""
        segment = SubtitleSegment(index=1, start=10.5, end=15.75, text="Test")
        assert segment.duration == pytest.approx(5.25)

    def test_to_dict(self, sample_segment):
        """测试转换为字典"""
        d = sample_segment.to_dict()
        assert d["index"] == 1
        assert d["start"] == 0.0
        assert d["end"] == 2.5
        assert d["text"] == "Hello, world!"
        assert d["translated"] == "你好，世界！"

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "index": 5,
            "start": 10.0,
            "end": 12.5,
            "text": "Test text",
            "translated": "测试文本"
        }
        segment = SubtitleSegment.from_dict(data)
        assert segment.index == 5
        assert segment.start == 10.0
        assert segment.end == 12.5
        assert segment.text == "Test text"
        assert segment.translated == "测试文本"

    def test_from_dict_without_translation(self):
        """测试从字典创建（无翻译字段）"""
        data = {
            "index": 1,
            "start": 0.0,
            "end": 2.0,
            "text": "Hello"
        }
        segment = SubtitleSegment.from_dict(data)
        assert segment.translated == ""

    def test_roundtrip_conversion(self, sample_segment):
        """测试 to_dict 和 from_dict 的往返转换"""
        d = sample_segment.to_dict()
        restored = SubtitleSegment.from_dict(d)
        assert restored.index == sample_segment.index
        assert restored.start == sample_segment.start
        assert restored.end == sample_segment.end
        assert restored.text == sample_segment.text
        assert restored.translated == sample_segment.translated


class TestTranscriptionResult:
    """测试语音识别结果数据类"""

    def test_create_result(self, sample_transcription_result):
        """测试创建语音识别结果"""
        assert sample_transcription_result.language == "en"
        assert sample_transcription_result.duration == 8.5
        assert len(sample_transcription_result.segments) == 3

    def test_total_segments_property(self, sample_transcription_result):
        """测试总片段数属性"""
        assert sample_transcription_result.total_segments == 3

    def test_empty_segments(self):
        """测试空片段列表"""
        result = TranscriptionResult(segments=[], language="en", duration=0.0)
        assert result.total_segments == 0


class TestTranslationResult:
    """测试翻译结果数据类"""

    def test_create_result(self, sample_translation_result):
        """测试创建翻译结果"""
        assert sample_translation_result.source_language == "en"
        assert sample_translation_result.target_language == "zh"
        assert sample_translation_result.translator == "DeepSeek (deepseek-chat)"
        assert len(sample_translation_result.segments) == 3

    def test_segments_contain_translations(self, sample_translation_result):
        """测试片段包含翻译"""
        for segment in sample_translation_result.segments:
            assert segment.translated != ""
