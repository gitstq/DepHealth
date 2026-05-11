#!/usr/bin/env python3
"""
TUI module for DepHealth - Terminal User Interface
"""

import sys
from pathlib import Path
from typing import List, Optional

from .core import AnalysisResult, Dependency, HealthScore, PackageManager, Severity


class DepHealthTUI:
    """Terminal User Interface for DepHealth"""
    
    # Color codes
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bg_red": "\033[41m",
        "bg_green": "\033[42m",
        "bg_yellow": "\033[43m",
        "bg_blue": "\033[44m",
    }
    
    # Box drawing characters
    BOX = {
        "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
        "h": "═", "v": "║",
        "lt": "╠", "rt": "╣", "tt": "╦", "bt": "╩", "cr": "╬",
    }
    
    def __init__(self, use_color: bool = True):
        self.use_color = use_color and sys.stdout.isatty()
    
    def color(self, text: str, color: str) -> str:
        """Apply color to text"""
        if not self.use_color or color not in self.COLORS:
            return text
        return f"{self.COLORS[color]}{text}{self.COLORS['reset']}"
    
    def bold(self, text: str) -> str:
        """Make text bold"""
        if not self.use_color:
            return text
        return f"{self.COLORS['bold']}{text}{self.COLORS['reset']}"
    
    def display_header(self) -> None:
        """Display application header"""
        lines = [
            "",
            "  ╔═══════════════════════════════════════════════════════════╗",
            "  ║                                                           ║",
            "  ║   🏥 DepHealth - Dependency Health Intelligence Engine    ║",
            "  ║                                                           ║",
            "  ║   Lightweight CLI for analyzing project dependencies      ║",
            "  ║                                                           ║",
            "  ╚═══════════════════════════════════════════════════════════╝",
            "",
        ]
        print("\n".join(lines))
    
    def display_progress(self, message: str, done: bool = False) -> None:
        """Display progress message"""
        if done:
            print(f"\r  {self.color('✓', 'green')} {message}    ")
        else:
            print(f"\r  {self.color('⏳', 'yellow')} {message}...", end="", flush=True)
    
    def display_result(self, result: AnalysisResult) -> None:
        """Display analysis result"""
        self._display_summary(result)
        self._display_health_score(result.health_score)
        
        if result.vulnerable_count > 0:
            self._display_vulnerabilities(result)
        
        if result.outdated_count > 0:
            self._display_outdated(result)
        
        if result.deprecated_count > 0:
            self._display_deprecated(result)
        
        if result.errors:
            self._display_errors(result.errors)
        
        if result.warnings:
            self._display_warnings(result.warnings)
    
    def _display_summary(self, result: AnalysisResult) -> None:
        """Display summary section"""
        print()
        print(f"  {self.color('📊 Summary', 'cyan')}")
        print(f"  {'─' * 50}")
        print(f"  📁 Project:        {result.project_path}")
        print(f"  📦 Package Mgrs:   {', '.join(pm.value for pm in result.package_managers) or 'None detected'}")
        print(f"  📅 Analyzed:       {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  ⏱️  Time:           {result.analysis_time:.2f}s")
        print()
        
        # Stats
        print(f"  {'─' * 50}")
        print(f"  Total Dependencies:    {self._format_count(result.total_dependencies)}")
        print(f"  Direct Dependencies:   {self._format_count(result.direct_dependencies)}")
        print(f"  Dev Dependencies:      {self._format_count(result.dev_dependencies)}")
        print(f"  Outdated:              {self._format_count(result.outdated_count, 'yellow')}")
        print(f"  Vulnerable:            {self._format_count(result.vulnerable_count, 'red')}")
        print(f"  Deprecated:            {self._format_count(result.deprecated_count, 'yellow')}")
        print()
    
    def _display_health_score(self, score: HealthScore) -> None:
        """Display health score section"""
        print(f"  {self.color('🏥 Health Score', 'cyan')}")
        print(f"  {'─' * 50}")
        
        # Overall grade
        grade_color = self._get_grade_color(score.grade)
        print(f"  Overall Grade:  {self.color(score.grade, grade_color)} ({score.overall:.1f}/100)")
        print()
        
        # Score bars
        print(f"  Security:       {self._score_bar(score.security)} {score.security:.1f}")
        print(f"  Freshness:      {self._score_bar(score.freshness)} {score.freshness:.1f}")
        print(f"  Compatibility:  {self._score_bar(score.compatibility)} {score.compatibility:.1f}")
        print(f"  Maintenance:    {self._score_bar(score.maintenance)} {score.maintenance:.1f}")
        print()
    
    def _display_vulnerabilities(self, result: AnalysisResult) -> None:
        """Display vulnerabilities section"""
        vulnerable = [d for d in result.dependencies if d.has_vulnerabilities]
        
        print(f"  {self.color('🔒 Security Issues', 'red')}")
        print(f"  {'─' * 50}")
        
        for dep in vulnerable[:10]:
            print(f"  {self.color('⚠️', 'red')} {dep.name}@{dep.current_version}")
            for vuln in dep.vulnerabilities[:3]:
                sev = vuln.get("severity", "unknown").upper()
                sev_color = self._get_severity_color(sev)
                vuln_id = vuln.get("id", "N/A")
                summary = vuln.get("summary", "")[:40]
                print(f"      [{self.color(sev, sev_color)}] {vuln_id}: {summary}")
        
        if len(vulnerable) > 10:
            print(f"  ... and {len(vulnerable) - 10} more vulnerable packages")
        print()
    
    def _display_outdated(self, result: AnalysisResult) -> None:
        """Display outdated dependencies section"""
        outdated = [d for d in result.dependencies if d.is_outdated]
        
        print(f"  {self.color('📦 Outdated Dependencies', 'yellow')}")
        print(f"  {'─' * 50}")
        
        for dep in outdated[:15]:
            current = self.color(dep.current_version, "yellow")
            latest = self.color(dep.latest_version, "green")
            print(f"  • {dep.name}: {current} → {latest}")
        
        if len(outdated) > 15:
            print(f"  ... and {len(outdated) - 15} more outdated packages")
        print()
    
    def _display_deprecated(self, result: AnalysisResult) -> None:
        """Display deprecated dependencies section"""
        deprecated = [d for d in result.dependencies if d.deprecated]
        
        print(f"  {self.color('⚠️ Deprecated Dependencies', 'magenta')}")
        print(f"  {'─' * 50}")
        
        for dep in deprecated[:10]:
            print(f"  • {dep.name}@{dep.current_version}")
            if dep.deprecated_message:
                print(f"    {dep.deprecated_message[:60]}")
        
        if len(deprecated) > 10:
            print(f"  ... and {len(deprecated) - 10} more deprecated packages")
        print()
    
    def _display_errors(self, errors: List[str]) -> None:
        """Display errors section"""
        print(f"  {self.color('❌ Errors', 'red')}")
        print(f"  {'─' * 50}")
        for error in errors:
            print(f"  • {error}")
        print()
    
    def _display_warnings(self, warnings: List[str]) -> None:
        """Display warnings section"""
        print(f"  {self.color('⚠️ Warnings', 'yellow')}")
        print(f"  {'─' * 50}")
        for warning in warnings:
            print(f"  • {warning}")
        print()
    
    def display_dependency_list(self, dependencies: List[Dependency], title: str = "Dependencies") -> None:
        """Display a list of dependencies"""
        print(f"  {self.color(f'📋 {title}', 'cyan')}")
        print(f"  {'─' * 50}")
        
        for dep in dependencies[:50]:
            status = ""
            if dep.has_vulnerabilities:
                status += self.color(" 🔒", "red")
            if dep.is_outdated:
                status += self.color(" ⬆️", "yellow")
            if dep.deprecated:
                status += self.color(" ⚠️", "magenta")
            
            dev_marker = " (dev)" if dep.is_dev else ""
            print(f"  • {dep.name}@{dep.current_version}{dev_marker}{status}")
        
        if len(dependencies) > 50:
            print(f"  ... and {len(dependencies) - 50} more")
        print()
    
    def display_interactive_menu(self) -> str:
        """Display interactive menu and get user choice"""
        print()
        print(f"  {self.color('🎮 Options', 'cyan')}")
        print(f"  {'─' * 50}")
        print("  [1] View all dependencies")
        print("  [2] View outdated only")
        print("  [3] View vulnerable only")
        print("  [4] Export report (JSON)")
        print("  [5] Export report (HTML)")
        print("  [q] Quit")
        print()
        
        return input("  Choose an option: ").strip().lower()
    
    def _format_count(self, count: int, color: str = "white") -> str:
        """Format count with color"""
        if count == 0:
            return self.color(str(count), "green")
        return self.color(str(count), color)
    
    def _score_bar(self, score: float, width: int = 20) -> str:
        """Generate a text-based score bar"""
        filled = int(score / 100 * width)
        empty = width - filled
        
        if score >= 80:
            fill_char = self.color("█", "green")
        elif score >= 60:
            fill_char = self.color("█", "yellow")
        else:
            fill_char = self.color("█", "red")
        
        empty_char = "░"
        return f"{fill_char * filled}{empty_char * empty}"
    
    def _get_grade_color(self, grade: str) -> str:
        """Get color for grade"""
        if grade.startswith("A"):
            return "green"
        elif grade.startswith("B"):
            return "cyan"
        elif grade.startswith("C"):
            return "yellow"
        elif grade.startswith("D"):
            return "red"
        return "red"
    
    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        colors = {
            "CRITICAL": "red",
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "blue",
            "INFO": "cyan",
        }
        return colors.get(severity.upper(), "white")
    
    def display_error(self, message: str) -> None:
        """Display error message"""
        print(f"\n  {self.color('❌ Error:', 'red')} {message}\n")
    
    def display_success(self, message: str) -> None:
        """Display success message"""
        print(f"\n  {self.color('✓', 'green')} {message}\n")
    
    def display_info(self, message: str) -> None:
        """Display info message"""
        print(f"  {self.color('ℹ️', 'cyan')} {message}")
    
    def clear_screen(self) -> None:
        """Clear terminal screen"""
        print("\033[2J\033[H", end="")
