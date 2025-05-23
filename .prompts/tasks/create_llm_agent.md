## Task: Create New ADK LlmAgent

### Goal

Generate a new Python file for an ADK LlmAgent within the `src/instabids/agents/` directory.

### Inputs Required

- `agent_name`: (string) e.g., "bid_analyzer"
- `class_name`: (string) e.g., "BidAnalyzerAgent"
- `description`: (string) Agent's purpose
- `model_id`: (string) Default: "gemini-2.0-flash-exp"
- `instructions`: (string) Detailed LLM instructions
- `tools`: (list) Tool function names
- `temperature`: (float) Default: 0.7
- `max_output_tokens`: (int) Default: 2048

### Implementation Steps

1. **Create Directory Structure**
   ```bash
   src/instabids/agents/{agent_name}/
   ├── __init__.py
   └── agent.py
   ```

2. **Generate Agent Class**
   ```python
   # src/instabids/agents/{agent_name}/agent.py
   from google.adk.agents import LlmAgent
   from google.adk.types import ToolContext
   from typing import List, Optional
   
   # Import tools
   from instabids.tools import {tool_imports}
   
   class {class_name}(LlmAgent):
       """{description}
       
       This agent uses the {model_id} model for {primary_purpose}.
       """
       
       def __init__(self):
           super().__init__(
               name="{agent_name}",
               model="{model_id}",
               instructions="""
               {instructions}
               """,
               tools=[
                   {tool_list}
               ],
               temperature={temperature},
               max_output_tokens={max_output_tokens}
           )
   
   # CRITICAL: Export as 'agent'
   agent = {class_name}()
   ```

3. **Create __init__.py**
   ```python
   # src/instabids/agents/{agent_name}/__init__.py
   """LlmAgent for {description}."""
   
   from .agent import agent
   
   __all__ = ["agent"]
   ```

4. **Update components.json**
   ```json
   {
     "name": "{agent_name}",
     "module": "instabids.agents.{agent_name}",
     "class": "{class_name}",
     "description": "{description}"
   }
   ```

5. **Generate Tests**
   ```python
   # tests/agents/test_{agent_name}.py
   import pytest
   from google.adk.testing import AgentTestHarness
   from instabids.agents.{agent_name} import agent
   
   @pytest.fixture
   def test_harness():
       return AgentTestHarness(
           agent=agent,
           mock_llm_responses=True
       )
   
   def test_agent_initialization():
       assert agent.name == "{agent_name}"
       assert agent.model == "{model_id}"
       assert len(agent.tools) == {tool_count}
   
   def test_agent_response(test_harness):
       response = test_harness.run("Test prompt")
       assert response is not None
       assert isinstance(response, str)
   ```

### Validation Checklist

- [ ] Agent class inherits from correct base (LlmAgent)
- [ ] Export variable is named `agent` (not `root_agent`)
- [ ] All tools are imported correctly
- [ ] Instructions are clear and comprehensive
- [ ] Temperature and token limits are appropriate
- [ ] __init__.py exports the agent
- [ ] Added to .adk/components.json
- [ ] Tests are comprehensive
- [ ] Docstrings follow conventions

### Common Patterns

**For Analysis Agents**:
- Lower temperature (0.3-0.5)
- Structured output format in instructions
- Include validation tools

**For Creative Agents**:
- Higher temperature (0.7-0.9)
- More flexible instructions
- Larger token limits

**For Decision Agents**:
- Medium temperature (0.5-0.7)
- Clear decision criteria in instructions
- Include scoring/ranking tools