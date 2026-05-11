<p align="center">
  <a href="README.md">简体中文</a> | 
  <a href="README_EN.md">English</a> | 
  <a href="README_TW.md">繁體中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/zero%20dependencies-✓-brightgreen.svg" alt="Zero Dependencies">
</p>

<h1 align="center">🏥 DepHealth</h1>

<p align="center">
  <strong>轻量级代码依赖健康度智能分析引擎</strong><br>
  <em>Lightweight Dependency Health Intelligence Engine</em>
</p>

<p align="center">
  一站式分析项目依赖健康度 · 安全漏洞检测 · 过时依赖预警 · AI驱动升级建议
</p>

---

## 🎉 项目介绍

**DepHealth** 是一款零依赖的轻量级CLI工具，专为开发者打造，帮助您快速了解项目依赖的健康状况。它能够自动检测多种包管理器的依赖，分析安全漏洞、过时包、废弃包等问题，并生成详细的健康度报告。

### 🎯 解决的痛点

- **依赖混乱**：项目依赖过多，难以追踪哪些需要更新
- **安全隐患**：不知道依赖是否存在已知安全漏洞
- **版本过时**：难以发现哪些依赖已经过时
- **多项目管理**：不同项目使用不同包管理器，需要统一分析工具

### ✨ 自研差异化亮点

- 🚀 **零依赖**：纯Python实现，无需安装任何第三方依赖
- 📦 **多包管理器支持**：支持pip、npm、yarn、pnpm、cargo、go、maven、composer、gem等
- 🔒 **实时安全检测**：集成OSV数据库，实时检测已知漏洞
- 📊 **健康度评分**：综合安全、新鲜度、兼容性等多维度评分
- 🎨 **美观TUI界面**：终端彩色输出，一目了然
- 📄 **多格式报告**：支持JSON、Markdown、HTML等多种输出格式

---

## ✨ 核心特性

### 🔍 智能依赖扫描
- 自动检测项目使用的包管理器
- 支持解析多种依赖文件格式
- 区分直接依赖与开发依赖

### 🔒 安全漏洞检测
- 集成OSV（Open Source Vulnerabilities）数据库
- 实时查询已知安全漏洞
- 按严重程度分级展示（Critical/High/Medium/Low）

### 📦 过时依赖分析
- 查询PyPI、npm、crates.io等官方源
- 对比当前版本与最新版本
- 提供升级建议

### ⚠️ 废弃包检测
- 检测已废弃的包
- 显示废弃原因和替代建议

### 📊 健康度评分
- **安全分数**：基于漏洞数量和严重程度
- **新鲜度分数**：基于过时依赖比例
- **兼容性分数**：基于废弃依赖比例
- **维护分数**：综合评估

### 📄 多格式报告
- 终端彩色输出
- JSON格式（便于CI/CD集成）
- Markdown格式（便于文档化）
- HTML格式（可视化报告）

---

## 🚀 快速开始

### 📋 环境要求

- Python 3.8 或更高版本
- 无需任何第三方依赖

### 📥 安装

```bash
# 方式一：从PyPI安装（推荐）
pip install dephealth

# 方式二：从源码安装
git clone https://github.com/gitstq/DepHealth.git
cd DepHealth
pip install -e .
```

### 🎮 基本使用

```bash
# 分析当前目录
dephealth

# 分析指定项目
dephealth ./my-project

# 输出JSON格式报告
dephealth --json

# 保存HTML报告
dephealth --html report.html

# 离线模式（跳过网络检查）
dephealth --offline

# 检查单个包
dephealth --check-single requests 2.28.0
```

---

## 📖 详细使用指南

### 命令行参数

| 参数 | 说明 |
|------|------|
| `path` | 项目路径（默认：当前目录） |
| `--json` | 输出JSON格式报告 |
| `--markdown, --md` | 输出Markdown格式报告 |
| `--html FILE` | 保存HTML报告到文件 |
| `--output, -o FILE` | 保存报告到文件（根据扩展名自动识别格式） |
| `--no-security` | 跳过安全漏洞检查 |
| `--no-outdated` | 跳过过时依赖检查 |
| `--no-deprecated` | 跳过废弃包检查 |
| `--no-dev` | 排除开发依赖 |
| `--offline` | 离线模式 |
| `--timeout SECONDS` | 网络请求超时时间（默认：30秒） |
| `--no-color` | 禁用彩色输出 |
| `--quiet, -q` | 静默模式 |

### 支持的包管理器

| 包管理器 | 依赖文件 |
|----------|----------|
| pip | requirements.txt, setup.py, setup.cfg |
| Poetry | pyproject.toml, poetry.lock |
| npm | package.json, package-lock.json |
| Yarn | package.json, yarn.lock |
| pnpm | package.json, pnpm-lock.yaml |
| Cargo | Cargo.toml, Cargo.lock |
| Go Modules | go.mod, go.sum |
| Maven | pom.xml |
| Gradle | build.gradle, build.gradle.kts |
| Composer | composer.json, composer.lock |
| RubyGems | Gemfile, Gemfile.lock |
| Pub (Dart) | pubspec.yaml, pubspec.lock |

### CI/CD 集成示例

```yaml
# GitHub Actions 示例
name: Dependency Health Check

on: [push, pull_request]

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install DepHealth
        run: pip install dephealth
      
      - name: Run health check
        run: dephealth --json > health-report.json
      
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: health-report
          path: health-report.json
```

---

## 💡 设计思路与迭代规划

### 设计理念

DepHealth 的设计遵循以下原则：

1. **零依赖优先**：核心功能不依赖任何第三方库，降低安装门槛
2. **多语言支持**：支持主流编程语言的包管理器
3. **安全第一**：集成权威漏洞数据库，确保安全检测的准确性
4. **开发者友好**：提供美观的终端输出和多种报告格式

### 技术选型

- **纯Python标准库**：使用`urllib`进行网络请求，`json`解析数据
- **正则表达式解析**：轻量级解析各种依赖文件格式
- **OSV API集成**：使用Google维护的开源漏洞数据库

### 后续迭代计划

- [ ] 添加依赖关系图可视化
- [ ] 支持更多包管理器（NuGet、CPAN等）
- [ ] 添加自动修复建议
- [ ] 支持配置文件（.dephealth.yaml）
- [ ] 添加Web UI界面
- [ ] 支持依赖许可证合规检查

---

## 📦 打包与部署指南

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/gitstq/DepHealth.git
cd DepHealth

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black dephealth tests
isort dephealth tests

# 类型检查
mypy dephealth
```

### 构建发布

```bash
# 安装构建工具
pip install build twine

# 构建
python -m build

# 检查
twine check dist/*

# 上传到PyPI
twine upload dist/*
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 提交规范

请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<p align="center">
  Made with ❤️ by DepHealth Team
</p>
