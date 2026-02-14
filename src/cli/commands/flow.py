# src/cli/commands/flow.py
"""Flow management commands: list, show."""

import json
import click
from rich.console import Console
from rich.panel import Panel

from src.core.flow_manager import FlowManager

console = Console()


def _get_flow_manager(manager):
    """Build FlowManager from CommandManager's storage."""
    return FlowManager(manager.storage)


def _group_flows_by_tag(flows):
    """Group flows by first tag (or 'uncategorized'). Returns dict tag -> list of flows."""
    groups = {}
    for f in flows:
        tag = f.tags[0] if f.tags else "uncategorized"
        if tag not in groups:
            groups[tag] = []
        groups[tag].append(f)
    return groups


@click.group(name="flow")
@click.pass_obj
def flow_group(manager):
    """Manage flows (multi-step workflows). Generate scripts from command sequences."""
    pass


@flow_group.command(name="list")
@click.option("--tag", "-t", help="Filter flows by tag")
@click.option("--compact", "-q", is_flag=True, help="Compact one-line per flow")
@click.pass_obj
def flow_list(manager, tag, compact):
    """
    List all flows or filter by tag.

    Examples:
        htb flow list
        htb flow list --tag enumeration
        htb flow list --compact
    """
    flow_mgr = _get_flow_manager(manager)
    flows = flow_mgr.list_flows(tag=tag)

    if not flows:
        console.print("[yellow]No flows found.[/yellow]")
        if tag:
            console.print(f"[dim]No flows with tag '{tag}'.[/dim]")
        return

    if compact:
        for f in flows:
            desc = (f.description[:50] + "…") if len(f.description) > 50 else f.description
            console.print(f"  • [cyan]{f.id:<25}[/cyan] - {desc}")
        return

    # Full view: group by first tag
    grouped = _group_flows_by_tag(flows)
    console.print(f"\n[bold]Available Flows ({len(flows)} total)[/bold]\n")
    for category in sorted(grouped.keys()):
        console.print(f"[yellow][{category}][/yellow]")
        for f in grouped[category]:
            console.print(f"  • [cyan]{f.id:<25}[/cyan] - {f.description}")
            console.print(f"    Steps: {len(f.steps)} | Tags: {', '.join(f.tags)}")
        console.print()
    console.print("[dim]---[/dim]")
    console.print("[dim]Use 'htb flow show <flow-id>' for detailed view[/dim]\n")


@flow_group.command(name="show")
@click.argument("flow_id", required=True)
@click.option("--compact", "-q", is_flag=True, help="Brief output")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_obj
def flow_show(manager, flow_id, compact, output_json):
    """
    Show detailed information about a flow.

    Examples:
        htb flow show smb-enumeration
        htb flow show smb-enumeration --compact
        htb flow show smb-enumeration --json
    """
    flow_mgr = _get_flow_manager(manager)
    flow = flow_mgr.get_flow(flow_id)

    if not flow:
        console.print(f"[bold red]Error:[/bold red] Flow '{flow_id}' not found.")
        return

    if output_json:
        # Flow has to_dict on the model but Flow model doesn't have to_dict returning full structure for JSON.
        # We can build a dict from flow fields.
        out = {
            "id": flow.id,
            "name": flow.name,
            "description": flow.description,
            "steps": [s.to_dict() for s in flow.steps],
            "flow_parameters": [
                {
                    "name": p.name,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                }
                for p in flow.flow_parameters
            ],
            "tags": flow.tags,
            "notes": flow.notes,
            "default_format": flow.default_format,
            "add_error_handling": flow.add_error_handling,
            "add_comments": flow.add_comments,
        }
        console.print(json.dumps(out, indent=2))
        return

    if compact:
        params_str = ", ".join(
            p.name + ("*" if p.required else "") for p in flow.flow_parameters
        )
        console.print(f"[bold]Flow:[/bold] {flow.name} ([cyan]{flow.id}[/cyan])")
        console.print(f"[bold]Parameters:[/bold] {params_str}")
        console.print(f"[bold]Steps:[/bold] {len(flow.steps)}")
        for i, step in enumerate(flow.steps, 1):
            console.print(f"  {i}. [dim]{step.command_ref}[/dim]")
        console.print(f"[bold]Tags:[/bold] {', '.join(flow.tags)}")
        return

    # Full view
    header_lines = [
        f"[bold]ID:[/bold]          {flow.id}",
        f"[bold]Description:[/bold] {flow.description}",
        f"[bold]Format:[/bold]      {flow.default_format}",
        f"[bold]Tags:[/bold]        {', '.join(flow.tags) or '-'}",
    ]
    console.print(Panel("\n".join(header_lines), title=f"Flow: {flow.name}", border_style="cyan"))
    console.print()

    console.print("[bold][Parameters][/bold]")
    if not flow.flow_parameters:
        console.print("  [dim](none)[/dim]")
    else:
        for p in flow.flow_parameters:
            req = "required" if p.required else "optional"
            default_str = f" [default: {p.default}]" if p.default is not None else ""
            console.print(f"  • [cyan]{p.name}[/cyan] ({req})    - {p.description}{default_str}")
    console.print()

    console.print(f"[bold][Steps][/bold] ({len(flow.steps)} total)")
    console.print()
    for i, step in enumerate(flow.steps, 1):
        console.print(f"  [bold]{i}. {step.id}[/bold]")
        console.print(f"     Command: [dim]{step.command_ref}[/dim]")
        if step.description:
            console.print(f"     Description: {step.description}")
        if step.parameters:
            console.print("     Parameters:")
            for k, v in step.parameters.items():
                console.print(f"       {k} = {v}")
        if step.notes:
            console.print(f"     Note: {step.notes}")
        console.print()

    if flow.notes:
        console.print("[bold][Notes][/bold]")
        console.print(flow.notes)
        console.print()

    console.print("[bold][Usage][/bold]")
    console.print(f"  Generate script: [dim]htb flow gen {flow.id} --param target=<IP>[/dim]")
    console.print(f"  Preview:         [dim]htb flow gen {flow.id} --param target=<IP> --preview[/dim]")
    console.print(f"  Save to file:    [dim]htb flow gen {flow.id} --param target=<IP> --save script.sh[/dim]")
    console.print()
