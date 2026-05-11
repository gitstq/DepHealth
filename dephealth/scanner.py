#!/usr/bin/env python3
"""
Dependency scanner module for DepHealth
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .core import Dependency, PackageManager


@dataclass
class ScanResult:
    """Result of dependency scanning"""
    dependencies: List[Dependency]
    package_managers: List[PackageManager]
    lock_files: List[Path]
    errors: List[str]
    warnings: List[str]


class DependencyScanner:
    """Scans project for dependencies across multiple package managers"""
    
    # Lock files that indicate exact versions
    LOCK_FILES = {
        "poetry.lock": PackageManager.POETRY,
        "package-lock.json": PackageManager.NPM,
        "yarn.lock": PackageManager.YARN,
        "pnpm-lock.yaml": PackageManager.PNPM,
        "Cargo.lock": PackageManager.CARGO,
        "go.sum": PackageManager.GO,
        "composer.lock": PackageManager.COMPOSER,
        "Gemfile.lock": PackageManager.GEM,
        "pubspec.lock": PackageManager.PUB,
    }
    
    # Manifest files
    MANIFEST_FILES = {
        "requirements.txt": PackageManager.PIP,
        "Pipfile": PackageManager.PIP,
        "pyproject.toml": PackageManager.POETRY,
        "setup.py": PackageManager.PIP,
        "setup.cfg": PackageManager.PIP,
        "package.json": PackageManager.NPM,
        "Cargo.toml": PackageManager.CARGO,
        "go.mod": PackageManager.GO,
        "pom.xml": PackageManager.MAVEN,
        "build.gradle": PackageManager.GRADLE,
        "build.gradle.kts": PackageManager.GRADLE,
        "composer.json": PackageManager.COMPOSER,
        "Gemfile": PackageManager.GEM,
        "pubspec.yaml": PackageManager.PUB,
    }
    
    def __init__(self, project_path: Path, recursive: bool = False):
        self.project_path = Path(project_path).resolve()
        self.recursive = recursive
        self._scanned_files: Set[Path] = set()
    
    def scan(self) -> ScanResult:
        """Scan project for all dependencies"""
        dependencies: List[Dependency] = []
        package_managers: List[PackageManager] = []
        lock_files: List[Path] = []
        errors: List[str] = []
        warnings: List[str] = []
        
        # Find all manifest and lock files
        manifest_files = self._find_files(self.MANIFEST_FILES.keys())
        found_lock_files = self._find_files(self.LOCK_FILES.keys())
        lock_files.extend(found_lock_files)
        
        # Detect package managers
        for file_path in manifest_files + found_lock_files:
            file_name = file_path.name
            if file_name in self.MANIFEST_FILES:
                pm = self.MANIFEST_FILES[file_name]
                if pm not in package_managers:
                    package_managers.append(pm)
            elif file_name in self.LOCK_FILES:
                pm = self.LOCK_FILES[file_name]
                if pm not in package_managers:
                    package_managers.append(pm)
        
        # Scan each manifest file
        for file_path in manifest_files:
            try:
                deps = self._scan_manifest(file_path)
                dependencies.extend(deps)
            except Exception as e:
                errors.append(f"Failed to scan {file_path}: {str(e)}")
        
        # Deduplicate dependencies
        dependencies = self._deduplicate(dependencies)
        
        return ScanResult(
            dependencies=dependencies,
            package_managers=package_managers,
            lock_files=lock_files,
            errors=errors,
            warnings=warnings,
        )
    
    def _find_files(self, file_names: Set[str]) -> List[Path]:
        """Find files in project directory"""
        found = []
        
        if self.recursive:
            for pattern in file_names:
                found.extend(self.project_path.rglob(pattern))
        else:
            for name in file_names:
                path = self.project_path / name
                if path.exists():
                    found.append(path)
        
        return found
    
    def _scan_manifest(self, file_path: Path) -> List[Dependency]:
        """Scan a manifest file for dependencies"""
        file_name = file_path.name
        
        if file_name == "requirements.txt":
            return self._scan_requirements_txt(file_path)
        elif file_name == "pyproject.toml":
            return self._scan_pyproject_toml(file_path)
        elif file_name == "package.json":
            return self._scan_package_json(file_path)
        elif file_name == "Cargo.toml":
            return self._scan_cargo_toml(file_path)
        elif file_name == "go.mod":
            return self._scan_go_mod(file_path)
        elif file_name == "pom.xml":
            return self._scan_pom_xml(file_path)
        elif file_name == "composer.json":
            return self._scan_composer_json(file_path)
        elif file_name == "Gemfile":
            return self._scan_gemfile(file_path)
        elif file_name == "pubspec.yaml":
            return self._scan_pubspec_yaml(file_path)
        elif file_name in ("setup.py", "setup.cfg"):
            return self._scan_setup_file(file_path)
        
        return []
    
    def _scan_requirements_txt(self, file_path: Path) -> List[Dependency]:
        """Scan requirements.txt"""
        deps = []
        content = file_path.read_text()
        
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Handle environment markers
            if ";" in line:
                line = line.split(";")[0].strip()
            
            # Handle extras
            if "[" in line:
                line = line.split("[")[0] + line.split("]")[-1]
            
            # Parse package spec
            patterns = [
                r"^([a-zA-Z0-9_-]+)\s*([<>=!]+)\s*([^\s]+)",
                r"^([a-zA-Z0-9_-]+)\s*==\s*([^\s]+)",
                r"^([a-zA-Z0-9_-]+)$",
            ]
            
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    name = groups[0]
                    version = groups[2] if len(groups) > 2 else (groups[1] if len(groups) > 1 else "*")
                    deps.append(Dependency(
                        name=name,
                        current_version=version,
                        package_manager=PackageManager.PIP,
                    ))
                    break
        
        return deps
    
    def _scan_pyproject_toml(self, file_path: Path) -> List[Dependency]:
        """Scan pyproject.toml"""
        deps = []
        content = file_path.read_text()
        
        # Simple TOML parsing
        sections = {
            "dependencies": False,
            "dev-dependencies": False,
            "optional-dependencies": False,
            "project.dependencies": False,
            "project.optional-dependencies": False,
            "tool.poetry.dependencies": False,
            "tool.poetry.dev-dependencies": False,
            "tool.poetry.group": False,
        }
        
        current_section = None
        is_dev = False
        
        for line in content.splitlines():
            stripped = line.strip()
            
            # Check for section headers
            if stripped.startswith("["):
                section_name = stripped.strip("[]").strip()
                current_section = section_name
                
                is_dev = any(x in section_name.lower() for x in ["dev", "test", "optional"])
                continue
            
            # Parse dependencies in current section
            if current_section and any(s in current_section for s in ["dependencies", "requires"]):
                if "=" in stripped and not stripped.startswith("#"):
                    # Handle different TOML formats
                    # name = "version" or name = {version = "x"}
                    match = re.match(r'^["\']?([a-zA-Z0-9_-]+)["\']?\s*=\s*(.+)', stripped)
                    if match:
                        name = match.group(1)
                        version_spec = match.group(2).strip()
                        
                        # Extract version from spec
                        if version_spec.startswith('"') or version_spec.startswith("'"):
                            version = version_spec.strip("\"'")
                        elif "{" in version_spec:
                            v_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', version_spec)
                            version = v_match.group(1) if v_match else "*"
                        else:
                            version = "*"
                        
                        # Skip python version
                        if name.lower() != "python":
                            deps.append(Dependency(
                                name=name,
                                current_version=version.lstrip("^~"),
                                is_dev=is_dev,
                                package_manager=PackageManager.POETRY,
                            ))
        
        return deps
    
    def _scan_package_json(self, file_path: Path) -> List[Dependency]:
        """Scan package.json"""
        deps = []
        data = json.loads(file_path.read_text())
        
        for dep_type, is_dev in [("dependencies", False), ("devDependencies", True), ("peerDependencies", False)]:
            for name, version in data.get(dep_type, {}).items():
                deps.append(Dependency(
                    name=name,
                    current_version=version.lstrip("^~>=<"),
                    is_dev=is_dev,
                    package_manager=PackageManager.NPM,
                ))
        
        return deps
    
    def _scan_cargo_toml(self, file_path: Path) -> List[Dependency]:
        """Scan Cargo.toml"""
        deps = []
        content = file_path.read_text()
        
        sections = {
            "dependencies": False,
            "dev-dependencies": True,
            "build-dependencies": False,
        }
        
        current_section = None
        is_dev = False
        
        for line in content.splitlines():
            stripped = line.strip()
            
            if stripped.startswith("["):
                section_name = stripped.strip("[]").strip()
                current_section = section_name
                
                for section, dev_flag in sections.items():
                    if section in section_name:
                        is_dev = dev_flag
                        break
                continue
            
            if current_section in sections:
                if "=" in stripped:
                    match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*(.+)', stripped)
                    if match:
                        name = match.group(1)
                        version_spec = match.group(2).strip()
                        
                        if version_spec.startswith('"') or version_spec.startswith("'"):
                            version = version_spec.strip("\"'")
                        elif "{" in version_spec:
                            v_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', version_spec)
                            version = v_match.group(1) if v_match else "*"
                        else:
                            version = "*"
                        
                        deps.append(Dependency(
                            name=name,
                            current_version=version,
                            is_dev=is_dev,
                            package_manager=PackageManager.CARGO,
                        ))
        
        return deps
    
    def _scan_go_mod(self, file_path: Path) -> List[Dependency]:
        """Scan go.mod"""
        deps = []
        content = file_path.read_text()
        
        in_require = False
        
        for line in content.splitlines():
            stripped = line.strip()
            
            if stripped.startswith("require ("):
                in_require = True
                continue
            elif stripped == ")" and in_require:
                in_require = False
                continue
            elif stripped.startswith("require ") and not in_require:
                # Single require line
                parts = stripped.replace("require", "").strip().split()
                if len(parts) >= 2:
                    deps.append(Dependency(
                        name=parts[0],
                        current_version=parts[1],
                        package_manager=PackageManager.GO,
                    ))
                continue
            
            if in_require:
                parts = stripped.split()
                if len(parts) >= 2 and not parts[0].startswith("//"):
                    deps.append(Dependency(
                        name=parts[0],
                        current_version=parts[1],
                        package_manager=PackageManager.GO,
                    ))
        
        return deps
    
    def _scan_pom_xml(self, file_path: Path) -> List[Dependency]:
        """Scan Maven pom.xml"""
        deps = []
        content = file_path.read_text()
        
        # Find all dependencies
        pattern = r"<dependency>\s*<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>(?:\s*<version>([^<]+)</version>)?\s*</dependency>"
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            group_id, artifact_id, version = match
            version = version if version else "*"
            deps.append(Dependency(
                name=f"{group_id}:{artifact_id}",
                current_version=version,
                package_manager=PackageManager.MAVEN,
            ))
        
        return deps
    
    def _scan_composer_json(self, file_path: Path) -> List[Dependency]:
        """Scan composer.json"""
        deps = []
        data = json.loads(file_path.read_text())
        
        for dep_type, is_dev in [("require", False), ("require-dev", True)]:
            for name, version in data.get(dep_type, {}).items():
                if name != "php":  # Skip PHP version
                    deps.append(Dependency(
                        name=name,
                        current_version=version.lstrip("^~>=<"),
                        is_dev=is_dev,
                        package_manager=PackageManager.COMPOSER,
                    ))
        
        return deps
    
    def _scan_gemfile(self, file_path: Path) -> List[Dependency]:
        """Scan Gemfile"""
        deps = []
        content = file_path.read_text()
        
        # Match gem declarations
        patterns = [
            r"gem\s+['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]",
            r"gem\s+['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"],\s*:group\s*=>\s*:([^,\s]+)",
            r"gem\s+['\"]([^'\"]+)['\"]",
        ]
        
        for line in content.splitlines():
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    groups = match.groups()
                    name = groups[0]
                    version = groups[1] if len(groups) > 1 else "*"
                    is_dev = "development" in line.lower() or "test" in line.lower()
                    
                    deps.append(Dependency(
                        name=name,
                        current_version=version,
                        is_dev=is_dev,
                        package_manager=PackageManager.GEM,
                    ))
                    break
        
        return deps
    
    def _scan_pubspec_yaml(self, file_path: Path) -> List[Dependency]:
        """Scan pubspec.yaml"""
        deps = []
        content = file_path.read_text()
        
        in_deps = False
        is_dev = False
        
        for line in content.splitlines():
            stripped = line.strip()
            
            if stripped.startswith("dependencies:"):
                in_deps = True
                is_dev = False
                continue
            elif stripped.startswith("dev_dependencies:"):
                in_deps = True
                is_dev = True
                continue
            elif stripped.startswith(("flutter:", "environment:", "  sdk:")) and in_deps:
                in_deps = False
                continue
            
            if in_deps and ":" in stripped:
                match = re.match(r'^([a-zA-Z0-9_-]+):\s*(.+)', stripped)
                if match:
                    name = match.group(1)
                    version_spec = match.group(2).strip()
                    
                    if version_spec.startswith("^") or version_spec.startswith("any"):
                        version = version_spec.lstrip("^")
                    elif version_spec.startswith('"') or version_spec.startswith("'"):
                        version = version_spec.strip("\"'")
                    else:
                        version = "*"
                    
                    deps.append(Dependency(
                        name=name,
                        current_version=version,
                        is_dev=is_dev,
                        package_manager=PackageManager.PUB,
                    ))
        
        return deps
    
    def _scan_setup_file(self, file_path: Path) -> List[Dependency]:
        """Scan setup.py or setup.cfg"""
        deps = []
        content = file_path.read_text()
        
        # Look for install_requires
        if file_path.suffix == ".py":
            # Parse setup.py
            match = re.search(r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL)
            if match:
                requires_block = match.group(1)
                for line in requires_block.splitlines():
                    line = line.strip().strip(",").strip("\"'")
                    if line and not line.startswith("#"):
                        dep_match = re.match(r"([a-zA-Z0-9_-]+)\s*([<>=!]+)?\s*(.+)?", line)
                        if dep_match:
                            name = dep_match.group(1)
                            version = dep_match.group(3) if dep_match.group(3) else "*"
                            deps.append(Dependency(
                                name=name,
                                current_version=version,
                                package_manager=PackageManager.PIP,
                            ))
        else:
            # Parse setup.cfg
            in_install_requires = False
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("install_requires"):
                    in_install_requires = True
                    continue
                elif stripped.startswith("[") and in_install_requires:
                    break
                
                if in_install_requires and stripped:
                    dep_match = re.match(r"([a-zA-Z0-9_-]+)\s*([<>=!]+)?\s*(.+)?", stripped)
                    if dep_match:
                        name = dep_match.group(1)
                        version = dep_match.group(3) if dep_match.group(3) else "*"
                        deps.append(Dependency(
                            name=name,
                            current_version=version,
                            package_manager=PackageManager.PIP,
                        ))
        
        return deps
    
    def _deduplicate(self, dependencies: List[Dependency]) -> List[Dependency]:
        """Remove duplicate dependencies, keeping the most specific version"""
        seen: Dict[str, Dependency] = {}
        
        for dep in dependencies:
            key = f"{dep.package_manager.value}:{dep.name}"
            if key not in seen:
                seen[key] = dep
            else:
                # Keep the one with a more specific version
                existing = seen[key]
                if dep.current_version != "*" and existing.current_version == "*":
                    seen[key] = dep
                elif dep.is_direct and not existing.is_direct:
                    seen[key] = dep
        
        return list(seen.values())
    
    def get_dependency_tree(self) -> Dict[str, List[str]]:
        """Get dependency tree (simplified)"""
        # This would require parsing lock files for full tree
        # For now, return a flat structure
        result = self.scan()
        tree: Dict[str, List[str]] = {}
        
        for dep in result.dependencies:
            pm = dep.package_manager.value
            if pm not in tree:
                tree[pm] = []
            tree[pm].append(dep.name)
        
        return tree
