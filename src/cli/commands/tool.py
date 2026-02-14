"""Tool management commands"""

import click
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from src.utils import load_config

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


@tool_group.command(name='add')
@click.argument('name', required=False)
@click.option('--description', '-d', help='Tool description')
@click.option('--category', '-c', default='misc',
              help='Tool category (default: misc)')
@click.pass_obj
def tool_add(manager, name: str, description: str, category: str):
    """
    Add a new tool (interactive or quick mode).

    Examples:
        htb tool add                           # Interactive prompts
        htb tool add gobuster -d "Dir bruster" -c web
    """
    # Interactive: prompt for missing values
    interactive = not name or not description
    if not name:
        name = Prompt.ask("[cyan]Tool name[/cyan]")
    if not description:
        description = Prompt.ask("[cyan]Description[/cyan]")
    if interactive:
        config = load_config()
        categories = config.get('categories', ['misc'])
        console.print(f"[dim]Categories: {', '.join(categories)}[/dim]")
        cat_input = Prompt.ask("[cyan]Category[/cyan]", default="misc")
        if cat_input:
            category = cat_input

    if manager.get_tool(name):
        console.print(f"[bold red]Error: Tool '{name}' already exists.[/bold red]")
        return

    manager.storage.create_tool_file(name, description, category)
    manager.register_dynamic_tool(name, description, category)
    console.print(f"[green]Added tool: {name}[/green]")


@tool_group.command(name='categories')
@click.pass_obj
def tool_categories(manager):
    """
    List all tool categories.

    Examples:
        htb tool categories
    """
    categories = manager.get_categories()

    if not categories:
        console.print("[yellow]No categories found.[/yellow]")
        return

    console.print("\n[bold cyan]Categories:[/bold cyan]")
    for cat in categories:
        console.print(f"  [yellow]•[/yellow] {cat}")
    console.print()
