#!/usr/bin/env bash
#
# 项目设置脚本 - 初始化开发环境
#

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

step() {
    echo -e "\n${CYAN}==>${NC} $1"
}

# 检测操作系统
detect_os() {
    case "$(uname -s)" in
        Darwin*)    OS="macos" ;;
        Linux*)     OS="linux" ;;
        MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
        *)          OS="unknown" ;;
    esac
    info "检测到操作系统: $OS"
}

# 检查 uv 是否安装
check_uv() {
    step "检查 uv 包管理器"
    
    if command -v uv &> /dev/null; then
        success "uv 已安装: $(uv --version)"
        return 0
    fi
    
    warn "uv 未安装"
    echo ""
    read -p "是否自动安装 uv? [Y/n] " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        error "请手动安装 uv: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
    
    info "正在安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # 刷新 PATH
    export PATH="$HOME/.local/bin:$PATH"
    
    if command -v uv &> /dev/null; then
        success "uv 安装成功: $(uv --version)"
    else
        error "uv 安装失败，请手动安装"
        exit 1
    fi
}

# 检查 FFmpeg 是否安装
check_ffmpeg() {
    step "检查 FFmpeg"
    
    if command -v ffmpeg &> /dev/null; then
        local version
        version=$(ffmpeg -version 2>&1 | head -n1)
        success "FFmpeg 已安装: $version"
        return 0
    fi
    
    warn "FFmpeg 未安装"
    echo ""
    echo "FFmpeg 是处理视频的必要依赖，请安装："
    echo ""
    
    case "$OS" in
        macos)
            echo "  brew install ffmpeg"
            echo ""
            read -p "是否使用 Homebrew 自动安装? [Y/n] " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                if command -v brew &> /dev/null; then
                    info "正在安装 FFmpeg..."
                    brew install ffmpeg
                    success "FFmpeg 安装成功"
                else
                    error "未检测到 Homebrew，请先安装: https://brew.sh"
                fi
            fi
            ;;
        linux)
            echo "  Ubuntu/Debian: sudo apt install ffmpeg"
            echo "  Fedora:        sudo dnf install ffmpeg"
            echo "  Arch:          sudo pacman -S ffmpeg"
            ;;
        windows)
            echo "  下载: https://ffmpeg.org/download.html"
            echo "  或使用 winget: winget install ffmpeg"
            ;;
        *)
            echo "  请访问: https://ffmpeg.org/download.html"
            ;;
    esac
}

# 安装 Python 依赖
install_dependencies() {
    step "安装 Python 依赖"
    
    cd "$PROJECT_ROOT"
    
    info "同步项目依赖..."
    uv sync --dev
    
    success "依赖安装完成"
}

# 检查 API Key 配置
check_api_key() {
    step "检查 API Key 配置"
    
    local has_key=false
    
    if [[ -n "${DEEPSEEK_API_KEY:-}" ]]; then
        success "DEEPSEEK_API_KEY 已配置"
        has_key=true
    fi
    
    if [[ -n "${OPENAI_API_KEY:-}" ]]; then
        success "OPENAI_API_KEY 已配置"
        has_key=true
    fi
    
    if [[ "$has_key" == "false" ]]; then
        warn "未检测到 API Key 环境变量"
        echo ""
        echo "请设置以下环境变量之一："
        echo ""
        echo "  DeepSeek (推荐，性价比高):"
        echo "    export DEEPSEEK_API_KEY='your-api-key'"
        echo "    获取地址: https://platform.deepseek.com/"
        echo ""
        echo "  OpenAI:"
        echo "    export OPENAI_API_KEY='your-api-key'"
        echo "    获取地址: https://platform.openai.com/"
        echo ""
        echo "提示: 可将上述命令添加到 ~/.bashrc 或 ~/.zshrc 中"
    fi
}

# 验证安装
verify_installation() {
    step "验证安装"
    
    cd "$PROJECT_ROOT"
    
    info "测试命令行工具..."
    if uv run video-translate --version &> /dev/null; then
        success "video-translate 命令可用"
    else
        error "video-translate 命令不可用"
        exit 1
    fi
    
    info "测试 Python 导入..."
    if uv run python -c "from video_translate import Config, TranslationPipeline; print('导入成功')" 2>/dev/null; then
        success "Python 模块导入正常"
    else
        error "Python 模块导入失败"
        exit 1
    fi
}

# 显示完成信息
show_completion() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}      项目设置完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "快速开始:"
    echo ""
    echo "  # 查看帮助"
    echo "  uv run video-translate --help"
    echo ""
    echo "  # 翻译视频 (英文 → 中文)"
    echo "  uv run video-translate video.mp4"
    echo ""
    echo "  # 日语翻译成中文"
    echo "  uv run video-translate video.mp4 --source ja --target zh"
    echo ""
    echo "开发命令:"
    echo ""
    echo "  uv run pytest          # 运行测试"
    echo "  uv run black src/      # 代码格式化"
    echo "  uv run ruff check src/ # 代码检查"
    echo ""
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "项目设置脚本 - 初始化开发环境"
    echo ""
    echo "选项:"
    echo "  -h, --help      显示帮助信息"
    echo "  --skip-deps     跳过依赖安装"
    echo "  --skip-verify   跳过安装验证"
    echo ""
    echo "此脚本将:"
    echo "  1. 检查并安装 uv 包管理器"
    echo "  2. 检查 FFmpeg 是否安装"
    echo "  3. 安装 Python 依赖"
    echo "  4. 检查 API Key 配置"
    echo "  5. 验证安装"
}

# 主函数
main() {
    local skip_deps=false
    local skip_verify=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            --skip-deps)
                skip_deps=true
                shift
                ;;
            --skip-verify)
                skip_verify=true
                shift
                ;;
            *)
                error "未知选项: $1\n使用 --help 查看帮助"
                exit 1
                ;;
        esac
    done
    
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════╗"
    echo "║   视频字幕翻译工具 - 环境设置         ║"
    echo "╚═══════════════════════════════════════╝"
    echo -e "${NC}"
    
    detect_os
    check_uv
    check_ffmpeg
    
    if [[ "$skip_deps" == "false" ]]; then
        install_dependencies
    else
        info "跳过依赖安装"
    fi
    
    check_api_key
    
    if [[ "$skip_verify" == "false" ]]; then
        verify_installation
    else
        info "跳过安装验证"
    fi
    
    show_completion
}

main "$@"
