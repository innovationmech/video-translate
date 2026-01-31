"""
包入口点 - 支持 python -m video_translate 方式运行
"""

try:
    from .cli import main
except ImportError:  # Fallback for frozen/entry-script execution
    from video_translate.cli import main

if __name__ == "__main__":
    main()
