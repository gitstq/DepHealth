#!/usr/bin/env python3
"""
DepHealth CLI - Command Line Interface
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from dephealth import __version__
from dephealth.core import DepHealthAnalyzer, PackageManager
from dephealth.reporter import HealthReporter
from dephealth.tui import DepHealthTUI


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog="dephealth",
        description="🏥 DepHealth - Lightweight Dependency Health Intelligence Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dephealth                    Analyze current directory
  dephealth ./my-project       Analyze specific project
  dephealth --json             Output JSON report
  dephealth --html report.html Save HTML report
  dephealth --no-security      Skip security checks
  dephealth --offline          Run in offline mode

For more information, visit: https://github.com/gitstq/DepHealth
        """,
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to project directory (default: current directory)",
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report in JSON format",
    )
    
    parser.add_argument(
        "--markdown", "--md",
        action="store_true",
        help="Output report in Markdown format",
    )
    
    parser.add_argument(
        "--html",
        metavar="FILE",
        help="Save HTML report to file",
    )
    
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Save report to file (format determined by extension)",
    )
    
    parser.add_argument(
        "--no-security",
        action="store_true",
        help="Skip security vulnerability checks",
    )
    
    parser.add_argument(
        "--no-outdated",
        action="store_true",
        help="Skip outdated package checks",
    )
    
    parser.add_argument(
        "--no-deprecated",
        action="store_true",
        help="Skip deprecated package checks",
    )
    
    parser.add_argument(
        "--no-dev",
        action="store_true",
        help="Exclude dev dependencies from analysis",
    )
    
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run in offline mode (skip network checks)",
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Network request timeout in seconds (default: 30)",
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress messages",
    )
    
    parser.add_argument(
        "--only",
        metavar="PM",
        choices=["pip", "npm", "yarn", "pnpm", "cargo", "go", "maven", "composer", "gem"],
        help="Only analyze dependencies for specified package manager",
    )
    
    parser.add_argument(
        "--check-single",
        nargs=2,
        metavar=("PACKAGE", "VERSION"),
        help="Check a single package for vulnerabilities",
    )
    
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point"""
    parser = create_parser()
    opts = parser.parse_args(args)
    
    # Initialize TUI
    tui = DepHealthTUI(use_color=not opts.no_color)
    
    # Check single package mode
    if opts.check_single:
        return check_single_package(opts.check_single[0], opts.check_single[1], tui)
    
    # Validate path
    project_path = Path(opts.path).resolve()
    if not project_path.exists():
        tui.display_error(f"Path does not exist: {project_path}")
        return 1
    
    if not project_path.is_dir():
        tui.display_error(f"Path is not a directory: {project_path}")
        return 1
    
    # Display header
    if not opts.json and not opts.markdown and not opts.quiet:
        tui.display_header()
    
    # Create analyzer
    analyzer = DepHealthAnalyzer(
        project_path=project_path,
        check_security=not opts.no_security,
        check_outdated=not opts.no_outdated,
        check_deprecated=not opts.no_deprecated,
        include_dev=not opts.no_dev,
        offline_mode=opts.offline,
        timeout=opts.timeout,
    )
    
    # Run analysis
    if not opts.json and not opts.markdown and not opts.quiet:
        tui.display_progress("Scanning dependencies...")
    
    result = analyzer.analyze()
    
    if not opts.json and not opts.markdown and not opts.quiet:
        tui.display_progress("Analysis complete", done=True)
    
    # Create reporter
    reporter = HealthReporter(result)
    
    # Output results
    if opts.json:
        print(reporter.generate_json_report())
    elif opts.markdown:
        print(reporter.generate_markdown_report())
    else:
        tui.display_result(result)
    
    # Save HTML report if requested
    if opts.html:
        reporter.save_report(Path(opts.html), format="html")
        if not opts.quiet:
            tui.display_success(f"HTML report saved to {opts.html}")
    
    # Save to output file if requested
    if opts.output:
        output_path = Path(opts.output)
        ext = output_path.suffix.lower()
        format_map = {
            ".json": "json",
            ".md": "markdown",
            ".markdown": "markdown",
            ".html": "html",
            ".htm": "html",
            ".txt": "text",
        }
        fmt = format_map.get(ext, "text")
        reporter.save_report(output_path, format=fmt)
        if not opts.quiet:
            tui.display_success(f"Report saved to {opts.output}")
    
    # Return exit code based on health
    if result.vulnerable_count > 0:
        return 2  # Security issues found
    if result.health_score.overall < 50:
        return 1  # Poor health
    
    return 0


def check_single_package(name: str, version: str, tui: DepHealthTUI) -> int:
    """Check a single package for vulnerabilities"""
    from dephealth.security import SecurityChecker
    
    tui.display_header()
    tui.display_info(f"Checking {name}@{version}...")
    
    checker = SecurityChecker()
    
    # Try different package managers
    for pm in [PackageManager.PIP, PackageManager.NPM, PackageManager.CARGO]:
        vulns = checker.check_single_package(name, version, pm)
        if vulns:
            break
    
    if not vulns:
        tui.display_success(f"No known vulnerabilities found for {name}@{version}")
        return 0
    
    print()
    print(f"  {tui.color('🔒 Vulnerabilities Found', 'red')}")
    print(f"  {'─' * 50}")
    
    for vuln in vulns:
        sev_color = tui._get_severity_color(vuln.severity.value)
        print(f"  [{tui.color(vuln.severity.value.upper(), sev_color)}] {vuln.id}")
        print(f"      {vuln.title}")
        if vuln.patched_versions:
            print(f"      Fix: Upgrade to {vuln.patched_versions[0]} or later")
        print()
    
    return 2


if __name__ == "__main__":
    sys.exit(main())
