"""
配置管理模块
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class TranslatorType(Enum):
    """翻译引擎类型"""

    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    # 预留其他翻译引擎
    # GOOGLE = "google"
    # AZURE = "azure"


class WhisperModel(Enum):
    """Whisper 模型大小"""

    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Language(Enum):
    """支持的语言"""

    # 常用语言
    CHINESE = "zh"
    ENGLISH = "en"
    JAPANESE = "ja"
    KOREAN = "ko"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    RUSSIAN = "ru"
    PORTUGUESE = "pt"
    ITALIAN = "it"
    DUTCH = "nl"
    POLISH = "pl"
    TURKISH = "tr"
    ARABIC = "ar"
    HINDI = "hi"
    THAI = "th"
    VIETNAMESE = "vi"
    INDONESIAN = "id"
    # 可以继续添加更多语言

    @classmethod
    def from_code(cls, code: str) -> "Language":
        """从语言代码获取语言枚举"""
        code = code.lower()
        for lang in cls:
            if lang.value == code:
                return lang
        raise ValueError(f"不支持的语言代码: {code}")

    @classmethod
    def list_codes(cls) -> list[str]:
        """列出所有支持的语言代码"""
        return [lang.value for lang in cls]


# 语言名称映射（用于提示词和显示）
LANGUAGE_NAMES = {
    Language.CHINESE: {"native": "中文", "english": "Chinese"},
    Language.ENGLISH: {"native": "English", "english": "English"},
    Language.JAPANESE: {"native": "日本語", "english": "Japanese"},
    Language.KOREAN: {"native": "한국어", "english": "Korean"},
    Language.FRENCH: {"native": "Français", "english": "French"},
    Language.GERMAN: {"native": "Deutsch", "english": "German"},
    Language.SPANISH: {"native": "Español", "english": "Spanish"},
    Language.RUSSIAN: {"native": "Русский", "english": "Russian"},
    Language.PORTUGUESE: {"native": "Português", "english": "Portuguese"},
    Language.ITALIAN: {"native": "Italiano", "english": "Italian"},
    Language.DUTCH: {"native": "Nederlands", "english": "Dutch"},
    Language.POLISH: {"native": "Polski", "english": "Polish"},
    Language.TURKISH: {"native": "Türkçe", "english": "Turkish"},
    Language.ARABIC: {"native": "العربية", "english": "Arabic"},
    Language.HINDI: {"native": "हिन्दी", "english": "Hindi"},
    Language.THAI: {"native": "ไทย", "english": "Thai"},
    Language.VIETNAMESE: {"native": "Tiếng Việt", "english": "Vietnamese"},
    Language.INDONESIAN: {"native": "Bahasa Indonesia", "english": "Indonesian"},
}


def get_language_name(lang: Language, native: bool = True) -> str:
    """获取语言的显示名称"""
    names = LANGUAGE_NAMES.get(lang, {"native": lang.value, "english": lang.value})
    return names["native"] if native else names["english"]


@dataclass
class TranslatorConfig:
    """翻译器配置"""

    type: TranslatorType = TranslatorType.DEEPSEEK
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None
    temperature: float = 0.3
    max_tokens: int = 2000
    batch_size: int = 10
    source_language: Language = Language.ENGLISH
    target_language: Language = Language.CHINESE

    def __post_init__(self):
        # 设置默认值
        if self.type == TranslatorType.DEEPSEEK:
            self.base_url = self.base_url or "https://api.deepseek.com"
            self.model = self.model or "deepseek-chat"
            self.api_key = self.api_key or os.environ.get("DEEPSEEK_API_KEY")
        elif self.type == TranslatorType.OPENAI:
            self.base_url = self.base_url or "https://api.openai.com/v1"
            self.model = self.model or "gpt-4o-mini"
            self.api_key = self.api_key or os.environ.get("OPENAI_API_KEY")

    @property
    def source_language_name(self) -> str:
        return get_language_name(self.source_language)

    @property
    def target_language_name(self) -> str:
        return get_language_name(self.target_language)


@dataclass
class TranscriberConfig:
    """语音识别配置"""

    model: WhisperModel = WhisperModel.BASE
    language: str = "en"  # Whisper 语言代码
    device: str | None = None  # None 表示自动检测

    @property
    def model_name(self) -> str:
        return self.model.value


@dataclass
class SubtitleConfig:
    """字幕配置"""

    target_only: bool = False  # 只输出目标语言
    bilingual: bool = True  # 双语字幕
    target_first: bool = True  # 目标语言在上


@dataclass
class VideoConfig:
    """视频处理配置"""

    embed_subtitle: bool = True  # 是否嵌入字幕
    soft_subtitle: bool = True  # 软字幕（vs 硬字幕）
    font_name: str = "PingFang SC"
    font_size: int = 24


@dataclass
class Config:
    """主配置类"""

    transcriber: TranscriberConfig = field(default_factory=TranscriberConfig)
    translator: TranslatorConfig = field(default_factory=TranslatorConfig)
    subtitle: SubtitleConfig = field(default_factory=SubtitleConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    output_dir: Path | None = None

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量创建配置"""
        return cls(
            translator=TranslatorConfig(
                api_key=os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
            )
        )

    def validate(self) -> list[str]:
        """验证配置，返回错误列表"""
        errors = []

        if not self.translator.api_key:
            errors.append("未设置翻译 API Key")

        if self.translator.source_language == self.translator.target_language:
            errors.append("源语言和目标语言不能相同")

        return errors
