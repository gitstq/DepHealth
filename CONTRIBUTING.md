# Contributing to DepHealth

First off, thank you for considering contributing to DepHealth! It's people like you that make DepHealth such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what you expected**
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain the expected behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible
- Follow the Python style guide
- Include tests for new functionality
- Update documentation for changed functionality

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setup

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/DepHealth.git
cd DepHealth

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check dephealth

# Run type checking
mypy dephealth
```

## Style Guide

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Maximum line length is 100 characters
- Use type hints for all function signatures

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation only changes
- `style:` Changes that do not affect the meaning of the code
- `refactor:` A code change that neither fixes a bug nor adds a feature
- `perf:` A code change that improves performance
- `test:` Adding missing tests or correcting existing tests
- `chore:` Changes to the build process or auxiliary tools

Example:
```
feat: add support for NuGet package manager

- Add NuGet package detection
- Parse packages.config and *.csproj files
- Query NuGet API for latest versions
```

## Project Structure

```
DepHealth/
├── dephealth/           # Main package
│   ├── __init__.py     # Package initialization
│   ├── cli.py          # Command line interface
│   ├── core.py         # Core analyzer logic
│   ├── scanner.py      # Dependency scanner
│   ├── security.py     # Security checker
│   ├── reporter.py     # Report generator
│   └── tui.py          # Terminal UI
├── tests/              # Test suite
├── docs/               # Documentation
├── README.md           # Main README
├── pyproject.toml      # Project configuration
└── LICENSE             # MIT License
```

## Adding Support for a New Package Manager

1. Add the package manager to the `PackageManager` enum in `core.py`
2. Add the dependency file patterns to `PACKAGE_FILES` in `DepHealthAnalyzer`
3. Implement the scanning method in `DependencyScanner`
4. Implement the version fetching method if applicable
5. Add tests for the new package manager
6. Update documentation

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a PR
- Aim for high test coverage (80%+)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dephealth --cov-report=html
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features

## License

By contributing to DepHealth, you agree that your contributions will be licensed under the MIT License.
