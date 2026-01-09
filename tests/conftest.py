"""
pytest 配置和共享 fixtures
"""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_translate.config import (
    Config,
    Language,
    SubtitleConfig,
    TranscriberConfig,
    TranslatorConfig,
    TranslatorType,
    VideoConfig,
    WhisperModel,
)
from video_translate.models import SubtitleSegment, TranscriptionResult, TranslationResult


@pytest.fixture
def sample_segment():
    """创建一个示例字幕片段"""
    return SubtitleSegment(
        index=1, start=0.0, end=2.5, text="Hello, world!", translated="你好，世界！"
    )


@pytest.fixture
def sample_segments():
    """创建多个示例字幕片段"""
    return [
        SubtitleSegment(
            index=1, start=0.0, end=2.5, text="Hello, world!", translated="你好，世界！"
        ),
        SubtitleSegment(index=2, start=3.0, end=5.5, text="How are you?", translated="你好吗？"),
        SubtitleSegment(
            index=3, start=6.0, end=8.5, text="I'm fine, thank you.", translated="我很好，谢谢。"
        ),
    ]


@pytest.fixture
def sample_transcription_result(sample_segments):
    """创建示例语音识别结果"""
    return TranscriptionResult(segments=sample_segments, language="en", duration=8.5)


@pytest.fixture
def sample_translation_result(sample_segments):
    """创建示例翻译结果"""
    return TranslationResult(
        segments=sample_segments,
        source_language="en",
        target_language="zh",
        translator="DeepSeek (deepseek-chat)",
    )


@pytest.fixture
def default_translator_config():
    """创建默认翻译器配置"""
    return TranslatorConfig(
        type=TranslatorType.DEEPSEEK,
        api_key="test-api-key",
        source_language=Language.ENGLISH,
        target_language=Language.CHINESE,
    )


@pytest.fixture
def default_transcriber_config():
    """创建默认语音识别配置"""
    return TranscriberConfig(model=WhisperModel.BASE, language="en", device="cpu")


@pytest.fixture
def default_subtitle_config():
    """创建默认字幕配置"""
    return SubtitleConfig(target_only=False, bilingual=True, target_first=True)


@pytest.fixture
def default_video_config():
    """创建默认视频配置"""
    return VideoConfig(
        embed_subtitle=True, soft_subtitle=True, font_name="PingFang SC", font_size=24
    )


@pytest.fixture
def default_config(
    default_transcriber_config,
    default_translator_config,
    default_subtitle_config,
    default_video_config,
):
    """创建默认完整配置"""
    return Config(
        transcriber=default_transcriber_config,
        translator=default_translator_config,
        subtitle=default_subtitle_config,
        video=default_video_config,
    )


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_srt_content():
    """示例 SRT 文件内容"""
    return """1
00:00:00,000 --> 00:00:02,500
Hello, world!

2
00:00:03,000 --> 00:00:05,500
How are you?

3
00:00:06,000 --> 00:00:08,500
I'm fine, thank you.
"""


@pytest.fixture
def sample_srt_file(temp_dir, sample_srt_content):
    """创建示例 SRT 文件"""
    srt_path = temp_dir / "test.srt"
    srt_path.write_text(sample_srt_content, encoding="utf-8")
    return srt_path
