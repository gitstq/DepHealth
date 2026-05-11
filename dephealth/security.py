#!/usr/bin/env python3
"""
Security checker module for DepHealth
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .core import Dependency, PackageManager, Severity


@dataclass
class Vulnerability:
    """Represents a security vulnerability"""
    id: str
    package_name: str
    severity: Severity
    title: str
    description: str
    affected_versions: List[str]
    patched_versions: List[str]
    cwe_ids: List[str] = field(default_factory=list)
    cve_ids: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    published_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    
    @property
    def severity_color(self) -> str:
        """Get color for severity level"""
        colors = {
            Severity.CRITICAL: "bright_red",
            Severity.HIGH: "red",
            Severity.MEDIUM: "yellow",
            Severity.LOW: "blue",
            Severity.INFO: "cyan",
        }
        return colors.get(self.severity, "white")


@dataclass
class SecurityCheckResult:
    """Result of security check"""
    total_vulnerabilities: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    vulnerabilities: List[Vulnerability]
    checked_packages: int
    check_time: float
    errors: List[str] = field(default_factory=list)


class SecurityChecker:
    """Check for security vulnerabilities in dependencies"""
    
    # Map package managers to OSV ecosystems
    ECOSYSTEM_MAP = {
        PackageManager.PIP: "PyPI",
        PackageManager.POETRY: "PyPI",
        PackageManager.NPM: "npm",
        PackageManager.YARN: "npm",
        PackageManager.PNPM: "npm",
        PackageManager.CARGO: "crates.io",
        PackageManager.GO: "Go",
        PackageManager.MAVEN: "Maven",
        PackageManager.GRADLE: "Maven",
        PackageManager.COMPOSER: "Packagist",
        PackageManager.GEM: "RubyGems",
        PackageManager.PUB: "Pub",
    }
    
    def __init__(self, timeout: int = 30, batch_size: int = 20):
        self.timeout = timeout
        self.batch_size = batch_size
    
    def check(self, dependencies: List[Dependency]) -> SecurityCheckResult:
        """Check dependencies for vulnerabilities"""
        import time
        start_time = time.time()
        
        vulnerabilities: List[Vulnerability] = []
        errors: List[str] = []
        checked = 0
        
        # Group by ecosystem for batch queries
        by_ecosystem: Dict[str, List[Dependency]] = {}
        for dep in dependencies:
            ecosystem = self.ECOSYSTEM_MAP.get(dep.package_manager)
            if ecosystem:
                if ecosystem not in by_ecosystem:
                    by_ecosystem[ecosystem] = []
                by_ecosystem[ecosystem].append(dep)
        
        # Query OSV for each ecosystem
        for ecosystem, deps in by_ecosystem.items():
            try:
                batch_vulns = self._query_osv_batch(deps, ecosystem)
                vulnerabilities.extend(batch_vulns)
                checked += len(deps)
            except Exception as e:
                errors.append(f"Failed to check {ecosystem} packages: {str(e)}")
        
        # Count by severity
        critical = sum(1 for v in vulnerabilities if v.severity == Severity.CRITICAL)
        high = sum(1 for v in vulnerabilities if v.severity == Severity.HIGH)
        medium = sum(1 for v in vulnerabilities if v.severity == Severity.MEDIUM)
        low = sum(1 for v in vulnerabilities if v.severity == Severity.LOW)
        
        end_time = time.time()
        
        return SecurityCheckResult(
            total_vulnerabilities=len(vulnerabilities),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            vulnerabilities=vulnerabilities,
            checked_packages=checked,
            check_time=end_time - start_time,
            errors=errors,
        )
    
    def _query_osv_batch(self, dependencies: List[Dependency], ecosystem: str) -> List[Vulnerability]:
        """Query OSV API for a batch of dependencies"""
        vulnerabilities = []
        
        for dep in dependencies:
            try:
                vulns = self._query_osv_single(dep, ecosystem)
                vulnerabilities.extend(vulns)
            except Exception:
                pass
        
        return vulnerabilities
    
    def _query_osv_single(self, dep: Dependency, ecosystem: str) -> List[Vulnerability]:
        """Query OSV API for a single package"""
        vulnerabilities = []
        
        try:
            url = "https://api.osv.dev/v1/query"
            data = {
                "package": {
                    "name": dep.name,
                    "ecosystem": ecosystem,
                },
                "version": dep.current_version,
            }
            
            req = Request(
                url,
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            
            with urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode())
                
                for vuln_data in result.get("vulns", []):
                    vuln = self._parse_osv_vulnerability(vuln_data, dep.name)
                    if vuln:
                        vulnerabilities.append(vuln)
        except Exception:
            pass
        
        return vulnerabilities
    
    def _parse_osv_vulnerability(self, data: Dict[str, Any], package_name: str) -> Optional[Vulnerability]:
        """Parse OSV vulnerability data"""
        try:
            # Determine severity
            severity = Severity.MEDIUM
            severity_data = data.get("severity", [])
            
            for sev in severity_data:
                if sev.get("type") == "CVSS":
                    score = sev.get("score", 0)
                    if isinstance(score, str):
                        # Parse CVSS vector string like "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                        pass
                    elif isinstance(score, (int, float)):
                        if score >= 9.0:
                            severity = Severity.CRITICAL
                        elif score >= 7.0:
                            severity = Severity.HIGH
                        elif score >= 4.0:
                            severity = Severity.MEDIUM
                        else:
                            severity = Severity.LOW
            
            # Get affected versions
            affected_versions = []
            patched_versions = []
            
            for affected in data.get("affected", []):
                for version_range in affected.get("versions", []):
                    affected_versions.append(version_range)
                
                for ranges in affected.get("ranges", []):
                    for event in ranges.get("events", []):
                        if "fixed" in event:
                            patched_versions.append(event["fixed"])
            
            # Get CWE/CVE IDs
            cwe_ids = []
            cve_ids = []
            
            for alias in data.get("aliases", []):
                if alias.startswith("CVE-"):
                    cve_ids.append(alias)
                elif alias.startswith("CWE-"):
                    cwe_ids.append(alias)
            
            # Get references
            references = [ref.get("url") for ref in data.get("references", []) if ref.get("url")]
            
            # Parse dates
            published = None
            modified = None
            
            if data.get("published"):
                try:
                    published = datetime.fromisoformat(data["published"].replace("Z", "+00:00"))
                except Exception:
                    pass
            
            if data.get("modified"):
                try:
                    modified = datetime.fromisoformat(data["modified"].replace("Z", "+00:00"))
                except Exception:
                    pass
            
            return Vulnerability(
                id=data.get("id", "UNKNOWN"),
                package_name=package_name,
                severity=severity,
                title=data.get("summary", "No summary available"),
                description=data.get("details", ""),
                affected_versions=affected_versions,
                patched_versions=patched_versions,
                cwe_ids=cwe_ids,
                cve_ids=cve_ids,
                references=references,
                published_date=published,
                modified_date=modified,
            )
        except Exception:
            return None
    
    def check_single_package(self, name: str, version: str, package_manager: PackageManager) -> List[Vulnerability]:
        """Check a single package for vulnerabilities"""
        ecosystem = self.ECOSYSTEM_MAP.get(package_manager)
        if not ecosystem:
            return []
        
        dep = Dependency(name=name, current_version=version, package_manager=package_manager)
        return self._query_osv_single(dep, ecosystem)
    
    def get_fix_suggestion(self, vuln: Vulnerability) -> str:
        """Get fix suggestion for a vulnerability"""
        if vuln.patched_versions:
            return f"Upgrade to version {vuln.patched_versions[0]} or later"
        return "No patched version available. Consider removing or replacing this dependency."
    
    def get_severity_summary(self, vulnerabilities: List[Vulnerability]) -> Dict[str, int]:
        """Get summary of vulnerabilities by severity"""
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
        
        for vuln in vulnerabilities:
            summary[vuln.severity.value] += 1
        
        return summary
