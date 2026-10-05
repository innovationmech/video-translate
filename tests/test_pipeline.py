"""字幕模式的流水线集成测试（语音识别和视频编码使用 mock）。"""

import json
from unittest.mock import Mock

import pytest

from video_translate import pipeline, subtitle, utils
from video_translate.config import (
    Config,
    Language,
    SubtitleConfig,
    TranscriberConfig,
    TranslatorConfig,
    VideoConfig,
)
from video_translate.models import SubtitleSegment, TranscriptionResult, TranslationResult
from video_translate.pipeline import TranslationPipeline
from video_translate.utils import ProgressReporter


@pytest.mark.parametrize("json_mode", [False, True])
@pytest.mark.parametrize("embed,soft", [(False, True), (True, True), (True, False)])
def test_original_subtitles_skip_api_and_preserve_text(
    tmp_path, monkeypatch, capsys, json_mode, embed, soft
):
    video = tmp_path / "video.mp4"
    video.touch()
    config = Config(
        source_only=True,
        transcriber=TranscriberConfig(language="ja"),
        translator=TranslatorConfig(
            source_language=Language.JAPANESE, target_language=Language.JAPANESE
        ),
        # 原生模式必须覆盖已保存的“只输出译文”和双语设置。
        subtitle=SubtitleConfig(target_only=True, bilingual=True),
        video=VideoConfig(embed_subtitle=embed, soft_subtitle=soft),
    )
    config.translator.api_key = None
    assert config.validate() == []

    transcription = TranscriptionResult(
        segments=[SubtitleSegment(1, 0, 2.5, "こんにちは。\n元気ですか？")],
        language="ja",
        duration=2.5,
    )
    monkeypatch.setattr(pipeline.Transcriber, "transcribe", Mock(return_value=transcription))
    translator = Mock(side_effect=AssertionError("原生模式不能初始化翻译器"))
    summarizer = Mock(side_effect=AssertionError("原生模式不能初始化总结器"))
    monkeypatch.setattr(pipeline, "create_translator", translator)
    monkeypatch.setattr(pipeline, "create_summarizer", summarizer)
    reporter = ProgressReporter(json_mode=json_mode)
    monkeypatch.setattr(pipeline, "progress", reporter)
    monkeypatch.setattr(subtitle, "progress", reporter)
    processor = Mock()
    processor_factory = Mock(return_value=processor)
    monkeypatch.setattr(pipeline, "VideoProcessor", processor_factory)

    result = TranslationPipeline(config, json_mode=json_mode).process(video)

    assert result["subtitle_file"] == tmp_path / "video_ja_original.srt"
    assert result["subtitle_file"].read_text() == (
        "1\n00:00:00,000 --> 00:00:02,500\nこんにちは。\n元気ですか？\n\n"
    )
    assert result["summary_file"] is None
    assert result["summary"] is None
    assert config.subtitle.target_only is True
    translator.assert_not_called()
    summarizer.assert_not_called()
    if embed:
        assert result["output_video"] == tmp_path / "video_ja_original.mp4"
        processor.embed_subtitle.assert_called_once_with(
            video, result["subtitle_file"], result["output_video"]
        )
        assert processor_factory.call_args.args[0].subtitle_language == "ja"
    else:
        assert result["output_video"] is None
        processor.embed_subtitle.assert_not_called()
    if json_mode:
        events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
        steps = [event for event in events if event["type"] == "progress"]
        assert {event["total_steps"] for event in steps} == {3}
        assert {event["step_name"] for event in steps} == {
            "transcribing",
            "generating",
            "embedding",
        }
        assert steps[-1]["step"] == 3
        assert steps[-1]["percent"] == 100


def test_translation_without_summary_keeps_bilingual_output(tmp_path, monkeypatch, capsys):
    video = tmp_path / "video.mp4"
    video.touch()
    config = Config()
    config.summary.enabled = False
    config.video.embed_subtitle = False
    segments = [SubtitleSegment(1, 0, 2.5, "Hello")]
    monkeypatch.setattr(
        pipeline.Transcriber,
        "transcribe",
        Mock(return_value=TranscriptionResult(segments, "en", 2.5)),
    )
    translated = [SubtitleSegment(1, 0, 2.5, "Hello", "你好")]
    translator = Mock()
    translator.translate_segments.return_value = TranslationResult(translated, "en", "zh", "test")
    monkeypatch.setattr(pipeline, "create_translator", Mock(return_value=translator))
    reporter = ProgressReporter(json_mode=True)
    monkeypatch.setattr(pipeline, "progress", reporter)
    monkeypatch.setattr(subtitle, "progress", reporter)

    result = TranslationPipeline(config, json_mode=True).process(video)

    assert result["subtitle_file"].name == "video_zh.srt"
    assert "你好\nHello" in result["subtitle_file"].read_text()
    translator.translate_segments.assert_called_once()
    events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    steps = [event for event in events if event["type"] == "progress"]
    assert {event["total_steps"] for event in steps} == {4}
    assert steps[-1]["step_name"] == "embedding"


def test_cli_original_subtitles_without_api_key(tmp_path, monkeypatch, capsys):
    from video_translate.cli import main

    for name in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    video = tmp_path / "video.mp4"
    video.touch()
    segments = [SubtitleSegment(1, 0, 1, "中文原文")]
    output = tmp_path / "new" / "subtitles"
    transcribe = Mock(return_value=TranscriptionResult(segments, "zh", 1))
    monkeypatch.setattr(pipeline.Transcriber, "transcribe", transcribe)
    reporter = ProgressReporter()
    for module in (utils, pipeline, subtitle):
        monkeypatch.setattr(module, "progress", reporter)

    main(
        [
            str(video),
            "--source",
            "ZH",
            "--source-only",
            "--target-only",
            "--no-embed",
            "--output",
            str(output),
            "--json-progress",
        ]
    )

    events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert events[-1]["type"] == "result"
    assert events[-1]["status"] == "success"
    assert events[-1]["summary_file"] is None
    assert events[-1]["output_video"] is None
    assert (output / "video_zh_original.srt").read_text().count("中文原文") == 1
