#!/usr/bin/env python3
"""
Check for common ADK 1.0.0 pitfalls in the codebase
Run this before committing to catch issues early
"""
import os
import re
import sys
from pathlib import Path


class PitfallChecker:
    """Checks codebase for common ADK 1.0.0 issues"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.errors = []
        self.warnings = []
        
    def check_all(self):
        """Run all pitfall checks"""
        print("🔍 Checking for ADK 1.0.0 common pitfalls...")
        
        self.check_import_patterns()
        self.check_agent_exports()
        self.check_tool_signatures()
        self.check_state_prefixes()
        self.check_model_ids()
        self.check_dependencies()
        
        # Report results
        if self.errors:
            print(f"\n❌ Found {len(self.errors)} errors:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  Found {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ No pitfalls detected!")
        
        return len(self.errors) == 0
    
    def check_import_patterns(self):
        """Check for incorrect genai import patterns"""
        pattern = re.compile(r'import\s+google\.generativeai')
        
        for py_file in self.root_dir.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if pattern.search(content):
                self.errors.append(
                    f"{py_file.relative_to(self.root_dir)}: "
                    f"Wrong import pattern. Use 'from google import genai'"
                )
    
    def check_agent_exports(self):
        """Check for incorrect agent variable names"""
        src_path = self.root_dir / "src" / "windsurf_agents"
        
        if not src_path.exists():
            return
            
        for agent_file in src_path.rglob("agent.py"):
            with open(agent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "root_agent =" in content:
                self.errors.append(
                    f"{agent_file.relative_to(self.root_dir)}: "
                    f"Wrong export name. Use 'agent =' not 'root_agent ='"
                )
            
            if "agent =" not in content and "agent:" not in content:
                self.warnings.append(
                    f"{agent_file.relative_to(self.root_dir)}: "
                    f"No 'agent' variable found"
                )
    
    def check_tool_signatures(self):
        """Check for missing ToolContext parameters"""
        tools_path = self.root_dir / "src" / "windsurf_agents" / "tools"
        
        if not tools_path.exists():
            return
            
        # Simple regex to find function definitions
        func_pattern = re.compile(r'def\s+(\w+)\s*\(([^)]*)\):')
        
        for tool_file in tools_path.rglob("*.py"):
            if tool_file.name == "__init__.py":
                continue
                
            with open(tool_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for match in func_pattern.finditer(content):
                func_name = match.group(1)
                params = match.group(2)
                
                if not func_name.startswith('_'):  # Skip private functions
                    if 'tool_context' not in params:
                        self.errors.append(
                            f"{tool_file.relative_to(self.root_dir)}: "
                            f"Function '{func_name}' missing 'tool_context' parameter"
                        )
    
    def check_state_prefixes(self):
        """Check for state keys without proper prefixes"""
        pattern = re.compile(r'state\[[\"\']([^\"\']+)[\"\']\]')
        valid_prefixes = ('user:', 'app:', 'temp:')
        
        for py_file in self.root_dir.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for match in pattern.finditer(content):
                key = match.group(1)
                if not key.startswith(valid_prefixes):
                    self.warnings.append(
                        f"{py_file.relative_to(self.root_dir)}: "
                        f"State key '{key}' missing prefix (user:, app:, or temp:)"
                    )
    
    def check_model_ids(self):
        """Check for hardcoded model IDs"""
        # Look for model ID patterns
        for py_file in self.root_dir.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for old model IDs
            if "gemini-2.0-flash-live-001" in content:
                self.warnings.append(
                    f"{py_file.relative_to(self.root_dir)}: "
                    f"Using specific live model ID - consider using 'gemini-2.0-flash-exp'"
                )
    
    def check_dependencies(self):
        """Check pyproject.toml for critical dependencies"""
        pyproject = self.root_dir / "pyproject.toml"
        
        if pyproject.exists():
            with open(pyproject, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for protobuf pinning
            if 'protobuf' not in content:
                self.errors.append(
                    "pyproject.toml: Missing protobuf dependency"
                )
            elif 'protobuf = "==5.29.4"' not in content:
                self.warnings.append(
                    "pyproject.toml: Consider pinning protobuf to 5.29.4"
                )
            
            # Check for ADK extras
            if 'google-adk' in content and '[vertexai]' not in content:
                self.warnings.append(
                    "pyproject.toml: Consider using google-adk[vertexai] for full features"
                )


def main():
    """Run pitfall checker on current directory"""
    root_dir = Path.cwd()
    checker = PitfallChecker(root_dir)
    
    success = checker.check_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
