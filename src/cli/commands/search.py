# src/cli/commands/search.py
"""Search command for finding commands by keyword"""

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.command(name='search')
@click.argument('query', required=False)
@click.option('--tag', 'tags_str', default=None, help='Filter by tags (comma-separated)')
@click.option('--tool', 'tool_name', default=None, help='Search in specific tool only')
@click.pass_obj
def search_commands(manager, query: str, tags_str: str, tool_name: str):
    """
    Search commands by keyword and/or tags.
    
    Searches in command name, explanation, and command template.
    Use --tag to filter by tags, --tool to limit to one tool.
    
    Examples:
        htb search "version detection"
        htb search --tag enumeration
        htb search --tool nmap --tag scanning
    """
    # Require at least one filter
    tags = [t.strip() for t in tags_str.split(',')] if tags_str else None
    if not query and not tags:
        console.print("[bold red]Error: Provide a search query or --tag filter.[/bold red]")
        return
    
    # Validate tool exists if specified
    if tool_name and not manager.get_tool(tool_name):
        console.print(f"[bold red]Error: Tool '{tool_name}' not found.[/bold red]")
        return
    
    # Search across all tools
    results = manager.search_all(query=query or None, tags=tags, tool=tool_name)
    
    # Flatten results: list of (tool_name, command) tuples
    commands_with_tools = []
    for tool_name, commands in results.items():
        for cmd in commands:
            commands_with_tools.append((tool_name, cmd))
    
    # Display
    if not commands_with_tools:
        parts = []
        if query:
            parts.append(f"'{query}'")
        if tags:
            parts.append(f"tags: {', '.join(tags)}")
        if tool_name:
            parts.append(f"tool: {tool_name}")
        msg = ", ".join(parts) if parts else "criteria"
        console.print(f"[yellow]No commands found matching {msg}.[/yellow]")
        return

    # Create table
    title_parts = []
    if query:
        title_parts.append(f"'{query}'")
    if tags:
        title_parts.append(f"tags: {', '.join(tags)}")
    if tool_name:
        title_parts.append(f"tool: {tool_name}")
    title = f"Search results for {', '.join(title_parts)}"
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Tool", style="green", width=12)
    table.add_column("ID", style="yellow", width=20)
    table.add_column("Name", style="bold", width=30)
    table.add_column("Tags", style="dim", width=25)
    
    for tool_name, cmd in commands_with_tools:
        tags_display = ", ".join(cmd.tags[:3]) if cmd.tags else "-"
        if len(cmd.tags) > 3:
            tags_display += "..."
        
        table.add_row(
            tool_name,
            cmd.id,
            cmd.name,
            tags_display
        )
    
    console.print(table)
    console.print(f"\n[dim]Found {len(commands_with_tools)} command(s)[/dim]")
    console.print("[dim]Use 'htb show <tool>:<command-id>' to see details[/dim]")
