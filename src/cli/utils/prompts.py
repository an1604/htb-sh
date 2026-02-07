# src/cli/utils/prompts.py
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from typing import List, Optional, Dict
from src.core.command import Parameter, Example


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
        console.print("\n[bold cyan]Available Tools:[/bold cyan]")
        for category, cat_tools in sorted(by_category.items()):
            console.print(f"\n[yellow]{category}[/yellow]")
            for tool in cat_tools:
                console.print(f"  • {tool['name']:<15} - {tool['description']}")
        
        # Prompt for selection
        tool_name = Prompt.ask("\n[bold]Select tool[/bold]")
        return tool_name
    
    @staticmethod
    def input_command_details() -> Dict:
        """Prompt for basic command details"""
        console.print("\n[bold cyan]Command Details[/bold cyan]")
        
        name = Prompt.ask("Command Name")
        
        # Auto-generate ID from name
        suggested_id = name.lower().replace(' ', '-').replace('_', '-')
        command_id = Prompt.ask("Command ID", default=suggested_id)
        
        command = Prompt.ask("Command Template (use {param} for variables)")
        explanation = Prompt.ask("Explanation")
        
        return {
            'id': command_id,
            'name': name,
            'command': command,
            'explanation': explanation
        }
    
    @staticmethod
    def configure_parameter(param_name: str) -> Parameter:
        """Interactive parameter configuration"""
        console.print(f"\n[bold cyan]Configure Parameter: {param_name}[/bold cyan]")
        
        description = Prompt.ask("  Description")
        required = Confirm.ask("  Required?", default=True)
        default = None
        
        if not required:
            default = Prompt.ask("  Default value (optional)", default="")
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
        console.print("\n[bold cyan]Tags[/bold cyan]")
        
        if suggestions:
            console.print(f"  Suggestions: {', '.join(suggestions)}")
        
        tags_input = Prompt.ask("Tags (comma-separated)", default="")
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        return tags
    
    @staticmethod
    def add_example() -> Optional[Dict]:
        """Prompt to add an example"""
        if not Confirm.ask("\n[bold]Add an example?[/bold]", default=False):
            return None
        
        console.print("\n[bold cyan]Command Example[/bold cyan]")
        
        example_input = Prompt.ask("  Example Input")
        
        console.print("  Example Output (paste, then press Enter on empty line):")
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
        
        description = Prompt.ask("  Example Description (optional)", default="")
        
        return {
            'input': example_input,
            'output': output,
            'description': description if description else None
        }
    
    @staticmethod
    def review_and_confirm(command_data: Dict) -> bool:
        """Display command summary and ask for confirmation"""
        console.print("\n[bold cyan]Review Command[/bold cyan]")
        
        panel_content = f"""[yellow]Tool:[/yellow] {command_data.get('tool', 'N/A')}
[yellow]ID:[/yellow] {command_data['id']}
[yellow]Name:[/yellow] {command_data['name']}
[yellow]Command:[/yellow] {command_data['command']}
[yellow]Explanation:[/yellow] {command_data['explanation']}
[yellow]Parameters:[/yellow] {len(command_data.get('parameters', []))}
[yellow]Examples:[/yellow] {len(command_data.get('examples', []))}
[yellow]Tags:[/yellow] {', '.join(command_data.get('tags', []))}"""
        
        console.print(Panel(panel_content, title="Command Summary"))
        
        return Confirm.ask("\n[bold]Save this command?[/bold]", default=True)
