"""
翻译模块 - 支持多种翻译引擎和多语言翻译
"""

from abc import ABC, abstractmethod

from .config import Language, TranslatorConfig, TranslatorType, get_language_name
from .models import SubtitleSegment, TranslationResult
from .utils import progress


class BaseTranslator(ABC):
    """翻译器基类"""

    def __init__(self, config: TranslatorConfig):
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """翻译器名称"""
        pass

    @property
    def source_lang(self) -> Language:
        """源语言"""
        return self.config.source_language

    @property
    def target_lang(self) -> Language:
        """目标语言"""
        return self.config.target_language

    @property
    def source_lang_name(self) -> str:
        """源语言名称"""
        return get_language_name(self.source_lang)

    @property
    def target_lang_name(self) -> str:
        """目标语言名称"""
        return get_language_name(self.target_lang)

    @abstractmethod
    def translate_text(self, text: str, context: str = "") -> str:
        """翻译单个文本"""
        pass

    @abstractmethod
    def translate_batch(self, texts: list[str]) -> list[str]:
        """批量翻译文本"""
        pass

    def translate_segments(
        self,
        segments: list[SubtitleSegment],
    ) -> TranslationResult:
        """
        翻译字幕片段

        Args:
            segments: 字幕片段列表

        Returns:
            TranslationResult: 翻译结果
        """
        batch_size = self.config.batch_size
        total = len(segments)

        progress.translate(
            f"开始使用 {self.name} 翻译 {total} 个字幕片段 "
            f"({self.source_lang_name} → {self.target_lang_name})..."
        )

        # 批量翻译
        for i in range(0, total, batch_size):
            batch = segments[i : i + batch_size]
            batch_text = "\n".join([f"[{seg.index}] {seg.text}" for seg in batch])

            progress.step(
                min(i + batch_size, total),
                total,
                f"翻译第 {i+1}-{min(i+batch_size, total)} 个片段...",
            )

            translated = self._translate_batch_with_index(batch_text)
            self._parse_and_assign(batch, translated)

        # 检查并重新翻译失败的片段
        for seg in segments:
            if not seg.translated:
                progress.warning(f"重新翻译第 {seg.index} 个片段...")
                seg.translated = self.translate_text(seg.text)

        progress.success("翻译完成")

        return TranslationResult(
            segments=segments,
            source_language=self.source_lang.value,
            target_language=self.target_lang.value,
            translator=self.name,
        )

    def _translate_batch_with_index(self, batch_text: str) -> str:
        """带编号的批量翻译"""
        return self.translate_text(batch_text)

    def _parse_and_assign(self, batch: list[SubtitleSegment], translated_text: str):
        """解析翻译结果并分配给对应片段"""
        for line in translated_text.split("\n"):
            line = line.strip()
            if not line or not line.startswith("["):
                continue

            try:
                bracket_end = line.index("]")
                idx = int(line[1:bracket_end])
                translation = line[bracket_end + 1 :].strip()

                for seg in batch:
                    if seg.index == idx:
                        seg.translated = translation
                        break
            except (ValueError, IndexError):
                continue


class OpenAICompatibleTranslator(BaseTranslator):
    """OpenAI 兼容 API 翻译器（支持 DeepSeek、OpenAI 等）"""

    def __init__(self, config: TranslatorConfig):
        super().__init__(config)
        self._client = None

    @property
    def name(self) -> str:
        if self.config.type == TranslatorType.DEEPSEEK:
            return f"DeepSeek ({self.config.model})"
        elif self.config.type == TranslatorType.OPENAI:
            return f"OpenAI ({self.config.model})"
        return f"{self.config.type.value} ({self.config.model})"

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

    def _get_system_prompt(self, for_batch: bool = False) -> str:
        """获取系统提示词，支持多语言"""
        source_name = get_language_name(self.source_lang, native=False)
        target_name = get_language_name(self.target_lang, native=False)
        target_native = get_language_name(self.target_lang, native=True)

        base_prompt = f"""You are a professional video subtitle translator. \
Please translate from {source_name} to {target_name}.

Requirements:
1. The translation should be natural and fluent, conforming to {target_native} expression habits
2. Maintain the tone and style of the original text
3. Technical terms can be kept in the original language or annotated in parentheses"""

        if for_batch:
            base_prompt += """
4. Each line format: [number] translated content
5. Maintain the original numbering order"""
        else:
            base_prompt += "\n4. Only output the translation result, do not add any explanation"

        return base_prompt

    def translate_text(self, text: str, context: str = "") -> str:
        """翻译单个文本"""
        target_name = get_language_name(self.target_lang, native=False)

        user_prompt = f"Please translate the following subtitle to {target_name}:\n\n{text}"
        if context:
            user_prompt = f"Context: {context}\n\n{user_prompt}"

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt(for_batch=False)},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return response.choices[0].message.content.strip()

    def translate_batch(self, texts: list[str]) -> list[str]:
        """批量翻译文本"""
        target_name = get_language_name(self.target_lang, native=False)
        batch_text = "\n".join([f"[{i+1}] {text}" for i, text in enumerate(texts)])

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt(for_batch=True)},
                {
                    "role": "user",
                    "content": (
                        f"Please translate the following subtitles to {target_name}:"
                        f"\n\n{batch_text}"
                    ),
                },
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        translated_text = response.choices[0].message.content.strip()

        # 解析结果
        results = [""] * len(texts)
        for line in translated_text.split("\n"):
            line = line.strip()
            if line.startswith("["):
                try:
                    bracket_end = line.index("]")
                    idx = int(line[1:bracket_end]) - 1
                    if 0 <= idx < len(results):
                        results[idx] = line[bracket_end + 1 :].strip()
                except (ValueError, IndexError):
                    continue

        return results

    def _translate_batch_with_index(self, batch_text: str) -> str:
        """带编号的批量翻译"""
        target_name = get_language_name(self.target_lang, native=False)

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt(for_batch=True)},
                {
                    "role": "user",
                    "content": (
                        f"Please translate the following subtitles to {target_name}:"
                        f"\n\n{batch_text}"
                    ),
                },
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return response.choices[0].message.content.strip()


def create_translator(config: TranslatorConfig) -> BaseTranslator:
    """
    创建翻译器工厂函数

    Args:
        config: 翻译器配置

    Returns:
        BaseTranslator: 翻译器实例
    """
    if config.type in [TranslatorType.DEEPSEEK, TranslatorType.OPENAI]:
        return OpenAICompatibleTranslator(config)
    else:
        raise ValueError(f"不支持的翻译器类型: {config.type}")
