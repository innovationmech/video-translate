#!/usr/bin/env bash
#
# 版本号更新脚本 - 自动更新项目版本号
#
# 使用方法:
#   ./scripts/bump_version.sh patch   # 1.0.0 -> 1.0.1
#   ./scripts/bump_version.sh minor   # 1.0.0 -> 1.1.0
#   ./scripts/bump_version.sh major   # 1.0.0 -> 2.0.0
#   ./scripts/bump_version.sh 2.1.0   # 指定版本号
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

# 版本文件
PYPROJECT_FILE="$PROJECT_ROOT/pyproject.toml"
INIT_FILE="$PROJECT_ROOT/src/video_translate/__init__.py"

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

# 获取当前版本号
get_current_version() {
    grep -E '^version = "' "$PYPROJECT_FILE" | sed 's/version = "\(.*\)"/\1/'
}

# 验证版本号格式
validate_version() {
    local version="$1"
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
        error "无效的版本号格式: $version\n应该是 MAJOR.MINOR.PATCH 格式，如 1.2.3"
    fi
}

# 计算新版本号
calculate_new_version() {
    local current="$1"
    local bump_type="$2"
    
    # 解析当前版本号
    local major minor patch
    IFS='.' read -r major minor patch <<< "$current"
    
    # 移除 patch 中可能的预发布标签
    patch="${patch%%-*}"
    
    case "$bump_type" in
        major)
            ((major++))
            minor=0
            patch=0
            ;;
        minor)
            ((minor++))
            patch=0
            ;;
        patch)
            ((patch++))
            ;;
        *)
            # 直接使用指定的版本号
            validate_version "$bump_type"
            echo "$bump_type"
            return
            ;;
    esac
    
    echo "${major}.${minor}.${patch}"
}

# 更新 pyproject.toml 中的版本号
update_pyproject() {
    local new_version="$1"
    
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS
        sed -i '' "s/^version = \".*\"/version = \"$new_version\"/" "$PYPROJECT_FILE"
    else
        # Linux
        sed -i "s/^version = \".*\"/version = \"$new_version\"/" "$PYPROJECT_FILE"
    fi
    
    info "已更新 pyproject.toml"
}

# 更新 __init__.py 中的版本号
update_init() {
    local new_version="$1"
    
    if [[ "$(uname)" == "Darwin" ]]; then
        # macOS
        sed -i '' "s/^__version__ = \".*\"/__version__ = \"$new_version\"/" "$INIT_FILE"
    else
        # Linux
        sed -i "s/^__version__ = \".*\"/__version__ = \"$new_version\"/" "$INIT_FILE"
    fi
    
    info "已更新 __init__.py"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 <版本类型|版本号>"
    echo ""
    echo "版本号更新脚本 - 自动更新项目版本号"
    echo ""
    echo "版本类型:"
    echo "  major     主版本号升级 (1.0.0 -> 2.0.0)"
    echo "  minor     次版本号升级 (1.0.0 -> 1.1.0)"
    echo "  patch     补丁版本号升级 (1.0.0 -> 1.0.1)"
    echo ""
    echo "或直接指定版本号:"
    echo "  $0 2.1.0"
    echo "  $0 1.0.0-beta.1"
    echo ""
    echo "选项:"
    echo "  -h, --help      显示帮助信息"
    echo "  -c, --current   显示当前版本号"
    echo "  -n, --dry-run   预览更改，不实际修改文件"
    echo ""
    echo "示例:"
    echo "  $0 patch            # 发布补丁版本"
    echo "  $0 minor            # 发布功能版本"
    echo "  $0 major            # 发布重大版本"
    echo "  $0 2.0.0-rc.1       # 发布预览版"
}

# 主函数
main() {
    local dry_run=false
    local bump_type=""
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--current)
                echo "当前版本: $(get_current_version)"
                exit 0
                ;;
            -n|--dry-run)
                dry_run=true
                shift
                ;;
            *)
                if [[ -z "$bump_type" ]]; then
                    bump_type="$1"
                else
                    error "多余的参数: $1"
                fi
                shift
                ;;
        esac
    done
    
    # 检查是否提供了版本类型
    if [[ -z "$bump_type" ]]; then
        show_help
        exit 1
    fi
    
    # 获取当前版本
    local current_version
    current_version=$(get_current_version)
    
    # 计算新版本
    local new_version
    new_version=$(calculate_new_version "$current_version" "$bump_type")
    
    echo ""
    echo -e "${CYAN}版本更新${NC}"
    echo "----------------------------------------"
    echo -e "  当前版本: ${YELLOW}$current_version${NC}"
    echo -e "  新版本:   ${GREEN}$new_version${NC}"
    echo "----------------------------------------"
    echo ""
    
    if [[ "$dry_run" == "true" ]]; then
        warn "预览模式 - 不会实际修改文件"
        echo ""
        echo "将要更新的文件:"
        echo "  - $PYPROJECT_FILE"
        echo "  - $INIT_FILE"
        exit 0
    fi
    
    # 确认更新
    read -p "确认更新版本号? [y/N] " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "已取消"
        exit 0
    fi
    
    # 更新版本号
    update_pyproject "$new_version"
    update_init "$new_version"
    
    echo ""
    success "版本号已更新: $current_version -> $new_version"
    echo ""
    echo "后续步骤:"
    echo "  1. 检查更改: git diff"
    echo "  2. 提交更改: git commit -am 'chore: bump version to $new_version'"
    echo "  3. 创建标签: git tag v$new_version"
    echo "  4. 推送更改: git push && git push --tags"
    echo ""
}

main "$@"
