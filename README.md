# 🎬 视频英文字幕翻译工具

将英文视频自动识别语音、翻译成中文，并生成字幕文件或嵌入视频。

## ✨ 功能特点

- 🎤 **语音识别**: 使用 OpenAI Whisper 进行高精度语音识别
- 🌐 **智能翻译**: 支持 DeepSeek、OpenAI 等翻译引擎
- 📄 **字幕生成**: 支持 SRT、VTT、ASS 等多种字幕格式
- 🎥 **字幕嵌入**: 支持软字幕和硬字幕两种方式
- 🌍 **双语字幕**: 可选择生成中英双语字幕
- 💰 **性价比高**: DeepSeek API 价格实惠，翻译质量优秀
- 🏗️ **模块化设计**: 易于扩展和维护

## 📁 项目结构

```
video-translate/
├── src/
│   └── video_translate/
│       ├── __init__.py      # 包初始化
│       ├── __main__.py      # 入口点
│       ├── cli.py           # 命令行接口
│       ├── config.py        # 配置管理
│       ├── models.py        # 数据模型
│       ├── transcriber.py   # 语音识别模块
│       ├── translator.py    # 翻译模块
│       ├── subtitle.py      # 字幕处理模块
│       ├── video.py         # 视频处理模块
│       ├── pipeline.py      # 处理流水线
│       └── utils.py         # 工具函数
├── pyproject.toml           # 项目配置
├── requirements.txt         # 依赖列表
└── README.md
```

## 📦 安装

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/video-translate.git
cd video-translate
```

### 2. 安装依赖

```bash
# 使用 pip 安装（推荐）
pip install -e .

# 或者只安装依赖
pip install -r requirements.txt
```

### 3. 安装 FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
下载并安装 [FFmpeg](https://ffmpeg.org/download.html)

### 4. 设置 API Key

前往 [DeepSeek 开放平台](https://platform.deepseek.com/) 注册并获取 API Key

```bash
export DEEPSEEK_API_KEY='your-api-key-here'
```

或者使用 OpenAI:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 🚀 使用方法

### 命令行使用

```bash
# 基本用法
video-translate video.mp4

# 或者使用 python -m
python -m video_translate video.mp4
```

### 命令行选项

| 选项 | 说明 |
|------|------|
| `-o, --output` | 指定输出目录 |
| `-m, --model` | Whisper 模型大小 (tiny/base/small/medium/large) |
| `--translator` | 翻译引擎 (deepseek/openai) |
| `--api-key` | 翻译 API Key |
| `--chinese-only` | 只输出中文字幕，不含英文原文 |
| `--english-first` | 英文在上，中文在下 |
| `--no-embed` | 不嵌入字幕到视频，只生成字幕文件 |
| `--hard-sub` | 使用硬字幕（烧录到视频中） |
| `--font-size` | 硬字幕字体大小 (默认: 24) |

### 示例

```bash
# 使用更大的模型提高识别准确度
video-translate video.mp4 --model large

# 只生成字幕文件，不嵌入视频
video-translate video.mp4 --no-embed

# 生成硬字幕（烧录到视频中）
video-translate video.mp4 --hard-sub

# 只输出中文字幕
video-translate video.mp4 --chinese-only

# 使用 OpenAI 翻译
video-translate video.mp4 --translator openai

# 指定输出目录
video-translate video.mp4 -o ./output
```

### 作为库使用

```python
from video_translate import (
    Config,
    TranscriberConfig,
    TranslatorConfig,
    TranslationPipeline,
    WhisperModel,
    TranslatorType,
)

# 创建配置
config = Config(
    transcriber=TranscriberConfig(model=WhisperModel.BASE),
    translator=TranslatorConfig(
        type=TranslatorType.DEEPSEEK,
        api_key="your-api-key"
    ),
)

# 创建处理流水线
pipeline = TranslationPipeline(config)

# 处理视频
result = pipeline.process("video.mp4")

print(f"字幕文件: {result['subtitle_file']}")
print(f"输出视频: {result['output_video']}")
```

## 🤖 Whisper 模型选择

| 模型 | 大小 | 显存需求 | 速度 | 准确度 |
|------|------|----------|------|--------|
| tiny | 39M | ~1GB | 最快 | 较低 |
| base | 74M | ~1GB | 快 | 中等 |
| small | 244M | ~2GB | 中等 | 较高 |
| medium | 769M | ~5GB | 较慢 | 高 |
| large | 1550M | ~10GB | 慢 | 最高 |

建议：
- 快速预览：使用 `tiny` 或 `base`
- 正式使用：使用 `small` 或 `medium`
- 最高质量：使用 `large`

## 🔌 扩展翻译引擎

项目采用模块化设计，可以轻松添加新的翻译引擎：

```python
from video_translate.translator import BaseTranslator

class MyTranslator(BaseTranslator):
    @property
    def name(self) -> str:
        return "MyTranslator"
    
    def translate_text(self, text: str, context: str = "") -> str:
        # 实现翻译逻辑
        pass
    
    def translate_batch(self, texts: list[str]) -> list[str]:
        # 实现批量翻译逻辑
        pass
```

## 📁 输出文件

- `视频名_cn.srt` - 中文字幕文件
- `视频名_cn.mp4` - 带字幕的视频（如果选择嵌入）

## ⚠️ 注意事项

1. **首次运行**会自动下载 Whisper 模型，请确保网络畅通
2. **硬字幕**会重新编码视频，耗时较长
3. **软字幕**只复制流，速度快但某些播放器可能不支持
4. 确保系统已安装 FFmpeg
5. Apple Silicon Mac 会自动使用 MPS 加速

## 🛠️ 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/

# 代码检查
ruff check src/
```

## 📄 License

MIT License
