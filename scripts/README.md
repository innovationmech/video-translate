# 脚本使用指南

本目录包含项目开发、测试、构建和发布所需的所有自动化脚本。

## 📋 脚本概览

| 脚本 | 用途 | 常用命令 |
|------|------|----------|
| `setup.sh` | 初始化开发环境 | `./scripts/setup.sh` |
| `test.sh` | 运行测试套件 | `./scripts/test.sh` |
| `build.sh` | 构建发行包 | `./scripts/build.sh` |
| `bump_version.sh` | 更新版本号 | `./scripts/bump_version.sh patch` |
| `check_version.sh` | 检查版本一致性 | `./scripts/check_version.sh` |
| `publish.sh` | 发布到 PyPI | `./scripts/publish.sh` |

---

## 🚀 setup.sh - 环境设置

初始化开发环境，包括检查依赖、安装包和验证安装。

### 基本用法

```bash
# 完整设置（推荐首次使用）
./scripts/setup.sh

# 跳过依赖安装
./scripts/setup.sh --skip-deps

# 跳过安装验证
./scripts/setup.sh --skip-verify
```

### 功能说明

1. **检查 uv 包管理器** - 如未安装会提示自动安装
2. **检查 FFmpeg** - 视频处理必需依赖
3. **安装 Python 依赖** - 通过 `uv sync --dev` 安装
4. **检查 API Key 配置** - 检查 DEEPSEEK_API_KEY 或 OPENAI_API_KEY
5. **验证安装** - 测试命令行工具和模块导入

---

## 🧪 test.sh - 测试套件

运行项目测试，支持覆盖率报告、代码检查等功能。

### 基本用法

```bash
# 运行所有测试（带覆盖率）
./scripts/test.sh

# 运行指定测试文件
./scripts/test.sh tests/test_utils.py

# 按关键字筛选测试
./scripts/test.sh -k 'config'

# 按标记筛选测试
./scripts/test.sh -m slow
```

### 测试选项

| 选项 | 说明 |
|------|------|
| `-v, --verbose` | 详细输出（默认启用） |
| `-q, --quiet` | 简洁输出 |
| `-c, --cov` | 启用覆盖率报告（默认启用） |
| `--no-cov` | 禁用覆盖率报告 |
| `-x, --fail-fast` | 遇到失败立即停止 |
| `-p, --parallel` | 并行运行测试（需要 pytest-xdist） |
| `-k, --keyword KEY` | 按名称关键字筛选测试 |
| `-m, --marker MARK` | 按标记筛选测试 |

### 覆盖率报告

```bash
# 生成 HTML 覆盖率报告并自动打开
./scripts/test.sh --html
```

### 监视模式

```bash
# 文件变化时自动运行测试
./scripts/test.sh --watch
```

### 代码质量检查

```bash
# 只运行代码检查（ruff + black）
./scripts/test.sh --lint

# 只运行类型检查（mypy）
./scripts/test.sh --type

# 完整测试套件（测试 + 类型检查 + 代码检查）
./scripts/test.sh --full
```

---

## 📦 build.sh - 构建发行包

构建 Python wheel 和 sdist 发行包。

### 基本用法

```bash
# 构建 wheel 和 sdist
./scripts/build.sh

# 只清理构建文件
./scripts/build.sh --clean
```

### 输出

构建产物将保存在 `dist/` 目录：

```
dist/
├── video_translate-x.x.x-py3-none-any.whl
└── video_translate-x.x.x.tar.gz
```

---

## 🔢 bump_version.sh - 版本管理

自动更新项目版本号，同步更新 `pyproject.toml` 和 `__init__.py`。

### 基本用法

```bash
# 补丁版本升级: 1.0.0 -> 1.0.1
./scripts/bump_version.sh patch

# 次版本升级: 1.0.0 -> 1.1.0
./scripts/bump_version.sh minor

# 主版本升级: 1.0.0 -> 2.0.0
./scripts/bump_version.sh major

# 指定版本号
./scripts/bump_version.sh 2.1.0

# 预发布版本
./scripts/bump_version.sh 2.0.0-rc.1
```

### 其他选项

```bash
# 查看当前版本
./scripts/bump_version.sh --current

# 预览模式（不实际修改文件）
./scripts/bump_version.sh --dry-run patch
```

### 版本号格式

遵循语义化版本规范 (SemVer)：`MAJOR.MINOR.PATCH[-PRERELEASE]`

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复
- **PRERELEASE**: 预发布标签（如 `alpha.1`、`beta.2`、`rc.1`）

---

## ✅ check_version.sh - 版本检查

检查项目中各处版本号是否一致。

### 基本用法

```bash
./scripts/check_version.sh
```

### 检查内容

- `pyproject.toml` 中的版本号
- `__init__.py` 中的版本号
- Git 最新标签

---

## 🚀 publish.sh - 发布到 PyPI

将项目发布到 PyPI 或 TestPyPI。

### 基本用法

```bash
# 发布到 PyPI（正式环境）
./scripts/publish.sh

# 发布到 TestPyPI（测试环境）
./scripts/publish.sh --test

# 预览模式（不实际上传）
./scripts/publish.sh --dry-run
```

### 发布选项

| 选项 | 说明 |
|------|------|
| `-t, --test` | 发布到 TestPyPI |
| `-n, --dry-run` | 预览模式，不实际上传 |
| `--skip-build` | 跳过构建步骤 |
| `--skip-checks` | 跳过版本和 Git 检查 |

### 首次发布准备

1. 在 [PyPI](https://pypi.org) 或 [TestPyPI](https://test.pypi.org) 注册账号
2. 创建 API Token
3. 设置环境变量：

```bash
export UV_PUBLISH_TOKEN='pypi-xxxxx'
```

### 发布流程

脚本会自动执行以下步骤：

1. 检查版本一致性
2. 检查 Git 状态
3. 检查/创建 Git 标签
4. 构建发行包
5. 上传到 PyPI/TestPyPI

---

## 🔄 典型工作流程

### 1. 初始设置（新开发者）

```bash
git clone <repo-url>
cd video-translate
./scripts/setup.sh
```

### 2. 日常开发

```bash
# 运行测试
./scripts/test.sh

# 监视模式开发
./scripts/test.sh --watch

# 完整检查
./scripts/test.sh --full
```

### 3. 发布新版本

```bash
# 1. 确保测试通过
./scripts/test.sh --full

# 2. 更新版本号
./scripts/bump_version.sh patch

# 3. 提交更改
git add -A
git commit -m "chore: bump version to x.x.x"

# 4. 先发布到 TestPyPI 测试
./scripts/publish.sh --test

# 5. 验证后发布到正式 PyPI
./scripts/publish.sh
```

---

## 💡 提示

- 所有脚本都支持 `-h` 或 `--help` 查看帮助信息
- 脚本使用彩色输出区分信息类型：🔵 INFO | 🟢 SUCCESS | 🟡 WARN | 🔴 ERROR
- 脚本会自动检测操作系统并适配命令差异
- 建议在发布前始终运行 `./scripts/test.sh --full` 进行完整检查
