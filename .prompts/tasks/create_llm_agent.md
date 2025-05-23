## Task Prompt: Create New ADK Agent

### Goal

Generate a new ADK agent file with proper structure, configuration, and integration.

### Required Inputs

- `agent_name`: Snake_case name (e.g., "contractor_bidding")
- `agent_class`: PascalCase class name (e.g., "ContractorBiddingAgent")
- `agent_type`: Base class ("LiveAgent", "LlmAgent", or "WorkflowAgent")
- `description`: Agent purpose and capabilities
- `model_id`: Model to use (default: "gemini-2.0-flash-exp")
- `tools`: List of tool names this agent will use
- `module_path`: Path under src/instabids/agents/

### Step-by-Step Process

#### 1. Create Directory Structure

```bash
mkdir -p src/instabids/agents/{agent_name}
touch src/instabids/agents/{agent_name}/__init__.py
touch src/instabids/agents/{agent_name}/agent.py
touch src/instabids/agents/{agent_name}/prompts.py
```

#### 2. Generate Agent Class

```python
# src/instabids/agents/{agent_name}/agent.py
from google.adk.agents import {agent_type}
from google.adk.types import ToolContext
from typing import List, Optional, Dict, Any

from instabids.tools import {tool_imports}
from .prompts import SYSTEM_INSTRUCTIONS


class {agent_class}({agent_type}):
    """{description}
    
    This agent handles:
    - [Specific responsibility 1]
    - [Specific responsibility 2]
    - [Specific responsibility 3]
    """
    
    def __init__(self):
        super().__init__(
            name="{agent_name}",
            model="{model_id}",
            instructions=SYSTEM_INSTRUCTIONS,
            tools=self._get_tools(),
            temperature=0.7,
            max_output_tokens=2048
        )
    
    def _get_tools(self) -> List:
        """Return configured tools for this agent."""
        return [
            # Tool instances
        ]
    
    async def on_start(self, context: ToolContext) -> None:
        """Initialize agent state on startup."""
        context.state["app:agent_ready"] = True
        context.state["temp:session_id"] = context.session_id


# CRITICAL: Export as 'agent'
agent = {agent_class}()
```

#### 3. Create Prompts File

```python
# src/instabids/agents/{agent_name}/prompts.py

SYSTEM_INSTRUCTIONS = """
You are the {agent_class} for InstaBids.

## Your Role
{description}

## Core Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]
3. [Responsibility 3]

## Available Tools
- tool_1: [Description]
- tool_2: [Description]

## Interaction Guidelines
- Be professional and helpful
- Validate all inputs
- Provide clear feedback
- Learn from interactions

## State Management
Use these prefixes for state keys:
- user: for user-specific data
- app: for application-wide data
- temp: for temporary session data
"""
```

#### 4. Update __init__.py

```python
# src/instabids/agents/{agent_name}/__init__.py
from .agent import agent

__all__ = ["agent"]
```

#### 5. Register in ADK Components

Add to `.adk/components.json`:
```json
{
  "name": "{agent_name}",
  "module": "instabids.agents.{agent_name}",
  "class": "{agent_class}",
  "description": "{description}"
}
```

#### 6. Create Tests

```python
# tests/agents/test_{agent_name}.py
import pytest
from google.adk.testing import AgentTestHarness
from instabids.agents.{agent_name} import agent


class Test{agent_class}:
    @pytest.fixture
    def harness(self):
        return AgentTestHarness(agent=agent)
    
    def test_agent_initialization(self, harness):
        """Test agent initializes correctly."""
        assert harness.agent.name == "{agent_name}"
        assert harness.agent.model == "{model_id}"
    
    def test_tools_available(self, harness):
        """Test all required tools are available."""
        tool_names = [t.name for t in harness.agent.tools]
        assert "expected_tool" in tool_names
    
    @pytest.mark.asyncio
    async def test_basic_interaction(self, harness):
        """Test basic agent interaction."""
        response = await harness.run("Test input")
        assert response is not None
```

### Validation Checklist

- [ ] Agent inherits from correct base class
- [ ] Exported as `agent` (not `root_agent`)
- [ ] All tools imported and configured
- [ ] Comprehensive docstrings
- [ ] State management uses proper prefixes
- [ ] Tests cover initialization and basic interaction
- [ ] Added to `.adk/components.json`
- [ ] No violations of `docs/COMMON_PITFALLS.md`

### Common Patterns

**For LiveAgent (streaming)**:
```python
async def on_message(self, message: str, context: ToolContext):
    # Handle streaming messages
    pass
```

**For LlmAgent (request-response)**:
```python
def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
    # Process and return response
    pass
```

### Final Steps

1. Run tests: `poetry run pytest tests/agents/test_{agent_name}.py`
2. Check in ADK UI: `poetry run adk web`
3. Commit with message: `feat(agents): add {agent_name} agent`