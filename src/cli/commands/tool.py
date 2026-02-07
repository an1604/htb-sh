"""Tool management commands"""

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group(name='tool')
@click.pass_obj
def tool_group(manager):
    """Manage pentesting tools."""
    pass


@tool_group.command(name='list')
@click.option('--category', '-c', help='Filter tools by category')
@click.pass_obj
def tool_list(manager, category):
    """
    List all registered tools.

    Examples:
        htb tool list
        htb tool list --category reconnaissance
    """
    tools = manager.list_tools(category=category)

    if not tools:
        console.print("[yellow]No tools found.[/yellow]")
        return

    title = f"Tools ({len(tools)})" + (f" in {category}" if category else "")
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green", width=14)
    table.add_column("Category", style="yellow", width=18)
    table.add_column("Commands", style="dim", width=10)
    table.add_column("Description", style="dim")

    for t in tools:
        table.add_row(
            t["name"],
            t["category"],
            str(t["command_count"]),
            t["description"],
        )

    console.print(table)
