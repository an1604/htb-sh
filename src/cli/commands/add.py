# src/cli/commands/add.py
"""Add command for creating new commands interactively"""

import click
from src.cli.utils import InteractivePrompts
from src.core.command import Command, Parameter, Example
from src.utils import load_config, get_tag_suggestions


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
    command_data = {
        'tool': tool_name,
        'id': command.id,
        'name': command.name,
        'command': command.command,
        'explanation': command.explanation,
        'parameters': command.parameters,
        'examples': command.examples,
        'tags': command.tags
    }
    
    if prompts.review_and_confirm(command_data):
        # Save command
        tool.add_command(command)
        click.echo(f"\n✅ Command '{tool_name}:{command.id}' saved successfully!")
    else:
        click.echo("\n❌ Command not saved.")

