## Task: Critique and Improve Code

### Goal

Review code for quality, adherence to best practices, and potential issues. Provide actionable feedback and improved versions.

### Review Criteria

#### 1. ADK Best Practices
- [ ] Correct import pattern (`from google import genai`)
- [ ] Agent exported as `agent` not `root_agent`
- [ ] Tools have `tool_context` as first parameter
- [ ] State keys use proper prefixes (`user:`, `app:`, `temp:`)
- [ ] Model ID is appropriate for use case
- [ ] No AdkApp wrapper pattern used

#### 2. Code Quality
- [ ] Clear, descriptive naming
- [ ] Proper type hints
- [ ] Comprehensive docstrings
- [ ] DRY principle followed
- [ ] Single responsibility per function/class
- [ ] Appropriate abstraction levels

#### 3. Error Handling
- [ ] All exceptions caught appropriately
- [ ] Meaningful error messages
- [ ] Graceful degradation
- [ ] No silent failures
- [ ] Proper logging

#### 4. Security
- [ ] Input validation
- [ ] No hardcoded secrets
- [ ] SQL injection prevention
- [ ] Proper authentication checks
- [ ] RLS considerations

#### 5. Performance
- [ ] Efficient algorithms
- [ ] Appropriate caching
- [ ] Batch operations where possible
- [ ] No unnecessary loops
- [ ] Async where beneficial

### Review Process

```python
# Example code review format
"""
Code Review: {module_name}

Overall Score: 8/10

## Strengths
- Clear structure and organization
- Good error handling
- Comprehensive docstrings

## Issues Found

### 🔴 Critical (Must Fix)
1. **Import Pattern**
   - Line 5: `import google.generativeai as genai`
   - Fix: `from google import genai`

2. **Missing State Prefix**
   - Line 42: `tool_context.state["project_id"] = id`
   - Fix: `tool_context.state["user:current_project_id"] = id`

### 🟡 Important (Should Fix)
1. **No Input Validation**
   - Function `save_project` accepts any data
   - Add Pydantic model for validation

### 🟢 Suggestions (Nice to Have)
1. **Consider Caching**
   - Frequent DB queries could be cached
   - Use @lru_cache or Redis

## Improved Version
"""
```

### Code Improvement Template

```python
# BEFORE: Original code with issues
def problematic_function(data):
    # No type hints
    # No docstring
    # No validation
    result = db.insert(data)  # No error handling
    return result

# AFTER: Improved version
from typing import Dict, Any
from pydantic import BaseModel, validator
import logging

logger = logging.getLogger(__name__)

class ProjectData(BaseModel):
    """Validated project data model."""
    title: str
    description: str
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v

def save_project(
    tool_context: ToolContext,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Save project with validation and error handling.
    
    Args:
        tool_context (ToolContext): ADK context for state.
        data (dict): Project data to save.
        
    Returns:
        dict: Result with status and project ID.
    """
    try:
        # Validate input
        validated_data = ProjectData(**data)
        
        # Add metadata
        project_dict = validated_data.dict()
        project_dict['owner_id'] = tool_context.state.get("user:id")
        
        # Save to database
        result = db.table('projects').insert(project_dict).execute()
        
        # Update state
        tool_context.state["user:current_project_id"] = result.data[0]['id']
        
        logger.info(f"Project saved: {result.data[0]['id']}")
        
        return {
            "status": "success",
            "project_id": result.data[0]['id']
        }
        
    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        return {
            "status": "error",
            "message": "Invalid project data",
            "errors": e.errors()
        }
    except Exception as e:
        logger.error(f"Failed to save project: {e}")
        return {
            "status": "error",
            "message": "Failed to save project"
        }
```

### Common Patterns to Fix

#### Pattern 1: Async Without Await
```python
# BAD
async def get_data():
    return db.fetch()  # Missing await

# GOOD
async def get_data():
    return await db.fetch()
```

#### Pattern 2: Mutable Default Arguments
```python
# BAD
def process(items=[]):
    items.append("new")
    return items

# GOOD
def process(items=None):
    if items is None:
        items = []
    items.append("new")
    return items
```

#### Pattern 3: Broad Exception Handling
```python
# BAD
try:
    complex_operation()
except:
    pass  # Silent failure

# GOOD
try:
    complex_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error")
    return error_response(e)
```

### Checklist for Review

```markdown
## Code Review Checklist

### Structure
- [ ] File organization logical
- [ ] Imports organized (stdlib, third-party, local)
- [ ] No circular imports
- [ ] Appropriate module separation

### Documentation
- [ ] Module docstring present
- [ ] All public functions documented
- [ ] Complex logic has inline comments
- [ ] README updated if needed

### Testing
- [ ] Unit tests exist
- [ ] Edge cases covered
- [ ] Integration tests for workflows
- [ ] Test coverage > 80%

### ADK Specific
- [ ] Components.json updated
- [ ] Agent registration correct
- [ ] Tool signatures valid
- [ ] State management proper

### Deployment
- [ ] Environment variables documented
- [ ] Migration scripts included
- [ ] CI/CD pipeline passes
- [ ] Performance benchmarked
```

### Output Format

```markdown
# Code Review Summary

**File**: `{file_path}`
**Reviewer**: AI Code Critic
**Date**: {current_date}

## Overview
{brief_summary}

## Critical Issues (0)
{list_critical_issues_or_none}

## Warnings (2)
1. {warning_1}
2. {warning_2}

## Suggestions (3)
1. {suggestion_1}
2. {suggestion_2}
3. {suggestion_3}

## Recommended Actions
1. {action_1}
2. {action_2}

## Approval Status
✅ Approved with minor changes
```