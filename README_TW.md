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
  <strong>輕量級程式碼依賴健康度智慧分析引擎</strong><br>
  <em>Lightweight Dependency Health Intelligence Engine</em>
</p>

<p align="center">
  一站式分析專案依賴健康度 · 安全漏洞檢測 · 過時依賴預警 · AI驅動升級建議
</p>

---

## 🎉 專案介紹

**DepHealth** 是一款零依賴的輕量級CLI工具，專為開發者打造，幫助您快速了解專案依賴的健康狀況。它能夠自動檢測多種套件管理器的依賴，分析安全漏洞、過時套件、廢棄套件等問題，並生成詳細的健康度報告。

### 🎯 解決的痛點

- **依賴混亂**：專案依賴過多，難以追蹤哪些需要更新
- **安全隱患**：不知道依賴是否存在已知安全漏洞
- **版本過時**：難以發現哪些依賴已經過時
- **多專案管理**：不同專案使用不同套件管理器，需要統一分析工具

### ✨ 自研差異化亮點

- 🚀 **零依賴**：純Python實現，無需安裝任何第三方依賴
- 📦 **多套件管理器支援**：支援pip、npm、yarn、pnpm、cargo、go、maven、composer、gem等
- 🔒 **即時安全檢測**：整合OSV資料庫，即時檢測已知漏洞
- 📊 **健康度評分**：綜合安全、新鮮度、相容性等多維度評分
- 🎨 **美觀TUI介面**：終端彩色輸出，一目瞭然
- 📄 **多格式報告**：支援JSON、Markdown、HTML等多種輸出格式

---

## ✨ 核心特性

### 🔍 智慧依賴掃描
- 自動檢測專案使用的套件管理器
- 支援解析多種依賴檔案格式
- 區分直接依賴與開發依賴

### 🔒 安全漏洞檢測
- 整合OSV（Open Source Vulnerabilities）資料庫
- 即時查詢已知安全漏洞
- 按嚴重程度分級展示（Critical/High/Medium/Low）

### 📦 過時依賴分析
- 查詢PyPI、npm、crates.io等官方來源
- 對比當前版本與最新版本
- 提供升級建議

### ⚠️ 廢棄套件檢測
- 檢測已廢棄的套件
- 顯示廢棄原因和替代建議

### 📊 健康度評分
- **安全分數**：基於漏洞數量和嚴重程度
- **新鮮度分數**：基於過時依賴比例
- **相容性分數**：基於廢棄依賴比例
- **維護分數**：綜合評估

### 📄 多格式報告
- 終端彩色輸出
- JSON格式（便於CI/CD整合）
- Markdown格式（便於文件化）
- HTML格式（視覺化報告）

---

## 🚀 快速開始

### 📋 環境要求

- Python 3.8 或更高版本
- 無需任何第三方依賴

### 📥 安裝

```bash
# 方式一：從PyPI安裝（推薦）
pip install dephealth

# 方式二：從原始碼安裝
git clone https://github.com/gitstq/DepHealth.git
cd DepHealth
pip install -e .
```

### 🎮 基本使用

```bash
# 分析當前目錄
dephealth

# 分析指定專案
dephealth ./my-project

# 輸出JSON格式報告
dephealth --json

# 儲存HTML報告
dephealth --html report.html

# 離線模式（跳過網路檢查）
dephealth --offline

# 檢查單一套件
dephealth --check-single requests 2.28.0
```

---

## 📖 詳細使用指南

### 命令列參數

| 參數 | 說明 |
|------|------|
| `path` | 專案路徑（預設：當前目錄） |
| `--json` | 輸出JSON格式報告 |
| `--markdown, --md` | 輸出Markdown格式報告 |
| `--html FILE` | 儲存HTML報告到檔案 |
| `--output, -o FILE` | 儲存報告到檔案（根據副檔名自動識別格式） |
| `--no-security` | 跳過安全漏洞檢查 |
| `--no-outdated` | 跳過過時依賴檢查 |
| `--no-deprecated` | 跳過廢棄套件檢查 |
| `--no-dev` | 排除開發依賴 |
| `--offline` | 離線模式 |
| `--timeout SECONDS` | 網路請求逾時時間（預設：30秒） |
| `--no-color` | 停用彩色輸出 |
| `--quiet, -q` | 靜默模式 |

### 支援的套件管理器

| 套件管理器 | 依賴檔案 |
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

### CI/CD 整合範例

```yaml
# GitHub Actions 範例
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

## 💡 設計思路與迭代規劃

### 設計理念

DepHealth 的設計遵循以下原則：

1. **零依賴優先**：核心功能不依賴任何第三方函式庫，降低安裝門檻
2. **多語言支援**：支援主流程式語言的套件管理器
3. **安全第一**：整合權威漏洞資料庫，確保安全檢測的準確性
4. **開發者友善**：提供美觀的終端輸出和多種報告格式

### 技術選型

- **純Python標準庫**：使用`urllib`進行網路請求，`json`解析資料
- **正規表示式解析**：輕量級解析各種依賴檔案格式
- **OSV API整合**：使用Google維護的開源漏洞資料庫

### 後續迭代計劃

- [ ] 新增依賴關係圖視覺化
- [ ] 支援更多套件管理器（NuGet、CPAN等）
- [ ] 新增自動修復建議
- [ ] 支援設定檔（.dephealth.yaml）
- [ ] 新增Web UI介面
- [ ] 支援依賴授權合規檢查

---

## 📦 打包與部署指南

### 本地開發

```bash
# 複製儲存庫
git clone https://github.com/gitstq/DepHealth.git
cd DepHealth

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest

# 程式碼格式化
black dephealth tests
isort dephealth tests

# 類型檢查
mypy dephealth
```

### 建構發布

```bash
# 安裝建構工具
pip install build twine

# 建構
python -m build

# 檢查
twine check dist/*

# 上傳到PyPI
twine upload dist/*
```

---

## 🤝 貢獻指南

我們歡迎所有形式的貢獻！

### 如何貢獻

1. Fork 本儲存庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立 Pull Request

### 提交規範

請遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

- `feat:` 新功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建構/工具相關

---

## 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

<p align="center">
  Made with ❤️ by DepHealth Team
</p>
