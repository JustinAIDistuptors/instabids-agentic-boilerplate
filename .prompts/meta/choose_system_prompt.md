## Meta Prompt: Choose System Prompt

### Purpose

Analyze the current context and select the most appropriate system prompt for the task.

### Available System Prompts

1. **master_code_builder.md**
   - For: General development, architecture, integration
   - Keywords: build, implement, create, develop, integrate

2. **homeowner_agent_writer.md**
   - For: HomeownerAgent specific implementation
   - Keywords: homeowner, conversation, scoping, preferences

3. **debugging_agent.md**
   - For: Fixing errors, troubleshooting, debugging
   - Keywords: error, fix, debug, issue, problem

4. **prompt_selector.md**
   - For: Selecting prompts, meta-tasks
   - Keywords: select, choose, prompt, meta

### Selection Process

1. Parse the request for key terms
2. Match against prompt specializations
3. Consider task complexity
4. Return most specific applicable prompt

### Decision Logic

```python
if "error" in request or "fix" in request:
    return "system/debugging_agent.md"
elif "homeowner" in request or "conversation" in request:
    return "system/homeowner_agent_writer.md"
elif "select" in request and "prompt" in request:
    return "system/prompt_selector.md"
else:
    return "system/master_code_builder.md"  # Default
```

### Return Format

Return ONLY the relative path:
```
system/selected_prompt.md
```

### Examples

Request: "Fix the Supabase connection error"
Return: `system/debugging_agent.md`

Request: "Implement the contractor bidding agent"
Return: `system/master_code_builder.md`

Request: "Update homeowner conversation flow"
Return: `system/homeowner_agent_writer.md`