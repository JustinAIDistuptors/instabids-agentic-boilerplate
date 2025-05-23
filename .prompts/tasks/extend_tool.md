## Task: Extend Agent with New Tool

### Goal

Add or update a FunctionTool in an existing ADK agent.

### Inputs Required

- `agent_path`: Path to agent module
- `tool_name`: Name of the tool function
- `tool_purpose`: What the tool does
- `parameters`: List of parameters with types
- `return_type`: Expected return structure
- `implementation`: Tool logic (optional)

### Implementation Steps

1. **Create Tool Function**
   ```python
   # src/instabids/tools/{category}_tools.py
   from google.adk.types import ToolContext
   from typing import Dict, Any, Optional
   import json
   
   def {tool_name}(
       tool_context: ToolContext,
       {parameters}
   ) -> Dict[str, Any]:
       """
       {tool_purpose}
       
       Args:
           tool_context (ToolContext): ADK context for state access.
           {parameter_docs}
           
       Returns:
           dict: {return_description}
           Example: {return_example}
       """
       try:
           # Validate inputs
           if not {validation_condition}:
               return {
                   "status": "error",
                   "message": "Invalid input: {validation_message}"
               }
           
           # Access state if needed
           user_id = tool_context.state.get("user:id")
           
           # Tool implementation
           {implementation_logic}
           
           # Update state if needed
           tool_context.state["{state_key}"] = result_value
           
           return {
               "status": "success",
               {return_fields}
           }
           
       except Exception as e:
           return {
               "status": "error",
               "message": str(e),
               "error_type": type(e).__name__
           }
   ```

2. **Add Tool to Agent**
   ```python
   # Update agent file
   from instabids.tools.{category}_tools import {tool_name}
   
   class {AgentClass}(LiveAgent):
       def __init__(self):
           super().__init__(
               # ... existing config ...
               tools=[
                   # ... existing tools ...
                   {tool_name},  # Add new tool
               ]
           )
   ```

3. **Create Tool Tests**
   ```python
   # tests/tools/test_{category}_tools.py
   import pytest
   from google.adk.types import ToolContext
   from instabids.tools.{category}_tools import {tool_name}
   
   @pytest.fixture
   def mock_context():
       """Mock tool context for testing."""
       class MockContext:
           def __init__(self):
               self.state = {"user:id": "test-user-123"}
       return MockContext()
   
   def test_{tool_name}_success(mock_context):
       result = {tool_name}(
           mock_context,
           {test_params}
       )
       
       assert result["status"] == "success"
       assert "{expected_field}" in result
   
   def test_{tool_name}_validation(mock_context):
       result = {tool_name}(
           mock_context,
           {invalid_params}
       )
       
       assert result["status"] == "error"
       assert "Invalid input" in result["message"]
   
   def test_{tool_name}_error_handling(mock_context):
       # Test with params that cause exception
       result = {tool_name}(
           mock_context,
           {error_params}
       )
       
       assert result["status"] == "error"
       assert "error_type" in result
   ```

### Tool Categories

**Database Tools** (`supabase_tools.py`):
- CRUD operations
- Batch operations
- Search functions
- Aggregations

**Vision Tools** (`vision_tools.py`):
- Image analysis
- Object detection
- Damage assessment
- Material identification

**Notification Tools** (`notification_tools.py`):
- Email sending
- SMS dispatch
- In-app notifications
- Webhook triggers

**Utility Tools** (`utility_tools.py`):
- Data validation
- Format conversion
- Calculations
- External API calls

### Best Practices

1. **Always validate inputs** before processing
2. **Return consistent structure** with "status" field
3. **Handle exceptions** gracefully
4. **Use state prefixes** correctly
5. **Document thoroughly** with examples
6. **Test edge cases** comprehensively
7. **Log important operations** for debugging
8. **Consider rate limits** for external calls
9. **Implement retries** where appropriate
10. **Cache results** when beneficial

### Common Patterns

**Async Tool**:
```python
async def async_tool(
    tool_context: ToolContext,
    param: str
) -> Dict[str, Any]:
    """Async tool implementation."""
    result = await external_api_call(param)
    return {"status": "success", "data": result}
```

**Batch Operation**:
```python
def batch_operation(
    tool_context: ToolContext,
    items: List[Dict]
) -> Dict[str, Any]:
    """Process multiple items."""
    results = []
    errors = []
    
    for item in items:
        try:
            result = process_item(item)
            results.append(result)
        except Exception as e:
            errors.append({"item": item, "error": str(e)})
    
    return {
        "status": "partial" if errors else "success",
        "processed": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }
```