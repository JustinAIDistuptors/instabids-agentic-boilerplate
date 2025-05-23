## Task Prompt: Generate Comprehensive Tests

### Goal

Create thorough test coverage for agents, tools, and integrations following pytest best practices.

### Test Structure

```
tests/
├── agents/
│   ├── test_homeowner.py
│   ├── test_bidcard.py
│   └── test_contractor.py
├── tools/
│   ├── test_supabase_tools.py
│   ├── test_vision_tools.py
│   └── test_notification_tools.py
├── integration/
│   ├── test_project_flow.py
│   └── test_agent_communication.py
├── fixtures/
│   ├── agent_fixtures.py
│   └── db_fixtures.py
└── conftest.py
```

### Agent Test Template

```python
# tests/agents/test_{agent_name}.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from google.adk.testing import AgentTestHarness

from instabids.agents.{agent_name} import agent


class Test{AgentClass}:
    """Test suite for {AgentClass}."""
    
    @pytest.fixture
    def harness(self):
        """Provide test harness for agent."""
        return AgentTestHarness(
            agent=agent,
            mock_llm_responses=True
        )
    
    @pytest.fixture
    def mock_context(self):
        """Mock tool context."""
        context = Mock()
        context.state = {}
        context.session_id = "test-session-123"
        context.user_id = "test-user-456"
        return context
    
    def test_agent_initialization(self, harness):
        """Test agent initializes with correct configuration."""
        assert harness.agent.name == "{agent_name}"
        assert harness.agent.model == "gemini-2.0-flash-exp"
        assert len(harness.agent.tools) > 0
    
    def test_required_tools_present(self, harness):
        """Test all required tools are configured."""
        tool_names = [t.__name__ for t in harness.agent.tools]
        
        required_tools = [
            "save_project",
            "get_preferences",
            "analyze_image"
        ]
        
        for tool in required_tools:
            assert tool in tool_names, f"Missing required tool: {tool}"
    
    @pytest.mark.asyncio
    async def test_conversation_flow(self, harness):
        """Test basic conversation flow."""
        # Configure mock responses
        harness.set_llm_response(
            "Hello! I'd like to help you with your home improvement project."
        )
        
        # Start conversation
        response = await harness.run("I need to fix my roof")
        
        assert "roof" in response.lower()
        assert harness.conversation_turns == 1
    
    @pytest.mark.asyncio
    async def test_tool_invocation(self, harness, mock_context):
        """Test agent correctly invokes tools."""
        with patch('instabids.tools.supabase_tools.save_project') as mock_save:
            mock_save.return_value = {
                "status": "success",
                "project_id": "proj-123"
            }
            
            harness.set_llm_response(
                "I'll save your project now.",
                tool_calls=[{"name": "save_project", "args": {}}]
            )
            
            response = await harness.run("Save my project")
            
            assert mock_save.called
            assert "save" in response.lower()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, harness):
        """Test agent handles errors gracefully."""
        # Simulate tool failure
        with patch('instabids.tools.supabase_tools.save_project') as mock_save:
            mock_save.side_effect = Exception("Database error")
            
            response = await harness.run("Save my project")
            
            assert "error" in response.lower() or "problem" in response.lower()
            assert harness.agent_state.get("error_count", 0) > 0
```

### Tool Test Template

```python
# tests/tools/test_{tool_category}_tools.py
import pytest
from unittest.mock import Mock, patch
from instabids.tools.{tool_category}_tools import {tool_name}


class Test{ToolName}:
    """Test suite for {tool_name} tool."""
    
    @pytest.fixture
    def tool_context(self):
        """Mock tool context."""
        context = Mock()
        context.state = {
            "user:id": "test-user-123",
            "app:environment": "test"
        }
        return context
    
    def test_success_case(self, tool_context):
        """Test successful tool execution."""
        result = {tool_name}(
            tool_context,
            param1="valid_value",
            param2=42
        )
        
        assert result["status"] == "success"
        assert "data" in result
        assert result["data"] is not None
    
    def test_input_validation(self, tool_context):
        """Test input validation."""
        # Test missing required parameter
        result = {tool_name}(
            tool_context,
            param1="",  # Invalid empty string
            param2=42
        )
        
        assert result["status"] == "error"
        assert "required" in result["message"].lower()
    
    def test_type_validation(self, tool_context):
        """Test parameter type validation."""
        result = {tool_name}(
            tool_context,
            param1="valid",
            param2="not_a_number"  # Should be int
        )
        
        assert result["status"] == "error"
        assert "type" in result["message"].lower()
    
    @patch('instabids.db.client.SupabaseClient.get_client')
    def test_database_error(self, mock_client, tool_context):
        """Test database error handling."""
        mock_client.side_effect = Exception("Connection failed")
        
        result = {tool_name}(tool_context, param1="value", param2=42)
        
        assert result["status"] == "error"
        assert "database" in result["message"].lower()
    
    def test_state_updates(self, tool_context):
        """Test tool updates context state correctly."""
        initial_state = tool_context.state.copy()
        
        result = {tool_name}(
            tool_context,
            param1="value",
            param2=42
        )
        
        # Check expected state changes
        assert tool_context.state["app:last_tool_call"] == "{tool_name}"
        assert len(tool_context.state) > len(initial_state)
```

### Integration Test Template

```python
# tests/integration/test_project_flow.py
import pytest
from instabids.agents import AgentFactory
from instabids.db.client import SupabaseClient


@pytest.mark.integration
class TestProjectCreationFlow:
    """Test complete project creation flow."""
    
    @pytest.fixture
    async def clean_db(self):
        """Ensure clean database state."""
        client = SupabaseClient.get_client()
        # Clean test data
        yield
        # Cleanup after test
    
    async def test_full_project_flow(self, clean_db):
        """Test creating project from conversation to bid card."""
        factory = AgentFactory()
        
        # Step 1: Homeowner creates project
        homeowner = factory.get_agent("homeowner")
        project_data = await homeowner.process(
            "I need to repair my leaking roof. Budget is around $5000."
        )
        
        assert project_data["status"] == "success"
        assert "project_id" in project_data
        
        # Step 2: Bid card generation
        bidcard_agent = factory.get_agent("bidcard")
        bid_card = await bidcard_agent.generate(
            project_id=project_data["project_id"]
        )
        
        assert bid_card["category"] == "repair"
        assert bid_card["confidence"] >= 0.7
        
        # Step 3: Verify in database
        client = SupabaseClient.get_client()
        
        # Check project exists
        project = client.table('projects').select('*').eq(
            'id', project_data["project_id"]
        ).single().execute()
        
        assert project.data is not None
        assert project.data["title"] is not None
        
        # Check bid card exists
        bid_card_db = client.table('bid_cards').select('*').eq(
            'project_id', project_data["project_id"]
        ).single().execute()
        
        assert bid_card_db.data is not None
        assert bid_card_db.data["status"] == "final"
```

### Fixture Templates

```python
# tests/fixtures/agent_fixtures.py
import pytest
from typing import Dict, Any


@pytest.fixture
def mock_llm_response():
    """Mock LLM responses for testing."""
    responses = {
        "greeting": "Hello! How can I help you today?",
        "project_query": "I understand you need help with {project_type}.",
        "confirmation": "I've saved your project successfully."
    }
    return responses


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "title": "Roof Repair Project",
        "description": "Fix leaking roof in master bedroom",
        "budget_min": 3000,
        "budget_max": 5000,
        "timeline": "2 weeks",
        "location": "Seattle, WA"
    }
```

### Testing Best Practices

1. **Use fixtures for reusable test data**
2. **Mock external dependencies**
3. **Test both success and failure paths**
4. **Use descriptive test names**
5. **Group related tests in classes**
6. **Mark integration tests appropriately**
7. **Clean up test data after runs**

### Coverage Requirements

- Minimum 80% code coverage
- 100% coverage for critical paths
- All error cases tested
- All tool parameters validated

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

# Run tests in parallel
poetry run pytest -n auto
```

### Validation Checklist

- [ ] All public methods have tests
- [ ] Error cases are tested
- [ ] Mocks are used for external services
- [ ] Tests are independent
- [ ] No hardcoded test data
- [ ] Cleanup is performed
- [ ] Tests run in < 30 seconds