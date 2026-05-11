#!/usr/bin/env python3
"""
Reporter module for DepHealth - generates health reports
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO

from .core import AnalysisResult, Dependency, HealthScore, PackageManager, Severity


class HealthReporter:
    """Generate dependency health reports in various formats"""
    
    def __init__(self, result: AnalysisResult):
        self.result = result
    
    def generate_text_report(self, output: Optional[TextIO] = None) -> str:
        """Generate a text-based report"""
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("  DepHealth - Dependency Health Report")
        lines.append("=" * 60)
        lines.append("")
        
        # Project info
        lines.append(f"📁 Project: {self.result.project_path}")
        lines.append(f"📅 Analyzed: {self.result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"⏱️  Analysis time: {self.result.analysis_time:.2f}s")
        lines.append("")
        
        # Package managers
        if self.result.package_managers:
            pms = ", ".join(pm.value for pm in self.result.package_managers)
            lines.append(f"📦 Package Managers: {pms}")
        lines.append("")
        
        # Summary
        lines.append("-" * 60)
        lines.append("  📊 Summary")
        lines.append("-" * 60)
        lines.append(f"  Total Dependencies:    {self.result.total_dependencies}")
        lines.append(f"  Direct Dependencies:   {self.result.direct_dependencies}")
        lines.append(f"  Dev Dependencies:      {self.result.dev_dependencies}")
        lines.append(f"  Outdated:              {self.result.outdated_count}")
        lines.append(f"  Vulnerable:            {self.result.vulnerable_count}")
        lines.append(f"  Deprecated:            {self.result.deprecated_count}")
        lines.append("")
        
        # Health Score
        lines.append("-" * 60)
        lines.append("  🏥 Health Score")
        lines.append("-" * 60)
        score = self.result.health_score
        lines.append(f"  Overall:       {self._score_bar(score.overall)} {score.overall:.1f} ({score.grade})")
        lines.append(f"  Security:      {self._score_bar(score.security)} {score.security:.1f}")
        lines.append(f"  Freshness:     {self._score_bar(score.freshness)} {score.freshness:.1f}")
        lines.append(f"  Compatibility: {self._score_bar(score.compatibility)} {score.compatibility:.1f}")
        lines.append(f"  Maintenance:   {self._score_bar(score.maintenance)} {score.maintenance:.1f}")
        lines.append("")
        
        # Vulnerabilities
        vulnerable_deps = [d for d in self.result.dependencies if d.has_vulnerabilities]
        if vulnerable_deps:
            lines.append("-" * 60)
            lines.append("  🔒 Security Issues")
            lines.append("-" * 60)
            for dep in vulnerable_deps:
                lines.append(f"  ⚠️  {dep.name}@{dep.current_version}")
                for vuln in dep.vulnerabilities:
                    sev = vuln.get("severity", "unknown").upper()
                    lines.append(f"      [{sev}] {vuln.get('id', 'N/A')}: {vuln.get('summary', '')[:50]}")
            lines.append("")
        
        # Outdated packages
        outdated_deps = [d for d in self.result.dependencies if d.is_outdated]
        if outdated_deps:
            lines.append("-" * 60)
            lines.append("  📦 Outdated Dependencies")
            lines.append("-" * 60)
            for dep in outdated_deps[:20]:  # Limit to 20
                lines.append(f"  • {dep.name}: {dep.current_version} → {dep.latest_version}")
            if len(outdated_deps) > 20:
                lines.append(f"  ... and {len(outdated_deps) - 20} more")
            lines.append("")
        
        # Deprecated packages
        deprecated_deps = [d for d in self.result.dependencies if d.deprecated]
        if deprecated_deps:
            lines.append("-" * 60)
            lines.append("  ⚠️  Deprecated Dependencies")
            lines.append("-" * 60)
            for dep in deprecated_deps:
                lines.append(f"  • {dep.name}@{dep.current_version}")
                if dep.deprecated_message:
                    lines.append(f"    {dep.deprecated_message[:60]}")
            lines.append("")
        
        # Errors and warnings
        if self.result.errors:
            lines.append("-" * 60)
            lines.append("  ❌ Errors")
            lines.append("-" * 60)
            for error in self.result.errors:
                lines.append(f"  • {error}")
            lines.append("")
        
        if self.result.warnings:
            lines.append("-" * 60)
            lines.append("  ⚠️  Warnings")
            lines.append("-" * 60)
            for warning in self.result.warnings:
                lines.append(f"  • {warning}")
            lines.append("")
        
        # Footer
        lines.append("=" * 60)
        lines.append("  Generated by DepHealth")
        lines.append("=" * 60)
        
        report = "\n".join(lines)
        
        if output:
            output.write(report)
        
        return report
    
    def generate_json_report(self, output: Optional[TextIO] = None) -> str:
        """Generate a JSON report"""
        data = {
            "project": {
                "path": str(self.result.project_path),
                "timestamp": self.result.timestamp.isoformat(),
                "analysis_time": self.result.analysis_time,
            },
            "package_managers": [pm.value for pm in self.result.package_managers],
            "summary": {
                "total_dependencies": self.result.total_dependencies,
                "direct_dependencies": self.result.direct_dependencies,
                "dev_dependencies": self.result.dev_dependencies,
                "outdated_count": self.result.outdated_count,
                "vulnerable_count": self.result.vulnerable_count,
                "deprecated_count": self.result.deprecated_count,
            },
            "health_score": {
                "overall": self.result.health_score.overall,
                "grade": self.result.health_score.grade,
                "security": self.result.health_score.security,
                "freshness": self.result.health_score.freshness,
                "compatibility": self.result.health_score.compatibility,
                "maintenance": self.result.health_score.maintenance,
            },
            "dependencies": [],
            "vulnerabilities": [],
            "outdated": [],
            "deprecated": [],
            "errors": self.result.errors,
            "warnings": self.result.warnings,
        }
        
        # Add dependencies
        for dep in self.result.dependencies:
            dep_data = {
                "name": dep.name,
                "current_version": dep.current_version,
                "latest_version": dep.latest_version,
                "is_outdated": dep.is_outdated,
                "is_dev": dep.is_dev,
                "package_manager": dep.package_manager.value,
                "deprecated": dep.deprecated,
                "vulnerabilities": dep.vulnerabilities,
            }
            data["dependencies"].append(dep_data)
            
            if dep.has_vulnerabilities:
                data["vulnerabilities"].append({
                    "name": dep.name,
                    "version": dep.current_version,
                    "vulnerabilities": dep.vulnerabilities,
                })
            
            if dep.is_outdated:
                data["outdated"].append({
                    "name": dep.name,
                    "current": dep.current_version,
                    "latest": dep.latest_version,
                })
            
            if dep.deprecated:
                data["deprecated"].append({
                    "name": dep.name,
                    "version": dep.current_version,
                    "message": dep.deprecated_message,
                })
        
        report = json.dumps(data, indent=2)
        
        if output:
            output.write(report)
        
        return report
    
    def generate_markdown_report(self, output: Optional[TextIO] = None) -> str:
        """Generate a Markdown report"""
        lines = []
        
        # Header
        lines.append("# 🏥 DepHealth Report")
        lines.append("")
        lines.append(f"**Project:** `{self.result.project_path}`")
        lines.append(f"**Analyzed:** {self.result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Analysis Time:** {self.result.analysis_time:.2f}s")
        lines.append("")
        
        # Summary
        lines.append("## 📊 Summary")
        lines.append("")
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Dependencies | {self.result.total_dependencies} |")
        lines.append(f"| Direct Dependencies | {self.result.direct_dependencies} |")
        lines.append(f"| Dev Dependencies | {self.result.dev_dependencies} |")
        lines.append(f"| Outdated | {self.result.outdated_count} |")
        lines.append(f"| Vulnerable | {self.result.vulnerable_count} |")
        lines.append(f"| Deprecated | {self.result.deprecated_count} |")
        lines.append("")
        
        # Health Score
        lines.append("## 🏥 Health Score")
        lines.append("")
        score = self.result.health_score
        lines.append(f"**Overall Grade:** `{score.grade}` ({score.overall:.1f}/100)")
        lines.append("")
        lines.append("| Category | Score |")
        lines.append("|----------|-------|")
        lines.append(f"| Security | {score.security:.1f} |")
        lines.append(f"| Freshness | {score.freshness:.1f} |")
        lines.append(f"| Compatibility | {score.compatibility:.1f} |")
        lines.append(f"| Maintenance | {score.maintenance:.1f} |")
        lines.append("")
        
        # Vulnerabilities
        vulnerable_deps = [d for d in self.result.dependencies if d.has_vulnerabilities]
        if vulnerable_deps:
            lines.append("## 🔒 Security Issues")
            lines.append("")
            for dep in vulnerable_deps:
                lines.append(f"### {dep.name}@{dep.current_version}")
                lines.append("")
                for vuln in dep.vulnerabilities:
                    sev = vuln.get("severity", "unknown").upper()
                    lines.append(f"- **[{sev}]** {vuln.get('id', 'N/A')}")
                    lines.append(f"  - {vuln.get('summary', 'No summary')}")
                    if vuln.get("url"):
                        lines.append(f"  - [More info]({vuln['url']})")
                lines.append("")
        
        # Outdated
        outdated_deps = [d for d in self.result.dependencies if d.is_outdated]
        if outdated_deps:
            lines.append("## 📦 Outdated Dependencies")
            lines.append("")
            lines.append("| Package | Current | Latest |")
            lines.append("|---------|---------|--------|")
            for dep in outdated_deps:
                lines.append(f"| {dep.name} | {dep.current_version} | {dep.latest_version} |")
            lines.append("")
        
        # Deprecated
        deprecated_deps = [d for d in self.result.dependencies if d.deprecated]
        if deprecated_deps:
            lines.append("## ⚠️ Deprecated Dependencies")
            lines.append("")
            for dep in deprecated_deps:
                lines.append(f"- **{dep.name}@{dep.current_version}**")
                if dep.deprecated_message:
                    lines.append(f"  - {dep.deprecated_message}")
            lines.append("")
        
        report = "\n".join(lines)
        
        if output:
            output.write(report)
        
        return report
    
    def generate_html_report(self, output: Optional[TextIO] = None) -> str:
        """Generate an HTML report"""
        score = self.result.health_score
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DepHealth Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .score-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .score-item {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .score-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .score-label {{
            color: #666;
            margin-top: 5px;
        }}
        .grade {{
            font-size: 3em;
            font-weight: bold;
        }}
        .grade-a {{ color: #28a745; }}
        .grade-b {{ color: #17a2b8; }}
        .grade-c {{ color: #ffc107; }}
        .grade-d {{ color: #fd7e14; }}
        .grade-f {{ color: #dc3545; }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
        }}
        .severity-critical {{ color: #dc3545; font-weight: bold; }}
        .severity-high {{ color: #fd7e14; }}
        .severity-medium {{ color: #ffc107; }}
        .severity-low {{ color: #17a2b8; }}
        .progress-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        .progress-good {{ background: linear-gradient(90deg, #28a745, #20c997); }}
        .progress-medium {{ background: linear-gradient(90deg, #ffc107, #fd7e14); }}
        .progress-bad {{ background: linear-gradient(90deg, #fd7e14, #dc3545); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 DepHealth Report</h1>
        <p>Project: {self.result.project_path}</p>
        <p>Analyzed: {self.result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="card">
        <h2>📊 Summary</h2>
        <div class="score-grid">
            <div class="score-item">
                <div class="score-value">{self.result.total_dependencies}</div>
                <div class="score-label">Total Dependencies</div>
            </div>
            <div class="score-item">
                <div class="score-value">{self.result.outdated_count}</div>
                <div class="score-label">Outdated</div>
            </div>
            <div class="score-item">
                <div class="score-value">{self.result.vulnerable_count}</div>
                <div class="score-label">Vulnerable</div>
            </div>
            <div class="score-item">
                <div class="score-value">{self.result.deprecated_count}</div>
                <div class="score-label">Deprecated</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>🏥 Health Score</h2>
        <div class="score-grid">
            <div class="score-item">
                <div class="grade grade-{score.grade.lower().replace('+', '-plus').replace('-', '-minus')}">{score.grade}</div>
                <div class="score-label">Overall Grade</div>
                <div class="progress-bar" style="margin-top: 10px;">
                    <div class="progress-fill {self._get_progress_class(score.overall)}" style="width: {score.overall}%;"></div>
                </div>
            </div>
            <div class="score-item">
                <div class="score-value">{score.security:.0f}</div>
                <div class="score-label">Security</div>
            </div>
            <div class="score-item">
                <div class="score-value">{score.freshness:.0f}</div>
                <div class="score-label">Freshness</div>
            </div>
            <div class="score-item">
                <div class="score-value">{score.compatibility:.0f}</div>
                <div class="score-label">Compatibility</div>
            </div>
        </div>
    </div>
"""
        
        # Add vulnerabilities section
        vulnerable_deps = [d for d in self.result.dependencies if d.has_vulnerabilities]
        if vulnerable_deps:
            html += """
    <div class="card">
        <h2>🔒 Security Issues</h2>
        <table>
            <thead>
                <tr>
                    <th>Package</th>
                    <th>Severity</th>
                    <th>Vulnerability</th>
                    <th>Summary</th>
                </tr>
            </thead>
            <tbody>
"""
            for dep in vulnerable_deps:
                for vuln in dep.vulnerabilities:
                    sev = vuln.get("severity", "unknown").lower()
                    html += f"""
                <tr>
                    <td>{dep.name}@{dep.current_version}</td>
                    <td class="severity-{sev}">{sev.upper()}</td>
                    <td>{vuln.get('id', 'N/A')}</td>
                    <td>{vuln.get('summary', '')[:50]}</td>
                </tr>
"""
            html += """
            </tbody>
        </table>
    </div>
"""
        
        # Add outdated section
        outdated_deps = [d for d in self.result.dependencies if d.is_outdated]
        if outdated_deps:
            html += """
    <div class="card">
        <h2>📦 Outdated Dependencies</h2>
        <table>
            <thead>
                <tr>
                    <th>Package</th>
                    <th>Current</th>
                    <th>Latest</th>
                </tr>
            </thead>
            <tbody>
"""
            for dep in outdated_deps[:50]:
                html += f"""
                <tr>
                    <td>{dep.name}</td>
                    <td>{dep.current_version}</td>
                    <td>{dep.latest_version}</td>
                </tr>
"""
            html += """
            </tbody>
        </table>
    </div>
"""
        
        html += """
    <div class="card">
        <p style="text-align: center; color: #666;">
            Generated by <strong>DepHealth</strong> - Lightweight Dependency Health Intelligence Engine
        </p>
    </div>
</body>
</html>
"""
        
        if output:
            output.write(html)
        
        return html
    
    def save_report(self, path: Path, format: str = "text") -> None:
        """Save report to file"""
        path = Path(path)
        
        with open(path, "w", encoding="utf-8") as f:
            if format == "json":
                self.generate_json_report(f)
            elif format == "markdown" or format == "md":
                self.generate_markdown_report(f)
            elif format == "html":
                self.generate_html_report(f)
            else:
                self.generate_text_report(f)
    
    def _score_bar(self, score: float, width: int = 20) -> str:
        """Generate a text-based score bar"""
        filled = int(score / 100 * width)
        bar = "█" * filled + "░" * (width - filled)
        
        if score >= 80:
            return f"[green]{bar}[/green]"
        elif score >= 60:
            return f"[yellow]{bar}[/yellow]"
        else:
            return f"[red]{bar}[/red]"
    
    def _get_progress_class(self, score: float) -> str:
        """Get CSS class for progress bar"""
        if score >= 80:
            return "progress-good"
        elif score >= 60:
            return "progress-medium"
        return "progress-bad"
