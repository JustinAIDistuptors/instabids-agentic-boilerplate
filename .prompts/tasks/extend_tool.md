## Task Prompt: Extend or Add Tool to Agent

### Goal

Add a new tool or extend existing tool functionality for an ADK agent.

### Required Inputs

- `agent_path`: Path to agent module (e.g., "instabids.agents.homeowner")
- `tool_name`: Name of the tool (snake_case)
- `tool_description`: What the tool does
- `parameters`: List of parameters with types
- `return_type`: What the tool returns
- `implementation_type`: "new" or "extend"

### Tool Implementation Pattern

```python
def {tool_name}(
    tool_context: ToolContext,
    {parameters}
) -> Dict[str, Any]:
    """
    {tool_description}
    
    Args:
        tool_context (ToolContext): ADK context for state and session access.
        {parameter_docs}
        
    Returns:
        dict: Operation result with status.
        Example: {
            "status": "success",
            "data": {...},
            "message": "Operation completed"
        }
        
    Raises:
        ValueError: If input validation fails.
        RuntimeError: If operation cannot be completed.
    """
    # Input validation
    if not parameter:
        return {
            "status": "error",
            "message": "Parameter required"
        }
    
    try:
        # Implementation
        result = perform_operation()
        
        # Update state if needed
        tool_context.state["app:last_tool_call"] = tool_name
        
        return {
            "status": "success",
            "data": result,
            "message": f"{tool_name} completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
```

### Integration Steps

#### 1. Create Tool File

```python
# src/instabids/tools/{category}_tools.py
from google.adk.types import ToolContext
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
```

#### 2. Add to Agent

```python
# In agent.py
from instabids.tools.{category}_tools import {tool_name}

def _get_tools(self) -> List:
    return [
        {tool_name},  # Add new tool
        # ... existing tools
    ]
```

#### 3. Update Agent Instructions

```python
# In prompts.py, add to SYSTEM_INSTRUCTIONS
## Available Tools
- {tool_name}: {tool_description}
```

### Tool Categories

**Database Tools** (`supabase_tools.py`):
- CRUD operations
- Search functions
- Batch operations

**Vision Tools** (`vision_tools.py`):
- Image analysis
- Damage detection
- Material identification

**Communication Tools** (`notification_tools.py`):
- Email sending
- SMS dispatch
- In-app notifications

**Analytics Tools** (`analytics_tools.py`):
- Data aggregation
- Trend analysis
- Reporting

### Best Practices

1. **Always validate inputs**:
```python
if not isinstance(param, expected_type):
    raise ValueError(f"Expected {expected_type}, got {type(param)}")
```

2. **Use type hints**:
```python
def tool(tool_context: ToolContext, data: Dict[str, str]) -> Dict[str, Any]:
```

3. **Handle errors gracefully**:
```python
try:
    result = risky_operation()
except SpecificError as e:
    return {"status": "error", "message": f"Known issue: {e}"}
except Exception as e:
    logger.exception("Unexpected error")
    return {"status": "error", "message": "Operation failed"}
```

4. **Document side effects**:
```python
"""...
Side Effects:
    - Updates user preferences in database
    - Sends confirmation email
    - Logs action to audit trail
"""
```

### Testing Tools

```python
# tests/tools/test_{category}_tools.py
import pytest
from unittest.mock import Mock, patch
from instabids.tools.{category}_tools import {tool_name}


class Test{ToolName}:
    @pytest.fixture
    def mock_context(self):
        context = Mock()
        context.state = {}
        context.session_id = "test-session"
        return context
    
    def test_success_case(self, mock_context):
        result = {tool_name}(
            mock_context,
            param="valid_value"
        )
        
        assert result["status"] == "success"
        assert "data" in result
    
    def test_validation_error(self, mock_context):
        result = {tool_name}(
            mock_context,
            param=""  # Invalid
        )
        
        assert result["status"] == "error"
        assert "required" in result["message"]
    
    @patch('instabids.tools.{category}_tools.external_service')
    def test_external_failure(self, mock_service, mock_context):
        mock_service.side_effect = Exception("Service down")
        
        result = {tool_name}(mock_context, param="value")
        
        assert result["status"] == "error"
```

### Validation

- [ ] Tool has comprehensive docstring (≥5 lines)
- [ ] First parameter is `tool_context: ToolContext`
- [ ] Returns dict with "status" field
- [ ] All parameters have type hints
- [ ] Error cases return helpful messages
- [ ] Tests cover success and failure cases
- [ ] No security vulnerabilities
- [ ] Follows naming conventions