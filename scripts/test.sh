#!/usr/bin/env bash
#
# 运行测试套件
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

# 默认配置
COVERAGE=true
VERBOSE=true
WATCH=false
PARALLEL=false
FAIL_FAST=false
MARKER=""
KEYWORD=""
TEST_PATH=""

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
        error "uv 未安装。请先运行 ./scripts/setup.sh 或手动安装 uv"
    fi
}

# 检查依赖是否安装
check_dependencies() {
    step "检查测试依赖"
    
    cd "$PROJECT_ROOT"
    
    # 确保开发依赖已安装
    if ! uv run python -c "import pytest" &> /dev/null; then
        warn "pytest 未安装，正在安装开发依赖..."
        uv sync --dev
    fi
    
    success "测试依赖就绪"
}

# 运行测试
run_tests() {
    step "运行测试"
    
    cd "$PROJECT_ROOT"
    
    # 构建 pytest 参数
    local pytest_args=()
    
    # 详细输出
    if [[ "$VERBOSE" == "true" ]]; then
        pytest_args+=("-v")
    fi
    
    # 覆盖率报告
    if [[ "$COVERAGE" == "true" ]]; then
        pytest_args+=("--cov=video_translate" "--cov-report=term-missing")
    fi
    
    # 快速失败
    if [[ "$FAIL_FAST" == "true" ]]; then
        pytest_args+=("-x")
    fi
    
    # 并行运行
    if [[ "$PARALLEL" == "true" ]]; then
        if uv run python -c "import pytest_xdist" &> /dev/null; then
            pytest_args+=("-n" "auto")
        else
            warn "pytest-xdist 未安装，跳过并行测试"
        fi
    fi
    
    # 标记过滤
    if [[ -n "$MARKER" ]]; then
        pytest_args+=("-m" "$MARKER")
    fi
    
    # 关键字过滤
    if [[ -n "$KEYWORD" ]]; then
        pytest_args+=("-k" "$KEYWORD")
    fi
    
    # 指定测试路径
    if [[ -n "$TEST_PATH" ]]; then
        pytest_args+=("$TEST_PATH")
    fi
    
    echo ""
    info "执行命令: uv run pytest ${pytest_args[*]}"
    echo ""
    
    # 运行测试
    if uv run pytest "${pytest_args[@]}"; then
        echo ""
        success "所有测试通过！"
        return 0
    else
        echo ""
        error "测试失败"
        return 1
    fi
}

# 运行监视模式
run_watch() {
    step "启动测试监视模式"
    
    cd "$PROJECT_ROOT"
    
    # 检查 pytest-watch 是否安装
    if ! uv run python -c "import pytest_watch" &> /dev/null; then
        warn "pytest-watch 未安装，尝试安装..."
        uv pip install pytest-watch
    fi
    
    info "监视文件变化，自动运行测试..."
    info "按 Ctrl+C 退出"
    echo ""
    
    uv run ptw -- -v
}

# 生成 HTML 覆盖率报告
generate_html_report() {
    step "生成 HTML 覆盖率报告"
    
    cd "$PROJECT_ROOT"
    
    local pytest_args=("-v" "--cov=video_translate" "--cov-report=html")
    
    if [[ -n "$TEST_PATH" ]]; then
        pytest_args+=("$TEST_PATH")
    fi
    
    uv run pytest "${pytest_args[@]}"
    
    local report_path="$PROJECT_ROOT/htmlcov/index.html"
    
    if [[ -f "$report_path" ]]; then
        success "HTML 覆盖率报告已生成: $report_path"
        
        # 尝试自动打开报告
        case "$(uname -s)" in
            Darwin*)
                open "$report_path"
                ;;
            Linux*)
                if command -v xdg-open &> /dev/null; then
                    xdg-open "$report_path"
                fi
                ;;
        esac
    fi
}

# 运行类型检查
run_type_check() {
    step "运行类型检查"
    
    cd "$PROJECT_ROOT"
    
    if uv run python -c "import mypy" &> /dev/null; then
        info "执行 mypy 类型检查..."
        uv run mypy src/video_translate/
    else
        warn "mypy 未安装，跳过类型检查"
    fi
}

# 运行代码检查
run_lint() {
    step "运行代码检查"
    
    cd "$PROJECT_ROOT"
    
    local has_error=false
    
    # Ruff 检查
    if uv run python -c "import ruff" &> /dev/null 2>&1 || command -v ruff &> /dev/null; then
        info "执行 ruff 检查..."
        if ! uv run ruff check src/video_translate/; then
            has_error=true
        fi
    else
        warn "ruff 未安装，跳过 ruff 检查"
    fi
    
    # Black 格式检查
    if uv run python -c "import black" &> /dev/null; then
        info "执行 black 格式检查..."
        if ! uv run black --check src/video_translate/; then
            has_error=true
        fi
    else
        warn "black 未安装，跳过格式检查"
    fi
    
    if [[ "$has_error" == "true" ]]; then
        error "代码检查发现问题"
    else
        success "代码检查通过"
    fi
}

# 运行完整测试套件（测试 + 类型检查 + 代码检查）
run_full() {
    step "运行完整测试套件"
    
    run_lint
    run_type_check
    run_tests
    
    echo ""
    success "完整测试套件通过！"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项] [测试路径]"
    echo ""
    echo "运行测试套件"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -v, --verbose       详细输出 (默认启用)"
    echo "  -q, --quiet         简洁输出"
    echo "  -c, --cov           启用覆盖率报告 (默认启用)"
    echo "  --no-cov            禁用覆盖率报告"
    echo "  --html              生成 HTML 覆盖率报告"
    echo "  -x, --fail-fast     遇到失败立即停止"
    echo "  -p, --parallel      并行运行测试 (需要 pytest-xdist)"
    echo "  -w, --watch         监视模式，文件变化时自动运行测试"
    echo "  -m, --marker MARK   只运行指定标记的测试"
    echo "  -k, --keyword KEY   只运行名称包含关键字的测试"
    echo "  --lint              只运行代码检查"
    echo "  --type              只运行类型检查"
    echo "  --full              运行完整测试套件 (测试 + 类型检查 + 代码检查)"
    echo ""
    echo "示例:"
    echo "  $0                           运行所有测试"
    echo "  $0 tests/test_utils.py       运行指定测试文件"
    echo "  $0 -k 'test_config'          运行名称包含 'test_config' 的测试"
    echo "  $0 -m slow                   运行标记为 'slow' 的测试"
    echo "  $0 -x                        遇到失败立即停止"
    echo "  $0 --html                    生成 HTML 覆盖率报告"
    echo "  $0 --watch                   监视模式"
    echo "  $0 --full                    运行完整测试套件"
}

# 主函数
main() {
    local action="test"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -q|--quiet)
                VERBOSE=false
                shift
                ;;
            -c|--cov)
                COVERAGE=true
                shift
                ;;
            --no-cov)
                COVERAGE=false
                shift
                ;;
            --html)
                action="html"
                shift
                ;;
            -x|--fail-fast)
                FAIL_FAST=true
                shift
                ;;
            -p|--parallel)
                PARALLEL=true
                shift
                ;;
            -w|--watch)
                action="watch"
                shift
                ;;
            -m|--marker)
                MARKER="$2"
                shift 2
                ;;
            -k|--keyword)
                KEYWORD="$2"
                shift 2
                ;;
            --lint)
                action="lint"
                shift
                ;;
            --type)
                action="type"
                shift
                ;;
            --full)
                action="full"
                shift
                ;;
            -*)
                error "未知选项: $1\n使用 --help 查看帮助"
                ;;
            *)
                TEST_PATH="$1"
                shift
                ;;
        esac
    done
    
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════╗"
    echo "║      视频字幕翻译工具 - 测试套件      ║"
    echo "╚═══════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_uv
    
    case "$action" in
        test)
            check_dependencies
            run_tests
            ;;
        watch)
            check_dependencies
            run_watch
            ;;
        html)
            check_dependencies
            generate_html_report
            ;;
        lint)
            run_lint
            ;;
        type)
            run_type_check
            ;;
        full)
            check_dependencies
            run_full
            ;;
    esac
}

main "$@"
