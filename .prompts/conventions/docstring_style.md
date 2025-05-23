## Convention: ADK Tool Docstring Format

### Purpose

All Python functions intended for use as ADK FunctionTools MUST have comprehensive docstrings. The LLM relies critically on these for understanding and correct usage.

### Required Sections

Every tool docstring MUST include:

1. **Brief summary** (1-2 lines)
2. **Detailed description** (if needed)
3. **Args section** with types and descriptions
4. **Returns section** with type and structure
5. **Raises section** (if applicable)
6. **Examples section** (recommended)

### Standard Format

```python
def tool_name(
    tool_context: ToolContext,
    required_param: str,
    optional_param: Optional[int] = None
) -> Dict[str, Any]:
    """
    Brief one-line summary of what the tool does.
    
    More detailed description if needed. Explain when and why
    to use this tool, any important considerations, and how
    it fits into the larger system.
    
    Args:
        tool_context (ToolContext): The ADK tool context providing
            access to session state and other context. Always first.
        required_param (str): Description of this parameter. Be specific
            about format, constraints, and valid values.
        optional_param (Optional[int]): Description of optional parameter.
            Explain default behavior when None. Defaults to None.
    
    Returns:
        dict: Operation result with standardized structure:
            {
                "status": "success" or "error",
                "message": "Human-readable message",
                "data": {... actual result data ...},
                "metadata": {... optional metadata ...}
            }
    
    Raises:
        ValueError: If required_param is empty or invalid format.
        ConnectionError: If database connection fails.
        PermissionError: If user lacks required permissions.
    
    Examples:
        >>> result = tool_name(
        ...     tool_context,
        ...     required_param="example_value",
        ...     optional_param=42
        ... )
        >>> print(result["status"])
        "success"
    
    Note:
        This tool requires database write permissions and
        may modify user preferences.
    """
```

### Specific Guidelines

#### 1. Parameter Descriptions

```python
# ❌ Bad - Too vague
Args:
    data (dict): The data to process.
    
# ✅ Good - Specific and helpful
Args:
    data (dict): Project information containing:
        - title (str): Project title, 3-200 characters
        - description (str): Detailed description
        - budget_min (float): Minimum budget in USD
        - budget_max (float): Maximum budget in USD
```

#### 2. Return Value Documentation

```python
# ❌ Bad - Unclear structure
Returns:
    dict: The result.
    
# ✅ Good - Clear structure
Returns:
    dict: Operation result containing:
        - status (str): "success" or "error"
        - project_id (str): UUID of created project (on success)
        - message (str): Human-readable status message
        - error_code (str): Specific error code (on error)
```

#### 3. Complex Parameter Types

```python
def process_items(
    tool_context: ToolContext,
    items: List[Dict[str, Any]],
    options: Optional[ProcessOptions] = None
) -> Dict[str, Any]:
    """
    Process multiple items with configurable options.
    
    Args:
        tool_context (ToolContext): ADK context.
        items (List[Dict[str, Any]]): List of items where each item
            must contain:
            - id (str): Unique identifier
            - type (str): One of "project", "bid", "message"
            - data (dict): Type-specific data
        options (Optional[ProcessOptions]): Processing configuration:
            - batch_size (int): Items per batch (default: 10)
            - retry_failed (bool): Retry on failure (default: True)
            - timeout_seconds (int): Max time per item (default: 30)
    """
```

### Special Cases

#### 1. State-Modifying Tools

```python
def update_preferences(
    tool_context: ToolContext,
    preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update user preferences in both context state and database.
    
    This tool modifies:
    - tool_context.state["user:preferences"]
    - Database table `user_preferences`
    
    Args:
        tool_context (ToolContext): ADK context with user state.
        preferences (dict): Key-value pairs of preferences to update.
            Keys should be lowercase, underscored strings.
            Values can be strings, numbers, or booleans.
    """
```

#### 2. Async Tools

```python
async def fetch_external_data(
    tool_context: ToolContext,
    source_url: str,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Asynchronously fetch data from external source.
    
    This is an async tool that should be awaited. It performs
    non-blocking HTTP requests with automatic retry logic.
    
    Args:
        tool_context (ToolContext): ADK context.
        source_url (str): Full URL to fetch data from.
            Must start with https://.
        timeout (int): Request timeout in seconds. Defaults to 30.
    """
```

### Validation Rules

1. **Minimum Length**: At least 5 lines (excluding blank lines)
2. **First Parameter**: Must be `tool_context: ToolContext`
3. **All Parameters Documented**: Every parameter in Args section
4. **Return Structure Clear**: Explicit dict structure or reference
5. **Error Cases Mentioned**: Either in Raises or description

### Examples by Tool Type

#### Database Tool

```python
def get_project_by_id(
    tool_context: ToolContext,
    project_id: str,
    include_messages: bool = False
) -> Dict[str, Any]:
    """
    Retrieve project details from database by ID.
    
    Fetches project information and optionally includes
    associated messages. Uses RLS to ensure user can
    only access their own projects.
    
    Args:
        tool_context (ToolContext): ADK context containing user ID.
        project_id (str): UUID of the project to retrieve.
        include_messages (bool): Whether to include message history.
            Defaults to False.
    
    Returns:
        dict: Project information:
            {
                "status": "success",
                "project": {
                    "id": "uuid",
                    "title": "Project Title",
                    "description": "...",
                    "created_at": "2025-05-23T10:00:00Z",
                    "messages": [...] if include_messages=True
                }
            }
    
    Raises:
        ValueError: If project_id is not valid UUID format.
        PermissionError: If user doesn't own the project.
        LookupError: If project doesn't exist.
    """
```

#### Analytics Tool

```python
def calculate_project_stats(
    tool_context: ToolContext,
    time_range: str = "30d",
    group_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate statistics for user's projects.
    
    Aggregates project data over specified time range with
    optional grouping. Useful for dashboards and reports.
    
    Args:
        tool_context (ToolContext): ADK context with user ID.
        time_range (str): Time range for stats. Options:
            - "24h": Last 24 hours
            - "7d": Last 7 days  
            - "30d": Last 30 days (default)
            - "all": All time
        group_by (Optional[str]): Grouping field:
            - "category": Group by project category
            - "status": Group by project status
            - "week": Group by week
            - None: No grouping (default)
    
    Returns:
        dict: Statistical summary:
            {
                "status": "success",
                "stats": {
                    "total_projects": 42,
                    "average_budget": 5000.00,
                    "completion_rate": 0.75,
                    "by_category": {...} if grouped
                },
                "time_range": "30d",
                "generated_at": "2025-05-23T10:00:00Z"
            }
    """
```

### Quality Checklist

- [ ] Summary explains the "what"
- [ ] Description explains the "why" and "when"
- [ ] All parameters documented with types
- [ ] Return structure is explicit
- [ ] Error cases are covered
- [ ] Examples provided for complex tools
- [ ] Special behaviors noted
- [ ] No typos or grammar errors