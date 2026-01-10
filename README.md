# 🎬 Video Subtitle Translation Tool

Automatically transcribe video audio, translate to target language, and generate subtitle files or embed them into videos. **Supports translation between 18 languages**.

[中文文档](README.zh.md) | [日本語ドキュメント](README.ja.md) | [한국어 문서](README.ko.md)

## ✨ Features

- 🎤 **Speech Recognition**: High-precision speech recognition using OpenAI Whisper
- 🌐 **Multi-language Translation**: Supports translation between 18 languages (Chinese, English, Japanese, Korean, French, German, Spanish, etc.)
- 🤖 **Multiple Engine Support**: Supports DeepSeek, OpenAI, and other translation engines
- 📄 **Subtitle Generation**: Supports multiple subtitle formats including SRT, VTT, ASS
- 🎥 **Subtitle Embedding**: Supports both soft and hard subtitle methods
- 🌍 **Bilingual Subtitles**: Optional bilingual subtitle generation
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
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download and install [FFmpeg](https://ffmpeg.org/download.html)

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
git clone https://github.com/yourusername/video-translate.git
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

| Option | Description |
|--------|-------------|
| `-s, --source` | Source language code (default: en) |
| `-t, --target` | Target language code (default: zh) |
| `--list-languages` | List all supported languages |
| `-o, --output` | Specify output directory |
| `-m, --model` | Whisper model size (tiny/base/small/medium/large) |
| `--translator` | Translation engine (deepseek/openai) |
| `--api-key` | Translation API Key |
| `--target-only` | Output only target language subtitles, without source text |
| `--source-first` | Source language on top, target language below |
| `--no-embed` | Don't embed subtitles into video, only generate subtitle files |
| `--hard-sub` | Use hard subtitles (burned into video) |
| `--font-size` | Hard subtitle font size (default: 24) |

### More Examples

```bash
# Use a larger model for better accuracy
video-translate video.mp4 --model large

# Only generate subtitle files, don't embed into video
video-translate video.mp4 --no-embed

# Generate hard subtitles (burned into video)
video-translate video.mp4 --hard-sub

# Output only target language subtitles
video-translate video.mp4 --target-only

# Use OpenAI translation
video-translate video.mp4 --translator openai

# Specify output directory
video-translate video.mp4 -o ./output
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
)

# Create processing pipeline
pipeline = TranslationPipeline(config)

# Process video
result = pipeline.process("video.mp4")

print(f"Subtitle file: {result['subtitle_file']}")
print(f"Output video: {result['output_video']}")
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
- `videoname_{language_code}.mp4` - Video with embedded subtitles (if embedding is selected)

## ⚠️ Notes

1. **First run** will automatically download the Whisper model, please ensure a stable internet connection
2. **Hard subtitles** will re-encode the video, which takes longer
3. **Soft subtitles** only copy streams, faster but may not be supported by some players
4. Ensure FFmpeg is installed on your system
5. Apple Silicon Macs will automatically use MPS acceleration

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
