# 🎬 Video Subtitle Translation Tool

Automatically transcribe video audio, translate to target language, and generate subtitle files or embed them into videos. **Supports translation between 18 languages**.

[中文文档](README.zh.md) | [日本語ドキュメント](README.ja.md) | [한국어 문서](README.ko.md) | [Français](README.fr.md) | [Deutsch](README.de.md)

## ✨ Features

- 🎤 **Speech Recognition**: High-precision speech recognition using OpenAI Whisper
- 🌐 **Multi-language Translation**: Supports translation between 18 languages (Chinese, English, Japanese, Korean, French, German, Spanish, etc.)
- 🤖 **Multiple Engine Support**: Supports DeepSeek, OpenAI, and other translation engines
- 📄 **Subtitle Generation**: Supports multiple subtitle formats including SRT, VTT, ASS
- 🎥 **Subtitle Embedding**: Supports both soft and hard subtitle methods
- 🌍 **Bilingual Subtitles**: Optional bilingual subtitle generation
- 📝 **Video Summary**: LLM-powered video content summarization with key points, topics, and timeline
- ⚡ **Hardware Acceleration**: Auto-detect hardware encoding (VideoToolbox/NVENC/QSV/AMF) for faster hard subtitle rendering
- 🖥️ **GUI Integration**: JSON progress output for seamless integration with graphical interfaces
- 💰 **Cost-Effective**: DeepSeek API offers affordable pricing with excellent translation quality
- 🏗️ **Modular Design**: Easy to extend and maintain

## 🌍 Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| `zh` | Chinese (中文) | `en` | English |
| `ja` | Japanese (日本語) | `ko` | Korean (한국어) |
| `fr` | French (Français) | `de` | German (Deutsch) |
| `es` | Spanish (Español) | `ru` | Russian (Русский) |
| `pt` | Portuguese (Português) | `it` | Italian (Italiano) |
| `nl` | Dutch (Nederlands) | `pl` | Polish (Polski) |
| `tr` | Turkish (Türkçe) | `ar` | Arabic (العربية) |
| `hi` | Hindi (हिन्दी) | `th` | Thai (ไทย) |
| `vi` | Vietnamese (Tiếng Việt) | `id` | Indonesian (Bahasa Indonesia) |

Use `video-translate --list-languages` to view the complete list.

## 📁 Project Structure

```
video-translate/
├── src/
│   └── video_translate/
│       ├── __init__.py      # Package initialization
│       ├── __main__.py      # Entry point
│       ├── cli.py           # Command-line interface
│       ├── config.py        # Configuration management
│       ├── models.py        # Data models
│       ├── transcriber.py   # Speech recognition module
│       ├── translator.py    # Translation module
│       ├── summarizer.py    # Video content summarization module
│       ├── subtitle.py      # Subtitle processing module
│       ├── video.py         # Video processing module
│       ├── pipeline.py      # Processing pipeline
│       └── utils.py         # Utility functions
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
├── LICENSE                  # MIT License
├── .gitignore               # Git ignore file
└── README.md
```

## 📦 Installation

### Prerequisites

FFmpeg is required for video processing. Please install it first:

**macOS:**
```bash
# Basic installation (sufficient for soft subtitles)
brew install ffmpeg

# For hard subtitles (--hard-sub), you need FFmpeg with libass support:
brew install ffmpeg-full
echo 'export PATH="/opt/homebrew/opt/ffmpeg-full/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

> **Note**: The standard `brew install ffmpeg` does not include libass support, which is required for the `--hard-sub` feature. If you encounter errors like "No option name near force_style", please install `ffmpeg-full` instead.

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```
> The apt package typically includes libass support. If you encounter "No option name near force_style" errors with `--hard-sub`, install libass: `sudo apt install libass-dev` and reinstall ffmpeg.

**Windows:**
Download and install [FFmpeg](https://ffmpeg.org/download.html) (recommended: [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) full build or [BtbN](https://github.com/BtbN/FFmpeg-Builds/releases) builds, which include libass support)

### Quick Installation (Recommended)

```bash
pip install video-translate
```

Or use [uv](https://github.com/astral-sh/uv) (faster):

```bash
uv pip install video-translate
```

### Development Installation

If you want to contribute to development or modify the code:

```bash
# 1. Clone the project
git clone https://github.com/innovationmech/video-translate.git
cd video-translate

# 2. Install uv (if not already installed)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. Install dependencies (including dev tools)
uv sync --dev

# Or install with pip in editable mode
pip install -e ".[dev]"
```

### Set up API Key

Register and get an API Key from [DeepSeek Open Platform](https://platform.deepseek.com/):

```bash
export DEEPSEEK_API_KEY='your-api-key-here'
```

Or use OpenAI:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 🚀 Usage

### Command Line Usage

```bash
# Basic usage (English → Chinese)
video-translate video.mp4

# Or use python -m
python -m video_translate video.mp4
```

### Multi-language Translation Examples

```bash
# English → Chinese (default)
video-translate video.mp4

# Japanese → Chinese
video-translate video.mp4 --source ja --target zh

# English → Japanese
video-translate video.mp4 --source en --target ja

# Chinese → English
video-translate video.mp4 --source zh --target en

# Korean → Japanese
video-translate video.mp4 --source ko --target ja

# French → German
video-translate video.mp4 --source fr --target de
```

### Command Line Options

**Basic Options:**

| Option | Description |
|--------|-------------|
| `-s, --source` | Source language code (default: en) |
| `-t, --target` | Target language code (default: zh) |
| `--list-languages` | List all supported languages |
| `-o, --output` | Specify output directory |
| `-m, --model` | Whisper model size (tiny/base/small/medium/large) |
| `-v, --version` | Show version |
| `--verbose` | Show detailed logs |

**Translation Options:**

| Option | Description |
|--------|-------------|
| `--translator` | Translation engine (deepseek/openai) |
| `--api-key` | Translation API Key |
| `--api-base` | API Base URL (optional, for custom endpoints) |
| `--llm-model` | LLM model name (optional, override default model) |

**Subtitle Options:**

| Option | Description |
|--------|-------------|
| `--target-only` | Output only target language subtitles, without source text |
| `--source-first` | Source language on top, target language below |

**Video Options:**

| Option | Description |
|--------|-------------|
| `--no-embed` | Don't embed subtitles into video, only generate subtitle files |
| `--hard-sub` | Use hard subtitles (burned into video) |
| `--font-size` | Hard subtitle font size (default: 24) |
| `--hw-accel` | Hardware acceleration for hard subtitle encoding (auto/none/videotoolbox/nvenc/qsv/amf, default: auto) |
| `--video-quality` | Hard subtitle video quality, CRF value (0-51, lower is better, default: 23) |

**Summary Options:**

| Option | Description |
|--------|-------------|
| `--no-summary` | Disable video content summary |
| `--summary-lang` | Summary language code (default: follows target language) |
| `--max-key-points` | Max number of key points in summary (default: 5) |
| `--no-timeline` | Exclude timeline from summary |

**Advanced Options:**

| Option | Description |
|--------|-------------|
| `--json-progress` | Output JSON-formatted progress (for GUI integration) |

### More Examples

```bash
# Use a larger model for better accuracy
video-translate video.mp4 --model large

# Only generate subtitle files, don't embed into video
video-translate video.mp4 --no-embed

# Generate hard subtitles (burned into video)
video-translate video.mp4 --hard-sub

# Hard subtitles with NVIDIA hardware acceleration and high quality
video-translate video.mp4 --hard-sub --hw-accel nvenc --video-quality 18

# Output only target language subtitles
video-translate video.mp4 --target-only

# Use OpenAI translation
video-translate video.mp4 --translator openai

# Use a custom API endpoint and model
video-translate video.mp4 --api-base https://your-api.com/v1 --llm-model your-model

# Disable video content summary
video-translate video.mp4 --no-summary

# Generate summary in English with up to 10 key points
video-translate video.mp4 --summary-lang en --max-key-points 10

# Specify output directory
video-translate video.mp4 -o ./output

# JSON progress output for GUI integration
video-translate video.mp4 --json-progress
```

### Use as a Library

```python
from video_translate import (
    Config,
    TranscriberConfig,
    TranslatorConfig,
    TranslationPipeline,
    WhisperModel,
    TranslatorType,
    Language,
)
from video_translate.config import SummaryConfig, VideoConfig, HardwareAccel

# Create configuration - Japanese to Chinese translation
config = Config(
    transcriber=TranscriberConfig(
        model=WhisperModel.BASE,
        language="ja"  # Source language
    ),
    translator=TranslatorConfig(
        type=TranslatorType.DEEPSEEK,
        api_key="your-api-key",
        source_language=Language.JAPANESE,
        target_language=Language.CHINESE,
    ),
    video=VideoConfig(
        embed_subtitle=True,
        soft_subtitle=False,  # Use hard subtitles
        hardware_accel=HardwareAccel.AUTO,
    ),
    summary=SummaryConfig(
        enabled=True,
        max_key_points=5,
        include_timeline=True,
    ),
)

# Create processing pipeline
pipeline = TranslationPipeline(config)

# Process video
result = pipeline.process("video.mp4")

print(f"Subtitle file: {result['subtitle_file']}")
print(f"Output video: {result['output_video']}")
print(f"Summary file: {result['summary_file']}")

# Access summary data
if result['summary']:
    summary = result['summary']
    print(f"Title: {summary.title}")
    print(f"Overview: {summary.overview}")
    for point in summary.key_points:
        print(f"  - {point}")
```

## 🤖 Whisper Model Selection

| Model | Size | Memory | Speed | Accuracy |
|-------|------|--------|-------|----------|
| tiny | 39M | ~1GB | Fastest | Lower |
| base | 74M | ~1GB | Fast | Medium |
| small | 244M | ~2GB | Medium | Good |
| medium | 769M | ~5GB | Slow | High |
| large | 1550M | ~10GB | Slowest | Highest |

Recommendations:
- Quick preview: Use `tiny` or `base`
- Production use: Use `small` or `medium`
- Highest quality: Use `large`

## 🔌 Extending Translation Engines

The project uses a modular design, making it easy to add new translation engines:

```python
from video_translate.translator import BaseTranslator

class MyTranslator(BaseTranslator):
    @property
    def name(self) -> str:
        return "MyTranslator"

    def translate_text(self, text: str, context: str = "") -> str:
        # Implement translation logic
        pass

    def translate_batch(self, texts: list[str]) -> list[str]:
        # Implement batch translation logic
        pass
```

## 📁 Output Files

- `videoname_{language_code}.srt` - Subtitle file (e.g., `video_zh.srt`, `video_ja.srt`)
- `videoname_{language_code}_summary.json` - Video content summary in JSON format (title, overview, key points, topics, timeline)
- `videoname_{language_code}.mp4` - Video with embedded subtitles (if embedding is selected)

## ⚠️ Notes

1. **First run** will automatically download the Whisper model, please ensure a stable internet connection
2. **Hard subtitles** will re-encode the video, which takes longer; use `--hw-accel` to enable hardware acceleration for faster encoding
3. **Soft subtitles** only copy streams, faster but may not be supported by some players
4. Ensure FFmpeg is installed on your system
5. Apple Silicon Macs will automatically use MPS acceleration for Whisper and VideoToolbox for video encoding
6. **Video summary** is enabled by default and uses the same LLM API as translation; use `--no-summary` to disable

## 🛠️ Development

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Code formatting
uv run black src/

# Code linting
uv run ruff check src/

# Type checking
uv run mypy src/
```

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).

Copyright (c) 2026 innovationmech
