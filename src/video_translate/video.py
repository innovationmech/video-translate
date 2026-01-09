"""
视频处理模块 - 字幕嵌入等视频操作
"""

import subprocess
from pathlib import Path

from .config import VideoConfig
from .utils import progress


class VideoProcessor:
    """视频处理器"""

    # 支持的视频格式
    SUPPORTED_FORMATS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".flv"}

    # 字幕编码映射
    SUBTITLE_CODEC_MAP = {
        ".mp4": "mov_text",
        ".m4v": "mov_text",
        ".mov": "mov_text",
        ".mkv": "srt",
        ".webm": "webvtt",
        ".avi": "srt",
    }

    def __init__(self, config: VideoConfig | None = None):
        self.config = config or VideoConfig()

    @staticmethod
    def is_supported(file_path: str | Path) -> bool:
        """检查是否为支持的视频格式"""
        ext = Path(file_path).suffix.lower()
        return ext in VideoProcessor.SUPPORTED_FORMATS

    @staticmethod
    def check_ffmpeg() -> bool:
        """检查 FFmpeg 是否可用"""
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def get_subtitle_codec(self, output_path: str | Path) -> str:
        """根据输出格式获取字幕编码"""
        ext = Path(output_path).suffix.lower()
        return self.SUBTITLE_CODEC_MAP.get(ext, "srt")

    def embed_subtitle(
        self,
        video_path: str | Path,
        subtitle_path: str | Path,
        output_path: str | Path,
        soft_subtitle: bool | None = None,
    ) -> Path:
        """
        将字幕嵌入视频

        Args:
            video_path: 输入视频路径
            subtitle_path: 字幕文件路径
            output_path: 输出视频路径
            soft_subtitle: 是否使用软字幕（None 时使用配置）

        Returns:
            Path: 输出视频路径
        """
        video_path = Path(video_path)
        subtitle_path = Path(subtitle_path)
        output_path = Path(output_path)

        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        if not subtitle_path.exists():
            raise FileNotFoundError(f"字幕文件不存在: {subtitle_path}")

        if not self.check_ffmpeg():
            raise RuntimeError("FFmpeg 未安装或不可用")

        soft_sub = soft_subtitle if soft_subtitle is not None else self.config.soft_subtitle

        progress.video("正在将字幕嵌入视频...")

        if soft_sub:
            self._embed_soft_subtitle(video_path, subtitle_path, output_path)
        else:
            self._embed_hard_subtitle(video_path, subtitle_path, output_path)

        progress.success(f"视频已保存: {output_path}")
        return output_path

    def _embed_soft_subtitle(self, video_path: Path, subtitle_path: Path, output_path: Path):
        """嵌入软字幕（可关闭）"""
        subtitle_codec = self.get_subtitle_codec(output_path)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(subtitle_path),
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            "-c:s",
            subtitle_codec,
            "-metadata:s:s:0",
            "language=chi",
            str(output_path),
        ]

        self._run_ffmpeg(cmd)

    def _embed_hard_subtitle(self, video_path: Path, subtitle_path: Path, output_path: Path):
        """嵌入硬字幕（烧录到视频中）"""
        import shutil
        import tempfile

        # 为避免特殊字符问题，将字幕文件复制到临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_srt = Path(temp_dir) / "subtitle.srt"
            shutil.copy(subtitle_path, temp_srt)

            # 转义临时路径中可能的特殊字符
            srt_escaped = str(temp_srt).replace("\\", "/").replace(":", "\\:")

            # 字体样式 - 注意 FontName 不要有空格问题
            font_name = self.config.font_name.replace(" ", "\\ ")
            font_style = (
                f"FontSize={self.config.font_size},"
                f"FontName={font_name},"
                "PrimaryColour=&HFFFFFF,"
                "OutlineColour=&H000000,"
                "Outline=2"
            )

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-vf",
                f"subtitles={srt_escaped}:force_style='{font_style}'",
                "-c:a",
                "copy",
                str(output_path),
            ]

            self._run_ffmpeg(cmd)

    def _run_ffmpeg(self, cmd: list[str]):
        """运行 FFmpeg 命令"""
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            progress.error(f"FFmpeg 错误: {e.stderr}")
            raise RuntimeError(f"FFmpeg 处理失败: {e.stderr}") from e

    def get_video_info(self, video_path: str | Path) -> dict:
        """获取视频信息"""
        video_path = Path(video_path)

        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json

            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {}
