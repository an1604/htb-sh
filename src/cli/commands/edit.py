"""Edit command for updating stored commands"""

import click
from rich.console import Console
from rich.prompt import Prompt

from src.core.command import Command

console = Console()


@click.command(name='edit')
@click.argument('command_ref', required=True)
@click.option('--explanation', '-e', help='Update command explanation')
@click.pass_obj
def edit_command(manager, command_ref: str, explanation: str):
    """
    Edit a stored command.

    Format: tool:command-id

    Quick edit (update specific field):
        htb edit nmap:basic-scan --explanation "New explanation"
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

    # Get new value: from flag or interactive prompt
    if explanation:
        new_explanation = explanation
    else:
        console.print(f"\n[bold]Current explanation:[/bold] {command.explanation}\n")
        new_explanation = Prompt.ask(
            "[cyan]New explanation[/cyan] (press Enter to keep)",
            default=command.explanation
        )

    # Build updated command
    updated = Command(
        id=command.id,
        name=command.name,
        command=command.command,
        explanation=new_explanation,
        parameters=command.parameters,
        examples=command.examples,
        tags=command.tags,
        notes=command.notes
    )

    success = tool.update_command(command_id, updated)
    if success:
        console.print(f"[green]Updated: {tool_name}:{command_id}[/green]")
    else:
        console.print(f"[bold red]Error: Failed to update {tool_name}:{command_id}[/bold red]")
