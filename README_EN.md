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
  <strong>Lightweight Dependency Health Intelligence Engine</strong><br>
  <em>轻量级代码依赖健康度智能分析引擎</em>
</p>

<p align="center">
  One-stop analysis for dependency health · Security vulnerability detection · Outdated dependency alerts · AI-powered upgrade suggestions
</p>

---

## 🎉 Introduction

**DepHealth** is a zero-dependency lightweight CLI tool designed for developers to quickly understand the health status of project dependencies. It automatically detects dependencies across multiple package managers, analyzes security vulnerabilities, outdated packages, deprecated packages, and generates detailed health reports.

### 🎯 Problems Solved

- **Dependency Chaos**: Too many dependencies, hard to track which ones need updates
- **Security Risks**: Unknown vulnerabilities in dependencies
- **Outdated Versions**: Difficulty discovering which dependencies are outdated
- **Multi-Project Management**: Different projects use different package managers, need a unified analysis tool

### ✨ Unique Features

- 🚀 **Zero Dependencies**: Pure Python implementation, no third-party dependencies required
- 📦 **Multi-Package Manager Support**: pip, npm, yarn, pnpm, cargo, go, maven, composer, gem, and more
- 🔒 **Real-time Security Detection**: Integrated with OSV database for real-time vulnerability detection
- 📊 **Health Score**: Comprehensive scoring across security, freshness, compatibility, and more
- 🎨 **Beautiful TUI**: Colorful terminal output at a glance
- 📄 **Multi-Format Reports**: JSON, Markdown, HTML, and more

---

## ✨ Core Features

### 🔍 Smart Dependency Scanning
- Automatic detection of package managers used in projects
- Support for multiple dependency file formats
- Distinguish between direct and development dependencies

### 🔒 Security Vulnerability Detection
- Integrated with OSV (Open Source Vulnerabilities) database
- Real-time query for known security vulnerabilities
- Severity classification (Critical/High/Medium/Low)

### 📦 Outdated Dependency Analysis
- Query official sources like PyPI, npm, crates.io
- Compare current version with latest version
- Provide upgrade suggestions

### ⚠️ Deprecated Package Detection
- Detect deprecated packages
- Show deprecation reasons and alternative suggestions

### 📊 Health Score
- **Security Score**: Based on vulnerability count and severity
- **Freshness Score**: Based on outdated dependency ratio
- **Compatibility Score**: Based on deprecated dependency ratio
- **Maintenance Score**: Comprehensive evaluation

### 📄 Multi-Format Reports
- Colorful terminal output
- JSON format (for CI/CD integration)
- Markdown format (for documentation)
- HTML format (visual reports)

---

## 🚀 Quick Start

### 📋 Requirements

- Python 3.8 or higher
- No third-party dependencies required

### 📥 Installation

```bash
# Method 1: Install from PyPI (Recommended)
pip install dephealth

# Method 2: Install from source
git clone https://github.com/gitstq/DepHealth.git
cd DepHealth
pip install -e .
```

### 🎮 Basic Usage

```bash
# Analyze current directory
dephealth

# Analyze specific project
dephealth ./my-project

# Output JSON format report
dephealth --json

# Save HTML report
dephealth --html report.html

# Offline mode (skip network checks)
dephealth --offline

# Check single package
dephealth --check-single requests 2.28.0
```

---

## 📖 Detailed Usage Guide

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `path` | Project path (default: current directory) |
| `--json` | Output JSON format report |
| `--markdown, --md` | Output Markdown format report |
| `--html FILE` | Save HTML report to file |
| `--output, -o FILE` | Save report to file (auto-detect format by extension) |
| `--no-security` | Skip security vulnerability check |
| `--no-outdated` | Skip outdated dependency check |
| `--no-deprecated` | Skip deprecated package check |
| `--no-dev` | Exclude development dependencies |
| `--offline` | Offline mode |
| `--timeout SECONDS` | Network request timeout (default: 30s) |
| `--no-color` | Disable colored output |
| `--quiet, -q` | Quiet mode |

### Supported Package Managers

| Package Manager | Dependency Files |
|-----------------|------------------|
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

### CI/CD Integration Example

```yaml
# GitHub Actions Example
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

## 💡 Design Philosophy & Roadmap

### Design Principles

DepHealth follows these principles:

1. **Zero Dependencies First**: Core functionality doesn't depend on any third-party libraries
2. **Multi-Language Support**: Support mainstream programming language package managers
3. **Security First**: Integrate authoritative vulnerability databases
4. **Developer Friendly**: Beautiful terminal output and multiple report formats

### Technology Choices

- **Pure Python Standard Library**: Use `urllib` for network requests, `json` for data parsing
- **Regex Parsing**: Lightweight parsing of various dependency file formats
- **OSV API Integration**: Use Google-maintained open source vulnerability database

### Roadmap

- [ ] Add dependency graph visualization
- [ ] Support more package managers (NuGet, CPAN, etc.)
- [ ] Add auto-fix suggestions
- [ ] Support configuration file (.dephealth.yaml)
- [ ] Add Web UI
- [ ] Support dependency license compliance check

---

## 📦 Build & Deployment Guide

### Local Development

```bash
# Clone repository
git clone https://github.com/gitstq/DepHealth.git
cd DepHealth

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black dephealth tests
isort dephealth tests

# Type checking
mypy dephealth
```

### Build & Publish

```bash
# Install build tools
pip install build twine

# Build
python -m build

# Check
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

---

## 🤝 Contributing

We welcome all forms of contributions!

### How to Contribute

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

### Commit Convention

Please follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tool related

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ by DepHealth Team
</p>
