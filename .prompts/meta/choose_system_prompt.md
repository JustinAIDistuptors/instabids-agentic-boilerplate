## Meta Prompt: Choose System Prompt

### Task

Analyze the current conversation context and select the most appropriate system prompt for the task at hand.

### Available System Prompts

1. **master_code_builder.md**
   - Use for: General coding tasks, orchestration, multi-file changes
   - Keywords: "build", "create project", "implement feature", "refactor"

2. **homeowner_agent_writer.md**
   - Use for: HomeownerAgent specific implementation
   - Keywords: "homeowner", "project scoping", "conversation flow", "Q&A"

3. **adk_specialist.md**
   - Use for: ADK-specific patterns, agent architecture, tools
   - Keywords: "ADK", "agent pattern", "tool development", "A2A protocol"

4. **supabase_integration_agent.md**
   - Use for: Database operations, RLS, storage, migrations
   - Keywords: "database", "Supabase", "RLS", "migration", "storage"

5. **debugging_agent.md**
   - Use for: Fixing errors, troubleshooting, issue diagnosis
   - Keywords: "error", "bug", "not working", "debug", "fix"

### Selection Logic

```python
def select_system_prompt(user_message: str) -> str:
    """
    Select appropriate system prompt based on context.
    
    Returns:
        str: Path to selected prompt file.
    """
    message_lower = user_message.lower()
    
    # Check for debugging indicators
    debug_keywords = ["error", "bug", "fix", "not working", "issue"]
    if any(keyword in message_lower for keyword in debug_keywords):
        return "system/debugging_agent.md"
    
    # Check for Supabase/database tasks
    db_keywords = ["database", "supabase", "rls", "migration", "query"]
    if any(keyword in message_lower for keyword in db_keywords):
        return "system/supabase_integration_agent.md"
    
    # Check for ADK-specific tasks
    adk_keywords = ["adk", "agent pattern", "tool", "a2a", "workflow"]
    if any(keyword in message_lower for keyword in adk_keywords):
        return "system/adk_specialist.md"
    
    # Check for HomeownerAgent tasks
    homeowner_keywords = ["homeowner", "scoping", "conversation", "q&a"]
    if any(keyword in message_lower for keyword in homeowner_keywords):
        return "system/homeowner_agent_writer.md"
    
    # Default to master builder for general tasks
    return "system/master_code_builder.md"
```

### Decision Factors

1. **Error States**: Debugging agent for any error messages
2. **Component Focus**: Specialized agents for specific components
3. **Task Complexity**: Master builder for multi-component tasks
4. **Domain Expertise**: Specialist agents for deep technical work

### Output Format

Return ONLY the relative path to the selected prompt file.

Example outputs:
- `system/debugging_agent.md`
- `system/master_code_builder.md`
- `system/adk_specialist.md`

### Context Clues

**High Priority Indicators**:
- Error messages or stack traces → debugging_agent
- Database operations → supabase_integration_agent
- Agent architecture questions → adk_specialist
- Feature implementation → master_code_builder

**Consider Previous Context**:
- If already working on a specific component, continue with same specialist
- If switching contexts, select new appropriate prompt
- When unclear, default to master_code_builder