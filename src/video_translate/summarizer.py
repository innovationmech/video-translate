"""
视频内容总结模块 - 基于 LLM 生成结构化总结
"""

import json
from abc import ABC, abstractmethod
from collections.abc import Callable

from .config import Language, TranslatorConfig, get_language_name
from .models import SubtitleSegment, SummaryResult, TimelineItem
from .utils import format_timestamp, progress


class BaseSummarizer(ABC):
    """总结器基类"""

    def __init__(self, config: TranslatorConfig):
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """总结器名称"""
        pass

    @abstractmethod
    def summarize(
        self,
        segments: list[SubtitleSegment],
        language: Language | None = None,
        max_key_points: int = 5,
        include_timeline: bool = True,
        progress_callback: Callable[[int, str], None] | None = None,
    ) -> SummaryResult:
        """
        生成视频内容总结

        Args:
            segments: 字幕片段列表
            language: 总结语言（默认使用目标语言）
            max_key_points: 最大关键点数量
            include_timeline: 是否包含时间线
            progress_callback: 进度回调函数 (percent: int, message: str) -> None

        Returns:
            SummaryResult: 总结结果
        """
        pass


class LLMSummarizer(BaseSummarizer):
    """基于 LLM 的视频内容总结器"""

    def __init__(self, config: TranslatorConfig):
        super().__init__(config)
        self._client = None

    @property
    def name(self) -> str:
        return f"LLM Summarizer ({self.config.model})"

    @property
    def client(self):
        """获取 API 客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError("请安装 openai: pip install openai") from None

            self._client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
        return self._client

    def _format_transcript(self, segments: list[SubtitleSegment]) -> str:
        """将字幕片段格式化为转录文本"""
        lines = []
        for seg in segments:
            start_time = format_timestamp(seg.start).replace(",", ".")
            end_time = format_timestamp(seg.end).replace(",", ".")
            # 优先使用翻译后的文本，如果没有则使用原文
            text = seg.translated if seg.translated else seg.text
            lines.append(f"[{seg.index}] {start_time} - {end_time}: {text}")
        return "\n".join(lines)

    def _get_system_prompt(
        self,
        language: Language,
        max_key_points: int,
        include_timeline: bool,
    ) -> str:
        """获取系统提示词"""
        lang_name = get_language_name(language, native=False)
        lang_native = get_language_name(language, native=True)

        timeline_instruction = ""
        timeline_format = ""
        if include_timeline:
            timeline_instruction = """
5. Create a timeline with key moments and their timestamps
6. Timeline should capture the main structure/flow of the content"""
            timeline_format = """,
  "timeline": [
    {"time": "00:00:00", "description": "Opening/introduction"},
    {"time": "00:05:30", "description": "Key moment description"},
    ...
  ]"""

        return f"""You are an expert video content analyst. \
Analyze the following video transcript and provide a structured summary in {lang_name}.

Requirements:
1. Generate a concise, descriptive title for the video
2. Write a one-sentence overview that captures the main topic
3. Extract up to {max_key_points} key points/takeaways from the content
4. Identify the main topics/themes as tags{timeline_instruction}

Output your analysis in the following JSON format (respond in {lang_native}):
{{
  "title": "Video title",
  "overview": "One sentence overview of the video content",
  "key_points": [
    "Key point 1",
    "Key point 2",
    ...
  ],
  "topics": ["Topic1", "Topic2", ...]{timeline_format}
}}

IMPORTANT:
- Respond ONLY with valid JSON, no additional text
- All content must be in {lang_native}
- Key points should be concise and actionable
- Topics should be single words or short phrases
- Timeline timestamps should use format HH:MM:SS"""

    def _parse_response(self, response_text: str, include_timeline: bool) -> SummaryResult:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON 部分
            text = response_text.strip()

            # 处理可能的 markdown 代码块
            if text.startswith("```"):
                # 找到第一个换行后的内容
                start = text.find("\n") + 1
                end = text.rfind("```")
                if end > start:
                    text = text[start:end].strip()

            data = json.loads(text)

            # 解析时间线
            timeline = []
            if include_timeline and "timeline" in data:
                for item in data.get("timeline", []):
                    timeline.append(
                        TimelineItem(
                            time=item.get("time", "00:00:00"),
                            description=item.get("description", ""),
                        )
                    )

            return SummaryResult(
                title=data.get("title", "Untitled"),
                overview=data.get("overview", ""),
                key_points=data.get("key_points", []),
                topics=data.get("topics", []),
                timeline=timeline,
            )
        except json.JSONDecodeError as e:
            progress.warning(f"JSON 解析失败: {e}")
            # 返回一个基本的结果
            return SummaryResult(
                title="解析失败",
                overview=response_text[:200] if response_text else "",
                key_points=[],
                topics=[],
                timeline=[],
            )

    def summarize(
        self,
        segments: list[SubtitleSegment],
        language: Language | None = None,
        max_key_points: int = 5,
        include_timeline: bool = True,
        progress_callback: Callable[[int, str], None] | None = None,
    ) -> SummaryResult:
        """生成视频内容总结"""

        # 使用指定语言或默认使用目标语言
        summary_language = language or self.config.target_language
        lang_name = get_language_name(summary_language)

        progress.translate(f"开始使用 {self.name} 生成 {lang_name} 总结...")

        if progress_callback:
            progress_callback(10, "正在准备转录文本...")

        # 格式化转录文本
        transcript = self._format_transcript(segments)

        if progress_callback:
            progress_callback(20, "正在分析视频内容...")

        # 构建提示词
        system_prompt = self._get_system_prompt(summary_language, max_key_points, include_timeline)

        user_prompt = f"""Please analyze the following video transcript:

{transcript}"""

        if progress_callback:
            progress_callback(30, "正在调用 LLM 生成总结...")

        # 调用 LLM API
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            response_text = response.choices[0].message.content.strip()

            if progress_callback:
                progress_callback(80, "正在解析总结结果...")

            # 解析响应
            result = self._parse_response(response_text, include_timeline)
            result.language = summary_language.value

            if progress_callback:
                progress_callback(100, "总结生成完成")

            progress.success(f"总结生成完成: {result.title}")

            return result

        except Exception as e:
            progress.error(f"总结生成失败: {e}")
            raise


def create_summarizer(config: TranslatorConfig) -> BaseSummarizer:
    """
    创建总结器工厂函数

    Args:
        config: 翻译器配置（复用 API 配置）

    Returns:
        BaseSummarizer: 总结器实例
    """
    return LLMSummarizer(config)
