#!/usr/bin/env bash
#
# 发布脚本 - 将项目发布到 PyPI 或 TestPyPI
#
# 使用方法:
#   ./scripts/publish.sh              # 发布到 PyPI
#   ./scripts/publish.sh --test       # 发布到 TestPyPI
#   ./scripts/publish.sh --dry-run    # 预览模式
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

# 配置
DIST_DIR="$PROJECT_ROOT/dist"
PYPI_URL="https://upload.pypi.org/legacy/"
TEST_PYPI_URL="https://test.pypi.org/legacy/"
PYPIRC_FILE="$HOME/.pypirc"

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

step() {
    echo -e "\n${CYAN}==>${NC} $1"
}

# 检查 uv 是否安装
check_uv() {
    if ! command -v uv &> /dev/null; then
        error "uv 未安装。请先安装: curl -LsSf https://astral.sh/uv/install.sh | sh"
    fi
}

# 从 ~/.pypirc 读取凭据
# 参数: $1 = 索引名称 (pypi 或 testpypi)
# 返回: 设置 PYPI_USERNAME 和 PYPI_PASSWORD 变量
read_pypirc() {
    local index_name="$1"
    
    PYPI_USERNAME=""
    PYPI_PASSWORD=""
    
    if [[ ! -f "$PYPIRC_FILE" ]]; then
        warn "未找到 $PYPIRC_FILE 文件"
        return 1
    fi
    
    # 解析 .pypirc 文件
    local in_section=false
    local current_section=""
    
    while IFS= read -r line || [[ -n "$line" ]]; do
        # 去除首尾空白
        line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # 跳过空行和注释
        [[ -z "$line" || "$line" == \#* ]] && continue
        
        # 检测 section 头
        if [[ "$line" =~ ^\[([^\]]+)\]$ ]]; then
            current_section="${BASH_REMATCH[1]}"
            if [[ "$current_section" == "$index_name" ]]; then
                in_section=true
            else
                in_section=false
            fi
            continue
        fi
        
        # 在目标 section 中读取键值对
        if [[ "$in_section" == true ]]; then
            if [[ "$line" =~ ^username[[:space:]]*=[[:space:]]*(.+)$ ]]; then
                PYPI_USERNAME="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ ^password[[:space:]]*=[[:space:]]*(.+)$ ]]; then
                PYPI_PASSWORD="${BASH_REMATCH[1]}"
            fi
        fi
    done < "$PYPIRC_FILE"
    
    if [[ -n "$PYPI_USERNAME" && -n "$PYPI_PASSWORD" ]]; then
        return 0
    else
        return 1
    fi
}

# 获取当前版本号
get_version() {
    grep -E '^version = "' "$PROJECT_ROOT/pyproject.toml" | sed 's/version = "\(.*\)"/\1/'
}

# 检查版本一致性
check_version() {
    step "检查版本一致性"
    
    if ! "$SCRIPT_DIR/check_version.sh"; then
        error "版本检查失败，请先修复版本号问题"
    fi
}

# 检查 Git 状态
check_git_status() {
    step "检查 Git 状态"
    
    cd "$PROJECT_ROOT"
    
    # 检查是否有未提交的更改
    if [[ -n "$(git status --porcelain)" ]]; then
        warn "检测到未提交的更改:"
        git status --short
        echo ""
        read -p "是否继续发布? [y/N] " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "已取消发布"
            exit 0
        fi
    else
        success "工作区干净"
    fi
}

# 检查 Git 标签
check_git_tag() {
    local version="$1"
    local tag="v$version"
    
    step "检查 Git 标签"
    
    cd "$PROJECT_ROOT"
    
    if git rev-parse "$tag" &> /dev/null; then
        success "标签 $tag 已存在"
    else
        warn "标签 $tag 不存在"
        read -p "是否创建标签 $tag? [Y/n] " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            git tag "$tag"
            success "已创建标签 $tag"
            echo ""
            read -p "是否推送标签到远程? [Y/n] " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                git push origin "$tag"
                success "已推送标签 $tag"
            fi
        fi
    fi
}

# 清理并构建
build_package() {
    step "构建发行包"
    
    cd "$PROJECT_ROOT"
    
    # 清理旧的构建文件
    rm -rf "$DIST_DIR"
    rm -rf "$PROJECT_ROOT/build"
    
    # 构建
    uv build
    
    success "构建完成"
    
    # 显示构建产物
    echo ""
    info "构建产物:"
    ls -lh "$DIST_DIR"
}

# 发布到 PyPI
publish_to_pypi() {
    local target="$1"
    local dry_run="$2"
    
    step "发布到 $target"
    
    cd "$PROJECT_ROOT"
    
    local publish_url
    local index_name
    
    if [[ "$target" == "testpypi" ]]; then
        publish_url="$TEST_PYPI_URL"
        index_name="TestPyPI"
    else
        publish_url="$PYPI_URL"
        index_name="PyPI"
    fi
    
    if [[ "$dry_run" == "true" ]]; then
        warn "预览模式 - 不会实际上传"
        echo ""
        echo "将要上传的文件:"
        ls "$DIST_DIR"
        echo ""
        echo "目标: $index_name ($publish_url)"
        return
    fi
    
    # 读取 pypirc 凭据
    local pypirc_index="$target"
    
    echo ""
    info "准备上传到 $index_name"
    
    if read_pypirc "$pypirc_index"; then
        success "已从 $PYPIRC_FILE [$pypirc_index] 读取凭据"
        
        # 使用 uv publish 发布 (带凭据)
        # 如果用户名是 __token__，使用 --token 参数
        if [[ "$PYPI_USERNAME" == "__token__" ]]; then
            info "使用 API Token 认证"
            if [[ "$target" == "testpypi" ]]; then
                uv publish --publish-url "$publish_url" --token "$PYPI_PASSWORD"
            else
                uv publish --token "$PYPI_PASSWORD"
            fi
        else
            info "用户名: $PYPI_USERNAME"
            if [[ "$target" == "testpypi" ]]; then
                uv publish --publish-url "$publish_url" --username "$PYPI_USERNAME" --password "$PYPI_PASSWORD"
            else
                uv publish --username "$PYPI_USERNAME" --password "$PYPI_PASSWORD"
            fi
        fi
    else
        warn "无法从 $PYPIRC_FILE 读取 [$pypirc_index] 配置"
        echo ""
        echo "请确保 ~/.pypirc 文件存在且格式正确:"
        echo ""
        echo "  [pypi]"
        echo "  username = __token__"
        echo "  password = pypi-xxxxx"
        echo ""
        echo "  [testpypi]"
        echo "  username = __token__"
        echo "  password = pypi-xxxxx"
        echo ""
        echo "或者设置环境变量: UV_PUBLISH_TOKEN"
        echo ""
        
        # 回退到默认行为 (让 uv 处理认证)
        read -p "是否继续尝试发布 (uv 将提示输入凭据)? [y/N] " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "已取消发布"
            exit 0
        fi
        
        # 使用 uv publish 发布 (无凭据，让 uv 提示)
        if [[ "$target" == "testpypi" ]]; then
            uv publish --publish-url "$publish_url"
        else
            uv publish
        fi
    fi
    
    success "发布成功！"
    
    # 显示包链接
    local package_name version
    package_name=$(grep -E '^name = "' "$PROJECT_ROOT/pyproject.toml" | sed 's/name = "\(.*\)"/\1/')
    version=$(get_version)
    
    echo ""
    if [[ "$target" == "testpypi" ]]; then
        echo "查看包: https://test.pypi.org/project/$package_name/$version/"
        echo "安装命令: pip install -i https://test.pypi.org/simple/ $package_name==$version"
    else
        echo "查看包: https://pypi.org/project/$package_name/$version/"
        echo "安装命令: pip install $package_name==$version"
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "发布脚本 - 将项目发布到 PyPI 或 TestPyPI"
    echo ""
    echo "选项:"
    echo "  -h, --help      显示帮助信息"
    echo "  -t, --test      发布到 TestPyPI (测试环境)"
    echo "  -n, --dry-run   预览模式，不实际上传"
    echo "  --skip-build    跳过构建步骤"
    echo "  --skip-checks   跳过版本和 Git 检查"
    echo ""
    echo "示例:"
    echo "  $0                    # 发布到 PyPI"
    echo "  $0 --test             # 发布到 TestPyPI"
    echo "  $0 --test --dry-run   # 预览 TestPyPI 发布"
    echo ""
    echo "认证配置:"
    echo "  脚本会从 ~/.pypirc 文件读取凭据，文件格式示例:"
    echo ""
    echo "    [pypi]"
    echo "    username = __token__"
    echo "    password = pypi-xxxxx"
    echo ""
    echo "    [testpypi]"
    echo "    username = __token__"
    echo "    password = pypi-xxxxx"
    echo ""
    echo "首次发布前，请确保:"
    echo "  1. 在 PyPI/TestPyPI 注册账号"
    echo "  2. 创建 API Token"
    echo "     - PyPI: https://pypi.org/manage/account/token/"
    echo "     - TestPyPI: https://test.pypi.org/manage/account/token/"
    echo "  3. 配置 ~/.pypirc 文件"
}

# 主函数
main() {
    local target="pypi"
    local dry_run=false
    local skip_build=false
    local skip_checks=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--test)
                target="testpypi"
                shift
                ;;
            -n|--dry-run)
                dry_run=true
                shift
                ;;
            --skip-build)
                skip_build=true
                shift
                ;;
            --skip-checks)
                skip_checks=true
                shift
                ;;
            *)
                error "未知选项: $1\n使用 --help 查看帮助"
                ;;
        esac
    done
    
    # 显示标题
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════╗${NC}"
    if [[ "$target" == "testpypi" ]]; then
        echo -e "${CYAN}║     发布到 TestPyPI (测试环境)        ║${NC}"
    else
        echo -e "${CYAN}║          发布到 PyPI                  ║${NC}"
    fi
    echo -e "${CYAN}╚═══════════════════════════════════════╝${NC}"
    
    # 检查 uv
    check_uv
    
    # 获取版本号
    local version
    version=$(get_version)
    info "当前版本: $version"
    
    # 检查步骤
    if [[ "$skip_checks" == "false" ]]; then
        check_version
        check_git_status
        check_git_tag "$version"
    else
        warn "跳过版本和 Git 检查"
    fi
    
    # 构建步骤
    if [[ "$skip_build" == "false" ]]; then
        build_package
    else
        warn "跳过构建步骤"
        if [[ ! -d "$DIST_DIR" ]] || [[ -z "$(ls -A "$DIST_DIR" 2>/dev/null)" ]]; then
            error "dist 目录为空，请先运行构建或移除 --skip-build 选项"
        fi
    fi
    
    # 确认发布
    if [[ "$dry_run" == "false" ]]; then
        echo ""
        echo -e "${YELLOW}即将发布版本 $version 到 $target${NC}"
        read -p "确认发布? [y/N] " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "已取消发布"
            exit 0
        fi
    fi
    
    # 发布
    publish_to_pypi "$target" "$dry_run"
    
    echo ""
    success "发布流程完成！"
}

main "$@"
