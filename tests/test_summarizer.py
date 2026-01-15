"""
总结模块测试
"""

import json
from unittest.mock import Mock, patch

from video_translate.config import (
    Language,
    TranslatorConfig,
    TranslatorType,
)
from video_translate.models import SubtitleSegment, SummaryResult, TimelineItem
from video_translate.summarizer import (
    BaseSummarizer,
    LLMSummarizer,
    create_summarizer,
)


class MockSummarizer(BaseSummarizer):
    """用于测试的模拟总结器"""

    @property
    def name(self) -> str:
        return "MockSummarizer"

    def summarize(
        self,
        segments: list[SubtitleSegment],
        language: Language | None = None,
        max_key_points: int = 5,
        include_timeline: bool = True,
        progress_callback: callable = None,
    ) -> SummaryResult:
        return SummaryResult(
            title="Mock Title",
            overview="Mock overview",
            key_points=["Point 1", "Point 2"],
            topics=["Topic 1", "Topic 2"],
            timeline=[TimelineItem(time="00:00:00", description="Start")],
            language=language.value if language else "zh",
        )


class TestSummaryResult:
    """测试 SummaryResult 数据模型"""

    def test_to_dict(self):
        """测试转换为字典"""
        result = SummaryResult(
            title="Test Title",
            overview="Test overview",
            key_points=["Point 1", "Point 2"],
            topics=["Topic 1"],
            timeline=[TimelineItem(time="00:00:00", description="Start")],
            language="zh",
        )

        data = result.to_dict()

        assert data["title"] == "Test Title"
        assert data["overview"] == "Test overview"
        assert len(data["key_points"]) == 2
        assert len(data["topics"]) == 1
        assert len(data["timeline"]) == 1
        assert data["timeline"][0]["time"] == "00:00:00"

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "title": "Test Title",
            "overview": "Test overview",
            "key_points": ["Point 1"],
            "topics": ["Topic 1", "Topic 2"],
            "timeline": [{"time": "00:01:00", "description": "Middle"}],
            "language": "en",
        }

        result = SummaryResult.from_dict(data)

        assert result.title == "Test Title"
        assert result.overview == "Test overview"
        assert len(result.key_points) == 1
        assert len(result.topics) == 2
        assert len(result.timeline) == 1
        assert result.timeline[0].time == "00:01:00"
        assert result.language == "en"

    def test_to_json(self):
        """测试转换为 JSON"""
        result = SummaryResult(
            title="Test",
            overview="Overview",
            key_points=["Point"],
            topics=["Topic"],
            timeline=[],
            language="zh",
        )

        json_str = result.to_json()
        data = json.loads(json_str)

        assert data["title"] == "Test"

    def test_from_json(self):
        """测试从 JSON 创建"""
        json_str = (
            '{"title": "From JSON", "overview": "Test", "key_points": [], '
            '"topics": [], "timeline": [], "language": "ja"}'
        )

        result = SummaryResult.from_json(json_str)

        assert result.title == "From JSON"
        assert result.language == "ja"


class TestTimelineItem:
    """测试 TimelineItem 数据模型"""

    def test_to_dict(self):
        """测试转换为字典"""
        item = TimelineItem(time="00:05:30", description="Key moment")

        data = item.to_dict()

        assert data["time"] == "00:05:30"
        assert data["description"] == "Key moment"

    def test_from_dict(self):
        """测试从字典创建"""
        data = {"time": "00:10:00", "description": "End"}

        item = TimelineItem.from_dict(data)

        assert item.time == "00:10:00"
        assert item.description == "End"


class TestLLMSummarizer:
    """测试 LLM 总结器"""

    def test_name(self):
        """测试总结器名称"""
        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK, api_key="test-key", model="deepseek-chat"
        )
        summarizer = LLMSummarizer(config)
        assert "LLM Summarizer" in summarizer.name

    def test_format_transcript(self, sample_segments):
        """测试格式化转录文本"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        summarizer = LLMSummarizer(config)

        transcript = summarizer._format_transcript(sample_segments)

        assert "[1]" in transcript
        assert "[2]" in transcript
        assert "[3]" in transcript
        # 应该包含时间戳
        assert "00:00:00" in transcript

    def test_get_system_prompt_contains_language(self):
        """测试系统提示词包含语言信息"""
        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK,
            api_key="test-key",
            target_language=Language.CHINESE,
        )
        summarizer = LLMSummarizer(config)

        prompt = summarizer._get_system_prompt(
            language=Language.CHINESE,
            max_key_points=5,
            include_timeline=True,
        )

        assert "Chinese" in prompt
        assert "JSON" in prompt

    def test_get_system_prompt_without_timeline(self):
        """测试不包含时间线的系统提示词"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        summarizer = LLMSummarizer(config)

        prompt_with_timeline = summarizer._get_system_prompt(
            language=Language.CHINESE,
            max_key_points=5,
            include_timeline=True,
        )
        prompt_without_timeline = summarizer._get_system_prompt(
            language=Language.CHINESE,
            max_key_points=5,
            include_timeline=False,
        )

        # 有时间线的应该包含 timeline 关键字
        assert "timeline" in prompt_with_timeline.lower()
        # 没有时间线的提示词中不应该有 timeline 格式说明
        assert '"timeline"' not in prompt_without_timeline

    def test_parse_response_valid_json(self):
        """测试解析有效的 JSON 响应"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        summarizer = LLMSummarizer(config)

        response = """
        {
            "title": "Video Title",
            "overview": "This is an overview",
            "key_points": ["Point 1", "Point 2"],
            "topics": ["Topic A", "Topic B"],
            "timeline": [
                {"time": "00:00:00", "description": "Start"},
                {"time": "00:05:00", "description": "End"}
            ]
        }
        """

        result = summarizer._parse_response(response, include_timeline=True)

        assert result.title == "Video Title"
        assert result.overview == "This is an overview"
        assert len(result.key_points) == 2
        assert len(result.topics) == 2
        assert len(result.timeline) == 2

    def test_parse_response_with_markdown_code_block(self):
        """测试解析带有 markdown 代码块的响应"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        summarizer = LLMSummarizer(config)

        response = """```json
        {
            "title": "Markdown Title",
            "overview": "Overview",
            "key_points": [],
            "topics": []
        }
        ```"""

        result = summarizer._parse_response(response, include_timeline=False)

        assert result.title == "Markdown Title"

    def test_parse_response_invalid_json(self):
        """测试解析无效的 JSON 响应"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        summarizer = LLMSummarizer(config)

        response = "This is not valid JSON"

        result = summarizer._parse_response(response, include_timeline=False)

        # 应该返回一个默认的结果而不是抛出异常
        assert result.title == "解析失败"

    @patch("openai.OpenAI")
    def test_summarize(self, mock_openai_class, sample_segments):
        """测试生成总结"""
        # 设置 mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "title": "Test Video",
                "overview": "A test video about testing",
                "key_points": ["Key point 1", "Key point 2"],
                "topics": ["Testing", "Development"],
                "timeline": [{"time": "00:00:00", "description": "Introduction"}],
            }
        )
        mock_client.chat.completions.create.return_value = mock_response

        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK,
            api_key="test-key",
            target_language=Language.CHINESE,
        )
        summarizer = LLMSummarizer(config)

        result = summarizer.summarize(
            sample_segments,
            language=Language.CHINESE,
            max_key_points=5,
            include_timeline=True,
        )

        assert result.title == "Test Video"
        assert len(result.key_points) == 2
        assert result.language == "zh"
        mock_client.chat.completions.create.assert_called_once()

    @patch("openai.OpenAI")
    def test_client_lazy_loading(self, mock_openai_class):
        """测试客户端延迟加载"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        summarizer = LLMSummarizer(config)

        # 客户端应该还没有被创建
        assert summarizer._client is None

        # 访问 client 属性
        _ = summarizer.client

        # 现在应该被创建了
        assert mock_openai_class.called


class TestCreateSummarizer:
    """测试总结器工厂函数"""

    def test_create_summarizer(self):
        """测试创建总结器"""
        config = TranslatorConfig(type=TranslatorType.DEEPSEEK, api_key="test-key")
        summarizer = create_summarizer(config)

        assert isinstance(summarizer, LLMSummarizer)
        assert "LLM Summarizer" in summarizer.name


class TestSummaryWithDifferentLanguages:
    """测试不同语言配置"""

    def test_summarize_in_chinese(self):
        """测试生成中文总结"""
        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK,
            api_key="test-key",
            target_language=Language.CHINESE,
        )
        summarizer = LLMSummarizer(config)

        prompt = summarizer._get_system_prompt(
            language=Language.CHINESE,
            max_key_points=5,
            include_timeline=True,
        )

        assert "Chinese" in prompt
        assert "中文" in prompt

    def test_summarize_in_japanese(self):
        """测试生成日文总结"""
        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK,
            api_key="test-key",
            target_language=Language.JAPANESE,
        )
        summarizer = LLMSummarizer(config)

        prompt = summarizer._get_system_prompt(
            language=Language.JAPANESE,
            max_key_points=5,
            include_timeline=True,
        )

        assert "Japanese" in prompt
        assert "日本語" in prompt

    def test_summarize_in_english(self):
        """测试生成英文总结"""
        config = TranslatorConfig(
            type=TranslatorType.DEEPSEEK,
            api_key="test-key",
            target_language=Language.ENGLISH,
        )
        summarizer = LLMSummarizer(config)

        prompt = summarizer._get_system_prompt(
            language=Language.ENGLISH,
            max_key_points=3,
            include_timeline=False,
        )

        assert "English" in prompt
