# 🎬 Video-Untertitel-Übersetzungstool

Automatische Transkription von Videoaudio, Übersetzung in die Zielsprache und Erstellung von Untertiteldateien oder Einbettung in Videos. **Unterstützt Übersetzung zwischen 18 Sprachen**.

[English](README.md) | [中文文档](README.zh.md) | [日本語ドキュメント](README.ja.md) | [한국어 문서](README.ko.md) | [Français](README.fr.md)

## ✨ Funktionen

- 🎤 **Spracherkennung**: Hochpräzise Spracherkennung mit OpenAI Whisper
- 🌐 **Mehrsprachige Übersetzung**: Übersetzung zwischen 18 Sprachen (Chinesisch, Englisch, Japanisch, Koreanisch, Französisch, Deutsch, Spanisch usw.)
- 🤖 **Mehrere Engines**: Unterstützung für DeepSeek, OpenAI und andere Übersetzungsengines
- 📄 **Untertitelerstellung**: Unterstützung mehrerer Untertitelformate: SRT, VTT, ASS
- 🎥 **Untertiteleinbettung**: Sowohl Soft- als auch Hard-Untertitel
- 🌍 **Zweisprachige Untertitel**: Optionale zweisprachige Untertitelerstellung
- 📝 **Videozusammenfassung**: LLM-basierte Videoinhaltsanalyse mit Kernpunkten, Themen und Zeitleiste
- ⚡ **Hardwarebeschleunigung**: Automatische Erkennung der Hardware-Kodierung (VideoToolbox/NVENC/QSV/AMF) für schnelleres Hard-Untertitel-Rendering
- 🖥️ **GUI-Integration**: JSON-Fortschrittsausgabe für nahtlose Integration mit grafischen Oberflächen
- 💰 **Kosteneffizient**: Die DeepSeek-API bietet erschwingliche Preise bei hervorragender Übersetzungsqualität
- 🏗️ **Modulares Design**: Einfach erweiterbar und wartbar

## 🌍 Unterstützte Sprachen

| Code | Sprache | Code | Sprache |
|------|---------|------|---------|
| `zh` | 中文 (Chinesisch) | `en` | English (Englisch) |
| `ja` | 日本語 (Japanisch) | `ko` | 한국어 (Koreanisch) |
| `fr` | Français (Französisch) | `de` | Deutsch |
| `es` | Español (Spanisch) | `ru` | Русский (Russisch) |
| `pt` | Português (Portugiesisch) | `it` | Italiano (Italienisch) |
| `nl` | Nederlands (Niederländisch) | `pl` | Polski (Polnisch) |
| `tr` | Türkçe (Türkisch) | `ar` | العربية (Arabisch) |
| `hi` | हिन्दी (Hindi) | `th` | ไทย (Thailändisch) |
| `vi` | Tiếng Việt (Vietnamesisch) | `id` | Bahasa Indonesia (Indonesisch) |

Verwenden Sie `video-translate --list-languages`, um die vollständige Liste anzuzeigen.

## 📁 Projektstruktur

```
video-translate/
├── src/
│   └── video_translate/
│       ├── __init__.py      # Paketinitialisierung
│       ├── __main__.py      # Einstiegspunkt
│       ├── cli.py           # Kommandozeilenschnittstelle
│       ├── config.py        # Konfigurationsverwaltung
│       ├── models.py        # Datenmodelle
│       ├── transcriber.py   # Spracherkennungsmodul
│       ├── translator.py    # Übersetzungsmodul
│       ├── summarizer.py    # Videoinhalts-Zusammenfassungsmodul
│       ├── subtitle.py      # Untertitelverarbeitungsmodul
│       ├── video.py         # Videoverarbeitungsmodul
│       ├── pipeline.py      # Verarbeitungspipeline
│       └── utils.py         # Hilfsfunktionen
├── pyproject.toml           # Projektkonfiguration
├── requirements.txt         # Abhängigkeiten
├── LICENSE                  # MIT-Lizenz
├── .gitignore               # Git-Ignore-Datei
└── README.md
```

## 📦 Installation

### Voraussetzungen

FFmpeg ist für die Videoverarbeitung erforderlich. Bitte installieren Sie es zuerst:

**macOS:**
```bash
# Basisinstallation (ausreichend für Soft-Untertitel)
brew install ffmpeg

# Für Hard-Untertitel (--hard-sub) wird FFmpeg mit libass-Unterstützung benötigt:
brew install ffmpeg-full
echo 'export PATH="/opt/homebrew/opt/ffmpeg-full/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

> **Hinweis**: Das Standard-`brew install ffmpeg` enthält keine libass-Unterstützung, die für die Funktion `--hard-sub` erforderlich ist. Wenn der Fehler „No option name near force_style" auftritt, installieren Sie bitte `ffmpeg-full`.

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```
> Das apt-Paket enthält normalerweise libass-Unterstützung. Wenn bei `--hard-sub` der Fehler „No option name near force_style" auftritt, installieren Sie libass: `sudo apt install libass-dev` und installieren Sie ffmpeg neu.

**Windows:**
Laden Sie [FFmpeg](https://ffmpeg.org/download.html) herunter und installieren Sie es (empfohlen: [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) Full-Build oder [BtbN](https://github.com/BtbN/FFmpeg-Builds/releases) Builds, die libass-Unterstützung enthalten)

### Schnellinstallation (empfohlen)

```bash
pip install video-translate
```

Oder verwenden Sie [uv](https://github.com/astral-sh/uv) (schneller):

```bash
uv pip install video-translate
```

### Entwicklungsinstallation

Wenn Sie zur Entwicklung beitragen oder den Code ändern möchten:

```bash
# 1. Projekt klonen
git clone https://github.com/innovationmech/video-translate.git
cd video-translate

# 2. uv installieren (falls noch nicht installiert)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. Abhängigkeiten installieren (einschließlich Entwicklungstools)
uv sync --dev

# Oder mit pip im editierbaren Modus installieren
pip install -e ".[dev]"
```

### API-Schlüssel einrichten

Registrieren Sie sich und erhalten Sie einen API-Schlüssel auf der [DeepSeek Open Platform](https://platform.deepseek.com/):

```bash
export DEEPSEEK_API_KEY='your-api-key-here'
```

Oder verwenden Sie OpenAI:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 🚀 Verwendung

### Kommandozeilenverwendung

```bash
# Grundlegende Verwendung (Englisch → Chinesisch)
video-translate video.mp4

# Oder mit python -m
python -m video_translate video.mp4
```

### Beispiele für mehrsprachige Übersetzung

```bash
# Englisch → Chinesisch (Standard)
video-translate video.mp4

# Japanisch → Chinesisch
video-translate video.mp4 --source ja --target zh

# Englisch → Japanisch
video-translate video.mp4 --source en --target ja

# Chinesisch → Englisch
video-translate video.mp4 --source zh --target en

# Koreanisch → Japanisch
video-translate video.mp4 --source ko --target ja

# Französisch → Deutsch
video-translate video.mp4 --source fr --target de
```

### Kommandozeilenoptionen

**Grundoptionen:**

| Option | Beschreibung |
|--------|--------------|
| `-s, --source` | Quellsprachcode (Standard: en) |
| `-t, --target` | Zielsprachcode (Standard: zh) |
| `--list-languages` | Alle unterstützten Sprachen auflisten |
| `-o, --output` | Ausgabeverzeichnis angeben |
| `-m, --model` | Whisper-Modellgröße (tiny/base/small/medium/large) |
| `-v, --version` | Version anzeigen |
| `--verbose` | Detaillierte Protokolle anzeigen |

**Übersetzungsoptionen:**

| Option | Beschreibung |
|--------|--------------|
| `--translator` | Übersetzungsengine (deepseek/openai) |
| `--api-key` | Übersetzungs-API-Schlüssel |
| `--api-base` | API-Basis-URL (optional, für benutzerdefinierte Endpunkte) |
| `--llm-model` | LLM-Modellname (optional, überschreibt das Standardmodell) |

**Untertiteloptionen:**

| Option | Beschreibung |
|--------|--------------|
| `--target-only` | Nur Untertitel der Zielsprache ausgeben, ohne Quelltext |
| `--source-first` | Quellsprache oben, Zielsprache unten |

**Videooptionen:**

| Option | Beschreibung |
|--------|--------------|
| `--no-embed` | Untertitel nicht in Video einbetten, nur Untertiteldateien erstellen |
| `--hard-sub` | Hard-Untertitel verwenden (in Video eingebrannt) |
| `--font-size` | Schriftgröße der Hard-Untertitel (Standard: 24) |
| `--hw-accel` | Hardwarebeschleunigung für Hard-Untertitel-Kodierung (auto/none/videotoolbox/nvenc/qsv/amf, Standard: auto) |
| `--video-quality` | Videoqualität der Hard-Untertitel, CRF-Wert (0-51, niedriger = besser, Standard: 23) |

**Zusammenfassungsoptionen:**

| Option | Beschreibung |
|--------|--------------|
| `--no-summary` | Videoinhalts-Zusammenfassung deaktivieren |
| `--summary-lang` | Sprachcode der Zusammenfassung (Standard: folgt der Zielsprache) |
| `--max-key-points` | Maximale Anzahl der Kernpunkte in der Zusammenfassung (Standard: 5) |
| `--no-timeline` | Zeitleiste aus der Zusammenfassung ausschließen |

**Erweiterte Optionen:**

| Option | Beschreibung |
|--------|--------------|
| `--json-progress` | JSON-formatierte Fortschrittsausgabe (für GUI-Integration) |

### Weitere Beispiele

```bash
# Größeres Modell für bessere Genauigkeit verwenden
video-translate video.mp4 --model large

# Nur Untertiteldateien erstellen, nicht in Video einbetten
video-translate video.mp4 --no-embed

# Hard-Untertitel erstellen (in Video eingebrannt)
video-translate video.mp4 --hard-sub

# Hard-Untertitel mit NVIDIA-Hardwarebeschleunigung und hoher Qualität
video-translate video.mp4 --hard-sub --hw-accel nvenc --video-quality 18

# Nur Untertitel der Zielsprache ausgeben
video-translate video.mp4 --target-only

# OpenAI-Übersetzung verwenden
video-translate video.mp4 --translator openai

# Benutzerdefinierten API-Endpunkt und Modell verwenden
video-translate video.mp4 --api-base https://your-api.com/v1 --llm-model your-model

# Videoinhalts-Zusammenfassung deaktivieren
video-translate video.mp4 --no-summary

# Zusammenfassung auf Englisch mit bis zu 10 Kernpunkten erstellen
video-translate video.mp4 --summary-lang en --max-key-points 10

# Ausgabeverzeichnis angeben
video-translate video.mp4 -o ./output

# JSON-Fortschrittsausgabe für GUI-Integration
video-translate video.mp4 --json-progress
```

### Als Bibliothek verwenden

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

# Konfiguration erstellen - Übersetzung von Japanisch nach Chinesisch
config = Config(
    transcriber=TranscriberConfig(
        model=WhisperModel.BASE,
        language="ja"  # Quellsprache
    ),
    translator=TranslatorConfig(
        type=TranslatorType.DEEPSEEK,
        api_key="your-api-key",
        source_language=Language.JAPANESE,
        target_language=Language.CHINESE,
    ),
    video=VideoConfig(
        embed_subtitle=True,
        soft_subtitle=False,  # Hard-Untertitel verwenden
        hardware_accel=HardwareAccel.AUTO,
    ),
    summary=SummaryConfig(
        enabled=True,
        max_key_points=5,
        include_timeline=True,
    ),
)

# Verarbeitungspipeline erstellen
pipeline = TranslationPipeline(config)

# Video verarbeiten
result = pipeline.process("video.mp4")

print(f"Untertiteldatei: {result['subtitle_file']}")
print(f"Ausgabevideo: {result['output_video']}")
print(f"Zusammenfassungsdatei: {result['summary_file']}")

# Auf Zusammenfassungsdaten zugreifen
if result['summary']:
    summary = result['summary']
    print(f"Titel: {summary.title}")
    print(f"Überblick: {summary.overview}")
    for point in summary.key_points:
        print(f"  - {point}")
```

## 🤖 Whisper-Modellauswahl

| Modell | Größe | Speicher | Geschwindigkeit | Genauigkeit |
|--------|-------|----------|-----------------|-------------|
| tiny | 39M | ~1 GB | Am schnellsten | Niedrig |
| base | 74M | ~1 GB | Schnell | Mittel |
| small | 244M | ~2 GB | Mittel | Gut |
| medium | 769M | ~5 GB | Langsam | Hoch |
| large | 1550M | ~10 GB | Am langsamsten | Am höchsten |

Empfehlungen:
- Schnelle Vorschau: Verwenden Sie `tiny` oder `base`
- Produktionseinsatz: Verwenden Sie `small` oder `medium`
- Höchste Qualität: Verwenden Sie `large`

## 🔌 Übersetzungsengines erweitern

Das Projekt verwendet ein modulares Design, das das Hinzufügen neuer Übersetzungsengines erleichtert:

```python
from video_translate.translator import BaseTranslator

class MyTranslator(BaseTranslator):
    @property
    def name(self) -> str:
        return "MyTranslator"

    def translate_text(self, text: str, context: str = "") -> str:
        # Übersetzungslogik implementieren
        pass

    def translate_batch(self, texts: list[str]) -> list[str]:
        # Stapelübersetzungslogik implementieren
        pass
```

## 📁 Ausgabedateien

- `videoname_{sprachcode}.srt` - Untertiteldatei (z.B. `video_zh.srt`, `video_ja.srt`)
- `videoname_{sprachcode}_summary.json` - Videoinhalts-Zusammenfassung im JSON-Format (Titel, Überblick, Kernpunkte, Themen, Zeitleiste)
- `videoname_{sprachcode}.mp4` - Video mit eingebetteten Untertiteln (wenn Einbettung ausgewählt)

## ⚠️ Hinweise

1. **Beim ersten Start** wird das Whisper-Modell automatisch heruntergeladen. Bitte stellen Sie eine stabile Internetverbindung sicher
2. **Hard-Untertitel** kodieren das Video neu, was länger dauert; verwenden Sie `--hw-accel`, um die Hardwarebeschleunigung für schnellere Kodierung zu aktivieren
3. **Soft-Untertitel** kopieren nur Streams, schneller, aber möglicherweise nicht von allen Playern unterstützt
4. Stellen Sie sicher, dass FFmpeg auf Ihrem System installiert ist
5. Apple Silicon Macs verwenden automatisch MPS-Beschleunigung für Whisper und VideoToolbox für die Videokodierung
6. **Die Videozusammenfassung** ist standardmäßig aktiviert und verwendet dieselbe LLM-API wie die Übersetzung; verwenden Sie `--no-summary` zum Deaktivieren

## 🛠️ Entwicklung

```bash
# Entwicklungsabhängigkeiten installieren
uv sync --dev

# Tests ausführen
uv run pytest

# Code formatieren
uv run black src/

# Code prüfen
uv run ruff check src/

# Typprüfung
uv run mypy src/
```

## 📄 Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) als Open Source veröffentlicht.

Copyright (c) 2026 innovationmech
