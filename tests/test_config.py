"""
配置类测试
"""

import os
from unittest.mock import patch

import pytest

from video_translate.config import (
    LANGUAGE_NAMES,
    Config,
    Language,
    SubtitleConfig,
    TranscriberConfig,
    TranslatorConfig,
    TranslatorType,
    VideoConfig,
    WhisperModel,
    get_language_name,
)


class TestTranslatorType:
    """测试翻译器类型枚举"""

    def test_deepseek_value(self):
        """测试 DeepSeek 值"""
        assert TranslatorType.DEEPSEEK.value == "deepseek"

    def test_openai_value(self):
        """测试 OpenAI 值"""
        assert TranslatorType.OPENAI.value == "openai"


class TestWhisperModel:
    """测试 Whisper 模型枚举"""

    def test_all_models(self):
        """测试所有模型值"""
        assert WhisperModel.TINY.value == "tiny"
        assert WhisperModel.BASE.value == "base"
        assert WhisperModel.SMALL.value == "small"
        assert WhisperModel.MEDIUM.value == "medium"
        assert WhisperModel.LARGE.value == "large"


class TestLanguage:
    """测试语言枚举"""

    def test_chinese_value(self):
        """测试中文代码"""
        assert Language.CHINESE.value == "zh"

    def test_english_value(self):
        """测试英文代码"""
        assert Language.ENGLISH.value == "en"

    def test_japanese_value(self):
        """测试日语代码"""
        assert Language.JAPANESE.value == "ja"

    def test_from_code_valid(self):
        """测试从有效代码获取语言"""
        assert Language.from_code("zh") == Language.CHINESE
        assert Language.from_code("en") == Language.ENGLISH
        assert Language.from_code("ja") == Language.JAPANESE

    def test_from_code_case_insensitive(self):
        """测试大小写不敏感"""
        assert Language.from_code("ZH") == Language.CHINESE
        assert Language.from_code("En") == Language.ENGLISH

    def test_from_code_invalid(self):
        """测试无效代码抛出异常"""
        with pytest.raises(ValueError) as exc_info:
            Language.from_code("invalid")
        assert "不支持的语言代码" in str(exc_info.value)

    def test_list_codes(self):
        """测试列出所有语言代码"""
        codes = Language.list_codes()
        assert "zh" in codes
        assert "en" in codes
        assert "ja" in codes
        assert len(codes) == len(Language)


class TestGetLanguageName:
    """测试获取语言名称函数"""

    def test_chinese_native(self):
        """测试中文本地名称"""
        assert get_language_name(Language.CHINESE) == "中文"

    def test_chinese_english(self):
        """测试中文英文名称"""
        assert get_language_name(Language.CHINESE, native=False) == "Chinese"

    def test_english_native(self):
        """测试英语本地名称"""
        assert get_language_name(Language.ENGLISH) == "English"

    def test_japanese_native(self):
        """测试日语本地名称"""
        assert get_language_name(Language.JAPANESE) == "日本語"

    def test_all_languages_have_names(self):
        """测试所有语言都有名称映射"""
        for lang in Language:
            if lang in LANGUAGE_NAMES:
                assert get_language_name(lang) is not None


class TestTranslatorConfig:
    """测试翻译器配置"""

    def test_default_values(self):
        """测试默认值"""
        config = TranslatorConfig()
        assert config.type == TranslatorType.DEEPSEEK
        assert config.temperature == 0.3
        assert config.max_tokens == 2000
        assert config.batch_size == 10
        assert config.source_language == Language.ENGLISH
        assert config.target_language == Language.CHINESE

    def test_deepseek_defaults(self):
        """测试 DeepSeek 默认配置"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK)
        assert config.base_url == "https://api.deepseek.com"
        assert config.model == "deepseek-chat"

    def test_openai_defaults(self):
        """测试 OpenAI 默认配置"""
        config = TranslatorConfig(type=TranslatorType.OPENAI)
        assert config.base_url == "https://api.openai.com/v1"
        assert config.model == "gpt-4o-mini"

    def test_custom_values(self):
        """测试自定义值"""
        config = TranslatorConfig(
            type=TranslatorType.OPENAI,
            api_key="custom-key",
            model="gpt-4",
            temperature=0.7,
            batch_size=5,
        )
        assert config.api_key == "custom-key"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.batch_size == 5

    def test_language_name_properties(self):
        """测试语言名称属性"""
        config = TranslatorConfig(
            source_language=Language.ENGLISH, target_language=Language.JAPANESE
        )
        assert config.source_language_name == "English"
        assert config.target_language_name == "日本語"

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "env-api-key"}, clear=True)
    def test_api_key_from_env(self):
        """测试从环境变量获取 API Key"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK)
        assert config.api_key == "env-api-key"


class TestTranscriberConfig:
    """测试语音识别配置"""

    def test_default_values(self):
        """测试默认值"""
        config = TranscriberConfig()
        assert config.model == WhisperModel.BASE
        assert config.language == "en"
        assert config.device is None

    def test_model_name_property(self):
        """测试模型名称属性"""
        config = TranscriberConfig(model=WhisperModel.MEDIUM)
        assert config.model_name == "medium"

    def test_custom_device(self):
        """测试自定义设备"""
        config = TranscriberConfig(device="cuda")
        assert config.device == "cuda"


class TestSubtitleConfig:
    """测试字幕配置"""

    def test_default_values(self):
        """测试默认值"""
        config = SubtitleConfig()
        assert config.target_only is False
        assert config.bilingual is True
        assert config.target_first is True

    def test_target_only_mode(self):
        """测试仅目标语言模式"""
        config = SubtitleConfig(target_only=True)
        assert config.target_only is True

    def test_source_first_bilingual(self):
        """测试源语言在前的双语模式"""
        config = SubtitleConfig(bilingual=True, target_first=False)
        assert config.bilingual is True
        assert config.target_first is False


class TestVideoConfig:
    """测试视频配置"""

    def test_default_values(self):
        """测试默认值"""
        config = VideoConfig()
        assert config.embed_subtitle is True
        assert config.soft_subtitle is True
        assert config.font_name == "PingFang SC"
        assert config.font_size == 24

    def test_hard_subtitle(self):
        """测试硬字幕配置"""
        config = VideoConfig(soft_subtitle=False)
        assert config.soft_subtitle is False

    def test_custom_font(self):
        """测试自定义字体"""
        config = VideoConfig(font_name="Arial", font_size=20)
        assert config.font_name == "Arial"
        assert config.font_size == 20


class TestConfig:
    """测试主配置类"""

    def test_default_creation(self):
        """测试默认创建"""
        config = Config()
        assert config.transcriber is not None
        assert config.translator is not None
        assert config.subtitle is not None
        assert config.video is not None
        assert config.output_dir is None

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_missing_api_key(self):
        """测试验证缺少 API Key"""
        config = Config(translator=TranslatorConfig(api_key=None))
        errors = config.validate()
        assert any("API Key" in e for e in errors)

    def test_validate_same_language(self):
        """测试验证相同源语言和目标语言"""
        config = Config(
            translator=TranslatorConfig(
                api_key="test", source_language=Language.CHINESE, target_language=Language.CHINESE
            )
        )
        errors = config.validate()
        assert any("相同" in e for e in errors)

    def test_validate_valid_config(self):
        """测试验证有效配置"""
        config = Config(
            translator=TranslatorConfig(
                api_key="test-key",
                source_language=Language.ENGLISH,
                target_language=Language.CHINESE,
            )
        )
        errors = config.validate()
        assert len(errors) == 0

    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "env-key"}, clear=True)
    def test_from_env(self):
        """测试从环境变量创建配置"""
        config = Config.from_env()
        assert config.translator.api_key == "env-key"
