# Docstring Style Convention

## Overview

All Python code in the InstaBids project must include comprehensive docstrings following Google style with specific requirements for ADK tools.

## Module Docstrings

```python
"""Module for Supabase database operations.

This module provides tools for interacting with Supabase including
CRUD operations, batch processing, and real-time subscriptions.

Typical usage example:
    from instabids.tools import supabase_tools
    
    result = supabase_tools.save_project(
        tool_context,
        project_data={"title": "Kitchen Renovation"}
    )
"""
```

## Class Docstrings

```python
class HomeownerAgent(LiveAgent):
    """AI agent for guiding homeowners through project scoping.
    
    This agent conducts conversational Q&A to gather project requirements,
    analyzes uploaded images, and learns user preferences over time.
    
    Attributes:
        name: Agent identifier used in routing.
        model: LLM model ID for inference.
        tools: List of available tool functions.
        
    Example:
        agent = HomeownerAgent()
        response = await agent.process("I need help with my roof")
    """
```

## Function/Tool Docstrings

### Requirements for ADK Tools

**Minimum 5 lines** with the following structure:

```python
def analyze_project_image(
    tool_context: ToolContext,
    image_path: str,
    analysis_type: str = "general"
) -> Dict[str, Any]:
    """
    Analyze uploaded project images using OpenAI Vision API.
    
    This tool processes images to identify project scope, damage assessment,
    and material requirements. Results are used to enhance bid card accuracy.
    
    Args:
        tool_context (ToolContext): ADK context providing access to session state
            and user information. Required for all ADK tools.
        image_path (str): Path to uploaded image file. Must be within allowed
            storage directories.
        analysis_type (str, optional): Type of analysis to perform. Options:
            - "general": Overall project assessment
            - "damage": Specific damage identification
            - "materials": Material and fixture identification
            Defaults to "general".
    
    Returns:
        dict: Analysis results with the following structure:
            {
                "status": "success" or "error",
                "analysis": "Detailed description of findings",
                "confidence": 0.0-1.0 confidence score,
                "detected_issues": ["issue1", "issue2"],
                "estimated_scope": "minor" or "major",
                "metadata": {
                    "processing_time": 1.23,
                    "model_used": "gpt-4-vision"
                }
            }
    
    Raises:
        ValueError: If image_path is invalid or file not found.
        PermissionError: If image is outside allowed directories.
        APIError: If vision API call fails.
    
    Example:
        result = analyze_project_image(
            tool_context,
            "/tmp/uploads/user123/roof.jpg",
            analysis_type="damage"
        )
        
        if result["status"] == "success":
            print(f"Found issues: {result['detected_issues']}")
    
    Note:
        This tool consumes API credits. Results are cached for 24 hours
        to minimize costs. Large images are automatically resized.
    """
```

## Method Docstrings

```python
def _validate_input(self, data: Dict[str, Any]) -> bool:
    """Validate input data for completeness.
    
    Args:
        data: Input dictionary to validate.
        
    Returns:
        True if valid, False otherwise.
    """
```

## Property Docstrings

```python
@property
def is_ready(self) -> bool:
    """Check if agent is initialized and ready.
    
    Returns:
        bool: True if all required components are loaded.
    """
    return self._initialized and self._tools_loaded
```

## Style Rules

### 1. First Line Summary
- One line, ending with period
- Imperative mood ("Analyze" not "Analyzes")
- Under 79 characters

### 2. Extended Description
- Blank line after summary
- Explain why, not just what
- Include important behavior details

### 3. Args Section
- List each parameter
- Include type in parentheses
- Describe purpose and constraints
- Note optional parameters and defaults
- Special note for `tool_context` parameter

### 4. Returns Section
- Specify type
- Describe structure for complex returns
- Provide example structure for dicts
- Include all possible status values

### 5. Other Sections (as needed)
- **Raises**: Exception types and conditions
- **Yields**: For generators
- **Example**: Usage examples
- **Note**: Important information
- **Warning**: Potential issues
- **See Also**: Related functions

## ADK-Specific Requirements

### Tool Functions MUST:
1. Have minimum 5-line docstring
2. Document `tool_context` parameter explicitly
3. Include `Returns` section with example structure
4. Show `status` field in return example
5. List possible error states

### Agent Classes MUST:
1. Describe agent's role and capabilities
2. List all available tools
3. Include usage example
4. Note model and configuration

## Examples of Good vs Bad

### ❌ Bad Example
```python
def save_data(ctx, data):
    """Save data."""  # Too brief!
    return db.save(data)
```

### ✅ Good Example
```python
def save_project_data(
    tool_context: ToolContext,
    project_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Save project data to Supabase with user association.
    
    Creates a new project record linked to the current user,
    validates required fields, and updates session state.
    
    Args:
        tool_context (ToolContext): ADK context for state access.
        project_data (dict): Project information containing:
            - title (str): Project title
            - description (str): Detailed description
            - budget_range (dict, optional): Min/max budget
            
    Returns:
        dict: Operation result:
            {
                "status": "success",
                "project_id": "uuid-string",
                "created_at": "2025-05-23T10:00:00Z"
            }
    """
```

## Validation Script

```python
# scripts/validate_docstrings.py
import ast
import sys

def check_docstring(node, filename, errors):
    """Validate docstring compliance."""
    if not ast.get_docstring(node):
        errors.append(f"{filename}:{node.lineno} - Missing docstring")
        return
        
    docstring = ast.get_docstring(node)
    lines = docstring.split('\n')
    
    # Check minimum length for tools
    if isinstance(node, ast.FunctionDef) and 'tool' in node.name:
        if len(lines) < 5:
            errors.append(
                f"{filename}:{node.lineno} - Tool docstring too short"
            )
    
    # Check for required sections
    if isinstance(node, ast.FunctionDef):
        if 'Args:' not in docstring and node.args.args:
            errors.append(
                f"{filename}:{node.lineno} - Missing Args section"
            )
        if 'Returns:' not in docstring:
            errors.append(
                f"{filename}:{node.lineno} - Missing Returns section"
            )
```

## Enforcement

1. **Pre-commit Hook**: Validates docstrings before commit
2. **CI Check**: Fails build if docstrings missing
3. **Code Review**: Human verification of quality
4. **Documentation Generator**: Auto-generates API docs from docstrings