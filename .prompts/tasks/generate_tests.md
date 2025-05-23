## Task: Generate Comprehensive Tests

### Goal

Create thorough test coverage for agents, tools, and integrations in the InstaBids project.

### Test Structure

```
tests/
├── agents/
│   ├── test_homeowner.py
│   ├── test_bidcard.py
│   └── test_recruiter.py
├── tools/
│   ├── test_supabase_tools.py
│   ├── test_vision_tools.py
│   └── test_notification_tools.py
├── integration/
│   ├── test_project_flow.py
│   ├── test_bidding_flow.py
│   └── test_supabase_integration.py
├── e2e/
│   └── test_full_workflow.py
├── fixtures/
│   ├── agent_fixtures.py
│   └── data_fixtures.py
└── conftest.py
```

### Agent Test Template

```python
# tests/agents/test_{agent_name}.py
import pytest
from unittest.mock import Mock, patch
from google.adk.testing import AgentTestHarness
from instabids.agents.{agent_name} import agent

@pytest.fixture
def test_harness():
    """Create test harness for agent."""
    return AgentTestHarness(
        agent=agent,
        mock_llm_responses=True
    )

@pytest.fixture
def mock_tool_context():
    """Mock tool context with state."""
    context = Mock()
    context.state = {
        "user:id": "test-user-123",
        "user:preferences": {},
        "app:test_mode": True
    }
    return context

class Test{AgentName}:
    """Test suite for {AgentName}."""
    
    def test_initialization(self):
        """Test agent initializes correctly."""
        assert agent.name == "{agent_name}"
        assert agent.model == "gemini-2.0-flash-exp"
        assert len(agent.tools) > 0
    
    def test_instructions_loaded(self):
        """Test instructions are properly loaded."""
        assert agent.instructions is not None
        assert len(agent.instructions) > 100
        assert "{key_phrase}" in agent.instructions
    
    @pytest.mark.parametrize("input_text,expected_tool", [
        ("I need to fix my roof", "save_project"),
        ("Show me previous projects", "get_projects"),
        ("Upload a photo", "analyze_image"),
    ])
    def test_tool_selection(self, test_harness, input_text, expected_tool):
        """Test agent selects appropriate tools."""
        test_harness.set_mock_response(f"I'll use {expected_tool}")
        response = test_harness.run(input_text)
        
        assert test_harness.tool_called(expected_tool)
    
    def test_state_management(self, test_harness, mock_tool_context):
        """Test agent manages state correctly."""
        test_harness.set_tool_context(mock_tool_context)
        test_harness.run("Create a new project")
        
        # Verify state updates
        assert "user:current_project" in mock_tool_context.state
        assert "app:last_interaction" in mock_tool_context.state
    
    @pytest.mark.integration
    async def test_conversation_flow(self, test_harness):
        """Test multi-turn conversation."""
        conversation = [
            ("I need help with my kitchen", "kitchen project"),
            ("Budget is $10,000", "budget recorded"),
            ("Timeline is 2 weeks", "timeline noted"),
        ]
        
        for user_input, expected_phrase in conversation:
            response = await test_harness.run_async(user_input)
            assert expected_phrase.lower() in response.lower()
    
    def test_error_handling(self, test_harness):
        """Test agent handles errors gracefully."""
        test_harness.mock_tool_error("save_project", Exception("DB error"))
        
        response = test_harness.run("Save my project")
        assert "error" in response.lower() or "problem" in response.lower()
        assert "try again" in response.lower()
```

### Tool Test Template

```python
# tests/tools/test_{category}_tools.py
import pytest
from unittest.mock import Mock, patch
from instabids.tools.{category}_tools import {
    tool_function_1,
    tool_function_2
}

@pytest.fixture
def mock_context():
    """Create mock tool context."""
    context = Mock()
    context.state = {"user:id": "test-123"}
    return context

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    with patch('instabids.tools.{category}_tools.SupabaseClient') as mock:
        client = Mock()
        mock.get_client.return_value = client
        yield client

class Test{Category}Tools:
    """Test suite for {category} tools."""
    
    def test_tool_success_case(
        self, mock_context, mock_supabase_client
    ):
        """Test successful tool execution."""
        # Setup mock response
        mock_supabase_client.table().insert().execute.return_value = Mock(
            data=[{"id": "123", "status": "created"}]
        )
        
        result = tool_function_1(
            mock_context,
            param1="value1",
            param2="value2"
        )
        
        assert result["status"] == "success"
        assert "id" in result
        assert mock_supabase_client.table.called
    
    def test_tool_validation(
        self, mock_context
    ):
        """Test input validation."""
        result = tool_function_1(
            mock_context,
            param1="",  # Invalid empty string
            param2="valid"
        )
        
        assert result["status"] == "error"
        assert "Invalid input" in result["message"]
    
    def test_tool_error_handling(
        self, mock_context, mock_supabase_client
    ):
        """Test error handling."""
        mock_supabase_client.table().insert().execute.side_effect = \
            Exception("Database error")
        
        result = tool_function_1(
            mock_context,
            param1="value1",
            param2="value2"
        )
        
        assert result["status"] == "error"
        assert "Database error" in result["message"]
    
    @pytest.mark.parametrize("state_key,expected_behavior", [
        ("user:preferences", "use_existing"),
        (None, "create_new"),
    ])
    def test_state_interaction(
        self, mock_context, state_key, expected_behavior
    ):
        """Test tool state management."""
        if state_key:
            mock_context.state[state_key] = {"test": "data"}
        
        result = tool_function_2(mock_context)
        
        # Verify behavior based on state
        assert result["behavior"] == expected_behavior
```

### Integration Test Template

```python
# tests/integration/test_project_flow.py
import pytest
from instabids.agents import HomeownerAgent, BidCardAgent
from instabids.db import test_db

@pytest.mark.integration
class TestProjectFlow:
    """Integration tests for project creation flow."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self, test_db):
        """Setup and cleanup for each test."""
        test_db.reset()
        yield
        test_db.cleanup()
    
    async def test_complete_project_creation(self, test_db):
        """Test full project creation workflow."""
        # Initialize agents
        homeowner = HomeownerAgent()
        bidcard = BidCardAgent()
        
        # Simulate user interaction
        project_data = await homeowner.create_project({
            "user_id": "test-user",
            "description": "Kitchen renovation",
            "images": ["test.jpg"]
        })
        
        assert project_data["status"] == "success"
        assert "project_id" in project_data
        
        # Generate bid card
        bid_card = await bidcard.generate(
            project_id=project_data["project_id"]
        )
        
        assert bid_card["status"] == "final"
        assert bid_card["confidence"] >= 0.7
        
        # Verify in database
        project = test_db.get_project(project_data["project_id"])
        assert project is not None
        assert project["bid_cards"][0]["id"] == bid_card["id"]
```

### Test Utilities

```python
# tests/fixtures/agent_fixtures.py
import pytest
from typing import Dict, Any

class MockLLMResponse:
    """Mock LLM responses for testing."""
    
    responses = {
        "project_creation": "I'll help you create a project...",
        "preference_recall": "I remember you prefer a budget of...",
        "error_handling": "I encountered an issue but let me try..."
    }
    
    @classmethod
    def get_response(cls, scenario: str) -> str:
        return cls.responses.get(scenario, "Generic response")

@pytest.fixture
def mock_llm_responses():
    """Provide mock LLM responses."""
    return MockLLMResponse()
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=instabids --cov-report=html

# Run specific test file
poetry run pytest tests/agents/test_homeowner.py

# Run only integration tests
poetry run pytest -m integration

# Run with verbose output
poetry run pytest -v

# Run and stop on first failure
poetry run pytest -x
```

### Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: Critical paths covered
- **E2E Tests**: Happy path + key edge cases
- **Performance Tests**: Response time benchmarks
- **Security Tests**: Input validation, RLS checks