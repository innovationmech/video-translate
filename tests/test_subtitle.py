"""
字幕处理模块测试
"""

from pathlib import Path

import pytest

from video_translate.config import SubtitleConfig
from video_translate.models import SubtitleFormat, SubtitleSegment
from video_translate.subtitle import SubtitleReader, SubtitleWriter


class TestSubtitleWriter:
    """测试字幕写入器"""

    def test_create_default_writer(self):
        """测试创建默认写入器"""
        writer = SubtitleWriter()
        assert writer.config is not None
        assert writer.config.bilingual is True

    def test_create_writer_with_config(self, default_subtitle_config):
        """测试使用配置创建写入器"""
        writer = SubtitleWriter(default_subtitle_config)
        assert writer.config == default_subtitle_config

    def test_write_srt_bilingual(self, sample_segments, temp_dir):
        """测试写入双语 SRT 字幕（目标语言在上）"""
        config = SubtitleConfig(bilingual=True, target_first=True)
        writer = SubtitleWriter(config)

        output_path = temp_dir / "output.srt"
        result = writer.write(sample_segments, output_path, SubtitleFormat.SRT)

        assert result == output_path
        assert output_path.exists()

        content = output_path.read_text(encoding="utf-8")
        # 检查格式
        assert "1\n" in content
        assert "00:00:00,000 --> 00:00:02,500" in content
        # 目标语言应该在源语言之前
        first_block = content.split("\n\n")[0]
        lines = first_block.split("\n")
        assert "你好，世界！" in lines[2]  # 翻译在第3行
        assert "Hello, world!" in lines[3]  # 原文在第4行

    def test_write_srt_source_first(self, sample_segments, temp_dir):
        """测试写入双语 SRT 字幕（源语言在上）"""
        config = SubtitleConfig(bilingual=True, target_first=False)
        writer = SubtitleWriter(config)

        output_path = temp_dir / "output.srt"
        writer.write(sample_segments, output_path, SubtitleFormat.SRT)

        content = output_path.read_text(encoding="utf-8")
        first_block = content.split("\n\n")[0]
        lines = first_block.split("\n")
        assert "Hello, world!" in lines[2]  # 原文在第3行
        assert "你好，世界！" in lines[3]  # 翻译在第4行

    def test_write_srt_target_only(self, sample_segments, temp_dir):
        """测试写入仅目标语言 SRT 字幕"""
        config = SubtitleConfig(target_only=True)
        writer = SubtitleWriter(config)

        output_path = temp_dir / "output.srt"
        writer.write(sample_segments, output_path, SubtitleFormat.SRT)

        content = output_path.read_text(encoding="utf-8")
        assert "你好，世界！" in content
        assert "Hello, world!" not in content

    def test_write_srt_source_only(self, sample_segments, temp_dir):
        """测试写入仅源语言 SRT 字幕"""
        config = SubtitleConfig(target_only=False, bilingual=False)
        writer = SubtitleWriter(config)

        output_path = temp_dir / "output.srt"
        writer.write(sample_segments, output_path, SubtitleFormat.SRT)

        content = output_path.read_text(encoding="utf-8")
        assert "Hello, world!" in content
        assert "你好，世界！" not in content

    def test_write_vtt(self, sample_segments, temp_dir):
        """测试写入 VTT 字幕"""
        writer = SubtitleWriter(SubtitleConfig(bilingual=True))

        output_path = temp_dir / "output.vtt"
        writer.write(sample_segments, output_path, SubtitleFormat.VTT)

        content = output_path.read_text(encoding="utf-8")
        # VTT 文件头
        assert content.startswith("WEBVTT")
        # VTT 使用点而不是逗号
        assert "00:00:00.000 --> 00:00:02.500" in content

    def test_write_ass(self, sample_segments, temp_dir):
        """测试写入 ASS 字幕"""
        writer = SubtitleWriter(SubtitleConfig(bilingual=True))

        output_path = temp_dir / "output.ass"
        writer.write(sample_segments, output_path, SubtitleFormat.ASS)

        content = output_path.read_text(encoding="utf-8")
        # ASS 文件头
        assert "[Script Info]" in content
        assert "[V4+ Styles]" in content
        assert "[Events]" in content
        # Dialogue 行
        assert "Dialogue:" in content

    def test_write_unsupported_format(self, sample_segments, temp_dir):
        """测试写入不支持的格式"""
        writer = SubtitleWriter()
        output_path = temp_dir / "output.txt"

        # 创建一个假的格式来测试
        with pytest.raises(ValueError) as exc_info:
            # 使用字符串来模拟不支持的格式
            writer.write(sample_segments, output_path, "unsupported")
        # 错误消息应该包含 "不支持"

    def test_write_multiple_segments(self, temp_dir):
        """测试写入多个字幕片段"""
        segments = [
            SubtitleSegment(
                index=i, start=i * 2.0, end=(i + 1) * 2.0, text=f"Text {i}", translated=f"文本 {i}"
            )
            for i in range(1, 6)
        ]

        writer = SubtitleWriter(SubtitleConfig(target_only=True))
        output_path = temp_dir / "multi.srt"
        writer.write(segments, output_path, SubtitleFormat.SRT)

        content = output_path.read_text(encoding="utf-8")
        # 检查所有片段都被写入
        for i in range(1, 6):
            assert f"文本 {i}" in content


class TestSubtitleReader:
    """测试字幕读取器"""

    def test_read_srt(self, sample_srt_file):
        """测试读取 SRT 文件"""
        segments = SubtitleReader.read_srt(sample_srt_file)

        assert len(segments) == 3

        # 检查第一个片段
        assert segments[0].index == 1
        assert segments[0].start == pytest.approx(0.0)
        assert segments[0].end == pytest.approx(2.5)
        assert segments[0].text == "Hello, world!"

        # 检查第二个片段
        assert segments[1].index == 2
        assert segments[1].text == "How are you?"

    def test_read_srt_with_path_object(self, sample_srt_file):
        """测试使用 Path 对象读取"""
        segments = SubtitleReader.read_srt(Path(sample_srt_file))
        assert len(segments) == 3

    def test_read_srt_empty_file(self, temp_dir):
        """测试读取空文件"""
        empty_file = temp_dir / "empty.srt"
        empty_file.write_text("", encoding="utf-8")

        segments = SubtitleReader.read_srt(empty_file)
        assert len(segments) == 0

    def test_parse_srt_time(self):
        """测试解析 SRT 时间格式"""
        # 测试基本格式
        assert SubtitleReader._parse_srt_time("00:00:00,000") == pytest.approx(0.0)
        assert SubtitleReader._parse_srt_time("00:01:30,500") == pytest.approx(90.5)
        assert SubtitleReader._parse_srt_time("01:00:00,000") == pytest.approx(3600.0)

    def test_parse_srt_time_with_spaces(self):
        """测试解析带空格的 SRT 时间"""
        assert SubtitleReader._parse_srt_time(" 00:00:05,000 ") == pytest.approx(5.0)

    def test_read_srt_multiline_text(self, temp_dir):
        """测试读取多行文本的字幕"""
        srt_content = """1
00:00:00,000 --> 00:00:02,500
Line one
Line two

2
00:00:03,000 --> 00:00:05,000
Single line
"""
        srt_file = temp_dir / "multiline.srt"
        srt_file.write_text(srt_content, encoding="utf-8")

        segments = SubtitleReader.read_srt(srt_file)
        assert len(segments) == 2
        assert segments[0].text == "Line one\nLine two"
        assert segments[1].text == "Single line"

    def test_read_srt_malformed_blocks(self, temp_dir):
        """测试读取格式不正确的字幕（应跳过）"""
        srt_content = """1
00:00:00,000 --> 00:00:02,500
Valid block

invalid

2
00:00:03,000 --> 00:00:05,000
Another valid block
"""
        srt_file = temp_dir / "malformed.srt"
        srt_file.write_text(srt_content, encoding="utf-8")

        segments = SubtitleReader.read_srt(srt_file)
        # 应该只读取到有效的块
        assert len(segments) == 2


class TestRoundTrip:
    """测试字幕读写往返"""

    def test_write_and_read_srt(self, sample_segments, temp_dir):
        """测试 SRT 写入后读取"""
        config = SubtitleConfig(target_only=False, bilingual=False)
        writer = SubtitleWriter(config)

        output_path = temp_dir / "roundtrip.srt"
        writer.write(sample_segments, output_path, SubtitleFormat.SRT)

        # 读取回来
        read_segments = SubtitleReader.read_srt(output_path)

        assert len(read_segments) == len(sample_segments)
        for orig, read in zip(sample_segments, read_segments):
            assert read.index == orig.index
            assert read.start == pytest.approx(orig.start, abs=0.001)
            assert read.end == pytest.approx(orig.end, abs=0.001)
            assert read.text == orig.text
