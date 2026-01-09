#!/usr/bin/env bash
#
# 本地代码质量和安全检查脚本
# 用于在提交代码前运行，减少 CI 报错后的返工
#

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 默认配置
RUN_FORMAT=true
RUN_LINT=true
RUN_TYPE=true
RUN_SECURITY=true
RUN_BUILD=true
RUN_TEST=false
AUTO_FIX=false
QUICK_MODE=false
VERBOSE=false
STRICT_MODE=false
INSTALL_HOOKS=false

# 检查结果跟踪
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
SKIPPED_CHECKS=0
declare -a FAILED_ITEMS=()
declare -a WARNINGS=()

# 输出函数
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    WARNINGS+=("$1")
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

fatal() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

step() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}▶${NC} $1"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 记录检查结果
record_result() {
    local name="$1"
    local status="$2"  # pass, fail, skip, warn
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    case "$status" in
        pass)
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            success "$name"
            ;;
        fail)
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            FAILED_ITEMS+=("$name")
            error "$name"
            ;;
        skip)
            SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
            warn "$name (跳过)"
            ;;
        warn)
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            warn "$name (有警告)"
            ;;
    esac
}

# 检查 uv 是否安装
check_uv() {
    if ! command -v uv &> /dev/null; then
        fatal "uv 未安装。请先运行 ./scripts/setup.sh 或访问 https://docs.astral.sh/uv/getting-started/installation/"
    fi
}

# 确保依赖已安装
ensure_dependencies() {
    step "检查依赖"
    
    cd "$PROJECT_ROOT"
    
    info "同步开发依赖..."
    if uv sync --extra dev &> /dev/null; then
        success "依赖已就绪"
    else
        uv sync --extra dev
        success "依赖安装完成"
    fi
}

# 代码格式检查 (Black)
check_format() {
    step "代码格式检查 (Black)"
    
    cd "$PROJECT_ROOT"
    
    if [[ "$AUTO_FIX" == "true" ]]; then
        info "自动格式化代码..."
        if uv run black src/ tests/ 2>&1; then
            record_result "代码格式化" "pass"
        else
            record_result "代码格式化失败" "fail"
            return 1
        fi
    else
        info "检查代码格式..."
        if [[ "$VERBOSE" == "true" ]]; then
            if uv run black --check --diff src/ tests/; then
                record_result "代码格式检查" "pass"
            else
                error "代码格式不符合 Black 标准"
                echo ""
                echo -e "${YELLOW}💡 修复建议:${NC}"
                echo "  运行: uv run black src/ tests/"
                echo "  或使用: $0 --fix"
                record_result "代码格式检查" "fail"
                return 1
            fi
        else
            if uv run black --check src/ tests/ 2>&1; then
                record_result "代码格式检查" "pass"
            else
                error "代码格式不符合 Black 标准"
                echo ""
                echo -e "${YELLOW}💡 修复建议:${NC}"
                echo "  运行: uv run black src/ tests/"
                echo "  或使用: $0 --fix"
                record_result "代码格式检查" "fail"
                return 1
            fi
        fi
    fi
}

# 代码风格检查 (Ruff)
check_lint() {
    step "代码风格检查 (Ruff)"
    
    cd "$PROJECT_ROOT"
    
    if [[ "$AUTO_FIX" == "true" ]]; then
        info "自动修复代码风格问题..."
        # 先尝试修复
        uv run ruff check --fix src/ tests/ 2>&1 || true
        # 再检查是否还有问题
        if uv run ruff check src/ tests/ 2>&1; then
            record_result "代码风格检查" "pass"
        else
            error "部分代码风格问题无法自动修复"
            record_result "代码风格检查" "fail"
            return 1
        fi
    else
        info "检查代码风格..."
        local ruff_output
        if [[ "$VERBOSE" == "true" ]]; then
            if uv run ruff check src/ tests/ --output-format=full; then
                record_result "代码风格检查" "pass"
            else
                echo ""
                echo -e "${YELLOW}💡 修复建议:${NC}"
                echo "  运行: uv run ruff check --fix src/ tests/"
                echo "  或使用: $0 --fix"
                record_result "代码风格检查" "fail"
                return 1
            fi
        else
            if ruff_output=$(uv run ruff check src/ tests/ 2>&1); then
                record_result "代码风格检查" "pass"
            else
                error "发现代码风格问题"
                echo "$ruff_output"
                echo ""
                echo -e "${YELLOW}💡 修复建议:${NC}"
                echo "  运行: uv run ruff check --fix src/ tests/"
                echo "  或使用: $0 --fix"
                record_result "代码风格检查" "fail"
                return 1
            fi
        fi
    fi
}

# 类型检查 (MyPy)
check_type() {
    step "类型检查 (MyPy)"
    
    cd "$PROJECT_ROOT"
    
    info "运行 MyPy 类型检查..."
    
    local mypy_output
    local mypy_exit_code=0
    
    if [[ "$VERBOSE" == "true" ]]; then
        uv run mypy src/ || mypy_exit_code=$?
    else
        mypy_output=$(uv run mypy src/ 2>&1) || mypy_exit_code=$?
    fi
    
    if [[ $mypy_exit_code -eq 0 ]]; then
        record_result "类型检查" "pass"
    else
        if [[ "$STRICT_MODE" == "true" ]]; then
            if [[ "$VERBOSE" != "true" ]]; then
                echo "$mypy_output"
            fi
            echo ""
            echo -e "${YELLOW}💡 类型检查发现问题，请根据错误信息修复${NC}"
            record_result "类型检查" "fail"
            return 1
        else
            # 非严格模式下，类型检查失败只是警告
            if [[ "$VERBOSE" != "true" ]]; then
                echo "$mypy_output"
            fi
            warn "类型检查发现问题 (CI 中为 continue-on-error，不会导致失败)"
            record_result "类型检查" "warn"
        fi
    fi
}

# 安全检查 (pip-audit)
check_security() {
    step "安全检查 (pip-audit)"
    
    cd "$PROJECT_ROOT"
    
    # 检查 pip-audit 是否安装
    if ! command -v pip-audit &> /dev/null && ! uv run pip-audit --version &> /dev/null 2>&1; then
        info "安装 pip-audit..."
        uv pip install --system pip-audit || uv pip install pip-audit
    fi
    
    info "检查依赖安全漏洞..."
    
    local audit_output
    local audit_exit_code=0
    
    audit_output=$(uv run pip-audit 2>&1) || audit_exit_code=$?
    
    if [[ $audit_exit_code -eq 0 ]]; then
        record_result "安全检查" "pass"
    else
        echo "$audit_output"
        if [[ "$STRICT_MODE" == "true" ]]; then
            echo ""
            echo -e "${YELLOW}💡 发现安全漏洞，请更新相关依赖${NC}"
            record_result "安全检查" "fail"
            return 1
        else
            warn "安全检查发现问题 (CI 中为 continue-on-error，不会导致失败)"
            record_result "安全检查" "warn"
        fi
    fi
}

# 构建检查
check_build() {
    step "构建检查"
    
    cd "$PROJECT_ROOT"
    
    # 安装构建工具
    info "检查构建工具..."
    if ! command -v twine &> /dev/null; then
        uv pip install --system build twine 2>/dev/null || uv pip install build twine
    fi
    
    # 清理旧的构建产物
    info "清理旧的构建产物..."
    rm -rf dist/ build/ *.egg-info src/*.egg-info
    
    # 构建包
    info "构建包..."
    if ! python -m build 2>&1; then
        record_result "包构建" "fail"
        return 1
    fi
    
    # 检查包
    info "检查包完整性..."
    if twine check dist/* 2>&1; then
        record_result "构建检查" "pass"
    else
        record_result "构建检查" "fail"
        return 1
    fi
    
    # 显示构建的包
    info "构建产物:"
    ls -la dist/
}

# 运行测试
run_tests() {
    step "运行测试"
    
    cd "$PROJECT_ROOT"
    
    info "运行 pytest 测试..."
    
    if [[ "$VERBOSE" == "true" ]]; then
        if uv run pytest --cov=src --cov-report=term; then
            record_result "测试" "pass"
        else
            record_result "测试" "fail"
            return 1
        fi
    else
        if uv run pytest --cov=src --cov-report=term -q; then
            record_result "测试" "pass"
        else
            record_result "测试" "fail"
            return 1
        fi
    fi
}

# 安装 Git hooks
install_hooks() {
    step "安装 Git Hooks"
    
    cd "$PROJECT_ROOT"
    
    local hooks_dir="$PROJECT_ROOT/.git/hooks"
    
    if [[ ! -d "$hooks_dir" ]]; then
        fatal "未找到 .git 目录，请确保在 Git 仓库中运行"
    fi
    
    # 创建 pre-commit hook
    local pre_commit_hook="$hooks_dir/pre-commit"
    
    info "创建 pre-commit hook..."
    
    cat > "$pre_commit_hook" << 'HOOK_EOF'
#!/usr/bin/env bash
#
# Pre-commit hook: 在提交前运行代码质量检查
#

echo "🔍 运行提交前检查..."

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../../scripts && pwd)"

# 运行快速检查
if [[ -f "$SCRIPT_DIR/check.sh" ]]; then
    "$SCRIPT_DIR/check.sh" --quick
    exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        echo ""
        echo "❌ 提交前检查失败！"
        echo "请修复上述问题后重新提交。"
        echo ""
        echo "💡 提示: 运行 './scripts/check.sh --fix' 可自动修复部分问题"
        exit 1
    fi
else
    echo "⚠️ 未找到检查脚本，跳过检查"
fi

echo "✅ 提交前检查通过！"
exit 0
HOOK_EOF
    
    chmod +x "$pre_commit_hook"
    success "pre-commit hook 已安装"
    
    # 创建 pre-push hook
    local pre_push_hook="$hooks_dir/pre-push"
    
    info "创建 pre-push hook..."
    
    cat > "$pre_push_hook" << 'HOOK_EOF'
#!/usr/bin/env bash
#
# Pre-push hook: 在推送前运行完整检查
#

echo "🔍 运行推送前检查..."

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../../scripts && pwd)"

# 运行完整检查（不含测试，测试太慢）
if [[ -f "$SCRIPT_DIR/check.sh" ]]; then
    "$SCRIPT_DIR/check.sh" --no-test
    exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        echo ""
        echo "❌ 推送前检查失败！"
        echo "请修复上述问题后重新推送。"
        echo ""
        echo "💡 提示:"
        echo "  - 运行 './scripts/check.sh --fix' 可自动修复部分问题"
        echo "  - 使用 'git push --no-verify' 可跳过检查（不推荐）"
        exit 1
    fi
else
    echo "⚠️ 未找到检查脚本，跳过检查"
fi

echo "✅ 推送前检查通过！"
exit 0
HOOK_EOF
    
    chmod +x "$pre_push_hook"
    success "pre-push hook 已安装"
    
    echo ""
    success "Git hooks 安装完成！"
    info "- pre-commit: 提交前运行快速检查"
    info "- pre-push: 推送前运行完整检查"
}

# 卸载 Git hooks
uninstall_hooks() {
    step "卸载 Git Hooks"
    
    cd "$PROJECT_ROOT"
    
    local hooks_dir="$PROJECT_ROOT/.git/hooks"
    
    if [[ -f "$hooks_dir/pre-commit" ]]; then
        rm "$hooks_dir/pre-commit"
        success "pre-commit hook 已删除"
    fi
    
    if [[ -f "$hooks_dir/pre-push" ]]; then
        rm "$hooks_dir/pre-push"
        success "pre-push hook 已删除"
    fi
    
    success "Git hooks 已卸载"
}

# 打印检查摘要
print_summary() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}                 检查摘要               ${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  总检查项:   ${BLUE}$TOTAL_CHECKS${NC}"
    echo -e "  ✓ 通过:     ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "  ✗ 失败:     ${RED}$FAILED_CHECKS${NC}"
    echo -e "  ⚠ 跳过:     ${YELLOW}$SKIPPED_CHECKS${NC}"
    
    if [[ ${#WARNINGS[@]} -gt 0 ]]; then
        echo ""
        echo -e "${YELLOW}警告:${NC}"
        for w in "${WARNINGS[@]}"; do
            echo -e "  - $w"
        done
    fi
    
    if [[ ${#FAILED_ITEMS[@]} -gt 0 ]]; then
        echo ""
        echo -e "${RED}失败项目:${NC}"
        for item in "${FAILED_ITEMS[@]}"; do
            echo -e "  - $item"
        done
    fi
    
    echo ""
    
    if [[ $FAILED_CHECKS -gt 0 ]]; then
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}         ✗ 检查未通过                  ${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}💡 提示:${NC}"
        echo "  - 运行 '$0 --fix' 可自动修复格式和风格问题"
        echo "  - 运行 '$0 --verbose' 查看详细错误信息"
        return 1
    else
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}         ✓ 所有检查通过！              ${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        return 0
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "本地代码质量和安全检查脚本"
    echo "用于在提交代码前运行，减少 CI 报错后的返工"
    echo ""
    echo "检查模式:"
    echo "  --quick, -q         快速检查 (仅格式和风格检查)"
    echo "  --full, -f          完整检查 (包含所有检查项和测试)"
    echo "  --strict            严格模式 (类型检查和安全检查失败也会导致整体失败)"
    echo ""
    echo "检查项控制:"
    echo "  --format            只运行格式检查 (Black)"
    echo "  --lint              只运行风格检查 (Ruff)"
    echo "  --type              只运行类型检查 (MyPy)"
    echo "  --security          只运行安全检查 (pip-audit)"
    echo "  --build             只运行构建检查"
    echo "  --test              包含测试 (默认不运行测试)"
    echo "  --no-test           不运行测试"
    echo "  --no-format         跳过格式检查"
    echo "  --no-lint           跳过风格检查"
    echo "  --no-type           跳过类型检查"
    echo "  --no-security       跳过安全检查"
    echo "  --no-build          跳过构建检查"
    echo ""
    echo "修复选项:"
    echo "  --fix               自动修复可修复的问题 (格式和风格)"
    echo ""
    echo "Git Hooks:"
    echo "  --install-hooks     安装 Git pre-commit 和 pre-push hooks"
    echo "  --uninstall-hooks   卸载 Git hooks"
    echo ""
    echo "输出控制:"
    echo "  --verbose, -v       显示详细输出"
    echo "  --help, -h          显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                  运行默认检查 (格式+风格+类型+安全+构建)"
    echo "  $0 --quick          快速检查 (仅格式+风格)"
    echo "  $0 --full           完整检查 (包含测试)"
    echo "  $0 --fix            自动修复格式和风格问题"
    echo "  $0 --format --lint  只运行格式和风格检查"
    echo "  $0 --install-hooks  安装 Git hooks"
    echo ""
    echo "建议工作流:"
    echo "  1. 开发过程中: $0 --quick --fix"
    echo "  2. 提交前:     $0"
    echo "  3. 推送前:     $0 --full"
    echo ""
    echo "或者安装 Git hooks 自动化检查:"
    echo "  $0 --install-hooks"
}

# 主函数
main() {
    local only_mode=false
    local action="check"
    
    # 解析参数
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
            -q|--quick)
                QUICK_MODE=true
                RUN_TYPE=false
                RUN_SECURITY=false
                RUN_BUILD=false
                RUN_TEST=false
                shift
                ;;
            -f|--full)
                RUN_TEST=true
                shift
                ;;
            --strict)
                STRICT_MODE=true
                shift
                ;;
            --fix)
                AUTO_FIX=true
                shift
                ;;
            --format)
                if [[ "$only_mode" == "false" ]]; then
                    only_mode=true
                    RUN_FORMAT=false
                    RUN_LINT=false
                    RUN_TYPE=false
                    RUN_SECURITY=false
                    RUN_BUILD=false
                    RUN_TEST=false
                fi
                RUN_FORMAT=true
                shift
                ;;
            --lint)
                if [[ "$only_mode" == "false" ]]; then
                    only_mode=true
                    RUN_FORMAT=false
                    RUN_LINT=false
                    RUN_TYPE=false
                    RUN_SECURITY=false
                    RUN_BUILD=false
                    RUN_TEST=false
                fi
                RUN_LINT=true
                shift
                ;;
            --type)
                if [[ "$only_mode" == "false" ]]; then
                    only_mode=true
                    RUN_FORMAT=false
                    RUN_LINT=false
                    RUN_TYPE=false
                    RUN_SECURITY=false
                    RUN_BUILD=false
                    RUN_TEST=false
                fi
                RUN_TYPE=true
                shift
                ;;
            --security)
                if [[ "$only_mode" == "false" ]]; then
                    only_mode=true
                    RUN_FORMAT=false
                    RUN_LINT=false
                    RUN_TYPE=false
                    RUN_SECURITY=false
                    RUN_BUILD=false
                    RUN_TEST=false
                fi
                RUN_SECURITY=true
                shift
                ;;
            --build)
                if [[ "$only_mode" == "false" ]]; then
                    only_mode=true
                    RUN_FORMAT=false
                    RUN_LINT=false
                    RUN_TYPE=false
                    RUN_SECURITY=false
                    RUN_BUILD=false
                    RUN_TEST=false
                fi
                RUN_BUILD=true
                shift
                ;;
            --test)
                RUN_TEST=true
                shift
                ;;
            --no-test)
                RUN_TEST=false
                shift
                ;;
            --no-format)
                RUN_FORMAT=false
                shift
                ;;
            --no-lint)
                RUN_LINT=false
                shift
                ;;
            --no-type)
                RUN_TYPE=false
                shift
                ;;
            --no-security)
                RUN_SECURITY=false
                shift
                ;;
            --no-build)
                RUN_BUILD=false
                shift
                ;;
            --install-hooks)
                action="install-hooks"
                shift
                ;;
            --uninstall-hooks)
                action="uninstall-hooks"
                shift
                ;;
            *)
                fatal "未知选项: $1\n使用 --help 查看帮助"
                ;;
        esac
    done
    
    # 打印标题
    echo -e "${MAGENTA}"
    echo "╔═══════════════════════════════════════════╗"
    echo "║    视频字幕翻译工具 - 代码质量检查        ║"
    echo "╚═══════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_uv
    
    # 执行动作
    case "$action" in
        install-hooks)
            install_hooks
            exit 0
            ;;
        uninstall-hooks)
            uninstall_hooks
            exit 0
            ;;
        check)
            ensure_dependencies
            
            local has_failure=false
            
            # 运行各项检查
            if [[ "$RUN_FORMAT" == "true" ]]; then
                check_format || has_failure=true
            fi
            
            if [[ "$RUN_LINT" == "true" ]]; then
                check_lint || has_failure=true
            fi
            
            if [[ "$RUN_TYPE" == "true" ]]; then
                check_type || has_failure=true
            fi
            
            if [[ "$RUN_SECURITY" == "true" ]]; then
                check_security || has_failure=true
            fi
            
            if [[ "$RUN_BUILD" == "true" ]]; then
                check_build || has_failure=true
            fi
            
            if [[ "$RUN_TEST" == "true" ]]; then
                run_tests || has_failure=true
            fi
            
            # 打印摘要
            if print_summary; then
                exit 0
            else
                exit 1
            fi
            ;;
    esac
}

main "$@"
