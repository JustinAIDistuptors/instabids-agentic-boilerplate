"""
PromptSelectorAgent - Meta-agent for selecting appropriate prompts
Critical for 100% AI-driven development workflows
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from google import genai
from google.adk.agents import LlmAgent
from google.adk.types import ToolContext
import json
import yaml


def list_available_prompts(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Lists all available prompts in the .prompts directory.
    
    This tool scans the prompt repository and returns categorized prompts
    that can be used by other agents.
    
    Args:
        tool_context (ToolContext): ADK tool context providing session state access.
    
    Returns:
        dict: Available prompts organized by category.
              Example: {
                  "status": "success",
                  "prompts": {
                      "system": ["master_code_builder.md", "adk_specialist.md"],
                      "tasks": ["create_llm_agent.md", "debug_supabase.md"],
                      "conventions": ["docstring_style.md"],
                      "meta": ["choose_prompt.md"]
                  }
              }
    """
    try:
        prompts_dir = Path(__file__).parent.parent.parent.parent / ".prompts"
        
        if not prompts_dir.exists():
            return {"status": "error", "message": ".prompts directory not found"}
        
        prompts = {}
        for category_dir in prompts_dir.iterdir():
            if category_dir.is_dir():
                category = category_dir.name
                prompts[category] = [
                    f.name for f in category_dir.glob("*.md")
                ]
        
        # Cache in session state
        tool_context.state["temp:available_prompts"] = prompts
        
        return {"status": "success", "prompts": prompts}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


def retrieve_prompt_content(
    tool_context: ToolContext,
    category: str,
    filename: str
) -> Dict[str, Any]:
    """
    Retrieves the content of a specific prompt file.
    
    Args:
        tool_context (ToolContext): ADK tool context providing session state access.
        category (str): Prompt category (system, tasks, conventions, meta).
        filename (str): Name of the prompt file to retrieve.
    
    Returns:
        dict: Prompt content and metadata.
              Example: {
                  "status": "success",
                  "content": "Full prompt content...",
                  "metadata": {"category": "tasks", "filename": "create_llm_agent.md"}
              }
    """
    try:
        prompts_dir = Path(__file__).parent.parent.parent.parent / ".prompts"
        prompt_path = prompts_dir / category / filename
        
        if not prompt_path.exists():
            return {"status": "error", "message": f"Prompt not found: {category}/{filename}"}
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "status": "success",
            "content": content,
            "metadata": {
                "category": category,
                "filename": filename,
                "path": str(prompt_path.relative_to(prompts_dir))
            }
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


def compose_agent_prompt(
    tool_context: ToolContext,
    task_description: str,
    agent_role: Optional[str] = None,
    include_conventions: bool = True
) -> Dict[str, Any]:
    """
    Composes a complete prompt for an AI coding agent based on task requirements.
    
    This tool intelligently selects and combines prompts from different categories
    to create a comprehensive instruction set for specialized agents.
    
    Args:
        tool_context (ToolContext): ADK tool context providing session state access.
        task_description (str): Description of the task to be performed.
        agent_role (str, optional): Specific agent role if predetermined.
        include_conventions (bool): Whether to include coding conventions.
    
    Returns:
        dict: Composed prompt ready for agent use.
              Example: {
                  "status": "success",
                  "composed_prompt": "Full composed prompt...",
                  "components_used": ["system/master_code_builder.md", "tasks/create_llm_agent.md"],
                  "context_files": ["docs/ADK_BEST_PRACTICES.md", "docs/COMMON_PITFALLS.md"]
              }
    """
    # This is a simplified implementation
    # In production, this would use more sophisticated prompt selection logic
    
    components = []
    
    # Select base system prompt
    if agent_role:
        system_prompt = f"system/{agent_role}.md"
    else:
        system_prompt = "system/master_code_builder.md"
    components.append(system_prompt)
    
    # Add relevant task prompt based on keywords
    task_keywords = {
        "create agent": "tasks/create_llm_agent.md",
        "debug": "tasks/debug_supabase.md",
        "tool": "tasks/extend_tool.md",
        "test": "tasks/generate_tests.md"
    }
    
    for keyword, prompt_file in task_keywords.items():
        if keyword in task_description.lower():
            components.append(prompt_file)
            break
    
    # Add conventions if requested
    if include_conventions:
        components.extend([
            "conventions/docstring_style.md",
            "conventions/git_commit_style.md"
        ])
    
    # Store composition in session state
    tool_context.state["temp:last_prompt_composition"] = {
        "task": task_description,
        "components": components
    }
    
    return {
        "status": "success",
        "components_used": components,
        "context_files": [
            "docs/ADK_BEST_PRACTICES.md",
            "docs/COMMON_PITFALLS.md"
        ],
        "composed_prompt": f"Composed prompt using: {', '.join(components)}"
    }


class PromptSelectorAgent(LlmAgent):
    """
    Meta-agent responsible for selecting and composing prompts for other AI agents.
    This enables the 100% AI-driven development workflow by providing context-aware
    instruction selection.
    """
    
    def __init__(self):
        super().__init__(
            name="prompt_selector",
            model="gemini-2.0-flash-exp",
            description="Selects and composes appropriate prompts for AI coding agents",
            instructions="""You are a meta-agent responsible for prompt engineering.
            Your role is to:
            1. Analyze incoming task requirements
            2. Select appropriate system prompts for agent roles
            3. Choose relevant task-specific prompts
            4. Include necessary conventions and guidelines
            5. Compose comprehensive instructions for other agents
            
            You have access to:
            - System prompts defining agent roles
            - Task prompts for specific operations
            - Convention documents for consistency
            - Meta prompts for self-reflection
            
            Always ensure selected prompts are appropriate for the task and include
            references to relevant documentation files.""",
            tools=[
                list_available_prompts,
                retrieve_prompt_content,
                compose_agent_prompt
            ],
            output_key="composed_prompt"
        )


# Export the agent instance
agent = PromptSelectorAgent()
