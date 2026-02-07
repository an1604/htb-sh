# src/cli/commands/gen.py
"""Generate command for rendering commands with parameters"""

import click
from rich.console import Console

from src.utils import load_config

console = Console()


@click.command(name='gen')
@click.argument('command_ref', required=True)
@click.option('-p', '--param', 'params_list', multiple=True,
              help='Parameter as key=value (e.g., -p target=10.10.10.5)')
@click.option('--no-copy', is_flag=True, help='Do not copy generated command to clipboard')
@click.option('--print-only', is_flag=True, help='Print command only (no copy, minimal output)')
@click.pass_obj
def gen_command(manager, command_ref: str, params_list: tuple, no_copy: bool, print_only: bool):
    """
    Generate a command with parameters.
    
    Format: tool:command-id
    Use -p key=value to pass parameters (multiple allowed).
    
    Examples:
        htb gen nmap:basic-scan -p target=10.10.10.5
        htb gen nmap:service-version -p target=192.168.1.1 -p ports=-p80,443
    """
    # Parse tool:command-id format
    if ':' not in command_ref:
        console.print("[bold red]Error: Invalid format. Use 'tool:command-id' (e.g., 'nmap:basic-scan')[/bold red]")
        return

    # Build params dict from -p key=value
    params = {}
    for item in params_list:
        if '=' in item:
            key, _, value = item.partition('=')
            params[key.strip()] = value.strip()
        else:
            console.print(f"[bold red]Error: Invalid param '{item}'. Use key=value format.[/bold red]")
            return

    # Validate tool and command exist
    tool_name, command_id = command_ref.split(':', 1)
    tool = manager.get_tool(tool_name)
    if not tool:
        console.print(f"[bold red]Error: Tool '{tool_name}' not found.[/bold red]")
        return
    if not tool.get_command(command_id):
        console.print(f"[bold red]Error: Command '{command_id}' not found in tool '{tool_name}'.[/bold red]")
        return

    # Generate command
    try:
        generated = manager.generate_command(command_ref, params)

        if print_only:
            click.echo(generated)
        else:
            console.print(f"\n[bold green]{generated}[/bold green]\n")
            # Copy to clipboard unless --no-copy
            if not no_copy:
                config = load_config()
                if config.get('clipboard_enabled', True):
                    try:
                        import pyperclip
                        pyperclip.copy(generated)
                        console.print("[green]Copied to clipboard.[/green]")
                    except Exception:
                        console.print("[yellow]Could not copy to clipboard.[/yellow]")
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
