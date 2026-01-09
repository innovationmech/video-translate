"""
字幕处理模块 - 生成和解析字幕文件
"""

from pathlib import Path

from .config import SubtitleConfig
from .models import SubtitleFormat, SubtitleSegment
from .utils import format_timestamp, format_vtt_timestamp, progress


class SubtitleWriter:
    """字幕文件写入器"""

    def __init__(self, config: SubtitleConfig | None = None):
        self.config = config or SubtitleConfig()

    def write(
        self,
        segments: list[SubtitleSegment],
        output_path: str | Path,
        format: SubtitleFormat = SubtitleFormat.SRT,
    ) -> Path:
        """
        写入字幕文件

        Args:
            segments: 字幕片段列表
            output_path: 输出文件路径
            format: 字幕格式

        Returns:
            Path: 输出文件路径
        """
        output_path = Path(output_path)

        if format == SubtitleFormat.SRT:
            self._write_srt(segments, output_path)
        elif format == SubtitleFormat.VTT:
            self._write_vtt(segments, output_path)
        elif format == SubtitleFormat.ASS:
            self._write_ass(segments, output_path)
        else:
            raise ValueError(f"不支持的字幕格式: {format}")

        progress.file(f"字幕文件已保存: {output_path}")
        return output_path

    def _write_srt(self, segments: list[SubtitleSegment], output_path: Path):
        """写入 SRT 格式字幕"""
        with open(output_path, "w", encoding="utf-8") as f:
            for seg in segments:
                f.write(f"{seg.index}\n")
                f.write(f"{format_timestamp(seg.start)} --> {format_timestamp(seg.end)}\n")

                if self.config.target_only:
                    # 只输出目标语言（翻译结果）
                    f.write(f"{seg.translated}\n")
                elif self.config.bilingual:
                    # 双语字幕
                    if self.config.target_first:
                        # 目标语言在上
                        f.write(f"{seg.translated}\n")
                        f.write(f"{seg.text}\n")
                    else:
                        # 源语言在上
                        f.write(f"{seg.text}\n")
                        f.write(f"{seg.translated}\n")
                else:
                    # 只输出源语言
                    f.write(f"{seg.text}\n")

                f.write("\n")

    def _write_vtt(self, segments: list[SubtitleSegment], output_path: Path):
        """写入 VTT 格式字幕"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")

            for seg in segments:
                f.write(f"{seg.index}\n")
                f.write(f"{format_vtt_timestamp(seg.start)} --> {format_vtt_timestamp(seg.end)}\n")

                if self.config.target_only:
                    f.write(f"{seg.translated}\n")
                elif self.config.bilingual:
                    if self.config.target_first:
                        f.write(f"{seg.translated}\n")
                        f.write(f"{seg.text}\n")
                    else:
                        f.write(f"{seg.text}\n")
                        f.write(f"{seg.translated}\n")
                else:
                    f.write(f"{seg.text}\n")

                f.write("\n")

    def _write_ass(self, segments: list[SubtitleSegment], output_path: Path):
        """写入 ASS 格式字幕"""
        # ASS 文件头 - 使用列表拼接避免行过长问题
        style_format = (
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding"
        )
        style_default = (
            "Style: Default,PingFang SC,24,&H00FFFFFF,&H000000FF,"
            "&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1"
        )
        style_target = (
            "Style: Target,PingFang SC,26,&H00FFFFFF,&H000000FF,"
            "&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1"
        )
        style_source = (
            "Style: Source,Arial,20,&H00CCCCCC,&H000000FF,"
            "&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,1,2,10,10,50,1"
        )

        header = f"""[Script Info]
Title: Video Translate Subtitles
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0

[V4+ Styles]
{style_format}
{style_default}
{style_target}
{style_source}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        def format_ass_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:05.2f}"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header)

            for seg in segments:
                start = format_ass_time(seg.start)
                end = format_ass_time(seg.end)

                if self.config.target_only:
                    f.write(f"Dialogue: 0,{start},{end},Target,,0,0,0,,{seg.translated}\n")
                elif self.config.bilingual:
                    # 双语字幕：目标语言和源语言分两行
                    f.write(f"Dialogue: 0,{start},{end},Target,,0,0,0,,{seg.translated}\n")
                    f.write(f"Dialogue: 0,{start},{end},Source,,0,0,0,,{seg.text}\n")
                else:
                    f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{seg.text}\n")


class SubtitleReader:
    """字幕文件读取器"""

    @staticmethod
    def read_srt(file_path: str | Path) -> list[SubtitleSegment]:
        """读取 SRT 格式字幕"""
        file_path = Path(file_path)
        segments = []

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # 按空行分割
        blocks = content.strip().split("\n\n")

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 3:
                continue

            try:
                index = int(lines[0])
                time_line = lines[1]
                text = "\n".join(lines[2:])

                # 解析时间
                start_str, end_str = time_line.split(" --> ")
                start = SubtitleReader._parse_srt_time(start_str)
                end = SubtitleReader._parse_srt_time(end_str)

                segments.append(SubtitleSegment(index=index, start=start, end=end, text=text))
            except (ValueError, IndexError):
                continue

        return segments

    @staticmethod
    def _parse_srt_time(time_str: str) -> float:
        """解析 SRT 时间格式"""
        time_str = time_str.strip().replace(",", ".")
        parts = time_str.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
