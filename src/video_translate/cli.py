"""
命令行接口模块
"""

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import (
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
from .pipeline import TranslationPipeline

# 支持的语言代码列表
SUPPORTED_LANGUAGES = Language.list_codes()


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""

    # 生成支持的语言列表字符串
    lang_help = "支持的语言: " + ", ".join(
        [f"{lang.value}({get_language_name(lang)})" for lang in Language]
    )

    parser = argparse.ArgumentParser(
        prog="video-translate",
        description="视频字幕翻译工具 - 支持多语言翻译",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
示例:
  # 英文翻译成中文（默认）
  video-translate video.mp4

  # 日语翻译成中文
  video-translate video.mp4 --source ja --target zh

  # 英文翻译成日语
  video-translate video.mp4 --source en --target ja

  # 中文翻译成英文
  video-translate video.mp4 --source zh --target en

  # 使用更大的模型提高识别准确度
  video-translate video.mp4 --model large

  # 只生成字幕文件，不嵌入视频
  video-translate video.mp4 --no-embed

  # 只输出目标语言字幕（不含原文）
  video-translate video.mp4 --target-only

  # 使用 OpenAI 翻译
  video-translate video.mp4 --translator openai

{lang_help}
""",
    )

    # 位置参数
    parser.add_argument("video", help="视频文件路径")

    # 输出选项
    parser.add_argument("-o", "--output", help="输出目录")

    # 语言选项
    parser.add_argument(
        "-s", "--source", default="en", metavar="LANG", help="源语言代码 (默认: en)"
    )

    parser.add_argument(
        "-t", "--target", default="zh", metavar="LANG", help="目标语言代码 (默认: zh)"
    )

    parser.add_argument("--list-languages", action="store_true", help="列出所有支持的语言")

    # Whisper 选项
    parser.add_argument(
        "-m",
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper 模型大小 (默认: base)",
    )

    # 翻译选项
    parser.add_argument(
        "--translator",
        default="deepseek",
        choices=["deepseek", "openai"],
        help="翻译引擎 (默认: deepseek)",
    )

    parser.add_argument("--api-key", help="翻译 API Key (也可通过环境变量设置)")

    parser.add_argument("--api-base", help="API Base URL (可选)")

    parser.add_argument("--llm-model", help="LLM 模型名称 (可选)")

    # 字幕选项
    parser.add_argument("--target-only", action="store_true", help="只输出目标语言字幕，不包含原文")

    parser.add_argument("--source-first", action="store_true", help="源语言在上，目标语言在下")

    # 兼容旧选项
    parser.add_argument(
        "--chinese-only", action="store_true", help="(已废弃，请使用 --target-only) 只输出中文字幕"
    )

    parser.add_argument(
        "--english-first", action="store_true", help="(已废弃，请使用 --source-first) 英文在上"
    )

    # 视频选项
    parser.add_argument("--no-embed", action="store_true", help="不将字幕嵌入视频，只生成字幕文件")

    parser.add_argument("--hard-sub", action="store_true", help="使用硬字幕（烧录到视频中）")

    parser.add_argument("--font-size", type=int, default=24, help="硬字幕字体大小 (默认: 24)")

    # 其他选项
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    parser.add_argument("--verbose", action="store_true", help="显示详细日志")

    return parser


def list_languages():
    """列出所有支持的语言"""
    print("支持的语言:\n")
    print(f"{'代码':<8} {'语言名称':<15} {'English Name':<15}")
    print("-" * 40)
    for lang in Language:
        native_name = get_language_name(lang, native=True)
        english_name = get_language_name(lang, native=False)
        print(f"{lang.value:<8} {native_name:<15} {english_name:<15}")
    print()


def parse_language(code: str) -> Language:
    """解析语言代码"""
    try:
        return Language.from_code(code)
    except ValueError:
        print(f"❌ 不支持的语言代码: {code}")
        print("💡 使用 --list-languages 查看支持的语言")
        sys.exit(1)


def build_config(args: argparse.Namespace) -> Config:
    """从命令行参数构建配置"""

    # 翻译器类型
    translator_type = TranslatorType.DEEPSEEK
    if args.translator == "openai":
        translator_type = TranslatorType.OPENAI

    # Whisper 模型
    whisper_model = WhisperModel(args.model)

    # 解析语言
    source_lang = parse_language(args.source)
    target_lang = parse_language(args.target)

    # 处理兼容性选项
    target_only = args.target_only or args.chinese_only
    source_first = args.source_first or args.english_first

    config = Config(
        transcriber=TranscriberConfig(
            model=whisper_model,
            language=args.source,  # Whisper 使用源语言
        ),
        translator=TranslatorConfig(
            type=translator_type,
            api_key=args.api_key,
            base_url=args.api_base,
            model=args.llm_model,
            source_language=source_lang,
            target_language=target_lang,
        ),
        subtitle=SubtitleConfig(
            target_only=target_only,
            bilingual=not target_only,
            target_first=not source_first,
        ),
        video=VideoConfig(
            embed_subtitle=not args.no_embed,
            soft_subtitle=not args.hard_sub,
            font_size=args.font_size,
        ),
        output_dir=Path(args.output) if args.output else None,
    )

    return config


def main(argv: list[str] = None):
    """命令行入口函数"""
    parser = create_parser()
    args = parser.parse_args(argv)

    # 处理 --list-languages 选项
    if args.list_languages:
        list_languages()
        sys.exit(0)

    # 构建配置
    config = build_config(args)

    # 验证配置
    errors = config.validate()
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"   - {error}")
        print()

        if not config.translator.api_key:
            translator_type = config.translator.type.value.upper()
            print(f"💡 请设置 {translator_type} API Key:")
            print(f"   方式1: export {translator_type}_API_KEY='your-api-key'")
            print("   方式2: video-translate video.mp4 --api-key 'your-api-key'")
            print()

            if config.translator.type == TranslatorType.DEEPSEEK:
                print("🔗 获取 API Key: https://platform.deepseek.com/")
            elif config.translator.type == TranslatorType.OPENAI:
                print("🔗 获取 API Key: https://platform.openai.com/")

        sys.exit(1)

    # 检查视频文件
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"❌ 视频文件不存在: {video_path}")
        sys.exit(1)

    # 运行处理流水线
    try:
        pipeline = TranslationPipeline(config)
        pipeline.process(video_path)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
