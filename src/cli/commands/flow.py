# src/cli/commands/flow.py
"""Flow management commands: list, show, gen, add, edit, delete, search."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from src.core.flow import Flow, FlowStep
from src.core.flow_manager import FlowManager
from src.core.flow_script_generator import FlowScriptGenerator
from src.core.command import Parameter
from src.utils import load_config

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


@flow_group.command(name="gen")
@click.argument("flow_id", required=True)
@click.option("--param", "-p", "param_list", multiple=True, help="Flow parameter as name=value (repeatable)")
@click.option("--save", "-o", "save_path", type=click.Path(path_type=Path), help="Save script to file")
@click.option("--format", "-f", "script_format", type=click.Choice(["bash", "python"]), default=None, help="Script format (default: flow's default)")
@click.option("--preview", is_flag=True, help="Output only the list of commands (no script wrapper)")
@click.option("--no-copy", is_flag=True, help="Do not copy to clipboard")
@click.option("--executable", is_flag=True, default=None, help="Make saved script executable (default: true when using --save)")
@click.pass_obj
def flow_gen(manager, flow_id, param_list, save_path, script_format, preview, no_copy, executable):
    """
    Generate script from a flow (does not execute).

    Examples:
        htb flow gen smb-enumeration --param target=10.10.10.5
        htb flow gen smb-enumeration --param target=10.10.10.5 --save enum.sh
        htb flow gen smb-enumeration --param target=10.10.10.5 --preview
    """
    flow_mgr = _get_flow_manager(manager)
    flow = flow_mgr.get_flow(flow_id)
    if not flow:
        console.print(f"[bold red]Error:[/bold red] Flow '{flow_id}' not found.")
        return

    flow_params = {}
    for item in param_list:
        if "=" in item:
            key, _, value = item.partition("=")
            flow_params[key.strip()] = value.strip()
        else:
            console.print(f"[bold red]Error:[/bold red] Invalid param '{item}'. Use name=value.")
            return

    # Fill missing required params via prompt
    missing_required = [p for p in flow.flow_parameters if p.required and p.name not in flow_params]
    if missing_required:
        console.print("[bold]Flow parameters (missing required):[/bold]")
        for p in missing_required:
            value = Prompt.ask(f"  [cyan]{p.name}[/cyan]")
            if not value.strip():
                console.print(f"[red]'{p.name}' is required.[/red]")
                return
            flow_params[p.name] = value.strip()

    generator = FlowScriptGenerator(manager)
    fmt = script_format or flow.default_format or "bash"
    make_executable = executable if executable is not None else (save_path is not None)

    try:
        if preview:
            commands = generator.preview_commands(flow, flow_params)
            console.print(f"\n[bold]Commands in flow '{flow.name}'[/bold]\n")
            for i, cmd in enumerate(commands, 1):
                console.print(f"  {i}. [green]{cmd}[/green]")
            console.print()
            return
        script = generator.generate_script(flow, flow_params, format=fmt)
        if save_path:
            generator.save_script(script, save_path, make_executable=make_executable)
            console.print(f"[green]Generated script saved to: {save_path}[/green]")
        else:
            console.print("\n" + script + "\n")
        if not no_copy and not save_path:
            config = load_config()
            if config.get("clipboard_enabled", True):
                try:
                    import pyperclip
                    pyperclip.copy(script)
                    console.print("[green]Copied to clipboard.[/green]")
                except Exception:
                    console.print("[yellow]Could not copy to clipboard.[/yellow]")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@flow_group.command(name="add")
@click.pass_obj
def flow_add(manager):
    """
    Interactively create a new flow.

    You will be prompted for: id, name, description, parameters, steps (command_ref + param mapping), tags.
    """
    flow_mgr = _get_flow_manager(manager)
    console.print("\n[bold cyan]New Flow[/bold cyan]\n")
    flow_id = Prompt.ask("Flow ID", default="my-flow").strip() or "my-flow"
    if flow_mgr.get_flow(flow_id):
        console.print(f"[red]A flow with ID '{flow_id}' already exists.[/red]")
        return
    name = Prompt.ask("Name", default=flow_id.replace("-", " ").title()).strip() or flow_id
    description = Prompt.ask("Description", default="").strip() or "No description"
    flow_params = []
    while True:
        if not Confirm.ask("Add a flow parameter?", default=True):
            break
        pname = Prompt.ask("  Parameter name").strip()
        if not pname:
            continue
        pdesc = Prompt.ask("  Description", default="").strip()
        preq = Confirm.ask("  Required?", default=True)
        pdefault = None
        if not preq:
            pdefault = Prompt.ask("  Default value (optional)", default="").strip() or None
        flow_params.append(Parameter(name=pname, description=pdesc, required=preq, default=pdefault))
    steps = []
    while True:
        if not Confirm.ask("Add a step?", default=len(steps) == 0):
            break
        step_id = Prompt.ask("  Step ID", default=f"step-{len(steps)+1}").strip() or f"step-{len(steps)+1}"
        cmd_ref = Prompt.ask("  Command (tool:command-id)", default="").strip()
        if not cmd_ref or ":" not in cmd_ref:
            console.print("[red]Invalid command ref. Use tool:command-id[/red]")
            continue
        try:
            manager.get_command(cmd_ref)
        except Exception:
            console.print(f"[red]Command '{cmd_ref}' not found.[/red]")
            continue
        step_desc = Prompt.ask("  Step description (optional)", default="").strip() or None
        param_line = Prompt.ask("  Parameter mapping (e.g. host={target}, port={port})", default="").strip()
        step_params = {}
        if param_line:
            for part in param_line.split(","):
                part = part.strip()
                if "=" in part:
                    k, _, v = part.partition("=")
                    step_params[k.strip()] = v.strip()
        steps.append(FlowStep(id=step_id, command_ref=cmd_ref, parameters=step_params, description=step_desc))
    tags_str = Prompt.ask("Tags (comma-separated)", default="").strip()
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    notes = Prompt.ask("Notes (optional)", default="").strip() or None
    flow = Flow(
        id=flow_id,
        name=name,
        description=description,
        steps=steps,
        flow_parameters=flow_params,
        tags=tags,
        notes=notes,
    )
    flow_mgr.add_flow(flow)
    console.print(f"[green]Flow '{flow_id}' created.[/green]\n")


@flow_group.command(name="edit")
@click.argument("flow_id", required=True)
@click.pass_obj
def flow_edit(manager, flow_id):
    """Edit an existing flow (name, description, notes, tags)."""
    flow_mgr = _get_flow_manager(manager)
    flow = flow_mgr.get_flow(flow_id)
    if not flow:
        console.print(f"[bold red]Error:[/bold red] Flow '{flow_id}' not found.")
        return
    console.print(f"\n[bold cyan]Edit flow: {flow_id}[/bold cyan]\n")
    name = Prompt.ask("Name", default=flow.name).strip() or flow.name
    description = Prompt.ask("Description", default=flow.description).strip() or flow.description
    notes = Prompt.ask("Notes", default=flow.notes or "").strip() or None
    tags_str = Prompt.ask("Tags (comma-separated)", default=",".join(flow.tags)).strip()
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
    updated = Flow(
        id=flow.id,
        name=name,
        description=description,
        steps=flow.steps,
        flow_parameters=flow.flow_parameters,
        tags=tags,
        notes=notes,
        default_format=flow.default_format,
        add_error_handling=flow.add_error_handling,
        add_comments=flow.add_comments,
    )
    flow_mgr.update_flow(flow_id, updated)
    console.print(f"[green]Flow '{flow_id}' updated.[/green]\n")


@flow_group.command(name="delete")
@click.argument("flow_id", required=True)
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
@click.pass_obj
def flow_delete(manager, flow_id, force):
    """Delete a flow."""
    flow_mgr = _get_flow_manager(manager)
    flow = flow_mgr.get_flow(flow_id)
    if not flow:
        console.print(f"[bold red]Error:[/bold red] Flow '{flow_id}' not found.")
        return
    if not force and not Confirm.ask(f"Delete flow '{flow.name}' ({flow_id})?"):
        console.print("[yellow]Cancelled.[/yellow]")
        return
    if flow_mgr.delete_flow(flow_id):
        console.print(f"[green]Deleted flow '{flow_id}'.[/green]")
    else:
        console.print(f"[bold red]Error:[/bold red] Could not delete '{flow_id}'.")


@flow_group.command(name="search")
@click.argument("query", required=False)
@click.option("--tag", "-t", help="Filter by tag")
@click.option("--compact", "-q", is_flag=True, help="Compact output")
@click.pass_obj
def flow_search(manager, query, tag, compact):
    """Search flows by query and/or tag."""
    flow_mgr = _get_flow_manager(manager)
    flows = flow_mgr.search_flows(query=query, tag=tag)
    if not flows:
        console.print("[yellow]No flows found.[/yellow]")
        return
    if compact:
        for f in flows:
            desc = (f.description[:50] + "…") if len(f.description) > 50 else f.description
            console.print(f"  • [cyan]{f.id:<25}[/cyan] - {desc}")
        return
    grouped = _group_flows_by_tag(flows)
    title = f"Flows ({len(flows)} found)"
    if query:
        title += f" matching '{query}'"
    if tag:
        title += f" tag '{tag}'"
    console.print(f"\n[bold]{title}[/bold]\n")
    for category in sorted(grouped.keys()):
        console.print(f"[yellow][{category}][/yellow]")
        for f in grouped[category]:
            console.print(f"  • [cyan]{f.id:<25}[/cyan] - {f.description}")
            console.print(f"    Steps: {len(f.steps)} | Tags: {', '.join(f.tags)}")
        console.print()
