## Meta Prompt: Choose Task Prompt

### Task

Analyze the user's request and select the most appropriate task prompt template.

### Available Task Prompts

1. **create_llm_agent.md**
   - Use for: Creating new ADK agents from scratch
   - Keywords: "create agent", "new agent", "implement agent"
   - Output: Complete agent implementation with tests

2. **extend_tool.md**
   - Use for: Adding or modifying tools for existing agents
   - Keywords: "add tool", "new function", "extend capability"
   - Output: Tool function with integration

3. **debug_supabase.md**
   - Use for: Troubleshooting database-related issues
   - Keywords: "database error", "RLS", "403", "permission denied"
   - Output: Diagnosis and fix

4. **doctor_route.md**
   - Use for: Implementing health check endpoints
   - Keywords: "health check", "monitoring", "doctor route"
   - Output: Health check implementation

5. **generate_tests.md**
   - Use for: Creating test suites for existing code
   - Keywords: "test", "coverage", "unit test", "integration test"
   - Output: Comprehensive test files

6. **critique_code.md**
   - Use for: Code review and improvement suggestions
   - Keywords: "review", "improve", "refactor", "optimize"
   - Output: Detailed review with improvements

### Selection Algorithm

```python
def select_task_prompt(request: str, context: dict) -> str:
    """
    Select appropriate task prompt based on request.
    
    Args:
        request: User's request text
        context: Additional context (current file, error state, etc.)
        
    Returns:
        str: Path to selected task prompt
    """
    request_lower = request.lower()
    
    # Priority 1: Error states need debugging
    if context.get("has_error") or "error" in request_lower:
        if "supabase" in request_lower or "database" in request_lower:
            return "tasks/debug_supabase.md"
        return "tasks/critique_code.md"  # General debugging
    
    # Priority 2: Explicit task requests
    task_mapping = {
        "create.*agent": "tasks/create_llm_agent.md",
        "add.*tool|new.*function": "tasks/extend_tool.md",
        "health.*check|doctor.*route": "tasks/doctor_route.md",
        "write.*test|test.*coverage": "tasks/generate_tests.md",
        "review.*code|improve|refactor": "tasks/critique_code.md",
    }
    
    for pattern, prompt in task_mapping.items():
        if re.search(pattern, request_lower):
            return prompt
    
    # Priority 3: Context-based selection
    if context.get("current_file", "").endswith("_test.py"):
        return "tasks/generate_tests.md"
    
    if context.get("current_file", "").endswith("agent.py"):
        return "tasks/create_llm_agent.md"
    
    # Default: Code review for general requests
    return "tasks/critique_code.md"
```

### Task Characteristics

| Task | Input Required | Output Type | Typical Duration |
|------|---------------|-------------|------------------|
| create_llm_agent | Agent spec | Multiple files | 10-15 min |
| extend_tool | Tool spec | Single function | 5-10 min |
| debug_supabase | Error details | Fix + explanation | 5-10 min |
| doctor_route | Requirements | Route + tests | 10 min |
| generate_tests | Code to test | Test file | 10-20 min |
| critique_code | Code to review | Review document | 5-15 min |

### Decision Matrix

```
IF request contains "error" AND "database":
    → debug_supabase.md

ELSE IF request contains "create" AND "agent":
    → create_llm_agent.md

ELSE IF request contains "add" AND ("tool" OR "function"):
    → extend_tool.md

ELSE IF request contains "test":
    → generate_tests.md

ELSE IF request contains "health" OR "monitor":
    → doctor_route.md

ELSE IF request asks for improvement:
    → critique_code.md

ELSE:
    → critique_code.md (safe default)
```

### Context Signals

**Strong Signals**:
- Error stack trace → Debug task
- "Create new" → Creation task
- "Add to existing" → Extension task
- "Test this" → Test generation

**Weak Signals**:
- Current file type
- Previous conversation
- Time of day (feature work vs. debugging)

### Output

Return ONLY the relative path. Examples:
- `tasks/create_llm_agent.md`
- `tasks/debug_supabase.md`
- `tasks/generate_tests.md`