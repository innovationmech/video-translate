# 🎬 ビデオ字幕翻訳ツール

動画の音声を自動的に認識し、ターゲット言語に翻訳して、字幕ファイルの生成または動画への埋め込みを行います。**18言語間の翻訳をサポート**。

[English](README.md) | [中文文档](README.zh.md) | [한국어 문서](README.ko.md)

## ✨ 機能

- 🎤 **音声認識**: OpenAI Whisperによる高精度音声認識
- 🌐 **多言語翻訳**: 18言語間の翻訳をサポート（中国語、英語、日本語、韓国語、フランス語、ドイツ語、スペイン語など）
- 🤖 **複数エンジンサポート**: DeepSeek、OpenAIなどの翻訳エンジンをサポート
- 📄 **字幕生成**: SRT、VTT、ASSなど複数の字幕フォーマットをサポート
- 🎥 **字幕埋め込み**: ソフト字幕とハード字幕の両方に対応
- 🌍 **バイリンガル字幕**: バイリンガル字幕の生成オプション
- 💰 **コストパフォーマンス**: DeepSeek APIは手頃な価格で優れた翻訳品質
- 🏗️ **モジュール設計**: 拡張とメンテナンスが容易

## 🌍 サポート言語

| コード | 言語 | コード | 言語 |
|--------|------|--------|------|
| `zh` | 中文 | `en` | English |
| `ja` | 日本語 | `ko` | 한국어 |
| `fr` | Français | `de` | Deutsch |
| `es` | Español | `ru` | Русский |
| `pt` | Português | `it` | Italiano |
| `nl` | Nederlands | `pl` | Polski |
| `tr` | Türkçe | `ar` | العربية |
| `hi` | हिन्दी | `th` | ไทย |
| `vi` | Tiếng Việt | `id` | Bahasa Indonesia |

`video-translate --list-languages` で完全なリストを表示できます。

## 📁 プロジェクト構成

```
video-translate/
├── src/
│   └── video_translate/
│       ├── __init__.py      # パッケージ初期化
│       ├── __main__.py      # エントリーポイント
│       ├── cli.py           # コマンドラインインターフェース
│       ├── config.py        # 設定管理
│       ├── models.py        # データモデル
│       ├── transcriber.py   # 音声認識モジュール
│       ├── translator.py    # 翻訳モジュール
│       ├── subtitle.py      # 字幕処理モジュール
│       ├── video.py         # ビデオ処理モジュール
│       ├── pipeline.py      # 処理パイプライン
│       └── utils.py         # ユーティリティ関数
├── pyproject.toml           # プロジェクト設定
├── requirements.txt         # 依存関係
├── LICENSE                  # MITライセンス
├── .gitignore               # Git無視ファイル
└── README.md
```

## 📦 インストール

### 前提条件

ビデオ処理にはFFmpegが必要です。先にインストールしてください：

**macOS:**
```bash
# 基本インストール（ソフト字幕に十分）
brew install ffmpeg

# ハード字幕（--hard-sub）を使用する場合、libassサポート付きのFFmpegが必要：
brew install ffmpeg-full
echo 'export PATH="/opt/homebrew/opt/ffmpeg-full/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

> **注意**: 標準の `brew install ffmpeg` にはlibassサポートが含まれておらず、`--hard-sub` 機能にはlibassが必要です。「No option name near force_style」エラーが発生した場合は、`ffmpeg-full` をインストールしてください。

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```
> aptパッケージには通常libassサポートが含まれています。`--hard-sub` で「No option name near force_style」エラーが発生した場合は、libassをインストールしてください：`sudo apt install libass-dev` を実行し、ffmpegを再インストールしてください。

**Windows:**
[FFmpeg](https://ffmpeg.org/download.html) をダウンロードしてインストール（推奨：[gyan.dev](https://www.gyan.dev/ffmpeg/builds/) のフルビルドまたは [BtbN](https://github.com/BtbN/FFmpeg-Builds/releases) のビルド、これらにはlibassサポートが含まれています）

### クイックインストール（推奨）

```bash
pip install video-translate
```

または [uv](https://github.com/astral-sh/uv)（より高速）を使用：

```bash
uv pip install video-translate
```

### 開発インストール

開発に参加したい、またはコードを修正したい場合：

```bash
# 1. プロジェクトをクローン
git clone https://github.com/yourusername/video-translate.git
cd video-translate

# 2. uvをインストール（未インストールの場合）
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. 依存関係をインストール（開発ツールを含む）
uv sync --dev

# または、pipで編集可能モードでインストール
pip install -e ".[dev]"
```

### APIキーの設定

[DeepSeek Open Platform](https://platform.deepseek.com/) で登録してAPIキーを取得：

```bash
export DEEPSEEK_API_KEY='your-api-key-here'
```

またはOpenAIを使用：
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 🚀 使用方法

### コマンドライン使用

```bash
# 基本的な使い方（英語 → 中国語）
video-translate video.mp4

# またはpython -mを使用
python -m video_translate video.mp4
```

### 多言語翻訳の例

```bash
# 英語 → 中国語（デフォルト）
video-translate video.mp4

# 日本語 → 中国語
video-translate video.mp4 --source ja --target zh

# 英語 → 日本語
video-translate video.mp4 --source en --target ja

# 中国語 → 英語
video-translate video.mp4 --source zh --target en

# 韓国語 → 日本語
video-translate video.mp4 --source ko --target ja

# フランス語 → ドイツ語
video-translate video.mp4 --source fr --target de
```

### コマンドラインオプション

| オプション | 説明 |
|-----------|------|
| `-s, --source` | ソース言語コード（デフォルト: en） |
| `-t, --target` | ターゲット言語コード（デフォルト: zh） |
| `--list-languages` | サポートされているすべての言語をリスト |
| `-o, --output` | 出力ディレクトリを指定 |
| `-m, --model` | Whisperモデルサイズ（tiny/base/small/medium/large） |
| `--translator` | 翻訳エンジン（deepseek/openai） |
| `--api-key` | 翻訳APIキー |
| `--target-only` | ターゲット言語の字幕のみ出力、ソーステキストなし |
| `--source-first` | ソース言語を上に、ターゲット言語を下に |
| `--no-embed` | 字幕を動画に埋め込まず、字幕ファイルのみ生成 |
| `--hard-sub` | ハード字幕を使用（動画に焼き付け） |
| `--font-size` | ハード字幕のフォントサイズ（デフォルト: 24） |

### その他の例

```bash
# より大きなモデルを使用して精度を向上
video-translate video.mp4 --model large

# 字幕ファイルのみを生成、動画に埋め込まない
video-translate video.mp4 --no-embed

# ハード字幕を生成（動画に焼き付け）
video-translate video.mp4 --hard-sub

# ターゲット言語の字幕のみ出力
video-translate video.mp4 --target-only

# OpenAI翻訳を使用
video-translate video.mp4 --translator openai

# 出力ディレクトリを指定
video-translate video.mp4 -o ./output
```

### ライブラリとして使用

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

# 設定を作成 - 日本語から中国語への翻訳
config = Config(
    transcriber=TranscriberConfig(
        model=WhisperModel.BASE,
        language="ja"  # ソース言語
    ),
    translator=TranslatorConfig(
        type=TranslatorType.DEEPSEEK,
        api_key="your-api-key",
        source_language=Language.JAPANESE,
        target_language=Language.CHINESE,
    ),
)

# 処理パイプラインを作成
pipeline = TranslationPipeline(config)

# ビデオを処理
result = pipeline.process("video.mp4")

print(f"字幕ファイル: {result['subtitle_file']}")
print(f"出力ビデオ: {result['output_video']}")
```

## 🤖 Whisperモデルの選択

| モデル | サイズ | メモリ | 速度 | 精度 |
|--------|--------|--------|------|------|
| tiny | 39M | ~1GB | 最速 | 低 |
| base | 74M | ~1GB | 速い | 中 |
| small | 244M | ~2GB | 中 | 良 |
| medium | 769M | ~5GB | 遅い | 高 |
| large | 1550M | ~10GB | 最遅 | 最高 |

推奨：
- クイックプレビュー：`tiny` または `base` を使用
- 本番使用：`small` または `medium` を使用
- 最高品質：`large` を使用

## 🔌 翻訳エンジンの拡張

プロジェクトはモジュール設計を採用しており、新しい翻訳エンジンを簡単に追加できます：

```python
from video_translate.translator import BaseTranslator

class MyTranslator(BaseTranslator):
    @property
    def name(self) -> str:
        return "MyTranslator"

    def translate_text(self, text: str, context: str = "") -> str:
        # 翻訳ロジックを実装
        pass

    def translate_batch(self, texts: list[str]) -> list[str]:
        # バッチ翻訳ロジックを実装
        pass
```

## 📁 出力ファイル

- `videoname_{language_code}.srt` - 字幕ファイル（例：`video_zh.srt`、`video_ja.srt`）
- `videoname_{language_code}.mp4` - 字幕が埋め込まれた動画（埋め込みを選択した場合）

## ⚠️ 注意事項

1. **初回実行**時にWhisperモデルが自動的にダウンロードされます。安定したインターネット接続を確保してください
2. **ハード字幕**は動画を再エンコードするため、時間がかかります
3. **ソフト字幕**はストリームをコピーするだけなので高速ですが、一部のプレーヤーではサポートされていない場合があります
4. システムにFFmpegがインストールされていることを確認してください
5. Apple Silicon Macは自動的にMPSアクセラレーションを使用します

## 🛠️ 開発

```bash
# 開発依存関係をインストール
uv sync --dev

# テストを実行
uv run pytest

# コードフォーマット
uv run black src/

# コードリンティング
uv run ruff check src/

# 型チェック
uv run mypy src/
```

## 📄 ライセンス

このプロジェクトは [MITライセンス](LICENSE) の下でオープンソース化されています。

Copyright (c) 2026 innovationmech
