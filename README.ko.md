# 🎬 비디오 자막 번역 도구

동영상 음성을 자동으로 인식하여 대상 언어로 번역하고 자막 파일을 생성하거나 비디오에 임베드합니다. **18개 언어 간 번역 지원**.

[English](README.md) | [中文文档](README.zh.md) | [日本語ドキュメント](README.ja.md)

## ✨ 기능

- 🎤 **음성 인식**: OpenAI Whisper를 사용한 고정밀 음성 인식
- 🌐 **다국어 번역**: 18개 언어 간 번역 지원 (중국어, 영어, 일본어, 한국어, 프랑스어, 독일어, 스페인어 등)
- 🤖 **다중 엔진 지원**: DeepSeek, OpenAI 등의 번역 엔진 지원
- 📄 **자막 생성**: SRT, VTT, ASS 등 다양한 자막 형식 지원
- 🎥 **자막 임베딩**: 소프트 자막 및 하드 자막 모두 지원
- 🌍 **이중 언어 자막**: 이중 언어 자막 생성 옵션
- 💰 **비용 효율적**: DeepSeek API는 저렴한 가격에 우수한 번역 품질 제공
- 🏗️ **모듈식 설계**: 쉬운 확장 및 유지보수

## 🌍 지원 언어

| 코드 | 언어 | 코드 | 언어 |
|------|------|------|------|
| `zh` | 中文 | `en` | English |
| `ja` | 日本語 | `ko` | 한국어 |
| `fr` | Français | `de` | Deutsch |
| `es` | Español | `ru` | Русский |
| `pt` | Português | `it` | Italiano |
| `nl` | Nederlands | `pl` | Polski |
| `tr` | Türkçe | `ar` | العربية |
| `hi` | हिन्दी | `th` | ไทย |
| `vi` | Tiếng Việt | `id` | Bahasa Indonesia |

`video-translate --list-languages` 명령으로 전체 목록을 확인할 수 있습니다.

## 📁 프로젝트 구조

```
video-translate/
├── src/
│   └── video_translate/
│       ├── __init__.py      # 패키지 초기화
│       ├── __main__.py      # 진입점
│       ├── cli.py           # 커맨드라인 인터페이스
│       ├── config.py        # 설정 관리
│       ├── models.py        # 데이터 모델
│       ├── transcriber.py   # 음성 인식 모듈
│       ├── translator.py    # 번역 모듈
│       ├── subtitle.py      # 자막 처리 모듈
│       ├── video.py         # 비디오 처리 모듈
│       ├── pipeline.py      # 처리 파이프라인
│       └── utils.py         # 유틸리티 함수
├── pyproject.toml           # 프로젝트 설정
├── requirements.txt         # 종속성
├── LICENSE                  # MIT 라이선스
├── .gitignore               # Git 무시 파일
└── README.md
```

## 📦 설치

### 사전 요구사항

비디오 처리를 위해 FFmpeg가 필요합니다. 먼저 설치하세요:

**macOS:**
```bash
# 기본 설치 (소프트 자막에 충분)
brew install ffmpeg

# 하드 자막(--hard-sub)을 사용하려면 libass 지원이 포함된 FFmpeg가 필요합니다:
brew install ffmpeg-full
echo 'export PATH="/opt/homebrew/opt/ffmpeg-full/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

> **참고**: 표준 `brew install ffmpeg`에는 libass 지원이 포함되어 있지 않으며, `--hard-sub` 기능에는 libass가 필요합니다. "No option name near force_style" 오류가 발생하면 `ffmpeg-full`을 설치하세요.

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```
> apt 패키지에는 일반적으로 libass 지원이 포함되어 있습니다. `--hard-sub` 사용 시 "No option name near force_style" 오류가 발생하면 libass를 설치하세요: `sudo apt install libass-dev` 실행 후 ffmpeg를 다시 설치하세요.

**Windows:**
[FFmpeg](https://ffmpeg.org/download.html) 다운로드 및 설치 (권장: [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 전체 빌드 또는 [BtbN](https://github.com/BtbN/FFmpeg-Builds/releases) 빌드, libass 지원 포함)

### 빠른 설치 (권장)

```bash
pip install video-translate
```

또는 [uv](https://github.com/astral-sh/uv) 사용 (더 빠름):

```bash
uv pip install video-translate
```

### 개발 설치

개발에 참여하거나 코드를 수정하려는 경우:

```bash
# 1. 프로젝트 클론
git clone https://github.com/yourusername/video-translate.git
cd video-translate

# 2. uv 설치 (미설치된 경우)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. 종속성 설치 (개발 도구 포함)
uv sync --dev

# 또는 pip로 편집 가능 모드로 설치
pip install -e ".[dev]"
```

### API 키 설정

[DeepSeek Open Platform](https://platform.deepseek.com/)에서 등록하고 API 키를 받으세요:

```bash
export DEEPSEEK_API_KEY='your-api-key-here'
```

또는 OpenAI 사용:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 🚀 사용법

### 커맨드라인 사용

```bash
# 기본 사용법 (영어 → 중국어)
video-translate video.mp4

# 또는 python -m 사용
python -m video_translate video.mp4
```

### 다국어 번역 예제

```bash
# 영어 → 중국어 (기본값)
video-translate video.mp4

# 일본어 → 중국어
video-translate video.mp4 --source ja --target zh

# 영어 → 일본어
video-translate video.mp4 --source en --target ja

# 중국어 → 영어
video-translate video.mp4 --source zh --target en

# 한국어 → 일본어
video-translate video.mp4 --source ko --target ja

# 프랑스어 → 독일어
video-translate video.mp4 --source fr --target de
```

### 커맨드라인 옵션

| 옵션 | 설명 |
|------|------|
| `-s, --source` | 소스 언어 코드 (기본값: en) |
| `-t, --target` | 대상 언어 코드 (기본값: zh) |
| `--list-languages` | 지원되는 모든 언어 나열 |
| `-o, --output` | 출력 디렉토리 지정 |
| `-m, --model` | Whisper 모델 크기 (tiny/base/small/medium/large) |
| `--translator` | 번역 엔진 (deepseek/openai) |
| `--api-key` | 번역 API 키 |
| `--target-only` | 대상 언어 자막만 출력, 소스 텍스트 제외 |
| `--source-first` | 소스 언어를 위에, 대상 언어를 아래에 |
| `--no-embed` | 자막을 비디오에 임베드하지 않고 자막 파일만 생성 |
| `--hard-sub` | 하드 자막 사용 (비디오에 구워넣기) |
| `--font-size` | 하드 자막 폰트 크기 (기본값: 24) |

### 추가 예제

```bash
# 더 큰 모델을 사용하여 정확도 향상
video-translate video.mp4 --model large

# 자막 파일만 생성, 비디오에 임베드하지 않음
video-translate video.mp4 --no-embed

# 하드 자막 생성 (비디오에 구워넣기)
video-translate video.mp4 --hard-sub

# 대상 언어 자막만 출력
video-translate video.mp4 --target-only

# OpenAI 번역 사용
video-translate video.mp4 --translator openai

# 출력 디렉토리 지정
video-translate video.mp4 -o ./output
```

### 라이브러리로 사용

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

# 설정 생성 - 일본어에서 중국어로 번역
config = Config(
    transcriber=TranscriberConfig(
        model=WhisperModel.BASE,
        language="ja"  # 소스 언어
    ),
    translator=TranslatorConfig(
        type=TranslatorType.DEEPSEEK,
        api_key="your-api-key",
        source_language=Language.JAPANESE,
        target_language=Language.CHINESE,
    ),
)

# 처리 파이프라인 생성
pipeline = TranslationPipeline(config)

# 비디오 처리
result = pipeline.process("video.mp4")

print(f"자막 파일: {result['subtitle_file']}")
print(f"출력 비디오: {result['output_video']}")
```

## 🤖 Whisper 모델 선택

| 모델 | 크기 | 메모리 | 속도 | 정확도 |
|------|------|--------|------|--------|
| tiny | 39M | ~1GB | 가장 빠름 | 낮음 |
| base | 74M | ~1GB | 빠름 | 중간 |
| small | 244M | ~2GB | 중간 | 좋음 |
| medium | 769M | ~5GB | 느림 | 높음 |
| large | 1550M | ~10GB | 가장 느림 | 가장 높음 |

권장사항:
- 빠른 미리보기: `tiny` 또는 `base` 사용
- 프로덕션 사용: `small` 또는 `medium` 사용
- 최고 품질: `large` 사용

## 🔌 번역 엔진 확장

프로젝트는 모듈식 설계를 사용하여 새로운 번역 엔진을 쉽게 추가할 수 있습니다:

```python
from video_translate.translator import BaseTranslator

class MyTranslator(BaseTranslator):
    @property
    def name(self) -> str:
        return "MyTranslator"

    def translate_text(self, text: str, context: str = "") -> str:
        # 번역 로직 구현
        pass

    def translate_batch(self, texts: list[str]) -> list[str]:
        # 배치 번역 로직 구현
        pass
```

## 📁 출력 파일

- `videoname_{language_code}.srt` - 자막 파일 (예: `video_zh.srt`, `video_ja.srt`)
- `videoname_{language_code}.mp4` - 자막이 임베드된 비디오 (임베딩 선택 시)

## ⚠️ 주의사항

1. **첫 실행** 시 Whisper 모델이 자동으로 다운로드됩니다. 안정적인 인터넷 연결을 확인하세요
2. **하드 자막**은 비디오를 다시 인코딩하므로 시간이 더 걸립니다
3. **소프트 자막**은 스트림만 복사하므로 빠르지만 일부 플레이어에서 지원되지 않을 수 있습니다
4. 시스템에 FFmpeg가 설치되어 있는지 확인하세요
5. Apple Silicon Mac은 자동으로 MPS 가속을 사용합니다

## 🛠️ 개발

```bash
# 개발 종속성 설치
uv sync --dev

# 테스트 실행
uv run pytest

# 코드 포맷팅
uv run black src/

# 코드 린팅
uv run ruff check src/

# 타입 체크
uv run mypy src/
```

## 📄 라이선스

이 프로젝트는 [MIT License](LICENSE)에 따라 오픈소스로 제공됩니다.

Copyright (c) 2026 innovationmech
