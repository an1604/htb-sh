"""Delete command for removing stored commands"""

import click
from rich.console import Console

console = Console()


@click.command(name='delete')
@click.argument('command_ref', required=True)
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
@click.pass_obj
def delete_command(manager, command_ref: str, force: bool):
    """
    Delete a stored command.

    Format: tool:command-id

    Examples:
        htb delete nmap:basic-scan
        htb delete nmap:basic-scan --force
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

    # Get command to verify it exists
    command = tool.get_command(command_id)
    if not command:
        console.print(f"[bold red]Error: Command '{command_id}' not found in tool '{tool_name}'.[/bold red]")
        return

    # Confirm unless --force
    if not force:
        if not click.confirm(f"Delete command '{command.name}' ({tool_name}:{command_id})?"):
            console.print("[yellow]Cancelled.[/yellow]")
            return

    deleted = tool.delete_command(command_id)
    if deleted:
        console.print(f"[green]Deleted: {tool_name}:{command_id}[/green]")
    else:
        console.print(f"[bold red]Error: Failed to delete {tool_name}:{command_id}[/bold red]")
