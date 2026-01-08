"""
命令行接口模块
"""

import sys
import argparse
from pathlib import Path

from .config import (
    Config,
    TranscriberConfig,
    TranslatorConfig,
    SubtitleConfig,
    VideoConfig,
    TranslatorType,
    WhisperModel,
)
from .pipeline import TranslationPipeline
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="video-translate",
        description="视频英文字幕翻译为中文字幕工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  video-translate video.mp4
  
  # 使用更大的模型提高识别准确度
  video-translate video.mp4 --model large
  
  # 只生成字幕文件，不嵌入视频
  video-translate video.mp4 --no-embed
  
  # 生成硬字幕（烧录到视频中）
  video-translate video.mp4 --hard-sub
  
  # 只输出中文字幕（不含原文）
  video-translate video.mp4 --chinese-only
  
  # 使用 OpenAI 翻译
  video-translate video.mp4 --translator openai
"""
    )
    
    # 位置参数
    parser.add_argument(
        "video",
        help="视频文件路径"
    )
    
    # 输出选项
    parser.add_argument(
        "-o", "--output",
        help="输出目录"
    )
    
    # Whisper 选项
    parser.add_argument(
        "-m", "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper 模型大小 (默认: base)"
    )
    
    parser.add_argument(
        "--language",
        default="en",
        help="源语言 (默认: en)"
    )
    
    # 翻译选项
    parser.add_argument(
        "--translator",
        default="deepseek",
        choices=["deepseek", "openai"],
        help="翻译引擎 (默认: deepseek)"
    )
    
    parser.add_argument(
        "--api-key",
        help="翻译 API Key (也可通过环境变量设置)"
    )
    
    parser.add_argument(
        "--api-base",
        help="API Base URL (可选)"
    )
    
    parser.add_argument(
        "--llm-model",
        help="LLM 模型名称 (可选)"
    )
    
    # 字幕选项
    parser.add_argument(
        "--chinese-only",
        action="store_true",
        help="只输出中文字幕，不包含英文原文"
    )
    
    parser.add_argument(
        "--english-first",
        action="store_true",
        help="英文在上，中文在下"
    )
    
    # 视频选项
    parser.add_argument(
        "--no-embed",
        action="store_true",
        help="不将字幕嵌入视频，只生成字幕文件"
    )
    
    parser.add_argument(
        "--hard-sub",
        action="store_true",
        help="使用硬字幕（烧录到视频中）"
    )
    
    parser.add_argument(
        "--font-size",
        type=int,
        default=24,
        help="硬字幕字体大小 (默认: 24)"
    )
    
    # 其他选项
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细日志"
    )
    
    return parser


def build_config(args: argparse.Namespace) -> Config:
    """从命令行参数构建配置"""
    
    # 翻译器类型
    translator_type = TranslatorType.DEEPSEEK
    if args.translator == "openai":
        translator_type = TranslatorType.OPENAI
    
    # Whisper 模型
    whisper_model = WhisperModel(args.model)
    
    config = Config(
        transcriber=TranscriberConfig(
            model=whisper_model,
            language=args.language,
        ),
        translator=TranslatorConfig(
            type=translator_type,
            api_key=args.api_key,
            base_url=args.api_base,
            model=args.llm_model,
        ),
        subtitle=SubtitleConfig(
            chinese_only=args.chinese_only,
            bilingual=not args.chinese_only,
            chinese_first=not args.english_first,
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
            print(f"   方式2: video-translate video.mp4 --api-key 'your-api-key'")
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
