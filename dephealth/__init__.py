#!/usr/bin/env python3
"""
DepHealth - Lightweight Dependency Health Intelligence Analysis Engine
轻量级代码依赖健康度智能分析引擎

A comprehensive CLI tool for analyzing project dependency health across
multiple package managers with security vulnerability detection,
outdated dependency analysis, and AI-powered upgrade suggestions.
"""

__version__ = "1.0.0"
__author__ = "DepHealth Team"
__license__ = "MIT"

from dephealth.core import DepHealthAnalyzer
from dephealth.scanner import DependencyScanner
from dephealth.reporter import HealthReporter
from dephealth.security import SecurityChecker
from dephealth.tui import DepHealthTUI

__all__ = [
    "DepHealthAnalyzer",
    "DependencyScanner",
    "HealthReporter",
    "SecurityChecker",
    "DepHealthTUI",
]
