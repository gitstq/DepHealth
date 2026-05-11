# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-05-11

### Added
- 🎉 Initial release of DepHealth
- 🔍 Smart dependency scanning for multiple package managers
  - Python: pip, Poetry (requirements.txt, pyproject.toml, setup.py, setup.cfg)
  - Node.js: npm, Yarn, pnpm (package.json)
  - Rust: Cargo (Cargo.toml)
  - Go: Go Modules (go.mod)
  - Java: Maven, Gradle (pom.xml, build.gradle)
  - PHP: Composer (composer.json)
  - Ruby: RubyGems (Gemfile)
  - Dart: Pub (pubspec.yaml)
- 🔒 Security vulnerability detection via OSV API
- 📦 Outdated dependency analysis
- ⚠️ Deprecated package detection
- 📊 Health score calculation (Security, Freshness, Compatibility, Maintenance)
- 📄 Multi-format report output
  - Terminal colored output
  - JSON format
  - Markdown format
  - HTML format
- 🎨 Beautiful TUI interface
- 🚀 Zero dependencies - pure Python standard library
- 🌐 Multi-language README documentation (Chinese, English, Traditional Chinese)

### Features
- Cross-platform support (Linux, macOS, Windows)
- Offline mode for network-restricted environments
- CI/CD friendly with JSON output
- Configurable timeout settings
- Single package vulnerability check

### Documentation
- Comprehensive README with examples
- API documentation in code
- CI/CD integration examples

[1.0.0]: https://github.com/gitstq/DepHealth/releases/tag/v1.0.0
