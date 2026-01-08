"""
配置管理模块
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
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


@dataclass
class TranslatorConfig:
    """翻译器配置"""
    type: TranslatorType = TranslatorType.DEEPSEEK
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 2000
    batch_size: int = 10
    
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


@dataclass
class TranscriberConfig:
    """语音识别配置"""
    model: WhisperModel = WhisperModel.BASE
    language: str = "en"
    device: Optional[str] = None  # None 表示自动检测
    
    @property
    def model_name(self) -> str:
        return self.model.value


@dataclass
class SubtitleConfig:
    """字幕配置"""
    chinese_only: bool = False  # 只输出中文
    bilingual: bool = True  # 双语字幕
    chinese_first: bool = True  # 中文在上


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
    output_dir: Optional[Path] = None
    
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
        
        return errors
