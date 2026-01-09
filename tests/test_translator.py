"""
翻译模块测试
"""

from unittest.mock import Mock, patch

from video_translate.config import (
    Language,
    TranslatorConfig,
    TranslatorType,
)
from video_translate.models import SubtitleSegment
from video_translate.translator import (
    BaseTranslator,
    OpenAICompatibleTranslator,
    create_translator,
)


class MockTranslator(BaseTranslator):
    """用于测试的模拟翻译器"""

    @property
    def name(self) -> str:
        return "MockTranslator"

    def translate_text(self, text: str, context: str = "") -> str:
        return f"[翻译] {text}"

    def translate_batch(self, texts: list[str]) -> list[str]:
        return [f"[翻译] {t}" for t in texts]


class TestBaseTranslator:
    """测试翻译器基类"""

    def test_source_lang_property(self, default_translator_config):
        """测试源语言属性"""
        translator = MockTranslator(default_translator_config)
        assert translator.source_lang == Language.ENGLISH

    def test_target_lang_property(self, default_translator_config):
        """测试目标语言属性"""
        translator = MockTranslator(default_translator_config)
        assert translator.target_lang == Language.CHINESE

    def test_source_lang_name(self, default_translator_config):
        """测试源语言名称"""
        translator = MockTranslator(default_translator_config)
        assert translator.source_lang_name == "English"

    def test_target_lang_name(self, default_translator_config):
        """测试目标语言名称"""
        translator = MockTranslator(default_translator_config)
        assert translator.target_lang_name == "中文"

    def test_translate_segments(self, default_translator_config):
        """测试翻译字幕片段"""
        translator = MockTranslator(default_translator_config)
        segments = [
            SubtitleSegment(index=1, start=0.0, end=2.0, text="Hello"),
            SubtitleSegment(index=2, start=2.0, end=4.0, text="World"),
        ]

        result = translator.translate_segments(segments)

        assert result.source_language == "en"
        assert result.target_language == "zh"
        assert result.translator == "MockTranslator"

    def test_parse_and_assign(self, default_translator_config):
        """测试解析和分配翻译结果"""
        translator = MockTranslator(default_translator_config)
        segments = [
            SubtitleSegment(index=1, start=0.0, end=2.0, text="Hello"),
            SubtitleSegment(index=2, start=2.0, end=4.0, text="World"),
        ]

        translated_text = "[1] 你好\n[2] 世界"
        translator._parse_and_assign(segments, translated_text)

        assert segments[0].translated == "你好"
        assert segments[1].translated == "世界"

    def test_parse_and_assign_invalid_format(self, default_translator_config):
        """测试解析无效格式"""
        translator = MockTranslator(default_translator_config)
        segments = [
            SubtitleSegment(index=1, start=0.0, end=2.0, text="Hello"),
        ]

        # 无效格式应该被跳过
        translated_text = "Invalid format\nNo brackets here"
        translator._parse_and_assign(segments, translated_text)

        assert segments[0].translated == ""  # 未被赋值


class TestOpenAICompatibleTranslator:
    """测试 OpenAI 兼容翻译器"""

    def test_name_deepseek(self):
        """测试 DeepSeek 翻译器名称"""
        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK, api_key="test-key", model="deepseek-chat"
        )
        translator = OpenAICompatibleTranslator(config)
        assert "DeepSeek" in translator.name

    def test_name_openai(self):
        """测试 OpenAI 翻译器名称"""
        config = TranslatorConfig(
            type=TranslatorType.OPENAI, api_key="test-key", model="gpt-4o-mini"
        )
        translator = OpenAICompatibleTranslator(config)
        assert "OpenAI" in translator.name

    def test_system_prompt_contains_languages(self):
        """测试系统提示词包含语言信息"""
        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK,
            api_key="test-key",
            source_language=Language.ENGLISH,
            target_language=Language.JAPANESE,
        )
        translator = OpenAICompatibleTranslator(config)

        prompt = translator._get_system_prompt(for_batch=False)
        assert "English" in prompt
        assert "Japanese" in prompt

    def test_system_prompt_batch_mode(self):
        """测试批量模式系统提示词"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        translator = OpenAICompatibleTranslator(config)

        translator._get_system_prompt(for_batch=False)
        prompt_batch = translator._get_system_prompt(for_batch=True)

        # 批量模式应该包含编号要求
        assert "number" in prompt_batch.lower()
        assert "numbering" in prompt_batch.lower() or "number" in prompt_batch.lower()

    @patch("openai.OpenAI")
    def test_translate_text(self, mock_openai_class):
        """测试翻译单个文本"""
        # 设置 mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "你好"
        mock_client.chat.completions.create.return_value = mock_response

        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        translator = OpenAICompatibleTranslator(config)

        result = translator.translate_text("Hello")

        assert result == "你好"
        mock_client.chat.completions.create.assert_called_once()

    @patch("openai.OpenAI")
    def test_translate_batch(self, mock_openai_class):
        """测试批量翻译"""
        # 设置 mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "[1] 你好\n[2] 世界"
        mock_client.chat.completions.create.return_value = mock_response

        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        translator = OpenAICompatibleTranslator(config)

        results = translator.translate_batch(["Hello", "World"])

        assert len(results) == 2
        assert results[0] == "你好"
        assert results[1] == "世界"

    @patch("openai.OpenAI")
    def test_client_lazy_loading(self, mock_openai_class):
        """测试客户端延迟加载"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        translator = OpenAICompatibleTranslator(config)

        # 客户端应该还没有被创建
        assert translator._client is None

        # 访问 client 属性
        _ = translator.client

        # 现在应该被创建了
        assert mock_openai_class.called


class TestCreateTranslator:
    """测试翻译器工厂函数"""

    def test_create_deepseek_translator(self):
        """测试创建 DeepSeek 翻译器"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        translator = create_translator(config)

        assert isinstance(translator, OpenAICompatibleTranslator)
        assert "DeepSeek" in translator.name

    def test_create_openai_translator(self):
        """测试创建 OpenAI 翻译器"""
        config = TranslatorConfig(type=TranslatorType.OPENAI, api_key="test-key")
        translator = create_translator(config)

        assert isinstance(translator, OpenAICompatibleTranslator)
        assert "OpenAI" in translator.name


class TestTranslationWithDifferentLanguages:
    """测试不同语言配置"""

    def test_english_to_chinese(self):
        """测试英语到中文"""
        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK,
            api_key="test-key",
            source_language=Language.ENGLISH,
            target_language=Language.CHINESE,
        )
        translator = OpenAICompatibleTranslator(config)

        prompt = translator._get_system_prompt()
        assert "English" in prompt
        assert "Chinese" in prompt

    def test_chinese_to_japanese(self):
        """测试中文到日语"""
        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK,
            api_key="test-key",
            source_language=Language.CHINESE,
            target_language=Language.JAPANESE,
        )
        translator = OpenAICompatibleTranslator(config)

        prompt = translator._get_system_prompt()
        assert "Chinese" in prompt
        assert "Japanese" in prompt

    def test_french_to_german(self):
        """测试法语到德语"""
        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK,
            api_key="test-key",
            source_language=Language.FRENCH,
            target_language=Language.GERMAN,
        )
        translator = OpenAICompatibleTranslator(config)

        prompt = translator._get_system_prompt()
        assert "French" in prompt
        assert "German" in prompt
