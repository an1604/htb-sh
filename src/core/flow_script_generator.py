# src/core/flow_script_generator.py
"""Generates executable scripts from flows (does not execute them)."""

from pathlib import Path
from typing import List, Dict
from datetime import datetime

from .flow import Flow
from .command_manager import CommandManager


def _substitute_placeholders(text: str, params: Dict[str, str]) -> str:
    """Replace {key} in text with params[key] for each key in params."""
    result = text
    for key, value in params.items():
        result = result.replace("{" + key + "}", str(value))
    return result


def _resolve_flow_params(flow: Flow, flow_params: Dict[str, str]) -> Dict[str, str]:
    """Fill in default values for missing flow parameters."""
    resolved = dict(flow_params)
    for p in flow.flow_parameters:
        if p.name not in resolved and p.default is not None:
            resolved[p.name] = p.default
    return resolved


def _resolve_step_parameters(
    step_params: Dict[str, str], flow_params: Dict[str, str]
) -> Dict[str, str]:
    """Resolve step parameter values by substituting flow param placeholders."""
    return {
        k: _substitute_placeholders(v, flow_params)
        for k, v in step_params.items()
    }


class FlowScriptGenerator:
    """
    Generates executable scripts from flows.
    Does not execute scripts; only produces script content.
    """

    def __init__(self, command_manager: CommandManager):
        self.command_manager = command_manager

    def preview_commands(self, flow: Flow, flow_params: Dict[str, str]) -> List[str]:
        """
        Return the list of command strings that would be in the script.
        No script wrapper (shebang, comments, etc.).
        """
        resolved = _resolve_flow_params(flow, flow_params)
        commands = []
        for step in flow.steps:
            step_params = _resolve_step_parameters(step.parameters, resolved)
            cmd = self.command_manager.generate_command(step.command_ref, step_params)
            commands.append(cmd)
        return commands

    def generate_script(
        self,
        flow: Flow,
        flow_params: Dict[str, str],
        format: str = "bash",
    ) -> str:
        """
        Generate full script (bash or python) with shebang, comments, and step commands.
        """
        resolved = _resolve_flow_params(flow, flow_params)
        commands = self.preview_commands(flow, flow_params)

        if format.lower() == "python":
            return self._generate_python(flow, resolved, commands)
        return self._generate_bash(flow, resolved, commands)

    def _generate_bash(
        self,
        flow: Flow,
        flow_params: Dict[str, str],
        commands: List[str],
    ) -> str:
        lines = [
            "#!/bin/bash",
            "################################################################################",
            f"# Flow: {flow.name}",
            f"# Description: {flow.description}",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "################################################################################",
            "",
        ]
        if flow.add_error_handling:
            lines.append("set -e  # Exit on error")
            lines.append("")
        if flow.add_comments and flow_params:
            lines.append("# Flow Parameters")
            for name, value in flow_params.items():
                safe_name = name.replace("-", "_").upper()
                safe_value = str(value).replace('"', '\\"')
                lines.append(f'{safe_name}="{safe_value}"')
            lines.append("")
        lines.append('echo "=================================================="')
        lines.append(f'echo "Flow: {flow.name}"')
        if flow_params:
            first_name = next(iter(flow_params))
            first_safe = first_name.replace("-", "_").upper()
            lines.append(f'echo "{first_name}: ${{{first_safe}}}"')
        lines.append('echo "=================================================="')
        lines.append('echo ""')
        for i, step in enumerate(flow.steps, 1):
            if flow.add_comments and step.description:
                lines.append(f'# Step {i}: {step.description}')
            lines.append(f'echo "[{i}/{len(flow.steps)}] {step.description or step.id}"')
            if flow.add_comments and step.notes:
                lines.append(f'echo "Note: {step.notes}"')
            lines.append("echo \"\"")
            lines.append(commands[i - 1])
            lines.append("echo \"\"")
        lines.append('echo "=================================================="')
        lines.append('echo "Flow completed successfully!"')
        lines.append('echo "=================================================="')
        return "\n".join(lines)

    def _generate_python(
        self,
        flow: Flow,
        flow_params: Dict[str, str],
        commands: List[str],
    ) -> str:
        escaped_desc = flow.description.replace('"""', '\\"\\"\\"')
        lines = [
            "#!/usr/bin/env python3",
            '"""',
            f"Flow: {flow.name}",
            f"Description: {escaped_desc}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            '"""',
            "import subprocess",
            "import sys",
            "from typing import Optional",
            "",
            "# Flow Parameters",
        ]
        for name, value in flow_params.items():
            lines.append(f"{name} = {repr(value)}")
        lines.append("")
        lines.append("")
        lines.append('def run_command(cmd: str, description: str, notes: Optional[str] = None) -> int:')
        lines.append('    """Run a command and display output."""')
        lines.append('    print(f"\\n{\'=\'*60}")')
        lines.append("    print(f\"[*] {description}\")")
        lines.append("    print(f\"Command: {cmd}\")")
        lines.append("    if notes:")
        lines.append("        print(f\"Note: {notes}\")")
        lines.append("    print('='*60)")
        lines.append("")
        lines.append("    result = subprocess.run(cmd, shell=True, capture_output=False)")
        lines.append("")
        lines.append("    if result.returncode != 0:")
        lines.append("        print(f\"[!] Command failed with exit code {result.returncode}\", file=sys.stderr)")
        lines.append("        sys.exit(result.returncode)")
        lines.append("")
        lines.append("    return result.returncode")
        lines.append("")
        lines.append("")
        lines.append("def main():")
        lines.append('    """Execute flow steps."""')
        lines.append("    print(\"=\"*60)")
        lines.append(f"    print(\"Flow: {flow.name}\")")
        if flow_params:
            first_param = next(iter(flow_params))
            lines.append(f"    print(f\"{first_param}: {{{first_param}}}\")")
        lines.append("    print(\"=\"*60)")
        for i, step in enumerate(flow.steps):
            cmd_repr = repr(commands[i])
            desc_escaped = (step.description or step.id).replace('"', '\\"')
            notes_arg = f", {repr(step.notes)}" if step.notes else ""
            lines.append("")
            lines.append(f"    # Step {i + 1}: {step.description or step.id}")
            lines.append(f"    run_command({cmd_repr}, \"{desc_escaped}\"{notes_arg})")
        lines.append("")
        lines.append("    print(\"\\n\" + \"=\"*60)")
        lines.append('    print("[✓] Flow completed successfully!")')
        lines.append("    print(\"=\"*60)")
        lines.append("")
        lines.append("")
        lines.append('if __name__ == "__main__":')
        lines.append("    main()")
        return "\n".join(lines)

    def save_script(
        self,
        script: str,
        filepath: Path,
        make_executable: bool = True,
    ) -> None:
        """
        Write script to file. On Unix, set executable bit when make_executable is True.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(script, encoding="utf-8")
        if make_executable:
            try:
                path.chmod(path.stat().st_mode | 0o111)
            except OSError:
                pass  # Ignore on Windows or permission errors
