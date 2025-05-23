## Task Prompt: Critique and Review Code

### Goal

Review code for quality, adherence to standards, and potential issues. Provide actionable feedback.

### Review Checklist

#### 1. ADK Compliance
- [ ] Imports use `from google import genai`
- [ ] Agents exported as `agent`
- [ ] Tools have `tool_context: ToolContext` first
- [ ] State keys use proper prefixes
- [ ] Model ID is valid
- [ ] Tool returns include "status"

#### 2. Code Quality
- [ ] Functions have docstrings
- [ ] Type hints are used
- [ ] No code duplication
- [ ] Proper error handling
- [ ] Logging is appropriate
- [ ] Comments explain "why" not "what"

#### 3. Security
- [ ] No hardcoded credentials
- [ ] Input validation present
- [ ] SQL injection prevention
- [ ] Path traversal protection
- [ ] Proper authentication checks

#### 4. Performance
- [ ] No unnecessary loops
- [ ] Efficient database queries
- [ ] Proper caching usage
- [ ] Async/await used correctly
- [ ] No blocking operations

#### 5. Testing
- [ ] Tests exist for new code
- [ ] Edge cases covered
- [ ] Mocks used appropriately
- [ ] Tests are maintainable

### Review Format

```markdown
## Code Review: [Component Name]

### Summary
- **Overall Quality**: 🟢 Good / 🟡 Needs Improvement / 🔴 Major Issues
- **ADK Compliance**: ✅ Pass / ❌ Fail
- **Test Coverage**: X%

### Strengths
1. [Positive aspect 1]
2. [Positive aspect 2]

### Issues Found

#### 🔴 Critical Issues
1. **[Issue Title]**
   - Location: `file.py:line`
   - Problem: [Description]
   - Impact: [Why this matters]
   - Fix: 
   ```python
   # Suggested correction
   ```

#### 🟡 Improvements Needed
1. **[Improvement Title]**
   - Location: `file.py:line`
   - Current: [What exists]
   - Better: [What it should be]
   - Example:
   ```python
   # Improved version
   ```

#### 🔵 Suggestions
1. **[Suggestion Title]**
   - Consider: [Recommendation]
   - Benefits: [Why this helps]

### Action Items
- [ ] Fix critical issue #1
- [ ] Address improvement #1
- [ ] Add missing tests
- [ ] Update documentation
```

### Common Issues to Check

#### Wrong Import Pattern
```python
# ❌ Wrong
import google.generativeai as genai

# ✅ Correct
from google import genai
```

#### Missing Tool Context
```python
# ❌ Wrong
def my_tool(data: dict) -> dict:
    pass

# ✅ Correct
def my_tool(tool_context: ToolContext, data: dict) -> dict:
    pass
```

#### Improper State Management
```python
# ❌ Wrong
context.state["project_id"] = "123"

# ✅ Correct
context.state["user:project_id"] = "123"
```

#### Poor Error Handling
```python
# ❌ Wrong
try:
    result = risky_operation()
except:
    return {"error": "Failed"}

# ✅ Correct
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return {
        "status": "error",
        "message": f"Failed to complete operation: {str(e)}",
        "error_code": "OPERATION_FAILED"
    }
```

#### Missing Validation
```python
# ❌ Wrong
def save_project(tool_context, title, budget):
    # Direct use without validation
    
# ✅ Correct
def save_project(tool_context, title: str, budget: float):
    if not title or len(title) < 3:
        return {"status": "error", "message": "Title too short"}
    
    if budget < 0:
        return {"status": "error", "message": "Invalid budget"}
```

### Review Priorities

1. **Security vulnerabilities** - Fix immediately
2. **Data corruption risks** - Fix before deployment
3. **Performance bottlenecks** - Fix if impacting users
4. **Code maintainability** - Fix in next iteration
5. **Style issues** - Fix when touching the code

### Automated Checks

Run these before manual review:
```bash
# Linting
poetry run ruff check .

# Type checking
poetry run mypy .

# Security scan
poetry run bandit -r src/

# Test coverage
poetry run pytest --cov=instabids
```

### Feedback Guidelines

1. **Be specific**: Point to exact lines and files
2. **Be constructive**: Suggest improvements, not just problems
3. **Be educational**: Explain why something is an issue
4. **Be practical**: Consider development constraints
5. **Be positive**: Acknowledge good practices

### Sample Review Comments

**For Good Code**:
> "Excellent error handling here. The specific exception types and detailed messages will help with debugging."

**For Issues**:
> "This tool is missing the required `tool_context` parameter. Add it as the first parameter to comply with ADK standards. See docs/ADK_BEST_PRACTICES.md for details."

**For Improvements**:
> "Consider extracting this logic into a separate function for better testability and reuse. This would also make the main function more readable."

### Post-Review Actions

1. Create GitHub issues for major problems
2. Update tests to prevent regression
3. Document patterns in team wiki
4. Share learnings with team