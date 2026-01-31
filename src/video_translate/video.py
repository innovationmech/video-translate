"""
视频处理模块 - 字幕嵌入等视频操作
"""

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import TypedDict

from .config import HardwareAccel, VideoConfig
from .utils import progress


class EncoderConfig(TypedDict):
    """硬件编码器配置"""

    h264: str
    hevc: str
    quality_param: str
    quality_scale: Callable[[int], int]


# 硬件编码器配置映射
HARDWARE_ENCODERS: dict[HardwareAccel, EncoderConfig] = {
    HardwareAccel.VIDEOTOOLBOX: {
        "h264": "h264_videotoolbox",
        "hevc": "hevc_videotoolbox",
        "quality_param": "-q:v",  # VideoToolbox 使用 -q:v (1-100, 越高质量越好)
        "quality_scale": lambda crf: max(1, min(100, 100 - crf * 2)),  # CRF 转换
    },
    HardwareAccel.NVENC: {
        "h264": "h264_nvenc",
        "hevc": "hevc_nvenc",
        "quality_param": "-cq",  # NVENC 使用 CQ (Constant Quality)
        "quality_scale": lambda crf: crf,  # 直接使用 CRF 值
    },
    HardwareAccel.QSV: {
        "h264": "h264_qsv",
        "hevc": "hevc_qsv",
        "quality_param": "-global_quality",
        "quality_scale": lambda crf: crf,
    },
    HardwareAccel.AMF: {
        "h264": "h264_amf",
        "hevc": "hevc_amf",
        "quality_param": "-qp_i",  # AMF 使用 QP
        "quality_scale": lambda crf: crf,
    },
}


def get_ffmpeg_path() -> str:
    """获取 FFmpeg 可执行文件路径，支持环境变量覆盖"""
    return os.environ.get("FFMPEG_PATH", "ffmpeg")


def get_ffprobe_path() -> str:
    """获取 FFprobe 可执行文件路径，支持环境变量覆盖"""
    return os.environ.get("FFPROBE_PATH", "ffprobe")


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
            ffmpeg = get_ffmpeg_path()
            result = subprocess.run([ffmpeg, "-version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def check_encoder(encoder: str) -> bool:
        """检查指定编码器是否可用"""
        try:
            ffmpeg = get_ffmpeg_path()
            result = subprocess.run(
                [ffmpeg, "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
            )
            return encoder in result.stdout
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    @staticmethod
    def detect_hardware_accel() -> HardwareAccel:
        """自动检测可用的硬件加速方案"""
        # 按优先级检测
        if sys.platform == "darwin":
            # macOS 优先使用 VideoToolbox
            if VideoProcessor.check_encoder("h264_videotoolbox"):
                progress.info("检测到 VideoToolbox 硬件加速")
                return HardwareAccel.VIDEOTOOLBOX
        else:
            # Linux/Windows 检测顺序: NVENC > QSV > AMF
            if VideoProcessor.check_encoder("h264_nvenc"):
                progress.info("检测到 NVIDIA NVENC 硬件加速")
                return HardwareAccel.NVENC
            if VideoProcessor.check_encoder("h264_qsv"):
                progress.info("检测到 Intel QSV 硬件加速")
                return HardwareAccel.QSV
            if VideoProcessor.check_encoder("h264_amf"):
                progress.info("检测到 AMD AMF 硬件加速")
                return HardwareAccel.AMF

        progress.info("未检测到硬件加速，将使用 CPU 编码")
        return HardwareAccel.NONE

    def get_encoder_settings(self, accel: HardwareAccel) -> dict | None:
        """获取硬件编码器设置"""
        if accel == HardwareAccel.AUTO:
            accel = self.detect_hardware_accel()

        if accel == HardwareAccel.NONE:
            return None

        if accel not in HARDWARE_ENCODERS:
            return None

        encoder_config = HARDWARE_ENCODERS[accel]
        encoder = encoder_config["h264"]

        # 验证编码器是否真正可用
        if not self.check_encoder(encoder):
            progress.warning(f"编码器 {encoder} 不可用，回退到 CPU 编码")
            return None

        return {
            "encoder": encoder,
            "quality_param": encoder_config["quality_param"],
            "quality_value": encoder_config["quality_scale"](self.config.video_quality),
        }

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
            get_ffmpeg_path(),
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

            # 字体样式 - ASS override tags 格式
            font_style = (
                f"FontSize={self.config.font_size},"
                f"FontName={self.config.font_name},"
                "PrimaryColour=&HFFFFFF,"
                "OutlineColour=&H000000,"
                "Outline=2"
            )

            # 获取硬件编码器设置
            encoder_settings = self.get_encoder_settings(self.config.hardware_accel)

            # 创建 filtergraph 脚本文件，避免命令行转义问题
            # FFmpeg 8.0+ 对命令行转义非常严格，使用 filter_script 更可靠
            filter_script = Path(temp_dir) / "filter.txt"

            # 在 filter script 中，路径需要转义特殊字符（冒号、反斜杠、单引号）
            # 注意：文件路径参数不应该用引号包裹，否则会导致解析错误
            srt_path_escaped = (
                str(temp_srt).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
            )

            # 写入 filtergraph 脚本
            # subtitles 的文件路径不需要引号，只有 force_style 的值需要引号
            filter_content = f"subtitles={srt_path_escaped}:force_style='{font_style}'"
            filter_script.write_text(filter_content)

            cmd = [
                get_ffmpeg_path(),
                "-y",
                "-i",
                str(video_path),
                "-filter_script:v",
                str(filter_script),
            ]

            # 添加编码器参数
            if encoder_settings:
                progress.info(f"使用硬件编码器: {encoder_settings['encoder']}")
                cmd.extend(["-c:v", encoder_settings["encoder"]])
                # 添加质量参数
                cmd.extend(
                    [encoder_settings["quality_param"], str(encoder_settings["quality_value"])]
                )
            else:
                # CPU 编码 (libx264)
                progress.info("使用 CPU 编码器: libx264")
                cmd.extend(["-c:v", "libx264", "-crf", str(self.config.video_quality)])

            cmd.extend(["-c:a", "copy", str(output_path)])

            self._run_ffmpeg(cmd)

    def _run_ffmpeg(self, cmd: list[str]):
        """运行 FFmpeg 命令"""
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            progress.error(f"FFmpeg 错误: {e.stderr}")
            raise RuntimeError(f"FFmpeg 处理失败: {e.stderr}") from e

    def get_video_info(self, video_path: str | Path) -> dict[str, object]:
        """获取视频信息"""
        video_path = Path(video_path)

        cmd = [
            get_ffprobe_path(),
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

            info: dict[str, object] = json.loads(result.stdout)
            return info
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {}
