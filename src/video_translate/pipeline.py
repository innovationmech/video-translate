"""
处理流水线模块 - 整合各模块完成视频翻译
"""

from pathlib import Path

from .config import Config, get_language_name
from .models import SubtitleSegment
from .subtitle import SubtitleWriter
from .transcriber import Transcriber
from .translator import create_translator
from .utils import progress
from .video import VideoProcessor


class TranslationPipeline:
    """视频翻译处理流水线"""

    def __init__(self, config: Config, json_mode: bool = False):
        self.config = config
        self.json_mode = json_mode
        self._transcriber: Transcriber | None = None
        self._translator = None
        self._subtitle_writer: SubtitleWriter | None = None
        self._video_processor: VideoProcessor | None = None

    @property
    def transcriber(self) -> Transcriber:
        if self._transcriber is None:
            self._transcriber = Transcriber(self.config.transcriber)
        return self._transcriber

    @property
    def translator(self):
        if self._translator is None:
            self._translator = create_translator(self.config.translator)
        return self._translator

    @property
    def subtitle_writer(self) -> SubtitleWriter:
        if self._subtitle_writer is None:
            self._subtitle_writer = SubtitleWriter(self.config.subtitle)
        return self._subtitle_writer

    @property
    def video_processor(self) -> VideoProcessor:
        if self._video_processor is None:
            self._video_processor = VideoProcessor(self.config.video)
        return self._video_processor

    def _get_output_suffix(self) -> str:
        """获取输出文件的后缀标识"""
        target_lang = self.config.translator.target_language.value
        return f"_{target_lang}"

    def process(self, video_path: str | Path, output_dir: str | Path | None = None) -> dict:
        """
        处理视频的完整流水线

        Args:
            video_path: 视频文件路径
            output_dir: 输出目录（默认与视频同目录）

        Returns:
            dict: 包含输出文件路径的字典
        """
        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        # 设置输出目录
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = self.config.output_dir or video_path.parent

        # 生成输出文件名（使用目标语言代码作为后缀）
        base_name = video_path.stem
        suffix = self._get_output_suffix()
        srt_path = output_dir / f"{base_name}{suffix}.srt"
        video_output_path = output_dir / f"{base_name}{suffix}{video_path.suffix}"

        # 打印处理信息
        self._print_header(video_path, output_dir)

        result = {
            "input_video": video_path,
            "subtitle_file": None,
            "output_video": None,
        }

        # 步骤 1: 语音识别
        progress.step(1, 4, "语音识别")
        progress.progress(0, "正在加载 Whisper 模型...")
        progress.progress(10, "正在提取音频...")
        transcription = self.transcriber.transcribe(video_path)
        segments = transcription.segments
        progress.progress(100, f"识别到 {len(segments)} 条字幕")

        # 步骤 2: 翻译
        progress.step(2, 4, "翻译字幕")
        progress.progress(0, "正在初始化翻译引擎...")
        translation = self.translator.translate_segments(
            segments,
            progress_callback=lambda p, m: progress.progress(p, m) if self.json_mode else None,
        )
        segments = translation.segments
        progress.progress(100, "翻译完成")

        # 步骤 3: 生成字幕文件
        progress.step(3, 4, "生成字幕文件")
        progress.progress(0, "正在写入字幕文件...")
        self.subtitle_writer.write(segments, srt_path)
        result["subtitle_file"] = srt_path
        progress.progress(100, f"字幕文件已保存: {srt_path.name}")

        # 步骤 4: 嵌入字幕（可选）
        progress.step(4, 4, "嵌入字幕" if self.config.video.embed_subtitle else "跳过字幕嵌入")
        if self.config.video.embed_subtitle:
            progress.progress(0, "正在嵌入字幕到视频...")
            self.video_processor.embed_subtitle(video_path, srt_path, video_output_path)
            result["output_video"] = video_output_path
            progress.progress(100, f"视频已保存: {video_output_path.name}")
        else:
            progress.progress(100, "已跳过字幕嵌入")

        # 打印完成信息
        self._print_footer(result)

        return result

    def transcribe_only(self, video_path: str | Path) -> list[SubtitleSegment]:
        """只进行语音识别"""
        return self.transcriber.transcribe(video_path).segments

    def translate_only(self, segments: list[SubtitleSegment]) -> list[SubtitleSegment]:
        """只进行翻译"""
        return self.translator.translate_segments(segments).segments

    def _print_header(self, video_path: Path, output_dir: Path):
        """打印处理头信息"""
        if self.json_mode:
            return  # JSON 模式下不打印头信息

        source_lang = get_language_name(self.config.translator.source_language)
        target_lang = get_language_name(self.config.translator.target_language)

        progress.separator()
        progress.header("视频翻译工具")
        print(f"📁 输入视频: {video_path}")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 Whisper 模型: {self.config.transcriber.model_name}")
        print(f"🌐 翻译引擎: {self.translator.name}")
        print(f"🔤 翻译方向: {source_lang} → {target_lang}")
        progress.separator()
        print()

    def _print_footer(self, result: dict):
        """打印完成信息"""
        if self.json_mode:
            return  # JSON 模式下不打印尾信息

        print()
        progress.separator()
        progress.success("处理完成!")
        progress.separator()

        if result.get("subtitle_file"):
            print(f"📄 字幕文件: {result['subtitle_file']}")

        if result.get("output_video"):
            print(f"🎬 输出视频: {result['output_video']}")

        progress.separator()
        print()
