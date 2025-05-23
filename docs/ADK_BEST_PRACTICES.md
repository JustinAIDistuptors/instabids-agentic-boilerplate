# 📘 ADK Best Practices for InstaBids

> **Project-specific patterns for Google ADK 1.0.0+ development**

## 🎯 Core Principles

### 1. Plain Python Agents (Not AdkApp)

**✅ DO THIS** (90% of projects):
```python
# src/instabids/agents/homeowner/agent.py
from google.adk.agents import LiveAgent

class HomeownerAgent(LiveAgent):
    pass

agent = HomeownerAgent()  # Export as 'agent'
```

**❌ NOT THIS**:
```python
# Don't use AdkApp wrapper
from google.adk import AdkApp
class MyApp(AdkApp):  # Avoid this pattern
    pass
```

### 2. Agent Registration

```json
// .adk/components.json
{
  "agents": [
    {
      "name": "homeowner",
      "module": "instabids.agents.homeowner",
      "class": "HomeownerAgent"
    },
    {
      "name": "bidcard",
      "module": "instabids.agents.bidcard",
      "class": "BidCardAgent"
    }
  ]
}
```

## 🔧 Agent Design Patterns

### Conversation Management

```python
class HomeownerAgent(LiveAgent):
    def __init__(self):
        super().__init__(
            name="homeowner",
            model="gemini-2.0-flash-exp",
            instructions="""
            You are a helpful home improvement project assistant.
            Guide homeowners through project scoping with empathy.
            """,
            tools=[analyze_image, save_project, get_user_preferences]
        )
```

### State Management

```python
def save_project_state(tool_context: ToolContext, data: dict) -> dict:
    """Save project data with proper state prefixes."""
    # User-specific data
    tool_context.state["user:current_project"] = data["project_id"]
    tool_context.state["user:preferences"] = data.get("preferences", {})
    
    # Application-wide data
    tool_context.state["app:last_activity"] = datetime.now().isoformat()
    
    # Temporary data (cleared after session)
    tool_context.state["temp:draft_data"] = data.get("draft")
    
    return {"status": "success", "saved_keys": 3}
```

### Tool Development

```python
def analyze_project_image(
    tool_context: ToolContext,
    image_path: str,
    analysis_type: str = "general"
) -> dict:
    """
    Analyze uploaded project images using OpenAI Vision.
    
    Args:
        tool_context (ToolContext): ADK context for state access.
        image_path (str): Path to uploaded image.
        analysis_type (str): Type of analysis - 'general', 'damage', 'scope'.
        
    Returns:
        dict: Analysis results with confidence score.
        Example: {
            "status": "success",
            "analysis": "Roof shows signs of water damage...",
            "confidence": 0.85,
            "detected_issues": ["water_damage", "missing_shingles"]
        }
    """
    # Implementation here
    pass
```

## 🔄 Multi-Agent Patterns

### Sequential Processing

```python
from google.adk.agents import SequentialAgent

workflow = SequentialAgent(
    name="project_workflow",
    agents=[
        HomeownerAgent(),
        BidCardAgent(),
        OutboundRecruiterAgent()
    ]
)
```

### Agent Communication (A2A)

```python
# src/instabids/a2a/events.py
from dataclasses import dataclass
from google.adk.events import Event

@dataclass
class ProjectCreatedEvent(Event):
    project_id: str
    owner_id: str
    category: str
    confidence: float

@dataclass
class BidCardReadyEvent(Event):
    bid_card_id: str
    project_id: str
    status: str  # 'draft' or 'final'
```

## 🗄️ Session Management

### Persistent Memory

```python
from google.adk.sessions import PersistentMemory

class ProjectMemory(PersistentMemory):
    def save_preference(self, user_id: str, key: str, value: any):
        """Save user preference with confidence tracking."""
        pref_key = f"user:{user_id}:pref:{key}"
        self.set(pref_key, {
            "value": value,
            "confidence": 0.8,
            "updated_at": datetime.now().isoformat()
        })
```

### Context Preservation

```python
def preserve_context(agent: LiveAgent, session_id: str):
    """Preserve conversation context across sessions."""
    context_key = f"app:session:{session_id}:context"
    
    # Save after each turn
    agent.after_turn_callback = lambda ctx: 
        ctx.state.set(context_key, {
            "messages": ctx.messages[-10:],  # Last 10 messages
            "extracted_data": ctx.state.get("temp:extracted_data"),
            "timestamp": datetime.now().isoformat()
        })
```

## 🚀 Performance Optimization

### Model Selection

```python
# Fast operations (< 2s response time)
fast_agent = LiveAgent(
    model="gemini-2.0-flash-exp",
    temperature=0.3,  # Lower for consistency
    max_output_tokens=1024
)

# Complex reasoning
reasoning_agent = LlmAgent(
    model="gemini-2.0-pro",
    temperature=0.7,
    max_output_tokens=4096
)
```

### Streaming Responses

```python
async def stream_project_analysis(agent: LiveAgent, project_data: dict):
    """Stream responses for better UX."""
    async for event in agent.run_live(project_data):
        if event.type == "content":
            yield event.content
        elif event.type == "tool_call":
            yield f"\n[Analyzing {event.tool_name}...]\n"
```

## 🔌 Tool Integration

### Supabase Tools

```python
from instabids.tools import supabase_tools

homeowner_tools = [
    supabase_tools.get_project,
    supabase_tools.save_project,
    supabase_tools.update_preferences,
    supabase_tools.search_contractors
]
```

### Vision Tools

```python
from instabids.tools import vision_tools

analysis_tools = [
    vision_tools.analyze_damage,
    vision_tools.estimate_scope,
    vision_tools.identify_materials
]
```

## 🧪 Testing Patterns

### Agent Testing

```python
import pytest
from google.adk.testing import AgentTestHarness

@pytest.fixture
def homeowner_harness():
    return AgentTestHarness(
        agent=HomeownerAgent(),
        mock_llm_responses=True
    )

def test_project_scoping(homeowner_harness):
    response = homeowner_harness.run(
        "I need to fix my leaking roof"
    )
    
    assert "roof" in response.lower()
    assert homeowner_harness.tool_called("save_project")
```

### Integration Testing

```python
@pytest.mark.integration
async def test_full_project_flow():
    # Test complete flow from project creation to bid card
    agent_factory = AgentFactory()
    
    # 1. Create project
    homeowner = agent_factory.get_agent("homeowner")
    project = await homeowner.create_project(test_data)
    
    # 2. Generate bid card
    bidcard = agent_factory.get_agent("bidcard")
    card = await bidcard.generate(project.id)
    
    assert card.status == "final"
    assert card.confidence >= 0.7
```

## 🛡️ Error Handling

### Graceful Degradation

```python
class ResilientAgent(LiveAgent):
    async def handle_tool_error(self, error: Exception, tool_name: str):
        """Gracefully handle tool failures."""
        if isinstance(error, RateLimitError):
            await self.notify_user(
                "I'm experiencing high demand. Let me try another approach..."
            )
            return self.fallback_tool(tool_name)
        
        elif isinstance(error, NetworkError):
            return {
                "status": "error",
                "message": "Connection issue. Please try again.",
                "retry_after": 5
            }
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def reliable_api_call(agent: LiveAgent, prompt: str):
    """Retry API calls with exponential backoff."""
    return await agent.generate(prompt)
```

## 📊 Monitoring & Observability

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

class MonitoredAgent(LiveAgent):
    async def on_tool_call(self, tool_name: str, args: dict):
        logger.info(
            "tool_called",
            agent=self.name,
            tool=tool_name,
            args_keys=list(args.keys()),
            user_id=self.context.user_id
        )
```

### Performance Tracking

```python
from functools import wraps
import time

def track_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            
            logger.info(
                "operation_complete",
                operation=func.__name__,
                duration_seconds=duration,
                success=True
            )
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(
                "operation_failed",
                operation=func.__name__,
                duration_seconds=duration,
                error=str(e)
            )
            raise
    return wrapper
```

## 🔐 Security Considerations

### Input Validation

```python
from pydantic import BaseModel, validator

class ProjectInput(BaseModel):
    title: str
    description: str
    budget_min: float
    budget_max: float
    
    @validator('title')
    def title_length(cls, v):
        if len(v) < 3 or len(v) > 200:
            raise ValueError('Title must be 3-200 characters')
        return v
    
    @validator('budget_max')
    def budget_range(cls, v, values):
        if 'budget_min' in values and v < values['budget_min']:
            raise ValueError('Max budget must be >= min budget')
        return v
```

### Safe Tool Execution

```python
def safe_file_operation(tool_context: ToolContext, file_path: str) -> dict:
    """Safely handle file operations with validation."""
    # Validate path is within allowed directories
    allowed_dirs = ['/tmp/instabids', '/var/instabids/uploads']
    
    if not any(file_path.startswith(d) for d in allowed_dirs):
        return {
            "status": "error",
            "message": "Access denied: Invalid file path"
        }
    
    # Additional safety checks...
```

## 🎯 Summary

1. **Use plain Python agents** inheriting from ADK base classes
2. **Register agents** in `.adk/components.json`
3. **Prefix state keys** with `user:`, `app:`, or `temp:`
4. **Write comprehensive docstrings** for all tools
5. **Handle errors gracefully** with fallbacks
6. **Monitor performance** with structured logging
7. **Validate all inputs** using Pydantic models
8. **Test thoroughly** with harnesses and integration tests

Follow these patterns to build robust, scalable AI agents for InstaBids!