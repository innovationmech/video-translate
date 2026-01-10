# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

video-translate is a Python tool that automatically transcribes video audio using OpenAI Whisper, translates subtitles between 18 languages using LLM APIs (DeepSeek, OpenAI), and generates or embeds subtitles into videos. The tool supports multiple subtitle formats (SRT, VTT, ASS) and can create both soft and hard subtitles.

## Development Commands

### Environment Setup

```bash
# Install uv package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Install dependencies (including dev tools)
uv sync --dev

# Or using pip in editable mode
pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_translator.py

# Run specific test function
uv run pytest tests/test_translator.py::test_translate_segments

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov=src --cov-report=term-missing
```

### Code Quality

```bash
# Format code (line length: 100)
uv run black src/ tests/

# Check code formatting
uv run black --check src/ tests/

# Lint code (Ruff)
uv run ruff check src/ tests/

# Type check (MyPy)
uv run mypy src/

# Run all quality checks (as in CI)
uv run black --check src/ tests/
uv run ruff check src/ tests/
uv run mypy src/
```

### Building

```bash
# Build package
python -m build

# Check built package
twine check dist/*
```

### Running the Tool

```bash
# Basic usage
python -m video_translate video.mp4

# Or using the installed command
video-translate video.mp4

# With options
video-translate video.mp4 --source ja --target zh --model large
```

## Architecture Overview

### Core Pipeline (TranslationPipeline)

The processing pipeline follows four sequential steps:

1. **Transcription** (Transcriber): Extracts audio from video and uses Whisper to generate timed text segments
2. **Translation** (Translator): Translates segments from source to target language using LLM APIs
3. **Subtitle Generation** (SubtitleWriter): Writes translated segments to SRT files
4. **Video Processing** (VideoProcessor): Embeds subtitles into video using FFmpeg (optional)

### Key Design Patterns

**Lazy Initialization**: Pipeline components (transcriber, translator, subtitle_writer, video_processor) are created on first access via `@property` methods to avoid unnecessary initialization.

**Factory Pattern**: `create_translator()` in translator.py creates the appropriate translator instance based on configuration type.

**Configuration Dataclasses**: All configuration uses dataclasses with `__post_init__` hooks for default value setup based on environment variables and translator type.

**Abstract Base Classes**: `BaseTranslator` defines the interface for all translator implementations. Currently, only `OpenAICompatibleTranslator` is implemented, supporting both DeepSeek and OpenAI APIs.

### Module Responsibilities

- **config.py**: Configuration management with enums for TranslatorType, WhisperModel, Language. Includes language name mappings for 18 supported languages.
- **models.py**: Data models (SubtitleSegment, TranscriptionResult, TranslationResult) representing processing state.
- **transcriber.py**: Whisper integration with automatic device detection (CUDA/MPS/CPU).
- **translator.py**: LLM-based translation with batch processing and indexed output parsing.
- **subtitle.py**: SRT file generation supporting bilingual, target-only, and ordering options.
- **video.py**: FFmpeg integration for soft/hard subtitle embedding.
- **pipeline.py**: Orchestrates the end-to-end workflow.
- **cli.py**: Command-line interface with argument parsing and validation.
- **utils.py**: Shared utilities (device detection, progress logging).

### Extending Translation Engines

To add a new translator (e.g., Google, Azure):

1. Add enum value to `TranslatorType` in config.py
2. Create new class inheriting from `BaseTranslator` in translator.py
3. Implement required methods: `name`, `translate_text`, `translate_batch`
4. Update `create_translator()` factory function
5. Add API key environment variable handling in `TranslatorConfig.__post_init__`

### Device Management

The transcriber automatically detects the best available device:
- CUDA (NVIDIA GPUs)
- MPS (Apple Silicon)
- CPU (fallback)

FP16 precision is only enabled on CUDA devices. This is handled in `transcriber.py:61`.

## Dependencies

**Core Dependencies:**
- `openai-whisper`: Speech recognition
- `openai`: API client for LLM translation (works with DeepSeek and OpenAI)
- `torch`: Required by Whisper for model inference
- FFmpeg (system dependency): Required for video/audio processing and subtitle embedding

**Dev Dependencies:**
- `pytest`, `pytest-cov`: Testing framework
- `black`: Code formatter (line length 100)
- `ruff`: Fast Python linter
- `mypy`: Static type checker

## Testing Strategy

Tests are located in `tests/` directory with naming convention `test_*.py`. Each module has a corresponding test file:

- `test_config.py`: Configuration validation and language parsing
- `test_models.py`: Data model serialization
- `test_transcriber.py`: Whisper integration (may require mocking)
- `test_translator.py`: Translation logic and batch processing
- `test_subtitle.py`: SRT file generation
- `test_video.py`: FFmpeg integration (may require mocking)
- `conftest.py`: Shared pytest fixtures

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

- **ci.yml**: Runs on push/PR to master. Includes test (Python 3.10-3.12), lint (black, ruff, mypy), build (package check), and security (pip-audit) jobs.
- **code-quality.yml**: Additional code quality checks.
- **dependency-update.yml**: Automated dependency updates.

All CI jobs use `uv` for fast dependency management and caching.

## Environment Variables

- `DEEPSEEK_API_KEY`: DeepSeek API key (default translator)
- `OPENAI_API_KEY`: OpenAI API key (alternative translator)

The tool automatically selects the appropriate API key based on the `--translator` argument.

## Project Constraints

- Python 3.10+ required (uses modern type hints with `|` union operator)
- FFmpeg must be installed system-wide
- First run downloads Whisper model (size depends on `--model` choice: tiny=39M to large=1550M)
- Hard subtitle encoding is slower than soft subtitle embedding (full video re-encode vs stream copy)
