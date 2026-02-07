# src/cli/utils/prompts.py
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from typing import List, Optional, Dict
from src.core.command import Parameter
from .models import CommandDetails, ExampleDetails
from .constants import (
    MSG_AVAILABLE_TOOLS, MSG_COMMAND_DETAILS, MSG_CONFIGURE_PARAM,
    MSG_TAGS, MSG_COMMAND_EXAMPLE, MSG_REVIEW_COMMAND,
    PROMPT_SELECT_TOOL, PROMPT_COMMAND_NAME, PROMPT_COMMAND_ID,
    PROMPT_COMMAND_TEMPLATE, PROMPT_EXPLANATION, PROMPT_PARAM_DESC,
    PROMPT_PARAM_REQUIRED, PROMPT_PARAM_DEFAULT, PROMPT_TAGS_INPUT,
    PROMPT_EXAMPLE_INPUT, PROMPT_EXAMPLE_OUTPUT, PROMPT_EXAMPLE_DESC,
    PROMPT_ADD_EXAMPLE, PROMPT_SAVE_COMMAND, REVIEW_PANEL_TEMPLATE,
    PANEL_TITLE_SUMMARY, TAG_SUGGESTIONS_PREFIX, TAG_SEPARATOR
)


console = Console()


class InteractivePrompts:
    """User-friendly interactive prompts with Rich formatting"""
    
    @staticmethod
    def select_tool(tools: List[Dict]) -> str:
        """Interactive tool selection with category grouping"""
        # Group tools by category
        by_category = {}
        for tool in tools:
            cat = tool['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tool)
        
        # Display grouped list
        console.print(MSG_AVAILABLE_TOOLS)
        for category, cat_tools in sorted(by_category.items()):
            console.print(f"\n[yellow]{category}[/yellow]")
            for tool in cat_tools:
                console.print(f"  • {tool['name']:<15} - {tool['description']}")
        
        # Prompt for selection
        tool_name = Prompt.ask(PROMPT_SELECT_TOOL)
        return tool_name
    
    @staticmethod
    def input_command_details() -> CommandDetails:
        """Prompt for basic command details"""
        console.print(MSG_COMMAND_DETAILS)
        
        name = Prompt.ask(PROMPT_COMMAND_NAME)
        
        # Auto-generate ID from name
        suggested_id = name.lower().replace(' ', '-').replace('_', '-')
        command_id = Prompt.ask(PROMPT_COMMAND_ID, default=suggested_id)
        
        command = Prompt.ask(PROMPT_COMMAND_TEMPLATE)
        explanation = Prompt.ask(PROMPT_EXPLANATION)
        
        return CommandDetails(
            id=command_id,
            name=name,
            command=command,
            explanation=explanation
        )
    
    @staticmethod
    def configure_parameter(param_name: str) -> Parameter:
        """Interactive parameter configuration"""
        console.print(MSG_CONFIGURE_PARAM.format(param_name))
        
        description = Prompt.ask(PROMPT_PARAM_DESC)
        required = Confirm.ask(PROMPT_PARAM_REQUIRED, default=True)
        default = None
        
        if not required:
            default = Prompt.ask(PROMPT_PARAM_DEFAULT, default="")
            default = default if default else None
        
        return Parameter(
            name=param_name,
            description=description,
            required=required,
            default=default
        )
    
    @staticmethod
    def input_tags(suggestions: List[str] = None) -> List[str]:
        """Prompt for tags with suggestions"""
        console.print(MSG_TAGS)
        
        if suggestions:
            console.print(f"{TAG_SUGGESTIONS_PREFIX}{TAG_SEPARATOR.join(suggestions)}")
        
        tags_input = Prompt.ask(PROMPT_TAGS_INPUT, default="")
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        return tags
    
    @staticmethod
    def add_example() -> Optional[ExampleDetails]:
        """Prompt to add an example"""
        if not Confirm.ask(PROMPT_ADD_EXAMPLE, default=False):
            return None
        
        console.print(MSG_COMMAND_EXAMPLE)
        
        example_input = Prompt.ask(PROMPT_EXAMPLE_INPUT)
        
        console.print(PROMPT_EXAMPLE_OUTPUT)
        output_lines = []
        empty_count = 0
        while True:
            try:
                line = console.input("  ")
                if line == "":
                    empty_count += 1
                    if empty_count >= 1:  # Single empty line ends input
                        break
                else:
                    empty_count = 0
                output_lines.append(line)
            except EOFError:
                break
        
        output = "\n".join(output_lines)
        
        description = Prompt.ask(PROMPT_EXAMPLE_DESC, default="")
        
        return ExampleDetails(
            input=example_input,
            output=output,
            description=description if description else None
        )
    
    @staticmethod
    def review_and_confirm(command_data: Dict) -> bool:
        """Display command summary and ask for confirmation"""
        console.print(MSG_REVIEW_COMMAND)
        
        panel_content = REVIEW_PANEL_TEMPLATE.format(
            tool=command_data.get('tool', 'N/A'),
            id=command_data['id'],
            name=command_data['name'],
            command=command_data['command'],
            explanation=command_data['explanation'],
            param_count=len(command_data.get('parameters', [])),
            example_count=len(command_data.get('examples', [])),
            tags=TAG_SEPARATOR.join(command_data.get('tags', []))
        )
        
        console.print(Panel(panel_content, title=PANEL_TITLE_SUMMARY))
        
        return Confirm.ask(PROMPT_SAVE_COMMAND, default=True)
