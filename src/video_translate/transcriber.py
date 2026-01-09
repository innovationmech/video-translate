"""
语音识别模块 - 使用 Whisper 进行语音识别
"""

from pathlib import Path

from .config import TranscriberConfig
from .models import SubtitleSegment, TranscriptionResult
from .utils import get_device, get_device_name, progress


class Transcriber:
    """Whisper 语音识别器"""

    def __init__(self, config: TranscriberConfig | None = None):
        self.config = config or TranscriberConfig()
        self._model = None
        self._device = None

    @property
    def device(self) -> str:
        """获取计算设备"""
        if self._device is None:
            self._device = self.config.device or get_device()
        return self._device

    def _load_model(self):
        """加载 Whisper 模型"""
        if self._model is not None:
            return

        try:
            import whisper
        except ImportError:
            raise ImportError("请安装 openai-whisper: pip install openai-whisper") from None

        progress.loading(f"加载 Whisper 模型: {self.config.model_name}")
        progress.device(f"使用设备: {get_device_name(self.device)}")

        self._model = whisper.load_model(self.config.model_name, device=self.device)

    def transcribe(self, video_path: str | Path) -> TranscriptionResult:
        """
        识别视频/音频中的语音

        Args:
            video_path: 视频或音频文件路径

        Returns:
            TranscriptionResult: 识别结果
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"文件不存在: {video_path}")

        self._load_model()

        progress.audio("正在识别视频中的语音...")

        # FP16 只在 CUDA 上支持
        fp16 = self.device == "cuda"

        result = self._model.transcribe(
            str(video_path),
            language=self.config.language,
            task="transcribe",
            verbose=False,
            fp16=fp16,
        )

        # 转换为 SubtitleSegment 列表
        segments = []
        for i, seg in enumerate(result["segments"], 1):
            segment = SubtitleSegment(
                index=i, start=seg["start"], end=seg["end"], text=seg["text"].strip()
            )
            segments.append(segment)

        # 计算总时长
        duration = segments[-1].end if segments else 0.0

        progress.success(f"识别完成，共 {len(segments)} 个字幕片段")

        return TranscriptionResult(
            segments=segments,
            language=result.get("language", self.config.language),
            duration=duration,
        )

    def unload_model(self):
        """卸载模型释放内存"""
        self._model = None

        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
