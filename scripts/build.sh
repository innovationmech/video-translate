#!/usr/bin/env bash
#
# 构建 Python 包的 wheel 和 sdist 发行版
#

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 输出目录
DIST_DIR="$PROJECT_ROOT/dist"

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
    exit 1
}

# 检查 uv 是否安装
check_uv() {
    if ! command -v uv &> /dev/null; then
        error "uv 未安装。请先安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    fi
    info "uv 版本: $(uv --version)"
}

# 清理旧的构建文件
clean() {
    info "清理旧的构建文件..."
    rm -rf "$DIST_DIR"
    rm -rf "$PROJECT_ROOT/build"
    rm -rf "$PROJECT_ROOT/src"/*.egg-info
    success "清理完成"
}

# 构建包
build() {
    info "开始构建..."
    cd "$PROJECT_ROOT"
    
    # 使用 uv build 构建 wheel 和 sdist
    uv build
    
    success "构建完成"
}

# 显示构建结果
show_result() {
    echo ""
    info "构建产物:"
    echo "----------------------------------------"
    ls -lh "$DIST_DIR"
    echo "----------------------------------------"
    echo ""
    success "所有构建产物已保存至: $DIST_DIR"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -c, --clean     只清理构建文件，不构建"
    echo "  -h, --help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0              构建 wheel 和 sdist"
    echo "  $0 --clean      只清理构建文件"
}

# 主函数
main() {
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--clean)
            clean
            exit 0
            ;;
        "")
            check_uv
            clean
            build
            show_result
            ;;
        *)
            error "未知选项: $1\n使用 --help 查看帮助"
            ;;
    esac
}

main "$@"
