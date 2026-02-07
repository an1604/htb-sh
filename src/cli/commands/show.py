# src/cli/commands/show.py
"""Show command for displaying command details"""

import click
from rich.console import Console
from rich.panel import Panel
from src.cli.utils.constants import (
    SHOW_TOOL_LINE,
    SHOW_ID_LINE,
    SHOW_NAME_LINE,
    SHOW_COMMAND_LABEL,
    SHOW_COMMAND_VALUE,
    SHOW_EXPLANATION_LABEL,
    SHOW_EXPLANATION_VALUE,
    PANEL_TITLE_COMMAND,
)

console = Console()


@click.command(name='show')
@click.argument('command_ref', required=True)
@click.pass_obj
def show_command(manager, command_ref: str):
    """
    Show detailed information about a command.
    
    Format: tool:command-id
    
    Examples:
        htb show nmap:basic-scan
        htb show smb:list-shares
    """
    # Parse tool:command-id format
    if ':' not in command_ref:
        console.print("[bold red]Error: Invalid format. Use 'tool:command-id' (e.g., 'nmap:basic-scan')[/bold red]")
        return
    
    tool_name, command_id = command_ref.split(':', 1)
    
    # Get tool
    tool = manager.get_tool(tool_name)
    if not tool:
        console.print(f"[bold red]Error: Tool '{tool_name}' not found.[/bold red]")
        return
    
    # Get command
    command = tool.get_command(command_id)
    if not command:
        console.print(f"[bold red]Error: Command '{command_id}' not found in tool '{tool_name}'.[/bold red]")
        return
    
    # Display command details
    _display_command_details(tool_name, command)


def _display_command_details(tool_name: str, command):
    """Display command details in a formatted panel"""
    # Build content
    content_lines = [
        SHOW_TOOL_LINE.format(tool_name),
        SHOW_ID_LINE.format(command.id),
        SHOW_NAME_LINE.format(command.name),
        "",
        SHOW_COMMAND_LABEL,
        SHOW_COMMAND_VALUE.format(command.command),
        "",
        SHOW_EXPLANATION_LABEL,
        SHOW_EXPLANATION_VALUE.format(command.explanation),
    ]
    
    # Add parameters if any
    if command.parameters:
        content_lines.append("")
        content_lines.append(f"[bold]Parameters:[/bold] {len(command.parameters)}")
        for param in command.parameters:
            req_marker = "*" if param.required else ""
            default_text = f" (default: {param.default})" if param.default else ""
            content_lines.append(f"  • {param.name}{req_marker}: {param.description}{default_text}")
    
    # Add tags if any
    if command.tags:
        content_lines.append("")
        content_lines.append(f"[bold]Tags:[/bold] {', '.join(command.tags)}")
    
    # Add examples if any
    if command.examples:
        content_lines.append("")
        content_lines.append(f"[bold]Examples:[/bold] {len(command.examples)}")
        for i, example in enumerate(command.examples, 1):
            content_lines.append(f"  [cyan]Example {i}:[/cyan]")
            content_lines.append(f"    Input: {example.input}")
            if example.description:
                content_lines.append(f"    Description: {example.description}")
    
    # Display panel
    content = "\n".join(content_lines)
    panel = Panel(content, title=PANEL_TITLE_COMMAND.format(command.name), border_style="cyan")
    console.print(panel)
