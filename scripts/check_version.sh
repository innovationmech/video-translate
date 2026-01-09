#!/usr/bin/env bash
#
# 版本检查脚本 - 检查项目中各处版本号是否一致
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

# 版本文件
PYPROJECT_FILE="$PROJECT_ROOT/pyproject.toml"
INIT_FILE="$PROJECT_ROOT/src/video_translate/__init__.py"

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 从 pyproject.toml 获取版本号
get_pyproject_version() {
    grep -E '^version = "' "$PYPROJECT_FILE" | sed 's/version = "\(.*\)"/\1/'
}

# 从 __init__.py 获取版本号
get_init_version() {
    grep -E '^__version__ = "' "$INIT_FILE" | sed 's/__version__ = "\(.*\)"/\1/'
}

# 检查 Git 标签版本
get_git_tag_version() {
    if git describe --tags --abbrev=0 2>/dev/null; then
        return 0
    fi
    echo "无标签"
}

# 主函数
main() {
    echo ""
    echo -e "${BLUE}版本检查${NC}"
    echo "========================================"
    echo ""
    
    local has_error=false
    
    # 获取各处版本号
    local pyproject_version init_version git_tag
    pyproject_version=$(get_pyproject_version)
    init_version=$(get_init_version)
    
    cd "$PROJECT_ROOT"
    git_tag=$(get_git_tag_version)
    
    # 显示版本信息
    echo "版本信息:"
    echo "  pyproject.toml:    $pyproject_version"
    echo "  __init__.py:       $init_version"
    echo "  Git 最新标签:      $git_tag"
    echo ""
    
    # 检查一致性
    echo "一致性检查:"
    
    # 检查 pyproject.toml 和 __init__.py 是否一致
    if [[ "$pyproject_version" == "$init_version" ]]; then
        success "pyproject.toml 与 __init__.py 版本一致"
    else
        error "pyproject.toml ($pyproject_version) 与 __init__.py ($init_version) 版本不一致"
        has_error=true
    fi
    
    # 检查与 Git 标签是否一致
    if [[ "$git_tag" != "无标签" ]]; then
        # 移除 v 前缀进行比较
        local tag_version="${git_tag#v}"
        if [[ "$pyproject_version" == "$tag_version" ]]; then
            success "版本号与 Git 标签一致"
        else
            echo -e "${YELLOW}[!]${NC} 版本号 ($pyproject_version) 与最新 Git 标签 ($git_tag) 不同"
            echo "    提示: 发布新版本后请创建对应的 Git 标签"
        fi
    else
        echo -e "${YELLOW}[!]${NC} 尚未创建 Git 标签"
    fi
    
    echo ""
    echo "========================================"
    
    if [[ "$has_error" == "true" ]]; then
        echo ""
        error "版本检查失败！请运行以下命令修复:"
        echo ""
        echo "  ./scripts/bump_version.sh $pyproject_version"
        echo ""
        exit 1
    else
        echo ""
        success "版本检查通过"
        echo ""
    fi
}

main "$@"
