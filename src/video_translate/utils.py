"""
工具函数模块
"""

import json
import logging
import sys
from typing import Any

# 设置日志
logger = logging.getLogger("video_translate")


def setup_logging(level: int = logging.INFO, log_file: str | None = None):
    """配置日志"""
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（可选）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.setLevel(level)


def format_timestamp(seconds: float) -> str:
    """将秒数转换为 SRT 时间戳格式 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_vtt_timestamp(seconds: float) -> str:
    """将秒数转换为 VTT 时间戳格式 (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def format_duration(seconds: float) -> str:
    """格式化时长为人类可读格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}小时{minutes}分{secs}秒"
    elif minutes > 0:
        return f"{minutes}分{secs}秒"
    else:
        return f"{secs}秒"


def get_device() -> str:
    """检测并返回可用的计算设备"""
    try:
        import torch
    except ImportError:
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def get_device_name(device: str) -> str:
    """获取设备的友好名称"""
    device_names = {"cuda": "NVIDIA GPU (CUDA)", "mps": "Apple Silicon GPU (MPS)", "cpu": "CPU"}
    return device_names.get(device, device)


class ProgressReporter:
    """进度报告器"""

    def __init__(self, use_emoji: bool = True, json_mode: bool = False):
        self.use_emoji = use_emoji
        self.json_mode = json_mode
        self._current_step = 0
        self._total_steps = 4
        self._step_names = {
            1: "transcribing",
            2: "translating",
            3: "generating",
            4: "embedding",
        }

    def set_json_mode(self, enabled: bool):
        """设置 JSON 模式"""
        self.json_mode = enabled

    def _emit_json(self, data: dict[str, Any]):
        """输出 JSON 格式的消息到 stdout"""
        print(json.dumps(data, ensure_ascii=False), flush=True)

    def _icon(self, emoji: str, fallback: str = "") -> str:
        return emoji if self.use_emoji else fallback

    def _print(self, message: str):
        """输出消息，在 JSON 模式下作为 log 类型"""
        if self.json_mode:
            self._emit_json({"type": "log", "level": "info", "message": message})
        else:
            print(message)

    def info(self, message: str):
        self._print(f"{self._icon('ℹ️ ')}  {message}")

    def success(self, message: str):
        self._print(f"{self._icon('✅')} {message}")

    def error(self, message: str):
        if self.json_mode:
            self._emit_json({"type": "log", "level": "error", "message": message})
        else:
            print(f"{self._icon('❌')} {message}")

    def warning(self, message: str):
        if self.json_mode:
            self._emit_json({"type": "log", "level": "warning", "message": message})
        else:
            print(f"{self._icon('⚠️ ')}  {message}")

    def step(self, step_num: int, total: int, message: str):
        self._current_step = step_num
        self._total_steps = total
        if self.json_mode:
            step_name = self._step_names.get(step_num, "processing")
            self._emit_json({
                "type": "progress",
                "step": step_num,
                "total_steps": total,
                "step_name": step_name,
                "percent": 0,
                "message": message,
            })
        else:
            print(f"{self._icon('📝')} [{step_num}/{total}] {message}")

    def progress(self, percent: int, message: str | None = None):
        """报告当前步骤的进度百分比"""
        if self.json_mode:
            step_name = self._step_names.get(self._current_step, "processing")
            self._emit_json({
                "type": "progress",
                "step": self._current_step,
                "total_steps": self._total_steps,
                "step_name": step_name,
                "percent": percent,
                "message": message,
            })

    def result(
        self,
        status: str,
        subtitle_file: str | None = None,
        output_video: str | None = None,
    ):
        """报告最终结果（仅 JSON 模式）"""
        if self.json_mode:
            self._emit_json({
                "type": "result",
                "status": status,
                "subtitle_file": subtitle_file,
                "output_video": output_video,
            })

    def emit_error(self, message: str):
        """报告错误（仅 JSON 模式）"""
        if self.json_mode:
            self._emit_json({"type": "error", "message": message})

    def loading(self, message: str):
        self._print(f"{self._icon('🎯')} {message}")

    def video(self, message: str):
        self._print(f"{self._icon('🎬')} {message}")

    def audio(self, message: str):
        self._print(f"{self._icon('🎤')} {message}")

    def translate(self, message: str):
        self._print(f"{self._icon('🌐')} {message}")

    def file(self, message: str):
        self._print(f"{self._icon('📄')} {message}")

    def device(self, message: str):
        self._print(f"{self._icon('💻')} {message}")

    def separator(self, char: str = "=", length: int = 60):
        if not self.json_mode:
            print(char * length)

    def header(self, title: str):
        if not self.json_mode:
            self.separator()
            print(f"{self._icon('🎥')} {title}")
            self.separator()


# 全局进度报告器实例
progress = ProgressReporter()
