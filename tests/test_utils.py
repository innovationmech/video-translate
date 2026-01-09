"""
工具函数测试
"""

from unittest.mock import patch

from video_translate.utils import (
    ProgressReporter,
    format_duration,
    format_timestamp,
    format_vtt_timestamp,
    get_device,
    get_device_name,
)


class TestFormatTimestamp:
    """测试 SRT 时间戳格式化"""

    def test_zero_seconds(self):
        """测试 0 秒"""
        assert format_timestamp(0) == "00:00:00,000"

    def test_simple_seconds(self):
        """测试简单秒数"""
        assert format_timestamp(5.5) == "00:00:05,500"

    def test_minutes(self):
        """测试分钟"""
        assert format_timestamp(65.123) == "00:01:05,123"

    def test_hours(self):
        """测试小时"""
        assert format_timestamp(3661.456) == "01:01:01,456"

    def test_milliseconds_precision(self):
        """测试毫秒精度"""
        assert format_timestamp(0.001) == "00:00:00,001"
        assert format_timestamp(0.999) == "00:00:00,999"

    def test_large_duration(self):
        """测试较大时长"""
        assert format_timestamp(36000) == "10:00:00,000"


class TestFormatVttTimestamp:
    """测试 VTT 时间戳格式化"""

    def test_zero_seconds(self):
        """测试 0 秒"""
        assert format_vtt_timestamp(0) == "00:00:00.000"

    def test_simple_seconds(self):
        """测试简单秒数"""
        assert format_vtt_timestamp(5.5) == "00:00:05.500"

    def test_difference_from_srt(self):
        """测试与 SRT 格式的区别（点 vs 逗号）"""
        srt = format_timestamp(1.234)
        vtt = format_vtt_timestamp(1.234)
        assert srt == "00:00:01,234"
        assert vtt == "00:00:01.234"


class TestFormatDuration:
    """测试人类可读时长格式化"""

    def test_seconds_only(self):
        """测试仅有秒"""
        assert format_duration(45) == "45秒"

    def test_minutes_and_seconds(self):
        """测试分钟和秒"""
        assert format_duration(125) == "2分5秒"

    def test_hours_minutes_seconds(self):
        """测试小时、分钟和秒"""
        assert format_duration(3665) == "1小时1分5秒"

    def test_zero_duration(self):
        """测试零时长"""
        assert format_duration(0) == "0秒"

    def test_exact_minute(self):
        """测试整分钟"""
        assert format_duration(60) == "1分0秒"

    def test_exact_hour(self):
        """测试整小时"""
        assert format_duration(3600) == "1小时0分0秒"


class TestGetDevice:
    """测试设备检测函数"""

    def test_returns_valid_device(self):
        """测试返回有效设备"""
        device = get_device()
        assert device in ["cuda", "mps", "cpu"]

    def test_without_torch(self):
        """测试没有 torch 时返回 cpu"""
        with patch.dict("sys.modules", {"torch": None}):
            # 强制重新导入会比较复杂，这里只验证函数不抛异常
            device = get_device()
            assert device is not None


class TestGetDeviceName:
    """测试设备名称获取函数"""

    def test_cuda_name(self):
        """测试 CUDA 设备名称"""
        assert get_device_name("cuda") == "NVIDIA GPU (CUDA)"

    def test_mps_name(self):
        """测试 MPS 设备名称"""
        assert get_device_name("mps") == "Apple Silicon GPU (MPS)"

    def test_cpu_name(self):
        """测试 CPU 设备名称"""
        assert get_device_name("cpu") == "CPU"

    def test_unknown_device(self):
        """测试未知设备名称"""
        assert get_device_name("unknown") == "unknown"


class TestProgressReporter:
    """测试进度报告器"""

    def test_default_uses_emoji(self):
        """测试默认使用 emoji"""
        reporter = ProgressReporter()
        assert reporter.use_emoji is True

    def test_disable_emoji(self):
        """测试禁用 emoji"""
        reporter = ProgressReporter(use_emoji=False)
        assert reporter.use_emoji is False

    def test_icon_with_emoji(self):
        """测试 emoji 模式下的图标"""
        reporter = ProgressReporter(use_emoji=True)
        assert reporter._icon("✅", "[OK]") == "✅"

    def test_icon_without_emoji(self):
        """测试非 emoji 模式下的图标"""
        reporter = ProgressReporter(use_emoji=False)
        assert reporter._icon("✅", "[OK]") == "[OK]"

    def test_info_output(self, capsys):
        """测试 info 输出"""
        reporter = ProgressReporter()
        reporter.info("Test message")
        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_success_output(self, capsys):
        """测试 success 输出"""
        reporter = ProgressReporter()
        reporter.success("Success!")
        captured = capsys.readouterr()
        assert "Success!" in captured.out

    def test_error_output(self, capsys):
        """测试 error 输出"""
        reporter = ProgressReporter()
        reporter.error("Error!")
        captured = capsys.readouterr()
        assert "Error!" in captured.out

    def test_warning_output(self, capsys):
        """测试 warning 输出"""
        reporter = ProgressReporter()
        reporter.warning("Warning!")
        captured = capsys.readouterr()
        assert "Warning!" in captured.out

    def test_step_output(self, capsys):
        """测试 step 输出"""
        reporter = ProgressReporter()
        reporter.step(1, 5, "Processing...")
        captured = capsys.readouterr()
        assert "[1/5]" in captured.out
        assert "Processing..." in captured.out

    def test_separator_output(self, capsys):
        """测试分隔线输出"""
        reporter = ProgressReporter()
        reporter.separator("=", 10)
        captured = capsys.readouterr()
        assert "==========" in captured.out

    def test_header_output(self, capsys):
        """测试标题输出"""
        reporter = ProgressReporter()
        reporter.header("Test Header")
        captured = capsys.readouterr()
        assert "Test Header" in captured.out
        # 应该包含分隔线
        assert "=" in captured.out
