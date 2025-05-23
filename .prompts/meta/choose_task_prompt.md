## Meta Prompt: Choose Task Prompt

### Purpose

Select the most appropriate task-specific prompt based on the requested action.

### Available Task Prompts

1. **create_llm_agent.md**
   - For: Creating new ADK agents
   - Keywords: create agent, new agent, add agent

2. **extend_tool.md**
   - For: Adding or modifying tools
   - Keywords: add tool, extend tool, new function

3. **debug_supabase.md**
   - For: Database-related issues
   - Keywords: database, supabase, RLS, permission

4. **generate_tests.md**
   - For: Writing test cases
   - Keywords: test, testing, coverage, pytest

5. **critique_code.md**
   - For: Code review and feedback
   - Keywords: review, critique, feedback, quality

6. **doctor_route.md**
   - For: Health check implementation
   - Keywords: health, doctor, monitoring, status

### Selection Logic

```python
def select_task_prompt(request: str) -> str:
    request_lower = request.lower()
    
    if any(word in request_lower for word in ["test", "pytest", "coverage"]):
        return "tasks/generate_tests.md"
    
    elif any(word in request_lower for word in ["review", "critique", "quality"]):
        return "tasks/critique_code.md"
    
    elif any(word in request_lower for word in ["agent", "create agent"]):
        return "tasks/create_llm_agent.md"
    
    elif any(word in request_lower for word in ["tool", "function", "extend"]):
        return "tasks/extend_tool.md"
    
    elif any(word in request_lower for word in ["database", "supabase", "rls"]):
        return "tasks/debug_supabase.md"
    
    elif any(word in request_lower for word in ["health", "doctor", "monitor"]):
        return "tasks/doctor_route.md"
    
    else:
        # Default to most general
        return "tasks/create_llm_agent.md"
```

### Specificity Priority

When multiple prompts could apply, choose the most specific:

1. Exact match (e.g., "debug supabase" → `debug_supabase.md`)
2. Primary keyword match (e.g., "add tool" → `extend_tool.md`)
3. Secondary keyword match
4. Default fallback

### Return Format

Return ONLY the relative path:
```
tasks/selected_task.md
```

### Examples

Request: "Write tests for the homeowner agent"
Return: `tasks/generate_tests.md`

Request: "Add a notification tool to the contractor agent"
Return: `tasks/extend_tool.md`

Request: "Review the save_project function"
Return: `tasks/critique_code.md`

Request: "Fix RLS policy for messages table"
Return: `tasks/debug_supabase.md`