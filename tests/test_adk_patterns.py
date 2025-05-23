"""
Critical tests for ADK 1.0.0 patterns and common pitfalls
"""
import pytest
import inspect
import ast
import os
from pathlib import Path
from typing import Dict, List, Any
from google import genai
from google.adk.agents import LlmAgent
from google.adk.types import ToolContext


class TestADKPatterns:
    """Test suite to ensure ADK 1.0.0 best practices are followed"""
    
    def test_correct_genai_import(self):
        """Verify we're using the correct import pattern"""
        # This test itself demonstrates the correct pattern
        assert genai is not None
        assert hasattr(genai, 'discovery')
        
    def test_model_registry(self):
        """Check if configured models exist in the registry"""
        models = genai.discovery.list_models()
        model_names = [m.name for m in models]
        
        # Check for our default model
        assert any("flash" in name for name in model_names), \
            "No Flash model found in registry - check ADK installation"
    
    def test_agent_export_pattern(self):
        """Verify all agent modules export 'agent' variable"""
        src_path = Path(__file__).parent.parent / "src" / "windsurf_agents"
        
        if not src_path.exists():
            pytest.skip("Source directory not found")
            
        # Check each agent package
        for agent_dir in src_path.glob("*/"):
            if agent_dir.is_dir() and (agent_dir / "agent.py").exists():
                # Read the agent.py file
                with open(agent_dir / "agent.py", "r") as f:
                    content = f.read()
                
                # Check for correct export
                assert "agent =" in content, \
                    f"Agent in {agent_dir.name} must export 'agent' variable"
                assert "root_agent =" not in content, \
                    f"Agent in {agent_dir.name} using wrong export name 'root_agent'"


class TestToolPatterns:
    """Test suite for ADK tool implementation patterns"""
    
    def test_tool_signatures(self):
        """Verify all tools have ToolContext as first parameter"""
        tools_path = Path(__file__).parent.parent / "src" / "windsurf_agents" / "tools"
        
        if not tools_path.exists():
            pytest.skip("Tools directory not found")
            
        for tool_file in tools_path.glob("*.py"):
            if tool_file.name == "__init__.py":
                continue
                
            # Parse the Python file
            with open(tool_file, "r") as f:
                tree = ast.parse(f.read())
            
            # Check each function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):  # Skip private functions
                        # Check first parameter
                        if node.args.args:
                            first_param = node.args.args[0].arg
                            assert first_param == "tool_context", \
                                f"Tool {node.name} in {tool_file.name} must have 'tool_context' as first parameter"
    
    def test_tool_docstrings(self):
        """Verify all tools have comprehensive docstrings"""
        tools_path = Path(__file__).parent.parent / "src" / "windsurf_agents" / "tools"
        
        if not tools_path.exists():
            pytest.skip("Tools directory not found")
            
        for tool_file in tools_path.glob("*.py"):
            if tool_file.name == "__init__.py":
                continue
                
            with open(tool_file, "r") as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):
                        docstring = ast.get_docstring(node)
                        assert docstring is not None, \
                            f"Tool {node.name} in {tool_file.name} missing docstring"
                        
                        # Check docstring quality
                        assert len(docstring.split('\n')) >= 5, \
                            f"Tool {node.name} docstring too short (must be ≥5 lines)"
                        assert "Args:" in docstring, \
                            f"Tool {node.name} docstring missing Args: section"
                        assert "Returns:" in docstring, \
                            f"Tool {node.name} docstring missing Returns: section"


class TestStateManagement:
    """Test suite for session state management patterns"""
    
    def test_state_prefix_usage(self):
        """Verify state keys use proper prefixes"""
        src_path = Path(__file__).parent.parent / "src"
        
        if not src_path.exists():
            pytest.skip("Source directory not found")
            
        # Pattern to find state access
        import re
        state_pattern = re.compile(r'state\["([^"]+)"\]|state\[\'([^\']+)\'\]')
        prefix_pattern = re.compile(r'^(user:|app:|temp:)')
        
        violations = []
        
        for py_file in src_path.rglob("*.py"):
            with open(py_file, "r") as f:
                content = f.read()
            
            # Find all state key accesses
            matches = state_pattern.findall(content)
            for match in matches:
                key = match[0] or match[1]
                if not prefix_pattern.match(key):
                    violations.append(f"{py_file.name}: state key '{key}' missing prefix")
        
        assert len(violations) == 0, \
            f"State keys without prefixes found:\n" + "\n".join(violations)


class TestWindowsCompatibility:
    """Test suite for Windows-specific requirements"""
    
    def test_proactor_loop_initialization(self):
        """Verify Proactor loop is initialized for Windows"""
        init_file = Path(__file__).parent.parent / "src" / "windsurf_agents" / "__init__.py"
        
        if init_file.exists():
            with open(init_file, "r") as f:
                content = f.read()
            
            assert "WindowsProactorEventLoopPolicy" in content, \
                "Windows Proactor loop initialization missing"
            assert 'sys.platform.startswith("win")' in content, \
                "Windows platform check missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
