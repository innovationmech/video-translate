"""
视频处理模块测试
"""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from video_translate.config import Config, TranslatorConfig, VideoConfig
from video_translate.pipeline import TranslationPipeline
from video_translate.video import VideoProcessor


class TestVideoProcessorStatic:
    """测试 VideoProcessor 静态方法"""

    def test_supported_formats(self):
        """测试支持的视频格式列表"""
        formats = VideoProcessor.SUPPORTED_FORMATS
        assert ".mp4" in formats
        assert ".mkv" in formats
        assert ".avi" in formats
        assert ".mov" in formats
        assert ".webm" in formats

    def test_is_supported_mp4(self):
        """测试 MP4 格式支持"""
        assert VideoProcessor.is_supported("video.mp4") is True
        assert VideoProcessor.is_supported("VIDEO.MP4") is True  # 大小写

    def test_is_supported_mkv(self):
        """测试 MKV 格式支持"""
        assert VideoProcessor.is_supported("video.mkv") is True

    def test_is_supported_path_object(self):
        """测试 Path 对象"""
        assert VideoProcessor.is_supported(Path("video.mp4")) is True

    def test_is_not_supported_txt(self):
        """测试不支持的格式"""
        assert VideoProcessor.is_supported("file.txt") is False

    def test_is_not_supported_mp3(self):
        """测试音频格式不支持"""
        assert VideoProcessor.is_supported("audio.mp3") is False


class TestVideoProcessorInit:
    """测试 VideoProcessor 初始化"""

    def test_default_config(self):
        """测试默认配置"""
        processor = VideoProcessor()
        assert processor.config is not None
        assert processor.config.embed_subtitle is True

    def test_custom_config(self, default_video_config):
        """测试自定义配置"""
        processor = VideoProcessor(default_video_config)
        assert processor.config == default_video_config

    def test_default_font(self):
        """测试默认字体使用跨平台中文字体。"""
        processor = VideoProcessor()
        assert processor.config.font_name == "Noto Sans CJK SC"


class TestSubtitleCodecMap:
    """测试字幕编码映射"""

    def test_mp4_codec(self):
        """测试 MP4 字幕编码"""
        processor = VideoProcessor()
        assert processor.get_subtitle_codec("video.mp4") == "mov_text"

    def test_mkv_codec(self):
        """测试 MKV 字幕编码"""
        processor = VideoProcessor()
        assert processor.get_subtitle_codec("video.mkv") == "srt"

    def test_webm_codec(self):
        """测试 WebM 字幕编码"""
        processor = VideoProcessor()
        assert processor.get_subtitle_codec("video.webm") == "webvtt"

    def test_unknown_format_fallback(self):
        """测试未知格式回退"""
        processor = VideoProcessor()
        assert processor.get_subtitle_codec("video.unknown") == "srt"


class TestPipelineOutputPath:
    """测试输出视频路径选择。"""

    def test_hard_sub_webm_uses_mp4_output(self):
        """测试 WebM 硬字幕输出自动切换为 MP4。"""
        config = Config(
            translator=TranslatorConfig(api_key="test-api-key"),
            video=VideoConfig(embed_subtitle=True, soft_subtitle=False),
        )
        pipeline = TranslationPipeline(config)

        output_path = pipeline._get_output_video_path(
            Path("sample.webm"),
            Path("/tmp"),
            "_zh",
        )

        assert output_path == Path("/tmp/sample_zh.mp4")

    def test_soft_sub_preserves_original_container(self):
        """测试软字幕仍保留原始容器。"""
        config = Config(
            translator=TranslatorConfig(api_key="test-api-key"),
            video=VideoConfig(embed_subtitle=True, soft_subtitle=True),
        )
        pipeline = TranslationPipeline(config)

        output_path = pipeline._get_output_video_path(
            Path("sample.webm"),
            Path("/tmp"),
            "_zh",
        )

        assert output_path == Path("/tmp/sample_zh.webm")


class TestCheckFFmpeg:
    """测试 FFmpeg 检查"""

    @patch("subprocess.run")
    def test_ffmpeg_available(self, mock_run):
        """测试 FFmpeg 可用"""
        mock_run.return_value = Mock(returncode=0)
        assert VideoProcessor.check_ffmpeg() is True

    @patch("subprocess.run")
    def test_ffmpeg_not_available(self, mock_run):
        """测试 FFmpeg 不可用（返回非零）"""
        mock_run.return_value = Mock(returncode=1)
        assert VideoProcessor.check_ffmpeg() is False

    @patch("subprocess.run")
    def test_ffmpeg_not_installed(self, mock_run):
        """测试 FFmpeg 未安装"""
        mock_run.side_effect = FileNotFoundError()
        assert VideoProcessor.check_ffmpeg() is False


class TestEmbedSubtitle:
    """测试字幕嵌入"""

    @patch.object(VideoProcessor, "check_ffmpeg", return_value=True)
    @patch.object(VideoProcessor, "_run_ffmpeg")
    def test_embed_soft_subtitle(self, mock_run_ffmpeg, mock_check, temp_dir):
        """测试嵌入软字幕"""
        # 创建测试文件
        video_file = temp_dir / "test.mp4"
        video_file.touch()
        subtitle_file = temp_dir / "test.srt"
        subtitle_file.write_text("1\n00:00:00,000 --> 00:00:02,000\nTest", encoding="utf-8")
        output_file = temp_dir / "output.mp4"

        config = VideoConfig(soft_subtitle=True)
        processor = VideoProcessor(config)

        result = processor.embed_subtitle(video_file, subtitle_file, output_file)

        assert result == output_file
        mock_run_ffmpeg.assert_called_once()

        # 检查调用参数
        call_args = mock_run_ffmpeg.call_args[0][0]
        assert "ffmpeg" in call_args
        assert "-c:s" in call_args  # 软字幕使用字幕编码

    @patch.object(VideoProcessor, "check_ffmpeg", return_value=True)
    @patch.object(VideoProcessor, "_run_ffmpeg")
    @patch.object(VideoProcessor, "_resolve_subtitle_font", return_value="Noto Sans CJK SC")
    def test_embed_hard_subtitle(self, mock_resolve_font, mock_run_ffmpeg, mock_check, temp_dir):
        """测试嵌入硬字幕"""
        video_file = temp_dir / "test.mp4"
        video_file.touch()
        subtitle_file = temp_dir / "test.srt"
        subtitle_file.write_text("1\n00:00:00,000 --> 00:00:02,000\nTest", encoding="utf-8")
        output_file = temp_dir / "output.mp4"

        config = VideoConfig(soft_subtitle=False)
        processor = VideoProcessor(config)

        processor.embed_subtitle(video_file, subtitle_file, output_file)

        mock_run_ffmpeg.assert_called_once()
        call_args = mock_run_ffmpeg.call_args[0][0]
        assert "-filter_script:v" in call_args  # 硬字幕使用 filter_script
        mock_resolve_font.assert_called_once()

    def test_embed_video_not_found(self, temp_dir):
        """测试视频文件不存在"""
        processor = VideoProcessor()
        subtitle_file = temp_dir / "test.srt"
        subtitle_file.touch()

        with pytest.raises(FileNotFoundError) as exc_info:
            processor.embed_subtitle(
                temp_dir / "nonexistent.mp4", subtitle_file, temp_dir / "output.mp4"
            )
        assert "视频文件" in str(exc_info.value)

    def test_embed_subtitle_not_found(self, temp_dir):
        """测试字幕文件不存在"""
        processor = VideoProcessor()
        video_file = temp_dir / "test.mp4"
        video_file.touch()

        with pytest.raises(FileNotFoundError) as exc_info:
            processor.embed_subtitle(
                video_file, temp_dir / "nonexistent.srt", temp_dir / "output.mp4"
            )
        assert "字幕文件" in str(exc_info.value)

    @patch.object(VideoProcessor, "check_ffmpeg", return_value=False)
    def test_embed_ffmpeg_not_available(self, mock_check, temp_dir):
        """测试 FFmpeg 不可用"""
        processor = VideoProcessor()
        video_file = temp_dir / "test.mp4"
        video_file.touch()
        subtitle_file = temp_dir / "test.srt"
        subtitle_file.touch()

        with pytest.raises(RuntimeError) as exc_info:
            processor.embed_subtitle(video_file, subtitle_file, temp_dir / "output.mp4")
        assert "FFmpeg" in str(exc_info.value)

    @patch.object(VideoProcessor, "check_ffmpeg", return_value=True)
    @patch.object(VideoProcessor, "_run_ffmpeg")
    def test_embed_override_soft_subtitle(self, mock_run_ffmpeg, mock_check, temp_dir):
        """测试覆盖软字幕设置"""
        video_file = temp_dir / "test.mp4"
        video_file.touch()
        subtitle_file = temp_dir / "test.srt"
        subtitle_file.write_text("1\n00:00:00,000 --> 00:00:02,000\nTest", encoding="utf-8")
        output_file = temp_dir / "output.mp4"

        # 配置是软字幕，但调用时指定硬字幕
        config = VideoConfig(soft_subtitle=True)
        processor = VideoProcessor(config)

        processor.embed_subtitle(
            video_file, subtitle_file, output_file, soft_subtitle=False  # 覆盖配置
        )

        call_args = mock_run_ffmpeg.call_args[0][0]
        assert "-filter_script:v" in call_args  # 应该使用硬字幕 (filter_script)

    @patch("subprocess.run")
    def test_resolve_subtitle_font_uses_available_default(self, mock_run):
        """测试可用时优先使用默认字体。"""
        mock_run.return_value = Mock(returncode=0, stdout='NotoSansCJK-Regular.ttc: "Noto Sans CJK SC"')

        processor = VideoProcessor(VideoConfig(font_name="Noto Sans CJK SC"))

        assert processor._resolve_subtitle_font() == "Noto Sans CJK SC"

    @patch("subprocess.run")
    def test_resolve_subtitle_font_falls_back_when_default_missing(self, mock_run):
        """测试默认字体不存在时回退到可用中文字体。"""

        def run_side_effect(cmd, capture_output, text, check=False):
            font_name = cmd[1]
            if font_name == "Noto Sans CJK SC":
                return Mock(returncode=0, stdout='DejaVuSans.ttf: "DejaVu Sans" "Book"')
            if font_name == "Source Han Sans SC":
                return Mock(returncode=0, stdout='SourceHanSansSC-Regular.otf: "Source Han Sans SC"')
            return Mock(returncode=0, stdout='DejaVuSans.ttf: "DejaVu Sans" "Book"')

        mock_run.side_effect = run_side_effect
        processor = VideoProcessor(VideoConfig(font_name="Noto Sans CJK SC"))

        assert processor._resolve_subtitle_font() == "Source Han Sans SC"


class TestRunFFmpeg:
    """测试 FFmpeg 命令执行"""

    @patch("subprocess.run")
    def test_run_ffmpeg_success(self, mock_run):
        """测试成功执行"""
        mock_run.return_value = Mock(returncode=0)

        processor = VideoProcessor()
        # 应该不抛出异常
        processor._run_ffmpeg(["ffmpeg", "-version"])

    @patch("subprocess.run")
    def test_run_ffmpeg_failure(self, mock_run):
        """测试执行失败"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg", stderr="Error message")

        processor = VideoProcessor()
        with pytest.raises(RuntimeError) as exc_info:
            processor._run_ffmpeg(["ffmpeg", "-invalid"])
        assert "FFmpeg" in str(exc_info.value)


class TestGetVideoInfo:
    """测试获取视频信息"""

    @patch("subprocess.run")
    def test_get_video_info_success(self, mock_run):
        """测试成功获取视频信息"""
        mock_result = Mock()
        mock_result.stdout = '{"format": {"duration": "120.5"}}'
        mock_run.return_value = mock_result

        processor = VideoProcessor()
        info = processor.get_video_info("test.mp4")

        assert "format" in info
        assert info["format"]["duration"] == "120.5"

    @patch("subprocess.run")
    def test_get_video_info_failure(self, mock_run):
        """测试获取视频信息失败"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffprobe")

        processor = VideoProcessor()
        info = processor.get_video_info("test.mp4")

        assert info == {}

    @patch("subprocess.run")
    def test_get_video_info_ffprobe_not_found(self, mock_run):
        """测试 ffprobe 未安装"""
        mock_run.side_effect = FileNotFoundError()

        processor = VideoProcessor()
        info = processor.get_video_info("test.mp4")

        assert info == {}


class TestVideoConfig:
    """测试视频配置对 VideoProcessor 的影响"""

    def test_font_settings(self):
        """测试字体设置"""
        config = VideoConfig(font_name="Arial", font_size=32)
        processor = VideoProcessor(config)

        assert processor.config.font_name == "Arial"
        assert processor.config.font_size == 32

    def test_embed_subtitle_setting(self):
        """测试嵌入字幕设置"""
        config = VideoConfig(embed_subtitle=False)
        processor = VideoProcessor(config)

        assert processor.config.embed_subtitle is False
