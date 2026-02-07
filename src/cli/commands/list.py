# src/cli/commands/list.py
"""List command for displaying commands"""

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.command(name='list')
@click.argument('tool_name', required=False)
@click.pass_obj
def list_commands(manager, tool_name: str):
    """
    List all commands or commands for a specific tool.
    
    Examples:
        htb list           # List all commands
        htb list nmap      # List nmap commands only
    """
    # Get commands
    if tool_name:
        # List commands for specific tool
        tool = manager.get_tool(tool_name)
        if not tool:
            console.print(f"[bold red]❌ Tool '{tool_name}' not found.[/bold red]")
            return
        
        commands = tool.get_all_commands()
        title = f"Commands for {tool.name}"
    else:
        # List all commands from all tools
        tools = manager.list_tools()
        commands = []
        for tool_info in tools:
            tool = manager.get_tool(tool_info['name'])
            if tool:
                commands.extend(tool.get_all_commands())
        
        title = "All Commands"
    
    # Display commands
    if not commands:
        console.print("[yellow]No commands found.[/yellow]")
        return
    
    # Create table
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Tool", style="green", width=12)
    table.add_column("ID", style="yellow", width=20)
    table.add_column("Name", style="bold", width=30)
    table.add_column("Tags", style="dim", width=25)
    
    # Add rows
    for cmd in commands:
        # Get tool name for this command (we need to track it)
        tool_display = tool_name if tool_name else _get_tool_for_command(manager, cmd)
        tags_display = ", ".join(cmd.tags[:3]) if cmd.tags else "-"
        if len(cmd.tags) > 3:
            tags_display += "..."
        
        table.add_row(
            tool_display,
            cmd.id,
            cmd.name,
            tags_display
        )
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(commands)} command(s)[/dim]")
    console.print("[dim]Use 'htb show <tool>:<command-id>' to see details[/dim]")


def _get_tool_for_command(manager, command):
    """Helper to find which tool a command belongs to"""
    tools = manager.list_tools()
    for tool_info in tools:
        tool = manager.get_tool(tool_info['name'])
        if tool and command in tool.get_all_commands():
            return tool.name
    return "unknown"
