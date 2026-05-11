#!/usr/bin/env python3
"""
Core analyzer module for DepHealth
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class PackageManager(Enum):
    """Supported package managers"""
    PIP = "pip"
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    CARGO = "cargo"
    GO = "go"
    MAVEN = "maven"
    GRADLE = "gradle"
    COMPOSER = "composer"
    GEM = "gem"
    POETRY = "poetry"
    PUB = "pub"


class Severity(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Dependency:
    """Represents a single dependency"""
    name: str
    current_version: str
    latest_version: Optional[str] = None
    wanted_version: Optional[str] = None
    is_dev: bool = False
    is_direct: bool = True
    package_manager: PackageManager = PackageManager.PIP
    description: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    deprecated: bool = False
    deprecated_message: Optional[str] = None
    vulnerabilities: List[Dict[str, Any]] = field(default_factory=list)
    outdated_days: Optional[int] = None
    release_date: Optional[datetime] = None
    
    @property
    def is_outdated(self) -> bool:
        """Check if dependency is outdated"""
        if not self.latest_version:
            return False
        return self.current_version != self.latest_version
    
    @property
    def has_vulnerabilities(self) -> bool:
        """Check if dependency has known vulnerabilities"""
        return len(self.vulnerabilities) > 0
    
    @property
    def vulnerability_severity(self) -> Optional[Severity]:
        """Get highest vulnerability severity"""
        if not self.vulnerabilities:
            return None
        severity_order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
        for sev in severity_order:
            for vuln in self.vulnerabilities:
                if vuln.get("severity", "").lower() == sev.value:
                    return sev
        return Severity.INFO


@dataclass
class HealthScore:
    """Health score breakdown"""
    overall: float  # 0-100
    security: float  # 0-100
    freshness: float  # 0-100
    compatibility: float  # 0-100
    maintenance: float  # 0-100
    
    @property
    def grade(self) -> str:
        """Get letter grade for health score"""
        if self.overall >= 90:
            return "A+"
        elif self.overall >= 85:
            return "A"
        elif self.overall >= 80:
            return "A-"
        elif self.overall >= 75:
            return "B+"
        elif self.overall >= 70:
            return "B"
        elif self.overall >= 65:
            return "B-"
        elif self.overall >= 60:
            return "C+"
        elif self.overall >= 55:
            return "C"
        elif self.overall >= 50:
            return "C-"
        elif self.overall >= 40:
            return "D"
        else:
            return "F"


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    project_path: Path
    package_managers: List[PackageManager]
    dependencies: List[Dependency]
    health_score: HealthScore
    total_dependencies: int
    direct_dependencies: int
    dev_dependencies: int
    outdated_count: int
    vulnerable_count: int
    deprecated_count: int
    analysis_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DepHealthAnalyzer:
    """Main analyzer class for dependency health analysis"""
    
    PACKAGE_FILES = {
        "requirements.txt": PackageManager.PIP,
        "Pipfile": PackageManager.PIP,
        "Pipfile.lock": PackageManager.PIP,
        "pyproject.toml": PackageManager.POETRY,
        "poetry.lock": PackageManager.POETRY,
        "package.json": PackageManager.NPM,
        "package-lock.json": PackageManager.NPM,
        "yarn.lock": PackageManager.YARN,
        "pnpm-lock.yaml": PackageManager.PNPM,
        "Cargo.toml": PackageManager.CARGO,
        "Cargo.lock": PackageManager.CARGO,
        "go.mod": PackageManager.GO,
        "go.sum": PackageManager.GO,
        "pom.xml": PackageManager.MAVEN,
        "build.gradle": PackageManager.GRADLE,
        "build.gradle.kts": PackageManager.GRADLE,
        "composer.json": PackageManager.COMPOSER,
        "composer.lock": PackageManager.COMPOSER,
        "Gemfile": PackageManager.GEM,
        "Gemfile.lock": PackageManager.GEM,
        "pubspec.yaml": PackageManager.PUB,
        "pubspec.lock": PackageManager.PUB,
    }
    
    def __init__(
        self,
        project_path: Path,
        check_security: bool = True,
        check_outdated: bool = True,
        check_deprecated: bool = True,
        include_dev: bool = True,
        offline_mode: bool = False,
        timeout: int = 30,
    ):
        self.project_path = Path(project_path).resolve()
        self.check_security = check_security
        self.check_outdated = check_outdated
        self.check_deprecated = check_deprecated
        self.include_dev = include_dev
        self.offline_mode = offline_mode
        self.timeout = timeout
        self._dependencies: List[Dependency] = []
        self._errors: List[str] = []
        self._warnings: List[str] = []
    
    def detect_package_managers(self) -> List[PackageManager]:
        """Detect package managers used in the project"""
        detected = []
        for file_name, pm in self.PACKAGE_FILES.items():
            if (self.project_path / file_name).exists():
                if pm not in detected:
                    detected.append(pm)
        return detected
    
    def analyze(self) -> AnalysisResult:
        """Run complete dependency health analysis"""
        start_time = datetime.now()
        
        # Detect package managers
        package_managers = self.detect_package_managers()
        if not package_managers:
            self._warnings.append("No supported package manager files found")
        
        # Scan dependencies for each package manager
        for pm in package_managers:
            try:
                deps = self._scan_dependencies(pm)
                self._dependencies.extend(deps)
            except Exception as e:
                self._errors.append(f"Failed to scan {pm.value} dependencies: {str(e)}")
        
        # Check for outdated packages
        if self.check_outdated and not self.offline_mode:
            self._check_outdated()
        
        # Check for security vulnerabilities
        if self.check_security and not self.offline_mode:
            self._check_security()
        
        # Check for deprecated packages
        if self.check_deprecated and not self.offline_mode:
            self._check_deprecated()
        
        # Calculate health score
        health_score = self._calculate_health_score()
        
        # Calculate counts
        total_deps = len(self._dependencies)
        direct_deps = sum(1 for d in self._dependencies if d.is_direct)
        dev_deps = sum(1 for d in self._dependencies if d.is_dev)
        outdated = sum(1 for d in self._dependencies if d.is_outdated)
        vulnerable = sum(1 for d in self._dependencies if d.has_vulnerabilities)
        deprecated = sum(1 for d in self._dependencies if d.deprecated)
        
        end_time = datetime.now()
        analysis_time = (end_time - start_time).total_seconds()
        
        return AnalysisResult(
            project_path=self.project_path,
            package_managers=package_managers,
            dependencies=self._dependencies,
            health_score=health_score,
            total_dependencies=total_deps,
            direct_dependencies=direct_deps,
            dev_dependencies=dev_deps,
            outdated_count=outdated,
            vulnerable_count=vulnerable,
            deprecated_count=deprecated,
            analysis_time=analysis_time,
            errors=self._errors,
            warnings=self._warnings,
        )
    
    def _scan_dependencies(self, pm: PackageManager) -> List[Dependency]:
        """Scan dependencies for a specific package manager"""
        if pm in (PackageManager.PIP, PackageManager.POETRY):
            return self._scan_python_deps(pm)
        elif pm in (PackageManager.NPM, PackageManager.YARN, PackageManager.PNPM):
            return self._scan_node_deps(pm)
        elif pm == PackageManager.CARGO:
            return self._scan_cargo_deps()
        elif pm == PackageManager.GO:
            return self._scan_go_deps()
        elif pm in (PackageManager.MAVEN, PackageManager.GRADLE):
            return self._scan_java_deps(pm)
        elif pm == PackageManager.COMPOSER:
            return self._scan_php_deps()
        elif pm == PackageManager.GEM:
            return self._scan_ruby_deps()
        elif pm == PackageManager.PUB:
            return self._scan_dart_deps()
        return []
    
    def _scan_python_deps(self, pm: PackageManager) -> List[Dependency]:
        """Scan Python dependencies"""
        deps = []
        
        # Check requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            deps.extend(self._parse_requirements_txt(req_file))
        
        # Check pyproject.toml
        pyproject = self.project_path / "pyproject.toml"
        if pyproject.exists():
            deps.extend(self._parse_pyproject_toml(pyproject))
        
        return deps
    
    def _parse_requirements_txt(self, file_path: Path) -> List[Dependency]:
        """Parse requirements.txt file"""
        deps = []
        try:
            content = file_path.read_text()
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # Parse package name and version
                match = re.match(r"^([a-zA-Z0-9_-]+)\s*([<>=!]+)\s*([^\s;]+)", line)
                if match:
                    name = match.group(1)
                    operator = match.group(2)
                    version = match.group(3)
                    deps.append(Dependency(
                        name=name,
                        current_version=version,
                        package_manager=PackageManager.PIP,
                    ))
        except Exception as e:
            self._errors.append(f"Failed to parse {file_path}: {str(e)}")
        return deps
    
    def _parse_pyproject_toml(self, file_path: Path) -> List[Dependency]:
        """Parse pyproject.toml file"""
        deps = []
        try:
            content = file_path.read_text()
            # Simple TOML parsing for dependencies
            in_deps = False
            in_dev_deps = False
            for line in content.splitlines():
                line = line.strip()
                if "dependencies" in line and "[" in line:
                    in_deps = True
                    in_dev_deps = "dev" in line.lower() or "optional" in line.lower()
                    continue
                if line.startswith("[") and in_deps:
                    in_deps = False
                    in_dev_deps = False
                    continue
                if in_deps and "=" in line:
                    match = re.match(r'^["\']?([a-zA-Z0-9_-]+)["\']?\s*=\s*["\']([^"\']+)["\']', line)
                    if match:
                        deps.append(Dependency(
                            name=match.group(1),
                            current_version=match.group(2),
                            is_dev=in_dev_deps,
                            package_manager=PackageManager.POETRY,
                        ))
        except Exception as e:
            self._errors.append(f"Failed to parse {file_path}: {str(e)}")
        return deps
    
    def _scan_node_deps(self, pm: PackageManager) -> List[Dependency]:
        """Scan Node.js dependencies"""
        deps = []
        package_json = self.project_path / "package.json"
        
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                
                # Regular dependencies
                for name, version in data.get("dependencies", {}).items():
                    deps.append(Dependency(
                        name=name,
                        current_version=version.lstrip("^~"),
                        package_manager=pm,
                        is_direct=True,
                    ))
                
                # Dev dependencies
                if self.include_dev:
                    for name, version in data.get("devDependencies", {}).items():
                        deps.append(Dependency(
                            name=name,
                            current_version=version.lstrip("^~"),
                            package_manager=pm,
                            is_dev=True,
                            is_direct=True,
                        ))
            except Exception as e:
                self._errors.append(f"Failed to parse package.json: {str(e)}")
        
        return deps
    
    def _scan_cargo_deps(self) -> List[Dependency]:
        """Scan Rust/Cargo dependencies"""
        deps = []
        cargo_toml = self.project_path / "Cargo.toml"
        
        if cargo_toml.exists():
            try:
                content = cargo_toml.read_text()
                in_deps = False
                in_dev_deps = False
                
                for line in content.splitlines():
                    line = line.strip()
                    if line == "[dependencies]":
                        in_deps = True
                        in_dev_deps = False
                        continue
                    elif line == "[dev-dependencies]":
                        in_deps = True
                        in_dev_deps = True
                        continue
                    elif line.startswith("[") and in_deps:
                        in_deps = False
                        continue
                    
                    if in_deps and "=" in line:
                        match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']?([^"\'\s]+)', line)
                        if match:
                            deps.append(Dependency(
                                name=match.group(1),
                                current_version=match.group(2),
                                is_dev=in_dev_deps,
                                package_manager=PackageManager.CARGO,
                            ))
            except Exception as e:
                self._errors.append(f"Failed to parse Cargo.toml: {str(e)}")
        
        return deps
    
    def _scan_go_deps(self) -> List[Dependency]:
        """Scan Go dependencies"""
        deps = []
        go_mod = self.project_path / "go.mod"
        
        if go_mod.exists():
            try:
                content = go_mod.read_text()
                in_require = False
                
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("require ("):
                        in_require = True
                        continue
                    elif line == ")" and in_require:
                        in_require = False
                        continue
                    elif line.startswith("require ") and not in_require:
                        # Single line require
                        parts = line.replace("require", "").strip().split()
                        if len(parts) >= 2:
                            deps.append(Dependency(
                                name=parts[0],
                                current_version=parts[1],
                                package_manager=PackageManager.GO,
                            ))
                        continue
                    
                    if in_require:
                        parts = line.split()
                        if len(parts) >= 2:
                            deps.append(Dependency(
                                name=parts[0],
                                current_version=parts[1],
                                package_manager=PackageManager.GO,
                            ))
            except Exception as e:
                self._errors.append(f"Failed to parse go.mod: {str(e)}")
        
        return deps
    
    def _scan_java_deps(self, pm: PackageManager) -> List[Dependency]:
        """Scan Java dependencies (Maven/Gradle)"""
        deps = []
        
        if pm == PackageManager.MAVEN:
            pom_xml = self.project_path / "pom.xml"
            if pom_xml.exists():
                deps.extend(self._parse_pom_xml(pom_xml))
        
        return deps
    
    def _parse_pom_xml(self, file_path: Path) -> List[Dependency]:
        """Parse Maven pom.xml file"""
        deps = []
        try:
            content = file_path.read_text()
            # Simple regex-based parsing
            pattern = r"<dependency>.*?<groupId>([^<]+)</groupId>.*?<artifactId>([^<]+)</artifactId>.*?<version>([^<]+)</version>.*?</dependency>"
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                group_id, artifact_id, version = match
                deps.append(Dependency(
                    name=f"{group_id}:{artifact_id}",
                    current_version=version,
                    package_manager=PackageManager.MAVEN,
                ))
        except Exception as e:
            self._errors.append(f"Failed to parse pom.xml: {str(e)}")
        return deps
    
    def _scan_php_deps(self) -> List[Dependency]:
        """Scan PHP/Composer dependencies"""
        deps = []
        composer_json = self.project_path / "composer.json"
        
        if composer_json.exists():
            try:
                data = json.loads(composer_json.read_text())
                
                for name, version in data.get("require", {}).items():
                    if name != "php":  # Skip PHP version requirement
                        deps.append(Dependency(
                            name=name,
                            current_version=version.lstrip("^~"),
                            package_manager=PackageManager.COMPOSER,
                        ))
                
                if self.include_dev:
                    for name, version in data.get("require-dev", {}).items():
                        deps.append(Dependency(
                            name=name,
                            current_version=version.lstrip("^~"),
                            is_dev=True,
                            package_manager=PackageManager.COMPOSER,
                        ))
            except Exception as e:
                self._errors.append(f"Failed to parse composer.json: {str(e)}")
        
        return deps
    
    def _scan_ruby_deps(self) -> List[Dependency]:
        """Scan Ruby/Gem dependencies"""
        deps = []
        gemfile = self.project_path / "Gemfile"
        
        if gemfile.exists():
            try:
                content = gemfile.read_text()
                pattern = r"gem\s+['\"]([^'\"]+)['\"],?\s*['\"]?([^'\"\s]*)['\"]?"
                matches = re.findall(pattern, content)
                for name, version in matches:
                    deps.append(Dependency(
                        name=name,
                        current_version=version or "latest",
                        package_manager=PackageManager.GEM,
                    ))
            except Exception as e:
                self._errors.append(f"Failed to parse Gemfile: {str(e)}")
        
        return deps
    
    def _scan_dart_deps(self) -> List[Dependency]:
        """Scan Dart/Pub dependencies"""
        deps = []
        pubspec = self.project_path / "pubspec.yaml"
        
        if pubspec.exists():
            try:
                content = pubspec.read_text()
                in_deps = False
                in_dev_deps = False
                
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("dependencies:"):
                        in_deps = True
                        in_dev_deps = False
                        continue
                    elif line.startswith("dev_dependencies:"):
                        in_deps = True
                        in_dev_deps = True
                        continue
                    elif line.startswith(("flutter:", "environment:")) and in_deps:
                        in_deps = False
                        continue
                    
                    if in_deps and ":" in line:
                        match = re.match(r'^([a-zA-Z0-9_-]+):\s*["\']?([^"\'\s]+)', line)
                        if match:
                            deps.append(Dependency(
                                name=match.group(1),
                                current_version=match.group(2),
                                is_dev=in_dev_deps,
                                package_manager=PackageManager.PUB,
                            ))
            except Exception as e:
                self._errors.append(f"Failed to parse pubspec.yaml: {str(e)}")
        
        return deps
    
    def _check_outdated(self) -> None:
        """Check for outdated packages"""
        for dep in self._dependencies:
            try:
                latest = self._get_latest_version(dep)
                if latest:
                    dep.latest_version = latest
            except Exception:
                pass
    
    def _get_latest_version(self, dep: Dependency) -> Optional[str]:
        """Get latest version of a package"""
        try:
            if dep.package_manager in (PackageManager.PIP, PackageManager.POETRY):
                return self._get_pypi_version(dep.name)
            elif dep.package_manager in (PackageManager.NPM, PackageManager.YARN, PackageManager.PNPM):
                return self._get_npm_version(dep.name)
            elif dep.package_manager == PackageManager.CARGO:
                return self._get_crate_version(dep.name)
            elif dep.package_manager == PackageManager.GO:
                return None  # Go modules don't have a simple version API
            elif dep.package_manager == PackageManager.MAVEN:
                return self._get_maven_version(dep.name)
        except Exception:
            pass
        return None
    
    def _get_pypi_version(self, name: str) -> Optional[str]:
        """Get latest version from PyPI"""
        try:
            url = f"https://pypi.org/pypi/{name}/json"
            req = Request(url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode())
                return data.get("info", {}).get("version")
        except Exception:
            return None
    
    def _get_npm_version(self, name: str) -> Optional[str]:
        """Get latest version from npm registry"""
        try:
            url = f"https://registry.npmjs.org/{name}/latest"
            req = Request(url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode())
                return data.get("version")
        except Exception:
            return None
    
    def _get_crate_version(self, name: str) -> Optional[str]:
        """Get latest version from crates.io"""
        try:
            url = f"https://crates.io/api/v1/crates/{name}"
            req = Request(url, headers={"Accept": "application/json", "User-Agent": "DepHealth/1.0"})
            with urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode())
                return data.get("crate", {}).get("newest_version")
        except Exception:
            return None
    
    def _get_maven_version(self, name: str) -> Optional[str]:
        """Get latest version from Maven Central"""
        try:
            parts = name.split(":")
            if len(parts) == 2:
                group_id, artifact_id = parts
                group_path = group_id.replace(".", "/")
                url = f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/maven-metadata.xml"
                req = Request(url)
                with urlopen(req, timeout=self.timeout) as response:
                    content = response.read().decode()
                    match = re.search(r"<latest>([^<]+)</latest>", content)
                    if match:
                        return match.group(1)
        except Exception:
            pass
        return None
    
    def _check_security(self) -> None:
        """Check for security vulnerabilities"""
        for dep in self._dependencies:
            try:
                vulns = self._get_vulnerabilities(dep)
                if vulns:
                    dep.vulnerabilities = vulns
            except Exception:
                pass
    
    def _get_vulnerabilities(self, dep: Dependency) -> List[Dict[str, Any]]:
        """Get known vulnerabilities for a package"""
        # This is a simplified implementation
        # In production, you would integrate with OSV, Snyk, or GitHub Advisory DB
        vulnerabilities = []
        
        try:
            # Try OSV API
            if dep.package_manager in (PackageManager.PIP, PackageManager.POETRY):
                ecosystem = "PyPI"
            elif dep.package_manager in (PackageManager.NPM, PackageManager.YARN, PackageManager.PNPM):
                ecosystem = "npm"
            elif dep.package_manager == PackageManager.CARGO:
                ecosystem = "crates.io"
            elif dep.package_manager == PackageManager.GO:
                ecosystem = "Go"
            elif dep.package_manager == PackageManager.MAVEN:
                ecosystem = "Maven"
            else:
                return vulnerabilities
            
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
                for vuln in result.get("vulns", []):
                    severity = "medium"
                    if vuln.get("severity"):
                        sev_data = vuln["severity"][0]
                        if sev_data.get("type") == "CVSS":
                            score = sev_data.get("score", 0)
                            if isinstance(score, str) and "CVSS:" in score:
                                # Parse CVSS vector string
                                pass
                            elif isinstance(score, (int, float)):
                                if score >= 9.0:
                                    severity = "critical"
                                elif score >= 7.0:
                                    severity = "high"
                                elif score >= 4.0:
                                    severity = "medium"
                                else:
                                    severity = "low"
                    
                    vulnerabilities.append({
                        "id": vuln.get("id"),
                        "summary": vuln.get("summary", ""),
                        "severity": severity,
                        "url": f"https://osv.dev/vulnerability/{vuln.get('id')}",
                    })
        except Exception:
            pass
        
        return vulnerabilities
    
    def _check_deprecated(self) -> None:
        """Check for deprecated packages"""
        for dep in self._dependencies:
            try:
                if dep.package_manager in (PackageManager.PIP, PackageManager.POETRY):
                    self._check_pypi_deprecated(dep)
                elif dep.package_manager in (PackageManager.NPM, PackageManager.YARN, PackageManager.PNPM):
                    self._check_npm_deprecated(dep)
            except Exception:
                pass
    
    def _check_pypi_deprecated(self, dep: Dependency) -> None:
        """Check if PyPI package is deprecated"""
        try:
            url = f"https://pypi.org/pypi/{dep.name}/json"
            req = Request(url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode())
                info = data.get("info", {})
                classifiers = info.get("classifiers", [])
                
                for classifier in classifiers:
                    if "deprecated" in classifier.lower():
                        dep.deprecated = True
                        dep.deprecated_message = classifier
                        break
        except Exception:
            pass
    
    def _check_npm_deprecated(self, dep: Dependency) -> None:
        """Check if npm package is deprecated"""
        try:
            url = f"https://registry.npmjs.org/{dep.name}/{dep.current_version}"
            req = Request(url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode())
                if data.get("deprecated"):
                    dep.deprecated = True
                    dep.deprecated_message = data.get("deprecated")
        except Exception:
            pass
    
    def _calculate_health_score(self) -> HealthScore:
        """Calculate overall health score"""
        if not self._dependencies:
            return HealthScore(
                overall=100.0,
                security=100.0,
                freshness=100.0,
                compatibility=100.0,
                maintenance=100.0,
            )
        
        # Security score (0-100)
        security_score = 100.0
        for dep in self._dependencies:
            if dep.has_vulnerabilities:
                sev = dep.vulnerability_severity
                if sev == Severity.CRITICAL:
                    security_score -= 25
                elif sev == Severity.HIGH:
                    security_score -= 15
                elif sev == Severity.MEDIUM:
                    security_score -= 8
                elif sev == Severity.LOW:
                    security_score -= 3
        security_score = max(0, security_score)
        
        # Freshness score (0-100)
        total = len(self._dependencies)
        outdated = sum(1 for d in self._dependencies if d.is_outdated)
        freshness_score = ((total - outdated) / total) * 100 if total > 0 else 100
        
        # Compatibility score (based on deprecated packages)
        deprecated = sum(1 for d in self._dependencies if d.deprecated)
        compatibility_score = ((total - deprecated) / total) * 100 if total > 0 else 100
        
        # Maintenance score (simplified)
        maintenance_score = (freshness_score + compatibility_score) / 2
        
        # Overall score (weighted average)
        overall = (
            security_score * 0.4 +
            freshness_score * 0.25 +
            compatibility_score * 0.2 +
            maintenance_score * 0.15
        )
        
        return HealthScore(
            overall=round(overall, 1),
            security=round(security_score, 1),
            freshness=round(freshness_score, 1),
            compatibility=round(compatibility_score, 1),
            maintenance=round(maintenance_score, 1),
        )
