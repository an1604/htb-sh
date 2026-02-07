# src/cli/main.py
import click
from pathlib import Path
from src.core.storage import Storage
from src.core.command_manager import CommandManager
from src.tools import NmapTool, SMBTool, NetcatTool
from src.utils import load_config, get_data_dir
from src.cli.commands import add, list_commands, show_command, search_commands, gen_command, delete_command, edit_command


# Global command manager instance
_manager = None


def get_manager() -> CommandManager:
    """Get or create the global CommandManager instance"""
    global _manager
    if _manager is None:
        # Load configuration
        config = load_config()
        data_dir = get_data_dir(config)
        
        # Initialize storage and command manager
        storage = Storage(data_dir)
        _manager = CommandManager(storage)
        
        # Register all tools
        _manager.register_tool(NmapTool)
        _manager.register_tool(SMBTool)
        _manager.register_tool(NetcatTool)
    
    return _manager


@click.group()
@click.version_option(version="1.0.0")
@click.pass_context
def cli(ctx):
    """
    HTB Command Automation Tool
    
    A CLI tool for managing and executing pentesting commands.
    """
    # Store manager in context for commands to access
    ctx.obj = get_manager()


@cli.command()
@click.pass_obj
def test(manager):
    """Test command to verify tool registration"""
    tools = manager.list_tools()
    
    click.echo("\n✓ HTB Command Automation Tool initialized successfully!\n")
    click.echo(f"Registered tools: {len(tools)}\n")
    
    for tool in tools:
        click.echo(f"  • {tool['name']:<10} [{tool['category']:<15}] - {tool['description']}")
    
    click.echo()


# Register commands
cli.add_command(add)
cli.add_command(list_commands)
cli.add_command(show_command)
cli.add_command(search_commands)
cli.add_command(gen_command)
cli.add_command(delete_command)
cli.add_command(edit_command)


if __name__ == '__main__':
    cli()
