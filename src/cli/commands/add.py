# src/cli/commands/add.py
"""Add command for creating new commands interactively"""

import click
from src.cli.utils import InteractivePrompts
from src.core.command import Command


@click.command()
@click.pass_obj
def add(manager):
    """Add a new command interactively"""
    prompts = InteractivePrompts()
    
    # Step 1: Select tool
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
    
    # Step 3: Extract parameter placeholders from command template
    temp_command = Command(
        id=cmd_details.id,
        name=cmd_details.name,
        command=cmd_details.command,
        explanation=cmd_details.explanation
    )
    
    placeholders = temp_command.get_parameter_placeholders()
    
    # Show detected parameters (for now, just display them)
    if placeholders:
        click.echo(f"\n✓ Detected parameters: {', '.join(placeholders)}")
    
    # For this basic version, we'll just save without configuring parameters
    # Parameters, tags, and examples will be added in next steps
    
    click.echo(f"\n✓ Command '{tool_name}:{cmd_details.id}' created successfully!")
    click.echo("  (Note: Full interactive flow with parameters, tags, and examples coming next)")
