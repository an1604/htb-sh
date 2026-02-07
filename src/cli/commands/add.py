# src/cli/commands/add.py
"""Add command for creating new commands interactively"""

import click
from rich.console import Console

from src.cli.utils import InteractivePrompts, CommandReviewData
from src.core.command import Command, Parameter, Example
from src.utils import load_config, get_tag_suggestions

console = Console()


def _parse_param(s: str) -> Parameter:
    """Parse param string: name:description:required (description may contain colons)"""
    parts = s.split(':')
    if len(parts) < 3:
        raise ValueError(f"Invalid param format: {s}")
    name = parts[0].strip()
    req = parts[-1].strip().lower()
    desc = ':'.join(parts[1:-1]).strip().strip('"')
    required = req in ('required', 'true', '1')
    return Parameter(name=name, description=desc, required=required)


def _quick_add(manager, tool_name: str, cmd_id: str, cmd_name: str,
               cmd_template: str, explanation: str, params_list: tuple,
               tags_str: str):
    """Quick add: create command from flags without prompts."""
    tool = manager.get_tool(tool_name)
    if not tool:
        console.print(f"[bold red]Error: Tool '{tool_name}' not found.[/bold red]")
        return

    parameters = []
    for s in params_list:
        try:
            parameters.append(_parse_param(s))
        except ValueError as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            return

    tags = [t.strip() for t in tags_str.split(',')] if tags_str else []

    command = Command(
        id=cmd_id,
        name=cmd_name,
        command=cmd_template,
        explanation=explanation,
        parameters=parameters,
        examples=[],
        tags=tags
    )
    tool.add_command(command)
    console.print(f"[green]Added: {tool_name}:{cmd_id}[/green]")


@click.command()
@click.argument('tool_name', required=False)
@click.option('--id', 'cmd_id', help='Command ID')
@click.option('--name', 'cmd_name', help='Command display name')
@click.option('--cmd', 'cmd_template', help='Command template (use {param} for variables)')
@click.option('--explain', 'explanation', help='Command explanation')
@click.option('--param', 'params_list', multiple=True,
              help='Parameter as name:description:required (e.g., target:"Target IP":required)')
@click.option('--tag', 'tags_str', help='Tags (comma-separated)')
@click.pass_obj
def add(manager, tool_name: str, cmd_id: str, cmd_name: str, cmd_template: str,
        explanation: str, params_list: tuple, tags_str: str):
    """
    Add a new command interactively or via quick flags.

    Examples:
        htb add                    # Interactive
        htb add nmap               # Semi-interactive (skip tool selection)
        htb add nmap --id x --name "X" --cmd "cmd" --explain "..." --tag a,b
    """
    # Quick add: tool + all required flags
    quick_add = (tool_name and cmd_id and cmd_name and cmd_template and explanation)

    if quick_add:
        _quick_add(manager, tool_name, cmd_id, cmd_name, cmd_template,
                   explanation, params_list, tags_str)
        return

    prompts = InteractivePrompts()

    # Step 1: Get tool (select or from argument)
    if tool_name:
        tool = manager.get_tool(tool_name)
        if not tool:
            click.echo(f"❌ Tool '{tool_name}' not found.")
            return
    else:
        tools = manager.list_tools()
        if not tools:
            click.echo("❌ No tools available. Please register tools first.")
            return
        tool_name = prompts.select_tool(tools)
        tool = manager.get_tool(tool_name)
    
        if not tool:
            click.echo(f"❌ Tool '{tool_name}' not found.")
            return

    # Step 2: Get command details
    cmd_details = prompts.input_command_details()
    
    # Step 3: Extract and configure parameters
    temp_command = Command(
        id=cmd_details.id,
        name=cmd_details.name,
        command=cmd_details.command,
        explanation=cmd_details.explanation
    )
    
    placeholders = temp_command.get_parameter_placeholders()
    parameters = []
    
    if placeholders:
        click.echo(f"\n✓ Detected {len(placeholders)} parameter(s): {', '.join(placeholders)}")
        for param_name in placeholders:
            param = prompts.configure_parameter(param_name)
            parameters.append(param)
    
    # Step 4: Get tags
    config = load_config()
    tag_suggestions = get_tag_suggestions(config)
    tags = prompts.input_tags(tag_suggestions)
    
    # Step 5: Add examples (optional, can add multiple)
    examples = []
    while True:
        example_data = prompts.add_example()
        if example_data:
            example = Example(
                input=example_data.input,
                output=example_data.output,
                description=example_data.description
            )
            examples.append(example)
        else:
            break
    
    # Step 6: Build complete command
    command = Command(
        id=cmd_details.id,
        name=cmd_details.name,
        command=cmd_details.command,
        explanation=cmd_details.explanation,
        parameters=parameters,
        examples=examples,
        tags=tags
    )
    
    # Step 7: Review and confirm
    review_data = CommandReviewData(
        tool=tool_name,
        id=command.id,
        name=command.name,
        command=command.command,
        explanation=command.explanation,
        parameters=command.parameters,
        examples=command.examples,
        tags=command.tags
    )
    
    if prompts.review_and_confirm(review_data):
        # Save command
        tool.add_command(command)
        click.echo(f"\n✅ Command '{tool_name}:{command.id}' saved successfully!")
    else:
        click.echo("\n❌ Command not saved.")

